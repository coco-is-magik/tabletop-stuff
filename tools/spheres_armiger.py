"""Reviewed base Armiger Prowess heading gates and explicit feat grants."""
import re


def option_tags(title):
    level = 2
    tags = []
    requirement = re.search(r"\(requires (.*)\)", title, re.IGNORECASE)
    if requirement:
        clause = requirement[1].lower()
        match = re.fullmatch(r"armiger (\d+)", clause)
        if match:
            level = max(level, int(match[1]))
        elif clause in ("enhanced customization", "rapid assault"):
            level = 5
        elif clause == "leadership sphere and (cohort) package":
            tags.extend(["PREABILITY:1,CATEGORY=Spheres Combat Talent,Leadership Sphere",
                         "PREABILITY:1,CATEGORY=Spheres Leadership Package,Leadership Package - Cohort"])
        else:
            raise ValueError("Unreviewed Prowess prerequisite: " + clause)
    tags.insert(0, f"PREVARGTEQ:SPHERES_ARMIGER_LEVEL,{level}")
    name = title.split(" (")[0].split(" [")[0]
    if name == "Extra Focus":
        tags.append("ABILITY:FEAT|AUTOMATIC|Great Focus")
    elif name == "Customized Bond":
        tags.extend(["PREABILITY:1,CATEGORY=Special Ability,Armorist Bound Items (Reference)",
                     "ABILITY:FEAT|AUTOMATIC|Customized Bond"])
    elif name == "Deadly Prowess":
        tags.extend(["MULT:YES", "STACK:NO", "CHOOSE:NUMCHOICES=3|STRING|Deadly Aim|Piranha Strike|Power Attack",
                     "BONUS:VAR|ArmigerDeadly %LIST|1"])
    elif name == "Champion":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "BONUS:ABILITYPOOL|Armiger Champion Feat|1"])
    elif name == "Spell Dabbler":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "PREVARLT:SPHERES_ARMIGER_SPELL_DABBLER_COUNT,3",
                     "BONUS:VAR|SPHERES_ARMIGER_SPELL_DABBLER_COUNT|1",
                     "BONUS:ABILITYPOOL|Armiger Spell Dabbler Feat|1"])
    elif name == "Ranged Prowess":
        tags.extend(["MULT:YES", "STACK:NO", "CHOOSE:NUMCHOICES=2|STRING|Sniper|Barrage",
                     "BONUS:VAR|ArmigerRanged %LIST|1"])
    return tags


def feat_category():
    return ("ABILITYCATEGORY:Armiger Champion Feat\tCATEGORY:FEAT\tTYPE:Champion\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\t"
            "PLURAL:Armiger Champion Feats\tDISPLAYLOCATION:Feats")


def spell_dabbler_category():
    return ("ABILITYCATEGORY:Armiger Spell Dabbler Feat\tCATEGORY:FEAT\t"
            "ABILITYLIST:Basic Magic Training|Advanced Magic Training|Extra Magic Talent\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Feats")