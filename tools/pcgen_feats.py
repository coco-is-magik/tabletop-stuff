"""Bounded live feat selection and save/reload acceptance.

PCGen startup is slow on network filesystems; use the save/reload gate
arguments to split the two processes across separate invocations.
"""
import argparse
from pathlib import Path
import subprocess
from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture as magic_fixture
from pcgen_conscript_class import fixture as combat_fixture
from pcgen_class_catalog import fixture as class_fixture

TIMEOUT = 110


def run(system, gate="all", work=None):
    cp = classpath()
    work = work if work is not None else workspace()
    if not work.is_dir():
        raise ValueError("missing workspace: " + str(work))
    print("Feat evidence:", work, flush=True)
    character = work / "feats.pcg"
    saved = work / "saved.pcg"
    if gate != "reload":
        raw = magic_fixture(10, "INT") if system == "power" else combat_fixture(10)
        if system == 'mixed':
            raw = class_fixture('armorist', 4)
            raw += 'CLASS:Fighter|LEVEL:6|SKILLPOOL:0\n'
            raw += ''.join(f'CLASSABILITIESLEVEL:Fighter={n}|HITPOINTS:10|SKILLSGAINED:0|SKILLSREMAINING:0\n'
                           for n in range(1, 7))
        character.write_text("\n".join(line for line in raw.splitlines()
            if not line.startswith(("ABILITY:Spheres Magic Talent|", "ABILITY:Spheres Combat Talent|"))) + "\n")
        (work / "export.txt").write_text("level=|TOTALLEVELS|\n")
        if not (work / "pcgen/gui2/facade/PcgenFeats.class").is_file():
            with (work / "compile.log").open("w") as stream:
                subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16", "-cp", cp,
                    "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"), str(ROOT / "tools/PcgenFeats.java")],
                    stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    gates = {"save": [("feats-save", character)], "reload": [("feats-reload", saved)],
             "all": [("feats-save", character), ("feats-reload", saved)]}[gate]
    for name, source in gates:
        log = work / (name + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
            "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenFeats", str(source), str(work / "export.txt"),
            str(work / (name + ".txt")), "config.ini", name, str(saved), system]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                stderr=subprocess.STDOUT, timeout=TIMEOUT, check=True)
        validate_gate(log, name)
        print("PASS:", name)
    print("PASS:", system, "feats; completed gate:", gate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system", choices=("power", "might", "mixed"))
    parser.add_argument("gate", nargs="?", default="all", choices=("all", "save", "reload"))
    parser.add_argument("--work", type=Path, help="existing workspace for the reload gate")
    args = parser.parse_args()
    if args.gate == "reload" and args.work is None:
        parser.error("reload requires --work from the save run")
    if args.work is not None and args.gate != "reload":
        parser.error("--work only applies to the reload gate")
    run(args.system, args.gate, args.work)
