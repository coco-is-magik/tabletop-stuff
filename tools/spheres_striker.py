"""Base Striker art prerequisites and persistent tension capacities, not combat state."""
import re

LEVEL = "SPHERES_STRIKER_LEVEL"


def option_tags(title):
    level = 2
    tags = []
    requirement = re.search(r"\(requires ([^)]+)\)", title, re.IGNORECASE)
    if requirement:
        clause = requirement[1].lower()
        match = re.fullmatch(r"striker (\d+)", clause)
        if match:
            level = max(level, int(match[1]))
        elif clause in ("iron soul", "adrenaline rush"):
            tags.append("PREABILITY:1,CATEGORY=Striker Striker Art,Striker " + clause.title())
        else:
            raise ValueError("Unreviewed Striker Art prerequisite: " + clause)
    tags.insert(0, f"PREVARGTEQ:{LEVEL},{level}")
    name = re.sub(r"\s*\[[^]]+\]", "", title).split(" (")[0]
    if name in ("High Tension", "Extra Boost"):
        suffix = "HIGH_TENSION" if name == "High Tension" else "EXTRA_BOOST"
        counter = "SPHERES_STRIKER_" + suffix
        resource = "MAX_TENSION" if name == "High Tension" else "TENSION_BOOST"
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     f"PREVARLT:{counter},1+floor(({LEVEL}-5)/6)",
                     f"BONUS:VAR|{counter}|1", f"BONUS:VAR|SPHERES_STRIKER_{resource}|1|PREVARLT:{LEVEL},20"])
    elif name == "True Desperation":
        tags.append("BONUS:VAR|SPHERES_STRIKER_DESPERATE_TENSION|1")
    return tags


def resource_tags():
    tags = ["DEFINE:SPHERES_STRIKER_HIGH_TENSION|0", "DEFINE:SPHERES_STRIKER_EXTRA_BOOST|0"]
    # A zero finite cap at level 20 is meaningful only with UNLIMITED_TENSION=1.
    for name, formula in (("MAX_TENSION", f"if({LEVEL}>=20,0,max(1,CON)+floor({LEVEL}/3))"),
                          ("UNLIMITED_TENSION", f"if({LEVEL}>=20,1,0)"),
                          ("TENSION_COST_REDUCTION", f"if({LEVEL}>=20,1,0)"),
                          ("RISING_TENSION", f"if({LEVEL}<10,0,if({LEVEL}<16,1,2))"),
                          ("TENSION_BOOST", f"if({LEVEL}>=20,7,if({LEVEL}<2,0,1+floor(({LEVEL}-1)/6)))"),
                          ("DESPERATE_TENSION", f"if({LEVEL}<4,0,1)")):
        tags.extend([f"DEFINE:SPHERES_STRIKER_{name}|0", f"BONUS:VAR|SPHERES_STRIKER_{name}|{formula}"])
    return tags


def training_records(source):
    section = next(s for s in source['sections'] if s['heading'] == 'Tension Training (Ex)')
    names = ('Critical Offense', 'Deadly Offense', 'Deceptive Taunt', 'Threatening Taunt', 'Victorious Defense')
    choices = []
    for name in names:
        match = re.search(re.escape(name) + r': (.*?)(?=\n[A-Z]|$)', section['text'], re.S)
        if not match:
            raise ValueError('Missing tension training rule: ' + name)
        description = ' '.join(match[1].split()).replace('|', '/')
        choices.append(f'Striker Training - {name}\tCATEGORY:Striker Tension Training\t'
                       f'PREVARGTEQ:{LEVEL},5\tDESC:{description} '
                       'Apply once per round in combat; target must not be helpless or unaware '
                       'and must have at least half your character level in Hit Dice.')
    category = ('ABILITYCATEGORY:Striker Tension Training\tCATEGORY:Striker Tension Training\t'
                'EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\t'
                f'POOL:max(0,1+floor(({LEVEL}-5)/6))\tPLURAL:Tension Training\tDISPLAYLOCATION:Spheres')
    return category, choices