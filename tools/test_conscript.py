"""Class-only contracts; live PCGen tests are in pcgen_conscript_class.py."""
import unittest

from spheres import DATA, check_package
from pcgen_conscript_class import fixture, expected, TALENTS, PURCHASES


class ConscriptTest(unittest.TestCase):
    def test_chassis(self):
        text = (DATA / "spheres_conscript_class.lst").read_text()
        for tag in ("CLASS:Conscript", "HD:10", "MAXLEVEL:20", "STARTSKILLPTS:4",
                    "BASEAB|CL", "BASE.Fortitude,BASE.Reflex|2+floor(CL/2)",
                    "BASE.Will|floor(CL/3)", "AUTO:SHIELDPROF|Buckler"):
            self.assertIn(tag, text)
        self.assertNotIn("Spheres Casting Core", text)
        self.assertNotIn("SPHERES_MAGIC_TALENTS", text)
        self.assertIn("PASS", check_package())

    def test_fixture_matrix(self):
        costs = {"Gear Training": 1, "Fast Movement": 2, "Indomitable Will": 1, "Evasion": 1}
        for level in range(1, 21):
            self.assertEqual(TALENTS[level - 1], level + (level + 1) // 2)
            for mental in ("INT", "WIS", "CHA"):
                for points in range(6):
                    text = fixture(level, mental, points)
                    self.assertEqual(text.count("CLASSABILITIESLEVEL:"), level)
                    self.assertEqual(sum(costs[name] for name in PURCHASES[points]), points)
                    self.assertEqual(expected(level, mental, points)["bab"], level)
                    self.assertIn("APPLIEDTO:Acrobatics,Stealth,Bluff", text)
                    self.assertNotIn("CLASS:Incanter", text)
        for args in ((0, "INT", 0), (21, "INT", 0), (1, "STR", 0), (1, "WIS", -1), (1, "WIS", 6)):
            with self.assertRaises(ValueError):
                fixture(*args)

    def test_selection_boundaries(self):
        text = (DATA / "spheres_categories_conscript.lst").read_text()
        for tag in ("TYPE:Combat.Teamwork", "POOL:5*min(1,SPHERES_CONSCRIPT_LEVEL)",
                    "POOL:3*min(1,SPHERES_CONSCRIPT_LEVEL)", "POOL:SPHERES_COMBAT_TALENTS"):
            self.assertIn(tag, text)
        abilities = (DATA / "spheres_conscript.lst").read_text()
        self.assertIn("CHOOSE:SKILL|!CLASS\tCSKILL:LIST", abilities)
        self.assertIn("KEY", fixture(1))
        self.assertIn("CHOOSE:USERINPUT", abilities)
        for line in abilities.splitlines():
            if "CATEGORY:Conscript Specialization\t" in line:
                self.assertIn("PREVAREQ:SPHERES_CONSCRIPT_LEVEL,1", line)
                self.assertIn("BONUS:VAR|SPHERES_CONSCRIPT_SPECIALIZATION_POINTS|", line)
        self.assertNotIn("Incanter Active Specialization", abilities)
        self.assertIn("BONUS:VAR|SPHERES_COMBAT_TALENTS|-1-floor((SPHERES_CONSCRIPT_LEVEL-1)/4)", abilities)


if __name__ == "__main__":
    unittest.main()