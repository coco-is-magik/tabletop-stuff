"""Regression checks for weighted tradition choices using existing PCGen pools."""
import unittest

from spheres import DATA, records
from spheres_traditions import build, OUTPUT, sections, LEGACY, DEFERRED, CONFLICTS


class TraditionTests(unittest.TestCase):
    def test_feat_casters_qualify_for_custom_tradition(self):
        self.assertIn('CATEGORY=Custom Casting Tradition|Custom Casting Tradition.MOD\t'
                      'PRE:.CLEAR\tPREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core', build())

    def test_embodiment_records_substance_without_unpublished_repeat(self):
        row = next(row for row in build().splitlines() if row.startswith('Tradition - Embodiment\t'))
        self.assertIn('CHOOSE:USERINPUT|1|TITLE=Substance embodied', row)
        self.assertIn('PREVARLT:SPHERES_TRADITION_EMBODIMENT,1', row)
        self.assertIn('COST:2', row)
        self.assertIn('BONUS:VAR|SPHERES_TRADITION_BOONS|1', row)
        self.assertNotIn('BONUS:VAR|SPHERES_CASTER_LEVEL', row)

    def test_drawback_feat_reuses_feat_records(self):
        row = next(row for row in build().splitlines() if row.startswith('Tradition - Drawback Feat\t'))
        for tag in ('COST:2', 'MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                    'BONUS:ABILITYPOOL|Casting Tradition Drawback Feat|1'):
            self.assertIn(tag, row.split('\t'))
        category = next(row for row in records(DATA / 'spheres_categories_traditions.lst')
                        if row.startswith('ABILITYCATEGORY:Casting Tradition Drawback Feat\t'))
        self.assertIn('CATEGORY:FEAT', category)
        self.assertIn('TYPE:Drawback', category)

    def test_generated_ultimate_coverage(self):
        output = build()
        self.assertEqual(OUTPUT.read_text(), output)
        for key in sections('General Drawbacks'):
            if key not in LEGACY | DEFERRED:
                self.assertIn('Tradition - ' + key + '\tCATEGORY:Custom Casting Drawback', output)
        self.assertNotIn('Creating and Using a Deck\t', output)
        self.assertNotIn('Tradition - Card Casting\t', output)

    def test_conflicts_are_symmetric_across_generated_and_legacy(self):
        output = {}
        for row in build().splitlines()[1:]:
            key = row.split('\t')[0].removesuffix('.MOD').split('|')[-1]
            output[key] = output.get(key, '') + '\t' + row
        for pair in CONFLICTS:
            for left, right in (pair, pair[::-1]):
                self.assertIn('!PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - ' + right,
                              output['Tradition - ' + left])

    @classmethod
    def setUpClass(cls):
        cls.rows = {row.split('\t')[0]: row.split('\t')[1:]
                    for row in records(DATA / 'spheres_traditions.lst')}

    def test_second_selections_require_first_and_keep_legacy_key(self):
        for name in ('Somatic Casting', 'Extended Casting'):
            first = 'Tradition - ' + name
            second = first + ' Second Selection'
            self.assertIn(first, self.rows)
            self.assertIn('PREABILITY:1,CATEGORY=Custom Casting Drawback,' + first,
                          self.rows[second])
            for key in (first, second):
                self.assertIn('PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
                              self.rows[key])
                self.assertNotIn('MULT:YES', self.rows[key])

    def test_weighted_choices_charge_and_award_equal_points(self):
        for name, weight in (('Somatic Casting', 1), ('Extended Casting', 2)):
            for suffix in ('', ' Second Selection'):
                tags = self.rows['Tradition - ' + name + suffix]
                self.assertIn(f'BONUS:ABILITYPOOL|Custom Casting Boon|{weight}', tags)
                self.assertIn(f'BONUS:VAR|SPHERES_TRADITION_DRAWBACKS|{weight}', tags)
                cost = next((tag[5:] for tag in tags if tag.startswith('COST:')), '1')
                self.assertEqual(int(cost), weight)
                self.assertFalse(any(tag.startswith('DEFINE:') for tag in tags))

    def test_preparation_incompatibility_is_symmetric(self):
        for left, right in (('Prepared Caster', 'Charged Spells'),
                            ('Charged Spells', 'Prepared Caster')):
            self.assertIn('!PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - ' + right,
                          self.rows['Tradition - ' + left])

    def test_charged_credit_is_not_a_spell_point_drawback(self):
        tags = self.rows['Tradition - Charged Spells']
        self.assertIn('BONUS:ABILITYPOOL|Custom Casting Boon|2', tags)
        self.assertIn('BONUS:VAR|SPHERES_TRADITION_DRAWBACKS|1', tags)
        self.assertIn('BONUS:VAR|SPHERES_TRADITION_BOON_ONLY|1', tags)
        self.assertIn('BONUS:VAR|SPHERES_TRADITION_REMAINING|max(0,SPHERES_TRADITION_DRAWBACKS-max(0,2*SPHERES_TRADITION_BOONS-SPHERES_TRADITION_BOON_ONLY))',
                      self.rows['Custom Casting Tradition'])


if __name__ == '__main__':
    unittest.main()