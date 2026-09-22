"""PCG calculation fixtures only; PCGen remains the rules evaluator."""

# Independent expectations transcribed from the current Incanter progression.
# Total includes the first-casting two talents, but no bonus-feat purchases.
TALENTS = (4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 26, 28, 29, 31, 32)


def fixture(level, casting="INT"):
    if level not in range(1, 21) or casting not in ("INT", "WIS", "CHA"):
        raise ValueError("Expected Incanter level 1-20 and INT/WIS/CHA")
    stats = {"STR": 10, "DEX": 10, "CON": 10, "INT": 12, "WIS": 8, "CHA": 10}
    stats[casting] = 18
    lines = ["PCGVERSION:2.0",
             "CAMPAIGN:Core Rulebook|CAMPAIGN:Spheres PF1e - Architecture Prototype",
             "VERSION:6.08.00", "GAMEMODE:Pathfinder_RPG",
             f"CHARACTERNAME:Incanter progression {level} {casting}"]
    lines.extend(f"STAT:{stat}|SCORE:{score}" for stat, score in stats.items())
    lines.extend(["ALIGN:TN", "RACE:Human",
                  f"CLASS:Incanter (Spheres Prototype)|LEVEL:{level}|SKILLPOOL:0"])
    lines.extend(f"CLASSABILITIESLEVEL:Incanter (Spheres Prototype)={i}|HITPOINTS:6|SKILLSGAINED:0|SKILLSREMAINING:0"
                 for i in range(1, level + 1))
    lines.extend(["EXPERIENCE:0",
                  "ABILITY:Spheres Magic Talent|TYPE:NORMAL|CATEGORY:Spheres Magic Talent|KEY:Destruction Sphere",
                  "ABILITY:Spheres Magic Talent|TYPE:NORMAL|CATEGORY:Spheres Magic Talent|KEY:Searing Blast"])
    name = {"INT": "Intelligence", "WIS": "Wisdom", "CHA": "Charisma"}[casting]
    lines.append(f"ABILITY:Spheres Casting Ability|TYPE:NORMAL|CATEGORY:Spheres Casting Ability|KEY:{name} Casting")
    return "\n".join(lines) + "\n"


def expected(level):
    if level not in range(1, 21):
        raise ValueError("Expected Incanter level 1-20")
    return {"magic_talents": TALENTS[level - 1], "caster_level": level,
            "casting_modifier": 4, "magic_skill_bonus": level, "spell_points": level + 4,
            "destruction_cl": level, "destruction_dc": 14 + level // 2,
            "blast_dice": (level + 1) // 2, "boosted_blast_dice": max(2, level),
            "blast_range": 25 + 5 * (level // 2)}