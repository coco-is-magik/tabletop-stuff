"""Reviewed base Armorist Arsenal Trick prerequisites and persistent grants."""
import re

LEVEL = "SPHERES_ARMORIST_LEVEL"
CATEGORY = "Armorist Arsenal Trick"


def option_tags(title):
    level = 2
    tags = []
    requirement = re.search(r"\(requires ([^)]+)\)", title)
    if requirement:
        for clause in requirement[1].split(", "):
            match = re.fullmatch(r"armorist (\d+)", clause)
            if match:
                level = max(level, int(match[1]))
            elif clause in ("bound equipment", "boost equipment class feature", "bind implement class feature",
                            "armor training or greater armor training"):
                # The supported base-class chassis grants these features at fixed levels.
                level = max(level, {"bound equipment": 1, "boost equipment class feature": 10,
                                    "bind implement class feature": 5,
                                    "armor training or greater armor training": 3}[clause])
            elif clause == "natural materials or horseman’s materials":
                tags.append("PREABILITY:1,CATEGORY=" + CATEGORY +
                            ",Armorist Natural Materials,Armorist Horseman’s Materials")
            elif clause in ("grenadier", "advanced armaments"):
                key = "Grenadier (requires armorist 6)" if clause == "grenadier" else "Advanced Armaments"
                tags.append("PREABILITY:1,CATEGORY=" + CATEGORY + ",Armorist " + key)
            else:
                raise ValueError("Unreviewed Arsenal Trick prerequisite: " + clause)
    tags.insert(0, f"PREVARGTEQ:{LEVEL},{level}")
    name = title.split(" (")[0].split(" [")[0]
    if name in ("Champion", "Combat Feat", "Crafter"):
        tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                 "BONUS:ABILITYPOOL|Armorist " + name + " Feat|1"]
    elif name == "Combat Talent":
        tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|SPHERES_COMBAT_TALENTS|1"]
    elif name == "Greater Armor Training":
        tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|SPHERES_ARMORIST_ARMOR_TRAINING|1"]
    elif name == "Additional Binding":
        tags.append("BONUS:VAR|SPHERES_ARMORIST_BOUND_ITEMS|1")
    return tags


def feat_categories():
    return [f"ABILITYCATEGORY:Armorist {name} Feat\tCATEGORY:FEAT\tTYPE:{types}\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\t"
            f"PLURAL:Armorist {name} Feats\tDISPLAYLOCATION:Feats"
            for name, types in (("Champion", "Champion"), ("Combat Feat", "Combat"),
                                ("Crafter", "ItemCreation"))]