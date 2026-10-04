"""Report recorded Spheres coverage without equating tags with rules completion."""
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "spheres"
REPORT = ROOT / "docs" / "spheres-coverage.json"


def summarize(rows, unresolved=False):
    keys = [row["key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate coverage keys")
    result = {
        "records": len(rows),
        "records_with_recorded_mechanics": sum(bool(row["mechanics"]) for row in rows),
        "records_without_recorded_mechanics": sorted(
            row["key"] for row in rows if not row["mechanics"]),
    }
    if unresolved:
        missing = {row["key"]: row["unresolved_prerequisites"]
                   for row in rows if row["unresolved_prerequisites"]}
        result["records_with_unresolved_prerequisites"] = len(missing)
        result["unresolved_prerequisites"] = dict(sorted(missing.items()))
    return result


def build(data=DATA):
    def load(name):
        return json.loads((data / (name + ".json")).read_text())

    catalog = load("catalog")
    review = load("catalog-review")
    feats = load("feat-catalog")
    traits = load("trait-catalog")
    return {
        "scope": "Recorded catalog metadata, not a mechanical completion certificate",
        "limitations": [
            "Empty mechanics arrays can describe tactical-only effects or unimplemented effects.",
            "Generators also emit mechanics outside these arrays; review source and generated LSTs.",
            "Nonempty mechanics arrays do not prove full implementation or runtime verification.",
            "Basic talent review excludes four existing Destruction records and all advanced/legendary talents.",
            "Classes, traditions, racial replacements and prestige coverage require separate audits.",
        ],
        "spheres_by_system": dict(sorted(Counter(row["system"] for row in catalog).items())),
        "source_basic_talents": sum(len(row["talents"]) for row in catalog),
        "generated_basic_talents": summarize(review),
        "talents_by_sphere": {
            sphere: summarize([row for row in review if row["sphere"] == sphere])
            for sphere in sorted({row["sphere"] for row in review})
        },
        "feats": summarize(feats, unresolved=True),
        "feat_status_labels": dict(sorted(Counter(row["status"] for row in feats).items())),
        "traits": summarize(traits, unresolved=True),
    }


def render():
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    text = render()
    if args.write:
        REPORT.write_text(text)
    elif not REPORT.exists() or REPORT.read_text() != text:
        raise ValueError("Coverage report stale; run tools/spheres_coverage.py --write")
    report = json.loads(text)
    for name in ("generated_basic_talents", "feats", "traits"):
        group = report[name]
        print(f"{name}: {group['records']} records; "
              f"{group['records_with_recorded_mechanics']} with recorded mechanics; "
              f"{group.get('records_with_unresolved_prerequisites', 'not tracked')} unresolved")


if __name__ == "__main__":
    main()