"""Protect upstream replacement identities and free racial sphere grants."""
import unittest

from spheres_racial import OPTIONS, OUTPUT, build, source_trait
from spheres_catalog_source import ROOT


class RacialTests(unittest.TestCase):
    def test_generated_records(self):
        self.assertEqual(OUTPUT.read_text(), build())

    def test_replacements_exist_upstream(self):
        root = ROOT / 'vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game/core_essentials/races'
        for race, name, replacements, grant in OPTIONS:
            upstream = (root / race.lower().replace('-', '_') /
                        (race.lower().replace('-', '') + '_abilities_race.lst')).read_text()
            row = next(r for r in build().splitlines()
                       if '\tKEY:' + race + ' ~ Spheres ' + name + '\t' in r)
            for replacement in replacements:
                fact = race.replace('-', '') + '_Replace' + replacement
                self.assertIn(fact, upstream)
                self.assertIn('FACT:' + fact + '|true', row)
            self.assertIn('PRERACE:1,' + race, row)
            self.assertIn('COST:0', row)
            self.assertIn('ABILITY:Spheres Combat Talent|AUTOMATIC|' + grant, row)
            self.assertNotIn('BONUS:ABILITYPOOL', row)

    def test_source_boundaries(self):
        body, _ = source_trait('Gnome', 'Alchemical Training')
        self.assertIn('replaces gnome magic', body)
        self.assertNotIn('Arcane Engineer', body)
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            source_trait('Gnome', 'Invented Trait')

    def test_dreamless_sleep_preserves_second_purchase_exception(self):
        from spheres import DATA, records
        row = next(r for r in records(DATA / 'spheres_might_scout.lst')
                   if r.startswith('Scout - Somnambulance\t'))
        self.assertIn('PREMULT:1,[PREABILITY:1,CATEGORY=Spheres Combat Talent,Scout Sphere]', row)
        self.assertIn('Elf ~ Spheres Dreamless Sleep,Half-Elf ~ Spheres Dreamless Sleep]', row)
        self.assertIn('PREVARLT:SPHERES_SCOUT_SOMNAMBULANCE_COUNT,2', row)


if __name__ == '__main__':
    unittest.main()