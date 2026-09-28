"""Reviewed Technical Insight dependencies and persistent character effects."""
import re

DEPENDENCIES = {
    "Intuition, Combat": ("Intuition (Ex)",),
    "Intuition, Lucky": ("Intuition (Ex)", "Luck"),
    "Intuition, Meditative": ("Intuition (Ex)",),
    "Intuition, Reactive": ("Intuition (Ex)",),
    "Luck, Combatant’s": ("Luck",),
    "Luck, Showman’s": ("Luck",),
    "Luck, Socialite’s": ("Luck",),
}


def class_tags():
    return ["DEFINE:SPHERES_TECHNICIAN_GADGETS|0",
            "BONUS:VAR|SPHERES_TECHNICIAN_GADGETS|max(1,floor(SPHERES_TECHNICIAN_LEVEL/2)+INT)",
            "DEFINE:SPHERES_TECHNICIAN_GADGET_DC|0",
            "BONUS:VAR|SPHERES_TECHNICIAN_GADGET_DC|10+floor(SPHERES_TECHNICIAN_LEVEL/2)+INT",
            "BONUS:SKILL|Disable Device|max(1,floor(SPHERES_TECHNICIAN_LEVEL/2))",
            "BONUS:SKILL|Knowledge (Engineering)|floor(SPHERES_TECHNICIAN_LEVEL/2)|PREVARGTEQ:SPHERES_TECHNICIAN_LEVEL,2"]


def option_tags(title):
    name = re.sub(r"\s*\[[^]]+\]", "", title).strip()
    level = {"Expert’s Insight": 10, "Greater Craftsman": 6}.get(name, 2)
    tags = [f"PREVARGTEQ:SPHERES_TECHNICIAN_LEVEL,{level}"]
    for dependency in DEPENDENCIES.get(name, ()):
        tags.append("PREABILITY:1,CATEGORY=Technician Technical Insight,Technician " + dependency)
    if name == "Intuition (Ex)":
        tags.append("BONUS:VAR|SPHERES_TECHNICIAN_INTUITION|max(1,1+WIS)")
    elif name == "Luck":
        tags.append("BONUS:VAR|SPHERES_TECHNICIAN_LUCK|max(1,1+CHA)")
    elif name.startswith("Intuition,"):
        tags.append("BONUS:VAR|SPHERES_TECHNICIAN_INTUITION|1")
        if name == "Intuition, Lucky":
            tags.append("BONUS:VAR|SPHERES_TECHNICIAN_LUCK|1")
    elif name.startswith("Luck,"):
        tags.append("BONUS:VAR|SPHERES_TECHNICIAN_LUCK|1")
    elif name == "Professional Insight (Ex)":
        tags.append("BONUS:SKILL|TYPE=Craft,TYPE=Profession|floor(SPHERES_TECHNICIAN_LEVEL/2)")
    elif name == "Gadgeteer":
        tags.append("ABILITY:Spheres Combat Talent|AUTOMATIC|Tinker Sphere")
    return tags