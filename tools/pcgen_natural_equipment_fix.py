"""Keep restored natural-weapon equip sets linked to their granted weapon.

Pinned PCGen parser correction. Ordinary inventory still receives its own clone.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

from pcgen_spheres_smoke import JAVA, ROOT, PCGEN, classpath
from pcgen_movement_fix import rebuild_jar

OLD = "\t\t\tEquipment aEquip = eqI.clone();\n\n\t\t\tif (itemQuantity != null)"
NEW = ("\t\t\t// Natural weapons must retain their grant identity for removal after reload.\n"
       "\t\t\tEquipment aEquip = eqI.isNatural() ? eqI : eqI.clone();\n\n"
       "\t\t\tif (itemQuantity != null)")
RELATIVE = "pcgen/io/PCGVer2Parser"


def patched_source(text):
    if text.count(NEW) == 1 and OLD not in text:
        return text
    if text.count(OLD) != 1 or NEW in text:
        raise ValueError("Unexpected natural-equipment parser; review the pinned patch")
    return text.replace(OLD, NEW, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = PCGEN / "code/src/java" / (RELATIVE + ".java")
    original = source.read_text()
    fixed = patched_source(original)
    if not args.apply:
        if original != fixed:
            raise ValueError("Natural-equipment fix is not applied; run with --apply")
        print("PASS: natural-equipment source fix present (does not verify jar)")
        return
    jar = PCGEN / "build/libs/pcgen-6.09.06.jar"
    with tempfile.TemporaryDirectory(prefix="pcgen-natural-equipment-", dir=ROOT / "build") as directory:
        work = Path(directory)
        temporary_source = work / "PCGVer2Parser.java"
        temporary_source.write_text(fixed)
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                        "-cp", classpath(), "-d", str(work), str(temporary_source)],
                       stdin=subprocess.DEVNULL, timeout=30, check=True)
        classes = sorted(work.glob(RELATIVE + "*.class"))
        if not classes or len(classes) > 20:
            raise ValueError("Unexpected parser compilation output")
        replacement = work / jar.name
        rebuild_jar(jar, replacement, {str(path.relative_to(work)): path.read_bytes() for path in classes})
        replacement.chmod(jar.stat().st_mode)
        replacement.replace(jar)
        source.write_text(fixed)
    print("PASS: rebuilt natural-equipment parser; run live save/reload/removal gates")


if __name__ == "__main__":
    main()