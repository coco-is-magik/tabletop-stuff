"""Source-table and selection-boundary regression for the Elementalist class."""
import unittest

from spheres import DATA, check_package
from pcgen_elementalist_class import expected, fixture


class ElementalistTest(unittest.TestCase):
    def test_source_progression(self):
        for level in range(1, 21):
            with self.subTest(level=level):
                values = expected(level)
                self.assertEqual(values["caster_level"], level * 3 // 4)
                self.assertEqual(values["magic_talents"], 2 + level * 3 // 4)
                self.assertEqual(values["destruction_cl"], level)
                self.assertEqual(values["spell_points"], level + 4)
                self.assertEqual(values["dodge"], level // 4)
                self.assertEqual(fixture(level).count("CLASSABILITIESLEVEL:"), level)
                self.assertEqual(fixture(level).count("KEY:Elementalist Land Speed"), level >= 7)
        for level in (0, 21, -1):
            with self.assertRaises(ValueError):
                fixture(level)
            with self.assertRaises(ValueError):
                expected(level)

    def test_packaging_and_choice_limits(self):
        self.assertIn("PASS", check_package())
        campaign = (DATA / "spheres.pcc").read_text()
        for path in ("spheres_elementalist_class.lst", "spheres_categories_elementalist.lst",
                     "spheres_elementalist.lst"):
            self.assertIn(path, campaign)
        categories = (DATA / "spheres_categories_elementalist.lst").read_text()
        self.assertIn("POOL:SPHERES_ELEMENTALIST_COMBAT_FEATS", categories)
        self.assertIn("SPHERES_ELEMENTALIST_LEVEL>=19", categories)
        self.assertIn("POOL:if(SPHERES_ELEMENTALIST_LEVEL>=3,1,0)", categories)
        abilities = (DATA / "spheres_elementalist.lst").read_text()
        self.assertIn("AUTOMATIC|Destruction Sphere", abilities)
        self.assertIn("BONUS:VAR|SPHERES_DESTRUCTION_CL_BONUS|SPHERES_ELEMENTALIST_LEVEL-SPHERES_CASTER_LEVEL", abilities)
        self.assertIn("BONUS:MOVEADD|TYPE=Walk|SPHERES_ELEMENTALIST_LAND", abilities)
        self.assertIn("DR:10/magic", abilities)
        self.assertNotIn("SPHERES_CONSCRIPT_LEVEL", abilities)


if __name__ == "__main__":
    unittest.main()