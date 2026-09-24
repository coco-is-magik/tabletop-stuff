"""Build the Power/Might feat catalog from pinned OGC snapshots, without network access.

Only exact prerequisite grammar is compiled. Unsupported clauses require explicit
per-feat adjudication; they are never silently treated as satisfied.
"""
import argparse
import json
import re

from spheres_catalog import clean_name, inventory
from spheres_catalog_lst import category, key, text, token, PACKAGES
from spheres_catalog_source import ROOT, SNAPSHOTS, POWER, MIGHT, FEATS

DATA = ROOT / "data/spheres"
LEGACY = {"Extra Magic Talent", "Extra Spell Points", "Extra Arsenal Trick", "Extra Combat Talent"}
SPHERE_CHOICES = {"Sphere Focus", "Combat Sphere Focus", "Combat Sphere Specialization"}
TYPES = {t.lower(): t for t in (
    "Combat", "Teamwork", "Metamagic", "ItemCreation", "Admixture", "Anathema",
    "Aristeia", "Champion", "Chance", "Channeling", "Companion", "Counterspell",
    "Damnation", "Drawback", "DualSphere", "Necrosis", "Plague", "Protokinesis",
    "Proxy", "Purring", "Racial", "Ritual", "Squadron", "Surreal", "Theurge", "WildMagic")}


def normalize(value):
    return " ".join(value.replace("’", "'").replace("–", "-").split()).casefold()


def name(heading):
    value = clean_name(heading).rstrip("*").strip()
    # The source alternates between these two spellings in its prerequisites.
    match = re.fullmatch(r"(.+), (Improved|Greater|Superior)", value)
    return match[2] + " " + match[1] if match else value


def rules(value):
    return value.split("\n| Spheres of Power")[0].split("\n| Spheres of Might")[0].strip()


def inventory_feats():
    result = {}
    for slug in FEATS + POWER + MIGHT:
        source = json.loads((SNAPSHOTS / (slug + ".json")).read_text())
        active = slug in FEATS
        boundary = 0
        current = None
        for section in source["sections"]:
            heading, level = section["heading"], section["level"]
            # Current entries have TOC anchors. The wiki's Original tab does not;
            # importing it reintroduces renamed/retired feats as new choices.
            if level and not section["anchor"]:
                current = None
                continue
            if slug not in FEATS and level <= 2:
                active = "feat" in heading.lower() and not re.search(r"old|original", heading, re.I)
                boundary = level
                current = None
            if not active or not level or level == boundary:
                continue
            body = rules(section["text"])
            if not re.search(r"\bBenefits?:", body):
                if current and level > current["level"]:
                    current["text"] += "\n" + heading + ": " + body
                continue
            feat_name = name(heading)
            identity = normalize(feat_name)
            if identity in result:
                result[identity]["sources"].append(source["url"] + "#" + section["anchor"])
                continue
            types = []
            for group in re.findall(r"[([]([^])]+)[)\]]", heading):
                for part in group.split(","):
                    recognized = TYPES.get(re.sub(r"[ -]", "", part).lower())
                    if recognized:
                        types.append(recognized)
            current = {"name": feat_name, "heading": heading, "level": level,
                       "types": sorted(set(types)) or ["General"], "text": body,
                       "sources": [source["url"] + "#" + section["anchor"]]}
            result[identity] = current
    return sorted(result.values(), key=lambda r: normalize(r["name"]))


def split_clauses(value):
    """Commas inside sphere talent/package lists are not conjunction boundaries."""
    parts, start, depth = [], 0, 0
    for i, char in enumerate(value):
        depth += (char == "(") - (char == ")")
        if char in ",;" and depth == 0:
            parts.append(value[start:i].strip())
            start = i + 1
    parts.append(value[start:].strip())
    return [p for p in parts if p]


def core_feats():
    path = ROOT / "vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game/core_rulebook/cr_feats.lst"
    return {normalize(line.split("\t")[0]): line.split("\t")[0]
            for line in path.read_text().splitlines() if line and not line.startswith("#")}


