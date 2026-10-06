"""Guard the pinned temporary-effect removal patch."""
import unittest
from pcgen_temp_filter_fix import OLD, NEW, patched_source


class TempFilterFixTests(unittest.TestCase):
    def test_scoped_and_idempotent(self):
        source = 'before\n' + OLD + '\nafter'
        fixed = patched_source(source)
        self.assertEqual(fixed, 'before\n' + NEW + '\nafter')
        self.assertEqual(patched_source(fixed), fixed)

    def test_missing_duplicate_and_partial_source_rejected(self):
        for source in ('', OLD + OLD, NEW + OLD,
                       '\t\ttheCharacter.unsetTempBonusFilter(tempBonus.toString());\n' + OLD):
            with self.subTest(source=source), self.assertRaises(ValueError):
                patched_source(source)


if __name__ == '__main__':
    unittest.main()