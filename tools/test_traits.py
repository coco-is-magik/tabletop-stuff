"""Deterministic trait catalog and fail-closed selection regressions."""
import json
import unittest

from spheres_traits import DATA, build, inventory, requirements
from spheres_feats import Prerequisites


class TraitTests(unittest.TestCase):
    def test_destructive_talent_damage_is_not_global_weapon_damage(self):
        self.assertEqual(self.by_name["Destructive Talent"]["mechanics"], [
            "DEFINE:SPHERES_DESTRUCTION_TRAIT_DAMAGE|0",
            "BONUS:VAR|SPHERES_DESTRUCTION_TRAIT_DAMAGE|1+floor(TL/10)|TYPE=Trait|PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere"])
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere",
                      self.by_name["Destructive Talent"]["prerequisites"])
    def test_bountiful_charm_default_recruitment_bonus(self):
        self.assertEqual(self.by_name["Bountiful Charm"]["mechanics"], [
            "CSKILL:Diplomacy", "BONUS:SITUATION|Diplomacy=Recruit cohorts|2|TYPE=Trait"])

    def test_abrasive_penalties_are_not_all_diplomacy_checks(self):
        self.assertEqual(self.by_name["Abrasive"]["mechanics"], [
            "BONUS:SITUATION|Diplomacy=Improve a creature's attitude|-5",
            "BONUS:SITUATION|Diplomacy=Entertain|-5",
            "BONUS:SITUATION|Diplomacy=Impressive display of skill|-5"])

    def test_steel_body_additional_hit_dice_scaling(self):
        self.assertEqual(self.by_name["Steel Body"]["mechanics"],
                         ["BONUS:HP|CURRENTMAX|1+floor((TL-1)/2)|PRERULE:1,DAMAGE_HP"])

    def test_scarred_by_war_uses_native_damage_reduction(self):
        self.assertEqual(self.by_name["Scarred by War"]["mechanics"],
                         ["CSKILL:Intimidate", "DR:1/piercing"])

    def test_identification_traits_keep_class_skill_and_situational_bonus(self):
        for name, skill, situation in (
                ("Impersonator", "Bluff", "Impersonate another creature"),
                ("Guardian Of The Real", "Knowledge (Planes)", "Identify monsters")):
            self.assertEqual(self.by_name[name]["mechanics"], [
                "CSKILL:" + skill, f"BONUS:SITUATION|{skill}={situation}|2|TYPE=Trait"])

    def test_weird_virtuoso_only_bonuses_subtle_casting(self):
        self.assertEqual(self.by_name["Weird Virtuoso"]["mechanics"], [
            "BONUS:SITUATION|Perform (Dance)=Subtly provide somatic components|1|TYPE=Trait",
            "BONUS:SITUATION|Perform (Oratory)=Whisper verbal components|1|TYPE=Trait",
            "BONUS:SITUATION|Perform (Sing)=Whisper verbal components|1|TYPE=Trait"])

    def test_class_skill_grants_do_not_invent_unconditional_benefits(self):
        for name, skill in (("Learned Readiness", "Perception"),
                            ("Industrial Worker", "Knowledge (Engineering)"),
                            ("Higher Calling", "Diplomacy")):
            self.assertEqual(self.by_name[name]["mechanics"], ["CSKILL:" + skill])

    def test_daysense_grants_only_one_chosen_class_skill(self):
        rows = {row["name"]: row for row in json.loads(build()["trait-catalog.json"])}
        self.assertEqual(rows["Daysense"]["mechanics"], [
            "MULT:YES", "STACK:NO", "CHOOSE:NUMCHOICES=1|SKILL|Knowledge (Geography)|Survival",
            "CSKILL:LIST", "BONUS:SKILL|Knowledge (Geography),Survival|1|TYPE=Trait"])

    def test_situational_bonuses_do_not_become_general_skill_bonuses(self):
        rows = {row["name"]: row for row in json.loads(build()["trait-catalog.json"])}
        for name, skill, situation, amount in (
                ("Corpse Watcher", "Heal", "Learn information (not treatment)", 3),
                ("Colloquial Terms", "Linguistics", "Communicate without a shared language", 4)):
            self.assertEqual(rows[name]["mechanics"], [
                f"BONUS:SITUATION|{skill}={situation}|{amount}|TYPE=Trait"])
        self.assertEqual(rows["Skeptical"]["mechanics"], [
            "BONUS:SKILL|Sense Motive|1|TYPE=Trait"])

    def test_persistent_skill_bonuses_and_conditional_charge_capacity(self):
        rows = {row["name"]: row for row in json.loads(build()["trait-catalog.json"])}
        self.assertEqual(rows["Aura"]["mechanics"], [
            "CSKILL:Knowledge (Religion)", "BONUS:SKILL|Knowledge (Religion)|1|TYPE=Trait"])
        self.assertEqual(rows["Spatial Awareness"]["mechanics"], ["CSKILL:Knowledge (Engineering)"])
        self.assertEqual(rows["Technophile"]["mechanics"], [
            "BONUS:SKILL|Craft (Mechanical)|2|TYPE=Trait",
            "BONUS:VAR|SPHERES_TECH_CHARGE_CAPACITY|2|PREABILITY:1,CATEGORY=Spheres Combat Talent,Tech Sphere"])

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