import unittest

from spheres_martial_traditions import TRADITIONS, PACKAGES, build, catalog, expand, sources
from spheres_catalog import inventory


class MartialTraditionTests(unittest.TestCase):
    def test_elven_duelist_two_finesse_ranks(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        row = next(row for row in output.splitlines()
                   if row.startswith('Martial Tradition - Elven Duelist\t'))
        grant = next(tag for tag in row.split('\t')
                     if tag.startswith('ABILITY:Spheres Combat Talent|AUTOMATIC|Equipment -'))
        self.assertEqual(grant.count('|Equipment - Finesse Fighting'), 1)
        self.assertIn('BONUS:VAR|SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT|1', row)
        self.assertIn('BONUS:VAR|SPHERES_EQUIPMENT_TALENTS|1', row)

    def test_targeted_inventory_preserves_equipment_catalog(self):
        self.assertEqual(inventory(['equipment-sphere']),
                         [row for row in inventory() if row['slug'] == 'equipment-sphere'])

    def test_generated_files(self):
        for path, content in build().items():
            self.assertEqual(path.read_text(), content)

    def test_four_talents_and_source_coverage(self):
        for name, (fixed, choices) in TRADITIONS.items():
            self.assertIn(name, sources())
            linked = 2 if name == 'Tattooed Warrior' else 1 if name in ('Highlander', 'Janjaweed') else 0
            self.assertEqual(len(fixed) + sum(count for count, _ in choices) + linked, 4, name)
            self.assertTrue(name in ('Iron Breaker Style', 'Free Runner') or any(key.startswith('Equipment - ') for key in fixed)
                            or any('Equipment discipline*' in options for _, options in choices))

    def test_equipment_free_tradition_does_not_grant_equipment(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        row = next(row for row in output.splitlines()
                   if row.startswith('Martial Tradition - Iron Breaker Style\t'))
        self.assertNotIn('|Equipment Sphere', row)
        self.assertNotIn('BONUS:ABILITYPOOL|Spheres Equipment Bonus Talent', row)
        self.assertIn('|Berserker - Greater Sunder', row)

    def test_tattooed_warrior_reuses_feats_and_restricted_ranks(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        row = next(row for row in output.splitlines()
                   if row.startswith('Martial Tradition - Tattooed Warrior\t'))
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Dragon’s Tattoos|Zodiac Tattoos', row)
        self.assertIn('BONUS:SKILLRANK|Craft (Tattoos)|TL', row)
        self.assertNotIn('BONUS:SKILLPOINTS', row)

    def test_choices_resolve_and_never_include_advanced_talents(self):
        abilities = catalog()
        for _, choices in TRADITIONS.values():
            for _, options in choices:
                for key in expand(options, abilities):
                    self.assertNotIn('SpheresLegendaryTalent', abilities[key])
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            expand(['Invented Sphere'], abilities)
        with self.assertRaisesRegex(ValueError, 'Empty'):
            expand(['Invented*'], abilities)

    def test_fixed_packages_replace_free_package_slot(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        rows = {row.split('\t')[0]: row for row in output.splitlines()}
        for title, (sphere, package) in PACKAGES.items():
            row = rows['Martial Tradition - ' + title]
            self.assertIn('ABILITY:Spheres ' + sphere + ' Package|AUTOMATIC|' + sphere + ' Package - ' + package, row)
            self.assertIn('BONUS:ABILITYPOOL|Spheres ' + sphere + ' Package|-1', row)

    def test_optional_riding_package_is_conditional(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        for title in ('Bushido Warrior', 'Imperialist', 'Knightly Arts'):
            row = next(row for row in output.splitlines()
                       if row.startswith('Martial Tradition - ' + title + '\t'))
            self.assertNotIn('Beastmastery Package', row)
            branch = next(row for row in output.splitlines()
                          if row.startswith(title + ' Tradition Choice 1 - Beastmastery Sphere\t'))
            self.assertIn('ABILITY:Spheres Beastmastery Package|AUTOMATIC|Beastmastery Package - Ride', branch)
            self.assertIn('BONUS:ABILITYPOOL|Spheres Beastmastery Package|-1', branch)
            self.assertIn('PREABILITY:1,CATEGORY=Conscript Martial Tradition,Martial Tradition - ' + title, branch)

    def test_highlander_talent_tracks_selected_sphere(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        for sphere, other in (('Scout', 'Dual Wielding'), ('Dual Wielding', 'Scout')):
            branch = next(row for row in output.splitlines()
                          if row.startswith('Highlander Tradition Choice 1 - ' + sphere + ' Sphere\t'))
            self.assertIn('BONUS:ABILITYPOOL|Highlander ' + sphere + ' Talent|1', branch)
            self.assertNotIn('Highlander ' + other + ' Talent', branch)

    def test_janjaweed_branches_are_pairs_not_independent_choices(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        rows = {row.split('\t')[0]: row for row in output.splitlines()}
        mounted = rows['Janjaweed Tradition Choice 1 - Mounted Training']
        gunmanship = rows['Janjaweed Tradition Choice 1 - Gunmanship']
        self.assertIn('BONUS:ABILITYPOOL|Janjaweed Beastmastery Talents|2', mounted)
        self.assertNotIn('|Barrage Sphere', mounted)
        self.assertIn('ABILITY:Spheres Combat Talent|AUTOMATIC|Barrage Sphere|Sniper Sphere', gunmanship)
        self.assertNotIn('BONUS:ABILITYPOOL', gunmanship)

    def test_wandering_artist_can_choose_existing_unarmed_feat(self):
        output = next(content for path, content in build().items()
                      if path.name == 'spheres_martial_traditions.lst')
        row = next(row for row in output.splitlines() if row.startswith(
            'Wandering Martial Artist Tradition Choice 1 - Improved Unarmed Strike\t'))
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Improved Unarmed Strike', row)
        self.assertNotIn('BONUS:ABILITYPOOL|FEAT', row)
        force = next(row for row in output.splitlines()
                     if row.startswith('Equipment - Force Redirection Technique\t'))
        self.assertIn('TYPE:SpheresLegendaryTalent.Equipment', force)
        self.assertNotIn('SpheresBasicTalent', force)


if __name__ == '__main__':
    unittest.main()