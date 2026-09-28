"""Reviewed Scholar knack dependencies and Studied Technique grants."""
import re


DEPENDENCIES = {
    "Animal Training, Large": ("Animal Training - Small",),
    "Genetic Modification": ("Animal Training - Small",),
    "Arcane Studies": ("Amateur Arcanist",),
    "Breakthrough Historian": ("Amateur Arcanist",),
    "Crafting Genius": ("Amateur Arcanist",),
    "Chronomancy": ("Chronomancy - Amateur",),
    "Chronomancy, Advanced": ("Chronomancy - Amateur", "Chronomancy"),
    "Lightning Rod, Improved": ("Lightning Rod",),
    "Ritual Crafter": ("Ritual Student",),
}


def medical_records():
    category = ("ABILITYCATEGORY:Scholar Medical Ability\tCATEGORY:Scholar Medical Ability\t"
                "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\t"
                "POOL:min(1,SPHERES_SCHOLAR_LEVEL)\tPLURAL:Medical Ability\tDISPLAYLOCATION:Spheres")
    ability = ("Scholar Intelligence for Heal\tCATEGORY:Scholar Medical Ability\t"
               "PREVARGTEQ:SPHERES_SCHOLAR_LEVEL,1\tBONUS:SKILL|Heal|INT-WIS\t"
               "DESC:Use Intelligence instead of Wisdom for Heal. Leave unselected to use Wisdom.")
    return category, ability


def medical_resources():
    level = "SPHERES_SCHOLAR_LEVEL"
    values = (("ATTEMPTS_PER_PATIENT", "max(1,INT)"),
              ("HP_MULTIPLIER", f"if({level}<5,1,if({level}<9,2,3))"),
              ("ABILITY_DAMAGE", 'if(skillinfo("TOTALRANK","Heal")>=5,1,0)'),
              ("ABILITY_DRAIN", f'if({level}>=5,if(skillinfo("TOTALRANK","Heal")>=8,1,0),0)'),
              ("REVIVE", f'if({level}>=9,if(skillinfo("TOTALRANK","Heal")>=11,1,0),0)'))
    tags = []
    for suffix, formula in values:
        variable = "SPHERES_SCHOLAR_MEDICAL_" + suffix
        tags.extend([f"DEFINE:{variable}|0", f"BONUS:VAR|{variable}|{formula}"])
    return tags


def option_tags(title):
    name = re.sub(r"\s*\[[^]]+\]", "", title).strip()
    tags = ["PREVARGTEQ:SPHERES_SCHOLAR_LEVEL," + ("6" if name == "Liquefying Injections" else "2")]
    for dependency in DEPENDENCIES.get(name, ()):
        tags.append("PREABILITY:1,CATEGORY=Scholar Scholar'S Knack,Scholar " + dependency)
    if name == "Studied Technique":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "PREVARLT:SPHERES_SCHOLAR_STUDIED_TECHNIQUE,3",
                     "BONUS:VAR|SPHERES_SCHOLAR_STUDIED_TECHNIQUE|1",
                     "BONUS:VAR|SPHERES_COMBAT_TALENTS|3"])
    elif name == "Academic Knowledge":
        tags.append("BONUS:SKILL|TYPE=Knowledge|max(1,floor(SPHERES_SCHOLAR_LEVEL/2))")
    elif name == "Expert Healing":
        tags.append("BONUS:SKILL|Heal|max(1,floor(SPHERES_SCHOLAR_LEVEL/2))")
    elif name == "Astrology":
        tags.extend(["DEFINE:SPHERES_SCHOLAR_INSIGHT_CAPACITY|0",
                     "BONUS:VAR|SPHERES_SCHOLAR_INSIGHT_CAPACITY|max(1,floor(SPHERES_SCHOLAR_LEVEL/2))+max(0,INT)"])
    return tags