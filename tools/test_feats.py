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

    def test_multi_clause_or_branches(self):
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Troop Commander.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertEqual(len(tags), 1)
        self.assertTrue(tags[0].startswith("PREMULT:1,[PREMULT:2,"))
        for piece in ("PREABILITY:1,CATEGORY=Spheres Magic Talent,War Sphere",
                      "PREFEAT:1,Squadron Commander",
                      "PREABILITY:1,CATEGORY=Spheres Combat Talent,Warleader Sphere",
                      "PREFEAT:1,Troop Commander"):
            self.assertIn(piece, tags[0])

    def test_or_branch_global_requirements_hoisted(self):
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Troop Commander; character level 10th.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PRELEVEL:MIN=10", tags)
        self.assertNotIn("PRELEVEL", tags[0])
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Troop Commander; caster level 5th or 5 ranks in Diplomacy.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREMULT:1,[PREVARGTEQ:SPHERES_CL_WAR,5],[PRESKILL:1,Diplomacy=5]", tags)

    def test_or_branch_fail_closed(self):
        tags, missing = self.parser.compile("Prerequisites: War sphere; or Performance sphere.\nBenefit: Test.")
        self.assertEqual(tags, [])
        self.assertEqual(missing, ["War sphere; or Performance sphere"])
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Unknown Talent.\nBenefit: Test.")
        self.assertEqual(tags, [])
        self.assertTrue(missing)

    def test_drawback_prerequisites(self):
        for text, record in (("Terrain Casting drawback", "Tradition - Terrain Casting"),
                             ("Charged Spells", "Tradition - Charged Spells"),
                             ("Draining Casting (drawback)", "Tradition - Draining Casting"),
                             ("Vampiric Casting drawback", "Tradition - Vampiric Casting")):
            self.assertEqual(self.parser.clause(text),
                             ["PREABILITY:1,CATEGORY=Custom Casting Drawback," + record])
        tags = self.parser.clause("Draining Casting (drawback) or Unsettling Casting (drawback)")
        self.assertEqual(tags, ["PREMULT:1,[PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Draining Casting],"
                                "[PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Unsettling Casting]"])

    def test_skill_rank_forms(self):
        self.assertEqual(self.parser.clause("Craft (alchemy) 5 ranks"), ["PRESKILL:1,Craft (Alchemy)=5"])
        self.assertEqual(self.parser.clause("Knowledge (planes) 5 ranks"), ["PRESKILL:1,Knowledge (Planes)=5"])
        self.assertEqual(self.parser.clause("Heal 1 rank"), ["PRESKILL:1,Heal=1"])
        self.assertEqual(self.parser.clause("5 ranks in Diplomacy"), ["PRESKILL:1,Diplomacy=5"])
        self.assertIsNone(self.parser.clause("5 ranks in any 2 skills"))
        self.assertIsNone(self.parser.clause("Profession (notaskill) 5 ranks"))

    def test_one_of_alternatives(self):
        tags = self.parser.clause("one of Agonizing Defiling, Ruinous Defiling, or Spellburn Defiling")
        self.assertEqual(tags, ["PREMULT:1,[PREFEAT:1,Agonizing Defiling],[PREFEAT:1,Ruinous Defiling],"
                                "[PREFEAT:1,Spellburn Defiling]"])
        tags, missing = self.parser.compile(
            "Prerequisites: Terrain Casting drawback, one of Agonizing Defiling, Ruinous Defiling, or Spellburn Defiling.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Terrain Casting", tags)
        self.assertTrue(any(t.startswith("PREMULT:1,[PREFEAT:1,Agonizing Defiling]") for t in tags))
        self.assertIsNone(self.parser.clause("one of Fabricated Feat, or Spellburn Defiling"))

    def test_limited_repeatability(self):
        line = next(s for s in self.outputs["spheres_feat_catalog.lst"].splitlines()
                    if s.startswith("Practiced Interruption\t"))
        self.assertIn("PREVARLT:SPHERES_FEAT_PRACTICEDINTERRUPTION_COUNT,2", line)

    def test_martial_focus_eligibility(self):
        focus = "PREABILITY:1,CATEGORY=Special Ability,Spheres Martial Focus"
        for clause in ("martial focus", "Ability to gain martial focus", "ability to maintain martial focus"):
            self.assertEqual(self.parser.clause(clause), [focus])
        self.assertEqual(self.parser.clause("combat training class feature"),
                         ["PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresCombatTraining"])
        self.assertEqual(self.parser.clause("casting class feature or ability to gain martial focus"),
                         ["PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core],[" + focus + "]"])
        self.assertIsNone(self.parser.clause("ability to gain martial focus or use skill leverage"))
        self.assertIsNone(self.parser.clause("currently has martial focus"))
        self.assertEqual(self.by_name["Unified Focus"]["unresolved_prerequisites"], [])
        self.assertTrue(self.by_name["Winded By Words"]["unresolved_prerequisites"])

    def test_focus_grant_sources(self):
        records = {line.split("\t")[0]: line for line in
                   (DATA / "spheres_conscript.lst").read_text().splitlines()}
        grant = "ABILITY:Special Ability|AUTOMATIC|Spheres Martial Focus"
        for name in ("Conscript Combat Training", "Extra Combat Talent", "Martial Tradition (Manual)"):
            self.assertIn(grant, records[name])
        self.assertIn("TYPE:SpheresInternal.SpheresCombatTraining", records["Conscript Combat Training"])
        self.assertNotIn("SpheresCombatTraining", records["Extra Combat Talent"])
        custom = next(line for line in (DATA / "spheres_traditions.lst").read_text().splitlines()
                      if line.startswith("Custom Martial Tradition\t"))
        self.assertIn(grant, custom)
        focus = next(line for line in (DATA / "spheres_core.lst").read_text().splitlines()
                     if line.startswith("Spheres Martial Focus\t"))
        self.assertIn("DEFINE:SPHERES_MARTIAL_FOCUS_CAPACITY|1", focus)


if __name__ == "__main__":
    unittest.main()