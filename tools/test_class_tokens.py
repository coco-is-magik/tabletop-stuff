"""Class records must reference real skills and real internal abilities.

Live PCGen rejects an unresolved CSKILL or ABILITY name with a SEVERE
"Unconstructed Reference" and aborts the whole character load. Those names come
from the same source data the live harness loads, so they are checkable offline
against the pinned Core Rulebook skills and the Spheres campaign's own skills.
"""
import re
import unittest

from spheres import DATA, ROOT

CORE = ROOT / "vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game"
CORE_SKILLS = CORE / "core_rulebook/cr_skills.lst"
PROF_FILES = tuple(CORE.glob("core_*/cr_abilities_class.lst"))
PROF = re.compile(r"^(Weapon|Armor|Shield) Prof[^\t]*")


def skill_records(path):
    """Yield (name, type tokens) for each skill record in a PCGen skill file."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "\tKEYSTAT:" not in line:
            continue
        name = line.split("\t", 1)[0].strip()
        match = re.search(r"TYPE:([^\t]+)", line)
        types = [t for t in (match[1].split(".") if match else []) if t]
        yield name, types


def load_skills():
    names, types = set(), set()
    for path in (CORE_SKILLS, DATA / "spheres_skills.lst"):
        for name, tokens in skill_records(path):
            names.add(name)
            types.update(tokens)
    return names, types


def load_internal_profs():
    """Names of internal proficiency abilities PCGen actually ships."""
    names = set()
    for path in PROF_FILES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "CATEGORY:Internal" in line and PROF.match(line):
                names.add(line.split("\t", 1)[0].strip())
    return names


def class_fields():
    """Yield (filename, kind, token) for every external reference a class record makes."""
    for path in sorted(DATA.glob("spheres_*_class.lst")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            for match in re.finditer(r"CSKILL:([^\t]*)", line):
                for token in match[1].split("|"):
                    if token.strip():
                        yield path.name, "cskill", token.strip()
            for match in re.finditer(r"ABILITY:Internal\|[^|]*\|([^\t]*)", line):
                for token in match[1].split("|"):
                    token = token.strip()
                    if token and not token.startswith("PRE"):
                        yield path.name, "internal", token
            for match in re.finditer(r"ABILITY:Special Ability\|[^|]*\|([^\t]*)", line):
                for token in match[1].split("|"):
                    token = token.strip()
                    if token and not token.startswith("PRE"):
                        yield path.name, "ability", token


def defined_abilities():
    """Names of every ability record the Spheres campaign or the Core Rulebook defines."""
    names = set()
    for path in tuple(DATA.glob("spheres_*.lst")) + tuple((CORE / "core_rulebook").glob("*.lst")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "\tCATEGORY:" in line and not line.startswith("#"):
                names.add(line.split("\t", 1)[0].strip())
    return names


@unittest.skipUnless(CORE_SKILLS.is_file(), "vendored PCGen Core Rulebook data not present")
class ClassTokenTest(unittest.TestCase):
    def test_class_skill_tokens_resolve(self):
        names, types = load_skills()
        self.assertIn("Craft (Alchemy)", names, "Core skill data missing")
        self.assertIn("Craft", types, "Craft skill type missing")
        for filename, kind, token in class_fields():
            if kind != "cskill":
                continue
            if token.startswith("TYPE="):
                self.assertIn(token[5:], types, f"{filename}: unknown skill type {token}")
            else:
                self.assertIn(token, names, f"{filename}: unresolved skill {token!r}")

    def test_internal_proficiency_names_are_real(self):
        real = load_internal_profs()
        self.assertIn("Weapon Prof ~ Simple", real, "Core proficiency data missing")
        for filename, kind, token in class_fields():
            if kind == "internal":
                self.assertIn(token, real, f"{filename}: unknown internal ability {token!r}")

    def test_granted_ability_names_are_defined(self):
        defined = defined_abilities()
        self.assertIn("Spheres Casting Core", defined, "Spheres ability data missing")
        for filename, kind, token in class_fields():
            if kind == "ability":
                self.assertIn(token, defined, f"{filename}: undefined ability {token!r}")


if __name__ == "__main__":
    unittest.main()
