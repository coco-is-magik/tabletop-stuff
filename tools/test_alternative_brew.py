import unittest
from spheres_alternative_brew import build, skills, key


class AlternativeBrewTests(unittest.TestCase):
    def test_loaded_craft_and_profession_choices_only(self):
        choices = skills()
        self.assertIn('Craft (Alchemy)', choices)
        self.assertIn('Craft (Mechanical)', choices)
        self.assertIn('Profession (Soldier)', choices)
        self.assertNotIn('Heal', choices)
        self.assertEqual(len(choices), len(set(choices)))
        self.assertEqual(len(choices), len({key(skill) for skill in choices}))
        self.assertTrue(all('(' not in key(skill) for skill in choices))

    def test_guarded_grants_and_single_choice(self):
        category, rows = build()
        self.assertIn('POOL:1', category)
        self.assertIn('EDITPOOL:NO', category)
        for row in rows:
            self.assertIn('!PREABILITY:1,CATEGORY=Special Ability,Martial Drawback - Alternative-Brew (Heal)', row)
            self.assertNotIn('BONUS:ABILITYPOOL', row)
            for tag in row.split('\t'):
                if tag.startswith('BONUS:'):
                    self.assertIn('|PREABILITY:1,CATEGORY=Spheres Combat Talent,Alchemy Sphere', tag)


if __name__ == '__main__':
    unittest.main()