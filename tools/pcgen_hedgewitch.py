"""Bounded live Hedgewitch general-secret controller and persistence gates."""
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
    parser.add_argument("--level", type=int, choices=range(1, 21), default=6)
    parser.add_argument("--profile", choices=("general", "resources", "herbology", "spirits", "combat", "umbral", "exorcism", "charlatan", "inspiration"), default="general")
    parser.add_argument("--fey-levels", type=int, choices=range(0, 11), default=0)
    args = parser.parse_args()
    if (args.gate == "reload") != (args.work is not None):
        parser.error("--work is required only for reload")
    work = args.work if args.work is not None else workspace()
    cp = classpath()
    print("Hedgewitch evidence:", work, flush=True)
    saved = work / "saved.pcg"
    source = saved
    if args.gate == "save":
        source = work / "hedgewitch.pcg"
        text = fixture("hedgewitch", args.level)
        if args.profile == "charlatan":
            text = text.replace("KEY:Hedgewitch Academia", "KEY:Hedgewitch Charlatanism")
        if args.profile == "inspiration":
            text = text.replace("KEY:Hedgewitch Academia", "KEY:Hedgewitch Font Of Inspiration")
        if args.profile == "resources":
            text = text.replace("KEY:Hedgewitch Academia", "KEY:Hedgewitch Temporal Traveler")
            text = text.replace("KEY:Hedgewitch Astrology", "KEY:Hedgewitch Transmuter")
        if args.profile in ("herbology", "spirits"):
            first, second = (("Herbology", "Transmuter") if args.profile == "herbology" else ("Black Magic", "Spiritualism"))
            text = text.replace("KEY:Hedgewitch Academia", "KEY:Hedgewitch " + first)
            text = text.replace("KEY:Hedgewitch Astrology", "KEY:Hedgewitch " + second)
        if args.profile == "combat":
            text = text.replace("KEY:Hedgewitch Astrology", "KEY:Hedgewitch Combat")
        if args.profile == "umbral":
            text = text.replace("KEY:Hedgewitch Academia", "KEY:Hedgewitch Umbral")
        if args.profile == "exorcism":
            text = text.replace("KEY:Hedgewitch Academia", "KEY:Hedgewitch Exorcism")
        if args.fey_levels:
            text += f"CLASS:Fey Adept|LEVEL:{args.fey_levels}|SKILLPOOL:0\n"
            text += "".join(f"CLASSABILITIESLEVEL:Fey Adept={level}|HITPOINTS:6|SKILLSGAINED:0|SKILLSREMAINING:0\n"
                            for level in range(1, args.fey_levels + 1))
        source.write_text(text)
        (work / "profile.txt").write_text(args.profile)
        (work / "export.txt").write_text("level=|TOTALLEVELS|\n")
        with (work / "compile.log").open("w") as stream:
            subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                            "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                            str(ROOT / "tools/PcgenHedgewitch.java")], stdout=stream,
                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    gate = "hedgewitch-" + args.gate
    log = work / (gate + ".log")
    with log.open("w") as stream:
        subprocess.run([str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
                        f"-Dpcgen.config={work}", "-cp", cp + ":" + str(work),
                        "pcgen.gui2.facade.PcgenHedgewitch", str(source), str(work / "export.txt"),
                        str(work / (gate + ".txt")), "config.ini", gate, str(saved),
                        (work / "profile.txt").read_text() if (work / "profile.txt").exists() else "general"],
                       cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=110, check=True)
    validate_gate(log, gate)
    print("PASS:", gate)


if __name__ == "__main__":
    main()