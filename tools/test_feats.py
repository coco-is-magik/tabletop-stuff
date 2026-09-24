"""Regression tests for feat source boundaries and fail-closed qualification."""
import json
import unittest
from spheres_feats import build, Prerequisites, split_clauses, DATA


class FeatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build()
        cls.rows = json.loads(cls.outputs["feat-catalog.json"])
        cls.parser = Prerequisites(cls.rows)
        cls.by_name = {r["name"]: r for r in cls.rows}

    def test_generated_data_current(self):
        for name, content in self.outputs.items():
            self.assertEqual((DATA / name).read_text(), content, name)

    def test_identity_and_no_legacy_duplicates(self):
        lines = self.outputs["spheres_feat_catalog.lst"].splitlines()[1:]
        keys = [line.split("\t")[0] for line in lines]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertNotIn("Extra Magic Talent", keys)
        self.assertNotIn("Extra Combat Talent", keys)
        self.assertIn("Improved Counterspell (Spheres)", keys)
        self.assertGreater(len(self.rows), 1000)

    def test_unknown_prerequisites_require_explicit_approval(self):
        records = {s.split("\t")[0]: s for s in self.outputs["spheres_feat_catalog.lst"].splitlines()[1:]}
        for row in self.rows:
            if row["unresolved_prerequisites"] and row["key"] in records:
                self.assertIn("PREABILITY:1,CATEGORY=Spheres Feat Adjudication,Reviewed - " + row["key"], records[row["key"]])

    def test_or_not_accidentally_and(self):
        tags = self.parser.clause("Blood sphere or Duelist sphere")
        self.assertTrue(tags[0].startswith("PREMULT:1,"))
        self.assertIsNone(self.parser.clause("Improved Trip or a talent allowing safe trips"))
        tags, missing = self.parser.compile("Prerequisites: Bardic performance, raging song, or Warleader sphere.\nBenefit: Test.")
        self.assertEqual(tags, [])
        self.assertEqual(len(missing), 1)

    def test_nested_talent_prerequisites(self):
        self.assertEqual(len(split_clauses("Destruction sphere (Admixture, Searing Blast), caster level 5th")), 2)
        tags, missing = self.parser.compile("Prerequisites: Destruction sphere (Admixture), caster level 5th.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,Admixture", tags)
        self.assertIn("PREVARGTEQ:SPHERES_CL_DESTRUCTION,5", tags)
        self.assertEqual(self.parser.clause("Alchemy sphere ((formulae) package)")[-1],
                         "PREABILITY:1,CATEGORY=Spheres Alchemy Package,Alchemy Package - Formulae")

    def test_source_types_not_page_types(self):
        self.assertEqual(self.by_name["Basic Magic Training"]["types"], ["General"])
        self.assertIn("Combat", self.by_name["Extra Combat Talent"]["types"])
        self.assertNotIn("Advanced Magical Training", self.by_name)
        self.assertNotIn("Prepare Consumable", self.by_name)

    def test_counterspell_chain_avoids_core_name_collision(self):
        self.assertIn("PREFEAT:2,Counterspell,Improved Counterspell (Spheres)", self.by_name["Greater Counterspell"]["prerequisites"])

    def test_sphere_choices_are_distinct_and_targeted(self):
        data = self.outputs["spheres_feat_catalog.lst"]
        self.assertIn("Sphere Focus - Life\t", data)
        self.assertIn("BONUS:VAR|SPHERES_DC_LIFE|1", data)
        self.assertIn("Combat Sphere Specialization - Fencing\t", data)
        self.assertIn("BONUS:VAR|SPHERES_BAB_FENCING|min(max(0,TL-BAB),1+floor((TL-1)/4))", data)
        self.assertEqual(self.parser.clause("Sphere Focus"), ["PREFEAT:1,TYPE=SpheresFeatSphereFocus"])

    def test_no_invalid_key_delimiters(self):
        for line in self.outputs["spheres_feat_catalog.lst"].splitlines()[1:]:
            self.assertNotIn(",", line.split("\t")[0])

    def test_limited_repeatability(self):
        line = next(s for s in self.outputs["spheres_feat_catalog.lst"].splitlines()
                    if s.startswith("Practiced Interruption\t"))
        self.assertIn("PREVARLT:SPHERES_FEAT_PRACTICEDINTERRUPTION_COUNT,2", line)


if __name__ == "__main__":
    unittest.main()