class Prerequisites:
    def __init__(self, feats):
        self.spheres = {normalize(r["sphere"]): r for r in inventory()}
        self.feats = core_feats()
        self.feats.update({normalize(r["name"]): r["key"] for r in feats})
        self.feats.update({normalize(n): "TYPE=SpheresFeat" + token(n) for n in SPHERE_CHOICES})

    def clause(self, value, caster_variable="SPHERES_CASTER_LEVEL"):
        value = value.strip().rstrip(".")
        simple = normalize(value)
        if simple.startswith("and "):
            return self.clause(value[4:], caster_variable)
        # OR is valid only when every complete alternative can be represented.
        if " or " in simple and "(" not in value:
            alternatives = [self.clause(p, caster_variable) for p in re.split(r" or ", value, flags=re.I)]
            if all(p for p in alternatives):
                return ["PREMULT:1," + ",".join("[" + p[0] + "]" if len(p) == 1 else
                        "[PREMULT:" + str(len(p)) + "," + ",".join("[" + t + "]" for t in p) + "]"
                        for p in alternatives)]
            return None
        if simple in ("casting class feature", "spherecasting class feature"):
            return ["PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core"]
        if simple == "combat training class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,Conscript Combat Training"]
        if simple in ("no casting class feature", "no spherecasting class feature"):
            return ["!PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core"]
        if simple == "spell pool":
            return ["PREVARGTEQ:SPHERES_SPELL_POINTS,1"]
        if simple in ("any metamagic feat", "any item creation feat"):
            return ["PREFEAT:1,TYPE=" + ("Metamagic" if "metamagic" in simple else "ItemCreation")]
        for pattern, prefix in ((r"base attack bonus\s*\+?(\d+)", "PREATT:"),
                (r"(?:character )?level (\d+)(?:st|nd|rd|th)?", "PRELEVEL:MIN="),
                (r"caster level (\d+)(?:st|nd|rd|th)?", "PREVARGTEQ:" + caster_variable + ","),
                (r"magic skill bonus\s*\+?(\d+)", "PREVARGTEQ:SPHERES_MAGIC_SKILL_BONUS,")):
            match = re.fullmatch(pattern, simple)
            if match:
                return [prefix + match[1]]
        match = re.fullmatch(r"(str|dex|con|int|wis|cha) (\d+)", simple)
        if match:
            return ["PRESTAT:1," + match[1].upper() + "=" + match[2]]
        match = re.fullmatch(r"(.*?) (\d+) ranks?", value, re.I)
        if match and match[1].lower() in {"acrobatics", "bluff", "diplomacy", "fly", "intimidate", "perception", "ride", "sense motive", "sleight of hand", "spellcraft", "stealth", "survival", "swim", "climb", "use magic device", "handle animal", "knowledge (arcana)"}:
            return ["PRESKILL:1," + match[1].title() + "=" + match[2]]
        match = re.fullmatch(r"(.+?) sphere(?:\s*\((.*)\))?", value, re.I)
        if match and normalize(match[1]) in self.spheres:
            row = self.spheres[normalize(match[1])]
            tags = ["PREABILITY:1,CATEGORY=" + category(row) + "," + row["sphere"] + " Sphere"]
            talents = {normalize(t["name"]): key(row, t) for t in row["talents"]}
            if match[2]:
                for item in split_clauses(match[2]):
                    package = re.fullmatch(r"\(?([a-z ]+)\)? package", item, re.I)
                    if package and package[1].title() in PACKAGES.get(row["slug"], ()):
                        tags.append("PREABILITY:1,CATEGORY=Spheres " + row["sphere"] + " Package," + row["sphere"] + " Package - " + package[1].title())
                        continue
                    clean = normalize(clean_name(item))
                    if clean not in talents:
                        return None
                    tags.append("PREABILITY:1,CATEGORY=" + category(row) + "," + talents[clean])
            return tags
        if simple in self.feats:
            return ["PREFEAT:1," + self.feats[simple]]
        return None

    def compile(self, body):
        match = re.search(r"Prerequisites?:\s*(.*?)(?=\n|Benefits?:|$)", body, re.I)
        if not match:
            return [], []
        clauses = split_clauses(match[1].rstrip("."))
        # A comma-separated list ending in 'or' is not a conjunction. Preserve
        # the entire expression for review instead of enforcing a wrong subset.
        if any(re.match(r"or\b", c, re.I) for c in clauses):
            return [], [match[1].rstrip(".")]
        # Published CL prerequisites refer to the greatest prerequisite sphere CL.
        spheres = [r for n, r in self.spheres.items()
                   if re.search(r"\b" + re.escape(n) + r" sphere\b", normalize(match[1])) and r["system"] == "power"]
        variables = ["SPHERES_CL_" + token(r["sphere"]).upper() for r in spheres]
        caster = variables[0] if len(variables) == 1 else "max(" + ",".join(variables) + ")" if variables else "SPHERES_CASTER_LEVEL"
        tags, unresolved = [], []
        for clause in clauses:
            parsed = self.clause(clause, caster)
            if parsed:
                tags.extend(parsed)
            else:
                unresolved.append(clause)
        return list(dict.fromkeys(tags)), unresolved


