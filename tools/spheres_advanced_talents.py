"""Compile advanced-talent prerequisite clauses to PCGen prerequisite tokens.

Advanced talents carry real prerequisites. Anything this module cannot resolve is
reported as unresolved so the generated record stays gated behind manual approval
rather than becoming freely selectable.
"""
import re


def normalize(name):
    """Match published names to catalog records without annotation noise."""
    name = re.sub(r"\s*\([^()]*\)", "", name)
    return re.sub(r"[^a-z0-9]+", " ", name.replace("\u2019", "'").lower()).strip()


def split_top_level(value):
    """Split on commas that are not inside parentheses."""
    parts, depth, current = [], 0, []
    for char in value:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return [part.strip() for part in parts if part.strip()]


def clause(text):
    """Return the prerequisite clause, or None when the record states none."""
    match = re.search(r"Prerequisites?:\s*", text)
    if not match:
        return None
    rest = text[match.end():]
    index, depth = len(rest), 0
    for position, char in enumerate(rest):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and char in ".\n":
            index = position
            break
    return rest[:index].strip()


def indexes(rows):
    """Return (spheres, talents) name lookup tables for prerequisite clauses.

    A talent name that maps to more than one record is stored as None so callers
    treat it as unresolved instead of guessing a sphere.
    """
    spheres, talents = {}, {}
    for row in rows:
        category = "Spheres Magic Talent" if row["system"] == "power" else "Spheres Combat Talent"
        spheres[normalize(row["sphere"])] = (category, row["sphere"] + " Sphere")
        for talent in row["talents"] + row["advanced"]:
            name = normalize(talent["name"])
            key = (category, row["sphere"] + " - " + talent["name"].replace(",", ""))
            if row["slug"] == "destruction" and talent["name"] in {"Admixture", "Searing Blast",
                                                                   "Epicenter", "Gather Energy"}:
                key = (category, talent["name"])
            if name in talents and talents[name] != key:
                talents[name] = None
            else:
                talents.setdefault(name, key)
    return spheres, talents


def prerequisites(system, text, spheres, talents):
    """Return (tags, unresolved) for one advanced talent's prerequisite clause."""
    category = "Spheres Magic Talent" if system == "power" else "Spheres Combat Talent"
    raw = clause(text)
    tags, unresolved = [], []
    if raw is None:
        return tags, ["no prerequisite clause"]
    for part in split_top_level(raw):
        level = re.match(r"caster level\s*(\d+)", part, re.I)
        if level:
            tags.append("PREVARGTEQ:SPHERES_CASTER_LEVEL," + level[1])
            continue
        level = re.match(r"(?:character|class) level\s*(\d+)", part, re.I)
        if level:
            tags.append("PREVARGTEQ:TL," + level[1])
            continue
        sphere = re.match(r"([A-Za-z][A-Za-z' \-]*?)\s+[Ss]phere\b", part)
        if sphere and normalize(sphere[1]) in spheres:
            base_category, base = spheres[normalize(sphere[1])]
            tags.append("PREABILITY:1,CATEGORY=" + base_category + "," + base)
            inner = re.search(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)", part)
            if inner and re.search(r"\b(any|or|either|one of|whichever|both)\b", inner[1], re.I):
                unresolved.append(part)
            elif inner:
                for name in split_top_level(inner[1]):
                    key = talents.get(normalize(name))
                    if key is None:
                        unresolved.append(name)
                    else:
                        tags.append("PREABILITY:1,CATEGORY=" + key[0] + "," + key[1])
            continue
        unresolved.append(part)
    return list(dict.fromkeys(tags)), unresolved
