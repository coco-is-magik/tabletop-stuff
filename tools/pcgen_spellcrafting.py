"""Run the custom spell production-controller save/reload regression.

PCGen startup is slow on network filesystems; use the save/reload gate
arguments to split the two processes across separate invocations.
"""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture

TIMEOUT = 300


def command(cp, work, gate, source, saved):
    return [str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
            f"-Dpcgen.config={work}", "-cp", cp + ":" + str(work),
            "pcgen.gui2.facade.PcgenSpellcrafting", str(source),
            str(work / "export.txt"), str(work / (gate + ".txt")),
            "config.ini", gate, str(saved)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", nargs="?", default="all", choices=("all", "save", "reload"))
    parser.add_argument("--work", type=Path, help="existing workspace for the reload gate")
    args = parser.parse_args()
    if args.gate == "reload" and args.work is None:
        parser.error("reload requires --work from the save run")
    if args.work is not None and args.gate != "reload":
        parser.error("--work only applies to the reload gate")
    cp = classpath()
    work = args.work if args.work is not None else workspace()
    if not work.is_dir():
        raise ValueError("missing workspace: " + str(work))
    print("Spellcrafting evidence:", work, flush=True)
    character = work / "spell.pcg"
    saved = work / "saved.pcg"
    if args.gate != "reload":
        character.write_text(fixture(10, "WIS"))
        (work / "export.txt").write_text("level=|TOTALLEVELS|\n")
        if not (work / "pcgen/gui2/facade/PcgenSpellcrafting.class").is_file():
            with (work / "compile.log").open("w") as stream:
                subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                                "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                                str(ROOT / "tools/PcgenSpellcrafting.java")],
                               stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                               timeout=30, check=True)
    gates = {"save": [("spell-save", character)], "reload": [("spell-reload", saved)],
             "all": [("spell-save", character), ("spell-reload", saved)]}[args.gate]
    for gate, source in gates:
        log = work / (gate + ".log")
        with log.open("w") as stream:
            subprocess.run(command(cp, work, gate, source, saved),
                           cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=TIMEOUT, check=True)
        validate_gate(log, gate)
        print("PASS:", gate)
    print("PASS: custom spell prerequisites, acquisition, slots, refunds and save/reload")


if __name__ == "__main__":
    main()
