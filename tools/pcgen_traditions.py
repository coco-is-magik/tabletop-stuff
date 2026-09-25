"""Live custom casting/martial tradition controller save/reload checks."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture as casting_fixture
from pcgen_conscript_class import fixture as martial_fixture


def run(system):
    work = workspace()
    cp = classpath()
    print("Tradition evidence:", work, flush=True)
    character = work / "tradition.pcg"
    raw = casting_fixture(10, "WIS") if system == "power" else martial_fixture(10)
    if system == "might":
        raw = "\n".join(line for line in raw.splitlines()
                        if not line.startswith("ABILITY:Conscript Martial Tradition|")) + "\n"
    character.write_text(raw)
    template = work / "export.txt"
    template.write_text("level=|TOTALLEVELS|\n")
    with (work / "compile.log").open("w") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                        "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                        str(ROOT / "tools/PcgenTraditions.java")],
                       stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                       timeout=30, check=True)
    saved = work / "saved.pcg"
    for gate, source in (("tradition-save", character), ("tradition-reload", saved)):
        log = work / (gate + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenTraditions", str(source),
                   str(template), str(work / (gate + ".txt")), "config.ini", gate, str(saved), system]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=55, check=True)
        validate_gate(log, gate)
    print("PASS:", system, "custom tradition and reload/refund")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system", choices=("power", "might"))
    run(parser.parse_args().system)