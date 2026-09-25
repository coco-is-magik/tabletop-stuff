"""Deterministic trait catalog and fail-closed selection regressions."""
import json
import unittest

from spheres_traits import DATA, build, inventory, requirements
from spheres_feats import Prerequisites


class TraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build()
        cls.rows = json.loads(cls.outputs["trait-catalog.json"])
        cls.by_name = {r["name"]: r for r in cls.rows}

    def test_generated_data_current(self):
        for name, content in self.outputs.items():
            self.assertEqual((DATA / name).read_text(), content, name)

    def test_all_headings_and_appendix_deduplicated(self):
        self.assertEqual(len(self.rows), 161)
        self.assertEqual(len(self.rows), len({r["key"] for r in self.rows}))
        self.assertEqual(len([r for r in self.rows if r["group"] == "Drawback"]), 5)
        self.assertEqual(len([r for r in self.rows if r["group"] == "Tradition"]), 14)
        self.assertEqual(len([r for r in self.rows if r["group"] == "Legacy"]), 8)
        self.assertEqual(len(self.by_name["Combat Healer"]["sources"]), 2)
        self.assertNotIn("Highlander Tradition Package", self.by_name)
        self.assertNotIn("Optional Rule: Trait Talent Exchange", self.by_name)

    def test_shared_pool_restrictions_and_non_repeatable_drawbacks(self):
        regular = self.outputs["spheres_traits.lst"]
        drawbacks = self.outputs["spheres_trait_drawbacks.lst"]
        self.assertIn("TYPE:Trait.BasicTrait.CombatTrait.SpheresTrait", regular)
        self.assertIn("TYPE.CombatTrait", regular)
        self.assertIn("TYPE:Trait.SpheresDrawbackTrait", drawbacks)
        self.assertIn("BONUS:VAR|Pool_Traits|2", drawbacks)
        self.assertIn("!PREABILITY:1,CATEGORY=Special Ability,TYPE.SpheresDrawbackTrait", drawbacks)
        self.assertNotIn("BONUS:VAR|Pool_Traits|2", regular)

    def test_unmodeled_prerequisites_and_campaigns_require_review(self):
        regular = self.outputs["spheres_traits.lst"]
        approval = self.outputs["spheres_trait_adjudication.lst"]
        for row in self.rows:
            if row["unresolved_prerequisites"]:
                self.assertIn("Reviewed - " + row["key"] + "\t", approval)
                record = next(line for line in regular.splitlines() if line.startswith(row["key"] + "\t"))
                self.assertIn("PREABILITY:1,CATEGORY=Spheres Trait Adjudication,Reviewed - " + row["key"], record)
        self.assertIn("GM approval", " ".join(self.by_name["Artificery Training"]["unresolved_prerequisites"]))
        self.assertIn("Limited Warp", str(self.by_name["Additional Medium"]["unresolved_prerequisites"]))
        self.assertIn("Communication sphere", str(self.by_name["Social Butterfly"]["unresolved_prerequisites"]))

    def test_unknown_prerequisite_fails_closed(self):
        tags, unknown = requirements({"heading": "Unseen (requires fictional ancestry)",
                                      "text": "Prerequisite: a blessing from an unmodeled deity\nBenefit: Test."}, Prerequisites([]))
        self.assertEqual(tags, [])
        self.assertEqual(len(unknown), 2)


if __name__ == "__main__":
    unittest.main()