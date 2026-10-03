"""Direct equivalences must reference existing feats without granting effects."""
import re
import unittest

from spheres_associated_feats import ASSOCIATED, equivalence_tags
from spheres_catalog import inventory
from spheres_catalog_lst import build, key
from spheres_feats import core_feats


class AssociatedFeatTests(unittest.TestCase):
    def test_all_targets_are_loaded_core_feats(self):
        known = set(core_feats().values())
        for ability, feats in ASSOCIATED.items():
            self.assertTrue(set(feats) <= known, (ability, set(feats) - known))

    def test_associations_are_explicit_in_pinned_source(self):
        texts = {}
        for sphere in inventory():
            texts[sphere['sphere'] + ' Sphere'] = sphere['base']
            texts.update((key(sphere, talent), talent['text']) for talent in sphere['talents'])
        for ability, feats in ASSOCIATED.items():
            declarations = re.findall(r'Associated Feats?:[^\n]+', texts[ability])
            for feat in feats:
                self.assertTrue(any(feat in declaration for declaration in declarations), (ability, feat))

    def test_tags_do_not_grant_or_spend_feats(self):
        files, _ = build()
        records = {line.split('\t')[0]: line for content in files.values()
                   for line in content.splitlines() if not line.startswith('#')}
        for ability in ASSOCIATED:
            self.assertIn(equivalence_tags(ability)[0], records[ability])
            self.assertNotIn('ABILITY:FEAT|AUTOMATIC', equivalence_tags(ability)[0])
        for ability in ('Equipment - Dagger Bravo', 'Equipment - Versatile Fighter',
                        'Athletics Sphere', 'Beastmastery Sphere', 'Invented Talent'):
            self.assertEqual(equivalence_tags(ability), [])

    def test_versatile_fighter_has_mutually_exclusive_active_choices(self):
        files, _ = build()
        equipment = files['spheres_might_equipment-sphere.lst']
        talent = next(row for row in equipment.splitlines()
                      if row.startswith('Equipment - Versatile Fighter\t'))
        self.assertIn('BONUS:ABILITYPOOL|Spheres Versatile Fighter Stance|1', talent)
        self.assertNotIn('ABILITY:FEAT|AUTOMATIC', talent)
        self.assertNotIn('SERVESAS:', talent)
        choices = [row for row in files['spheres_catalog_packages.lst'].splitlines()
                   if row.startswith('Versatile Fighter - ')]
        self.assertEqual(len(choices), 3)
        for row in choices:
            grant = next(tag for tag in row.split('\t') if tag.startswith('ABILITY:FEAT'))
            self.assertIn('|PREABILITY:1,CATEGORY=Spheres Combat Talent,Equipment - Versatile Fighter', grant)


if __name__ == '__main__':
    unittest.main()