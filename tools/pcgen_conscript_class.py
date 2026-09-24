"""Thin Conscript real-PCGen acceptance, one bounded character round trip."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from pcgen_incanter_class import validate_chassis


PURCHASES = ((), ("Gear Training",), ("Fast Movement",),
             ("Fast Movement", "Indomitable Will"),
             ("Fast Movement", "Indomitable Will", "Evasion"),
             ("Fast Movement", "Indomitable Will", "Evasion", "Gear Training"))
TALENTS = (2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 23, 24, 26, 27, 29, 30)


def fixture(level, mental="WIS", points=0):
    if level not in range(1, 21) or mental not in ("INT", "WIS", "CHA") or points not in range(6):
        raise ValueError("Expected level 1-20, mental ability, budget 0-5")
    lines = ["PCGVERSION:2.0", "CAMPAIGN:Core Rulebook|CAMPAIGN:Spheres PF1e - Architecture Prototype",
             "VERSION:6.08.00", "GAMEMODE:Pathfinder_RPG", f"CHARACTERNAME:Conscript {level} {mental}"]
    lines.extend(f"STAT:{stat}|SCORE:{18 if stat == mental else 10}" for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"))
    lines.extend(["ALIGN:TN", "RACE:Human", f"CLASS:Conscript|LEVEL:{level}|SKILLPOOL:0"])
    lines.extend(f"CLASSABILITIESLEVEL:Conscript={i}|HITPOINTS:10|SKILLSGAINED:0|SKILLSREMAINING:0" for i in range(1, level + 1))
    name = {"INT": "Intelligence", "WIS": "Wisdom", "CHA": "Charisma"}[mental]
    lines.append(f"ABILITY:Conscript Practitioner Ability|TYPE:NORMAL|CATEGORY:Conscript Practitioner Ability|KEY:{name} Practitioner")
    for choice in PURCHASES[points]:
        lines.append(f"ABILITY:Conscript Specialization|TYPE:NORMAL|CATEGORY:Conscript Specialization|KEY:Conscript {choice}")
    lines.append("ABILITY:Spheres Combat Talent|TYPE:NORMAL|CATEGORY:Spheres Combat Talent|KEY:Combat Talent (Manual)|APPLIEDTO:Athletics")
    lines.append("ABILITY:Conscript Class Skill|TYPE:NORMAL|CATEGORY:Conscript Class Skill|KEY:Conscript Additional Class Skill|APPLIEDTO:Acrobatics,Stealth,Bluff")
    lines.append("ABILITY:Conscript Martial Tradition|TYPE:NORMAL|CATEGORY:Conscript Martial Tradition|KEY:Martial Tradition (Manual)|APPLIEDTO:Custom tradition record")
    return "\n".join(lines) + "\n"


def expected(level, mental, points):
    fixture(level, mental, points)  # Validate before indexing the independent table.
    return {"level": level, "bab": level, "fortitude": 2 + level // 2,
            "reflex": 2 + level // 2,
            "will": (2 + level // 2 if points >= 3 else level // 3) + (4 if mental == "WIS" else 0)}


def run(level, mental, points, features=None):
    text = fixture(level, mental, points)
    if features:
        if points != 4:
            raise ValueError("Resource feature profile requires --points 4")
        text = "\n".join(line for line in text.splitlines() if not line.startswith("ABILITY:Conscript Specialization|")) + "\n"
        names = (("Banner", "Inspiration", "Armor Training", "Resolve") if features == "resources"
                 else ("Sneak Attack", "Studied Target"))
        for name in names:
            text += f"ABILITY:Conscript Specialization|TYPE:NORMAL|CATEGORY:Conscript Specialization|KEY:Conscript {name}\n"
    work = workspace()
    cp = classpath()
    character = work / "conscript.pcg"
    character.write_text(text)
    template = work / "class-export.txt"
    template.write_text("level=|TOTALLEVELS|\nbab=|VAR.BAB.INTVAL|\nfortitude=|CHECK.FORTITUDE.TOTAL|\nreflex=|CHECK.REFLEX.TOTAL|\nwill=|CHECK.WILL.TOTAL|\n")
    print(f"Conscript evidence: {work}", flush=True)
    with (work / "compile.log").open("w") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16", "-cp", cp,
                        "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java"), str(ROOT / "tools/PcgenConscript.java")],
                       stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    saved = work / "saved.pcg"
    for gate, source in (("conscript-save", character), ("conscript-reload", saved)):
        output = work / f"{gate}.txt"
        log = work / f"{gate}.log"
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenConscript", str(source),
                   str(template), str(output), "config.ini", gate, str(saved)]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, timeout=90, check=True)
        validate_gate(log, gate)
        validate_chassis(output.read_text(), expected(level, mental, 0 if features else points))
    print(f"PASS: Conscript {level} {mental}, budget {points}: math, choices, feats, reload/refund")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", type=int, choices=range(1, 21), required=True)
    parser.add_argument("--mental", choices=("INT", "WIS", "CHA"), default="WIS")
    parser.add_argument("--points", type=int, choices=range(6), default=0)
    parser.add_argument("--features", nargs="?", const="resources", choices=("resources", "precision"),
                        help="Test class resources or Sneak Attack/Studied Target instead of budget profile")
    args = parser.parse_args()
    try:
        run(args.level, args.mental, args.points, args.features)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"conscript: {error}\n")


if __name__ == "__main__":
    main()