"""Compile snapshotted sphere sections to a deterministic review manifest.

Section bounds are explicit: import the Ultimate-tab basic and advanced talents,
but never import Original tabs, sphere feats or legendary talents.
"""
import argparse
import json
import re
from pathlib import Path

from spheres_catalog_source import ROOT, SNAPSHOTS, POWER, MIGHT

BOUNDS = dict(zip(POWER, [(6,59),(7,51),(17,91),(14,44),(8,67),(6,49),(4,84),
    (29,74),(4,42),(6,58),(9,81),(9,50),(7,48),(8,61),(8,58),(6,61),(10,59),
    (7,78),(8,42),(5,37),(8,103),(4,42),(15,75),(3,29),(6,27),(13,45)]))
BOUNDS.update(dict(zip(MIGHT, [(5,91),(10,81),(3,27),(5,53),(6,45),(3,40),
    (4,41),(4,40),(2,33),(2,41),(1,121),(2,39),(5,61),(3,36),(2,25),
    (4,42),(3,44),(2,35),(2,28),(2,30),(4,54),(5,50),(4,45),(13,48),
    (15,110),(17,58),(9,37)])))
MANIFEST = ROOT / "data/spheres/catalog.json"


def clean_name(heading):
    return re.sub(r"\s*\([^)]*\)|\s*\[[^]]*\]", "", heading).strip()


def clean_intro(text):
    paragraphs = [p for p in text.splitlines() if "FoldUnfold" not in p and p not in ("Ultimate", "Original")]
    return re.sub(r"[^\n]*?\$\d+\.\d{2}\s*", "", "\n".join(paragraphs))


def advanced_talents(source, end):
    """Talents between the advanced heading and the next top-level section.

    The heading at ``end`` names either the advanced talents or, for pages that
    have none, the legendary talents. Legendary entries are never imported.
    """
    sections = source["sections"]
    heading = sections[end]["heading"]
    if "Advanced" not in heading:
        return []
    start = end + 1 if sections[end]["level"] == 1 else end
    group = clean_name(heading)
    talents, by_name = [], {}
    for section in sections[start:]:
        if section["level"] == 1:
            break
        if section["level"] < 4:
            group = clean_name(section["heading"])
            continue
        if section["level"] > 4:
            if talents:
                talents[-1]["text"] += "\n" + section["heading"] + ": " + section["text"]
            continue
        key = clean_name(section["heading"])
        if key in by_name:
            continue
        row = {"name": key, "heading": section["heading"], "group": group,
               "url": source["url"] + "#" + section["anchor"], "text": section["text"]}
        talents.append(row)
        by_name[key] = row
    return talents


def inventory(slugs=None):
    result = []
    for slug in POWER + MIGHT if slugs is None else slugs:
        source = json.loads((SNAPSHOTS / (slug + ".json")).read_text())
        sections = source["sections"]
        start, end = BOUNDS[slug]
        if "talent" not in sections[start]["heading"].lower():
            raise ValueError(f"Source layout changed: {slug} start")
        if not re.search(r"Advanced|Legendary", sections[end]["heading"]):
            raise ValueError(f"Source layout changed: {slug} end")
        system = "power" if slug in POWER else "might"
        name = slug.removesuffix("-sphere").replace("-", " ").title()
        base_start = 3 if slug == "veilweaving" else 0
        base = []
        for s in sections[base_start:start]:
            text = clean_intro(s["text"])
            if text:
                base.append((s["heading"] + ": " if s["level"] else "") + text)
        talents = []
        by_name = {}
        group = ""
        level = 2 if slug == "pilot" else 4
        for s in sections[start:end]:
            if s["level"] < level:
                group = s["heading"]
                continue
            if s["level"] > level:
                if talents:
                    talents[-1]["text"] += "\n" + s["heading"] + ": " + s["text"]
                continue
            key = clean_name(s["heading"])
            if key in by_name:
                if (" ".join(by_name[key]["text"].split()) != " ".join(s["text"].split())
                        and s["text"] != "See its entry above."
                        and not (slug == "trap" and key == "Flash Trap")):
                    raise ValueError(f"Conflicting duplicate: {slug}/{key}")
                continue
            row = {"name": key, "heading": s["heading"], "group": group,
                   "url": source["url"] + "#" + s["anchor"], "text": s["text"]}
            talents.append(row)
            by_name[key] = row
        result.append({"sphere": name, "slug": slug, "system": system,
                       "url": source["url"], "source_sha256": source["sha256"],
                       "base": "\n".join(base), "talents": talents,
                       "advanced": advanced_talents(source, end)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    rows = inventory()
    if args.write_manifest:
        MANIFEST.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    for row in rows:
        print(f'{row["system"]:5} {row["sphere"]:15} {len(row["talents"]):3} basic talents')
    print(f'{len(rows)} spheres; {sum(len(r["talents"]) for r in rows)} basic talents; '
          f'{sum(len(r["advanced"]) for r in rows)} advanced talents')


if __name__ == "__main__":
    main()