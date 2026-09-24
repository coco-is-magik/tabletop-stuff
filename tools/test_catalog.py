"""Offline catalog integrity; live controller evidence is pcgen_catalog.py."""
import json
import unittest
from spheres_catalog import inventory, MANIFEST
from spheres_catalog_lst import build, DATA, key, repeat_limit, text, PACKAGES
from spheres_catalog_source import Page


class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = inventory()
        cls.files, cls.review = build()

    def test_pinned_inventory(self):
        self.assertEqual(self.rows, json.loads(MANIFEST.read_text()))
        self.assertEqual(len(self.rows), 53)
        self.assertEqual(sum(len(r['talents']) for r in self.rows), 2330)
        self.assertEqual(sum(r['system'] == 'power' for r in self.rows), 26)

    def test_generated_files_and_campaign(self):
        campaign = (DATA / 'spheres.pcc').read_text()
        for name, content in self.files.items():
            self.assertEqual((DATA / name).read_text(), content, name)
            self.assertTrue(any(line.endswith(':' + name) for line in campaign.splitlines()))

    def test_keys_and_prerequisites(self):
        keys = set()
        for record in self.review:
            self.assertNotIn(record['key'], keys)
            self.assertNotIn(',', record['key'])
            keys.add(record['key'])
            self.assertTrue(any('Sphere' in p for p in record['prerequisites']))

    def test_no_advanced_or_original_import(self):
        for row in self.rows:
            for talent in row['talents']:
                self.assertNotIn('Advanced', talent['group'])
                self.assertNotIn('Legendary', talent['group'])
        destruction = next(r for r in self.rows if r['slug'] == 'destruction')
        self.assertEqual(key(destruction, {'name': 'Admixture'}), 'Admixture')

    def test_repeat_detection(self):
        for rule, expected in [('You may take this talent up to two times.', 2),
                               ('You can take this talent a second time.', 2),
                               ('You may take this talent multiple times.', 99),
                               ('Deals two times your level in damage.', 1)]:
            self.assertEqual(repeat_limit({'text': rule}), expected)

    def test_mechanical_overrides_resolve_to_catalog_records(self):
        overrides = json.loads((DATA / 'catalog-mechanics.json').read_text())
        records = {row['sphere'] + ' Sphere' for row in self.rows}
        records.update(key(row, talent) for row in self.rows for talent in row['talents'])
        self.assertFalse(set(overrides) - records)
        for name, tags in overrides.items():
            self.assertTrue(tags, name)
            self.assertTrue(all('\t' not in tag and '\n' not in tag for tag in tags), name)

    def test_package_pools_and_equipment_grant(self):
        categories = self.files['spheres_categories_catalog.lst']
        self.assertEqual(categories.count('ABILITYCATEGORY:'), len(PACKAGES) + 1)
        equipment_pool = next(line for line in categories.splitlines() if line.startswith('ABILITYCATEGORY:Spheres Equipment Bonus Talent'))
        self.assertIn('TYPE:EquipmentTalent\t', equipment_pool)
        self.assertNotIn('TYPE:Equipment\t', equipment_pool)
        self.assertIn('BONUS:ABILITYPOOL|Spheres Equipment Bonus Talent|1', self.files['spheres_might_equipment-sphere.lst'])
        self.assertIn('BONUS:SKILLRANK|Bluff|min(TL,5*SPHERES_FENCING_TALENTS)', self.files['spheres_might_fencing.lst'])
        self.assertIn('BONUS:VAR|SPHERES_ATHLETICS_PACKAGES|2', self.files['spheres_might_athletics.lst'])
        beast = self.files['spheres_might_beastmastery.lst']
        self.assertIn('Extra Beastmastery Package', beast)
        self.assertIn('BONUS:VAR|SPHERES_BEASTMASTERY_PACKAGES|1', beast)

    def test_source_parser_boundaries(self):
        page = Page()
        page.feed('<div>outside</div><div id="page-content"><h2 id="one">Talent</h2><p>Rule &amp; text</p></div><p>outside</p>')
        self.assertEqual(page.sections[-1]['heading'], 'Talent')
        self.assertEqual(page.sections[-1]['text'], 'Rule & text')
        self.assertEqual(text('10% (a|b)'), '10 percent [a/b]')


if __name__ == '__main__':
    unittest.main()