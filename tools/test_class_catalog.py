"""Independent class-source table checks; live checks in pcgen_class_catalog.py."""
import json
import unittest

from spheres import DATA, check_package
from spheres_class_catalog import NAMES, SNAPSHOTS, generate, table, number, source_options
from pcgen_class_catalog import expected, fixture


class ClassCatalogTest(unittest.TestCase):
    def test_all_class_tables_and_package(self):
        campaign = (DATA / "spheres.pcc").read_text()
        self.assertIn("PASS", check_package())
        for slug in NAMES:
            with self.subTest(slug=slug):
                snapshot = json.loads((SNAPSHOTS / f"{slug}.json").read_text())
                headers, rows = table(snapshot)
                class_lst, features, categories, details = generate(slug)
                for suffix, content in (("class", class_lst), ("features", features), ("categories", categories)):
                    if content:
                        file = f"spheres_{slug}_{suffix}.lst"
                        self.assertIn(f":{file}", campaign)
                        self.assertEqual((DATA / file).read_text(), content)
                for level, row in enumerate(rows, 1):
                    result = expected(slug, level)
                    self.assertEqual(result["bab"], number(row[1]))
                    self.assertEqual([result[key] for key in ("fortitude", "reflex", "will")],
                                     [number(row[j]) for j in (2, 3, 4)])
                    self.assertEqual(result["talents"] - (2 if details["magic"] else 0)
                                     - (slug == "mageknight"), number(row[headers.index("Magic Talents") if "Magic Talents" in headers else headers.index("Talents") if details["magic"] else headers.index("Combat Talents")]))
                    if details["magic"]:
                        self.assertEqual(result["caster_level"], number(row[headers.index("Caster Level")]))
                        self.assertEqual(result["spell_points"], level)
                    self.assertEqual(fixture(slug, level).count("CLASSABILITIESLEVEL:"), level)

    def test_free_sphere_and_choice_boundaries(self):
        for slug, sphere in (("eliciter", "Mind"), ("fey-adept", "Illusion"),
                             ("shifter", "Alteration"), ("symbiat", "Mind Sphere|Telekinesis")):
            self.assertIn(f"{sphere} Sphere" if slug != "symbiat" else sphere + " Sphere",
                          generate(slug)[1])
        self.assertIn("CATEGORY:Striker Bare Knuckles", generate("striker")[2])
        self.assertIn("CATEGORY:Hedgewitch Path", generate("hedgewitch")[2])
        self.assertIn("CATEGORY:Wraith Haunt Path", generate("wraith")[2])
        self.assertIn("CATEGORY:Soul Weaver Channel", generate("soul-weaver")[2])
        for slug, sphere in (("commander", "Warleader"), ("technician", "Trap"),
                             ("scholar", "Alchemy"), ("sentinel", "Guardian")):
            self.assertIn(f"{sphere} Sphere", generate(slug)[1])
        self.assertIn("CATEGORY:Commander Enhanced Tactic", generate("commander")[2])
        self.assertIn("CATEGORY:Thaumaturge Bonus Feat", generate("thaumaturge")[2])
        self.assertIn("AUTO:WEAPONPROF|Longsword|Rapier|Sap|Sword (Short)|Shortbow|Whip",
                      generate("symbiat")[0])
        self.assertIn("CATEGORY:Technician Invention Base Form", generate("technician")[2])
        self.assertIn("Technician Independent Invention\tCATEGORY:Technician Invention Base Form", generate("technician")[1])
        self.assertIn("Wraith Path of the Anima - Weather\tCATEGORY:Wraith Haunt Path", generate("wraith")[1])
        hedgewitch = generate("hedgewitch")[1]
        self.assertIn("Hedgewitch Arcane Builder\tCATEGORY:Hedgewitch Secret\tPREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10", hedgewitch)
        for slug, heading, allowed, excluded in (("wraith", "Wraith Haunts", "Amnesiac Possession", "Path of the Ancestor"),
                                                   ("technician", "List of Technical Insights", "Aesthetic Insight", "Improved Crossbow")):
            snapshot = json.loads((SNAPSHOTS / f"{slug}.json").read_text())
            names = [name for name, _ in source_options(snapshot, heading)]
            self.assertIn(allowed, names)
            self.assertNotIn(excluded, names)
        for slug, level in (("unknown", 1), ("armorist", 0), ("armorist", 21)):
            with self.assertRaises(ValueError):
                fixture(slug, level)
            with self.assertRaises(ValueError):
                expected(slug, level)
        with self.assertRaises(ValueError):
            generate("unknown")
        broken = {"url": "broken", "sections": [{"text": "Table: Broken | Level | Base Attack Bonus\n| 1 | +0"}]}
        with self.assertRaises(ValueError):
            table(broken)

    def test_eliciter_persuasive_boundaries(self):
        abilities = generate("eliciter")[1]
        self.assertIn("BONUS:VAR|SPHERES_ELICITER_PERSUASIVE|2+floor(SPHERES_ELICITER_LEVEL/6)", abilities)
        for level, expected_bonus in ((1, 2), (5, 2), (6, 3), (11, 3),
                                      (12, 4), (17, 4), (18, 5), (20, 5)):
            self.assertEqual(2 + level // 6, expected_bonus)


if __name__ == "__main__":
    unittest.main()