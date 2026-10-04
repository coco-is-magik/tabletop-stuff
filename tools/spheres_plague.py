"""Reviewed Plague feat entry branches and their shared trailing requirements."""
import re

PREFIX = ("Blood sphere and 5th caster level; or Death sphere and 5th caster level; "
          "or Duelist sphere and base attack bonus +5; or Alchemy sphere and base attack bonus +5")
SUFFIXES = {
    "Virulent Ailment": "",
    "Encompassing Illness": "; Virulent Ailment, character level 9th",
    "Pathological Host": "; Virulent Ailment, character level 7th",
    "Pathology": "; Virulent Ailment",
    "Rotten Hordes": "; Death sphere (Shroud), Virulent Ailment (plague)",
}


def prerequisites(name, text):
    if name not in SUFFIXES:
        return None
    match = re.search(r"Prerequisites:\s*([^\n]+)", text)
    if not match or match[1].rstrip(".") != PREFIX + SUFFIXES[name]:
        raise ValueError("Plague prerequisite source changed; review " + name)
    branches = []
    for sphere in ("Blood", "Death", "Duelist", "Alchemy"):
        magic = sphere in ("Blood", "Death")
        category = "Spheres Magic Talent" if magic else "Spheres Combat Talent"
        threshold = f"PREVARGTEQ:SPHERES_CL_{sphere.upper()},5" if magic else "PREATT:5"
        branches.append(f"[PREMULT:2,[PREABILITY:1,CATEGORY={category},{sphere} Sphere],[{threshold}]]")
    tags = ["PREMULT:1," + ",".join(branches)]
    if name != "Virulent Ailment":
        tags.append("PREFEAT:1,Virulent Ailment")
    if name in ("Encompassing Illness", "Pathological Host"):
        tags.append("PREVARGTEQ:TL," + ("9" if name == "Encompassing Illness" else "7"))
    if name == "Rotten Hordes":
        tags.extend(["PREABILITY:1,CATEGORY=Spheres Magic Talent,Death Sphere",
                     "PREABILITY:1,CATEGORY=Spheres Magic Talent,Death - Shroud"])
    return tags