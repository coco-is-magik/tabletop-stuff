"""Bounded live Scholar'S Knack selection and save/reload gates."""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from pcgen_class_catalog import fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("save", "reload"))
    parser.add_argument("--level", type=int, choices=range(2, 21), default=12)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--intelligence", type=int, choices=(8, 10, 16), default=16)
    parser.add_argument("--wisdom", type=int, choices=(8, 10, 16), default=10)
    args = parser.parse_args()
    if (args.gate == "reload") != (args.work is not None):
        parser.error("--work is required only for reload")
    work = args.work if args.work is not None else workspace()
    cp = classpath()
    print("Scholar evidence:", work, flush=True)
    saved = work / "saved.pcg"
    source = saved
    if args.gate == "save":
        source = work / "scholar.pcg"
        raw = fixture("scholar", args.level)
        raw = raw.replace("STAT:INT|SCORE:10", f"STAT:INT|SCORE:{args.intelligence}")
        raw = raw.replace("STAT:WIS|SCORE:10", f"STAT:WIS|SCORE:{args.wisdom}")
        source.write_text("\n".join(line for line in raw.splitlines()
                          if not line.startswith("ABILITY:Scholar Scholar'S Knack|")) + "\n")
        (work / "export.txt").write_text("level=|TOTALLEVELS|\n")
        with (work / "compile.log").open("w") as stream:
            subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                            "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                            str(ROOT / "tools/PcgenScholar.java")], stdout=stream,
                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    gate = "scholar-" + args.gate
    log = work / (gate + ".log")
    with log.open("w") as stream:
        subprocess.run([str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
                        f"-Dpcgen.config={work}", "-cp", cp + ":" + str(work),
                        "pcgen.gui2.facade.PcgenScholar", str(source), str(work / "export.txt"),
                        str(work / (gate + ".txt")), "config.ini", gate, str(saved)],
                       cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=110, check=True)
    validate_gate(log, gate)
    print("PASS:", gate)


if __name__ == "__main__":
    main()