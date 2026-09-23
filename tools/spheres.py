"""Check prototype packaging or compare real PCGen exports; never evaluate LST."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "spheres"


def records(path):
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def check_package(data=DATA):
    references = []
    for line in records(data / "spheres.pcc"):
        tag, value = line.split(":", 1)
        if tag in {"ABILITY", "ABILITYCATEGORY", "CLASS"}:
            if Path(value).name != value or not value.endswith(".lst"):
                raise ValueError("unsafe source reference")
            references.append(value)
    required = {
        "spheres_categories.lst", "spheres_categories_incanter.lst",
        "spheres_core.lst", "spheres_destruction.lst", "spheres_incanter.lst",
        "spheres_incanter_sword.lst", "spheres_incanter_favored.lst", "spheres_incanter_domains.lst",
        "spheres_incanter_bloodlines.lst", "spheres_feats.lst",
        "spheres_classes.lst",
    }
    if len(set(references)) != len(references) or not required.issubset(references):
        raise ValueError("duplicate or missing required LST reference")
    for name in references:
        if not records(data / name):
            raise ValueError(f"empty source: {name}")
    abilities = records(data / "spheres_destruction.lst")
    if len(abilities) != 5:
        raise ValueError("expected sphere and four talents")
    prerequisite = "PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere"
    for line in abilities:
        if line.startswith("Destruction Sphere\t"):
            continue
        if prerequisite not in line.split("\t"):
            raise ValueError("talent missing base-sphere prerequisite")
    return "PASS: package structure (not PCGen parsing or formula validation)"


def compare_export(text, expected):
    actual = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+)=(-?\d+)", line.strip())
        if not match or match[1] in actual:
            raise ValueError(f"invalid or duplicate export field: {line!r}")
        actual[match[1]] = int(match[2])
    if actual != expected:
        differences = {key: (expected.get(key), actual.get(key))
                       for key in sorted(expected.keys() | actual.keys())
                       if expected.get(key) != actual.get(key)}
        raise ValueError(f"export mismatch (expected, actual): {differences}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    verify = sub.add_parser("verify")
    verify.add_argument("case")
    verify.add_argument("export", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check":
            print(check_package())
        else:
            cases = json.loads((ROOT / "testdata/spheres/expected.json").read_text())
            if args.case not in cases:
                raise ValueError("unknown fixture case")
            if args.export.stat().st_size > 16384:
                raise ValueError("export exceeds 16 KiB")
            compare_export(args.export.read_text(encoding="utf-8"), cases[args.case])
            print(f"PASS: export matches {args.case}")
    except (ValueError, OSError) as error:
        parser.exit(1, f"spheres: {error}\n")


if __name__ == "__main__":
    main()