"""Bounded Soul Weaver channel prerequisite and retained-feat gates."""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from pcgen_class_catalog import fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("save", "reload"))
    parser.add_argument("--work", type=Path)
    parser.add_argument("--level", type=int, choices=range(1, 21), default=5)
    parser.add_argument("--charisma", type=int, choices=range(3, 31), default=10)
    classes = parser.add_mutually_exclusive_group()
    classes.add_argument("--cleric", action="store_true")
    classes.add_argument("--paladin", action="store_true")
    classes.add_argument("--mixed", action="store_true")
    args = parser.parse_args()
    if (args.gate == "reload") != (args.work is not None):
        parser.error("--work is required only for reload")
    if args.mixed and args.level != 5:
        parser.error("--mixed requires --level 5 for the independent 3d6-pool regression")
    if args.paladin and args.level < 4:
        parser.error("Paladin channel tests require level 4 or higher")
    work = args.work if args.work is not None else workspace()
    cp = classpath()
    print("Channel evidence:", work, flush=True)
    saved = work / "saved.pcg"
    source = saved
    if args.gate == "save":
        source = work / "channel.pcg"
        raw = "\n".join(line for line in fixture("soul-weaver", args.level).splitlines()
                        if not line.startswith("ABILITY:Soul Weaver Channel|")) + "\n"
        raw = raw.replace("STAT:CHA|SCORE:10", f"STAT:CHA|SCORE:{args.charisma}")
        if not args.cleric and not args.paladin:
            raw = raw.replace("STAT:INT|SCORE:10", "STAT:INT|SCORE:18")
            raw += "ABILITY:Spheres Casting Ability|TYPE:NORMAL|CATEGORY:Spheres Casting Ability|KEY:Intelligence Casting\n"
        if args.cleric:
            raw = raw.replace("Soul Weaver", "Cleric")
        if args.paladin:
            raw = raw.replace("Soul Weaver", "Paladin").replace("ALIGN:TN", "ALIGN:LG")
        if args.mixed:
            raw += "CLASS:Cleric|LEVEL:5|SKILLPOOL:0\n"
            raw += "".join(f"CLASSABILITIESLEVEL:Cleric={level}|HITPOINTS:8|SKILLSGAINED:0|SKILLSREMAINING:0\n"
                           for level in range(1, 6))
        source.write_text(raw)
        (work / "export.txt").write_text("level=|TOTALLEVELS|\n")
        with (work / "compile.log").open("w") as stream:
            subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                            "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                            str(ROOT / "tools/PcgenChannel.java")], stdout=stream,
                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    gate = "channel-" + args.gate
    log = work / (gate + ".log")
    with log.open("w") as stream:
        subprocess.run([str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
                        f"-Dpcgen.config={work}", "-cp", cp + ":" + str(work),
                        "pcgen.gui2.facade.PcgenChannel", str(source), str(work / "export.txt"),
                        str(work / (gate + ".txt")), "config.ini", gate, str(saved)],
                       cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=110, check=True)
    validate_gate(log, gate)
    print("PASS:", gate)


if __name__ == "__main__":
    main()