"""Live PCGen class-table arithmetic and save/reload for Spheres base classes."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from spheres import compare_export
from spheres_class_catalog import NAMES, class_name, generate


def fixture(slug, level):
    if slug not in NAMES or level not in range(1, 21):
        raise ValueError("Expected a catalog base class and level 1-20")
    name = class_name(slug)
    lines = ["PCGVERSION:2.0", "CAMPAIGN:Core Rulebook|CAMPAIGN:Spheres PF1e - Architecture Prototype",
             "VERSION:6.08.00", "GAMEMODE:Pathfinder_RPG", f"CHARACTERNAME:{name} progression",
             "STAT:STR|SCORE:10", "STAT:DEX|SCORE:10", "STAT:CON|SCORE:10",
             "STAT:INT|SCORE:10", "STAT:WIS|SCORE:10", "STAT:CHA|SCORE:10",
             "ALIGN:TN", "RACE:Human", f"CLASS:{name}|LEVEL:{level}|SKILLPOOL:0"]
    hd = int(generate(slug)[0].split("HD:", 1)[1].split("\t", 1)[0])
    lines += [f"CLASSABILITIESLEVEL:{name}={i}|HITPOINTS:{hd}|SKILLSGAINED:0|SKILLSREMAINING:0"
              for i in range(1, level + 1)]
    lines.append("EXPERIENCE:0")
    if slug == "soul-weaver":
        lines.append("ABILITY:Soul Weaver Channel|TYPE:NORMAL|CATEGORY:Soul Weaver Channel|KEY:Soul Weaver Positive Channel")
    if slug == "armiger":
        lines.append("ABILITY:Armiger Practitioner Ability|TYPE:NORMAL|CATEGORY:Armiger Practitioner Ability|KEY:Armiger Wisdom Practitioner")
    if slug == "hedgewitch":
        lines.extend(("ABILITY:Hedgewitch Path|TYPE:NORMAL|CATEGORY:Hedgewitch Path|KEY:Hedgewitch Academia",
                      "ABILITY:Hedgewitch Path|TYPE:NORMAL|CATEGORY:Hedgewitch Path|KEY:Hedgewitch Astrology"))
    if slug == "wraith":
        lines.append("ABILITY:Wraith Haunt Path|TYPE:NORMAL|CATEGORY:Wraith Haunt Path|KEY:Wraith Path of the Shadow")
    if slug == "striker":
        lines.append("ABILITY:Striker Bare Knuckles|TYPE:NORMAL|CATEGORY:Striker Bare Knuckles|KEY:Striker Boxing Knuckles")
    representative = {
        "armorist": (2, "Armorist Arsenal Trick", "Armorist Additional Binding (requires bound equipment)"),
        "eliciter": (2, "Eliciter Emotion", "Eliciter Apathy"),
        "mageknight": (2, "Mageknight Mystic Combat", "Mageknight Arcane Weapon Focus (Su)"),
        "shifter": (2, "Shifter Bestial Trait", "Shifter Adaptation (Ex)"),
        "thaumaturge": (1, "Thaumaturge Invocations", "Thaumaturge Lingering Blessing"),
        "armiger": (2, "Armiger Prowess", "Armiger Armored Armiger"),
        "commander": (2, "Commander Enhanced Tactic", "Commander Command Attack"),
        "scholar": (2, "Scholar Scholar'S Knack", "Scholar Academic Knowledge"),
        "technician": (2, "Technician Technical Insight", "Technician Aesthetic Insight"),
    }.get(slug)
    if representative and level >= representative[0]:
        _, category, key = representative
        lines.append(f"ABILITY:{category}|TYPE:NORMAL|CATEGORY:{category}|KEY:{key}")
    return "\n".join(lines) + "\n"


def expected(slug, level):
    if slug not in NAMES or level not in range(1, 21):
        raise ValueError("Expected a catalog base class and level 1-20")
    source = generate(slug)[3]
    result = {"level": level, "bab": source["bab"][level - 1],
              "fortitude": source["saves"][0][level - 1],
              "reflex": source["saves"][1][level - 1],
              "will": source["saves"][2][level - 1],
              "talents": source["talents"][level - 1] + (2 if source["magic"] else 0)
                         + (1 if slug == "mageknight" else 0)}
    if source["magic"]:
        result["caster_level"] = source["caster"][level - 1]
        result["spell_points"] = level
    return result


def run(slug, level):
    source = generate(slug)[3]
    work = workspace()
    character = work / "class.pcg"
    character.write_text(fixture(slug, level))
    template = work / "class-export.txt"
    template.write_text("level=|TOTALLEVELS|\nbab=|VAR.BAB.INTVAL|\n"
                        "fortitude=|CHECK.FORTITUDE.TOTAL|\nreflex=|CHECK.REFLEX.TOTAL|\n"
                        "will=|CHECK.WILL.TOTAL|\n"
                        f"talents=|VAR.{'SPHERES_MAGIC_TALENTS' if source['magic'] else 'SPHERES_COMBAT_TALENTS'}.INTVAL|\n" +
                        ("caster_level=|VAR.SPHERES_CASTER_LEVEL.INTVAL|\n"
                         "spell_points=|VAR.SPHERES_SPELL_POINTS.INTVAL|\n" if source["magic"] else ""))
    prefix = "SPHERES_" + slug.replace("-", "_").upper()
    reference = {"armorist": ("BOUND_ITEMS", lambda n: 1 + n // 5),
                 "eliciter": ("PERSUASIVE", lambda n: 2 + n // 6),
                 "fey-adept": ("SHADOWMARK_DICE", lambda n: (n + 1) // 2),
                 "mageknight": ("RESIST_MAGIC", lambda n: 1 + (n - 1) // 4),
                 "soul-weaver": ("CHANNEL_DICE", lambda n: (n + 1) // 2),
                 "symbiat": ("PSIONICS_ROUNDS", lambda n: 4 + 2 * (n - 1)),
                 "thaumaturge": ("FORBIDDEN_LORE", lambda n: 2 + (n - 1) // 4),
                 "armiger": ("TALENTS_PER_CUSTOMIZED_WEAPON", lambda n: (n + 1) // 4 + 1),
                 "blacksmith": ("THUNDEROUS_BLOWS_DICE", lambda n: (n + 1) // 2),
                 "sentinel": ("RESERVE_POINTS", lambda n: max(1, n // 2)),
                 "technician": ("TRAPFINDING", lambda n: max(1, n // 2))}.get(slug)
    values = expected(slug, level)
    if reference:
        suffix, formula = reference
        template.write_text(template.read_text() + f"reference=|VAR.{prefix}_{suffix}.INTVAL|\n")
        values["reference"] = formula(level)
    saved = work / "saved.pcg"
    print(f"{slug} {level} evidence: {work}", flush=True)
    cp = classpath()
    required = {"eliciter": "M:Mind", "fey-adept": "M:Illusion", "shifter": "M:Alteration",
                "symbiat": "M:Mind,M:Telekinesis", "soul-weaver": "M:Life",
                "sentinel": "C:Guardian", "wraith": "M:Dark", "striker": "C:Boxing",
                "commander": "C:Warleader", "technician": "C:Trap",
                "scholar": "C:Alchemy,C:Scout"}.get(slug, "-")
    choice = {"hedgewitch": "Hedgewitch Path:Hedgewitch Academia",
              "wraith": "Wraith Haunt Path:Wraith Path of the Shadow",
              "striker": "Striker Bare Knuckles:Striker Boxing Knuckles",
              "armiger": "Armiger Practitioner Ability:Armiger Wisdom Practitioner",
              "soul-weaver": "Soul Weaver Channel:Soul Weaver Positive Channel"}.get(slug, "-")
    if choice == "-":
        chosen = next((line for line in fixture(slug, level).splitlines()
                       if line.startswith("ABILITY:") and "|TYPE:NORMAL|" in line), None)
        if chosen:
            choice = chosen.split("|CATEGORY:", 1)[1].split("|KEY:", 1)[0] + ":" + chosen.split("|KEY:", 1)[1]
    pools = {f"{source['name']} {group.title().replace('’', chr(39))}": sum(at <= level for at in levels)
             for group, levels in source["choices"].items()}
    if slug == "hedgewitch":
        pools["Hedgewitch Path"] = 2
    if slug == "wraith":
        pools["Wraith Haunt Path"] = 1
    if slug == "armiger":
        pools.update({"Armiger Practitioner Ability": 1,
                      "Armiger Customized Weapon": 3 + (level >= 11) + (level >= 19)})
    if slug == "soul-weaver":
        pools["Soul Weaver Channel"] = 1
    if slug == "striker":
        pools["Striker Bare Knuckles"] = 1
    if slug == "blacksmith":
        pools["Blacksmith Equipment Specialist Talent"] = 1
    if slug == "technician":
        pools["Technician Invention"] = 1 + (level >= 3) + sum(level >= n for n in (7, 11, 15, 19))
        pools["Technician Invention Base Form"] = pools["Technician Invention"]
    if slug == "thaumaturge":
        pools["Thaumaturge Bonus Feat"] = level // 4
    pool_argument = "@".join(f"{key}={value}" for key, value in pools.items()) or "-"
    for source_file, destination, phase in ((character, saved, "first"), (saved, None, "reload")):
        output = work / f"{phase}.txt"
        log = work / f"{phase}.log"
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp, "--source", "16", str(ROOT / "tools/PcgenClassCatalog.java"),
                   str(source_file), str(template), str(output), "config.ini", required, choice, pool_argument]
        if destination:
            command.append(str(destination))
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=90, check=True)
        diagnostics = log.read_text()
        if "LSTERROR:" in diagnostics or "SEVERE:" in diagnostics or not output.is_file():
            raise ValueError(f"PCGen class load failed; inspect {log}")
        compare_export(output.read_text().replace("=+", "="), values)
        if destination and not saved.is_file():
            raise ValueError(f"Missing saved character; inspect {log}")
    print(f"PASS: {slug} level {level}, class table and save/reload", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", choices=NAMES)
    parser.add_argument("--level", type=int, choices=range(1, 21), default=20)
    args = parser.parse_args()
    try:
        run(args.slug, args.level)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"class catalog: {error}\n")


if __name__ == "__main__":
    main()