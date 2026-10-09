"""Checks for generated Incanter Sphere Specialization records."""
import json
import unittest

from spheres import DATA, records
from spheres_catalog_source import SNAPSHOTS
from spheres_incanter_specializations import (build, OUTPUT, CATEGORIES, sphere_sections,
                                              sphere_name, var_name, pool_key, EXISTING)


def campaign_records():
    """Every record key across the campaign's ability files."""
    keys = set()
    for path in sorted(DATA.glob("*.lst")):
        for line in records(path):
            keys.add(line.split('\t')[0])
    return keys


class IncanterSpecializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text, cls.category_text = build()
        cls.rows = {}
        for line in cls.text.splitlines():
            if '\t' in line:
                cells = line.split('\t')
                cls.rows[cells[0]] = cells[1:]
        cls.spheres = [sphere for sphere, _row in sphere_sections()]
        cls.campaign = campaign_records()
        cls.defines = ''.join(path.read_text(encoding='utf-8')
                              for path in sorted(DATA.glob('*.lst')))

    def test_generated_files_are_current(self):
        self.assertEqual(OUTPUT.read_text(), self.text)
        self.assertEqual(CATEGORIES.read_text(), self.category_text)

    def test_every_published_sphere_is_present(self):
        source = json.loads((SNAPSHOTS / 'incanter.json').read_text())
        published = {sphere_name(row['heading']) for row in source['sections']
                     if row['level'] == 3 and 'Sub-Specialization' not in row['heading']}
        generated = {sphere for sphere, _row in sphere_sections()}
        self.assertEqual(generated, published)
        for sphere in published:
            if sphere in EXISTING:
                continue
            self.assertIn('Sphere Specialization (' + sphere + ')', self.rows, sphere)

    def test_taking_a_specialization_grants_its_sphere_and_caster_level(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            purchase = self.rows['Sphere Specialization (' + sphere + ')']
            self.assertIn('ABILITY:Spheres Magic Talent|AUTOMATIC|' + sphere + ' Sphere',
                          purchase, sphere)
            self.assertIn('BONUS:VAR|SPHERES_CL_' + var_name(sphere) + '|1', purchase, sphere)
            # The bonused caster-level variable is defined by the campaign.
            self.assertIn('DEFINE:SPHERES_CL_' + var_name(sphere), self.defines)
            # Both grants belong to the taken specialization, not to activation.
            active = self.rows['Active Sphere Specialization (' + sphere + ')']
            self.assertNotIn('ABILITY:Spheres Magic Talent|AUTOMATIC|' + sphere + ' Sphere', active)
            self.assertNotIn('BONUS:VAR|SPHERES_CL_' + var_name(sphere), active)

    def test_already_known_variant_grants_a_talent_instead_of_the_sphere(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            base = self.rows['Sphere Specialization (' + sphere + ')']
            known = self.rows['Sphere Specialization (' + sphere + ') - Already Known']
            # The alternative is an explicit, mutually exclusive pair. Both records are
            # hidden when the other applies, and the base record is also hidden once the
            # sphere is held - a selection prerequisite is checked when the choice is
            # made, so it is not broken by the record's own sphere grant.
            self.assertIn('!PREABILITY:1,CATEGORY=Spheres Magic Talent,' + sphere + ' Sphere',
                          base)
            self.assertIn('!PREABILITY:1,CATEGORY=Incanter Specialization,Sphere'
                          ' Specialization (' + sphere + ') - Already Known', base)
            self.assertNotIn('ABILITY:Spheres Magic Talent|AUTOMATIC|' + sphere + ' Sphere', known)
            # Only offered when the sphere is already possessed (never grants it, so the
            # test is stable); the base record stays available either way, because PCGen
            # evaluates a grant against the post-grant state.
            self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,' + sphere + ' Sphere', known)
            self.assertIn('!PREABILITY:1,CATEGORY=Incanter Specialization,Sphere'
                          ' Specialization (' + sphere + ')', known)
            self.assertIn('BONUS:ABILITYPOOL|' + pool_key(sphere) + '|1', known)
            # Both variants are equal-cost and both keep the sphere caster level.
            for row in (base, known):
                self.assertIn('COST:3', row)
                self.assertIn('BONUS:VAR|SPHERES_INCANTER_SPECIALIZATION_POINTS|3', row)
                self.assertIn('BONUS:VAR|SPHERES_CL_' + var_name(sphere) + '|1', row)

    def test_activation_accepts_either_variant(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            active = self.rows['Active Sphere Specialization (' + sphere + ')']
            self.assertIn(
                f'PREMULT:1,[PREABILITY:1,CATEGORY=Incanter Specialization,Sphere'
                f' Specialization ({sphere})],[PREABILITY:1,CATEGORY=Incanter'
                f' Specialization,Sphere Specialization ({sphere}) - Already Known]', active)

    def test_talent_pool_is_restricted_to_its_sphere(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            self.assertIn(
                f'ABILITYCATEGORY:{pool_key(sphere)}\tCATEGORY:Spheres Magic Talent'
                f'\tTYPE:SpheresBasicTalent.{sphere}', self.category_text, sphere)

    def test_activation_only_brings_abilities_into_effect(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            active = self.rows['Active Sphere Specialization (' + sphere + ')']
            self.assertTrue(any(tag.startswith('ABILITY:Special Ability|AUTOMATIC|')
                                for tag in active), sphere)
            for tag in active:
                if tag.startswith('BONUS:VAR'):
                    self.fail(f'{sphere} activation must not grant variables: {tag}')

    def test_sphere_reference_resolves_to_a_sphere_record(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            self.assertIn(sphere + ' Sphere', self.campaign, sphere)

    def test_ability_gates_resolve_to_generated_special_abilities(self):
        for key, tags in self.rows.items():
            for tag in tags:
                if tag.startswith('ABILITY:Special Ability|AUTOMATIC|'):
                    names = tag.split('|')[2].split('|')
                    for name in (n for n in names if n):
                        self.assertIn(name, self.rows, f'{key} -> {name}')

    def test_active_requires_its_specialization(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            active = self.rows['Active Sphere Specialization (' + sphere + ')']
            self.assertTrue(any(tag.startswith('PREMULT:1,')
                                and 'Sphere Specialization (' + sphere + ')]' in tag
                                for tag in active), sphere)
            self.assertIn('COST:2', active)

    def test_technomancy_heading_is_normalized(self):
        self.assertIn('Sphere Specialization (Technomancy)', self.rows)
        for key in self.rows:
            self.assertNotIn('Incanter Sphere Specialization:', key)

    def test_every_ability_has_a_level_gate(self):
        for sphere, _row in sphere_sections():
            if sphere in EXISTING:
                continue
            active = self.rows['Active Sphere Specialization (' + sphere + ')']
            gates = [tag for tag in active if tag.startswith('ABILITY:Special Ability')]
            self.assertTrue(gates, sphere)
            for tag in gates:
                self.assertRegex(tag, r'\|PREVARGTEQ:SPHERES_INCANTER_LEVEL,\d+$')


if __name__ == '__main__':
    unittest.main()
