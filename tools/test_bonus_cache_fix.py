"""Safety checks for the pinned active-bonus cache patch."""
import unittest

from pcgen_bonus_cache_fix import OLD, NEW, OLD_WRITE, NEW_WRITE, patched_source


class BonusCacheFixTests(unittest.TestCase):
    def test_patch_is_scoped_and_idempotent(self):
        original = 'before\n' + OLD + '\nmiddle\n' + OLD_WRITE + '\nafter'
        fixed = patched_source(original)
        self.assertEqual(fixed, 'before\n' + NEW + '\nmiddle\n' + NEW_WRITE + '\nafter')
        self.assertEqual(patched_source(fixed), fixed)
        self.assertIn('if (targetMap == activeBonusMap)', fixed)

    def test_unexpected_or_partial_source_rejected(self):
        for text in ('', OLD, OLD_WRITE, OLD + OLD + OLD_WRITE,
                     OLD + OLD_WRITE + OLD_WRITE, NEW + OLD_WRITE, OLD + NEW_WRITE):
            with self.subTest(text=text), self.assertRaises(ValueError):
                patched_source(text)


if __name__ == '__main__':
    unittest.main()