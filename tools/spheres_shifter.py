"""Pinned Shifter bestial-trait prerequisites and persistent effects."""
import re


def key(title):
    return re.sub(r"\s*\[[^]]+\]", "", title).strip().replace(",", " -").replace(";", " or").replace(":", " -")


def option_tags(title, options):
    names = {re.split(r" \(| \[", name)[0].lower(): key(name) for name, _ in options}
    aliases = {"improved adaptation": "adaptation, improved",
               "permanent greater size change": "permanent size change, greater",
               "incredible permanent size change": "permanent size change, incredible"}
    level = 2
    tags = []

    def prerequisite(clause):
        clause = clause.strip().removesuffix(" bestial trait")
        if " or " in clause:
            return "PREMULT:1," + ",".join("[" + prerequisite(part) + "]" for part in clause.split(" or "))
        if clause == "darkvision":
            return "PREVISION:1,Darkvision=ANY"
        if clause == "huge size":
            return "PRESIZEGTEQ:H"
        if clause == "endurance":
            return "PREFEAT:1,Endurance"
        name = aliases.get(clause, clause)
        if name not in names:
            raise ValueError("Unreviewed Shifter requirement: " + clause)
        return "PREABILITY:1,CATEGORY=Shifter Bestial Trait,Shifter " + names[name]

    match = re.search(r"\(requires ([^)]+)\)", title, re.I)
    if match:
        for clause in match[1].lower().split(","):
            minimum = re.fullmatch(r"shifter(?: level)? (\d+)(?:th)?", clause.strip())
            if minimum:
                level = max(level, int(minimum[1]))
            else:
                tags.append(prerequisite(clause))
    tags.insert(0, f"PREVARGTEQ:SPHERES_SHIFTER_LEVEL,{level}")
    name = re.split(r" \(| \[", title)[0]
    repeated = ("Animal Hide", "Bestial Speed", "Combat Talent", "Champion", "Quick Healing")
    if name in repeated:
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE"])
    effects = {
        "Animal Hide": ["BONUS:COMBAT|AC|1|TYPE=NaturalArmor.STACK"],
        "Bestial Speed": ["BONUS:MOVEADD|TYPE.All|10"],
        "Animal Trainer": ["BONUS:SKILL|Handle Animal|floor(SPHERES_SHIFTER_LEVEL/2)"],
        "Track Master": ["BONUS:SKILL|Survival|max(1,floor(SPHERES_SHIFTER_LEVEL/2))"],
        "Jumper": ["BONUS:SITUATION|Acrobatics=Jump|SPHERES_SHIFTER_LEVEL"],
        "Spider Climb": ["MOVE:Climb,30"],
        "Spider Climb, Improved": ["BONUS:MOVEADD|TYPE.Climb|10"],
        "Home in the Underground": ["MOVE:Burrow,20"],
        "Home in Water": ["MOVE:Swim,30"],
        "Flight": ["MOVE:Fly,30", "BONUS:VAR|Maneuverability|1|TYPE=Base.REPLACE"],
        "Flight, Perfect": ["BONUS:VAR|Maneuverability|floor(SPHERES_SHIFTER_LEVEL/6)|PREMOVE:1,Fly=1"],
        "Superior Senses": ["VISION:Blindsense (15')"],
        "Nightvision": ["VISION:Darkvision (30')", "BONUS:VISION|Darkvision|30"],
        "Scent": ["VISION:Scent (30')"],
        "See in Darkness": ["VISION:See in Darkness"],
        "Sprint": ["ABILITY:FEAT|AUTOMATIC|Run"],
        "Snatch": ["ABILITY:FEAT|AUTOMATIC|Snatch"],
        "Animal Advisor": ["DEFINE:FamiliarMasterLVL|0",
                           "ABILITY:Internal|AUTOMATIC|Standard Familiar List",
                           "BONUS:VAR|FamiliarMasterLVL|SPHERES_SHIFTER_LEVEL|TYPE=Base.STACK",
                           "FOLLOWERS:Familiar|1"],
        "Multiattack": ["ABILITY:FEAT|AUTOMATIC|Multiattack"],
        "Magical Attacks": ["BONUS:COMBAT|TOHIT.Natural,DAMAGE.Natural|1+floor(SPHERES_SHIFTER_LEVEL/5)|TYPE=Enhancement"],
        "Evasion": ["ABILITY:Special Ability|AUTOMATIC|Evasion"],
        "Improved Evasion": ["ABILITY:Special Ability|AUTOMATIC|Improved Evasion"],
        "Learned Behavior": ["ABILITY:Spheres Magic Talent|AUTOMATIC|Alteration - Mimicry"],
        "Combat Talent": ["BONUS:VAR|SPHERES_COMBAT_TALENTS|1"],
        "Champion": ["BONUS:ABILITYPOOL|Shifter Champion Feat|1"],
        "Quick Healing": ["BONUS:VAR|SPHERES_SHIFTER_QUICK_HEALING_HP|5*floor(SPHERES_SHIFTER_LEVEL/2)"],
    }
    tags.extend(effects.get(name, []))
    if name in ("Bite", "Claws", "Gore"):
        tags.extend(f"ABILITY:Special Ability|AUTOMATIC|Shifter {name} Natural Weapons {size}|PRESIZEEQ:{size}"
                    for size in ("F", "D", "T", "S", "M", "L", "H", "G", "C"))
    if name == "Adaptation, Improved":
        tags.append("BONUS:VAR|AcidResistanceBonus,ColdResistanceBonus,ElectricityResistanceBonus,FireResistanceBonus,SonicResistanceBonus|SPHERES_SHIFTER_LEVEL|TYPE=Resistance")
    if name == "Adaptation, Greater":
        tags.extend(["MULT:YES", "STACK:NO", "CHOOSE:NUMCHOICES=5|STRING|Acid|Cold|Electricity|Fire|Sonic",
                     "BONUS:VAR|ShifterImmunity %LIST|1"])
        tags.extend(f"ABILITY:Special Ability|AUTOMATIC|Immunity to {energy}|PREVARGTEQ:ShifterImmunity {energy},1"
                    for energy in ("Acid", "Cold", "Electricity", "Fire", "Sonic"))
    if name == "Fortification":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "PREVARLT:SPHERES_SHIFTER_FORTIFICATION_COUNT,min(3,floor(SPHERES_SHIFTER_LEVEL/6))",
                     "BONUS:VAR|SPHERES_SHIFTER_FORTIFICATION_COUNT|1",
                     "BONUS:VAR|SPHERES_SHIFTER_FORTIFICATION_PERCENT|25"])
    if name == "Flight, Skillful":
        tags.extend(["MULT:YES", "STACK:NO",
                     "CHOOSE:NUMCHOICES=3|STRING|Flyby Attack|Hover|Wingover",
                     "BONUS:VAR|ShifterFlightFeat %LIST|1"])
    if name == "Improved Natural Attack":
        tags.extend(["MULT:YES", "STACK:NO", "PREWEAPONPROF:1,TYPE.Natural",
                     "CHOOSE:WEAPONPROFICIENCY|PC,TYPE=Natural",
                     "BONUS:WEAPONPROF=%LIST|DAMAGESIZE|1"])
    if name == "Shifting Style":
        # Knowledge of Many Shapes belongs to the excluded Apex archetype.
        # Reserve an explicit capability rather than silently waive it.
        tags.append("PREVARGTEQ:SPHERES_KNOWLEDGE_OF_MANY_SHAPES,1")
    if name == "Fast Healing":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "PREVARLT:SPHERES_SHIFTER_FAST_HEALING_COUNT,2",
                     "BONUS:VAR|SPHERES_SHIFTER_FAST_HEALING_COUNT|1"])
    if name == "Breath Weapon":
        tags.extend(["BONUS:ABILITYPOOL|Shifter Breath Weapon Configuration|1",
                     "DEFINE:SPHERES_SHIFTER_BREATH_DICE|0",
                     "BONUS:VAR|SPHERES_SHIFTER_BREATH_DICE|floor((SPHERES_SHIFTER_LEVEL+1)/2)",
                     "DEFINE:SPHERES_SHIFTER_BREATH_DC|0",
                     "BONUS:VAR|SPHERES_SHIFTER_BREATH_DC|10+floor(SPHERES_SHIFTER_LEVEL/2)+SPHERES_CASTING_ABILITY"])
    if name == "Breath Weapon, Improved":
        tags.append("BONUS:VAR|SPHERES_SHIFTER_BREATH_IMPROVED|1")
    return tags


