"""Offline catalog integrity; live controller evidence is pcgen_catalog.py."""
import json
import unittest
from spheres_catalog import inventory, MANIFEST
from spheres_catalog_lst import build, DATA, key, repeat_limit, text, PACKAGES
from spheres_catalog_source import Page


class CatalogTest(unittest.TestCase):
    def test_time_age_applies_only_delta_of_cumulative_adult_penalties(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_time_effects.lst'].splitlines()}
        ages = {'Young Adult': 0, 'Middle Age': -1, 'Old Age': -3, 'Venerable': -6}
        transitions = [key for key in rows if key.startswith('Time Effect - Age - ')]
        self.assertEqual(len(transitions), 12)
        for original, base in ages.items():
            for target, penalty in ages.items():
                if original == target:
                    continue
                row = rows['Time Effect - Age - ' + original + ' to ' + target]
                self.assertIn('TEMPBONUS:ANYPC|STAT|STR,DEX,CON|' + str(penalty - base), row)
                self.assertEqual(row.count('TEMPBONUS:'), 1)
                self.assertNotIn('TEMPVALUE:', row)
                self.assertNotIn('INT,WIS,CHA', row)
                self.assertIn('replace rather than combine', row)

    def test_time_reference_limits_do_not_apply_permanent_effects(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_power_time.lst'].splitlines()}
        expected = {
            'Age': 'AGE_CATEGORY_LIMIT|1+floor(SPHERES_CL_TIME/5)',
            'Time Zone': 'ZONE_GLOBE_RADIUS_MAX|10+5*floor(SPHERES_CL_TIME/2)',
            'Causality': 'CAUSALITY_DAMAGE_D8|floor(SPHERES_CL_TIME/2)',
            'Lingering Time': 'LINGER_ROUNDS|2',
            'After Image': 'min(50,20+5*floor(SPHERES_CL_TIME/3))',
            'Retroactive Preparation': 'VALUE_EXCLUSIVE|100*SPHERES_CL_TIME',
            'Fast Time': 'FAST_RADIUS|10+5*floor(SPHERES_CL_TIME/5)',
            'Stretch Time': 'STRETCH_ADDED_ROUNDS_MAX|SPHERES_CL_TIME',
            'Time Bubble': 'BUBBLE_DAMAGE_D8|floor(SPHERES_CL_TIME/2)',
            'Time Freeze': 'FREEZE_RADIUS|10+5*floor(SPHERES_CL_TIME/5)',
        }
        for name, formula in expected.items():
            self.assertIn(formula, rows['Time - ' + name])
            self.assertNotIn('BONUS:COMBAT', rows['Time - ' + name])
        self.assertIn('ZONE_WALL_CUBES_MAX|3+SPHERES_CL_TIME', rows['Time - Time Zone'])
        self.assertIn('AGE_RELEASED_MINUTES|SPHERES_CL_TIME', rows['Time - Age'])

    def test_timeline_bridge_separates_knowledge_and_spent_defenses(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_time_effects.lst'].splitlines()}
        for name, bonus in (('Knowledge', 'SKILL|TYPE.Knowledge'),
                            ('Single Attack Defense', 'COMBAT|AC'),
                            ('Single Save', 'SAVE|ALL')):
            row = rows['Time Effect - Timeline Bridge - ' + name]
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|floor(%CHOICE/2)|TYPE=Insight', row)
            self.assertEqual(row.count('TEMPBONUS:'), 1)
            self.assertNotIn('SKILLRANK', row)
        self.assertIn('untrained is resolved at the table', rows['Time Effect - Timeline Bridge - Knowledge'])

    def test_rapid_response_recipient_bonuses_are_competence(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_time_effects.lst'].splitlines()}
        self.assertIn('COMBAT|INITIATIVE|max(1,floor(%CHOICE/2))|TYPE=Competence',
                      rows['Time Effect - Rapid Response - Initiative'])
        for name, amount in (('Two Selections', 2), ('Three Selections', 4)):
            row = rows['Time Effect - Rapid Response - ' + name]
            self.assertIn('SAVE|Reflex|' + str(amount) + '|TYPE=Competence', row)
            self.assertEqual(row.count('TEMPBONUS:'), 1)
            self.assertNotIn('ABILITY:', row)

    def test_broken_time_penalizes_attacks_and_skills_only(self):
        row = next(line for line in self.files['spheres_time_effects.lst'].splitlines()
                   if line.startswith('Time Effect - Broken Time\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT|-floor(%CHOICE/2)', row)
        self.assertIn('TEMPBONUS:ANYPC|SKILL|ALL|-floor(%CHOICE/2)', row)
        self.assertEqual(row.count('TEMPBONUS:'), 2)
        self.assertIn('new free-action Will save each round', row)
        self.assertNotIn('|SAVE|', row)

    def test_time_effects_separate_dodge_movement_and_slow(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_time_effects.lst'].splitlines()}
        self.assertIn('COMBAT|TOHIT|1+floor(%CHOICE/10)', rows['Time Effect - Haste - Attack'])
        self.assertNotIn('TYPE=Dodge', rows['Time Effect - Haste - Attack'])
        self.assertEqual(rows['Time Effect - Haste - Dodge'].count('TYPE=Dodge'), 2)
        self.assertIn('SAVE|Reflex|-1-floor(%CHOICE/10)', rows['Time Effect - Slow - Penalties'])
        self.assertNotIn('SAVE|ALL', rows['Time Effect - Slow - Penalties'])
        self.assertIn('minimum 5 feet', rows['Time Effect - Slow - Penalties'])
        for mode in ('Walk', 'Climb', 'Swim', 'Fly', 'Burrow'):
            self.assertIn('MOVEADD|TYPE.' + mode + '|10+10*floor(%CHOICE/5)|TYPE=Enhancement', rows['Time Effect - Haste - ' + mode])
        self.assertIn('COMBAT|ATTACKS|1|TYPE=Enhancement', rows['Time Effect - Improved Haste - Full Attack'])
        self.assertIn('VAR|SPHERES_RECEIVED_IMPROVED_HASTE_AOO|1+floor(%CHOICE/5)', rows['Time Effect - Improved Haste - Attacks of Opportunity'])
        self.assertNotIn('COMBAT|ATTACKS', rows['Time Effect - Improved Haste - Attacks of Opportunity'])

    def test_divination_range_and_duration_use_sphere_caster_level(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_power_divination.lst'].splitlines()}
        self.assertIn('400+40*SPHERES_CL_DIVINATION,100+10*SPHERES_CL_DIVINATION', rows['Divination Sphere'])
        self.assertIn('DEFINE:SPHERES_DIVINATION_SENSE_HOURS|SPHERES_CL_DIVINATION', rows['Divination Sphere'])
        self.assertIn('BONUS:VAR|SPHERES_DIVINATION_GREATER_DIVINE|1', rows['Divination - Greater Divine'])
        self.assertIn('BONUS:VAR|SPHERES_DIVINATION_LINGER_ROUNDS|2', rows['Divination - Lingering Divination'])
        self.assertIn('DEFINE:SPHERES_DIVINATION_SHARED_TARGETS|2+floor(SPHERES_CL_DIVINATION/5)', rows['Divination - Shared Perception'])
        self.assertIn('DEFINE:SPHERES_DIVINATION_SHARED_RANGE|400+40*SPHERES_CL_DIVINATION', rows['Divination - Shared Perception'])
        self.assertIn('DEFINE:SPHERES_DIVINATION_VIEWING_DETECT_DC|20+SPHERES_CL_DIVINATION', rows['Divination - Viewing'])

    def test_explicit_repeat_maximum_precedes_multiple_times(self):
        self.assertEqual(repeat_limit({'text': 'You may take this talent multiple times, to a maximum of 5 times.'}), 5)
        self.assertEqual(repeat_limit({'text': 'You may take this talent multiple times.'}), 99)
        row = next(line for line in self.files['spheres_power_divination.lst'].splitlines()
                   if line.startswith('Divination - Divine Future\t'))
        self.assertIn('PREVARLT:SPHERES_DIVINATION_DIVINEFUTURE_COUNT,5', row)

    def test_divination_effects_use_current_not_original_prescience(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_divination_effects.lst'].splitlines()
                if not line.startswith('#')}
        self.assertEqual(len(rows), 19)
        sense = rows['Divination Effect - Prescience']
        self.assertIn('COMBAT|TOHIT|1+floor(%CHOICE/10)|TYPE=Insight', sense)
        self.assertNotIn('|CMB|', sense)
        self.assertIn('COMBAT|CMB|10+floor(%CHOICE/2)|TYPE=Insight',
                      rows['Divination Effect - Prescience - Dismissed Maneuver'])
        self.assertIn('Knowledge (Nature),Survival|1+floor(%CHOICE/5)', rows['Divination Effect - Nature Sense'])
        self.assertNotIn('TYPE=Insight', rows['Divination Effect - Nature Sense'])
        self.assertIn('SAVE|Reflex|2+floor(%CHOICE/10)', rows['Divination Effect - Foreshadow'])
        self.assertNotIn('COMBAT|AC', rows['Divination Effect - Foreshadow'])
        self.assertIn('TYPE=Dodge', rows['Divination Effect - Foreshadow - Dodge AC'])
        self.assertIn('TEMPLATE:spheres_divination_effects.lst', (DATA / 'spheres.pcc').read_text())

    def test_sensory_overload_penalty_is_conditional_and_save_specific(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_divination_effects.lst'].splitlines()}
        line = rows['Divination Effect - Sensory Overload - Mindless Target']
        self.assertIn('TEMPBONUS:ANYPC|SAVE|Fortitude,Will|-2', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('TEMPVALUE:', line)
        self.assertIn('unrelated saving throws do not suffer', line)
        self.assertIn('Does not make the recipient mindless', line)

    def test_discern_individual_is_insight_only_for_monster_lore(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_divination_effects.lst'].splitlines()}
        line = rows['Divination Effect - Discern Individual - Monster Lore']
        self.assertIn('|max(1,floor(%CHOICE/2))|TYPE=Insight', line)
        for skill in ('Arcana', 'Dungeoneering', 'Local', 'Nature', 'Planes', 'Religion'):
            self.assertIn('Knowledge (' + skill + ')', line)
        self.assertNotIn('Knowledge (History)', line)
        self.assertNotIn('SKILLRANK', line)
        self.assertIn('Disable for other Knowledge checks', line)

    def test_divine_future_requires_roll_result_not_caster_level(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_divination_effects.lst'].splitlines()}
        for target, kind in (('Attack', 'COMBAT|TOHIT'), ('Save', 'SAVE|ALL'),
                             ('Skill', 'SKILL|ALL'), ('Initiative', 'COMBAT|INITIATIVE'),
                             ('Maneuver', 'COMBAT|CMB')):
            line = rows['Divination Effect - Divine Future - ' + target]
            self.assertIn('TEMPBONUS:ANYPC|' + kind + '|%CHOICE|TYPE=Insight', line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('not caster level', line)
            self.assertIn('Disable immediately after', line)
            self.assertNotIn('COMBAT|DAMAGE', line)

    def test_divine_capability_only_applies_during_assessment(self):
        line = next(line for line in self.files['spheres_divination_effects.lst'].splitlines()
                    if line.startswith('Divination Effect - Divine Capability - Assessed Target\t'))
        self.assertIn('TEMPBONUS:ANYPC|SKILL|ALL|floor(%CHOICE/2)|TYPE=Circumstance', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertIn('Other skill checks and other targets do not benefit', line)
        self.assertIn('creature successfully divined', line)

    def test_conditional_divination_perception_benefits_are_not_permanent(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_divination_effects.lst'].splitlines()}
        ghost = rows['Divination Effect - Ghost Sight - Invisible or Ethereal Target']
        self.assertIn('TEMPBONUS:ANYPC|SKILL|Perception|%CHOICE', ghost)
        self.assertEqual(ghost.count('TEMPBONUS:'), 1)
        unhooded = rows['Divination Effect - Unhooded Sight - Disbelieve Illusion']
        self.assertIn('TEMPBONUS:ANYPC|SAVE|Will|max(1,floor(%CHOICE/2))', unhooded)
        self.assertIn('TEMPBONUS:ANYPC|VAR|SPHERES_MAGIC_SKILL_BONUS|max(1,floor(%CHOICE/2))', unhooded)
        self.assertNotIn('SAVE|ALL', unhooded)
        self.assertIn('Disable immediately afterward', unhooded)

    def test_snipers_eye_offsets_only_eligible_penalties(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_divination_effects.lst'].splitlines()}
        for target, kind, cap in (('Distance Perception', 'SKILL|Perception', 'caster level'),
                                  ('Ranged Attack Penalties', 'COMBAT|TOHIT', 'floor(caster level/2)')):
            line = rows["Divination Effect - Sniper's Eye - " + target]
            self.assertIn('TEMPBONUS:ANYPC|' + kind + '|%CHOICE', line)
            self.assertIn('TEMPVALUE:MIN=0', line)
            self.assertIn('penalty magnitude and ' + cap, line)
            self.assertIn('never produce a net bonus', line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)

    def test_swords_discharge_is_confirmation_only(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        line = rows['Fate Effect - Swords - Discharged Confirmation Only']
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT|max(1,floor(%CHOICE/2))', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertIn('ordinary attacks do not benefit', line)
        self.assertIn('automatically threatens a critical hit', line)
        self.assertIn('one-minute', line)

    def test_motif_references_do_not_apply_permanent_caster_defenses(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_power_fate.lst'].splitlines()}
        expected = {
            'Cups': ['CUPS_RETAINED_D20|2+floor(SPHERES_CL_FATE/7)',
                     'CUPS_DISCHARGE_MINUTES|SPHERES_CL_FATE'],
            'Pentacles': ['PENTACLES_REROLLS|1+floor(SPHERES_CL_FATE/10)',
                          'PENTACLES_DISCHARGE_MINUTES|SPHERES_CL_FATE'],
            'Swords': ['SWORDS_CONFIRM_BONUS|max(1,floor(SPHERES_CL_FATE/2))',
                       'SWORDS_DISCHARGE_MINUTES|1'],
            'Wands': ['WANDS_DISCHARGE_MINUTES|SPHERES_CL_FATE'],
            'The Empress': ['EMPRESS_INITIAL_POINTS|1+SPHERES_CL_FATE',
                            'EMPRESS_SPEND_LIMIT|max(1,floor(SPHERES_CL_FATE/5))'],
            'The Wheel': ['WHEEL_D4_COUNT|1+floor(SPHERES_CL_FATE/10)',
                          'WHEEL_BONUS_PER_RESULT|1+floor(SPHERES_CL_FATE/10)'],
            'The Tower': ['TOWER_BYPASS|5+floor(SPHERES_CL_FATE/4)', 'TOWER_DISCHARGE_D4|SPHERES_CL_FATE'],
            'The Queen': ['QUEEN_FEAR_ROUND_REDUCTION|2+floor(SPHERES_CL_FATE/5)',
                          'QUEEN_DISCHARGE_DAMAGE_REDUCTION|max(1,floor(SPHERES_CL_FATE/2))'],
            'The Page': ['PAGE_MORALE_EXTRA_ROUNDS|1+floor(SPHERES_CL_FATE/10)'],
            'The Lovers': ['LOVERS_MAX_SAVE_BONUS|2+floor(SPHERES_CL_FATE/5)'],
        }
        for name, formulas in expected.items():
            line = rows['Fate - ' + name]
            for formula in formulas:
                self.assertIn('DEFINE:SPHERES_FATE_' + formula, line)
            self.assertNotIn('\tDR:', line)
            self.assertNotIn('\tBONUS:SAVE', line)

    def test_knight_only_offsets_condition_initiative_penalties(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The Knight - Condition Initiative Penalties\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|INITIATIVE|%CHOICE', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertIn('TEMPVALUE:MIN=0', line)
        self.assertIn('Keep the original conditions active', line)
        self.assertIn('Does not cancel other initiative penalties', line)

    def test_lovers_requires_capped_adjacency_not_caster_level(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The Lovers - Adjacent Allies\t'))
        self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|%CHOICE|TYPE=Insight', line)
        self.assertIn('TEMPVALUE:MIN=0', line)
        self.assertIn('lesser of adjacent ally count', line)
        self.assertIn('2 + floor(caster level/5)', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)

    def test_page_discharge_doubles_existing_morale_not_caster_level(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target in ('Attack', 'Damage', 'Save', 'Skill', 'Initiative'):
            line = rows['Fate Effect - The Page - Discharged Morale - ' + target]
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('|2*%CHOICE|TYPE=Morale', line)
            self.assertNotIn('TYPE=Morale.STACK', line)
            self.assertIn('not caster level', line)
            self.assertIn('Do not use without an existing', line)

    def test_emperor_discharge_excludes_self_imposed_penalty_bonus(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target in ('Attack', 'Damage', 'Save', 'Skill', 'Initiative'):
            line = rows['Fate Effect - The Emperor - Discharged Insight - ' + target]
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('|%CHOICE|TYPE=Insight', line)
            self.assertIn('this record does not cancel it', line)
            self.assertIn('grant no insight bonus', line)

    def test_emperor_reduction_does_not_grant_unconditional_insight(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target in ('Attack', 'Damage', 'Save', 'Skill', 'Initiative'):
            line = rows['Fate Effect - The Emperor - Penalty Reduction - ' + target]
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('|%CHOICE', line)
            self.assertNotIn('TYPE=Insight', line)
            self.assertIn('magnitude minus 1', line)
            self.assertIn('Leave the original penalty active', line)

    def test_wheel_ongoing_groups_use_aggregated_insight_bonus(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for category, count in (('1 - Attack and Damage', 1), ('2 - Saves', 1),
                                ('3 - Initiative and Skills', 2), ('4 - Concentration and Maneuvers', 3)):
            line = rows['Fate Effect - The Wheel - Ongoing - ' + category]
            self.assertEqual(line.count('TEMPBONUS:'), count)
            self.assertEqual(line.count('|%CHOICE|TYPE=Insight'), count)
            self.assertIn('Apply each category at most once', line)
            self.assertNotIn('TYPE=Insight.STACK', line)

    def test_wheel_discharge_uses_dice_sum_and_excludes_damage(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target in ('Attack', 'Save', 'Skill', 'Initiative', 'Concentration'):
            line = rows['Fate Effect - The Wheel - Discharged - ' + target]
            self.assertIn('|2*%CHOICE|TYPE=Insight', line)
            self.assertIn('SUM of the original d4 results', line)
            self.assertNotIn('COMBAT|DAMAGE', line)
            self.assertNotIn('COMBAT|CMD', line)
            self.assertEqual(line.count('TEMPBONUS:'), 2 if target == 'Concentration' else 1)

    def test_king_concentration_supports_spells_and_spheres(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The King\t'))
        self.assertIn('CONCENTRATION|ALLSPELLS|1+floor(%CHOICE/10)|TYPE=Insight', line)
        self.assertIn('VAR|SPHERES_CONCENTRATION_CHECK|1+floor(%CHOICE/10)|TYPE=Insight', line)
        self.assertEqual(line.count('TEMPBONUS:'), 2)
        self.assertNotIn('VAR|SPHERES_CASTER_LEVEL', line)

    def test_perfect_accelerated_diplomacy_is_separate_and_conditional(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        line = rows['Fate Effect - Perfect - CHA - One Round Diplomacy']
        self.assertIn('TEMPBONUS:ANYPC|SKILL|Diplomacy|-10', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('TEMPVALUE:', line)
        self.assertIn('Disable immediately', line)
        self.assertNotIn('Diplomacy|-10', rows['Fate Effect - Perfect - CHA'])

    def test_fate_range_and_reference_values_use_sphere_caster_level(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_power_fate.lst'].splitlines()}
        base = rows['Fate Sphere']
        self.assertIn('DEFINE:SPHERES_FATE_UNDO_HARM_MAX_HEALING|if(SPHERES_FATE_UNDOHARM_COUNT,5+SPHERES_CL_FATE,0)', base)
        self.assertIn('DEFINE:SPHERES_FATE_UNDO_HARM_CONDITIONS|if(SPHERES_FATE_UNDOHARM_COUNT>=2,1+floor(SPHERES_CL_FATE/10),0)', base)
        self.assertNotIn('DEFINE:', rows['Fate - Undo Harm'])
        self.assertIn('DEFINE:SPHERES_FATE_RESOUNDINGWORD_COUNT|0', base)
        self.assertIn('DEFINE:SPHERES_FATE_CONSECRATION_RADIUS|20+5*floor(SPHERES_CL_FATE/5)', base)
        self.assertIn('400+40*SPHERES_CL_FATE', base)
        self.assertIn('100+10*SPHERES_CL_FATE', base)
        self.assertIn('25+5*floor(SPHERES_CL_FATE/2)', base)
        ranged = rows['Fate - Resounding Word']
        self.assertIn('PREVARLT:SPHERES_FATE_RESOUNDINGWORD_COUNT,2', ranged)
        self.assertNotIn('DEFINE:', ranged)
        for name in ('Echoing Word', 'Bargain', 'Harm'):
            self.assertIn('max(1,floor(SPHERES_CL_FATE/2))', rows['Fate - ' + name])
        self.assertIn('1+floor(SPHERES_CL_FATE/5)', rows['Fate - Consequences'])

    def test_malice_uses_current_total_not_level_or_permanent_bonus(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - Malice - Accumulated Bonus\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT,DAMAGE|%CHOICE', line)
        self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|%CHOICE', line)
        self.assertEqual(line.count('TEMPBONUS:'), 2)
        self.assertNotIn('TYPE=Luck', line)
        self.assertIn('not caster level', line)
        self.assertIn('at most once per round', line)
        self.assertIn('up to the casting ability modifier', line)
        self.assertIn('do not add copies', line)

    def test_enmity_penalty_only_applies_to_its_save_and_strongest_aura(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for strength, penalty in (('Strong', 1), ('Overwhelming', 2)):
            line = rows['Fate Effect - Enmity - ' + strength + ' Opposing Aura']
            self.assertIn('TEMPBONUS:ANYPC|SAVE|Will|-' + str(penalty), line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('Use only the strongest opposing aura', line)
            self.assertIn('Remove immediately after the save', line)
            self.assertNotIn('TEMPVALUE:', line)

    def test_tug_fate_requires_actual_ten_and_separates_luck_from_penalty(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Save', 'SAVE|ALL'),
                              ('Skill', 'SKILL|ALL'), ('Initiative', 'COMBAT|INITIATIVE')):
            for mode, formula in (('Bonus', '10+floor(%CHOICE/2)|TYPE=Luck'),
                                  ('Penalty', '-10-floor(%CHOICE/2)')):
                line = rows['Fate Effect - Tug Fate - ' + mode + ' - ' + target]
                self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|' + formula, line)
                self.assertEqual(line.count('TEMPBONUS:'), 1)
                self.assertIn('Does not apply when taking 10', line)
                self.assertIn('then remove immediately', line)
                if mode == 'Penalty':
                    self.assertNotIn('TYPE=Luck', line)

    def test_pain_penalizes_mental_skills_without_damage_or_rank_changes(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - Pain\t'))
        self.assertIn('TEMPBONUS:ANYPC|SKILL|STAT.INT,STAT.WIS,STAT.CHA|-4', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('SKILLRANK', line)
        self.assertNotIn('TEMPVALUE:', line)
        self.assertIn('magic skill check required to cast', line)

    def test_hanged_man_discharge_uses_damage_paid_and_single_roll(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Save', 'SAVE|ALL'),
                              ('Combat Maneuver', 'COMBAT|CMB'), ('Skill', 'SKILL|ALL'),
                              ('Initiative', 'COMBAT|INITIATIVE')):
            line = rows['Fate Effect - The Hanged Man - Discharged - ' + target]
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|max(1,floor(%CHOICE/2))|TYPE=Insight', line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('lesser of recipient Hit Dice and caster level', line)
            self.assertIn('Remove immediately after the roll', line)
            self.assertNotIn('TEMPBONUS:ANYPC|STAT|', line)
            self.assertNotIn('TEMPBONUS:ANYPC|HP|', line)

    def test_borrow_trouble_is_post_reroll_and_category_scoped(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for category, bonus in (('Attack Rolls', 'COMBAT|TOHIT'),
                                ('Saving Throws', 'SAVE|ALL'),
                                ('Skill Checks', 'SKILL|ALL'),
                                ('Ability Checks', 'COMBAT|INITIATIVE')):
            line = rows['Fate Effect - Borrow Trouble - ' + category]
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|4\t', line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertNotIn('TYPE=Luck', line)
            self.assertNotIn('TEMPVALUE:', line)
            self.assertIn('AFTER the Borrow Trouble reroll', line)
            self.assertIn('initial reroll does not end', line)
            self.assertIn('Remove after a subsequent success', line)

    def test_perfect_maneuver_bonus_requires_independent_safe_maneuver(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for maneuver in ('BullRush', 'Overrun', 'Trip'):
            line = rows['Fate Effect - Perfect - STR - ' + maneuver + ' Already Safe']
            self.assertIn('TEMPBONUS:ANYPC|VAR|CMB_' + maneuver + '|2+floor(%CHOICE/4)', line)
            self.assertIn('independently of Perfect', line)
            self.assertNotIn('CMD_', line)
            self.assertNotIn('ABILITY:', line)

    def test_perfect_preserves_ability_scores_and_scopes_training(self):
        rows = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for stat in ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'):
            line = rows['Fate Effect - Perfect - ' + stat]
            self.assertIn('TEMPBONUS:ANYPC|SKILL|STAT.' + stat + '|1', line)
            self.assertNotIn('TEMPBONUS:ANYPC|STAT|', line)
            self.assertNotIn('SKILLRANK', line)
        self.assertIn('COMBAT|INITIATIVE|1\t', rows['Fate Effect - Perfect - DEX'])
        self.assertIn('MOVEADD|TYPE.All|10+5*floor(%CHOICE/5)', rows['Fate Effect - Perfect - DEX'])
        self.assertNotIn('TYPE=Enhancement', rows['Fate Effect - Perfect - DEX'])
        self.assertIn('COMBAT|INITIATIVE|1+floor(%CHOICE/5)', rows['Fate Effect - Perfect - WIS'])
        trained = rows['Fate Effect - Perfect - INT - Trained Check Only']
        self.assertIn('SKILL|ALL|2+floor(%CHOICE/5)', trained)
        self.assertIn('Do not enable for untrained skills', trained)
        self.assertNotIn('SKILLRANK', trained)

    def test_villainy_bonus_is_paid_target_scoped_and_untyped(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - Villainy - Paid Ally Bonus\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT,DAMAGE|1+floor(%CHOICE/3)', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('TYPE=Insight', line)
        self.assertIn('additional spell point', line)
        self.assertIn('weapons only', line)
        self.assertIn('other targets', line)

    def test_sun_discharge_uses_signed_casting_modifier_not_level(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The Sun - Discharged\t'))
        for bonus in ('COMBAT|AC', 'SAVE|ALL'):
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|%CHOICE|TYPE=Insight', line)
        self.assertEqual(line.count('TEMPBONUS:'), 2)
        self.assertIn('TEMPVALUE:MIN=-10|MAX=100', line)
        self.assertIn('not caster level', line)
        self.assertIn('Remove after one round', line)
        self.assertNotIn('HP|', line)

    def test_fool_penalty_decreases_without_becoming_a_bonus(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The Fool\t'))
        self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|-max(0,3-floor(%CHOICE/10))', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('TYPE=Insight', line)
        self.assertIn('same penalty', line)
        self.assertIn('then remove', line)

    def test_arcana_received_bonuses_are_untyped_and_stat_scoped(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for name, bonus in (
                ('Cups', 'SKILL|STAT.INT,STAT.WIS,STAT.CHA|2+floor(%CHOICE/10)'),
                ('Swords', 'COMBAT|TOHIT|1+floor(%CHOICE/10)'),
                ('Wands', 'COMBAT|INITIATIVE|2+floor(%CHOICE/10)'),
                *(("Pentacles - " + save, 'SAVE|' + save + '|1+floor(%CHOICE/10)')
                  for save in ('Fortitude', 'Reflex', 'Will'))):
            line = records['Fate Effect - ' + name]
            self.assertIn('TEMPBONUS:ANYPC|' + bonus, line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertNotIn('TYPE=Insight', line)
            self.assertNotIn('SKILLRANK', line)
            self.assertIn('Remove when expired or discharged', line)
            self.assertIn('Do not apply when attached as an arcana', line)

    def test_empress_spending_and_discharge_use_points_not_caster_level(self):
        lines = [line for line in self.files['spheres_fate_effects.lst'].splitlines()
                 if line.startswith('Fate Effect - The Empress - ')]
        self.assertEqual(len(lines), 9)
        for line in lines:
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('TYPE=Insight', line)
            self.assertIn('NOT caster level', line)
            self.assertIn('cannot exceed remaining points', line)
            self.assertIn('single eligible roll', line)
            if ' - Discharge - ' in line:
                self.assertIn('|5+floor(%CHOICE/4)|TYPE=Insight', line)
                self.assertIn('TEMPVALUE:MIN=0', line)
                self.assertNotIn('|DAMAGE|', line)
            else:
                self.assertIn('|%CHOICE|TYPE=Insight', line)
                self.assertIn('TEMPVALUE:MIN=1', line)

    def test_hermit_self_aid_is_scoped_and_replaces_normal_aid(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Defense', 'COMBAT|AC'), ('Skill', 'SKILL|ALL')):
            line = records['Fate Effect - The Hermit - Self Aid - ' + target]
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|3+floor(%CHOICE/5)', line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertNotIn('TYPE=Insight', line)
            self.assertIn('replaces the normal aid bonus', line)
            self.assertIn('Do not combine with aid from another creature', line)
            self.assertIn('Disable immediately', line)
            self.assertNotIn('ABILITY:', line)

    def test_high_priestess_discharge_is_received_one_round_insight(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The High Priestess - Discharged\t'))
        self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|floor(%CHOICE/2)|TYPE=Insight', line)
        self.assertIn('TEMPVALUE:MIN=5|MAX=100', line)
        self.assertIn('Remove after one round', line)
        self.assertIn('ally within 30 feet', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('ABILITY:', line)

    def test_magician_separates_opportunity_attacks_and_untrained_skills(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_fate_effects.lst'].splitlines()}
        for target, bonus in (('Attacks of Opportunity', 'COMBAT|TOHIT'), ('Untrained Skills', 'SKILL|ALL')):
            line = records['Fate Effect - The Magician - ' + target]
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|2+floor(%CHOICE/5)|TYPE=Insight', line)
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('Enable ONLY', line)
            self.assertIn('Disable immediately', line)
            self.assertNotIn('SKILLRANK', line)
            self.assertNotIn('|DAMAGE|', line)

    def test_world_bonus_requires_take_check_context(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - The World - Conditional Skills\t'))
        self.assertIn('TEMPBONUS:ANYPC|SKILL|ALL|2+floor(%CHOICE/5)|TYPE=Insight', line)
        self.assertIn('Enable ONLY', line)
        self.assertIn('Disable immediately', line)
        self.assertNotIn('SKILLRANK', line)
        self.assertNotIn('|STAT|', line)

    def test_received_fate_effects_preserve_types_and_context(self):
        lines = self.files['spheres_fate_effects.lst'].splitlines()[1:]
        self.assertEqual(len(lines), 104)
        self.assertIn('TEMPLATE:spheres_fate_effects.lst', (DATA / 'spheres.pcc').read_text())
        self.assertIn('COMBAT|TOHIT,INITIATIVE|1|TYPE=Luck', lines[0])
        self.assertNotIn('TEMPVALUE:', lines[0])
        for kind, line in zip(('Sacred', 'Profane'), lines[1:]):
            self.assertIn('COMBAT|TOHIT,AC|1+floor(%CHOICE/10)|TYPE=' + kind, line)
            self.assertIn('SAVE|ALL|1+floor(%CHOICE/10)|TYPE=' + kind, line)
            self.assertIn('Enable ONLY', line)
            self.assertIn('Disable immediately', line)
            self.assertNotIn('IMMUNE:', line)

    def test_received_fate_penalties_preserve_roll_categories(self):
        lines = self.files['spheres_fate_effects.lst'].splitlines()[1:]
        enemy = lines[3]
        for bonus in ('COMBAT|TOHIT,INITIATIVE', 'SKILL|ALL', 'SAVE|ALL'):
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|-%CHOICE', enemy)
        self.assertIn('NOT caster level', enemy)
        self.assertNotIn('TYPE=Luck', enemy)
        luck = [line for line in lines if line.startswith('Fate Effect - Borrow Luck - ')]
        self.assertEqual(len(luck), 4)
        for line, bonus in zip(luck, ('COMBAT|TOHIT', 'SAVE|ALL', 'SKILL|ALL', 'COMBAT|INITIATIVE')):
            self.assertEqual(line.count('TEMPBONUS:'), 1)
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|-4', line)
            self.assertNotIn('TEMPVALUE:', line)
            self.assertNotIn('|STAT|', line)
            self.assertIn('Apply AFTER', line)
            self.assertIn('do not end it', line)

    def test_received_fate_motifs_are_conditional_insight_bonuses(self):
        lines = [line for line in self.files['spheres_fate_effects.lst'].splitlines()
                 if line.startswith(('Fate Effect - The Star - Conditional\t', 'Fate Effect - The Chariot - Conditional\t'))]
        for line, formula in zip(lines, ('COMBAT|AC|2+floor(%CHOICE/5)', 'SAVE|ALL|2+floor(%CHOICE/10)')):
            self.assertIn('TEMPBONUS:ANYPC|' + formula + '|TYPE=Insight', line)
            self.assertIn('Enable ONLY', line)
            self.assertIn('Disable immediately', line)
            self.assertNotIn('IMMUNE:', line)

    def test_strength_motif_targets_maneuvers_and_strength_skills(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - Strength\t'))
        self.assertTrue(line.startswith('Fate Effect - Strength\t'))
        for bonus in ('COMBAT|CMB,CMD', 'SKILL|STAT.STR'):
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|2+floor(%CHOICE/4)|TYPE=Insight', line)
        self.assertNotIn('|STAT|', line)
        self.assertNotIn('|TOHIT|', line)

    def test_mind_defense_motifs_distinguish_aura_recipient(self):
        lines = self.files['spheres_fate_effects.lst'].splitlines()
        for name, divisor in (('The Moon', 10), ('The Hierophant', 5)):
            line = next(line for line in lines if line.startswith('Fate Effect - ' + name + ' - Conditional\t'))
            self.assertIn('SAVE|ALL|2+floor(%CHOICE/' + str(divisor) + ')|TYPE=Insight', line)
            self.assertIn('against mind-affecting effects', line)
            self.assertIn('Disable immediately', line)
            self.assertNotIn('IMMUNE:', line)
            if name == 'The Hierophant':
                self.assertIn('30 feet', line)
                self.assertIn('OTHER than yourself', line)

    def test_hanged_man_has_fixed_penalty_and_two_scaling_saves(self):
        lines = [line for line in self.files['spheres_fate_effects.lst'].splitlines()
                 if line.startswith('Fate Effect - The Hanged Man - Penalize ')]
        self.assertEqual(len(lines), 3)
        for penalty, line in zip(('Fortitude', 'Reflex', 'Will'), lines):
            other = ','.join(save for save in ('Fortitude', 'Reflex', 'Will') if save != penalty)
            self.assertIn('TEMPBONUS:ANYPC|SAVE|' + penalty + '|-2\t', line)
            self.assertIn('TEMPBONUS:ANYPC|SAVE|' + other + '|2+floor(%CHOICE/10)|TYPE=Insight', line)
            self.assertIn('Use only ONE', line)

    def test_pain_penalizes_mental_skills_without_ability_damage(self):
        line = next(line for line in self.files['spheres_fate_effects.lst'].splitlines()
                    if line.startswith('Fate Effect - Pain - Mental Skills\t'))
        self.assertTrue(line.startswith('Fate Effect - Pain - Mental Skills\t'))
        self.assertIn('TEMPBONUS:ANYPC|SKILL|STAT.INT,STAT.WIS,STAT.CHA|-4', line)
        self.assertEqual(line.count('TEMPBONUS:'), 1)
        self.assertNotIn('|STAT|', line)
        self.assertNotIn('TEMPVALUE:', line)

    def test_targeted_fate_combat_bonuses_remain_conditional(self):
        lines = [line for line in self.files['spheres_fate_effects.lst'].splitlines()
                 if line.startswith(('Fate Effect - Justice - Conditional\t',
                                     'Fate Effect - The Devil - Discharged - Conditional\t'))]
        self.assertEqual(len(lines), 2)
        for line, stats, divisor in zip(lines, ('TOHIT,DAMAGE', 'TOHIT,AC'), (5, 4)):
            self.assertIn('TEMPBONUS:ANYPC|COMBAT|' + stats + '|2+floor(%CHOICE/' + str(divisor) + ')|TYPE=Insight', line)
            self.assertIn('Enable ONLY', line)
            self.assertIn('Disable immediately for other targets', line)
        self.assertIn('one round after that damage', lines[0])
        self.assertIn('after discharge', lines[1])

    def test_energy_resistance_is_received_typed_and_energy_specific(self):
        lines = self.files['spheres_protection_effects.lst'].splitlines()[-5:]
        for energy, line in zip(('Acid', 'Cold', 'Electricity', 'Fire', 'Sonic'), lines):
            self.assertTrue(line.startswith('Protection Effect - Energy Resistance - ' + energy + '\t'))
            self.assertIn('TEMPBONUS:ANYPC|VAR|' + energy + 'ResistanceBonus|10+%CHOICE|TYPE=Resistance', line)
            self.assertNotIn('\tBONUS:', line)
            self.assertNotIn('|SAVE|', line)
            self.assertIn('Does not implement the area ward', line)

    def test_mass_aegis_counts_additional_targets_and_reduced_duration(self):
        line = next(line for line in self.files['spheres_power_protection.lst'].splitlines()
                    if line.startswith('Protection - Mass Aegis\t'))
        self.assertIn('MASS_ADDITIONAL_TARGETS|max(1,floor(SPHERES_CL_PROTECTION/2))', line)
        self.assertIn('MASS_DURATION_MINUTES|10*SPHERES_CL_PROTECTION', line)
        self.assertNotIn('SPHERES_PROTECTION_WARD_CL', line)

    def test_helping_hand_is_scoped_to_rerolled_skill_check(self):
        line = next(line for line in self.files['spheres_protection_effects.lst'].splitlines()
                    if line.startswith('Protection Effect - Helping Hand - Skill Reroll Only\t'))
        self.assertIn('TEMPBONUS:ANYPC|SKILL|ALL|max(1,floor(%CHOICE/4))|TYPE=Circumstance', line)
        self.assertIn('Disable immediately', line)
        self.assertIn('even if worse', line)
        self.assertNotIn('|STAT|', line)
        self.assertNotIn('|SAVE|', line)

    def test_aegis_reference_values_do_not_grant_caster_defenses(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_protection.lst'].splitlines()}
        for name, formula in (
                ('Ablating', 'min(50,20+5*floor(SPHERES_CL_PROTECTION/3))'),
                ('Ray Deflection', 'min(50,20+5*floor(SPHERES_CL_PROTECTION/5))'),
                ('Painful Aegis', 'max(1,floor(SPHERES_CL_PROTECTION/2))')):
            line = records['Protection - ' + name]
            self.assertIn(formula, line)
            self.assertNotIn('BONUS:COMBAT', line)
            self.assertNotIn('SPHERES_PROTECTION_WARD_CL', line)

    def test_protection_distinguishes_ward_and_aegis_range_and_duration(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_protection.lst'].splitlines()}
        base = records['Protection Sphere']
        self.assertIn('WARD_DURATION_ROUNDS|SPHERES_PROTECTION_WARD_CL*if(SPHERES_PROTECTION_ENDURING,10,1)', base)
        self.assertIn('AEGIS_DURATION_HOURS|SPHERES_CL_PROTECTION', base)
        for kind, cl in (('WARD', 'SPHERES_PROTECTION_WARD_CL'), ('AEGIS', 'SPHERES_CL_PROTECTION')):
            formula = next(tag for tag in base.split('\t') if tag.startswith('DEFINE:SPHERES_PROTECTION_' + kind + '_RANGE_FEET|'))
            self.assertIn('400+40*' + cl, formula)
            self.assertIn('100+10*' + cl, formula)
            self.assertIn('25+5*floor(' + cl + '/2)', formula)
        self.assertIn('BONUS:VAR|SPHERES_PROTECTION_ENDURING|1', records['Protection - Enduring Protection'])

    def test_durable_barrier_reduces_barrier_damage_not_caster_damage(self):
        line = next(line for line in self.files['spheres_power_protection.lst'].splitlines()
                    if line.startswith('Protection - Durable Barrier\t'))
        self.assertIn('DEFINE:SPHERES_PROTECTION_BARRIER_DAMAGE_REDUCTION|max(1,floor(SPHERES_PROTECTION_WARD_CL/2))', line)
        self.assertNotIn('\tDR:', line)
        self.assertNotIn('BONUS:HP', line)

    def test_barrier_values_use_ward_specific_caster_level(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_protection.lst'].splitlines()}
        for key in ('Protection Sphere', 'Protection - Greater Barrier', 'Protection - Buttressing', 'Protection - Shaped Ward'):
            self.assertIn('SPHERES_PROTECTION_WARD_CL', records[key])
            self.assertNotIn('BONUS:HP', records[key])
        self.assertIn('BARRIER_BREAK_DC|15+floor(SPHERES_PROTECTION_WARD_CL/2)', records['Protection Sphere'])
        self.assertIn('GREATER_BARRIER_HP|10*SPHERES_PROTECTION_WARD_CL', records['Protection - Greater Barrier'])

    @classmethod
    def setUpClass(cls):
        cls.rows = inventory()
        cls.files, cls.review = build()

    def test_pinned_inventory(self):
        self.assertEqual(self.rows, json.loads(MANIFEST.read_text()))
        self.assertEqual(len(self.rows), 53)
        self.assertEqual(sum(len(r['talents']) for r in self.rows), 2330)
        self.assertEqual(sum(r['system'] == 'power' for r in self.rows), 26)

    def test_received_enhancements_use_native_temporary_bonuses(self):
        from spheres_enhancement_effects import skills, effect_key
        lines = [line for line in self.files['spheres_enhancement_effects.lst'].splitlines()
                 if not line.startswith('#')]
        self.assertEqual(len(lines), 21 + len(skills()))
        self.assertEqual(len(set(line.split('\t')[0] for line in lines)), len(lines))
        for line, stat in zip(lines, ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA')):
            self.assertIn('TEMPBONUS:ANYPC|STAT|' + stat + '|2+2*floor(%CHOICE/7)|TYPE=Enhancement', line)
            self.assertIn('TEMPVALUE:MIN=1|MAX=100', line)
            self.assertNotIn('\tBONUS:', line)
            self.assertNotIn('SPHERES_CL_', line)
            self.assertNotIn('PREABILITY:', line)
        self.assertIn('TEMPLATE:spheres_enhancement_effects.lst', (DATA / 'spheres.pcc').read_text())
        by_key = {line.split('\t')[0]: line for line in lines}
        for save in ('Fortitude', 'Reflex', 'Will'):
            line = by_key[effect_key('Staunch Resistance', save)]
            self.assertIn('TEMPBONUS:ANYPC|SAVE|' + save + '|2+floor(%CHOICE/5)', line)
            self.assertNotIn('TYPE=Resistance', line)
        for skill in skills():
            self.assertIn('TEMPBONUS:ANYPC|SKILL|' + skill + '|5+floor(%CHOICE/4)|TYPE=Enhancement',
                          by_key[effect_key('Enhance Focus', skill)])
        self.assertIn('Craft (Mechanical)', skills())
        self.assertFalse(any(':' in skill for skill in skills()))
        reflexes = by_key['Enhancement Effect - Superior Reflexes']
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|INITIATIVE|1+floor((%CHOICE-1)/4)', reflexes)
        self.assertIn('TEMPBONUS:ANYPC|VAR|SPHERES_RECEIVED_SUPERIOR_REFLEXES_AOO|1+floor((%CHOICE-1)/4)', reflexes)
        self.assertNotIn('ABILITY:', reflexes)

    def test_spectral_armor_save_effect_is_conditional_and_circumstance(self):
        line = next(line for line in self.files['spheres_enhancement_effects.lst'].splitlines()
                    if line.startswith('Enhancement Effect - Spectral Enhancement - Conditional Saves\t'))
        self.assertTrue(line.startswith('Enhancement Effect - Spectral Enhancement - Conditional Saves\t'))
        self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|2+floor(%CHOICE/5)|TYPE=Circumstance', line)
        self.assertIn('Disable immediately', line)
        self.assertIn('additional spell point paid', line)
        self.assertNotIn('|COMBAT|', line)

    def test_cripple_penalizes_rolls_not_scores_or_damage(self):
        line = self.files['spheres_enhancement_effects.lst'].splitlines()[-1]
        self.assertTrue(line.startswith('Enhancement Effect - Cripple\t'))
        for bonus in ('COMBAT|TOHIT,INITIATIVE', 'SAVE|ALL', 'SKILL|ALL'):
            self.assertIn('TEMPBONUS:ANYPC|' + bonus + '|-2-floor(%CHOICE/5)', line)
        self.assertNotIn('|STAT|', line)
        self.assertNotIn('DAMAGE', line)
        self.assertIn('other ability checks at the table', line)

    def test_alter_movement_does_not_grant_movement_modes(self):
        lines = self.files['spheres_enhancement_effects.lst'].splitlines()
        for movement in ('Walk', 'Climb', 'Swim', 'Fly', 'Burrow'):
            line = next(line for line in lines if line.startswith('Enhancement Effect - Alter Movement - ' + movement + '\t'))
            self.assertIn('TEMPBONUS:ANYPC|MOVEADD|TYPE.' + movement + '|10+10*floor(%CHOICE/5)|TYPE=Enhancement', line)
            self.assertNotIn('\tMOVE:', line)
        conditional = next(line for line in lines if line.startswith('Enhancement Effect - Alter Movement - Conditional Skills\t'))
        self.assertIn('Enable ONLY', conditional)
        self.assertIn('Disable immediately', conditional)

    def test_lighten_cmd_is_explicitly_conditional(self):
        lines = self.files['spheres_enhancement_effects.lst'].splitlines()
        for weight, penalty in (('Half Weight', 2), ('Weightless or Floating', 4)):
            line = next(line for line in lines if line.startswith('Enhancement Effect - Lighten - ' + weight + ' - Conditional CMD\t'))
            self.assertIn('TEMPBONUS:ANYPC|COMBAT|CMD|-' + str(penalty), line)
            self.assertIn('bull rush, drag, or reposition', line)
            self.assertIn('Choose only one', line)
            self.assertNotIn('|STAT|', line)
            self.assertNotIn('|AC|', line)

    def test_lighten_levitation_uses_attack_count_not_caster_level(self):
        line = next(line for line in self.files['spheres_enhancement_effects.lst'].splitlines()
                    if line.startswith('Enhancement Effect - Lighten - Levitating Attack\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT|-%CHOICE', line)
        self.assertIn('TEMPVALUE:MIN=1|MAX=5|', line)
        self.assertIn('full-round action', line)
        self.assertIn('Disable for nonweapon attacks', line)
        self.assertNotIn('|DAMAGE|', line)

    def test_received_protection_uses_ultimate_resistance_progression(self):
        lines = self.files['spheres_protection_effects.lst'].splitlines()[1:]
        self.assertEqual(len(lines), 24)
        self.assertIn('TEMPLATE:spheres_protection_effects.lst', (DATA / 'spheres.pcc').read_text())
        expected = (
            'COMBAT|AC|1+floor(%CHOICE/5)|TYPE=Deflection',
            'COMBAT|AC|3+floor(%CHOICE/5)|TYPE=Armor',
            'COMBAT|AC|1+floor(%CHOICE/5)|TYPE=Shield',
            'SAVE|ALL|1+floor(%CHOICE/4)|TYPE=Resistance',
        )
        for line, bonus in zip(lines, expected):
            self.assertIn('TEMPBONUS:ANYPC|' + bonus, line)
            self.assertNotIn('\tBONUS:', line)
            self.assertNotIn('PREABILITY:', line)

    def test_conditional_aegis_saves_are_explicit_context_toggles(self):
        lines = self.files['spheres_protection_effects.lst'].splitlines()[6:11]
        self.assertEqual(len(lines), 5)
        for line in lines:
            self.assertIn(' - Conditional Saves\t', line)
            self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|4|TYPE=Morale', line)
            self.assertIn('Enable ONLY while resolving', line)
            self.assertIn('Disable immediately afterward', line)
            self.assertNotIn('\tBONUS:', line)
            self.assertNotIn('TEMPVALUE:', line)

    def test_slippery_modifies_only_its_skills_and_cmd(self):
        line = self.files['spheres_protection_effects.lst'].splitlines()[5]
        self.assertTrue(line.startswith('Protection Effect - Slippery\t'))
        self.assertIn('TEMPBONUS:ANYPC|SKILL|Acrobatics,Escape Artist|2+floor(%CHOICE/5)|TYPE=Enhancement', line)
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|CMD|2+floor(%CHOICE/5)|TYPE=Enhancement', line)
        self.assertNotIn('|AC|', line)
        self.assertNotIn('|CMB|', line)

    def test_conditional_defense_types_and_exceptions(self):
        lines = self.files['spheres_protection_effects.lst'].splitlines()[11:15]
        self.assertEqual(len(lines), 4)
        for line in lines:
            self.assertIn('TEMPBONUS:ANYPC|SAVE|ALL|4', line)
            self.assertIn('TEMPBONUS:ANYPC|COMBAT|AC|4', line)
            self.assertIn('Disable immediately', line)
        self.assertIn('Destructionless', lines[0])
        self.assertIn('breath weapons', lines[0])
        self.assertIn('not saves to disbelieve', lines[1])
        self.assertIn('not Bludgeon attacks', lines[2])
        self.assertNotIn('TYPE=Morale', lines[3])
        self.assertIn('not every electricity attack', lines[3])

    def test_mettle_is_only_a_confirmation_context_bonus(self):
        line = next(line for line in self.files['spheres_protection_effects.lst'].splitlines()
                    if line.startswith('Protection Effect - Mettle - Critical Confirmation Only\t'))
        self.assertTrue(line.startswith('Protection Effect - Mettle - Critical Confirmation Only\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|AC|5+%CHOICE', line)
        self.assertIn('Disable immediately', line)
        self.assertNotIn('TYPE=', line)
        self.assertNotIn('|SAVE|', line)

    def test_inner_peace_skills_are_situational_not_general(self):
        line = next(line for line in self.files['spheres_protection_effects.lst'].splitlines()
                    if line.startswith('Protection Effect - Inner Peace - Situational Skills\t'))
        for situation in ('Bluff=Conceal Emotions', 'Bluff=Relay Secret Messages',
                          'Diplomacy=Calm Creatures'):
            self.assertIn('TEMPBONUS:ANYPC|SITUATION|' + situation + '|4|TYPE=Morale', line)
        self.assertNotIn('|SKILL|', line)
        self.assertNotIn('|SAVE|', line)

    def test_guardian_aegis_penalty_targets_attacker_only(self):
        line = next(line for line in self.files['spheres_protection_effects.lst'].splitlines()
                    if line.startswith('Protection Effect - Guardian - Attacker Penalty\t'))
        self.assertTrue(line.startswith('Protection Effect - Guardian - Attacker Penalty\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT|-1-floor(%CHOICE/5)', line)
        self.assertIn('ATTACKER, not the aegis bearer', line)
        self.assertIn('do not apply when attacking another Guardian', line)

    def test_exclusion_penalty_requires_boundary_and_material_context(self):
        line = next(line for line in self.files['spheres_protection_effects.lst'].splitlines()
                    if line.startswith('Protection Effect - Exclusion - Attacker Penalty\t'))
        self.assertIn('TEMPBONUS:ANYPC|COMBAT|TOHIT|-%CHOICE', line)
        self.assertIn('excluded material that crosses from outside into the ward', line)
        self.assertIn('Disable immediately', line)
        self.assertNotIn('|AC|', line)
        self.assertNotIn('|AC|', line)

    def test_enhancement_equipment_duration_is_distinct_from_other_effects(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_enhancement.lst'].splitlines()}
        self.assertIn('min(5,1+floor(SPHERES_CL_ENHANCEMENT/4))+SPHERES_ENHANCEMENT_GREATER_EQUIPMENT', records['Enhancement Sphere'])
        self.assertIn('if(SPHERES_ENHANCEMENT_DEEP,60,10)', records['Enhancement Sphere'])
        for name, flag in (('Deep Enhancement', 'DEEP'), ('Greater Enhance Equipment', 'GREATER_EQUIPMENT')):
            self.assertIn('BONUS:VAR|SPHERES_ENHANCEMENT_' + flag + '|1', records['Enhancement - ' + name])
            self.assertNotIn('BONUS:COMBAT', records['Enhancement - ' + name])

    def test_lighten_and_flexibility_are_target_references(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_enhancement.lst'].splitlines()}
        lighten = records['Enhancement - Lighten']
        for threshold in (3, 5, 8, 11, 15, 20, 25):
            self.assertIn('SPHERES_CL_ENHANCEMENT>=' + str(threshold), lighten)
        self.assertIn('LIGHTEN_HALF_SIZE_INDEX|min(8,', lighten)
        self.assertIn('LIGHTEN_WEIGHTLESS_SIZE_INDEX|min(8,SPHERES_ENHANCEMENT_LIGHTEN_TABLE_STEP-1)', lighten)
        self.assertIn('LIGHTEN_FLOAT_SIZE_INDEX|min(8,SPHERES_ENHANCEMENT_LIGHTEN_TABLE_STEP-2)', lighten)
        flexibility = records['Enhancement - Improved Flexibility']
        for threshold in (6, 12, 18):
            self.assertIn('SPHERES_CL_ENHANCEMENT>=' + str(threshold), flexibility)
        for line in (lighten, flexibility):
            for forbidden in ('\tSIZE:', 'BONUS:MOVE', 'BONUS:COMBAT', 'BONUS:SKILL', 'BONUS:WEIGHT'):
                self.assertNotIn(forbidden, line)

    def test_animated_object_capacity_does_not_modify_caster_size_or_hd(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_enhancement.lst'].splitlines()}
        line = records['Enhancement - Animate Object']
        self.assertIn('ANIMATE_TOTAL_HD|2*SPHERES_CL_ENHANCEMENT', line)
        self.assertIn('SPHERES_CL_ENHANCEMENT>=42', line)
        for forbidden in ('\tSIZE:', '\tHITDIE:', '\tFOLLOWERS:', 'BONUS:COMBAT'):
            self.assertNotIn(forbidden, line)

    def test_enhancement_target_bonuses_are_not_permanent_benefits(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_enhancement.lst'].splitlines()}
        for name in ('Enhance Focus', 'Staunch Resistance', 'Superior Reflexes'):
            line = records['Enhancement - ' + name]
            self.assertIn('DEFINE:SPHERES_ENHANCEMENT_', line)
            for forbidden in ('BONUS:SAVE', 'BONUS:SKILL', 'BONUS:COMBAT'):
                self.assertNotIn(forbidden, line)
        self.assertIn('floor((SPHERES_CL_ENHANCEMENT-1)/4)', records['Enhancement - Superior Reflexes'])

    def test_enhancement_additional_target_effects_are_scoped(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_enhancement.lst'].splitlines()}
        for name in ('Alter Movement', 'Bestow Intelligence', 'Cripple', 'Deadly Weapon',
                     'Emphasize Belief', 'Mental Enhancement', 'Physical Enhancement', 'Ragged Edges',
                     'Energize Body', 'Energy Enhancement', 'Harden/Weaken', 'Supply Vigor', 'Traveling Weapon',
                     'Ravenous Weapon', 'Spectral Enhancement', 'Enhance Potency'):
            line = records['Enhancement - ' + name]
            self.assertIn('DEFINE:SPHERES_ENHANCEMENT_', line)
            for forbidden in ('BONUS:STAT', 'BONUS:MOVE', 'BONUS:COMBAT', 'BONUS:SKILL', '\tDR:'):
                self.assertNotIn(forbidden, line)
        self.assertIn('2+2*floor(SPHERES_CL_ENHANCEMENT/7)', records['Enhancement - Mental Enhancement'])
        self.assertIn('CRIPPLE_PENALTY|-2-floor', records['Enhancement - Cripple'])
        self.assertIn('RAVENOUS_D6|1+floor(SPHERES_CL_ENHANCEMENT/4)', records['Enhancement - Ravenous Weapon'])
        self.assertNotIn('BONUS:SAVE', records['Enhancement - Spectral Enhancement'])
        self.assertIn('SPECTRAL_SIZE_INDEX|2+if', records['Enhancement - Spectral Enhancement'])

    def test_telekinesis_references_do_not_change_ordinary_skills_or_movement(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_telekinesis.lst'].splitlines()}
        self.assertIn('DEFINE:SPHERES_TELEKINESIS_GREATER_SPEED|0', records['Telekinesis Sphere'])
        self.assertIn('BONUS:VAR|SPHERES_TELEKINESIS_GREATER_SPEED|1', records['Telekinesis - Greater Speed'])
        for name in ('Finesse', 'Steal'):
            line = records['Telekinesis - ' + name]
            self.assertIn('_PENALTY|-5', line)
            self.assertIn('_PENALTY|5|PREFEAT:1,Skillful Force', line)
            self.assertNotIn('BONUS:SKILL|', line)
        self.assertIn('BONUS:VAR|SPHERES_TELEKINESIS_TOOL_BONUS|2|PREFEAT:1,Skillful Force', records['Telekinesis - Telekinetic Tools'])
        self.assertNotIn('BONUS:MOVE', records['Telekinesis - Greater Speed'])
        self.assertIn('DEFINE:SPHERES_TELEKINESIS_GRAPPLE_CMD|10+SPHERES_TELEKINESIS_MANEUVER_CMB', records['Telekinesis - Telekinetic Maneuver'])

    def test_telekinetic_target_effects_are_not_permanent_character_bonuses(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_telekinesis.lst'].splitlines()}
        for name in ('Divided Mind', 'Dampening Field', 'Dancing Weapon', 'Gravity Ward/Well', 'Telekinetic Push'):
            line = records['Telekinesis - ' + name]
            self.assertIn('DEFINE:SPHERES_TELEKINESIS_', line)
            for forbidden in ('BONUS:COMBAT', 'BONUS:MOVE', '\tDR:', 'BONUS:SKILL'):
                self.assertNotIn(forbidden, line)
        self.assertIn('SPHERES_TELEKINESIS_SPEED/2', records['Telekinesis - Telekinetic Push'])
        self.assertIn('max(1,floor(SPHERES_CL_TELEKINESIS/2))', records['Telekinesis - Divided Mind'])

    def test_telekinetic_range_counter_and_size_do_not_resize_character(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_telekinesis.lst'].splitlines()}
        self.assertIn('DEFINE:SPHERES_TELEKINESIS_INCREASEDRANGE_COUNT|0', records['Telekinesis Sphere'])
        self.assertIn('BONUS:VAR|SPHERES_TELEKINESIS_INCREASEDRANGE_COUNT|1', records['Telekinesis - Increased Range'])
        self.assertIn('BONUS:VAR|SPHERES_TELEKINESIS_POWERFUL|1', records['Telekinesis - Powerful Telekinesis'])
        self.assertNotIn('\tSIZE:', records['Telekinesis - Powerful Telekinesis'])
        self.assertIn('SPHERES_CL_TELEKINESIS>=60', records['Telekinesis Sphere'])
        for name in ('Steal', 'Telekinetic Maneuver', 'Gravity Ward/Well'):
            self.assertIn('+2*SPHERES_TELEKINESIS_FORCEFUL', records['Telekinesis - ' + name])
        self.assertNotIn('BONUS:COMBAT', records['Telekinesis - Forceful Telekinesis'])

    def test_kinetic_field_references_survive_partial_repeat_refunds(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_telekinesis.lst'].splitlines()}
        base = records['Telekinesis Sphere']
        field = records['Telekinesis - Kinetic Field']
        self.assertIn('DEFINE:SPHERES_TELEKINESIS_KINETICFIELD_COUNT|0', base)
        self.assertIn('PREVARLT:SPHERES_TELEKINESIS_KINETICFIELD_COUNT,2', field)
        self.assertNotIn('DEFINE:', field)
        self.assertIn('DEFINE:SPHERES_TELEKINESIS_FIELD_CUBES|if(SPHERES_TELEKINESIS_KINETICFIELD_COUNT>=2', base)
        self.assertIn('if(SPHERES_TELEKINESIS_KINETICFIELD_COUNT,max(1,floor(SPHERES_CL_TELEKINESIS/3)),0)', records['Telekinesis - Quick Reactions'])

    def test_telekinetic_activated_senses_and_movement_are_not_permanent(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_telekinesis.lst'].splitlines()}
        self.assertNotIn('\tVISION:', records['Telekinesis - Kinetic Sense'])
        self.assertNotIn('\tMOVE:', records['Telekinesis - Flight'])
        self.assertIn('SPHERES_TELEKINESIS_FLIGHT_SPEED|SPHERES_TELEKINESIS_SPEED', records['Telekinesis - Flight'])
        self.assertNotIn('SPHERES_TELEKINESIS_SPEED', records['Telekinesis - Whirlwind Assembly'])
        self.assertIn('SPHERES_TELEKINESIS_TETHER_BREAK_DC|SPHERES_DC_TELEKINESIS', records['Telekinesis - Tether'])

    def test_zero_progression_casters_can_select_base_spheres(self):
        for filename, contents in self.files.items():
            if not filename.startswith('spheres_power_') or filename == 'spheres_power_destruction.lst':
                continue
            base = next(line for line in contents.splitlines() if not line.startswith('#'))
            self.assertIn('PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core', base)
            self.assertNotIn('PREVARGTEQ:SPHERES_CASTER_LEVEL,1', base)

    def test_telekinetic_duration_and_area_references_are_scoped(self):
        records = {line.split('\t')[0]: line for line in self.files['spheres_power_telekinesis.lst'].splitlines()}
        for name, expected in (
            ('Gravity Shift', 'GRAVITY_SHIFT_RADIUS|10+5*floor(SPHERES_CL_TELEKINESIS/5)'),
            ('Homing', 'HOMING_ROUNDS|SPHERES_CL_TELEKINESIS'),
            ('Pantomime Cage', 'CAGE_ESCAPE_DC|SPHERES_DC_TELEKINESIS'),
        ):
            line = records['Telekinesis - ' + name]
            self.assertIn('DEFINE:SPHERES_TELEKINESIS_' + expected, line)
            self.assertNotIn('BONUS:COMBAT', line)
            self.assertNotIn('BONUS:MOVE', line)
        self.assertIn('CAGE_ROUNDS|SPHERES_CL_TELEKINESIS', records['Telekinesis - Pantomime Cage'])

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
        self.assertIn('DEFINE:SPHERES_LIFE_INVIGORATE_HP|max(1,SPHERES_CL_LIFE)', records['Life Sphere'])
        self.assertNotIn('BONUS:VAR|SPHERES_LIFE_INVIGORATE_HP|max(1,SPHERES_CL_LIFE)', records['Life Sphere'])
        self.assertIn('BONUS:VAR|SPHERES_LIFE_DEEPER_HEALING|1', records['Life - Deeper Healing'])
        greater = records['Life - Greater Invigorate']
        self.assertIn('BONUS:VAR|SPHERES_LIFE_GREATER_INVIGORATE|1', greater)
        self.assertIn('DEFINE:SPHERES_LIFE_INVIGORATE_HOURS|1+SPHERES_LIFE_GREATER_INVIGORATE*(SPHERES_CL_LIFE-1)', records['Life Sphere'])
        self.assertIn('SPHERES_LIFE_DEEPER_HEALING*SPHERES_CL_LIFE+SPHERES_LIFE_GREATER_INVIGORATE*SPHERES_CASTING_ABILITY', records['Life Sphere'])
        for name in ('Life - Deeper Healing', 'Life - Greater Invigorate', 'Life - Restore Health'):
            for tag in records[name].split('\t'):
                if tag.startswith('BONUS:'):
                    self.assertNotIn('SPHERES_CL_LIFE', tag)
        self.assertNotIn('BONUS:VAR|SPHERES_LIFE_CURE', greater)

    def test_studied_healing_is_cure_only_and_cannot_reduce_existing_cl(self):
        line = next(line for line in self.files['spheres_power_life.lst'].splitlines() if line.startswith('Life Sphere\t'))
        self.assertIn('DEFINE:SPHERES_LIFE_CURE_CL|SPHERES_CL_LIFE+SPHERES_STUDIED_HEALING*max(0,min(ceil(skillinfo("TOTALRANK","Heal")/2),TL-SPHERES_CL_LIFE))', line)
        self.assertIn('floor(SPHERES_LIFE_CURE_CL/5)', line)
        self.assertIn('DEFINE:SPHERES_LIFE_CURE_BONUS|SPHERES_LIFE_CURE_CL*(1+SPHERES_LIFE_RESTORE_HEALTH)', line)
        for tag in line.split('\t'):
            if 'INVIGORATE' in tag:
                self.assertNotIn('CURE_CL', tag)

    def test_ward_cl_keeps_class_and_rank_bonuses_separate(self):
        line = next(line for line in self.files['spheres_power_protection.lst'].splitlines() if line.startswith('Protection Sphere\t'))
        self.assertIn('DEFINE:SPHERES_PROTECTION_WARD_CLASS_BONUS|0', line)
        self.assertIn('DEFINE:SPHERES_PROTECTION_WARD_BASE_CL|SPHERES_CL_PROTECTION+SPHERES_PROTECTION_WARD_CLASS_BONUS', line)
        self.assertIn('min(TL-SPHERES_PROTECTION_WARD_BASE_CL,SPHERES_GRAPHOMANCY*ceil', line)
        self.assertNotIn('BONUS:VAR|SPHERES_CL_PROTECTION', line)

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