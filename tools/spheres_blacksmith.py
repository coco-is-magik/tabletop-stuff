"""Reviewed Smithing Insight gates and persistent feat/skill grants."""
import re


def option_tags(title):
    tags = ["PREVARGTEQ:SPHERES_BLACKSMITH_LEVEL,2"]
    requirement = re.search(r"\(requires ([^)]+)\)", title, re.IGNORECASE)
    if requirement:
        if requirement[1].lower() != "shieldsmith":
            raise ValueError("Unreviewed Smithing Insight prerequisite: " + requirement[1])
        tags.append("PREABILITY:1,CATEGORY=Blacksmith Smithing Insight,Blacksmith Shieldsmith")
    name = title.split(" (")[0].split(" [")[0]
    if name in ("Armorclad Mastery", "Stunning Strikes"):
        tags[0] = "PREVARGTEQ:SPHERES_BLACKSMITH_LEVEL," + str(
            {"Armorclad Mastery": 4, "Stunning Strikes": 12}[name])
    if name == "Durable":
        tags.append("ABILITY:FEAT|AUTOMATIC|Endurance|Toughness")
    elif name == "Crafting Competence":
        tags.extend(["MULT:YES", "STACK:NO", "CHOOSE:SKILL|TYPE=Craft",
                     "BONUS:SKILL|LIST|SPHERES_BLACKSMITH_LEVEL|TYPE=Competence"])
    elif name == "Expanded Crafting":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "BONUS:ABILITYPOOL|Blacksmith Item Creation Feat|1"])
    return tags


def feat_category():
    return ("ABILITYCATEGORY:Blacksmith Item Creation Feat\tCATEGORY:FEAT\tTYPE:ItemCreation\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\t"
            "PLURAL:Blacksmith Item Creation Feats\tDISPLAYLOCATION:Feats")