def breath_configuration():
    category = "Shifter Breath Weapon Configuration"
    categories = (f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\tEDITPOOL:NO\t"
                  "FRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Spheres")
    abilities = []
    for energy in ("Acid", "Cold", "Electricity", "Fire"):
        for shape, distance in (("Cone", 30), ("Line", 60)):
            abilities.append(
                f"Shifter Breath {energy} {shape}\tCATEGORY:{category}\t"
                "PREABILITY:1,CATEGORY=Shifter Bestial Trait,Shifter Breath Weapon (Su)\t"
                "PREVARLT:SPHERES_SHIFTER_BREATH_CONFIGURED,1\t"
                "BONUS:VAR|SPHERES_SHIFTER_BREATH_CONFIGURED|1\t"
                f"BONUS:VAR|SPHERES_SHIFTER_BREATH_RANGE|{distance}*(1+SPHERES_SHIFTER_BREATH_IMPROVED)\t"
                f"DESC:{energy} breath in a {shape.lower()}; range %1 ft.; %2d%3 damage; Reflex DC %4 half. "
                "Base cooldown 1d4 rounds; Improved Breath Weapon permits use once per round. "
                "Resolve damage and cooldown at the table.|SPHERES_SHIFTER_BREATH_RANGE|SPHERES_SHIFTER_BREATH_DICE|"
                "8+2*SPHERES_SHIFTER_BREATH_IMPROVED|SPHERES_SHIFTER_BREATH_DC")
    return categories, abilities


