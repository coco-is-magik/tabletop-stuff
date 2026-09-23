"""Direct PCGen export check using a pinned local or ThinkPad JDK; no packaging."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from spheres import ROOT, DATA, compare_export
from spheres_progression_fixtures import fixture, expected as progression_expected

PCGEN = ROOT / "vendor/upstream/pcgen-6.08.00RC10"
JAVA = Path("/home/danbo/.local/lib/jvm/temurin-16.0.2+7/bin/java")
CACHE = Path("/home/danbo/.gradle/caches/modules-2/files-2.1/org.openjfx")
if not JAVA.is_file() and (ROOT / "vendor/jdk16/bin/java").is_file():
    JAVA = ROOT / "vendor/jdk16/bin/java"
    CACHE = ROOT / "vendor/gradle-cache/caches/modules-2/files-2.1/org.openjfx"
CASES = ("incanter1-int18", "incanter2-int18", "incanter1-int7")


def classpath():
    jar = PCGEN / "build/libs/pcgen-6.09.06.jar"
    if not JAVA.is_file() or not jar.is_file():
        raise ValueError("Requires a pinned Java 16 JDK and built PCGen JAR")
    # PCGen's pinned build names its JAR 6.09.06 despite the source tag RC10.
    jars = [jar]
    for module in ("base", "graphics", "controls", "fxml", "swing", "web"):
        matches = list((CACHE / f"javafx-{module}" / "16").glob(f"*/javafx-{module}-16-linux.jar"))
        if len(matches) != 1:
            raise ValueError(f"Expected one cached JavaFX 16 Linux {module} JAR")
        jars.extend(matches)
    return os.pathsep.join(map(str, jars))


def validate_result(output, log, expected):
    diagnostics = log.read_text(encoding="utf-8")
    if "SEVERE:" in diagnostics or "LSTERROR:" in diagnostics:
        raise ValueError(f"PCGen reported load/export errors; inspect {log}")
    if not output.is_file() or output.stat().st_size > 16384:
        raise ValueError(f"Missing/oversized export; inspect {log}")
    compare_export(output.read_text(encoding="utf-8"), expected)


def validate_selection(log):
    marker = "SPHERES_SELECTION_OK: Destruction Sphere, Searing Blast; spent=2"
    if marker not in log.read_text(encoding="utf-8").splitlines():
        raise ValueError(f"Missing PCGen selection/pool verification; inspect {log}")


def workspace():
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    # Fresh settings and output prevent an old export from passing a failed run.
    work = Path(tempfile.mkdtemp(prefix="pcgen-spheres-", dir=build))
    (work / "config.ini").write_text(
        f"settingsPath={work}\nsystemsPath={PCGEN / 'system'}\n"
        f"pluginsPath={PCGEN / 'plugins'}\npccFilesPath={PCGEN / 'data'}\n"
        f"osPath={PCGEN / 'outputsheets'}\npreviewPath={PCGEN / 'preview'}\n", encoding="utf-8")
    (work / "options.ini").write_text(
        f"pcgen.files.homebrewdataPath={ROOT / 'data'}\n"
        f"pcgen.files.characters={work}\n"
        f"pcgen.files.customPath={work / 'custom'}\n"
        f"pcgen.files.vendordataPath={work / 'vendor'}\n", encoding="utf-8")
    return work


def smoke(case, level=None, casting="INT"):
    if level is None and case not in CASES:
        raise ValueError(f"Unsupported fixture: {case}")
    generated = fixture(level, casting) if level is not None else None
    cp = classpath()
    work = workspace()
    output = work / "export.txt"
    log = work / "pcgen.log"
    character = ROOT / f"testdata/spheres/{case}.pcg"
    if generated is not None:
        character = work / "progression.pcg"
        character.write_text(generated, encoding="utf-8")
    command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
               f"-Dpcgen.config={work}", "-cp", cp, "--source", "16",
               str(ROOT / "tools/PcgenSpheresExport.java"),
               str(character),
               str(DATA / "spheres_export.txt"), str(output), "config.ini"]
    saved = work / "saved.pcg"
    print(f"PCGen output and diagnostic log: {work}", flush=True)
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run([*command, str(saved)], cwd=work, stdin=subprocess.DEVNULL,
                       stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
    expected = (progression_expected(level) if level is not None else
                json.loads((ROOT / "testdata/spheres/expected.json").read_text())[case])
    validate_result(output, log, expected)
    validate_selection(log)
    if not saved.is_file():
        raise ValueError(f"Missing saved character; inspect {log}")
    reloaded = work / "reloaded.txt"
    reload_log = work / "reload.log"
    command[-4] = str(saved)
    command[-2] = str(reloaded)
    with reload_log.open("w", encoding="utf-8") as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL,
                       stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
    validate_result(reloaded, reload_log, expected)
    validate_selection(reload_log)
    print(f"PASS: PCGen export, two spent talents and save/reload match {case}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=[*CASES, "all", "progression"])
    parser.add_argument("--level", type=int, choices=range(1, 21))
    parser.add_argument("--casting", choices=("INT", "WIS", "CHA"), default="INT")
    args = parser.parse_args()
    try:
        if args.case == "progression":
            if args.level is None:
                raise ValueError("progression requires --level")
            smoke(f"incanter{args.level}-{args.casting.lower()}18", args.level, args.casting)
            return
        if args.level is not None or args.casting != "INT":
            raise ValueError("--level/--casting apply only to progression")
        for case in CASES if args.case == "all" else (args.case,):
            smoke(case)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"smoke: {error}\n")


if __name__ == "__main__":
    main()