def build():
    feats = inventory_feats()
    core = core_feats()
    for row in feats:
        row["key"] = row["name"].replace(",", "") + (" (Spheres)" if normalize(row["name"]) in core and row["name"] not in LEGACY else "")
    parser = Prerequisites(feats)
    overrides = json.loads((DATA / "feat-mechanics.json").read_text())
    lines = ["# Generated by tools/spheres_feats.py; OGC: catalog-OGL.txt"]
    approvals = ["# Explicit adjudication for prerequisite clauses unsupported by this dataset."]
    for row in feats:
        prereqs, unresolved = parser.compile(row["text"])
        override = overrides.get(row["name"], {})
        if "prerequisites" in override:
            prereqs, unresolved = override["prerequisites"], []
        row["prerequisites"] = prereqs
        row["unresolved_prerequisites"] = unresolved
        row["mechanics"] = list(override.get("tags", []))
        cost = re.search(r"\bCost: \+(\d+) spell points?\s*$", row["text"], re.M)
        if "Metamagic" in row["types"] and cost:
            row["mechanics"].append("DEFINE:SPHERES_METAMAGIC_" + token(row["name"]).upper() + "_COST|" + cost[1])
        if row["name"] in LEGACY:
            row["status"] = "existing"
            continue
        types = row["types"] + ["SpheresFeat"]
        # Incanter grants only feats explicitly referring to spheres/spell points,
        # plus metamagic, crafting, and drawback feats (not all magic-adjacent feats).
        requirement = re.search(r"Prerequisites?:\s*(.*?)(?=\n|Benefits?:|$)", row["text"], re.I)
        requirement = normalize(requirement[1]) if requirement else ""
        if ("casting class feature" in requirement or "spell pool" in requirement or
                any(normalize(r["sphere"]) + " sphere" in requirement for r in parser.spheres.values() if r["system"] == "power")):
            types.append("IncanterBonus")
        if any(t in types for t in ("Drawback", "Proxy", "Theurge")):
            types.append("IncanterBonus")
        tags = [row["key"], "CATEGORY:FEAT", "TYPE:" + ".".join(dict.fromkeys(types))] + prereqs
        if row["name"] in SPHERE_CHOICES:
            tags[2] += ".SpheresFeat" + token(row["name"])
            # Explicit per-sphere records avoid fragile string substitution in BONUS.
            # They share one source feat identity and cannot stack on the same sphere.
            for sphere in parser.spheres.values():
                if (sphere["system"] == "power") != (row["name"] == "Sphere Focus"):
                    continue
                ident = token(sphere["sphere"]).upper()
                variant = tags.copy()
                variant[0] += " - " + sphere["sphere"]
                variant = [t for t in variant if not t.startswith("PREABILITY:") or "Spheres Casting Core" in t]
                if row["name"] == "Combat Sphere Specialization":
                    variant.append("PREABILITY:1,CATEGORY=Spheres Combat Talent," + sphere["sphere"] + " Sphere")
                    variant.append("BONUS:VAR|SPHERES_BAB_" + ident + "|min(max(0,TL-BAB),1+floor((TL-1)/4))")
                else:
                    variant.append("BONUS:VAR|SPHERES_DC_" + ident + "|1")
                variant += ["DESC:" + text(row["text"]) + " Selected sphere: " + sphere["sphere"] + ".",
                            "SOURCEPAGE:" + row["sources"][0]]
                lines.append("\t".join(variant))
            row["status"] = "sphere-specific-records"
            continue
        if unresolved:
            approval = "Reviewed - " + row["key"]
            tags.append("PREABILITY:1,CATEGORY=Spheres Feat Adjudication," + approval)
            approvals.append("\t".join([approval, "CATEGORY:Spheres Feat Adjudication", "COST:0",
                "DESC:Manual prerequisite approval only; does not grant the feat or its effects. Verify: " + text("; ".join(unresolved))]))
        if not any(t.startswith("MULT:") for t in row["mechanics"]):
            if re.search(r"(?:take|select|gain|taken|selected) (?:this feat )?multiple times", row["text"], re.I):
                tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE"] if "effects stack" in row["text"].lower() and "do not stack" not in row["text"].lower() else ["MULT:YES", "STACK:NO", "CHOOSE:USERINPUT|1|TITLE=Distinct feat target (verify source restrictions)"]
            elif re.search(r"(?:take|select|gain) this feat (?:a second time|twice)", row["text"], re.I):
                counter = "SPHERES_FEAT_" + token(row["key"]).upper() + "_COUNT"
                tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "DEFINE:" + counter + "|0",
                         "BONUS:VAR|" + counter + "|1", "PREVARLT:" + counter + ",2"]
        tags += row["mechanics"]
        tags += ["DESC:" + text(row["text"]) + " Automated tags and remaining manual effects: docs/spheres-feats.md. Apply unautomated effects manually.", "SOURCEPAGE:" + row["sources"][0]]
        lines.append("\t".join(tags))
        row["status"] = "partial" if unresolved or not row["mechanics"] else "mechanics-added"
    return {"spheres_feat_catalog.lst": "\n".join(lines) + "\n",
            "spheres_feat_adjudication.lst": "\n".join(approvals) + "\n",
            "spheres_categories_feats.lst": "ABILITYCATEGORY:Spheres Feat Adjudication\tCATEGORY:Spheres Feat Adjudication\tEDITABLE:YES\tEDITPOOL:NO\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:YES\tPLURAL:Manual Feat Prerequisite Approvals\tDISPLAYLOCATION:Spheres\n"
                "ABILITYCATEGORY:Spheres Basic Magic Sphere\tCATEGORY:Spheres Magic Talent\tTYPE:SpheresBaseSphere\tEDITABLE:YES\tEDITPOOL:NO\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPLURAL:Basic Magic Training Sphere\tDISPLAYLOCATION:Spheres\n",
            "feat-catalog.json": json.dumps(feats, indent=2, ensure_ascii=False) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    outputs = build()
    for filename, content in outputs.items():
        path = DATA / filename
        if args.write:
            path.write_text(content, encoding="utf-8")
        elif not path.exists() or path.read_text() != content:
            raise SystemExit("Stale feat catalog: " + str(path))
    rows = json.loads(outputs["feat-catalog.json"])
    print(f'{len(rows)} source feats; {sum(bool(r["unresolved_prerequisites"]) for r in rows)} require prerequisite adjudication')


if __name__ == "__main__":
    main()