def champion_category():
    return ("ABILITYCATEGORY:Shifter Champion Feat\tCATEGORY:FEAT\tTYPE:Champion\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Feats")


def natural_weapons():
    """Explicit size-qualified attacks avoid PCGen's default Medium weapons."""
    lines = ["# Generated Shifter natural attacks; qualified by current size."]
    for name, weapon, count, die, damage in (
        ("Bite", "Bite", 1, "1d6", "Bludgeoning.Piercing.Slashing"),
        ("Claws", "Claw", 2, "1d4", "Slashing"),
        ("Gore", "Gore", 1, "1d6", "Piercing"),
    ):
        dice = ("0", "1", "1d2", "1d3", "1d4", "1d6", "1d8", "2d6", "3d6") if die == "1d4" else (
            "1", "1d2", "1d3", "1d4", "1d6", "1d8", "2d6", "3d6", "4d6")
        for size, damage_die in zip(("F", "D", "T", "S", "M", "L", "H", "G", "C"), dice):
            lines.append(f"Shifter {name} Natural Weapons {size}\tCATEGORY:Special Ability\tVISIBLE:NO\tPRESIZEEQ:{size}\t"
                         f"NATURALATTACKS:{weapon},Weapon.Natural.Melee.Finesseable.Weapon Group Natural.{damage},*{count},{damage_die}")
    return "\n".join(lines) + "\n"


def class_features():
    """Return level-gated persistent grants; transformation execution stays manual."""
    return [
        (1, "Wild Empathy", ["ABILITY:Special Ability|AUTOMATIC|Wild Empathy",
                             "BONUS:VAR|WildEmpathyLVL|SPHERES_SHIFTER_LEVEL"]),
        (3, "Endurance", ["ABILITY:FEAT|AUTOMATIC|Endurance"]),
        (7, "Enhanced Physicality", ["BONUS:STAT|CON|2+2*floor((SPHERES_SHIFTER_LEVEL-7)/6)|TYPE=Inherent"]),
        (8, "Poison Immunity", ["ABILITY:Special Ability|AUTOMATIC|Immunity to Poison"]),
        (12, "Disease Immunity", ["ABILITY:Special Ability|AUTOMATIC|Immunity to Disease"]),
    ]