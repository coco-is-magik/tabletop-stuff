"""Live Spheres trait pool, category, and save/reload gate."""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture


def run(gate="all", work=None, profile="default", level=1):
    work = work if work is not None else workspace()
    cp = classpath()
    print("Trait evidence:", work, flush=True)
    character = work / "traits.pcg"
    if gate != "reload":
        character.write_text(fixture(level).replace("CAMPAIGN:Core Rulebook|", "CAMPAIGN:Core Rulebook|CAMPAIGN:Advanced Player's Guide|"))
    template = work / "export.txt"
    template.write_text("level=|TOTALLEVELS|\n")
    with (work / "compile.log").open("w") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16", "-cp", cp,
                        "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                        str(ROOT / "tools/PcgenTraits.java")], stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=30, check=True)
    saved = work / "saved.pcg"
    gates = {"save": [("traits-save", character)], "reload": [("traits-reload", saved)],
             "all": [("traits-save", character), ("traits-reload", saved)]}[gate]
    for gate, source in gates:
        log = work / (gate + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenTraits", str(source),
                   str(template), str(work / (gate + ".txt")), "config.ini", gate, str(saved), profile]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=110, check=True)
        validate_gate(log, gate)
        print("PASS:", gate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", nargs="?", default="all", choices=("all", "save", "reload"))
    parser.add_argument("--work", type=Path)
    parser.add_argument("--profile", choices=("default", "daysense", "steel", "destructive"), default="default")
    parser.add_argument("--level", type=int, choices=range(1, 21), default=1)
    args = parser.parse_args()
    if (args.gate == "reload") != (args.work is not None):
        parser.error("reload requires --work; --work only applies to reload")
    run(args.gate, args.work, args.profile, args.level)