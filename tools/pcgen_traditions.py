"""Live custom casting/martial tradition controller save/reload checks.

PCGen startup is slow on network filesystems; use the save/reload gate
arguments to split the two processes across separate invocations.
"""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture as casting_fixture
from pcgen_conscript_class import fixture as martial_fixture

TIMEOUT = 300


def run(system, gate="all", work=None):
    cp = classpath()
    work = work if work is not None else workspace()
    if not work.is_dir():
        raise ValueError("missing workspace: " + str(work))
    print("Tradition evidence:", work, flush=True)
    character = work / "tradition.pcg"
    saved = work / "saved.pcg"
    if gate != "reload":
        raw = martial_fixture(10) if system in ('might', 'drawback-martial', 'ace') else casting_fixture(10, "WIS")
        if system in ('ace', 'medic', 'liturgist', 'brew'):
            raw = martial_fixture(1)
        if system in ('halfling', 'half-orc', 'elf'):
            raw = raw.replace('RACE:Human', 'RACE:' + {'halfling': 'Halfling', 'half-orc': 'Half-Orc', 'elf': 'Elf'}[system])
        if system in ('might', 'drawback-martial', 'ace', 'medic', 'liturgist', 'brew'):
            raw = "\n".join(line for line in raw.splitlines()
                            if not line.startswith("ABILITY:Conscript Martial Tradition|")) + "\n"
        character.write_text(raw)
        (work / "export.txt").write_text("level=|TOTALLEVELS|\n")
        if not (work / "pcgen/gui2/facade/PcgenTraditions.class").is_file():
            with (work / "compile.log").open("w") as stream:
                subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                                "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                                str(ROOT / "tools/PcgenTraditions.java")],
                               stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                               timeout=30, check=True)
    gates = {"save": [("tradition-save", character)], "reload": [("tradition-reload", saved)],
             "all": [("tradition-save", character), ("tradition-reload", saved)]}[gate]
    for name, source in gates:
        log = work / (name + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenTraditions", str(source),
                   str(work / "export.txt"), str(work / (name + ".txt")), "config.ini", name, str(saved), system]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=TIMEOUT, check=True)
        validate_gate(log, name)
        print("PASS:", name)
    print("PASS:", system, "custom tradition and reload/refund")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system", choices=("power", "might", "drawback-martial", "ace", "medic", "liturgist", "brew", "racial", "halfling", "half-orc", "elf"))
    parser.add_argument("gate", nargs="?", default="all", choices=("all", "save", "reload"))
    parser.add_argument("--work", type=Path, help="existing workspace for the reload gate")
    args = parser.parse_args()
    if args.gate == "reload" and args.work is None:
        parser.error("reload requires --work from the save run")
    if args.work is not None and args.gate != "reload":
        parser.error("--work only applies to the reload gate")
    run(args.system, args.gate, args.work)
