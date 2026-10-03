import unittest

from spheres_custom_training import build, weapons


class CustomTrainingTests(unittest.TestCase):
    def test_existing_weapon_keys_and_weighted_costs(self):
        costs = weapons()
        self.assertEqual(costs['Longsword'], 1)
        self.assertEqual(costs['Dagger'], 1)
        self.assertEqual(costs['Sword (Bastard)'], 2)
        self.assertNotIn('Bastard Sword', costs)
        self.assertNotIn('Longsword.MOD', costs)

    def test_grants_are_guarded_and_nonrepeatable(self):
        category, choices = build()
        self.assertIn('POOL:0', category)
        self.assertIn('EDITPOOL:NO', category)
        self.assertEqual(len(choices), len(weapons()))
        for row in choices:
            self.assertNotIn('MULT:YES', row)
            grant = next(tag for tag in row.split('\t') if tag.startswith('AUTO:'))
            self.assertIn('|PREABILITY:1,CATEGORY=Spheres Combat Talent,Equipment - Custom Training', grant)
            self.assertNotIn('ABILITY:FEAT', row)


if __name__ == '__main__':
    unittest.main()