"""Live Spheres trait pool, category, and save/reload gate."""
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture


def run():
    work = workspace()
    cp = classpath()
    print("Trait evidence:", work, flush=True)
    character = work / "traits.pcg"
    character.write_text(fixture(1).replace("CAMPAIGN:Core Rulebook|", "CAMPAIGN:Core Rulebook|CAMPAIGN:Advanced Player's Guide|"))
    template = work / "export.txt"
    template.write_text("level=|TOTALLEVELS|\n")
    with (work / "compile.log").open("w") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16", "-cp", cp,
                        "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"),
                        str(ROOT / "tools/PcgenTraits.java")], stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=30, check=True)
    saved = work / "saved.pcg"
    for gate, source in (("traits-save", character), ("traits-reload", saved)):
        log = work / (gate + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenTraits", str(source),
                   str(template), str(work / (gate + ".txt")), "config.ini", gate, str(saved)]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=55, check=True)
        validate_gate(log, gate)
    print("PASS: traits category restrictions, pool, refund, save/reload")


if __name__ == "__main__":
    run()