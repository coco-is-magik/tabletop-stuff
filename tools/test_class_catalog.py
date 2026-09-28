"""Independent class-source table checks; live checks in pcgen_class_catalog.py."""
import json
import unittest

from spheres import DATA, check_package
from spheres_class_catalog import NAMES, SNAPSHOTS, generate, table, number, source_options
from pcgen_class_catalog import expected, fixture
from spheres_mageknight import option_tags, CURSE_REVIEW, REVIEW_CATEGORY
from spheres_armorist import option_tags as armorist_tags
from spheres_armiger import option_tags as armiger_tags
from spheres_blacksmith import option_tags as blacksmith_tags
from spheres_scholar import option_tags as scholar_tags, DEPENDENCIES, medical_records, medical_resources
from spheres_striker import option_tags as striker_tags, resource_tags as striker_resources
from spheres_technician import option_tags as technician_tags, DEPENDENCIES as TECHNICIAN_DEPENDENCIES, class_tags as technician_class_tags
from spheres_eliciter import emotion_records


class ClassCatalogTest(unittest.TestCase):
    def test_armiger_ranged_prowess(self):
        tags = armiger_tags('Ranged Prowess')
        self.assertIn('STACK:NO', tags)
        self.assertIn('CHOOSE:NUMCHOICES=2|STRING|Sniper|Barrage', tags)
        self.assertIn('BONUS:VAR|ArmigerRanged %LIST|1', tags)
        classes = generate('armiger')[0]
        for sphere in ('Sniper', 'Barrage'):
            self.assertIn('DEFINE:ArmigerRanged ' + sphere + '|0', classes)
            self.assertIn('ABILITY:Spheres Combat Talent|AUTOMATIC|' + sphere +
                          ' Sphere|PREVARGTEQ:ArmigerRanged ' + sphere + ',1', classes)

    def test_eliciter_emotion_tiers(self):
        source = json.loads((SNAPSHOTS / 'eliciter.json').read_text())
        options = source_options(source, 'List of Emotions')
        records = emotion_records(options)
        self.assertEqual(len(records), 4 * len(options))
        self.assertEqual(len({r.split('\t')[0] for r in records}), len(records))
        for tier, level, previous in (('Lesser', 5, 'Eliciter Apathy'),
                                      ('Greater', 8, 'Eliciter Apathy - Lesser'),
                                      ('Master', 11, 'Eliciter Apathy - Greater')):
            line = next(r for r in records if r.startswith('Eliciter Apathy - ' + tier + '\t'))
            self.assertIn(f'PREVARGTEQ:SPHERES_ELICITER_LEVEL,{level}', line)
            self.assertIn('PREABILITY:1,CATEGORY=Eliciter Emotion,' + previous, line)
        self.assertNotIn('Lesser:', records[0])
        futility = next(r for r in records if r.startswith('Eliciter Futility\t'))
        self.assertIn('The eliciter wields futility', futility)
        self.assertNotIn('Aura of Ineptitude', futility)
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            emotion_records([('Unknown', 'Intro\nMinor: A\nGreater: B\nLesser: C\nMaster: D')])
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            emotion_records([('Unknown', 'Minor: Only one tier')])
        features = generate('eliciter')[1]
        self.assertIn('BONUS:SKILL|Bluff,Diplomacy,Intimidate|SPHERES_ELICITER_PERSUASIVE', features)
        self.assertIn('BONUS:VAR|SPHERES_DC_MIND|SPHERES_ELICITER_PERSUASIVE', features)

    def test_technician_insights(self):
        for tag in technician_class_tags():
            self.assertIn(tag, generate('technician')[0])
        records = generate('technician')[1]
        for name, dependencies in TECHNICIAN_DEPENDENCIES.items():
            for dependency in dependencies:
                tag = 'PREABILITY:1,CATEGORY=Technician Technical Insight,Technician ' + dependency
                self.assertIn(tag, technician_tags(name))
                self.assertIn(tag, records)
        self.assertIn('PREVARGTEQ:SPHERES_TECHNICIAN_LEVEL,10', technician_tags('Expert’s Insight'))
        self.assertIn('PREVARGTEQ:SPHERES_TECHNICIAN_LEVEL,6', technician_tags('Greater Craftsman'))
        self.assertIn('BONUS:VAR|SPHERES_TECHNICIAN_INTUITION|max(1,1+WIS)', technician_tags('Intuition (Ex)'))
        self.assertIn('BONUS:VAR|SPHERES_TECHNICIAN_LUCK|1', technician_tags('Intuition, Lucky'))
        self.assertIn('ABILITY:Spheres Combat Talent|AUTOMATIC|Tinker Sphere', technician_tags('Gadgeteer [SUE]'))
        self.assertNotIn('MULT:YES', technician_tags('Luck'))

    def test_scholar_medical_training(self):
        category, ability = medical_records()
        self.assertIn('POOL:min(1,SPHERES_SCHOLAR_LEVEL)', category)
        self.assertIn('PREVARGTEQ:SPHERES_SCHOLAR_LEVEL,1', ability)
        self.assertIn('BONUS:SKILL|Heal|INT-WIS', ability)
        self.assertIn(ability, generate('scholar')[1])
        for tag in medical_resources():
            self.assertIn(tag, generate('scholar')[0])
        self.assertIn('BONUS:VAR|SPHERES_SCHOLAR_MEDICAL_ATTEMPTS_PER_PATIENT|max(1,INT)', medical_resources())
        self.assertIn('BONUS:VAR|SPHERES_SCHOLAR_MEDICAL_REVIVE|if(SPHERES_SCHOLAR_LEVEL>=9,if(skillinfo("TOTALRANK","Heal")>=11,1,0),0)', medical_resources())

    def test_scholar_dependencies_and_talents(self):
        self.assertIn('BONUS:SKILL|Heal|max(1,floor(SPHERES_SCHOLAR_LEVEL/2))',
                      scholar_tags('Expert Healing'))
        records = generate('scholar')[1]
        for name, dependencies in DEPENDENCIES.items():
            for dependency in dependencies:
                tag = "PREABILITY:1,CATEGORY=Scholar Scholar'S Knack,Scholar " + dependency
                self.assertIn(tag, scholar_tags(name))
                self.assertIn(tag, records)
                self.assertIn('Scholar ' + dependency + '\t', records)
        self.assertEqual(scholar_tags('Liquefying Injections')[0], 'PREVARGTEQ:SPHERES_SCHOLAR_LEVEL,6')
        self.assertIn('DEFINE:SPHERES_SCHOLAR_STUDIED_TECHNIQUE|0', generate('scholar')[0])
        tags = scholar_tags('Studied Technique')
        self.assertIn('PREVARLT:SPHERES_SCHOLAR_STUDIED_TECHNIQUE,3', tags)
        self.assertIn('BONUS:VAR|SPHERES_COMBAT_TALENTS|3', tags)
        self.assertIn('STACK:YES', tags)
        self.assertFalse(any(t.startswith('DEFINE:') for t in tags))
        self.assertIn('BONUS:SKILL|TYPE=Knowledge|max(1,floor(SPHERES_SCHOLAR_LEVEL/2))',
                      scholar_tags('Academic Knowledge'))
        self.assertIn('BONUS:VAR|SPHERES_SCHOLAR_INSIGHT_CAPACITY|max(1,floor(SPHERES_SCHOLAR_LEVEL/2))+max(0,INT)',
                      scholar_tags('Astrology'))

    def test_striker_prerequisites_and_repeat_caps(self):
        source = json.loads((SNAPSHOTS / 'striker.json').read_text())
        for title, _ in source_options(source, 'Striker Art (Ex)'):
            self.assertTrue(striker_tags(title)[0].startswith('PREVARGTEQ:SPHERES_STRIKER_LEVEL,'))
        self.assertIn('PREVARGTEQ:SPHERES_STRIKER_LEVEL,8', striker_tags('Outburst [Tension] (requires Striker 8) [LG]'))
        self.assertIn('PREABILITY:1,CATEGORY=Striker Striker Art,Striker Iron Soul', striker_tags('Steel Heart (Requires Iron Soul)'))
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            striker_tags('Unknown (Requires an unknown feature)')
        for name, counter in (('High Tension', 'HIGH_TENSION'), ('Extra Boost', 'EXTRA_BOOST')):
            tags = striker_tags(name + ' (Requires Striker 5)')
            self.assertIn('PREVARLT:SPHERES_STRIKER_' + counter + ',1+floor((SPHERES_STRIKER_LEVEL-5)/6)', tags)
            self.assertIn('STACK:YES', tags)
            self.assertFalse(any(t.startswith('DEFINE:') for t in tags))
        self.assertIn('BONUS:VAR|SPHERES_STRIKER_UNLIMITED_TENSION|if(SPHERES_STRIKER_LEVEL>=20,1,0)', striker_resources())
        self.assertIn('if(SPHERES_STRIKER_LEVEL>=20,7,', '\t'.join(striker_resources()))
        self.assertEqual(generate('striker')[1].count('CATEGORY:Striker Tension Training\t'), 5)
        lines = generate('striker')[0].splitlines()
        for level in (3, 12):
            self.assertIn('BONUS:VAR|UncannyDodgeLVL|1', next(l for l in lines if l.startswith(str(level) + '\t')))

    def test_blacksmith_grants_and_prerequisites(self):
        source = json.loads((SNAPSHOTS / 'blacksmith.json').read_text())
        for title, _ in source_options(source, 'Smithing Insight (Ex)'):
            name = title.split(' [')[0]
            level = {'Armorclad Mastery': 4, 'Stunning Strikes': 12}.get(name, 2)
            self.assertEqual(blacksmith_tags(title)[0], f'PREVARGTEQ:SPHERES_BLACKSMITH_LEVEL,{level}')
        self.assertIn('PREABILITY:1,CATEGORY=Blacksmith Smithing Insight,Blacksmith Shieldsmith',
                      blacksmith_tags('Master Shieldsmith (Requires Shieldsmith)'))
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            blacksmith_tags('Unknown (Requires other feature)')
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Endurance|Toughness', blacksmith_tags('Durable'))
        self.assertIn('STACK:NO', blacksmith_tags('Crafting Competence [Apoc]'))
        self.assertIn('BONUS:ABILITYPOOL|Blacksmith Item Creation Feat|1', blacksmith_tags('Expanded Crafting [Apoc]'))
        self.assertIn('STACK:YES', blacksmith_tags('Expanded Crafting [Apoc]'))
        self.assertIn('TYPE:ItemCreation', generate('blacksmith')[2])
        lines = generate('blacksmith')[0].splitlines()
        self.assertIn('BONUS:SKILL|Profession (Blacksmith)|max(1,floor(SPHERES_BLACKSMITH_LEVEL/2))|TYPE=Competence',
                      next(line for line in lines if line.startswith('2\t')))
        self.assertIn('Profession (Blacksmith)\tKEYSTAT:WIS', (DATA / 'spheres_skills.lst').read_text())
        for level, feat in ((3, 'Craft Wondrous Item'), (5, 'Craft Magic Arms and Armor')):
            line = next(line for line in lines if line.startswith(str(level) + '\t'))
            self.assertIn('ABILITY:FEAT|AUTOMATIC|' + feat, line)

    def test_armiger_heading_gates_and_grants(self):
        source = json.loads((SNAPSHOTS / 'armiger.json').read_text())
        for title, _ in source_options(source, 'Prowess'):
            self.assertTrue(armiger_tags(title)[0].startswith('PREVARGTEQ:SPHERES_ARMIGER_LEVEL,'))
        for title in ('Faith in Steel (Requires Enhanced Customization)',
                      'Mobile Assault (Requires Rapid Assault)'):
            self.assertIn('PREVARGTEQ:SPHERES_ARMIGER_LEVEL,5', armiger_tags(title))
        tags = armiger_tags('Share Customized Weapon (Requires Leadership sphere and (cohort) package)')
        self.assertEqual(sum(t.startswith('PREABILITY:') for t in tags), 2)
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Great Focus', armiger_tags('Extra Focus (Requires Armiger 6)'))
        self.assertIn('STACK:YES', armiger_tags('Champion [CS]'))
        deadly = armiger_tags('Deadly Prowess')
        self.assertIn('STACK:NO', deadly)
        self.assertIn('CHOOSE:NUMCHOICES=3|STRING|Deadly Aim|Piranha Strike|Power Attack', deadly)
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Piranha Strike|PREVARGTEQ:ArmigerDeadly Piranha Strike,1', generate('armiger')[0])
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            armiger_tags('Unknown (Requires unreviewed feature)')

    def test_armorist_prerequisites_and_grants(self):
        source = json.loads((SNAPSHOTS / 'armorist.json').read_text())
        for title, _ in source_options(source, 'Arsenal Trick'):
            self.assertTrue(armorist_tags(title)[0].startswith('PREVARGTEQ:SPHERES_ARMORIST_LEVEL,'))
        self.assertIn('PREVARGTEQ:SPHERES_ARMORIST_LEVEL,10',
                      armorist_tags('Bonded Boost (requires armorist 10, boost equipment class feature)'))
        self.assertIn('PREABILITY:1,CATEGORY=Armorist Arsenal Trick,Armorist Grenadier (requires armorist 6)',
                      armorist_tags('Grenadier, Experimental (requires armorist 10, grenadier) [LG]'))
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            armorist_tags('Unknown (requires unknown feature)')
        for name in ('Combat Feat', 'Crafter', 'Champion'):
            self.assertIn('BONUS:ABILITYPOOL|Armorist ' + name + ' Feat|1', armorist_tags(name))
            self.assertIn('STACK:YES', armorist_tags(name))
        self.assertIn('BONUS:VAR|SPHERES_COMBAT_TALENTS|1', armorist_tags('Combat Talent [CotS]'))
        self.assertIn('BONUS:VAR|SPHERES_ARMORIST_BOUND_ITEMS|1',
                      armorist_tags('Additional Binding (requires bound equipment)'))
        self.assertIn('STACK:YES', armorist_tags('Greater Armor Training (requires armorist 3)'))
        features = generate('armorist')[1]
        self.assertIn('BONUS:MISC|MAXDEX|SPHERES_ARMORIST_ARMOR_TRAINING|PREEQUIP:1,TYPE=Armor', features)
        self.assertIn('BONUS:MISC|ACCHECK|SPHERES_ARMORIST_ARMOR_TRAINING|PREEQUIP:1,TYPE=Armor', features)
        self.assertIn('Armorist Heavy Armor Movement|PREVARGTEQ:SPHERES_ARMORIST_LEVEL,7', features)

    def test_mageknight_feat_choice_pools(self):
        categories = generate('mageknight')[2]
        for name, types in (('Champion', 'Champion'), ('Greater Combatant', 'Combat.Champion')):
            tags = option_tags(name)
            self.assertIn('MULT:YES', tags)
            self.assertIn('STACK:YES', tags)
            self.assertIn('BONUS:ABILITYPOOL|Mageknight ' + name + ' Feat|1', tags)
            self.assertIn('ABILITYCATEGORY:Mageknight ' + name + ' Feat\tCATEGORY:FEAT\tTYPE:' + types,
                          categories)
            self.assertFalse(any(tag.startswith('ABILITY:FEAT|AUTOMATIC') for tag in tags))

    def test_all_class_tables_and_package(self):
        campaign = (DATA / "spheres.pcc").read_text()
        self.assertIn("PASS", check_package())
        for slug in NAMES:
            with self.subTest(slug=slug):
                snapshot = json.loads((SNAPSHOTS / f"{slug}.json").read_text())
                headers, rows = table(snapshot)
                class_lst, features, categories, details = generate(slug)
                for suffix, content in (("class", class_lst), ("features", features), ("categories", categories)):
                    if content:
                        file = f"spheres_{slug}_{suffix}.lst"
                        self.assertIn(f":{file}", campaign)
                        self.assertEqual((DATA / file).read_text(), content)
                for level, row in enumerate(rows, 1):
                    result = expected(slug, level)
                    self.assertEqual(result["bab"], number(row[1]))
                    self.assertEqual([result[key] for key in ("fortitude", "reflex", "will")],
                                     [number(row[j]) for j in (2, 3, 4)])
                    self.assertEqual(result["talents"] - (2 if details["magic"] else 0)
                                     - (slug == "mageknight"), number(row[headers.index("Magic Talents") if "Magic Talents" in headers else headers.index("Talents") if details["magic"] else headers.index("Combat Talents")]))
                    if details["magic"]:
                        self.assertEqual(result["caster_level"], number(row[headers.index("Caster Level")]))
                        self.assertEqual(result["spell_points"], level)
                    self.assertEqual(fixture(slug, level).count("CLASSABILITIESLEVEL:"), level)

    def test_free_sphere_and_choice_boundaries(self):
        for slug, sphere in (("eliciter", "Mind"), ("fey-adept", "Illusion"),
                             ("shifter", "Alteration"), ("symbiat", "Mind Sphere|Telekinesis")):
            self.assertIn(f"{sphere} Sphere" if slug != "symbiat" else sphere + " Sphere",
                          generate(slug)[1])
        self.assertIn("CATEGORY:Striker Bare Knuckles", generate("striker")[2])
        self.assertIn("CATEGORY:Hedgewitch Path", generate("hedgewitch")[2])
        self.assertIn("CATEGORY:Wraith Haunt Path", generate("wraith")[2])
        self.assertIn("CATEGORY:Soul Weaver Channel", generate("soul-weaver")[2])
        for slug, sphere in (("commander", "Warleader"), ("technician", "Trap"),
                             ("scholar", "Alchemy"), ("sentinel", "Guardian")):
            self.assertIn(f"{sphere} Sphere", generate(slug)[1])
        self.assertIn("CATEGORY:Commander Enhanced Tactic", generate("commander")[2])
        self.assertIn("CATEGORY:Thaumaturge Bonus Feat", generate("thaumaturge")[2])
        self.assertIn("AUTO:WEAPONPROF|Longsword|Rapier|Sap|Sword (Short)|Shortbow|Whip",
                      generate("symbiat")[0])
        self.assertIn("CATEGORY:Technician Invention Base Form", generate("technician")[2])
        self.assertIn("Technician Independent Invention\tCATEGORY:Technician Invention Base Form", generate("technician")[1])
        self.assertIn("Wraith Path of the Anima - Weather\tCATEGORY:Wraith Haunt Path", generate("wraith")[1])
        hedgewitch = generate("hedgewitch")[1]
        self.assertIn("Hedgewitch Arcane Builder\tCATEGORY:Hedgewitch Secret\tPREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10", hedgewitch)
        for slug, heading, allowed, excluded in (("wraith", "Wraith Haunts", "Amnesiac Possession", "Path of the Ancestor"),
                                                   ("technician", "List of Technical Insights", "Aesthetic Insight", "Improved Crossbow")):
            snapshot = json.loads((SNAPSHOTS / f"{slug}.json").read_text())
            names = [name for name, _ in source_options(snapshot, heading)]
            self.assertIn(allowed, names)
            self.assertNotIn(excluded, names)
        for slug, level in (("unknown", 1), ("armorist", 0), ("armorist", 21)):
            with self.assertRaises(ValueError):
                fixture(slug, level)
            with self.assertRaises(ValueError):
                expected(slug, level)
        with self.assertRaises(ValueError):
            generate("unknown")
        broken = {"url": "broken", "sections": [{"text": "Table: Broken | Level | Base Attack Bonus\n| 1 | +0"}]}
        with self.assertRaises(ValueError):
            table(broken)

    def test_eliciter_persuasive_boundaries(self):
        abilities = generate("eliciter")[1]
        self.assertIn("BONUS:VAR|SPHERES_ELICITER_PERSUASIVE|2+floor(SPHERES_ELICITER_LEVEL/6)", abilities)
        for level, expected_bonus in ((1, 2), (5, 2), (6, 3), (11, 3),
                                      (12, 4), (17, 4), (18, 5), (20, 5)):
            self.assertEqual(2 + level // 6, expected_bonus)

    def test_combat_training_grants_focus(self):
        grant = "ABILITY:Special Ability|AUTOMATIC|Spheres Martial Focus"
        for slug in NAMES:
            _, abilities, _, details = generate(slug)
            if details["magic"]:
                self.assertNotIn(grant, abilities, slug)
            else:
                training = next(line for line in abilities.splitlines()
                                if line.startswith(details["name"] + " Combat Training\t"))
                self.assertIn("TYPE:SpheresInternal.SpheresCombatTraining", training, slug)
                self.assertIn(grant, training, slug)

    def test_mageknight_prerequisites(self):
        snapshot = json.loads((SNAPSHOTS / "mageknight.json").read_text())
        options = source_options(snapshot, "Mystic Combat (Su)")
        records = {line.split("\t")[0]: line for line in generate("mageknight")[1].splitlines()}
        for title, _ in options:
            tags = option_tags(title)
            self.assertTrue(tags[0].startswith("PREVARGTEQ:SPHERES_MAGEKNIGHT_LEVEL,"))
        for title, level in (("Elemental Defense (requires mystic defense)", 11),
                             ("Mark of Pain (requires marked)", 7),
                             ("Whirl of Blows (requires mageknight 6)", 6),
                             ("Magic Power", 2)):
            self.assertIn(f"PREVARGTEQ:SPHERES_MAGEKNIGHT_LEVEL,{level}", records["Mageknight " + title])
        self.assertIn("PREABILITY:1,CATEGORY=Mageknight Mystic Combat,Mageknight Spell Shield",
                      records["Mageknight Spell Mirror (requires mageknight 10 - spell shield)"])
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,War Sphere",
                      records["Mageknight Shared Marking (requires marked - War sphere)"])
        black_dog = next(value for key, value in records.items() if key.startswith("Mageknight Black Dog Companion"))
        self.assertIn("PREVARGTEQ:SPHERES_MAGEKNIGHT_LEVEL,4", black_dog)
        self.assertIn(f"PREABILITY:1,CATEGORY={REVIEW_CATEGORY},{CURSE_REVIEW}", black_dog)
        self.assertIn("COST:0", records[CURSE_REVIEW])
        with self.assertRaisesRegex(ValueError, "Unreviewed"):
            option_tags("Unreviewed Option (requires an unknown feature)")

    def test_mageknight_repeatable_grants(self):
        self.assertIn("DEFINE:SPHERES_COMBAT_TALENTS|0", generate("mageknight")[0])
        self.assertNotIn("DEFINE:SPHERES_COMBAT_TALENTS|0", option_tags("Combat Talent [CotS]"))
        for title, variable in (("Magic Power", "SPHERES_MAGIC_TALENTS"),
                                ("Combat Talent [CotS]", "SPHERES_COMBAT_TALENTS")):
            tags = option_tags(title)
            for tag in ("MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|" + variable + "|1"):
                self.assertIn(tag, tags)
        for title, feat in (("Whirl of Blows (requires mageknight 6)", "Whirlwind Attack"),
                            ("Sunder The Veil", "Pierce The Veil"),
                            ("Weirding Initiate", "Weird Defense")):
            self.assertIn("ABILITY:FEAT|AUTOMATIC|" + feat, option_tags(title))
        self.assertNotIn("MULT:YES", option_tags("Spell Shield [WM]"))
        for name, previous, talent, feat in (
                ('Weirding Adept', 'Weirding Initiate', 'Mage Feint', 'Weird Motion'),
                ('Weirding Master', 'Weirding Adept', 'Decoy', 'Weird Assault')):
            tags = option_tags(name)
            grant = next(t for t in tags if t.startswith('ABILITY:FEAT'))
            self.assertIn('|AUTOMATIC|' + feat + '|PREMULT:1,', grant)
            self.assertIn('Mageknight ' + previous, grant)
            self.assertIn('[PREATT:3]', grant)
            self.assertIn('Illusion Sphere', grant)
            self.assertTrue(any(t.startswith('ABILITY:Spheres Magic Talent|AUTOMATIC|Illusion - ' + talent)
                                for t in tags))
        self.assertIn('BONUS:VAR|SPHERES_MAGE_FEINT_CL|max(SPHERES_CASTER_LEVEL,SPHERES_CL_ILLUSION)+'
                      'SPHERES_MAGEKNIGHT_LEVEL-floor(SPHERES_MAGEKNIGHT_LEVEL/2)', option_tags('Weirding Adept'))
        self.assertFalse(any(t.startswith('BONUS:VAR|SPHERES_CL_ILLUSION|') for t in option_tags('Weirding Adept')))


if __name__ == "__main__":
    unittest.main()