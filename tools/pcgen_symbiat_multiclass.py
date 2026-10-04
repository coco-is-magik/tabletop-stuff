"""Live Symbiat 4 / Rogue 4 defensive stacking and retained-class round trip."""
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace, validate_result
from pcgen_class_catalog import fixture


def character_fixture():
    text = fixture("symbiat", 4)
    text += "CLASS:Rogue|LEVEL:4|SKILLPOOL:0\n"
    text += "".join(f"CLASSABILITIESLEVEL:Rogue={level}|HITPOINTS:8|SKILLSGAINED:0|SKILLSREMAINING:0\n"
                    for level in range(1, 5))
    return text


def main():
    work = workspace()
    print("Symbiat multiclass evidence:", work, flush=True)
    character = work / "mixed.pcg"
    character.write_text(character_fixture())
    template = work / "export.txt"
    template.write_text("level=|TOTALLEVELS|\ntrap=|VAR.TrapSenseBonus.INTVAL|\n"
                        "flanking=|VAR.UncannyDodgeFlankingLevel.INTVAL|\n")
    saved = work / "saved.pcg"
    for source, destination, phase in ((character, saved, "save"), (saved, None, "reload")):
        output = work / (phase + ".txt")
        log = work / (phase + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
                   f"-Dpcgen.config={work}", "-cp", classpath(), "--source", "16",
                   str(ROOT / "tools/PcgenClassCatalog.java"), str(source), str(template),
                   str(output), "config.ini", "M:Mind,M:Telekinesis", "-", "-"]
        if destination:
            command.append(str(destination))
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, timeout=110, check=True)
        validate_result(output, log, {"level": 8, "trap": 2, "flanking": 12})
    print("PASS: Symbiat/Rogue defensive stacking and save/reload")


if __name__ == "__main__":
    main()