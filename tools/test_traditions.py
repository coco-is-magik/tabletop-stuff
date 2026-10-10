"""Regression checks for weighted tradition choices using existing PCGen pools."""
import re
import unittest

from spheres import DATA, records
from spheres_traditions import (build, OUTPUT, sections, LEGACY, DEFERRED, CONFLICTS,
                                build_sphere_drawbacks, sphere_drawbacks, sphere_drawback_key,
                                strip_tags, SPHERE_DRAW_OUTPUT, SPHERE_DRAW_CATEGORIES,
                                SPHERE_DRAW_DEFERRED, SPHERE_DRAW_RESTRICTIONS, oaths, oath_rows,
                                OATHS_CORE, OATH_DRAW, OATH_ADJUDICATION, OATH_CATEGORIES, oath_key)


class TraditionTests(unittest.TestCase):
    def test_drawback_pool_is_not_capped_below_the_published_total(self):
        # The source caps the spell-point benefit at five drawbacks, not the number of
        # drawbacks a caster may take, so the selection pool must cover the total cost.
        costs = 0
        for path in (DATA / 'spheres_traditions.lst', OUTPUT):
            for line in records(path):
                cells = line.split('\t')
                if 'CATEGORY:Custom Casting Drawback' not in cells:
                    continue
                cost = next((cell for cell in cells if cell.startswith('COST:')), None)
                if cost:
                    costs += int(cost.split(':')[1])
        row = next(line for line in records(DATA / 'spheres_traditions.lst')
                   if line.startswith('Custom Casting Tradition\t'))
        match = re.search(r'BONUS:ABILITYPOOL\|Custom Casting Drawback\|(\d+)', row)
        self.assertIsNotNone(match, 'drawback pool grant missing')
        self.assertGreaterEqual(int(match.group(1)), costs)

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


