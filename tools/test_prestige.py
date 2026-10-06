"""Prestige progression must use prestige saves and retain entry prerequisites."""
import json
import unittest

from spheres import DATA
from spheres_catalog_source import SNAPSHOTS, PRESTIGE
from spheres_prestige import tempestarii


class PrestigeTests(unittest.TestCase):
    def test_generated_files(self):
        from spheres_prestige import archwizard, forest_lord, waking_sleeper
        files = tempestarii()
        files.update(forest_lord())
        files.update(waking_sleeper())
        files.update(archwizard())
        for name, content in files.items():
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

    def test_forest_lord_source_table_and_progression(self):
        from spheres_prestige import forest_lord
        source = json.loads((SNAPSHOTS / 'forest-lord.json').read_text())
        table = next(r['text'] for r in source['sections'] if r['heading'] == 'Class Features')
        rows = [r.split('|') for r in table.splitlines() if r.startswith('| ')]
        self.assertEqual(len(rows), 5)
        for level, row in enumerate(rows, 1):
            self.assertEqual([int(x.strip().lstrip('+')) for x in row[3:6]],
                             [1, 1, 1] if level <= 2 else [2, 2, 2] if level <= 4 else [3, 3, 3])
        files = forest_lord()
        classes = files['spheres_forest-lord_class.lst']
        for tag in ('TYPE:Prestige.PC', 'MAXLEVEL:5', 'PREVARGTEQ:SPHERES_CL_NATURE,5',
                    'PREABILITY:1,CATEGORY=Spheres Magic Talent,Nature Sphere',
                    'PREABILITY:1,CATEGORY=Spheres Nature Package,Nature Package - Plant',
                    'PRESKILL:2,Acrobatics=5,Knowledge (Nature)=5',
                    'PRESKILL:1,Survival=5'):
            self.assertIn(tag, classes)
        self.assertEqual(classes.count('BONUS:VAR|SPHERES_MAGIC_TALENTS|1'), 5)
        self.assertNotIn('Weapon Prof', classes)
        abilities = files['spheres_forest-lord_features.lst']
        self.assertIn('CRYPTWOOD_DR|SPHERES_FOREST_LORD_LEVEL', abilities)
        self.assertIn('JUMP_BONUS|2*SPHERES_FOREST_LORD_LEVEL', abilities)
        self.assertIn('STRENGTH_INHERENT|if(SPHERES_FOREST_LORD_LEVEL>=5,6', abilities)
        self.assertIn('CLIMB_SPEED|if(SPHERES_FOREST_LORD_LEVEL>=5,40', abilities)
        self.assertIn('CLASS:spheres_forest-lord_class.lst', (DATA / 'spheres.pcc').read_text())

    def test_waking_sleeper_source_table_and_progression(self):
        from spheres_prestige import waking_sleeper
        source = json.loads((SNAPSHOTS / 'waking-sleeper.json').read_text())
        table = next(r['text'] for r in source['sections'] if r['heading'] == 'Class Features')
        rows = [r.split('|') for r in table.splitlines() if r.startswith('| ')]
        self.assertEqual(len(rows), 5)
        for level, row in enumerate(rows, 1):
            self.assertEqual(int(row[2].strip().lstrip('+')), level)
        files = waking_sleeper()
        classes = files['spheres_waking-sleeper_class.lst']
        for tag in ('TYPE:Prestige.PC', 'MAXLEVEL:5', 'PREVARGTEQ:BAB,3',
                    'PRESKILL:1,Knowledge (Nobility)=5'):
            self.assertIn(tag, classes)
        self.assertIn('BONUS:SAVE|BASE.Fortitude|floor(CL/3)', classes)
        self.assertNotIn('BONUS:VAR|SPHERES_MAGIC_TALENTS', classes)
        abilities = files['spheres_waking-sleeper_features.lst']
        self.assertIn('RECALL_ROUNDS|2+2*SPHERES_WAKING_SLEEPER_LEVEL', abilities)
        self.assertIn('RECALL_STR|if(SPHERES_WAKING_SLEEPER_LEVEL>=5,6,2)', abilities)
        self.assertIn('RECALL_WILL|if(SPHERES_WAKING_SLEEPER_LEVEL>=5,6,if(SPHERES_WAKING_SLEEPER_LEVEL>=3,4,2))', abilities)
        self.assertIn('RECALL_FEATS|if(SPHERES_WAKING_SLEEPER_LEVEL>=5,5,if(SPHERES_WAKING_SLEEPER_LEVEL>=3,3,1))', abilities)
        self.assertIn('CLASS:spheres_waking-sleeper_class.lst', (DATA / 'spheres.pcc').read_text())

    def test_archwizard_source_table_and_progression(self):
        from spheres_prestige import archwizard
        source = json.loads((SNAPSHOTS / 'spheres-archwizard.json').read_text())
        table = next(r['text'] for r in source['sections'] if r['heading'] == 'Class Features')
        rows = [r.split('|') for r in table.splitlines() if r.startswith('| ')]
        self.assertEqual(len(rows), 10)
        for level, row in enumerate(rows, 1):
            self.assertEqual(int(row[1].strip()), level)
            self.assertEqual(int(row[2].strip().lstrip('+')), level // 2)
        files = archwizard()
        classes = files['spheres_archwizard_class.lst']
        for tag in ('TYPE:Prestige.PC', 'MAXLEVEL:10', 'PREVARGTEQ:SPHERES_CASTER_LEVEL,5'):
            self.assertIn(tag, classes)
        self.assertEqual(classes.count('BONUS:VAR|SPHERES_MAGIC_TALENTS|1'), 10)
        self.assertNotIn('Weapon Prof', classes)
        abilities = files['spheres_archwizard_features.lst']
        self.assertIn('BONUS:SKILL|Knowledge (Arcana),Spellcraft,Use Magic Device|5|TYPE=Insight', abilities)
        self.assertIn('METAMAGIC_REDUCTION|if(SPHERES_ARCHWIZARD_LEVEL>=10,3,if(SPHERES_ARCHWIZARD_LEVEL>=5,2,1))', abilities)
        self.assertIn('SPELL_ECHO_USES|floor(SPHERES_ARCHWIZARD_LEVEL/2)', abilities)
        self.assertIn('ARCHWIZARDRY_USES|max(1,floor(SPHERES_CASTER_LEVEL/6))', abilities)
        self.assertIn('CLASS:spheres_archwizard_class.lst', (DATA / 'spheres.pcc').read_text())

    def test_magemage_source_table_and_progression(self):
        from spheres_prestige import magemage
        source = json.loads((SNAPSHOTS / 'magemage.json').read_text())
        table = next(r['text'] for r in source['sections'] if 'Table: Magemage' in r['text'])
        rows = [r.split('|') for r in table.splitlines() if r.startswith('| ')
                and r.split('|')[1].strip().isdigit()]
        self.assertEqual(len(rows), 10)
        for level, row in enumerate(rows, 1):
            self.assertEqual(int(row[1].strip()), level)
            self.assertEqual(int(row[2].strip().lstrip('+')), level // 2)
            self.assertEqual(int(row[5].strip().lstrip('+')), (level + 1) // 2)
        files = magemage()
        classes = files['spheres_magemage_class.lst']
        for tag in ('TYPE:Prestige.PC', 'MAXLEVEL:10', 'PRECLASS:1,Mageknight=1',
                    'PRESKILL:1,Spellcraft=5', 'HD:8',
                    'BONUS:COMBAT|BASEAB|floor(CL/2)|TYPE=Base.REPLACE',
                    'BONUS:VAR|SPHERES_CASTER_LEVEL,SPHERES_MAGIC_SKILL_BONUS,SPHERES_SPELL_POOL_LEVELS|CL'):
            self.assertIn(tag, classes)
        self.assertEqual(classes.count('BONUS:VAR|SPHERES_MAGIC_TALENTS|1'), 10)
        abilities = files['spheres_magemage_features.lst']
        self.assertIn('Magemage Aligned Class', abilities)
        self.assertIn('SAGACITY_BONUS|max(1,INT)', abilities)
        self.assertIn('SPELLWROUGHT_DIE|floor(SPHERES_MAGEMAGE_LEVEL/2)', abilities)
        self.assertIn('CROWN_CL_BONUS|2', abilities)
        self.assertIn('CLASS:spheres_magemage_class.lst', (DATA / 'spheres.pcc').read_text())


if __name__ == '__main__':
    unittest.main()