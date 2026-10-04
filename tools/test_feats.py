"""Regression tests for feat source boundaries and fail-closed qualification."""
import json
import unittest
from unittest.mock import patch
from spheres_feats import build, Prerequisites, split_clauses, split_alternatives, DATA


class FeatTests(unittest.TestCase):
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
                         ['BONUS:VAR|SPHERES_FEY_ADEPT_SHADOWMARK_DIE_SIZE|2'])

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
        generic = self.parser.clause('channel energy class feature')
        self.assertEqual(generic, self.parser.clause('Channel Energy'))
        self.assertIn('TYPE=ChannelEnergy', generic[0])
        self.assertIn('TYPE=Channel Energy', generic[0])
        self.assertIn('CATEGORY=Soul Weaver Channel,Soul Weaver Positive Channel,Soul Weaver Negative Channel', generic[0])
        for energy in ('positive', 'negative'):
            tags = self.parser.clause('ability to channel ' + energy + ' energy')
            self.assertIn('TYPE=Channel ' + energy.title() + ' Energy', tags[0])
            self.assertIn('Soul Weaver ' + energy.title() + ' Channel', tags[0])
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
        for invalid in (0, -1, True, '3'):
            with self.assertRaises(ValueError):
                dice_prerequisite(invalid)
        for name in ('Defiler’s Channel', 'Pulsing Channel'):
            self.assertFalse(self.by_name[name]['unresolved_prerequisites'])

    def test_plague_persistent_effects(self):
        self.assertEqual(self.by_name['Rotten Hordes']['mechanics'],
                         ['BONUS:VAR|SPHERES_SPELL_POINTS|1'])
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
        self.assertTrue(self.by_name["Glimpse The Flow"]["unresolved_prerequisites"])

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
                ("nonlawful", "!PREALIGN:LG,LN,LE")):
            self.assertEqual(self.parser.clause(clause), [expected])
        self.assertIsNone(self.parser.clause("non-neutral alignment"))
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