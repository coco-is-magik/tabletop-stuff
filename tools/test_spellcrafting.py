"""Offline regression checks for reviewed custom-spell compilation."""
import copy
import json
import unittest

from spheres_spellcrafting import build, DEFINITIONS, OUTPUT, references


class SpellcraftingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(DEFINITIONS.read_text())
        cls.known = references()

    def render(self, edit=None):
        source = copy.deepcopy(self.source)
        if edit:
            edit(source['spells'][0])
        return build(source, self.known)

    def test_generated_file(self):
        self.assertEqual(OUTPUT.read_text(), self.render())

    def test_published_example(self):
        output = self.render()
        for text in ('Complexity 2; 3 SP; 1 casting-time increases',
                     'Research Spellcraft DC 10; learning 2 hours',
                     'spellbook 2 pages; writing 2 hours; decipher DC 22',
                     '|SPHERES_CL_PROTECTION|SPHERES_DC_PROTECTION'):
            self.assertIn(text, output)

    def test_learning_does_not_require_creation_feat(self):
        rows = self.render().splitlines()
        self.assertNotIn('PREFEAT:', rows[1])
        self.assertIn('PREFEAT:1,Spellcrafting', rows[2])
        self.assertNotIn('PREFEAT:', rows[3])
        self.assertIn('PREMULT:1,', rows[3])
        for row in rows[1:]:
            self.assertIn('CATEGORY=Spheres Magic Talent,Life Sphere', row)
            self.assertIn('CATEGORY=Spheres Magic Talent,Protection Sphere', row)

    def test_complexity_rounding_and_floor(self):
        for count in range(8):
            result = self.render(lambda s: s.update(changes=['foreign_talent_or_feat'] * count))
            self.assertIn(f'Complexity {count}; {2 + count // 2} SP; {(count + 1) // 2} casting-time', result)
        result = self.render(lambda s: s.update(changes=['decrease_duration'] * 3, duration_cost_adjustment=-2))
        self.assertIn('Complexity 0; 1 SP; 0 casting-time', result)

    def test_unknown_components_and_invalid_input(self):
        edits = [lambda s: s.update(base_sphere='Unknown'),
                 lambda s: s.update(review=''),
                 lambda s: s.update(name='Injected\tCATEGORY:FEAT'),
                 lambda s: s.update(changes=['invented']),
                 lambda s: s.update(duration_cost_adjustment=True),
                 lambda s: s['components'][0].update(key='Missing Sphere'),
                 lambda s: s['components'][0].update(kind='talent'),
                 lambda s: s['components'][0].update(spell_points=-1),
                 lambda s: s['components'].append(copy.deepcopy(s['components'][0]))]
        for edit in edits:
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                self.render(edit)

    def test_duplicates_and_schema(self):
        source = copy.deepcopy(self.source)
        source['spells'] *= 2
        with self.assertRaises(ValueError):
            build(source, self.known)
        for version in (True, 2, '1'):
            source = copy.deepcopy(self.source)
            source['version'] = version
            with self.assertRaises(ValueError):
                build(source, self.known)


if __name__ == '__main__':
    unittest.main()