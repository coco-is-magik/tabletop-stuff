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

    def test_repeat_counters_owned_by_base_sphere(self):
        for filename, contents in self.files.items():
            if not filename.startswith(('spheres_power_', 'spheres_might_')):
                continue
            lines = [line for line in contents.splitlines() if not line.startswith('#')]
            for line in lines:
                for tag in line.split('\t'):
                    if tag.startswith('BONUS:VAR|') and tag.split('|')[1].endswith('_COUNT'):
                        definition = 'DEFINE:' + tag.split('|')[1] + '|0'
                        self.assertNotIn(definition, line)
                        self.assertIn(definition, lines[0], filename)

    def test_repeat_threshold_does_not_override_unlimited_selection(self):
        row = next(r for r in self.rows if r['slug'] == 'pilot')
        talent = next(t for t in row['talents'] if t['name'] == 'Companion Vessel')
        self.assertEqual(repeat_limit(talent), 99)
        self.assertEqual(repeat_limit({'text': 'You may take this talent a second time.'}), 2)
        self.assertEqual(repeat_limit({'text': 'You may select this talent up to 2 times.'}), 2)
        self.assertEqual(repeat_limit({'text': 'You may take this talent more than once.'}), 99)
        line = next(line for line in self.files['spheres_might_pilot.lst'].splitlines()
                    if line.startswith('Pilot - Companion Vessel\t'))
        self.assertNotIn('PREVARLT:SPHERES_PILOT_COMPANIONVESSEL_COUNT', line)

    def test_extendo_second_selection_requires_training(self):
        line = next(line for line in self.files['spheres_might_tech.lst'].splitlines()
                    if line.startswith('Tech - Extendo Appendage\t'))
        self.assertIn('PREMULT:1,[PREVARLT:SPHERES_TECH_EXTENDOAPPENDAGE_COUNT,1],'
                      '[PRESKILL:1,Craft (Mechanical)=10]', line)
        self.assertIn('PREVARLT:SPHERES_TECH_EXTENDOAPPENDAGE_COUNT,2', line)
        line = next(line for line in self.files['spheres_might_tech.lst'].splitlines()
                    if line.startswith('Tech - Range Amplifier\t'))
        self.assertIn('PREVARLT:SPHERES_TECH_RANGEAMPLIFIER_COUNT,1+floor(SPHERES_TECH_RANKS/5)', line)
        self.assertIn('STACK:YES', line)

    def test_drone_and_ai_share_repeat_limit(self):
        tech = self.files['spheres_might_tech.lst']
        for name in ('Drone', 'Artificial Intelligence'):
            line = next(line for line in tech.splitlines() if line.startswith('Tech - ' + name + '\t'))
            self.assertIn('PREVARLT:SPHERES_TECH_DRONE_AI_COUNT,4', line)
            self.assertIn('BONUS:VAR|SPHERES_TECH_DRONE_AI_COUNT|1', line)
            self.assertIn('STACK:YES', line)
            self.assertNotIn('DEFINE:SPHERES_TECH_DRONE_AI_COUNT', line)

    def test_invigorate_grants_are_separate_from_cure(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_life.lst'].splitlines()}
        self.assertIn('BONUS:VAR|SPHERES_LIFE_INVIGORATE_HP|max(1,SPHERES_CL_LIFE)', records['Life Sphere'])
        self.assertIn('BONUS:VAR|SPHERES_LIFE_INVIGORATE_HP|SPHERES_CL_LIFE', records['Life - Deeper Healing'])
        greater = records['Life - Greater Invigorate']
        self.assertIn('BONUS:VAR|SPHERES_LIFE_INVIGORATE_HP|SPHERES_CASTING_ABILITY', greater)
        self.assertIn('BONUS:VAR|SPHERES_LIFE_INVIGORATE_HOURS|SPHERES_CL_LIFE-1', greater)
        self.assertNotIn('BONUS:VAR|SPHERES_LIFE_CURE', greater)

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
        self.assertEqual(categories.count('ABILITYCATEGORY:'), len(PACKAGES) + 6)
        stance_pool = next(line for line in categories.splitlines()
                           if line.startswith('ABILITYCATEGORY:Spheres Versatile Fighter Stance\t'))
        self.assertIn('POOL:0', stance_pool)
        self.assertIn('EDITPOOL:NO', stance_pool)
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

    def test_technical_skill_grants_and_resources(self):
        for slug in ('tech', 'tinker'):
            self.assertIn('BONUS:SKILLRANK|Craft (Mechanical)|min(TL,5*SPHERES_' + slug.upper() + '_TALENTS)',
                          self.files['spheres_might_' + slug + '.lst'])
        tech = self.files['spheres_might_tech.lst']
        self.assertIn('DEFINE:SPHERES_DC_TECH|10+floor(skillinfo("TOTALRANK","Craft (Mechanical)")/2)', tech)
        self.assertIn('DEFINE:SPHERES_TECH_CHARGE_CAPACITY|max(4,SPHERES_TECH_RANKS+SPHERES_TECH_TALENTS)', tech)
        self.assertIn('DEFINE:SPHERES_TECH_RECHARGE|1+floor(SPHERES_TECH_RANKS/2)', tech)
        self.assertIn('BONUS:SKILLRANK|Profession (Pilot)|min(TL,5*SPHERES_ATHLETICS_TALENTS)',
                      self.files['spheres_might_athletics.lst'])
        skills = (DATA / 'spheres_skills.lst').read_text()
        self.assertIn('Craft (Mechanical)\tKEYSTAT:INT', skills)
        self.assertIn('Profession (Pilot)\tKEYSTAT:WIS', skills)
        self.assertIn('SKILL:spheres_skills.lst', (DATA / 'spheres.pcc').read_text())

    def test_skill_based_dcs_and_free_gadgets(self):
        for slug, skill in (('trap', 'Craft (Traps)'),):
            self.assertIn('DEFINE:SPHERES_DC_' + slug.upper() + '|10+floor(skillinfo("TOTALRANK","' + skill + '")/2)',
                          self.files['spheres_might_' + slug + '.lst'])
        tech = self.files['spheres_might_tech.lst']
        alchemy = self.files['spheres_might_alchemy.lst']
        self.assertIn('DEFINE:SPHERES_DC_ALCHEMY|10+floor(SPHERES_ALCHEMY_RANKS/2)', alchemy)
        self.assertIn('BONUS:VAR|SPHERES_ALCHEMY_RANKS|skillinfo("TOTALRANK","Heal")|PREABILITY:', alchemy)
        self.assertIn('BONUS:VAR|SPHERES_ALCHEMY_RANKS|skillinfo("TOTALRANK","Craft (Alchemy)")|!PREABILITY:', alchemy)
        salve = next(row for row in alchemy.splitlines() if row.startswith('Alchemy - Salve\t'))
        self.assertIn('.AlchemyFormula', salve)
        self.assertIn('BONUS:ABILITYPOOL|Spheres Alchemy Bonus Formula|1', self.files['spheres_catalog_packages.lst'])
        self.assertIn('BONUS:VAR|SPHERES_ALCHEMY_FORMULAE|1', salve)
        poison = next(row for row in alchemy.splitlines() if row.startswith('Alchemy - Witchbane\t'))
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Alchemy Package,Alchemy Package - Poison', poison)
        self.assertNotIn('.AlchemyFormula', poison)
        self.assertIn('DEFINE:SPHERES_ALCHEMY_BATCH|1+floor(SPHERES_ALCHEMY_RANKS/4)', alchemy)
        self.assertIn('BONUS:ABILITYPOOL|Spheres Tech Bonus Gadget|1', tech)
        for line in tech.splitlines():
            if line.startswith('Tech - Battery\t'):
                self.assertIn('TYPE:SpheresBasicTalent.Tech.TechGadget\t', line)
            if line.startswith('Tech - Efficient Drones\t'):
                self.assertNotIn('TechGadget', line)
        self.assertIn('TYPE:TechGadget\t', self.files['spheres_categories_catalog.lst'])
        extra = next(line for line in tech.splitlines() if line.startswith('Tech - Extra Gadgets\t'))
        self.assertIn('STACK:YES', extra)
        self.assertIn('BONUS:VAR|SPHERES_TECH_CHARGE_CAPACITY|1', extra)
        self.assertIn('BONUS:VAR|SPHERES_TECH_PREPARED_GADGETS|2', extra)
        self.assertNotIn('BONUS:VAR|SPHERES_TECH_GADGET_TALENTS|1', extra)

    def test_craftsman_single_craft_choice(self):
        line = next(line for line in self.files['spheres_might_equipment-sphere.lst'].splitlines()
                    if line.startswith('Equipment - Craftsman\t'))
        self.assertIn('CHOOSE:NUMCHOICES=1|SKILL|TYPE=Craft', line)
        self.assertIn('BONUS:SKILLRANK|LIST|TL|TYPE=SpheresTraining', line)
        self.assertIn('STACK:NO', line)
        self.assertNotIn('CHOOSE:NOCHOICE', line)

    def test_secondary_skill_training(self):
        for slug, talent, skill, variable in (
                ('fencing', 'Fencing - Read Foe', 'Sense Motive', 'FENCING'),
                ('leadership', 'Leadership - Military Training', 'Profession (Soldier)', 'LEADERSHIP')):
            lines = self.files['spheres_might_' + slug + '.lst'].splitlines()
            trained = next(line for line in lines if line.startswith(talent + '\t'))
            grant = 'BONUS:SKILLRANK|' + skill + '|min(TL,5*SPHERES_' + variable + '_TALENTS)|TYPE=SpheresTraining'
            self.assertIn(grant, trained)
            self.assertEqual(sum(grant in line for line in lines), 1)
            self.assertIn('PREABILITY:1,CATEGORY=Spheres Combat Talent,', trained)

    def test_diplomacy_overlap_is_single_conditional_bonus(self):
        leadership = self.files['spheres_might_leadership.lst']
        warleader = self.files['spheres_might_warleader-sphere.lst']
        bonus = 'BONUS:SKILL|Diplomacy|floor(SPHERES_BAB_LEADERSHIP/2)|TYPE=Competence|PREABILITY:1,CATEGORY=Spheres Combat Talent,Warleader Sphere'
        self.assertEqual(leadership.count(bonus), 1)
        self.assertNotIn('BONUS:SKILL|Diplomacy|', warleader)
        for content in (leadership, warleader):
            self.assertIn('|TYPE=SpheresTraining', content.splitlines()[2])


if __name__ == '__main__':
    unittest.main()