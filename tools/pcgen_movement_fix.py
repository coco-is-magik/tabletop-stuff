"""Apply the pinned PCGen movement-cache fix and rebuild its affected classes.

This deliberately refuses unexpected source. Rebuilding uses the existing local
PCGen jar and private JDK; it does not download or change dependencies.
"""
import argparse
import copy
from pathlib import Path
import subprocess
import tempfile
import warnings
import zipfile

from pcgen_spheres_smoke import JAVA, ROOT, PCGEN, classpath

OLD = "\t\tprivate void adjustMoveRates(CharID id)\n\t\t{\n\t\t\tRace race = raceFacet.get(id);"
NEW = "\t\tprivate void adjustMoveRates(CharID id)\n\t\t{\n\t\t\tmoveRates.clear();\n\t\t\tRace race = raceFacet.get(id);"
RELATIVE = "pcgen/cdom/facet/analysis/MovementResultFacet"


def patched_source(text):
    if text.count(NEW) == 1 and OLD not in text:
        return text
    if text.count(OLD) != 1 or NEW in text:
        raise ValueError("Unexpected movement implementation; review the pinned patch")
    return text.replace(OLD, NEW, 1)


def rebuild_jar(original, destination, replacements):
    """Preserve shaded-jar duplicate resources; replace only compiled classes."""
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(destination, "w") as output:
        names = set(source.namelist())
        if not replacements.keys() <= names:
            raise ValueError("Compiled replacement missing from the pinned jar")
        output.comment = source.comment
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Duplicate name:", category=UserWarning)
            for entry in source.infolist():
                data = replacements[entry.filename] if entry.filename in replacements else source.read(entry)
                output.writestr(copy.copy(entry), data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = PCGEN / "code/src/java" / (RELATIVE + ".java")
    original = source.read_text()
    fixed = patched_source(original)
    if not args.apply:
        if original != fixed:
            raise ValueError("Movement cache fix is not applied; run with --apply")
        print("PASS: movement-cache source fix present (does not verify jar)")
        return
    jar = PCGEN / "build/libs/pcgen-6.09.06.jar"
    with tempfile.TemporaryDirectory(prefix="pcgen-movement-", dir=ROOT / "build") as directory:
        work = Path(directory)
        temporary_source = work / "MovementResultFacet.java"
        temporary_source.write_text(fixed)
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                        "-cp", classpath(), "-d", str(work), str(temporary_source)],
                       stdin=subprocess.DEVNULL, timeout=30, check=True)
        classes = sorted(work.glob(RELATIVE + "*.class"))
        if not classes or len(classes) > 10:
            raise ValueError("Unexpected movement-class compilation output")
        replacement = work / jar.name
        rebuild_jar(jar, replacement, {str(path.relative_to(work)): path.read_bytes() for path in classes})
        replacement.chmod(jar.stat().st_mode)
        replacement.replace(jar)
        source.write_text(fixed)
    print("PASS: rebuilt movement cache fix; run live removal/save/reload gates")


if __name__ == "__main__":
    main()