"""Advanced-talent prerequisite compilation must resolve or fail closed."""
import unittest

from spheres_advanced_talents import clause, indexes, normalize, prerequisites, split_top_level


def row(sphere, system, talents=(), advanced=()):
    return {"sphere": sphere, "slug": sphere.lower(), "system": system,
            "talents": [{"name": name, "text": "", "heading": name, "url": "", "group": ""}
                        for name in talents],
            "advanced": [{"name": name, "text": "", "heading": name, "url": "", "group": ""}
                         for name in advanced]}


ROWS = [row("Destruction", "power", talents=("Admixture", "Blast Salvo", "Sculpt Blast"),
            advanced=("Greater Admixture", "Split Blast")),
        row("Conjuration", "power", talents=("Companion",))]


class AdvancedTalentTests(unittest.TestCase):
    def setUp(self):
        self.spheres, self.talents = indexes(ROWS)

    def test_normalize_strips_annotations_and_punctuation(self):
        self.assertEqual(normalize("Blast Salvo (blast shape)"), "blast salvo")
        self.assertEqual(normalize("Gremlin\u2019s Presence"), "gremlin s presence")

    def test_split_top_level_ignores_nested_commas(self):
        self.assertEqual(split_top_level("a (x, y), b"), ["a (x, y)", "b"])

    def test_clause_stops_at_sentence_end(self):
        text = "Prerequisites: Destruction sphere, caster level 10th. When you blast, you may."
        self.assertEqual(clause(text), "Destruction sphere, caster level 10th")
        self.assertIsNone(clause("No prerequisite line here."))

    def test_resolves_sphere_talents_and_caster_level(self):
        text = ("Prerequisites: Destruction sphere (Admixture, Greater Admixture, "
                "Split Blast), caster level 10th. Body text.")
        tags, unresolved = prerequisites("power", text, self.spheres, self.talents)
        self.assertEqual(unresolved, [])
        self.assertEqual(tags, [
            "PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere",
            "PREABILITY:1,CATEGORY=Spheres Magic Talent,Admixture",
            "PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction - Greater Admixture",
            "PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction - Split Blast",
            "PREVARGTEQ:SPHERES_CASTER_LEVEL,10"])

    def test_alternatives_and_unknown_names_fail_closed(self):
        for text in ("Prerequisites: Destruction sphere (any blast shape).",
                     "Prerequisites: Destruction sphere (Admixture or Split Blast).",
                     "Prerequisites: Destruction sphere (Nonexistent Talent).",
                     "Prerequisites: ability to cast 3rd-level spells.",
                     "Prerequisites: none."):
            tags, unresolved = prerequisites("power", text, self.spheres, self.talents)
            self.assertTrue(unresolved, text)

    def test_missing_clause_is_unresolved(self):
        tags, unresolved = prerequisites("power", "Just an effect.", self.spheres, self.talents)
        self.assertEqual(tags, [])
        self.assertEqual(unresolved, ["no prerequisite clause"])

    def test_ambiguous_names_are_not_guessed(self):
        rows = [row("Destruction", "power", talents=("Focus",)),
                row("Conjuration", "power", talents=("Focus",))]
        _, talents = indexes(rows)
        self.assertIsNone(talents["focus"])

    def test_character_level_clause(self):
        tags, unresolved = prerequisites("power", "Prerequisites: character level 15th. Body.",
                                         self.spheres, self.talents)
        self.assertEqual(tags, ["PREVARGTEQ:TL,15"])
        self.assertEqual(unresolved, [])

    def test_singular_prerequisite_and_newline_termination(self):
        self.assertEqual(clause("Prerequisite: Destruction sphere\nWhen you blast."),
                         "Destruction sphere")
        tags, unresolved = prerequisites("power", "Prerequisite: Destruction sphere\nBody.",
                                         self.spheres, self.talents)
        self.assertEqual(tags, ["PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere"])
        self.assertEqual(unresolved, [])

    def test_unmodelled_requirements_fail_closed(self):
        for text in ("Prerequisites: base attack bonus +5.",
                     "Prerequisites: Destruction sphere, 5 ranks in Spellcraft.",
                     "Prerequisites: Spheres of Might."):
            tags, unresolved = prerequisites("power", text, self.spheres, self.talents)
            self.assertTrue(unresolved, text)


if __name__ == "__main__":
    unittest.main()
