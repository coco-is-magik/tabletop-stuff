"""Elementalist class source progression and live PCGen save/reload gate."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from spheres import compare_export


def fixture(level):
    if level not in range(1, 21):
        raise ValueError("Expected Elementalist level 1-20")
    lines = ["PCGVERSION:2.0", "CAMPAIGN:Core Rulebook|CAMPAIGN:Spheres PF1e - Architecture Prototype",
             "VERSION:6.08.00", "GAMEMODE:Pathfinder_RPG", "CHARACTERNAME:Elementalist progression",
             "STAT:STR|SCORE:10", "STAT:DEX|SCORE:10", "STAT:CON|SCORE:10",
             "STAT:INT|SCORE:18", "STAT:WIS|SCORE:10", "STAT:CHA|SCORE:10",
             "ALIGN:TN", "RACE:Human", f"CLASS:Elementalist|LEVEL:{level}|SKILLPOOL:0"]
    lines.extend(f"CLASSABILITIESLEVEL:Elementalist={i}|HITPOINTS:8|SKILLSGAINED:0|SKILLSREMAINING:0"
                 for i in range(1, level + 1))
    lines.extend(["EXPERIENCE:0", "ABILITY:Spheres Casting Ability|TYPE:NORMAL|CATEGORY:Spheres Casting Ability|KEY:Intelligence Casting",
                  "ABILITY:Spheres Magic Talent|TYPE:NORMAL|CATEGORY:Spheres Magic Talent|KEY:Searing Blast"])
    if level >= 3:
        lines.append("ABILITY:Elementalist Favored Element|TYPE:NORMAL|CATEGORY:Elementalist Favored Element|KEY:Favored Element (Manual)|APPLIEDTO:Fire")
    if level >= 9:
        lines.append("ABILITY:Elementalist Favored Element|TYPE:NORMAL|CATEGORY:Elementalist Favored Element|KEY:Favored Element (Manual)|APPLIEDTO:Cold")
    if level >= 15:
        lines.append("ABILITY:Elementalist Favored Element|TYPE:NORMAL|CATEGORY:Elementalist Favored Element|KEY:Favored Element (Manual)|APPLIEDTO:Electricity")
    if level >= 7:
        lines.append("ABILITY:Elementalist Movement|TYPE:NORMAL|CATEGORY:Elementalist Movement|KEY:Elementalist Land Speed")
    if level >= 13:
        lines.append("ABILITY:Elementalist Movement|TYPE:NORMAL|CATEGORY:Elementalist Movement|KEY:Elementalist Swim")
    if level >= 19:
        lines.append("ABILITY:Elementalist Movement|TYPE:NORMAL|CATEGORY:Elementalist Movement|KEY:Elementalist Fly")
    return "\n".join(lines) + "\n"


def expected(level):
    if level not in range(1, 21):
        raise ValueError("Expected Elementalist level 1-20")
    mid = level * 3 // 4
    return {"level": level, "bab": mid, "fortitude": 2 + level // 2,
            "reflex": 2 + level // 2, "will": 2 + level // 2,
            "magic_talents": 2 + mid, "caster_level": mid,
            "spell_points": level + 4, "destruction_cl": level,
            "combat_feats": 0 if level < 2 else 1 + (level - 2) // 4,
            "dodge": level // 4, "resistance": 0 if level < 5 else 20 if level == 20 else 5 + 5 * ((level - 5) // 6),
            "land": 0 if level < 7 else 20 + 10 * ((level - 7) // 6)}


def run(level):
    work = workspace()
    cp = classpath()
    template = work / "elementalist-export.txt"
    template.write_text("level=|TOTALLEVELS|\nbab=|VAR.BAB.INTVAL|\n"
                        "fortitude=|CHECK.FORTITUDE.TOTAL|\nreflex=|CHECK.REFLEX.TOTAL|\n"
                        "will=|CHECK.WILL.TOTAL|\nmagic_talents=|VAR.SPHERES_MAGIC_TALENTS.INTVAL|\n"
                        "caster_level=|VAR.SPHERES_CASTER_LEVEL.INTVAL|\n"
                        "spell_points=|VAR.SPHERES_SPELL_POINTS.INTVAL|\n"
                        "destruction_cl=|VAR.SPHERES_CL_DESTRUCTION.INTVAL|\n"
                        "combat_feats=|VAR.SPHERES_ELEMENTALIST_COMBAT_FEATS.INTVAL|\n"
                        "dodge=|VAR.SPHERES_ELEMENTALIST_DODGE.INTVAL|\n"
                        "resistance=|VAR.SPHERES_ELEMENTALIST_RESISTANCE.INTVAL|\n"
                        "land=|VAR.SPHERES_ELEMENTALIST_LAND.INTVAL|\n")
    character = work / "elementalist.pcg"
    character.write_text(fixture(level))
    saved = work / "saved.pcg"
    print(f"Elementalist class evidence: {work}", flush=True)
    for source, destination, export in ((character, saved, "first"), (saved, None, "reload")):
        output = work / f"{export}.txt"
        log = work / f"{export}.log"
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp, "--source", "16", str(ROOT / "tools/PcgenSpheresExport.java"),
                   str(source), str(template), str(output), "config.ini"]
        if destination is not None:
            command.append(str(destination))
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=90, check=True)
        if not output.exists():
            raise ValueError(f"No PCGen export; inspect {log}")
        if "SEVERE:" in log.read_text() or "LSTERROR:" in log.read_text():
            raise ValueError(f"PCGen load errors; inspect {log}")
        compare_export(output.read_text().replace("=+", "="), expected(level))
        if destination is not None and not saved.is_file():
            raise ValueError(f"PCGen did not save the character; inspect {log}")
        if destination is None:
            text = saved.read_text()
            favored = ("Fire", "Cold", "Electricity")[:sum(level >= n for n in (3, 9, 15))]
            if favored and f"APPLIEDTO:{','.join(favored)}" not in text:
                raise ValueError("Missing saved favored element choices")
            movements = ("Elementalist Land Speed", "Elementalist Swim", "Elementalist Fly")
            for name in movements[:sum(level >= n for n in (7, 13, 19))]:
                if f"KEY:{name}" not in text:
                    raise ValueError(f"Missing saved movement choice: {name}")
    print(f"PASS: Elementalist level {level} and save/reload")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", type=int, choices=range(1, 21), required=True)
    args = parser.parse_args()
    try:
        run(args.level)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"elementalist: {error}\n")


if __name__ == "__main__":
    main()