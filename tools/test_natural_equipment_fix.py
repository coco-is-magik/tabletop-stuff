"""Regression guards for the pinned natural-equipment parser correction."""
import unittest

from pcgen_natural_equipment_fix import OLD, NEW, patched_source


class NaturalEquipmentFixTests(unittest.TestCase):
    def test_exact_site_and_idempotence(self):
        original = "before\n" + OLD + "\nafter"
        fixed = patched_source(original)
        self.assertEqual(fixed, "before\n" + NEW + "\nafter")
        self.assertEqual(patched_source(fixed), fixed)
        self.assertIn("eqI.isNatural() ? eqI : eqI.clone()", fixed)

    def test_unexpected_and_ambiguous_source_rejected(self):
        for source in ("", OLD + OLD, NEW + NEW, OLD + NEW):
            with self.subTest(source=source), self.assertRaises(ValueError):
                patched_source(source)


if __name__ == "__main__":
    unittest.main()