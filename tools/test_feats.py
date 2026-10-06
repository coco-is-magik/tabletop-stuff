"""Regression tests for feat source boundaries and fail-closed qualification."""
import json
import unittest
from unittest.mock import patch
from spheres_feats import build, Prerequisites, split_clauses, split_alternatives, DATA


class FeatTests(unittest.TestCase):
    def test_precogniscent_feats_use_active_senses_and_hit_dice(self):
        rows = {row['name']: row for row in json.loads(build()['feat-catalog.json'])}
        for name, kind, divisor, bonus_type in (
                ('Protection', 'COMBAT|AC', 5, 'Insight'),
                ('Resistance', 'SAVE|ALL', 4, 'Resistance'),
                ('Smite', 'COMBAT|TOHIT,DAMAGE', 5, 'Insight')):
            row = rows['Precogniscent ' + name]
            self.assertFalse(row['unresolved_prerequisites'])
            self.assertIn('DEFINE:SPHERES_ACTIVE_DIVINATION_SENSES|0', row['mechanics'])
            self.assertIn('BONUS:' + kind + '|min(SPHERES_ACTIVE_DIVINATION_SENSES,1+floor(TL/'
                          + str(divisor) + '))|TYPE=' + bonus_type, row['mechanics'])

    def test_divination_base_sense_is_not_a_purchased_sense_talent(self):
        parser = Prerequisites(json.loads(build()['feat-catalog.json']))
        base = 'PREABILITY:1,CATEGORY=Spheres Magic Talent,Divination Sphere'
        self.assertEqual(parser.compile('Prerequisites: Divination sphere (one or more (sense) talents or abilities).'),
                         ([base], []))
        tags, unresolved = parser.compile('Prerequisites: Divination sphere (any (sense) talent).')
        self.assertFalse(unresolved)
        self.assertEqual(tags[0], base)
        self.assertIn('Divination - Prescience', tags[1])
        self.assertNotIn('Divination Sphere', tags[1])
        self.assertNotIn('Divination - Expanded Divination', tags[1])

    def test_mana_amp_requires_a_purchased_descriptor_member(self):
        rows = json.loads(build()['feat-catalog.json'])
        parser = Prerequisites(rows)
        for wording in ('any', 'at least one'):
            tags, unresolved = parser.compile('Prerequisites: Mana sphere (' + wording + ' (amp) talent).')
            self.assertFalse(unresolved)
            self.assertIn('Mana - Arcanodynamics', tags[-1])
            self.assertIn('Mana - Heightened Magic', tags[-1])
            self.assertNotIn('Mana - Bulwark', tags[-1])
            self.assertNotIn('Mana - Defensive Bond', tags[-1])
            self.assertNotIn('Mana Sphere', tags[-1])
        self.assertTrue(parser.compile('Prerequisites: Mana sphere (any (unknown) talent).')[1])

    def test_sacrosanct_firewall_uses_base_hallow_but_requires_technomancy(self):
        rows = json.loads(build()['feat-catalog.json'])
        row = next(row for row in rows if row['name'] == 'Sacrosanct Firewall')
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertEqual(row['prerequisites'], [
            'PREABILITY:1,CATEGORY=Spheres Magic Talent,Fate Sphere',
            'PREABILITY:1,CATEGORY=Spheres Magic Talent,Technomancy Sphere'])
        parser = Prerequisites(rows)
        self.assertTrue(parser.compile('Prerequisites: Fate sphere (Unknown (word)).')[1])

    def test_shared_sphere_suffix_preserves_alternatives(self):
        parser = Prerequisites(json.loads(build()['feat-catalog.json']))
        tags, unresolved = parser.compile('Prerequisites: Death or Fate sphere')
        self.assertFalse(unresolved)
        self.assertEqual(tags, ['PREMULT:1,[PREABILITY:1,CATEGORY=Spheres Magic Talent,Death Sphere],'
                                '[PREABILITY:1,CATEGORY=Spheres Magic Talent,Fate Sphere]'])
        self.assertTrue(parser.compile('Prerequisites: Unknown or Fate sphere')[1])
        self.assertTrue(parser.compile('Prerequisites: Death or Unknown sphere')[1])

    def test_sanctified_vigilance_requires_a_rally_not_a_totem(self):
        rows = json.loads(build()['feat-catalog.json'])
        row = next(row for row in rows if row['name'] == 'Sanctified Vigilance')
        self.assertFalse(row['unresolved_prerequisites'])
        family = row['prerequisites'][-1]
        self.assertIn('War - Absorb', family)
        self.assertNotIn('War Sphere', family)
        self.assertNotIn('War - Totem Of War', family)

    def test_object_familiar_uses_existing_familiar_advancement(self):
        rows = json.loads(build()['feat-catalog.json'])
        parser = Prerequisites(rows)
        self.assertEqual(parser.compile('Prerequisites: ability to acquire a familiar.'),
                         (['PREVARGTEQ:FamiliarMasterLVL,1'], []))
        row = next(row for row in rows if row['name'] == 'Object Familiar')
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Enhancement - Animate Object', row['prerequisites'])

    def test_base_enhance_ability_is_distinct_from_purchased_talent(self):
        rows = json.loads(build()['feat-catalog.json'])
        parser = Prerequisites(rows)
        tags, unresolved = parser.compile('Prerequisites: Alteration sphere, Enhancement sphere (any (enhance) ability).')
        self.assertEqual(unresolved, [])
        self.assertEqual(tags, [
            'PREABILITY:1,CATEGORY=Spheres Magic Talent,Alteration Sphere',
            'PREABILITY:1,CATEGORY=Spheres Magic Talent,Enhancement Sphere'])
        self.assertTrue(parser.compile('Prerequisites: Enhancement sphere (any unknown ability).')[1])

    def test_solid_illusions_requires_two_illusionary_touch_selections(self):
        rows = json.loads(build()['feat-catalog.json'])
        parser = Prerequisites(rows)
        tags, unresolved = parser.compile('Prerequisites: Enhancement sphere, Illusion sphere (Illusionary Touch (sensory, touch) x2).')
        self.assertEqual(unresolved, [])
        self.assertEqual(tags[-1], 'PREVARGTEQ:SPHERES_ILLUSION_ILLUSIONARYTOUCH_COUNT,2')
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Illusion Sphere', tags)
        self.assertTrue(parser.compile('Prerequisites: Illusion sphere (Illusionary Touch (sensory, touch) x3).')[1])

    def test_careful_magic_bonus_is_not_general_magic_defense(self):
        rows = {row['name']: row for row in json.loads(build()['feat-catalog.json'])}
        self.assertEqual(rows['Careful Magic']['mechanics'], [
            'DEFINE:SPHERES_CAREFUL_MAGIC_DISPEL_MSD_BONUS|max(1,SPHERES_CASTING_ABILITY)'])
        self.assertIn('PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Extended Casting', rows['Careful Magic']['prerequisites'])

    def test_exceptional_ally_requires_an_actual_enhance_talent(self):
        rows = json.loads(build()['feat-catalog.json'])
        parser = Prerequisites(rows)
        tags, unresolved = parser.compile('Prerequisites: Conjuration sphere, Enhancement sphere (at least one (enhance) talent).')
        self.assertEqual(unresolved, [])
        self.assertEqual(len(tags), 3)
        self.assertIn('Enhancement - Animate Object', tags[-1])
        self.assertIn('Enhancement - Lighten', tags[-1])
        self.assertNotIn('Enhancement Sphere', tags[-1])
        self.assertNotIn('Enhancement - Deep Enhancement', tags[-1])
        self.assertNotIn('Enhancement - Ranged Enhancement', tags[-1])
        self.assertTrue(parser.compile('Prerequisites: Enhancement sphere (at least two (enhance) talents).')[1])

    def test_animation_feats_require_animation_and_do_not_change_caster_hp(self):
        rows = {row['name']: row for row in json.loads(build()['feat-catalog.json'])}
        for name in ('Complex Animations', 'Durable Objects'):
            self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Enhancement - Animate Object', rows[name]['prerequisites'])
            self.assertTrue(rows[name]['mechanics'])
            self.assertFalse(any(tag.startswith(('BONUS:HP', 'BONUS:COMBAT', 'SIZE:')) for tag in rows[name]['mechanics']))

    def test_analyze_caster_bonus_is_limited_to_detect_spellcaster(self):
        rows = {row['name']: row for row in json.loads(build()['feat-catalog.json'])}
        self.assertEqual(rows['Analyze Caster']['mechanics'], [
            'BONUS:SITUATION|Spellcraft=Determine casting tradition with Detect Spellcaster|5'])

    def test_vigilant_skeptic_bonuses_remain_glamer_specific(self):
        rows = {row['name']: row for row in json.loads(build()['feat-catalog.json'])}
        tags = rows['Vigilant Skeptic']['mechanics']
        for skill in ('Perception', 'Sense Motive'):
            self.assertIn(f'BONUS:SITUATION|{skill}=Target benefiting from a glamer|floor(TL/2)', tags)
        self.assertIn('DEFINE:SPHERES_SKEPTIC_FIGMENT_RANGE|5+5*floor(skillinfo("TOTALRANK","Perception")/2)', tags)
        self.assertFalse(any(tag.startswith('BONUS:SKILL|') for tag in tags))

    def test_reviewed_feat_equivalences_do_not_grant_imitated_effects(self):
        rows = {row['name']: row for row in json.loads(build()['feat-catalog.json'])}
        self.assertEqual(rows['Liberating Triumph']['mechanics'], ['SERVESAS:ABILITY=FEAT|Great Fortitude|Lightning Reflexes|Iron Will'])
        self.assertEqual(rows['Combatant Caster']['mechanics'], ['SERVESAS:ABILITY=FEAT|Combat Casting'])

    def test_surgeon_bonus_is_situational_and_rank_scaled(self):
        rows = json.loads(build()['feat-catalog.json'])
        surgeon = next(row for row in rows if row['name'] == 'Surgeon’s Trade Secrets')
        self.assertIn('BONUS:SITUATION|Heal=Target under your blood control|if(skillinfo("TOTALRANK","Heal")>=10,6,3)', surgeon['mechanics'])
        self.assertFalse(any(tag.startswith('BONUS:SKILL|') for tag in surgeon['mechanics']))
        self.assertFalse(any(tag.startswith('SERVESAS:') for tag in surgeon['mechanics']))
        self.assertFalse(any(line.startswith('Skill Focus (Heal)\t')
                             for line in build()['spheres_feat_catalog.lst'].splitlines()))
        parser = Prerequisites(rows)
        tags, unresolved = parser.compile('Prerequisites: Skill Focus (Heal).')
        self.assertEqual(unresolved, [])
        self.assertEqual(tags, ['PREMULT:1,[PREFEAT:1,Skill Focus (Heal)],[PREFEAT:1,Surgeon’s Trade Secrets]'])

    def test_terrain_defiler_uses_reviewed_cataclysm_revision(self):
        rows = json.loads(build()['feat-catalog.json'])
        matches = [row for row in rows if row['name'] == 'Terrain Defiler']
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['types'], ['Defiler', 'Drawback'])
        self.assertIn('Four Defiler Feats:', matches[0]['text'])
        self.assertIn('BONUS:VAR|SPHERES_DEFILER_FEAT_COUNT|1', matches[0]['mechanics'])

    def test_defiler_necrosis_overlap_is_counted_once(self):
        rows = json.loads(build()['feat-catalog.json'])
        both = next(row for row in rows if row['name'] == 'Inhuman Defiler')
        self.assertIn('Defiler', both['types'])
        self.assertEqual(both['mechanics'].count('BONUS:VAR|SPHERES_NECROSIS_FEAT_COUNT|1'), 1)
        self.assertEqual(both['mechanics'].count('BONUS:VAR|SPHERES_DEFILER_FEAT_COUNT|1'), 1)
        self.assertFalse(any('COUNT|1|PREFEAT:' in tag for tag in both['mechanics']))
        distant = next(row for row in rows if row['name'] == 'Distant Defiling')
        self.assertIn('BONUS:VAR|SPHERES_NECROSIS_FEAT_COUNT|1|PREFEAT:1,Inhuman Defiler', distant['mechanics'])

    def test_scholar_divine_bonus_does_not_increase_general_caster_level(self):
        tags = json.loads((DATA / 'feat-mechanics.json').read_text())['Scholar Of Past And Future']['tags']
        self.assertEqual(tags[0], 'BONUS:SKILL|Knowledge (History)|if(skillinfo("TOTALRANK","Knowledge (History)")>=10,4,2)')
        self.assertTrue(tags[1].startswith('DEFINE:SPHERES_SCHOLAR_DIVINE_CL_BONUS|max(0,min('))
        self.assertFalse(any(tag.startswith('BONUS:VAR|SPHERES_CL_') for tag in tags))

    def test_necrosis_count_and_cold_heart_threshold(self):
        rows = json.loads(build()['feat-catalog.json'])
        necrosis = [row for row in rows if 'Necrosis' in row['types']]
        self.assertEqual(len(necrosis), 11)
        for row in necrosis:
            self.assertEqual(row['mechanics'].count('BONUS:VAR|SPHERES_NECROSIS_FEAT_COUNT|1'), 1)
        cold = next(row for row in necrosis if row['name'] == 'Cold Heart')
        self.assertIn('BONUS:VAR|SPHERES_SPELL_POINTS|1', cold['mechanics'])
        self.assertIn('BONUS:VAR|ColdResistanceBonus,ElectricityResistanceBonus|10|TYPE=Resistance|PREVARGTEQ:SPHERES_NECROSIS_FEAT_COUNT,4', cold['mechanics'])
        heart = next(row for row in necrosis if row['name'] == 'Necrotic Heart')
        self.assertNotIn('BONUS:VAR|SPHERES_SPELL_POINTS|1', heart['mechanics'])
        flesh = next(row for row in necrosis if row['name'] == 'Deadened Flesh')
        self.assertIn('DR:floor(SPHERES_NECROSIS_FEAT_COUNT*0.5)/-|PREVARGTEQ:SPHERES_NECROSIS_FEAT_COUNT,4', flesh['mechanics'])
        for name in ('Banshee’s Sotto Voce', 'Between Two Worlds', 'Deathknight’s Purchase',
                     'Hemomancy', 'Wandering Spirit'):
            row = next(row for row in necrosis if row['name'] == name)
            self.assertEqual(row['mechanics'].count('BONUS:VAR|SPHERES_SPELL_POINTS|1'), 1)
        blood = next(row for row in necrosis if row['name'] == 'Hemomancy')
        self.assertFalse(any(tag.startswith('VISION:') for tag in blood['mechanics']))

    def test_resistant_veins_is_natural_armor_not_an_enhancement(self):
        overrides = json.loads((DATA / 'feat-mechanics.json').read_text())
        self.assertEqual(overrides['Resistant Veins']['tags'],
                         ['BONUS:COMBAT|AC|1+floor(SPHERES_MAGIC_SKILL_BONUS/5)|TYPE=NaturalArmor'])
        self.assertEqual(Prerequisites([]).clause('Anemic'),
                         ['PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Anemic'])

    def test_channel_resistance_grants_personal_defense(self):
        overrides = json.loads((DATA / 'feat-mechanics.json').read_text())
        tags = overrides['Channel Resistance']['tags']
        self.assertEqual(tags, ['ABILITY:Special Ability|AUTOMATIC|Channel Resistance',
                               'BONUS:VAR|ChannelResistance|2'])

    def test_reviewed_racial_type_or_subtype(self):
        parser = Prerequisites([])
        for name in ('Construct', 'Fey', 'Plant'):
            self.assertEqual(parser.clause(name + ' type or subtype'),
                             [f'PRERACE:1,RACETYPE={name},RACESUBTYPE={name}'])
        self.assertIsNone(parser.clause('invented type or subtype'))

    def test_racial_subtype_is_not_interchangeable_with_type(self):
        parser = Prerequisites([])
        for name in ('Construct', 'Plant'):
            self.assertEqual(parser.clause(name + ' subtype'),
                             [f'PRERACE:1,RACESUBTYPE={name}'])
        self.assertEqual(parser.clause('Outsider with the native subtype'),
                         ['PRERACE:2,RACETYPE=Outsider,RACESUBTYPE=Native'])
        tags, unresolved = parser.compile('Prerequisites: Outsider with the native subtype, alignment matching either an extraplanar ancestor or a patron.')
        self.assertEqual(tags, ['PRERACE:2,RACETYPE=Outsider,RACESUBTYPE=Native'])
        self.assertEqual(unresolved, ['alignment matching either an extraplanar ancestor or a patron'])
        self.assertIsNone(parser.clause('invented subtype'))

    def test_greater_created_retains_creation_time_review(self):
        rows = json.loads(build()['feat-catalog.json'])
        row = next(row for row in rows if row['name'] == 'Greater Created')
        self.assertIn('PRERACE:1,RACESUBTYPE=Construct', row['prerequisites'])
        self.assertIn('Only selectable at character creation', row['unresolved_prerequisites'])

    def test_core_combat_class_feature_predicates(self):
        parser = Prerequisites([])
        self.assertEqual(parser.clause('Favored Terrain class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,TYPE=FavoredTerrain'])
        self.assertEqual(parser.clause('improved evasion class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,Improved Evasion'])
        self.assertEqual(parser.clause('rage class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,TYPE=Rage'])
        self.assertEqual(parser.clause('favored enemy class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,Ranger ~ Favored Enemy,TYPE=FavoredEnemy'])
        self.assertIsNone(parser.clause('invented rage class feature'))
        self.assertEqual(parser.clause('Ki pool class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,TYPE=Ki Pool'])

    def test_wild_magic_scaling_and_spell_pool_alias(self):
        from spheres_wild_magic import feat_tags, COUNT
        parser = Prerequisites([])
        self.assertEqual(parser.clause('Spell point pool'), parser.clause('Spell pool'))
        self.assertEqual(parser.clause('Spell point pool or casting class feature'), [
            'PREMULT:1,[PREVARGTEQ:SPHERES_SPELL_POINTS,1],'
            '[PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core]'])
        self.assertIn(f'DEFINE:SPHERES_CAREFUL_CASTER_REDUCTION|min(50,25+5*({COUNT}-1))',
                      feat_tags('Careful Caster'))
        self.assertIn('BONUS:VAR|SPHERES_COUNTERSPELL_CHECK_BONUS|1', feat_tags('Chaotic Counter'))
        self.assertFalse(any('BONUS:VAR|SPHERES_MAGIC_SKILL_BONUS|' in tag
                             for tag in feat_tags('Chaotic Counter')))
        self.assertIn('DEFINE:SPHERES_SHIFT_COST_REDUCTION|if(TL>=10,2,1)', feat_tags('Shift Cost'))
        for name in ('Blood Dampening', 'Careful Caster', 'Chaotic Counter', 'Energy Shift',
                     'Heedless Metamagic', 'Inspired Surge', 'Manipulate Result',
                     'Overpower Resistance', 'Rhythmic Chaos', 'Risk Management',
                     'Shift Cost', 'Shift Effect', 'Spectacular Surge', 'War on Reality'):
            tags = feat_tags(name)
            self.assertEqual(tags.count(f'BONUS:VAR|{COUNT}|1'), 1)
            self.assertTrue(any(tag.startswith('DEFINE:SPHERES_') and not tag.startswith('DEFINE:' + COUNT)
                                for tag in tags), name)

    def test_performance_prerequisites_require_features_not_skill_ranks(self):
        self.assertEqual(self.parser.clause('bardic performance or raging song class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,TYPE=BardicPerformance,TYPE=SkaldRagingSong'])
        self.assertEqual(self.parser.clause('bardic performance class ability'),
                         ['PREABILITY:1,CATEGORY=Special Ability,TYPE=BardicPerformance'])
        for name in ('Battle Fanfare', 'Crescendo', 'Enchanting Performance', 'Lightshow', 'Thrum Of Rain', 'Tribal Rhythm', 'Hold the Note'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'], name)
        self.assertIsNone(self.parser.clause('bardic performance or invented song class feature'))

    def test_shadow_magic_capacity_counts_feats_not_shadow_points(self):
        tags = self.by_name['Shadow Magic']['mechanics']
        self.assertIn('DEFINE:SPHERES_SHADOW_MAGIC_TALENT_CAPACITY|1+floor(SPHERES_SURREAL_FEAT_COUNT/5)', tags)
        self.assertIn('DEFINE:SPHERES_SHADOW_MAGIC_EFFECT_CL|max(1,SPHERES_CL_ILLUSION-2+SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS)', tags)
        self.assertFalse(any(tag.startswith('BONUS:ABILITYPOOL') for tag in tags))
        for row in self.by_name.values():
            if 'Surreal' in row['types']:
                self.assertIn('BONUS:VAR|SPHERES_SURREAL_FEAT_COUNT|1', row['mechanics'])
        self.assertNotIn('BONUS:VAR|SPHERES_SURREAL_FEAT_COUNT|1', self.by_name['Extra Shadowstuff']['mechanics'])

    def test_shadow_shield_capacity_does_not_grant_permanent_defense(self):
        shield = self.by_name['Shadow Shield']['mechanics']
        improved = self.by_name['Improved Shadow Shield']['mechanics']
        self.assertIn('DEFINE:SPHERES_SHADOW_SHIELD_DICE|TL', shield)
        self.assertIn('DEFINE:SPHERES_SHADOW_SHIELD_REDUCTION|1+floor(TL/5)', shield)
        self.assertIn('BONUS:VAR|SPHERES_SHADOW_SHIELD_HP_BONUS|TL|PREFEAT:1,Shadow Shield', improved)
        self.assertFalse(any(tag.startswith(('DR:', 'BONUS:HP', 'BONUS:COMBAT')) for tag in shield + improved))

    def test_create_reality_requires_the_class_feature(self):
        self.assertEqual(self.parser.clause('create reality class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresCreateReality'])
        self.assertFalse(self.by_name['Emulation Expert']['unresolved_prerequisites'])
        gate = ' '.join(self.by_name['Emulation Expert']['prerequisites'])
        self.assertIn('PREFEAT:1,Shadow Magic', gate)
        self.assertIn('TYPE=SpheresCreateReality', gate)

    def test_shadow_pool_accepts_class_or_surreal_feat_sources(self):
        self.assertEqual(self.parser.clause('shadow pool'), [
            'PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability,Fey Adept Shadow Points (Reference)],'
            '[PREFEAT:1,TYPE=Surreal]'])
        shadow = self.by_name['Shadow Magic']
        self.assertFalse(shadow['unresolved_prerequisites'])
        gate = ' '.join(shadow['prerequisites'])
        self.assertIn('Illusion - Shadow Infusion', gate)
        self.assertIn('Fey Adept Shadow Points (Reference)', gate)
        self.assertNotIn('PREFEAT:1,TYPE=Surreal', gate)
        self.assertIn('Shadow Shield', gate)
        self.assertFalse(self.by_name['Violent Shadow']['unresolved_prerequisites'])

    def test_every_surreal_feat_contributes_to_shared_shadow_capacity(self):
        surreal = [row for row in self.by_name.values() if 'Surreal' in row['types']]
        self.assertGreater(len(surreal), 10)
        for row in surreal:
            self.assertIn('DEFINE:SPHERES_FEY_ADEPT_SHADOW_POINTS|0', row['mechanics'], row['name'])
            self.assertIn('BONUS:VAR|SPHERES_FEY_ADEPT_SHADOW_POINTS|1', row['mechanics'], row['name'])
        strike = ' '.join(self.by_name['Surreal Strike']['mechanics'])
        self.assertIn('BONUS:VAR|SPHERES_SURREAL_STRIKE_LEVEL|max(1,TL-4)', strike)
        self.assertIn('Fey Adept Shadowmark Dice (Reference)', strike)
        self.assertNotIn('Fey Adept Shadow Points (Reference)', strike)

    def test_font_of_inspiration_feature_prerequisites(self):
        inspiration = self.parser.clause('inspiration class feature')
        studied = self.parser.clause('studied combat class feature')
        self.assertIn('Hedgewitch Font Of Inspiration', inspiration[0])
        self.assertIn('InvestigatorInspirationDice,1', inspiration[0])
        self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,5', studied[0])
        self.assertIn('InvestigatorStudiedCombatBonus,1', studied[0])
        for name in ('Deduction', 'Rigorous Defense'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])
        self.assertFalse(self.by_name['Studied Scout']['unresolved_prerequisites'])
        alternative = self.parser.clause('studied target or studied combat class feature')[0]
        self.assertIn('SlayerStudiedTargetBonus,1', alternative)
        self.assertIn('[' + studied[0] + ']', alternative)

    def test_extra_bestial_trait_requires_feature_and_grants_repeatable_slots(self):
        row = self.by_name['Extra Bestial Trait']
        self.assertEqual(row['prerequisites'], ['PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresBestialTrait'])
        self.assertFalse(row['unresolved_prerequisites'])
        for tag in ('MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE', 'BONUS:ABILITYPOOL|Shifter Bestial Trait|1'):
            self.assertIn(tag, row['mechanics'])

    def test_any_package_requires_selected_package_not_available_slot(self):
        tags = self.parser.clause('Nature sphere (any package)')
        self.assertEqual(tags, [
            'PREABILITY:1,CATEGORY=Spheres Magic Talent,Nature Sphere',
            'PREABILITY:1,CATEGORY=Spheres Nature Package,Nature Package - Air,Nature Package - Earth,Nature Package - Fire,Nature Package - Metal,Nature Package - Plant,Nature Package - Water'])
        self.assertFalse(self.by_name['Primal Blast']['unresolved_prerequisites'])
        self.assertIsNone(self.parser.clause('Destruction sphere (any package)'))
        self.assertIsNone(self.parser.clause('Nature sphere (any invented package)'))

    def test_cross_sphere_descriptor_prerequisites(self):
        strike = self.parser.clause('any talent with the strike descriptor')
        self.assertEqual(strike, self.parser.clause('one talent from any sphere that has the strike descriptor'))
        self.assertIn('Destruction - Energy Strike', strike[0].split(','))
        self.assertIn('Life - Clarified Strike', strike[0].split(','))
        self.assertNotIn('Destruction - Acid Blast', strike[0].split(','))
        stance = self.parser.clause('Any (stance) talent')
        self.assertIn('Berserker - Sword Eater', stance[0].split(','))
        self.assertNotIn('Berserker - Juggernaut', stance[0].split(','))
        for name in ('Spell Attack', 'Improved Spell Combat', 'Spell Maneuver', 'Pacified Strike', 'Extend Stance'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'], name)
        self.assertIsNone(self.parser.clause('any talent with the invented descriptor'))
        self.assertIsNone(self.parser.clause('two talents with the strike descriptor'))

    def test_shadowmark_feature_requires_grant_not_damage_value(self):
        expected = ['PREABILITY:1,CATEGORY=Special Ability,Fey Adept Shadowmark Dice (Reference)']
        self.assertEqual(self.parser.clause('Shadowmark class feature'), expected)
        for name in ('Gather Shadowstuff', 'Shadowblast'):
            self.assertEqual(self.by_name[name]['prerequisites'], expected)
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])

    def test_compound_heading_descriptors_are_exact_members(self):
        for sphere, descriptor, included, excluded in (
                ('Destruction', 'blast type', 'Destruction - Acid Blast', 'Destruction - Energy Aura'),
                ('Nature', 'spirit', 'Nature - Aquatic Adept', 'Nature - Water Mastery')):
            tags = self.parser.clause(f'{sphere} sphere (any ({descriptor}) talent)')
            self.assertIn(sphere + ' Sphere', tags[0])
            members = tags[1].split(',')[2:]
            self.assertIn(included, members)
            self.assertNotIn(excluded, members)
        for name in ('Furious Flare', 'Nature’s Enhancement', 'Spirit Form'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'], name)
        self.assertIsNone(self.parser.clause('Destruction sphere (any (blast) talent)'))
        self.assertIsNone(self.parser.clause('Destruction sphere (any (blast type) talent that deals cold damage)'))

    def test_sentinel_reserve_alternative_preserves_other_requirements(self):
        for spelling in ("sentinel’s reserve class feature", "sentinel's reserve class feature"):
            self.assertEqual(self.parser.clause(spelling),
                             ['PREABILITY:1,CATEGORY=Special Ability,Sentinel Reserve Points (Reference)'])
        row = self.by_name['Defender’s Bonds']
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertIn('PRELEVEL:MIN=3', row['prerequisites'])
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Combat Talent,Beastmastery Sphere', row['prerequisites'])
        self.assertIn('Sentinel Reserve Points (Reference)', '\t'.join(row['prerequisites']))
        self.assertIn('Hedgewitch Covenant Positive', '\t'.join(row['prerequisites']))
        self.assertNotIn('Hedgewitch Covenant Negative', '\t'.join(row['prerequisites']))

    def test_extra_class_options_grant_real_pools_with_source_caps(self):
        from spheres_extra_options import OPTIONS, rules
        for name, (klass, category, levels) in OPTIONS.items():
            row = self.by_name[name]
            self.assertFalse(row['unresolved_prerequisites'], name)
            self.assertIn('BONUS:ABILITYPOOL|' + category + '|1', row['mechanics'])
            self.assertIn('STACK:YES', row['mechanics'])
            self.assertNotIn('CHOOSE:USERINPUT', '\t'.join(row['mechanics']))
            for minimum in levels:
                self.assertIn(str(minimum), '\t'.join(row['prerequisites']))
            # Pool names are engine identifiers, not necessarily source headings.
            self.assertTrue(any('ABILITYCATEGORY:' + category + '\t' in path.read_text()
                                for path in DATA.glob('*categories*.lst')), category)
        self.assertIn('PREFEAT:1,Amateur Striker', '\t'.join(rules('Extra Striker Art')[0]))
        self.assertIsNone(rules('Unknown Extra Option'))

    def test_amateur_striker_choices_and_capacity(self):
        from spheres_amateur_striker import records, feat_tags
        abilities, categories = records()
        self.assertEqual(len(abilities), 14)
        self.assertEqual(len(categories), 2)
        for ability in abilities:
            self.assertIn('PREFEAT:1,Amateur Striker', ability)
            self.assertIn('!PRECLASS:1,Striker=1', ability)
            self.assertNotIn('BONUS:COMBAT', ability)
        self.assertIn('BONUS:VAR|SPHERES_AMATEUR_STRIKER_CAPACITY|max(0,CON)|!PRECLASS:1,Striker=1', feat_tags())
        self.assertTrue(set(feat_tags()).issubset(self.by_name['Amateur Striker']['mechanics']))

    def test_tension_pool_is_not_its_current_or_maximum_quantity(self):
        self.assertEqual(self.parser.clause('tension pool'),
                         ['PREMULT:1,[PRECLASS:1,Striker=1],[PREFEAT:1,Amateur Striker]'])
        self.assertEqual(self.parser.clause('Tension class feature'), ['PRECLASS:1,Striker=1'])
        self.assertEqual(self.parser.clause('No levels in a class that has the tension class feature'),
                         ['!PRECLASS:1,Striker=1'])
        for name in ('Amateur Striker', 'Expanded Tension Technique', 'Intense Metamagic'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'], name)
        # Resolving one side of an unknown alternative must not unlock it.
        self.assertIsNone(self.parser.clause('tension pool or imaginary resource'))
        self.assertFalse(self.by_name['Hold the Note']['unresolved_prerequisites'])
        for name in ('Building Performance', 'Dramatic Intensity'):
            self.assertTrue(self.by_name[name]['unresolved_prerequisites'], name)

    def test_expanded_tension_selects_only_unknown_base_techniques(self):
        from spheres_amateur_striker import expanded_records, expanded_tags, records
        abilities, categories = expanded_records()
        self.assertEqual(len(abilities), 11)
        self.assertEqual(len(categories), 1)
        for record in abilities:
            self.assertIn('PREFEAT:1,Expanded Tension Technique', record)
            self.assertIn('PREFEAT:1,Amateur Striker', record)
            self.assertIn('!PRECLASS:1,Striker=1', record)
            self.assertIn('!PREABILITY:1,CATEGORY=Amateur Striker Technique,', record)
            self.assertNotIn('BONUS:COMBAT', record)
        self.assertTrue(set(expanded_tags()).issubset(self.by_name['Expanded Tension Technique']['mechanics']))
        self.assertIn('!PREABILITY:1,CATEGORY=Expanded Tension Technique,Expanded Tension - Swift Focus',
                      '\n'.join(records()[0]))

    def test_customized_bond_requires_both_feature_sources(self):
        from spheres_armorist import option_tags as armorist
        from spheres_armiger import option_tags as armiger
        row = self.by_name['Customized Bond']
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertEqual(len(row['prerequisites']), 2)
        self.assertIn('Armorist Bound Items (Reference)', '\t'.join(row['prerequisites']))
        self.assertIn('Armiger Talents Per Customized Weapon (Reference)', '\t'.join(row['prerequisites']))
        for tags, other in ((armorist('Customized Bond'), 'Armiger Talents Per Customized Weapon'),
                            (armiger('Customized Bond'), 'Armorist Bound Items')):
            self.assertIn('ABILITY:FEAT|AUTOMATIC|Customized Bond', tags)
            self.assertIn(other + ' (Reference)', '\t'.join(tags))
        self.assertIn('PREFEAT:1,Transformation', self.by_name['Shifting Style']['prerequisites'])
        self.assertFalse(self.by_name['Shifting Style']['unresolved_prerequisites'])

    def test_spell_dabbler_is_capped_and_uses_real_feat_choices(self):
        from spheres_armiger import option_tags, spell_dabbler_category
        self.assertIn('PREVARLT:SPHERES_ARMIGER_SPELL_DABBLER_COUNT,3', option_tags('Spell Dabbler [CS]'))
        self.assertIn('BONUS:ABILITYPOOL|Armiger Spell Dabbler Feat|1', option_tags('Spell Dabbler [CS]'))
        self.assertIn('ABILITYLIST:Basic Magic Training|Advanced Magic Training|Extra Magic Talent', spell_dabbler_category())

    def test_reviewed_talent_families_require_actual_descriptor_members(self):
        for sphere, descriptor, member, excluded in (
                ('War', 'momentum', 'War - Aggressive Momentum', 'War - Combat Inertia'),
                ('Creation', 'material', 'Creation - Expanded Materials', 'Creation - Created Momentum'),
                ('Berserker', 'adrenaline', 'Berserker - Juggernaut', 'Berserker - Advancing Carnage')):
            for phrase in ('any ' + descriptor + ' talent', 'any (' + descriptor + ') talent'):
                tags = self.parser.clause(sphere + ' sphere (' + phrase + ')')
                self.assertEqual(len(tags), 2)
                self.assertIn(sphere + ' Sphere', tags[0])
                self.assertIn(member, tags[1])
                self.assertNotIn(excluded, tags[1])
        self.assertIsNone(self.parser.clause('War sphere (any invented talent)'))
        self.assertIsNone(self.parser.clause('Creation sphere (any momentum talent)'))

    def test_covenant_touch_prerequisites_preserve_polarity(self):
        from spheres_covenant import channel_prerequisite
        for name, key, energy in (('lay on hands', 'Paladin ~ Lay on Hands', 'Positive'),
                                  ('touch of corruption', 'Antipaladin ~ Touch of Corruption', 'Negative')):
            tags = self.parser.clause(name)
            self.assertEqual(tags, self.parser.clause(name + ' class feature'))
            self.assertIn(key, tags[0])
            self.assertIn(channel_prerequisite(energy), tags[0])
            self.assertNotIn('TYPE=LayOnHands', tags[0])
        self.assertFalse(self.by_name['Succor']['unresolved_prerequisites'])
        self.assertIsNone(self.parser.clause('lay on hands or invented healing class feature'))

    def test_covenant_channel_family_requires_channel_prerequisite(self):
        records = {line.split('\t')[0]: line for line in build()['spheres_feat_catalog.lst'].splitlines()}
        for name in ('Channel Luck', 'Channel Life', 'Pulsing Channel'):
            self.assertIn('HedgewitchChannelFeat', records[self.by_name[name]['key']].split('\t')[2])
        self.assertNotIn('HedgewitchChannelFeat', records[self.by_name['Extra Secret']['key']].split('\t')[2])

    def test_extra_secret_uses_feature_and_repeatable_pool(self):
        row = self.by_name['Extra Secret']
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertEqual(row['prerequisites'], ['PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresHedgewitchSecrets'])
        self.assertEqual(row['mechanics'], ['MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                                           'BONUS:ABILITYPOOL|Hedgewitch Secret|1'])
    def test_extra_wraith_haunt_requires_feature_and_grants_repeatable_slots(self):
        row = self.by_name['Extra Wraith Haunt']
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertEqual(row['prerequisites'], ['PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresWraithHaunt'])
        self.assertEqual(row['mechanics'], ['MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                                            'BONUS:ABILITYPOOL|Wraith Wraith Haunt|1'])

    def test_loaded_practitioner_class_thresholds_are_not_total_levels(self):
        for name, level in (('Commander', 5), ('Armiger', 5), ('Scholar', 7),
                            ('Blacksmith', 7), ('Striker', 5), ('Technician', 5)):
            self.assertEqual(self.parser.clause(f'{name} {level}'),
                             [f'PRECLASS:1,{name}={level}'])
        for clause in ('Commander 0', 'Commander -1', 'Warden 5', 'Associated ranks 3'):
            self.assertIsNone(self.parser.clause(clause))

    def test_friends_requires_followers_and_specialist(self):
        row = self.by_name['Friends In Close Places']
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertEqual(row['prerequisites'], [
            'PREABILITY:1,CATEGORY=Spheres Combat Talent,Leadership Sphere',
            'PREABILITY:1,CATEGORY=Spheres Leadership Package,Leadership Package - Followers',
            'PREABILITY:1,CATEGORY=Commander Logistic Specialty,Commander Call In A Specialist'])
        self.assertFalse(any(tag.startswith('BONUS:SKILL|') for tag in row['mechanics']))
        self.assertIn('DEFINE:SPHERES_COMMANDER_FOLLOWER_SPECIALIST_HOURS|SPHERES_COMMANDER_SPECIALIST_ARRIVAL_HOURS/2', row['mechanics'])
    def test_shadow_features_require_the_actual_resource(self):
        self.assertEqual(self.parser.clause('Shadowstuff class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,Fey Adept Shadow Points (Reference)'])
        self.assertEqual(self.parser.clause('Shadowmark 1d6'), [
            'PREABILITY:1,CATEGORY=Special Ability,Fey Adept Shadowmark Dice (Reference)',
            'PREVARGTEQ:SPHERES_FEY_ADEPT_SHADOWMARK_DICE,1'])
        self.assertIsNone(self.parser.clause('Shadowmark 0d6'))
        self.assertIsNone(self.parser.clause('Shadowmark 1d8'))
        for name in ('Extra Shadowstuff', 'Greater Shadowmark'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])
        self.assertIn('BONUS:VAR|SPHERES_FEY_ADEPT_SHADOW_POINTS|2', self.by_name['Extra Shadowstuff']['mechanics'])
        self.assertEqual(self.by_name['Greater Shadowmark']['mechanics'],
                         ['BONUS:VAR|SPHERES_FEY_ADEPT_SHADOWMARK_DIE_SIZE|2',
                          'DEFINE:SPHERES_FEY_ADEPT_SHADOW_POINTS|0',
                      'BONUS:VAR|SPHERES_FEY_ADEPT_SHADOW_POINTS|1',
                      'DEFINE:SPHERES_SURREAL_FEAT_COUNT|0',
                      'BONUS:VAR|SPHERES_SURREAL_FEAT_COUNT|1'])

    def test_forbidden_lore_checks_feature_not_generic_casting(self):
        expected = 'PREABILITY:1,CATEGORY=Special Ability,Thaumaturge Forbidden Lore (Reference)'
        self.assertEqual(self.parser.clause('forbidden lore class feature'), [expected])
        self.assertIn(expected, self.by_name['Tainted Manabond']['prerequisites'])
        self.assertFalse(self.by_name['Tainted Manabond']['unresolved_prerequisites'])
        self.assertIsNone(self.parser.clause('greater forbidden lore class feature'))

    def test_thaumaturge_type_requires_mandatory_casting(self):
        records = {line.split('\t')[0]: line for line in self.outputs['spheres_feat_catalog.lst'].splitlines()}
        self.assertIn('.SpheresCasting', records['Counterspell'])
        self.assertNotIn('.SpheresCasting', records['Basic Magic Training'])
        self.assertNotIn('.SpheresCasting', records['Advanced Magic Training'])

    def test_hedgewitch_magic_feat_family_requires_casting_or_magic_sphere(self):
        records = {line.split('\t')[0]: line for line in self.outputs['spheres_feat_catalog.lst'].splitlines()}
        self.assertIn('.HedgewitchMagicalSkill', records['Counterspell'])
        self.assertNotIn('.HedgewitchMagicalSkill', records['Basic Magic Training'])
        for row in self.rows:
            if row['name'] in ('Extra Magic Talent', 'Extra Spell Points', 'Extra Arsenal Trick', 'Extra Combat Talent'):
                continue
            if row['key'] not in records:
                continue
            if '.HedgewitchMagicalSkill' in records[row['key']]:
                self.assertTrue(any(tag == 'PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core'
                                    or tag.startswith('PREABILITY:1,CATEGORY=Spheres Magic Talent,')
                                    for tag in row['prerequisites']), row['name'])

    def test_blessing_feature_requires_a_granted_power(self):
        self.assertEqual(self.parser.clause('blessing/blight class feature'),
                         ['PREABILITY:1,CATEGORY=Special Ability,Soul Weaver Blessing,Soul Weaver Blight'])
        self.assertFalse(self.by_name['Blessing/Blight Mastery']['unresolved_prerequisites'])
        self.assertIn('Versatile Channeler', self.by_name['Blessing/Blight Versatility']['unresolved_prerequisites'])
        self.assertIsNone(self.parser.clause('greater blessing/blight class feature'))

    def test_extra_nexus_grants_souls_not_nexus_ability_choices(self):
        row = self.by_name['Extra Nexus Powers']
        self.assertFalse(row['unresolved_prerequisites'])
        self.assertEqual(row['prerequisites'],
                         ['PREABILITY:1,CATEGORY=Special Ability,Soul Weaver Bound Souls (Reference)'])
        self.assertEqual(row['mechanics'], ['MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                                          'BONUS:VAR|SPHERES_SOUL_WEAVER_BOUND_SOULS|2'])
        self.assertIsNone(self.parser.clause('greater bound nexus class feature'))

    def test_channel_energy_requires_actual_feature(self):
        from spheres_covenant import channel_prerequisite
        generic = self.parser.clause('channel energy class feature')
        self.assertEqual(generic, self.parser.clause('Channel Energy'))
        self.assertIn('TYPE=ChannelEnergy', generic[0])
        self.assertIn(channel_prerequisite(), generic[0])
        self.assertIn('TYPE=Channel Energy', generic[0])
        self.assertIn('CATEGORY=Soul Weaver Channel,Soul Weaver Positive Channel,Soul Weaver Negative Channel', generic[0])
        for energy in ('positive', 'negative'):
            tags = self.parser.clause('ability to channel ' + energy + ' energy')
            self.assertIn('TYPE=Channel ' + energy.title() + ' Energy', tags[0])
            self.assertIn('Soul Weaver ' + energy.title() + ' Channel', tags[0])
            self.assertIn(channel_prerequisite(energy.title()), tags[0])
            self.assertNotIn('PRECLASS', tags[0])
        for unsupported in ('channel energy 0d6', 'channel energy 4d8', 'channel fire energy'):
            self.assertIsNone(self.parser.clause(unsupported))
        for name in ('Channel Life', 'Channel Destruction', 'Channeled Detonation'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])
        either = self.parser.clause('Ability to channel positive or negative energy')
        self.assertIn('TYPE=Channel Positive Energy', either[0])
        self.assertIn('TYPE=Channel Negative Energy', either[0])
        self.assertFalse(self.by_name['Energized Spell']['unresolved_prerequisites'])
        self.assertIsNone(self.parser.clause('ability to channel positive or fire energy'))

    def test_channel_dice_do_not_combine_independent_pools(self):
        from spheres_channel import dice_prerequisite
        for dice in (3, 4):
            tags = self.parser.clause(f'channel energy {dice}d6')
            self.assertEqual(tags, [dice_prerequisite(dice)])
            self.assertNotIn('+', tags[0])
            self.assertEqual(tags[0].count('DieSize,6'), 3)
            self.assertIn(f'SPHERES_CHANNEL_DICE,{dice}', tags[0])
            self.assertIn(f'SPHERES_SOUL_WEAVER_CHANNEL_DICE,{dice}', tags[0])
            self.assertIn(f'SPHERES_HEDGEWITCH_COVENANT_DICE,{dice}', tags[0])
            self.assertIn('SPHERES_HEDGEWITCH_COVENANT_DIE_SIZE,6', tags[0])
            from spheres_covenant import channel_prerequisite
            self.assertIn(channel_prerequisite(), tags[0])
        for invalid in (0, -1, True, '3'):
            with self.assertRaises(ValueError):
                dice_prerequisite(invalid)
        for name in ('Defiler’s Channel', 'Pulsing Channel'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])

    def test_plague_persistent_effects(self):
        self.assertEqual(self.by_name['Rotten Hordes']['mechanics'],
                         ['BONUS:VAR|SPHERES_SPELL_POINTS|1',
                          'DEFINE:SPHERES_NECROSIS_FEAT_COUNT|0',
                          'BONUS:VAR|SPHERES_NECROSIS_FEAT_COUNT|1',
                          'DEFINE:SPHERES_DEFILER_FEAT_COUNT|0',
                          'BONUS:VAR|SPHERES_DEFILER_FEAT_COUNT|1|PREFEAT:1,Inhuman Defiler'])
        tags = self.by_name['Pathology']['mechanics']
        self.assertEqual(tags[:3], ['MULT:YES', 'STACK:NO', 'SELECT:2'])
        choices = tags[3].split('|')[1:]
        self.assertEqual(len(set(choices)), 12)
        for choice in choices:
            self.assertIn(choice.lower(), self.by_name['Pathology']['text'].lower())

    def test_plague_shared_requirements_apply_outside_alternatives(self):
        from spheres_plague import prerequisites, SUFFIXES
        base = self.by_name['Virulent Ailment']['prerequisites'][0]
        for sphere in ('BLOOD', 'DEATH'):
            self.assertIn(f'PREVARGTEQ:SPHERES_CL_{sphere},5', base)
        self.assertEqual(base.count('[PREATT:5]'), 2)
        for name in SUFFIXES:
            row = self.by_name[name]
            self.assertFalse(row['unresolved_prerequisites'])
            self.assertEqual(row['prerequisites'][0], base)
            if name != 'Virulent Ailment':
                self.assertIn('PREFEAT:1,Virulent Ailment', row['prerequisites'][1:])
            with self.assertRaises(ValueError):
                prerequisites(name, row['text'].replace('5th caster level', '6th caster level'))
        self.assertIn('PREVARGTEQ:TL,9', self.by_name['Encompassing Illness']['prerequisites'])
        self.assertIn('PREVARGTEQ:TL,7', self.by_name['Pathological Host']['prerequisites'])
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Death - Shroud',
                      self.by_name['Rotten Hordes']['prerequisites'])

    def test_conjoined_skill_branch_does_not_weaken_alternatives(self):
        row = self.by_name["Vigilant Skeptic"]
        self.assertFalse(row["unresolved_prerequisites"])
        self.assertEqual(row["prerequisites"], [
            "PREMULT:1,[PREMULT:2,[PRESKILL:1,Perception=5],[PRESKILL:1,Sense Motive=5]],[PREFEAT:1,Alertness]"])
        for invalid in ("Perception 5 ranks and Unknown 5 ranks", "Perception 5 ranks and Sense Motive 0 ranks"):
            self.assertIsNone(self.parser.clause(invalid))
        tags, missing = self.parser.compile(
            "Prerequisites: Perception 5 ranks and Unknown 5 ranks; or Alertness.\nBenefit: Test.")
        self.assertFalse(tags)
        self.assertTrue(missing)

    def test_cautious_incantation_filters_targets_by_ranks(self):
        self.assertEqual(self.by_name["Cautious Incantation"]["mechanics"],
                         ["MULT:YES", "STACK:NO", "CHOOSE:SKILL|RANKS=3"])
        self.assertEqual(self.by_name["Ritualistic Perseverance"]["mechanics"],
                         ["MULT:YES", "STACK:NO", "SELECT:2", "CHOOSE:SKILL|RANKS=3"])

    def test_any_single_skill_uses_individual_rank_threshold(self):
        for ranks in (1, 3, 5):
            self.assertEqual(self.parser.clause(f"{ranks} ranks in any 1 skill"),
                             [f"PRESKILL:1,TYPE.Base={ranks}"])
        for invalid in ("0 ranks in any 1 skill", "3 ranks in any 0 skills",
                        "3 total ranks in any 1 skill", "three ranks in any 1 skill"):
            self.assertIsNone(self.parser.clause(invalid))
        for name in ("Cautious Incantation", "Expedited Incantation", "Solitary Incantation"):
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere; or Warleader sphere, 3 ranks in any 1 skill.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PRESKILL:1,TYPE.Base=3", tags)

    def test_two_skills_count_distinct_qualifying_skills(self):
        self.assertEqual(self.parser.clause("3 ranks in any 2 skills"),
                         ["PRESKILL:2,TYPE.Base=3,CHECKMULT"])
        self.assertFalse(self.by_name["Ritualistic Perseverance"]["unresolved_prerequisites"])
        for invalid in ("0 ranks in any 2 skills", "3 total ranks in any 2 skills",
                        "3 ranks in any two skills"):
            self.assertIsNone(self.parser.clause(invalid))

    def test_reviewed_reversed_threshold_forms(self):
        for clause, tags in (
                ('+3 base attack bonus', ['PREATT:3']),
                ('3rd level', ['PRELEVEL:MIN=3']),
                ('Sense Motive ranks 3', ['PRESKILL:1,Sense Motive=3']),
                ('1 or more metamagic feats', ['PREFEAT:1,TYPE=Metamagic']),
                ('base attack bonus +5 or monk 3', ['PREMULT:1,[PREATT:5],[PRECLASS:1,Monk=3]'])):
            self.assertEqual(self.parser.clause(clause), tags)
        for clause in ('+three base attack bonus', 'third level', 'Unknown ranks 3',
                       'Sense Motive ranks 0', '2 or more metamagic feats', 'monk 0'):
            self.assertIsNone(self.parser.clause(clause))
        for name in ('Commanding Presence', 'Dimensional Archer', 'Heedless Metamagic', 'Tentacle Adept'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])
        self.assertIn('Two or more tentacles', self.by_name['Tentacle Novice']['unresolved_prerequisites'])

    def test_explicit_sphere_caster_level_does_not_use_global_or_other_spheres(self):
        for sphere, level in (("Blood", 5), ("Bear", 5), ("Illusion", 5), ("Divination", 6)):
            self.assertEqual(self.parser.clause(f"{sphere} sphere caster level {level}th", "SPHERES_CL_LIFE"), [
                f"PREABILITY:1,CATEGORY=Spheres Magic Talent,{sphere} Sphere",
                f"PREVARGTEQ:SPHERES_CL_{sphere.upper()},{level}"])
        for invalid in ("Unknown sphere caster level 5th", "Boxing sphere caster level 5th",
                        "Blood sphere caster level 0th", "Blood sphere caster level five"):
            self.assertIsNone(self.parser.clause(invalid))
        for name in ("Blood Construct Mastery", "Bruinous Temper", "Glamered Thievery"):
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])
        self.assertFalse(self.by_name["Glimpse The Flow"]["unresolved_prerequisites"])
        self.assertIn('PREVARGTEQ:SPHERES_CL_DIVINATION,6', self.by_name["Glimpse The Flow"]["prerequisites"])

    def test_craft_or_profession_requires_ranks_in_either_family(self):
        for ranks in (5, 10):
            self.assertEqual(self.parser.clause(f"Any Craft or Profession {ranks} ranks"),
                             [f"PRESKILL:1,TYPE.Craft={ranks},TYPE.Profession={ranks}"])
        for clause in ("Any Craft or Profession 0 ranks", "Any Craft or Profession five ranks",
                       "Any Craft or Unknown 5 ranks"):
            self.assertIsNone(self.parser.clause(clause))
        for name in ("Artificery", "Improved Artificery"):
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])

    def test_drawback_enumeration_keeps_other_prerequisites(self):
        expected = ("PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Skilled Casting,"
                    "Tradition - Somatic Casting,Tradition - Verbal Casting")
        clause = "at least one of the Skilled Casting, Somatic Casting, or Verbal Casting drawbacks"
        self.assertEqual(self.parser.clause(clause), [expected])
        row = self.by_name["Mystic Choreography"]
        self.assertFalse(row["unresolved_prerequisites"])
        for tag in (expected, "PREABILITY:1,CATEGORY=Spheres Magic Talent,Enhancement Sphere",
                    "PREFEAT:1,Circle Casting", "PREFEAT:1,Spell Proxy"):
            self.assertIn(tag, row["prerequisites"])
        for invalid in (clause.replace("Verbal Casting", "Unmodeled Casting"),
                        clause.replace("Verbal Casting", "Skilled Casting"),
                        clause.replace("at least one", "at least two")):
            self.assertIsNone(self.parser.clause(invalid))

    def test_spell_proxy_special_requires_review_without_drawback_model(self):
        row = self.by_name["Spell Proxy"]
        self.assertEqual(row["unresolved_prerequisites"],
                         ["Must not possess the Personal Magics sphere-specific drawback (Special)"])
        self.assertIn("PREFEAT:1,Circle Casting", row["prerequisites"])
        line = next(line for line in self.outputs["spheres_feat_catalog.lst"].splitlines()
                    if line.startswith("Spell Proxy\t"))
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Feat Adjudication,Reviewed - Spell Proxy", line)

    def test_msb_abbreviation_uses_magic_skill_not_caster_level(self):
        self.assertEqual(self.parser.clause("MSB +7"),
                         ["PREVARGTEQ:SPHERES_MAGIC_SKILL_BONUS,7"])
        self.assertIsNone(self.parser.clause("MSB +seven"))
        tags, missing = self.parser.compile(
            "Prerequisites: Life sphere; or Protection sphere, MSB +7.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREVARGTEQ:SPHERES_MAGIC_SKILL_BONUS,7", tags)
        for name in ("Admixture Efficiency", "Inspired Learning"):
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])

    def test_reviewed_feat_family_requirements(self):
        for clause, family in (("any one Admixture feat", "Admixture"),
                               ("any Admixture feat", "Admixture"),
                               ("at least one Proxy feat", "Proxy"),
                               ("Any one teamwork feat", "Teamwork"),
                               ("At least one metamagic feat", "Metamagic")):
            self.assertEqual(self.parser.clause(clause), ["PREFEAT:1,TYPE=" + family])
        for clause in ("any one unknown feat", "at least two Proxy feats",
                       "at least one Proxy feat or unknown prerequisite"):
            self.assertIsNone(self.parser.clause(clause))
        for name, family in (("Selective Admixture", "Admixture"),
                             ("Solipsistic Admixture", "Admixture"),
                             ("Maintain Proxy", "Proxy"),
                             ("Spell Proxy, Extended", "Proxy")):
            row = self.by_name[name]
            if family in row["types"]:
                family_tags = [tag for tag in row["prerequisites"]
                               if tag.startswith("PREFEAT:1,") and "Spell Proxy" in tag]
                self.assertEqual(len(family_tags), 1)
                self.assertNotIn(row["key"], family_tags[0].split(",")[1:])
                self.assertIn("Spell Proxy", family_tags[0].split(",")[1:])
            else:
                self.assertIn("PREFEAT:1,TYPE=" + family, row["prerequisites"])
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])

    def test_blended_training_grants_one_shared_allocation_not_both_talents(self):
        self.assertEqual(self.by_name["Extra Blended Training Talent"]["mechanics"], [
            "MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
            "BONUS:ABILITYPOOL|Spheres Blended Talent Allocation|1"])
        for kind in ("Magic", "Combat"):
            line = next(line for line in self.outputs['spheres_feat_catalog.lst'].splitlines()
                        if line.startswith('Blended Training - ' + kind + '\t'))
            self.assertIn('CATEGORY:Spheres Blended Talent Allocation', line)
            self.assertIn('BONUS:ABILITYPOOL|Spheres ' + kind
                          + ' Talent|1|PREFEAT:1,Extra Blended Training Talent', line)
            self.assertIn('PREFEAT:1,Extra Blended Training Talent', line)
            self.assertIn('|PREABILITY:2,CATEGORY=Special Ability,Spheres Casting Core,Spheres Martial Focus', line)
            self.assertNotIn('COST:0', line)

    def test_legacy_overrides_cannot_silently_claim_unemitted_mechanics(self):
        from pathlib import Path
        original = Path.read_text

        def read(path, *args, **kwargs):
            content = original(path, *args, **kwargs)
            if path == DATA / "feat-mechanics.json":
                rows = json.loads(content)
                rows["Extra Arsenal Trick"] = {"tags": ["BONUS:ABILITYPOOL|Armorist Arsenal Trick|1"]}
                return json.dumps(rows)
            return content

        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(ValueError, "Legacy feat overrides are not emitted.*Extra Arsenal Trick"):
                build()

    def test_extra_emotion_requires_feature_not_a_selected_power(self):
        for name in ("Elicit Strike", "Extra Emotion"):
            self.assertEqual(self.by_name[name]["prerequisites"],
                             ["PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresEmotion"])
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])
        self.assertEqual(self.by_name["Extra Emotion"]["mechanics"],
                         ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:ABILITYPOOL|Eliciter Emotion|1"])

    def test_extra_resources_require_existing_features(self):
        for name, feature, variable, increment in (
                ("Extra Psionics", "Symbiat Psionics Rounds (Reference)", "SPHERES_SYMBIAT_PSIONICS_ROUNDS", 6),
                ("Extra Invocations", "Thaumaturge Invocation Uses (Reference)", "SPHERES_THAUMATURGE_INVOCATION_USES", 2)):
            row = self.by_name[name]
            self.assertFalse(row["unresolved_prerequisites"])
            self.assertEqual(row["prerequisites"], ["PREABILITY:1,CATEGORY=Special Ability," + feature])
            self.assertEqual(row["mechanics"], ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                                               f"BONUS:VAR|{variable}|{increment}"])

    def test_extra_class_choices_require_features_and_grant_only_their_pool(self):
        for name, feature, pool in (("Extra Mystic Combat", "MysticCombat", "Mageknight Mystic Combat"),):
            row = self.by_name[name]
            self.assertFalse(row["unresolved_prerequisites"])
            self.assertEqual(row["prerequisites"], ["PREABILITY:1,CATEGORY=Special Ability,TYPE=Spheres" + feature])
            self.assertEqual(row["mechanics"], ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                                               "BONUS:ABILITYPOOL|" + pool + "|1"])

    def test_oxford_talent_enumeration_is_one_of_not_all_of(self):
        expected = ["PREABILITY:1,CATEGORY=Spheres Magic Talent,Telekinesis Sphere",
            "PREMULT:1,[PREABILITY:1,CATEGORY=Spheres Magic Talent,Telekinesis - Finesse],[PREABILITY:1,CATEGORY=Spheres Magic Talent,Telekinesis - Steal],[PREABILITY:1,CATEGORY=Spheres Magic Talent,Telekinesis - Telekinetic Tools]"]
        self.assertEqual(self.parser.clause("Telekinesis sphere (Finesse, Steal, or Telekinetic Tools)"), expected)
        self.assertFalse(self.by_name["Skillful Force"]["unresolved_prerequisites"])
        for value in ("Telekinesis sphere (Finesse, Steal, or imaginary talent)",
                      "Telekinesis sphere (Finesse or Steal, or Telekinetic Tools)"):
            self.assertIsNone(self.parser.clause(value))
        conjunction = self.parser.clause("Telekinesis sphere (Finesse, Steal)")
        self.assertEqual(len(conjunction), 3)
        self.assertTrue(all(tag.startswith("PREABILITY:") for tag in conjunction))

    def test_inner_talent_alternatives_are_not_conjunctions(self):
        tags = self.parser.clause("Destruction sphere (Energy Wall (blast shape) or Explosive Orb (blast shape))")
        self.assertEqual(tags, ["PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere",
            "PREMULT:1,[PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction - Energy Wall],[PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction - Explosive Orb]"])
        self.assertFalse(self.by_name["Shape Expert"]["unresolved_prerequisites"])
        for clause in ("Destruction sphere (Energy Wall or imaginary talent)",
                       "Destruction sphere (Energy Wall, Explosive Orb or imaginary talent)"):
            self.assertIsNone(self.parser.clause(clause))

    def test_parenthesized_sphere_alternatives_preserve_whole_branches(self):
        self.assertEqual(split_alternatives("Life sphere (Diagnose) or Mind sphere (Project Thoughts)"),
                         ["Life sphere (Diagnose)", "Mind sphere (Project Thoughts)"])
        self.assertEqual(split_alternatives("Destruction sphere (Energy Wall or Explosive Orb)"),
                         ["Destruction sphere (Energy Wall or Explosive Orb)"])
        expected = "PREMULT:1,[PREMULT:2,[PREABILITY:1,CATEGORY=Spheres Magic Talent,Life Sphere],[PREABILITY:1,CATEGORY=Spheres Magic Talent,Life - Diagnose]],[PREMULT:2,[PREABILITY:1,CATEGORY=Spheres Magic Talent,Mind Sphere],[PREABILITY:1,CATEGORY=Spheres Magic Talent,Mind - Project Thoughts]]"
        self.assertEqual(self.parser.clause("Life sphere (Diagnose) or Mind sphere (Project Thoughts)"),
                         [expected])
        for value in ("Life sphere (Diagnose) or unknown feature", "Life sphere (Diagnose))",
                      "Life sphere (Diagnose", "Life sphere ()", "Life sphere ( )",
                      "Life sphere (unknown talent) or Mind sphere"):
            self.assertIsNone(self.parser.clause(value), value)
        self.assertFalse(self.by_name["Universal Bonding"]["unresolved_prerequisites"])

    def test_package_suffix_punctuation_preserves_both_requirements(self):
        expected = ["PREABILITY:1,CATEGORY=Spheres Combat Talent,Alchemy Sphere",
                    "PREABILITY:1,CATEGORY=Spheres Alchemy Package,Alchemy Package - Formulae"]
        self.assertEqual(self.parser.clause("Alchemy sphere (formulae) package"), expected)
        self.assertIsNone(self.parser.clause("Alchemy sphere (fictional) package"))
        self.assertFalse(self.by_name["Technologically Alchemical Ammo"]["unresolved_prerequisites"])
        for tag in expected:
            self.assertIn(tag, self.by_name["Technologically Alchemical Ammo"]["prerequisites"])

    def test_reviewed_bare_talents_need_their_own_sphere(self):
        for talent, sphere in (("Ammo Spitter", "Tech"), ("Plant Mastery", "Nature")):
            tags, unknown = self.parser.compile(
                f"Prerequisites: {sphere} sphere, {talent}.\nBenefit: Test.")
            self.assertFalse(unknown)
            category = "Spheres Combat Talent" if sphere == "Tech" else "Spheres Magic Talent"
            self.assertIn(f"PREABILITY:1,CATEGORY={category},{sphere} - {talent}", tags)
            for context in ("", "Scout sphere, ", f"{sphere} sphere (fictional package), "):
                _, unknown = self.parser.compile(f"Prerequisites: {context}{talent}.\nBenefit: Test.")
                self.assertTrue(unknown)

    def test_drone_requires_explicit_tech_context(self):
        for name in ("Mobile Drone", "Reckless Drone", "Recon Drone", "Shield Drone", "Technical Compatibility"):
            row = self.by_name[name]
            self.assertNotIn("Drone", row["unresolved_prerequisites"])
            self.assertIn("PREABILITY:1,CATEGORY=Spheres Combat Talent,Tech - Drone", row["prerequisites"])
        for text in ("Drone", "Scout sphere, Drone", "Tech sphere or Drone", "Tech sphere, Drone or unknown talent"):
            _, unknown = self.parser.compile("Prerequisites: " + text + "\nBenefit: Test.")
            self.assertTrue(unknown, text)
        self.assertIsNone(self.parser.clause("Drone"))

    @classmethod
    def setUpClass(cls):
        cls.outputs = build()
        cls.rows = json.loads(cls.outputs["feat-catalog.json"])
        cls.parser = Prerequisites(cls.rows)
        cls.by_name = {r["name"]: r for r in cls.rows}

    def test_generated_data_current(self):
        for name, content in self.outputs.items():
            self.assertEqual((DATA / name).read_text(), content, name)

    def test_alchemy_required_feats_use_associated_ranks(self):
        affected = [row for row in self.rows
                    if 'PREABILITY:1,CATEGORY=Spheres Combat Talent,Alchemy Sphere' in row['prerequisites']
                    and any('SPHERES_ALCHEMY_RANKS' in tag for tag in row['prerequisites'])]
        self.assertTrue(affected)
        for row in affected:
            self.assertFalse(any('PRESKILL:1,Craft (Alchemy)=' in tag for tag in row['prerequisites']))
        self.assertEqual(self.parser.clause('Craft (alchemy) 5 ranks'),
                         ['PRESKILL:1,Craft (Alchemy)=5'])

    def test_identity_and_no_legacy_duplicates(self):
        lines = self.outputs["spheres_feat_catalog.lst"].splitlines()[1:]
        keys = [line.split("\t")[0] for line in lines]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertNotIn("Extra Magic Talent", keys)
        self.assertNotIn("Extra Combat Talent", keys)
        self.assertIn("Improved Counterspell (Spheres)", keys)
        self.assertGreater(len(self.rows), 1000)

    def test_unknown_prerequisites_require_explicit_approval(self):
        records = {s.split("\t")[0]: s for s in self.outputs["spheres_feat_catalog.lst"].splitlines()[1:]}
        for row in self.rows:
            if row["unresolved_prerequisites"] and row["key"] in records:
                self.assertIn("PREABILITY:1,CATEGORY=Spheres Feat Adjudication,Reviewed - " + row["key"], records[row["key"]])

    def test_or_not_accidentally_and(self):
        tags = self.parser.clause("Blood sphere or Duelist sphere")
        self.assertTrue(tags[0].startswith("PREMULT:1,"))
        self.assertIsNone(self.parser.clause("Improved Trip or a talent allowing safe trips"))
        tags, missing = self.parser.compile("Prerequisites: Bardic performance, raging song, or Warleader sphere.\nBenefit: Test.")
        self.assertEqual(tags, [])
        self.assertEqual(len(missing), 1)

    def test_exact_alignment_requirements(self):
        for clause, expected in (
                ("good alignment", "PREALIGN:LG,NG,CG"),
                ("evil alignment", "PREALIGN:LE,NE,CE"),
                ("non-good alignment", "!PREALIGN:LG,NG,CG"),
                ("nonlawful", "!PREALIGN:LG,LN,LE"),
                ("non-neutral alignment", "!PREALIGN:TN")):
            self.assertEqual(self.parser.clause(clause), [expected])
        self.assertFalse(self.by_name['Aligned Attacks']['unresolved_prerequisites'])
        self.assertIn('!PREALIGN:TN', self.by_name['Aligned Attacks']['prerequisites'])
        self.assertIn('PREVARGTEQ:SPHERES_CASTER_LEVEL,5', self.by_name['Aligned Attacks']['prerequisites'])
        self.assertIsNone(self.parser.clause("alignment matching a patron"))
        tags, missing = self.parser.compile(
            "Prerequisites: good alignment or evil alignment.\nBenefit: Test.")
        self.assertEqual(tags, ["PREMULT:1,[PREALIGN:LG,NG,CG],[PREALIGN:LE,NE,CE]"])
        self.assertFalse(missing)
        for name in ("Seraphic Glow", "Damning Darkness", "Terrain Defiler"):
            self.assertFalse(self.by_name[name]["unresolved_prerequisites"])

    def test_hubris_alternative_is_class_level_not_character_level(self):
        for name, level in (("Hubris Style", 3), ("Hubris Defiance", 5), ("Hubris Triumph", 9)):
            row = self.by_name[name]
            self.assertFalse(row["unresolved_prerequisites"])
            self.assertIn(f"PREMULT:1,[PREATT:{level}],[PRECLASS:1,Monk={level}]",
                          row["prerequisites"])
            self.assertIn("!PREALIGN:LG,LN,LE", row["prerequisites"])
        self.assertIsNone(self.parser.clause("monk level 0"))
        self.assertIsNone(self.parser.clause("unknown class level 3rd"))
        self.assertIsNone(self.parser.clause("base attack bonus +3 or unknown class level 3rd"))

    def test_counterspell_mastery_does_not_raise_global_magic_skill(self):
        self.assertEqual(self.by_name["Counterspell Mastery"]["mechanics"],
                         ["BONUS:VAR|SPHERES_COUNTERSPELL_CHECK_BONUS|2"])
        self.assertIn("DEFINE:SPHERES_COUNTERSPELL_CHECK|SPHERES_MAGIC_SKILL_BONUS+SPHERES_COUNTERSPELL_CHECK_BONUS",
                      self.by_name["Counterspell"]["mechanics"])

    def test_terrain_special_restrictions_preserve_primary_prerequisites(self):
        for name in ("Terrain Defiler", "Specialist Defiler"):
            row = self.by_name[name]
            self.assertIn("!PREFEAT:1,Terrain Focus", row["prerequisites"])
            self.assertIn("!PREALIGN:LG,NG,CG", row["prerequisites"])
            self.assertIn("You cannot gain this feat if you possess the Terrain Focus feat", row["text"])
        row = self.by_name["Terrain Focus"]
        self.assertIn("!PREFEAT:1,Terrain Defiler,Specialist Defiler", row["prerequisites"])
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,Nature Sphere", row["prerequisites"])
        self.assertIn("and vice versa", self.by_name["Specialist Defiler"]["text"])

    def test_nested_talent_prerequisites(self):
        self.assertEqual(len(split_clauses("Destruction sphere (Admixture, Searing Blast), caster level 5th")), 2)
        tags, missing = self.parser.compile("Prerequisites: Destruction sphere (Admixture), caster level 5th.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,Admixture", tags)
        self.assertIn("PREVARGTEQ:SPHERES_CL_DESTRUCTION,5", tags)
        self.assertEqual(self.parser.clause("Alchemy sphere ((formulae) package)")[-1],
                         "PREABILITY:1,CATEGORY=Spheres Alchemy Package,Alchemy Package - Formulae")

    def test_source_types_not_page_types(self):
        self.assertEqual(self.by_name["Basic Magic Training"]["types"], ["General"])
        self.assertIn("Combat", self.by_name["Extra Combat Talent"]["types"])
        self.assertNotIn("Advanced Magical Training", self.by_name)
        self.assertNotIn("Prepare Consumable", self.by_name)

    def test_counterspell_chain_avoids_core_name_collision(self):
        self.assertIn("PREFEAT:2,Counterspell,Improved Counterspell (Spheres)", self.by_name["Greater Counterspell"]["prerequisites"])

    def test_sphere_choices_are_distinct_and_targeted(self):
        data = self.outputs["spheres_feat_catalog.lst"]
        self.assertIn("Sphere Focus - Life\t", data)
        self.assertIn("BONUS:VAR|SPHERES_DC_LIFE|1", data)
        self.assertIn("Combat Sphere Specialization - Fencing\t", data)
        self.assertIn("BONUS:VAR|SPHERES_BAB_FENCING|min(max(0,TL-BAB),1+floor((TL-1)/4))", data)
        self.assertEqual(self.parser.clause("Sphere Focus"), ["PREFEAT:1,TYPE=SpheresFeatSphereFocus"])

    def test_no_invalid_key_delimiters(self):
        for line in self.outputs["spheres_feat_catalog.lst"].splitlines()[1:]:
            self.assertNotIn(",", line.split("\t")[0])

    def test_multi_clause_or_branches(self):
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Troop Commander.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertEqual(len(tags), 1)
        self.assertTrue(tags[0].startswith("PREMULT:1,[PREMULT:2,"))
        for piece in ("PREABILITY:1,CATEGORY=Spheres Magic Talent,War Sphere",
                      "PREFEAT:1,Squadron Commander",
                      "PREABILITY:1,CATEGORY=Spheres Combat Talent,Warleader Sphere",
                      "PREFEAT:1,Troop Commander"):
            self.assertIn(piece, tags[0])

    def test_or_branch_global_requirements_hoisted(self):
        for clause, expected in (('+3 base attack bonus', 'PREATT:3'),
                                 ('3rd level', 'PRELEVEL:MIN=3'),
                                 ('Sense Motive ranks 3', 'PRESKILL:1,Sense Motive=3')):
            tags, missing = self.parser.compile(
                f'Prerequisites: Life sphere; or Protection sphere, {clause}.\nBenefit: Test.')
            self.assertFalse(missing)
            self.assertIn(expected, tags)
            self.assertNotIn(expected, tags[0])
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Troop Commander; character level 10th.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PRELEVEL:MIN=10", tags)
        self.assertNotIn("PRELEVEL", tags[0])
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Troop Commander; caster level 5th or 5 ranks in Diplomacy.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREMULT:1,[PREVARGTEQ:SPHERES_CL_WAR,5],[PRESKILL:1,Diplomacy=5]", tags)

    def test_or_branch_fail_closed(self):
        tags, missing = self.parser.compile("Prerequisites: War sphere; or Performance sphere.\nBenefit: Test.")
        self.assertEqual(tags, [])
        self.assertEqual(missing, ["War sphere; or Performance sphere"])
        tags, missing = self.parser.compile(
            "Prerequisites: War sphere, Squadron Commander; or Warleader sphere, Unknown Talent.\nBenefit: Test.")
        self.assertEqual(tags, [])
        self.assertTrue(missing)

    def test_drawback_prerequisites(self):
        for text, record in (("Terrain Casting drawback", "Tradition - Terrain Casting"),
                             ("Charged Spells", "Tradition - Charged Spells"),
                             ("Draining Casting (drawback)", "Tradition - Draining Casting"),
                             ("Vampiric Casting drawback", "Tradition - Vampiric Casting")):
            self.assertEqual(self.parser.clause(text),
                             ["PREABILITY:1,CATEGORY=Custom Casting Drawback," + record])
        tags = self.parser.clause("Draining Casting (drawback) or Unsettling Casting (drawback)")
        self.assertEqual(tags, ["PREMULT:1,[PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Draining Casting],"
                                "[PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Unsettling Casting]"])

    def test_skill_rank_forms(self):
        self.assertEqual(self.parser.clause("Craft (alchemy) 5 ranks"), ["PRESKILL:1,Craft (Alchemy)=5"])
        self.assertEqual(self.parser.clause("Knowledge (planes) 5 ranks"), ["PRESKILL:1,Knowledge (Planes)=5"])
        self.assertEqual(self.parser.clause("Heal 1 rank"), ["PRESKILL:1,Heal=1"])
        self.assertEqual(self.parser.clause("5 ranks in Diplomacy"), ["PRESKILL:1,Diplomacy=5"])
        self.assertEqual(self.parser.clause("5 ranks in any 2 skills"),
                         ["PRESKILL:2,TYPE.Base=5,CHECKMULT"])
        self.assertIsNone(self.parser.clause("Profession (notaskill) 5 ranks"))

    def test_magic_training_does_not_count_other_caster_classes_as_martial(self):
        rows = self.outputs['spheres_feat_catalog.lst'].splitlines()
        for name in ('Basic Magic Training', 'Advanced Magic Training'):
            row = next(row for row in rows if row.startswith(name + '\t'))
            self.assertNotIn('SPHERES_INCANTER_LEVEL', row)
            self.assertIn('SPHERES_SPELL_POOL_LEVELS', row)
        advanced = next(row for row in rows if row.startswith('Advanced Magic Training\t'))
        self.assertIn('floor((TL-SPHERES_SPELL_POOL_LEVELS)/2)', advanced)

    def test_basic_training_unlocks_existing_casting_choices_without_class_levels(self):
        row = next(row for row in self.outputs['spheres_feat_catalog.lst'].splitlines()
                   if row.startswith('Basic Magic Training\t'))
        for category in ('Spheres Casting Ability', 'Custom Casting Tradition'):
            self.assertIn('BONUS:ABILITYPOOL|' + category +
                          '|1|PREVAREQ:SPHERES_SPELL_POOL_LEVELS,0', row)
        for row in (DATA / 'spheres_core.lst').read_text().splitlines():
            if '\tCATEGORY:Spheres Casting Ability\t' in row:
                self.assertIn('PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core', row)
                self.assertNotIn('PREVARGTEQ:SPHERES_SPELL_POOL_LEVELS', row)

    def test_one_of_alternatives(self):
        tags = self.parser.clause("one of Agonizing Defiling, Ruinous Defiling, or Spellburn Defiling")
        self.assertEqual(tags, ["PREMULT:1,[PREFEAT:1,Agonizing Defiling],[PREFEAT:1,Ruinous Defiling],"
                                "[PREFEAT:1,Spellburn Defiling]"])
        tags, missing = self.parser.compile(
            "Prerequisites: Terrain Casting drawback, one of Agonizing Defiling, Ruinous Defiling, or Spellburn Defiling.\nBenefit: Test.")
        self.assertFalse(missing)
        self.assertIn("PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Terrain Casting", tags)
        self.assertTrue(any(t.startswith("PREMULT:1,[PREFEAT:1,Agonizing Defiling]") for t in tags))
        self.assertIsNone(self.parser.clause("one of Fabricated Feat, or Spellburn Defiling"))

    def test_limited_repeatability(self):
        line = next(s for s in self.outputs["spheres_feat_catalog.lst"].splitlines()
                    if s.startswith("Practiced Interruption\t"))
        self.assertIn("PREVARLT:SPHERES_FEAT_PRACTICEDINTERRUPTION_COUNT,2", line)

    def test_martial_focus_eligibility(self):
        focus = "PREABILITY:1,CATEGORY=Special Ability,Spheres Martial Focus"
        for clause in ("martial focus", "Ability to gain martial focus", "ability to maintain martial focus"):
            self.assertEqual(self.parser.clause(clause), [focus])
        self.assertEqual(self.parser.clause("combat training class feature"),
                         ["PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresCombatTraining"])
        self.assertEqual(self.parser.clause("casting class feature or ability to gain martial focus"),
                         ["PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core],[" + focus + "]"])
        self.assertIsNone(self.parser.clause("ability to gain martial focus or use skill leverage"))
        self.assertIsNone(self.parser.clause("currently has martial focus"))
        self.assertEqual(self.by_name["Unified Focus"]["unresolved_prerequisites"], [])
        self.assertTrue(self.by_name["Winded By Words"]["unresolved_prerequisites"])

    def test_focus_grant_sources(self):
        records = {line.split("\t")[0]: line for line in
                   (DATA / "spheres_conscript.lst").read_text().splitlines()}
        grant = "ABILITY:Special Ability|AUTOMATIC|Spheres Martial Focus"
        for name in ("Conscript Combat Training", "Extra Combat Talent", "Martial Tradition (Manual)"):
            self.assertIn(grant, records[name])
        self.assertIn("TYPE:SpheresInternal.SpheresCombatTraining", records["Conscript Combat Training"])
        self.assertNotIn("SpheresCombatTraining", records["Extra Combat Talent"])
        custom = next(line for line in (DATA / "spheres_traditions.lst").read_text().splitlines()
                      if line.startswith("Custom Martial Tradition\t"))
        self.assertIn(grant, custom)
        focus = next(line for line in (DATA / "spheres_core.lst").read_text().splitlines()
                     if line.startswith("Spheres Martial Focus\t"))
        self.assertIn("DEFINE:SPHERES_MARTIAL_FOCUS_CAPACITY|1", focus)


if __name__ == "__main__":
    unittest.main()
