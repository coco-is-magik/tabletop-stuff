"""Independent class-source table checks; live checks in pcgen_class_catalog.py."""
import json
import unittest

from spheres import DATA, check_package
from spheres_class_catalog import NAMES, SNAPSHOTS, generate, table, number, source_options
from pcgen_class_catalog import expected, fixture
from spheres_mageknight import option_tags, CURSE_REVIEW, REVIEW_CATEGORY


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

    def test_combat_training_grants_focus(self):
        grant = "ABILITY:Special Ability|AUTOMATIC|Spheres Martial Focus"
        for slug in NAMES:
            _, abilities, _, details = generate(slug)
            if details["magic"]:
                self.assertNotIn(grant, abilities, slug)
            else:
                training = next(line for line in abilities.splitlines()
                                if line.startswith(details["name"] + " Combat Training\t"))
                self.assertIn("TYPE:SpheresInternal.SpheresCombatTraining", training, slug)
                self.assertIn(grant, training, slug)

    def test_mageknight_prerequisites(self):
        snapshot = json.loads((SNAPSHOTS / "mageknight.json").read_text())
        options = source_options(snapshot, "Mystic Combat (Su)")
        records = {line.split("\t")[0]: line for line in generate("mageknight")[1].splitlines()}
        for title, _ in options:
            tags = option_tags(title)
            self.assertTrue(tags[0].startswith("PREVARGTEQ:SPHERES_MAGEKNIGHT_LEVEL,"))
        for title, level in (("Elemental Defense (requires mystic defense)", 11),
                             ("Mark of Pain (requires marked)", 7),
                             ("Whirl of Blows (requires mageknight 6)", 6),
                             ("Magic Power", 2)):
            self.assertIn(f"PREVARGTEQ:SPHERES_MAGEKNIGHT_LEVEL,{level}", records["Mageknight " + title])
        self.assertIn("PREABILITY:1,CATEGORY=Mageknight Mystic Combat,Mageknight Spell Shield",
                      records["Mageknight Spell Mirror (requires mageknight 10 - spell shield)"])
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,War Sphere",
                      records["Mageknight Shared Marking (requires marked - War sphere)"])
        black_dog = next(value for key, value in records.items() if key.startswith("Mageknight Black Dog Companion"))
        self.assertIn("PREVARGTEQ:SPHERES_MAGEKNIGHT_LEVEL,4", black_dog)
        self.assertIn(f"PREABILITY:1,CATEGORY={REVIEW_CATEGORY},{CURSE_REVIEW}", black_dog)
        self.assertIn("COST:0", records[CURSE_REVIEW])
        with self.assertRaisesRegex(ValueError, "Unreviewed"):
            option_tags("Unreviewed Option (requires an unknown feature)")

    def test_mageknight_repeatable_grants(self):
        self.assertIn("DEFINE:SPHERES_COMBAT_TALENTS|0", generate("mageknight")[0])
        self.assertNotIn("DEFINE:SPHERES_COMBAT_TALENTS|0", option_tags("Combat Talent [CotS]"))
        for title, variable in (("Magic Power", "SPHERES_MAGIC_TALENTS"),
                                ("Combat Talent [CotS]", "SPHERES_COMBAT_TALENTS")):
            tags = option_tags(title)
            for tag in ("MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|" + variable + "|1"):
                self.assertIn(tag, tags)
        for title, feat in (("Whirl of Blows (requires mageknight 6)", "Whirlwind Attack"),
                            ("Sunder The Veil", "Pierce The Veil"),
                            ("Weirding Initiate", "Weird Defense")):
            self.assertIn("ABILITY:FEAT|AUTOMATIC|" + feat, option_tags(title))
        self.assertNotIn("MULT:YES", option_tags("Spell Shield [WM]"))
        self.assertFalse(any(tag.startswith("ABILITY:FEAT") for tag in option_tags("Weirding Adept")))


if __name__ == "__main__":
    unittest.main()