class SphereDrawbackTests(unittest.TestCase):
    """Sphere-specific drawbacks grant a talent in their own sphere."""

    @classmethod
    def setUpClass(cls):
        cls.generate, cls.categories, cls.restrictions = build_sphere_drawbacks()
        cls.rows = {}
        for line in cls.generate.splitlines():
            if '\t' in line:
                cells = line.split('\t')
                cls.rows[cells[0]] = cells[1:]
        cls.grouped = sphere_drawbacks()

    def test_generated_files_are_current(self):
        self.assertEqual(SPHERE_DRAW_OUTPUT.read_text(), self.generate)
        self.assertEqual(SPHERE_DRAW_CATEGORIES.read_text(), self.categories)
        self.assertEqual(SPHERE_DRAW_RESTRICTIONS.read_text(), self.restrictions)

    def test_every_drawback_requires_its_sphere_and_grants_one_talent(self):
        for sphere, entries in self.grouped.items():
            if sphere == 'Universal':
                continue
            for row in entries:
                if strip_tags(row['heading']) in SPHERE_DRAW_DEFERRED:
                    continue
                tags = self.rows[sphere_drawback_key(row['heading'])]
                self.assertIn(f'PREABILITY:1,CATEGORY=Spheres Magic Talent,{sphere} Sphere', tags)
                # Either a free talent from the sphere, or - when the source pins the
                # bonus talent - that exact talent granted automatically.
                paddings = [tag for tag in tags if tag.startswith('BONUS:ABILITYPOOL|')]
                pinned = [tag for tag in tags if tag.startswith('ABILITY:Spheres Magic Talent')]
                self.assertEqual(len(paddings) + len(pinned), 1, sphere)
                if paddings:
                    self.assertEqual(paddings,
                                     [f'BONUS:ABILITYPOOL|Custom {sphere} Drawback Talent|1'])
                else:
                    self.assertTrue(pinned[0].startswith(
                        f'ABILITY:Spheres Magic Talent|AUTOMATIC|{sphere} - '), pinned)
                self.assertFalse(any(tag.startswith('DEFINE:') for tag in tags))

    def test_forbidden_talents_resolve_to_real_records(self):
        campaign = set()
        for path in sorted(DATA.glob('*.lst')):
            campaign.update(line.split('\t')[0] for line in records(path))
        self.assertTrue(self.restrictions)
        for line in self.restrictions.splitlines():
            if not line or line.startswith('#'):
                continue
            key = line.split('\t')[0]
            self.assertTrue(key.endswith('.MOD'), key)
            self.assertTrue(key.startswith('CATEGORY=Spheres Magic Talent|'), key)
            target = key.removesuffix('.MOD').split('|', 1)[1]
            self.assertIn(target, campaign, key)
            blockers = [tag for tag in line.split('\t') if tag.startswith('!PREABILITY:')]
            self.assertEqual(len(blockers), 1, key)
            self.assertIn(blockers[0].split(',')[-1], self.rows, key)

    def test_pinned_bonus_talents_resolve_to_that_sphere(self):
        campaign = set()
        for path in sorted(DATA.glob('*.lst')):
            campaign.update(line.split('\t')[0] for line in records(path))
        for key, tags in self.rows.items():
            sphere = next(tag.split(',')[-1].removesuffix(' Sphere')
                          for tag in tags
                          if tag.startswith('PREABILITY:1,CATEGORY=Spheres Magic Talent,'))
            for tag in tags:
                if not tag.startswith('ABILITY:Spheres Magic Talent|AUTOMATIC|'):
                    continue
                talent = tag.rsplit('|', 1)[-1]
                self.assertIn(talent, campaign, key)
                self.assertEqual(talent.split(' - ')[0], sphere, key)

    def test_drawback_talent_pools_are_sphere_restricted(self):
        for sphere in self.grouped:
            if sphere == 'Universal':
                continue
            self.assertIn(f'ABILITYCATEGORY:Custom {sphere} Drawback Talent\t'
                          f'CATEGORY:Spheres Magic Talent\tTYPE:SpheresBasicTalent.{sphere}',
                          self.categories)

    def test_deferred_drawbacks_are_not_silently_approximated(self):
        for name in SPHERE_DRAW_DEFERRED:
            self.assertNotIn(sphere_drawback_key(name), self.rows)

    def test_incompatibilities_resolve_to_generated_records(self):
        for key, tags in self.rows.items():
            for tag in tags:
                if tag.startswith('!PREABILITY:1,CATEGORY=Custom Sphere Drawback,'):
                    self.assertIn(tag.split(',')[-1], self.rows, key)

    def test_incompatibilities_are_symmetric(self):
        blocking = {key: {tag.split(',')[-1] for tag in tags
                          if tag.startswith('!PREABILITY:1,CATEGORY=Custom Sphere Drawback,')}
                    for key, tags in self.rows.items()}
        for key, targets in blocking.items():
            for target in targets:
                self.assertIn(key, blocking.get(target, set()), f'{key} <-> {target}')

    def test_unresolvable_incompatibility_text_is_not_encoded(self):
        # "Any Conjuration drawback that affects the summon ability" is prose, not a key.
        for tags in self.rows.values():
            for tag in tags:
                if tag.startswith('!PREABILITY:'):
                    self.assertNotIn('Any Conjuration drawback', tag)


    def test_bound_creature_grants_the_conjuration_sphere(self):
        row = next(row for row in build().splitlines()
                   if row.startswith('Tradition - Bound Creature\t'))
        self.assertIn('ABILITY:Spheres Magic Talent|AUTOMATIC|Conjuration Sphere', row.split('\t'))
        self.assertIn('BONUS:VAR|SPHERES_TRADITION_BOONS|1', row.split('\t'))

    def test_wild_will_is_repeatable_with_a_chosen_environment(self):
        row = next(row for row in build().splitlines()
                   if row.startswith('Tradition - Wild Will\t'))
        for tag in ('MULT:YES', 'STACK:YES',
                    'CHOOSE:USERINPUT|1|TITLE=Favored terrain environment'):
            self.assertIn(tag, row.split('\t'))

    def test_all_published_boons_are_represented(self):
        generated = build()
        legacy = {row.split('\t')[0] for row in records(DATA / 'spheres_traditions.lst')}
        for key in sections('Boons'):
            self.assertTrue('Tradition - ' + key + '\t' in generated
                            or 'Tradition - ' + key in legacy, key)

    def test_oathbound_casting_publishes_its_wrapper_and_every_named_oath(self):
        self.assertNotIn('Oathbound Casting', DEFERRED)
        output = build()
        self.assertIn(OATH_DRAW + '\tCATEGORY:Custom Casting Drawback\tCOST:0', output)
        pinned = oaths()
        self.assertTrue(set(OATHS_CORE).issubset(pinned))
        self.assertTrue(len(pinned) > len(OATHS_CORE),
                        "the source publishes far more Oaths than the drawback names")
        for oath in pinned:
            self.assertIn('Tradition - Oathbound Casting: ' + oath + ' (', output)

    def test_only_the_named_oaths_are_free_and_the_rest_need_gm_approval(self):
        rows = {row.split('\t')[0]: row.split('\t')[1:]
                for row in build().splitlines()
                if row.startswith('Tradition - Oathbound Casting: ')}
        gate = 'PREABILITY:1,CATEGORY=Spheres Oath Adjudication,'
        approvals = {line.split('\t')[0] for line in records(OATH_ADJUDICATION)}
        for oath, (points, _row) in oaths().items():
            tags = rows[oath_key(oath, points)]
            if oath in OATHS_CORE:
                self.assertNotIn(gate, ' '.join(tags), oath)
                continue
            approval = [tag for tag in tags if tag.startswith(gate)]
            self.assertEqual(len(approval), 1, oath)
            self.assertIn(approval[0].split(gate)[1], approvals, oath)

    def test_oath_names_show_their_point_values(self):
        rows = {row.split('\t')[0]: row.split('\t')[1:]
                for row in build().splitlines()
                if row.startswith('Tradition - Oathbound Casting: ')}
        for oath, (points, _row) in oaths().items():
            unit = 'drawback point' if points == 1 else 'drawback points'
            tags = rows[oath_key(oath, points)]
            # The value is in the name and at the front of the description.
            self.assertIn(oath_key(oath, points), rows)
            desc = next(tag for tag in tags if tag.startswith('DESC:'))
            self.assertTrue(desc.startswith(f'DESC:Grants {points} {unit} ('), desc[:80])

    def test_oath_approval_category_is_declared(self):
        self.assertIn('ABILITYCATEGORY:Spheres Oath Adjudication',
                      OATH_CATEGORIES.read_text())

    def test_each_oath_grants_its_published_point_value(self):
        pinned = oaths()
        rows = {row.split('\t')[0]: row.split('\t')[1:]
                for row in build().splitlines()
                if row.startswith('Tradition - Oathbound Casting: ')}
        for oath, (points, _row) in pinned.items():
            tags = rows[oath_key(oath, points)]
            # An Oath counts as that many drawbacks: it grants points, never costs them.
            self.assertIn('COST:0', tags, oath)
            self.assertIn('BONUS:ABILITYPOOL|Custom Casting Boon|' + str(points), tags, oath)
            self.assertIn('BONUS:VAR|SPHERES_TRADITION_DRAWBACKS|' + str(points), tags, oath)
        # The published values differ, so the differentiation is real.
        self.assertEqual({oaths()[name][0] for name in OATHS_CORE}, {1, 2, 4})

    def test_oaths_are_mutually_exclusive(self):
        rows = {row.split('\t')[0]: row.split('\t')[1:]
                for row in build().splitlines()
                if row.startswith('Tradition - Oathbound Casting: ')}
        self.assertEqual(len(rows), len(oaths()))
        for oath in rows:
            for other in rows:
                if other == oath:
                    continue
                self.assertIn('!PREABILITY:1,CATEGORY=Custom Casting Drawback,' + other,
                              rows[oath], oath)

    def test_oaths_require_the_oathbound_drawback(self):
        for tags in oath_rows():
            self.assertIn('PREABILITY:1,CATEGORY=Custom Casting Drawback,' + OATH_DRAW,
                          tags.split('\t'))


if __name__ == '__main__':
    unittest.main()