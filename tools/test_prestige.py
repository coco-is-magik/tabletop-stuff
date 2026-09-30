"""Prestige progression must use prestige saves and retain entry prerequisites."""
import json
import unittest

from spheres import DATA
from spheres_catalog_source import SNAPSHOTS, PRESTIGE
from spheres_prestige import tempestarii


class PrestigeTests(unittest.TestCase):
    def test_generated_files(self):
        for name, content in tempestarii().items():
            self.assertEqual((DATA / name).read_text(), content)

    def test_source_table(self):
        source = json.loads((SNAPSHOTS / 'tempestarii.json').read_text())
        table = next(r['text'] for r in source['sections'] if r['heading'] == 'Class Features')
        rows = [r.split('|') for r in table.splitlines() if r.startswith('| ')]
        self.assertEqual(len(rows), 5)
        for level, row in enumerate(rows, 1):
            self.assertEqual([int(x.strip().lstrip('+')) for x in row[2:6]],
                             [level // 2, (level + 1) // 3, (level + 1) // 3, (level + 1) // 2])
        classes = tempestarii()['spheres_tempestarii_class.lst']
        for tag in ('TYPE:Prestige.PC', 'MAXLEVEL:5', 'PREVARGTEQ:SPHERES_CL_WEATHER,5',
                    'PRESKILL:1,Knowledge (Nature)=5',
                    'PREABILITY:1,CATEGORY=Spheres Magic Talent,Weather Sphere'):
            self.assertIn(tag, classes)
        self.assertEqual(classes.count('BONUS:VAR|SPHERES_MAGIC_TALENTS|1'), 5)
        self.assertNotIn('Weapon Prof', classes)

    def test_inventory_uses_spheres_archwizard(self):
        self.assertIn('spheres-archwizard', PRESTIGE)
        self.assertNotIn('archwizard', PRESTIGE)
        for slug in PRESTIGE:
            self.assertTrue((SNAPSHOTS / (slug + '.json')).is_file(), slug)


if __name__ == '__main__':
    unittest.main()