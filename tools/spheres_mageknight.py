"""Reviewed Mystic Combat selection rules; tactical effects remain source text."""
import re


REVIEW_CATEGORY = "Mageknight Mystic Combat Review"
CURSE_REVIEW = "Reviewed - Black Dog Companion Curse Talent"
LEVEL = "SPHERES_MAGEKNIGHT_LEVEL"


def option_tags(title):
    """Compile the pinned heading requirements; reject unreviewed new grammar."""
    tags = []
    requirements = re.search(r"\(requires ([^)]+)\)", title)
    level = 2
    if requirements:
        for clause in requirements[1].split(", "):
            if re.fullmatch(r"mageknight \d+", clause):
                level = max(level, int(clause.split()[1]))
            elif clause in ("resist magic", "marked", "mystic defense"):
                level = max(level, {"resist magic": 1, "marked": 7, "mystic defense": 11}[clause])
            elif clause in ("Life sphere", "War sphere", "Protection sphere"):
                tags.append("PREABILITY:1,CATEGORY=Spheres Magic Talent," + clause.replace("sphere", "Sphere"))
            elif clause in ("shadowblade", "spell shield"):
                tags.append("PREABILITY:1,CATEGORY=Mageknight Mystic Combat,Mageknight " +
                            {"shadowblade": "Shadowblade", "spell shield": "Spell Shield"}[clause])
            elif clause == "1 talent with the curse descriptor":
                tags.append("PREABILITY:1,CATEGORY=" + REVIEW_CATEGORY + "," + CURSE_REVIEW)
            else:
                raise ValueError("Unreviewed Mystic Combat prerequisite: " + clause)
    tags.insert(0, f"PREVARGTEQ:{LEVEL},{level}")
    name = title.split(" (")[0].split(" [")[0]
    if name in ("Magic Power", "Combat Talent"):
        variable = "SPHERES_MAGIC_TALENTS" if name == "Magic Power" else "SPHERES_COMBAT_TALENTS"
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|" + variable + "|1"])
    if name in ("Champion", "Greater Combatant"):
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "BONUS:ABILITYPOOL|Mageknight " + name + " Feat|1"])
    feat = {"Whirl of Blows": "Whirlwind Attack", "Sunder The Veil": "Pierce The Veil",
            "Weirding Initiate": "Weird Defense"}.get(name)
    if feat:
        # These options explicitly waive the granted feat's prerequisites.
        tags.append("ABILITY:FEAT|AUTOMATIC|" + feat)
    if name in ("Weirding Adept", "Weirding Master"):
        previous, talent, granted_feat = (
            ("Weirding Initiate", "Mage Feint", "Weird Motion") if name == "Weirding Adept" else
            ("Weirding Adept", "Decoy", "Weird Assault"))
        waiver = "PREABILITY:1,CATEGORY=Mageknight Mystic Combat,Mageknight " + previous
        sphere = "PREABILITY:1,CATEGORY=Spheres Magic Talent,Illusion Sphere"
        normal = [sphere, "PREABILITY:1,CATEGORY=Spheres Magic Talent,Illusion - Mage Feint", "PREATT:3"]
        if name == "Weirding Master":
            normal.append("PREABILITY:1,CATEGORY=Spheres Magic Talent,Illusion - Decoy")
        normal_gate = "PREMULT:" + str(len(normal)) + "," + ",".join("[" + p + "]" for p in normal)
        tags.extend([
            "ABILITY:Spheres Magic Talent|AUTOMATIC|Illusion - " + talent + "|PREMULT:1,[" + waiver + "],[" + sphere + "]",
            "ABILITY:FEAT|AUTOMATIC|" + granted_feat + "|PREMULT:1,[" + waiver + "],[" + normal_gate + "]"])
        if name == "Weirding Adept":
            tags.extend(["DEFINE:SPHERES_MAGE_FEINT_CL|max(SPHERES_CASTER_LEVEL,SPHERES_CL_ILLUSION)+"
                         + LEVEL + "-floor(" + LEVEL + "/2)"])
    return tags


def feat_categories():
    return [f"ABILITYCATEGORY:Mageknight {name} Feat\tCATEGORY:FEAT\tTYPE:{types}\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\t"
            f"PLURAL:Mageknight {name} Feats\tDISPLAYLOCATION:Feats"
            for name, types in (("Champion", "Champion"), ("Greater Combatant", "Combat.Champion"))]


def review_records():
    category = (f"ABILITYCATEGORY:{REVIEW_CATEGORY}\tCATEGORY:{REVIEW_CATEGORY}\tEDITABLE:YES\t"
                "EDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\t"
                "PLURAL:Mystic Combat Prerequisite Review\tDISPLAYLOCATION:Spheres")
    ability = (f"{CURSE_REVIEW}\tCATEGORY:{REVIEW_CATEGORY}\tCOST:0\tPREVARGTEQ:{LEVEL},4\t"
               "DESC:GM confirms a currently possessed talent has the curse descriptor. "
               "This attests only that prerequisite, not companion construction. "
               "Remove this record if the qualifying talent is lost.")
    return category, ability