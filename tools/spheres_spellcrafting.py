"""Compile reviewed Ultimate custom spells into PCGen data, without network access.

PCGen owns character qualification. This compiler checks definition structure and
references, not whether a proposed combination is balanced or correctly reviewed.
"""
import argparse
import json
from pathlib import Path
import re

from spheres import DATA, records

SOURCE = "https://spheresofpower.wikidot.com/spellcrafting"
DEFINITIONS = DATA / "custom-spells.json"
OUTPUT = DATA / "spheres_custom_spells.lst"
CHANGES = {"additional_effect": 2, "foreign_talent_or_feat": 1,
           "increase_range": 2, "increase_duration": 2,
           "decrease_range": -1, "decrease_duration": -1,
           "personal_to_touch": 1}


def label(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 '\-]*", value):
        raise ValueError(f"invalid definition label: {value!r}")
    return value


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("expected integer >= " + str(minimum))
    return value


def fields(value, names):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ValueError("expected fields: " + names)


def prose(value):
    if not isinstance(value, str) or not value.strip() or any(c in value for c in "\t\r\n|%"):
        raise ValueError("expected nonempty single-line prose without LST delimiters")
    return value.replace("(", "[").replace(")", "]")


def references():
    """Read only abilities loaded by this campaign and the pinned Core feat file."""
    result = {}
    paths = [DATA / line.split(":", 1)[1] for line in records(DATA / "spheres.pcc")
             if line.startswith("ABILITY:") and line != "ABILITY:spheres_custom_spells.lst"]
    paths.append(DATA.parents[1] / "vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game/core_rulebook/cr_feats.lst")
    for path in paths:
        for line in records(path):
            tags = line.split("\t")
            category = next((t[9:] for t in tags if t.startswith("CATEGORY:")), "FEAT")
            result[(category, tags[0])] = tags
    return result


def compile_spell(spell, known):
    fields(spell, "name base_sphere components changes duration_cost_adjustment review effect")
    name = label(spell["name"])
    base = label(spell["base_sphere"])
    review = prose(spell["review"])
    effect = prose(spell["effect"])
    components = spell["components"]
    if not isinstance(components, list) or not components:
        raise ValueError("a spell needs components")
    prerequisites, identities = [], set()
    counts = {"sphere": 0, "talent": 0, "feat": 0}
    effect_cost = 0
    spheres = set()
    for component in components:
        fields(component, "kind key effect spell_points")
        kind = component["kind"]
        if kind not in counts:
            raise ValueError("unsupported component kind")
        key = component["key"]
        if not isinstance(key, str) or any(c in key for c in ',|\t\r\n[]'):
            raise ValueError("component key contains unsupported prerequisite delimiters")
        identity = (kind, key, label(component["effect"]))
        if identity in identities:
            raise ValueError("same component effect applied twice")
        identities.add(identity)
        category = "FEAT" if kind == "feat" else "Spheres Magic Talent"
        tags = known.get((category, key))
        if tags is None:
            raise ValueError("unknown or unsupported component: " + key)
        is_sphere = any(t.startswith("TYPE:") and "SpheresBaseSphere" in t.split(":", 1)[1].split(".") for t in tags)
        # The original Destruction record predates the generated catalog type.
        is_sphere = is_sphere or key == "Destruction Sphere"
        if kind != "feat" and is_sphere != (kind == "sphere"):
            raise ValueError("component kind does not match catalog: " + key)
        if kind == "sphere":
            spheres.add(key)
        pre = ("PREFEAT:1," + key if kind == "feat" else
               "PREABILITY:1,CATEGORY=Spheres Magic Talent," + key)
        if pre not in prerequisites:
            prerequisites.append(pre)
        counts[kind] += 1
        effect_cost += integer(component["spell_points"])
    if base + " Sphere" not in spheres:
        raise ValueError("base sphere must be a component")
    # Require the base sphere of each catalog talent as an explicit component.
    for component in components:
        if component["kind"] == "talent":
            tags = known[("Spheres Magic Talent", component["key"])]
            for tag in tags:
                prefix = "PREABILITY:1,CATEGORY=Spheres Magic Talent,"
                if tag.startswith(prefix) and tag[len(prefix):].endswith(" Sphere"):
                    if tag[len(prefix):] not in spheres:
                        raise ValueError("talent's sphere must be a component")
    changes = spell["changes"]
    if not isinstance(changes, list) or any(not isinstance(c, str) or c not in CHANGES for c in changes):
        raise ValueError("unsupported complexity alteration")
    complexity = max(0, sum(CHANGES[c] for c in changes))
    adjustment = integer(spell["duration_cost_adjustment"], -len(components))
    if adjustment > len(components):
        raise ValueError("duration adjustment exceeds component count")
    cost = max(1, effect_cost + adjustment + complexity // 2)
    total = sum(counts.values())
    variable = "SPHERES_CL_" + re.sub(r"[^A-Za-z0-9]", "", base).upper()
    summary = (f"Complexity {complexity}; {cost} SP; {(complexity + 1) // 2} casting-time increases. "
               f"Research Spellcraft DC {5 * total}; learning {total} hours; "
               f"spellbook {total} pages; writing {counts['sphere'] + counts['talent']} hours; "
               f"decipher DC {20 + complexity}. Base CL %1; base DC %2. "
               f"{effect} Review: {review}")
    common = ["PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core", *prerequisites]
    rows = []
    for method in ("Learned", "Researched"):
        tags = [method + " - " + name, "CATEGORY:Spheres Spell Acquisition", "COST:0", *common]
        if method == "Researched":
            tags.append("PREFEAT:1,Spellcrafting")
        tags += ["DESC:Attests GM review and completed " + method.lower() +
                 " acquisition. Resolve required time and checks before selecting; does not grant a repertoire slot. Remove this record when forgetting the spell; relearning requires downtime again.",
                 "SOURCEPAGE:" + SOURCE]
        rows.append("\t".join(tags))
    tags = [name, "CATEGORY:Spheres Spell Repertoire", *common,
            "PREMULT:1,[PREABILITY:1,CATEGORY=Spheres Spell Acquisition,Learned - " + name +
            "],[PREABILITY:1,CATEGORY=Spheres Spell Acquisition,Researched - " + name + "]",
            "DESC:" + summary + "|" + variable + "|SPHERES_DC_" + variable[11:],
            "SOURCEPAGE:" + SOURCE]
    rows.append("\t".join(tags))
    return "\n".join(rows)


def build(definitions, known=None):
    fields(definitions, "version spells")
    if type(definitions["version"]) is not int or definitions["version"] != 1:
        raise ValueError("unsupported custom spell schema")
    spells = definitions["spells"]
    if not isinstance(spells, list) or not spells:
        raise ValueError("expected a nonempty spell list")
    known = references() if known is None else known
    names, rows = set(), []
    for spell in spells:
        row = compile_spell(spell, known)
        identity = spell["name"].casefold()
        if identity in names:
            raise ValueError("duplicate spell name")
        names.add(identity)
        rows.append(row)
    return "# Generated by tools/spheres_spellcrafting.py; Ultimate rules, not Original.\n" + "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--definitions", type=Path, default=DEFINITIONS)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        output = build(json.loads(args.definitions.read_text(encoding="utf-8")))
        if args.write:
            OUTPUT.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (ValueError, OSError) as error:
        parser.exit(1, f"spellcrafting: {error}\n")


if __name__ == "__main__":
    main()