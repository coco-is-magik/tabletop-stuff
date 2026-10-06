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
    def test_path_feat_secrets_suppress_grants_without_path(self):
        _, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        for path, secret, pool in (('Academia', 'Metamagic Knowledge', 'Metamagic Knowledge'),
                                   ('Combat', 'Combat Feat', 'Combat'), ('Combat', 'Tactician', 'Tactician'),
                                   ('Umbral', 'Touch of Darkness', 'Touch of Darkness'),
                                   ('Temporal Traveler', 'Grit Feats', 'Grit')):
            self.assertIn(f'BONUS:ABILITYPOOL|Hedgewitch {pool} Feat|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}',
                          records[f'Hedgewitch {path} {secret}'])
        self.assertIn('TACTICIAN_USES|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Combat',
                      records['Hedgewitch Combat Tactician'])
        for path, name in (('Academia', 'Extra Spell Points'), ('Academia', 'Scholarship'),
                           ('Combat', 'Greater Aid'), ('Temporal Traveler', 'Trapfinding')):
            bonuses = [tag for tag in records[f'Hedgewitch {path} {name}'].split('\t') if tag.startswith('BONUS:')]
            self.assertTrue(bonuses)
            for bonus in bonuses:
                self.assertIn(f'|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}', bonus)

    def test_covenant_shared_touch_channel_capacity(self):
        classes, abilities, categories, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        self.assertIn('BONUS:ABILITYPOOL|Hedgewitch Covenant Energy|1', records['Hedgewitch Covenant'])
        self.assertIn('COVENANT_USES|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)', records['Hedgewitch Covenant'])
        self.assertIn('COVENANT_DIE_SIZE|if(SPHERES_HEDGEWITCH_LEVEL>=20,8,6)', records['Hedgewitch Covenant'])
        self.assertIn('PREALIGN:LG,NG,CG,LN,TN,CN', records['Hedgewitch Covenant Positive'])
        self.assertIn('PREALIGN:LE,NE,CE,LN,TN,CN', records['Hedgewitch Covenant Negative'])
        self.assertIn('COVENANT_USES|4|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Covenant', records['Hedgewitch Covenant Extra Healing'])
        self.assertIn('STACK:YES', records['Hedgewitch Covenant Extra Healing'])
        smite = records['Hedgewitch Covenant Smite']
        self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', smite)
        self.assertIn('STACK:YES', smite)
        self.assertIn('COVENANT_SMITE_USES|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Covenant', smite)
        self.assertNotIn('BONUS:COMBAT', smite)
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_COVENANT_USES|0', classes)
        self.assertIn('ABILITYCATEGORY:Hedgewitch Covenant Energy', categories)
        self.assertIn('ABILITYCATEGORY:Hedgewitch Channel Feat', categories)
        self.assertIn('TYPE:HedgewitchChannelFeat', categories)
        self.assertIn('STACK:YES', records['Hedgewitch Covenant Channel Feats'])
        self.assertIn('BONUS:ABILITYPOOL|Hedgewitch Channel Feat|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Covenant', records['Hedgewitch Covenant Channel Feats'])

    def test_temporal_traveler_grit_secret_and_filtered_pool(self):
        _, abilities, categories, _ = generate('hedgewitch')
        record = next(line for line in abilities.splitlines()
                      if line.startswith('Hedgewitch Temporal Traveler Grit Feats\t'))
        self.assertIn('PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Temporal Traveler', record)
        self.assertIn('MULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE', record)
        self.assertIn('BONUS:ABILITYPOOL|Hedgewitch Grit Feat|1', record)
        category = next(line for line in categories.splitlines()
                        if line.startswith('ABILITYCATEGORY:Hedgewitch Grit Feat\t'))
        self.assertIn('CATEGORY:FEAT\tTYPE:Grit.Panache', category)
        self.assertIn('POOL:0', category)

    def test_umbral_uses_one_shared_shadow_pool(self):
        _, abilities, _, _ = generate('hedgewitch')
        umbral = next(line for line in abilities.splitlines() if line.startswith('Hedgewitch Umbral\t'))
        self.assertIn('BONUS:VAR|SPHERES_HEDGEWITCH_UMBRAL_LEVEL|SPHERES_HEDGEWITCH_LEVEL', umbral)
        self.assertIn('ABILITY:Special Ability|AUTOMATIC|Fey Adept Shadow Points (Reference)', umbral)
        _, fey, _, _ = generate('fey-adept')
        pool = next(line for line in fey.splitlines() if line.startswith('Fey Adept Shadow Points (Reference)\t'))
        self.assertIn('floor((SPHERES_FEY_ADEPT_LEVEL+SPHERES_HEDGEWITCH_UMBRAL_LEVEL)/2)', pool)
        self.assertIn('max(3,CHA)', pool)
        self.assertIn('max(1,CHA+floor(SPHERES_FEY_ADEPT_LEVEL/2))', pool)

    def test_combat_mastery_physical_choices_and_conditional_effects(self):
        from spheres_hedgewitch import academia_mastery
        category, records = academia_mastery('Combat')
        self.assertIn('CATEGORY:Hedgewitch Combat Mastery', category)
        self.assertEqual(len(records), 3)
        for record, stat in zip(records, ('STR', 'DEX', 'CON')):
            self.assertIn('BONUS:STAT|' + stat + '|2|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,20|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Combat', record)
        with self.assertRaises(ValueError):
            academia_mastery('Unknown')

    def test_hedgewitch_charlatan_scoped_resources(self):
        classes, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        path = records['Hedgewitch Charlatanism']
        self.assertIn('BONUS:ABILITYPOOL|Versatile Performance|1', path)
        self.assertIn('GUILE_SNEAK_DICE|ceil(SPHERES_HEDGEWITCH_LEVEL/2)', path)
        self.assertNotIn('BONUS:VAR|SneakAttack', path)
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_GUILE|0', classes)
        exceptional = records['Hedgewitch Charlatanism Exceptional Skill']
        self.assertIn('CHOOSE:NUMCHOICES=1|SKILL|!TYPE=Perform,!TYPE=SkillUse', exceptional)
        self.assertIn('BONUS:SKILL|Bluff (Perform (Act))|floor(SPHERES_HEDGEWITCH_LEVEL/2)', exceptional)
        self.assertIn('PREVARGTEQ:HedgewitchExceptional Bluff,1', exceptional)
        for name in ('Extra Guile', 'Versatile Performance'):
            self.assertIn('STACK:YES', records['Hedgewitch Charlatanism ' + name])
        self.assertIn('BONUS:ABILITYPOOL|Versatile Performance|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Charlatanism', records['Hedgewitch Charlatanism Versatile Performance'])

    def test_hedgewitch_inspiration_is_conditional(self):
        classes, abilities, _, _ = generate('hedgewitch')
        path = next(line for line in abilities.splitlines() if line.startswith('Hedgewitch Font Of Inspiration\t'))
        self.assertIn('ABILITY:Spheres Magic Talent|AUTOMATIC|Divination Sphere', path)
        self.assertIn('STUDIED_BONUS|floor(SPHERES_HEDGEWITCH_LEVEL/2)|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,5', path)
        self.assertNotIn('BONUS:COMBAT', path)
        extra = next(line for line in abilities.splitlines() if line.startswith('Hedgewitch Font Of Inspiration Extra Inspiration\t'))
        self.assertIn('STACK:YES', extra)
        self.assertIn('BONUS:VAR|SPHERES_HEDGEWITCH_INSPIRATION|2|PREABILITY:', extra)
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_INSPIRATION|0', classes)

    def test_hedgewitch_curse_and_spirit_capacity_not_permanent_talents(self):
        _, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        for path, secret, variable in (('Black Magic', 'Curses', 'CURSES'), ('Spiritualism', 'Extra Spirit', 'SPIRIT_USES')):
            self.assertIn('SPHERES_HEDGEWITCH_' + variable + '|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)', records['Hedgewitch ' + path])
            record = records['Hedgewitch ' + path + ' ' + secret]
            self.assertIn('STACK:YES', record)
            self.assertIn('PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch ' + path, record)
            self.assertNotIn('BONUS:ABILITYPOOL|Spheres', record)
        self.assertNotIn('ABILITY:Spheres Magic Talent', records['Hedgewitch Spiritualism'])

    def test_herbology_secret_dependencies(self):
        classes, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_CONCOCTION_HOURS|0', classes)
        self.assertIn('Assassin ~ Poison Use', records['Hedgewitch Herbology'])
        for name, dependency in (('Instant Poison', 'Swift Poison'), ('Miracle Man', 'Surgeon')):
            record = records['Hedgewitch Herbology ' + name]
            self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', record)
            self.assertIn('PREABILITY:1,CATEGORY=Hedgewitch Secret,Hedgewitch Herbology ' + dependency, record)
            self.assertIn('PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Herbology', record)
        self.assertIn('SPHERES_HEDGEWITCH_LEVEL-1', records['Hedgewitch Herbology Potent Concoctions'])

    def test_hedgewitch_temporal_and_transmuter_resources(self):
        _, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        self.assertIn('ABILITY:Spheres Magic Talent|AUTOMATIC|Time Sphere', records['Hedgewitch Temporal Traveler'])
        self.assertIn('SPHERES_HEDGEWITCH_INSIGHT_CAPACITY|max(1,SPHERES_CASTING_ABILITY)', records['Hedgewitch Temporal Traveler'])
        self.assertIn('SPHERES_HEDGEWITCH_TRANSMUTATION_DC|10+floor(SPHERES_HEDGEWITCH_LEVEL/2)+SPHERES_CASTING_ABILITY', records['Hedgewitch Transmuter'])
        self.assertIn('BONUS:VAR|SPHERES_HEDGEWITCH_CREATE_ENABLED|1|PREABILITY:1,CATEGORY=Spheres Magic Talent,Creation Sphere', records['Hedgewitch Transmuter'])
        self.assertNotIn('BONUS:VAR|SPHERES_HEDGEWITCH_CREATE_CL', records['Hedgewitch Transmuter'])
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_CREATE_CL|if(SPHERES_HEDGEWITCH_CREATE_ENABLED>0,SPHERES_CL_CREATION+SPHERES_HEDGEWITCH_LEVEL-floor(SPHERES_HEDGEWITCH_LEVEL*3/4),0)', generate('hedgewitch')[0])
        self.assertNotIn('BONUS:VAR|SPHERES_CL_CREATION|', records['Hedgewitch Transmuter'])
        self.assertIn('STACK:YES', records['Hedgewitch Transmuter Transformations'])
        for name in ('Expanded Transformation', 'Greater Transformation', 'New Life'):
            self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', records['Hedgewitch Transmuter ' + name])
        self.assertIn('TRANSMUTATION_HD_BONUS|1+floor((SPHERES_HEDGEWITCH_LEVEL-10)/3)', records['Hedgewitch Transmuter Greater Transformation'])
        self.assertNotIn('BONUS:SIZEMOD', records['Hedgewitch Transmuter Practiced Transmutation'])
        self.assertIn('TYPE=Trapfinding', records['Hedgewitch Temporal Traveler Trapfinding'])
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Distill Compound', records['Hedgewitch Herbology'])
        self.assertIn('SPHERES_HEDGEWITCH_CONCOCTION_HEALING_DICE|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))', records['Hedgewitch Herbology'])
        self.assertIn('STACK:YES', records['Hedgewitch Herbology Extra Concoctions'])

    def test_hedgewitch_astrology_known_aura_slots(self):
        _, abilities, categories, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        self.assertIn('ABILITY:Spheres Magic Talent|AUTOMATIC|Light Sphere', records['Hedgewitch Astrology'])
        self.assertIn('BONUS:ABILITYPOOL|Hedgewitch Celestial Aura|2', records['Hedgewitch Astrology'])
        self.assertIn('ABILITYCATEGORY:Hedgewitch Celestial Aura', categories)
        for name in ('Moon', 'Planet', 'Star', 'Sun'):
            record = records['Hedgewitch Celestial Aura - ' + name]
            self.assertIn('PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Astrology', record)
            self.assertNotIn('BONUS:', record)
        self.assertIn('PREVARLT:SPHERES_HEDGEWITCH_AURA_REACH_COUNT,2', records["Hedgewitch Astrology Heaven's Reach"])
        self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', records['Hedgewitch Astrology Syzygy'])
        self.assertIn('SPHERES_HEDGEWITCH_LEVEL+if(SPHERES_HEDGEWITCH_LEVEL>=20,5,0)', records['Hedgewitch Astrology'])

    def test_hedgewitch_path_secret_feat_pools(self):
        _, abilities, categories, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        for path, name, pool in (('Combat', 'Combat Feat', 'Combat'),
                                 ('Combat', 'Tactician', 'Tactician'),
                                 ('Umbral', 'Touch of Darkness', 'Touch of Darkness')):
            record = records[f'Hedgewitch {path} {name}']
            self.assertIn(f'PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}', record)
            self.assertIn('STACK:YES', record)
            self.assertIn(f'BONUS:ABILITYPOOL|Hedgewitch {pool} Feat|1', record)
            self.assertIn(f'ABILITYCATEGORY:Hedgewitch {pool} Feat', categories)
        knowledge = records['Hedgewitch Academia Metamagic Knowledge']
        self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', knowledge)
        self.assertNotIn('STACK:YES', knowledge)
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Shadow Magic', records['Hedgewitch Umbral Shadow Sculptor'])
        for name in ('Venom Immunity', 'Wild Vitality'):
            self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', records['Hedgewitch Green Magic ' + name])
        self.assertIn('Beastmastery Sphere|Beastmastery - Focusing Connection',
                      records['Hedgewitch Green Magic Bestial Bonds'])
        self.assertIn('TYPE=Competence', records['Hedgewitch Academia Scholarship'])
        self.assertIn('UNENCUMBEREDMOVE:HeavyArmor', records['Hedgewitch Combat Armor Training'])

    def test_shifter_trait_prerequisites_and_persistent_effects(self):
        from spheres_shifter import option_tags
        _, abilities, categories, _ = generate('shifter')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        improved = records['Shifter Adaptation - Improved (requires adaptation)']
        self.assertIn('PREABILITY:1,CATEGORY=Shifter Bestial Trait,Shifter Adaptation (Ex)', improved)
        greater = records['Shifter Adaptation - Greater (requires adaptation - improved adaptation - shifter 10)']
        self.assertIn('PREVARGTEQ:SPHERES_SHIFTER_LEVEL,10', greater)
        self.assertIn('Shifter Adaptation - Improved (requires adaptation)', greater)
        for name in ('Animal Hide (Ex)', 'Bestial Speed (Ex)', 'Combat Talent', 'Champion', 'Quick Healing (Su)'):
            self.assertIn('STACK:YES', records['Shifter ' + name])
        self.assertIn('BONUS:COMBAT|AC|1|TYPE=NaturalArmor.STACK', records['Shifter Animal Hide (Ex)'])
        self.assertIn('BONUS:MOVEADD|TYPE.All|10', records['Shifter Bestial Speed (Ex)'])
        self.assertIn('ABILITYCATEGORY:Shifter Champion Feat', categories)
        self.assertIn('FOLLOWERS:Familiar|1', records['Shifter Animal Advisor (Su)'])
        self.assertIn('BONUS:VAR|FamiliarMasterLVL|SPHERES_SHIFTER_LEVEL|TYPE=Base.STACK', records['Shifter Animal Advisor (Su)'])
        self.assertIn('PRESIZEGTEQ:H', records['Shifter Snatch (requires Huge size)'])
        self.assertIn('ABILITY:FEAT|AUTOMATIC|Snatch', records['Shifter Snatch (requires Huge size)'])
        self.assertIn('BONUS:COMBAT|TOHIT.Natural,DAMAGE.Natural|1+floor(SPHERES_SHIFTER_LEVEL/5)|TYPE=Enhancement', records['Shifter Magical Attacks (Su)'])
        improved_attack = records['Shifter Improved Natural Attack (Ex) (requires shifter 6)']
        self.assertIn('PREVARGTEQ:SPHERES_KNOWLEDGE_OF_MANY_SHAPES,1', records['Shifter Shifting Style'])
        for tag in ('PREVARGTEQ:SPHERES_SHIFTER_LEVEL,6', 'MULT:YES', 'STACK:NO',
                    'CHOOSE:WEAPONPROFICIENCY|PC,TYPE=Natural', 'BONUS:WEAPONPROF=%LIST|DAMAGESIZE|1'):
            self.assertIn(tag, improved_attack)
        self.assertIn('ABILITY:Spheres Magic Talent|AUTOMATIC|Alteration - Mimicry', records['Shifter Learned Behavior'])
        fortification = records['Shifter Fortification (Ex) (requires shifter level 6)']
        self.assertIn('PREVARLT:SPHERES_SHIFTER_FORTIFICATION_COUNT,min(3,floor(SPHERES_SHIFTER_LEVEL/6))', fortification)
        self.assertIn('BONUS:VAR|SPHERES_SHIFTER_FORTIFICATION_PERCENT|25', fortification)
        self.assertIn('CHOOSE:NUMCHOICES=5|STRING|Acid|Cold|Electricity|Fire|Sonic', greater)
        self.assertIn('PREVARGTEQ:ShifterImmunity Acid,1', greater)
        self.assertIn('MOVE:Fly,30', records['Shifter Flight (Ex) (requires shifter 6)'])
        self.assertIn('CHOOSE:NUMCHOICES=3|STRING|Flyby Attack|Hover|Wingover', records['Shifter Flight - Skillful (Ex)'])
        fast = records['Shifter Fast Healing (Ex) (requires quick healing bestial trait - shifter level 10)']
        self.assertIn('PREVARLT:SPHERES_SHIFTER_FAST_HEALING_COUNT,2', fast)
        self.assertIn('BONUS:VAR|SPHERES_SHIFTER_FAST_HEALING_COUNT|1', fast)
        with self.assertRaisesRegex(ValueError, 'Unreviewed Shifter requirement'):
            option_tags('Unknown (requires invented prerequisite)', [])

    def test_shifter_breath_choices_and_progression(self):
        classes, abilities, categories, _ = generate('shifter')
        configs = [line for line in abilities.splitlines() if '\tCATEGORY:Shifter Breath Weapon Configuration\t' in line]
        self.assertEqual(len(configs), 8)
        self.assertIn('ABILITYCATEGORY:Shifter Breath Weapon Configuration', categories)
        self.assertIn('DEFINE:SPHERES_SHIFTER_BREATH_IMPROVED|0', classes)
        for line in configs:
            self.assertIn('PREABILITY:1,CATEGORY=Shifter Bestial Trait,Shifter Breath Weapon (Su)', line)
            self.assertIn('PREVARLT:SPHERES_SHIFTER_BREATH_CONFIGURED,1', line)
        self.assertIn('floor((SPHERES_SHIFTER_LEVEL+1)/2)', abilities)

    def test_hedgewitch_path_class_skills(self):
        from spheres_hedgewitch import path_tags
        _, abilities, _, _ = generate('hedgewitch')
        paths = [line for line in abilities.splitlines() if '\tCATEGORY:Hedgewitch Path\t' in line]
        self.assertEqual(len(paths), 21)
        self.assertTrue(all('\tCSKILL:' in line for line in paths))
        academia = next(line for line in paths if line.startswith('Hedgewitch Academia\t'))
        self.assertIn('CSKILL:Knowledge (Geography)|Knowledge (Nature)|Knowledge (Planes)', academia)
        self.assertIn('BONUS:ABILITYPOOL|Hedgewitch Secret|1', academia)
        self.assertIn('BONUS:VAR|SPHERES_SPELL_POINTS|floor(SPHERES_HEDGEWITCH_LEVEL/2)', academia)
        green = next(line for line in paths if line.startswith('Hedgewitch Green Magic\t'))
        self.assertIn('BONUS:VAR|WildEmpathyLVL|SPHERES_HEDGEWITCH_LEVEL', green)
        self.assertIn('Druid ~ Woodland Stride', green)
        lamentation = next(line for line in paths if line.startswith('Hedgewitch Lamentation\t'))
        self.assertIn('CSKILL:Intimidate|Knowledge (Religion)|Perception', lamentation)
        with self.assertRaisesRegex(ValueError, 'class-skill block'):
            path_tags('No skill list')
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            path_tags('Class Skills: Swim|Fly. Path Benefit: invalid delimiter')

    def test_hedgewitch_academia_mastery(self):
        _, abilities, categories, _ = generate('hedgewitch')
        records = [line for line in abilities.splitlines()
                   if line.startswith('Hedgewitch Academia Mastery - ')]
        self.assertEqual(len(records), 3)
        for stat, record in zip(('INT', 'WIS', 'CHA'), records):
            self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,20', record)
            self.assertIn('BONUS:STAT|' + stat + '|2|PREVARGTEQ:', record)
            self.assertEqual(record.count('PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia'), 2)
        self.assertIn('ABILITYCATEGORY:Hedgewitch Academia Mastery', categories)

    def test_hedgewitch_academia_extra_spell_points(self):
        _, abilities, _, _ = generate('hedgewitch')
        record = next(line for line in abilities.splitlines()
                      if line.startswith('Hedgewitch Academia Extra Spell Points\t'))
        self.assertIn('CATEGORY:Hedgewitch Secret', record)
        self.assertIn('PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia', record)
        self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1', record)
        self.assertIn('MULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE', record)
        self.assertIn('BONUS:VAR|SPHERES_SPELL_POINTS|2', record)

    def test_hedgewitch_general_secret_grants(self):
        classes, abilities, categories, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        for name in ('Champion', 'Combat Talent', 'Magical Skill'):
            self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1', records['Hedgewitch ' + name])
            self.assertIn('[PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia]', records['Hedgewitch ' + name])
            self.assertIn('STACK:YES', records['Hedgewitch ' + name])
        for name in ('Arcane Builder', 'Extra Magic Item', 'Metamagic Master'):
            self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', records['Hedgewitch ' + name])
        self.assertIn('DEFINE:SPHERES_COMBAT_TALENTS|0', classes)
        self.assertIn('FOLLOWERS:Familiar|1', records['Hedgewitch Familiar'])
        self.assertIn('BONUS:VAR|FamiliarMasterLVL|SPHERES_HEDGEWITCH_LEVEL|TYPE=Base.STACK', abilities)
        self.assertIn('ABILITYCATEGORY:Hedgewitch Champion Feat', categories)
        master = records['Hedgewitch Metamagic Master']
        self.assertIn('PREFEAT:1,TYPE=Metamagic', master)
        self.assertIn('CHOOSE:FEAT|TYPE=Metamagic,PC', master)
        self.assertIn('MULT:YES\tSTACK:NO', master)
        builder = records['Hedgewitch Arcane Builder']
        self.assertIn('MULT:YES\tSTACK:NO', builder)
        self.assertIn('BONUS:SITUATION|Spellcraft=Craft %LIST|4', builder)
        self.assertNotIn('BONUS:SKILL|Spellcraft|4', builder)

    def test_shifter_class_feature_grants_use_source_levels(self):
        classes, abilities, _, _ = generate('shifter')
        for level, name in ((1, 'Wild Empathy'), (3, 'Endurance'), (7, 'Enhanced Physicality'),
                            (8, 'Poison Immunity'), (12, 'Disease Immunity')):
            line = next(line for line in classes.splitlines() if line.startswith(str(level) + '\t'))
            self.assertIn('ABILITY:Special Ability|AUTOMATIC|Shifter ' + name + ' Mechanics', line)
        self.assertIn('BONUS:STAT|CON|2+2*floor((SPHERES_SHIFTER_LEVEL-7)/6)|TYPE=Inherent', abilities)

    def test_shifter_natural_attacks_use_size_qualified_abilities(self):
        from spheres_shifter import natural_weapons
        text = natural_weapons()
        _, abilities, _, _ = generate('shifter')
        for name in ('Bite', 'Claws', 'Gore'):
            self.assertIn('ABILITY:Special Ability|AUTOMATIC|Shifter ' + name + ' Natural Weapons S|PRESIZEEQ:S', abilities)
            self.assertIn('Shifter ' + name + ' Natural Weapons S\tCATEGORY:Special Ability\tVISIBLE:NO\tPRESIZEEQ:S', text)
        self.assertIn('*2,1d4', text)
        self.assertEqual(text.count('*1,1d6'), 2)
        self.assertEqual((DATA / 'spheres_shifter_natural_weapons.lst').read_text(), text)

    def test_wraith_ghostly_talents_are_path_restricted(self):
        classes, abilities, categories, _ = generate('wraith')
        self.assertIn('DEFINE:SPHERES_WRAITH_GHOSTLY_TALENTS|0', classes)
        ghostly = next(line for line in abilities.splitlines() if line.startswith('Wraith Ghostly Talent\t'))
        for tag in ('MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                    'PREABILITY:1,CATEGORY=Wraith Haunt Path,TYPE=SpheresWraithPath',
                    'BONUS:VAR|SPHERES_WRAITH_GHOSTLY_TALENTS|1'):
            self.assertIn(tag, ghostly)
        self.assertNotIn('SPHERES_MAGIC_TALENTS', ghostly)
        death = next(line for line in categories.splitlines() if line.startswith('ABILITYCATEGORY:Wraith Ghostly Death Talent\t'))
        self.assertIn('CATEGORY:Spheres Magic Talent\tTYPE:Death', death)
        self.assertIn('POOL:0', death)
        path = next(line for line in abilities.splitlines() if line.startswith('Wraith Path of the Despoiler\tCATEGORY:Wraith Haunt Path\t'))
        self.assertIn('BONUS:ABILITYPOOL|Wraith Ghostly Death Talent|SPHERES_WRAITH_GHOSTLY_TALENTS', path)

    def test_wraith_expanded_paths_match_targets_without_granting_base_features(self):
        _, abilities, categories, _ = generate('wraith')
        self.assertIn('ABILITYCATEGORY:Wraith Expanded Path', categories)
        target = next(line for line in abilities.splitlines() if line.startswith('Wraith Path of the Poltergeist\tCATEGORY:Wraith Expanded Path\t'))
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Telekinesis Sphere', target)
        self.assertIn('!PREABILITY:1,CATEGORY=Wraith Haunt Path,Wraith Path of the Poltergeist', target)
        self.assertNotIn('BONUS:', target)
        self.assertNotIn('CSKILL:', target)
        improved = next(line for line in abilities.splitlines() if line.startswith('Wraith Path of the Poltergeist\tCATEGORY:Wraith Improved Expanded Path\t'))
        self.assertIn('PREVARGTEQ:SPHERES_WRAITH_LEVEL,12', improved)
        self.assertIn('PREABILITY:1,CATEGORY=Wraith Expanded Path,Wraith Path of the Poltergeist', improved)

    def test_wraith_reference_capacities_are_not_permanent_incorporeality(self):
        classes, abilities, _, _ = generate('wraith')
        self.assertIn('3\tABILITY:Special Ability|AUTOMATIC|Wraith Haunts', classes)
        self.assertIn('TYPE:SpheresClassFeature.SpheresWraithHaunt', abilities)
        self.assertIn('BONUS:VAR|SPHERES_WRAITH_FORM_UNLIMITED|if(SPHERES_WRAITH_LEVEL>=20,1,0)', abilities)
        self.assertIn('BONUS:VAR|SPHERES_WRAITH_POSSESSION_TARGETS|if(SPHERES_WRAITH_LEVEL<2,0,if(SPHERES_WRAITH_LEVEL<10,1,max(2,SPHERES_CASTING_ABILITY)))', abilities)
        self.assertIn('BONUS:VAR|SPHERES_WRAITH_FORM_ROUNDS|if(SPHERES_WRAITH_LEVEL>=20,0,SPHERES_WRAITH_LEVEL+SPHERES_CASTING_ABILITY)', abilities)
        self.assertNotIn('RACETYPE:Incorporeal', abilities)
        reactive = next(line for line in abilities.splitlines() if line.startswith('Wraith Reactive Possession ('))
        self.assertIn('[PREMULT:2,[PREABILITY:1,CATEGORY=Wraith Haunt Path,Wraith Path of the Poltergeist],'
                      '[PREVARGTEQ:SPHERES_WRAITH_LEVEL,8]]', reactive)
        expanded = next(line for line in abilities.splitlines() if line.startswith('Wraith Expanded Path Possession - Improved ('))
        self.assertIn('PREVARGTEQ:SPHERES_WRAITH_LEVEL,12', expanded)
        self.assertIn('PREABILITY:1,CATEGORY=Wraith Wraith Haunt,'
                      'Wraith Expanded Path Possession (requires haunt path - path sphere of the selected path)', expanded)
        armaments = next(line for line in abilities.splitlines() if line.startswith('Wraith Possess Armaments ('))
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Enhancement Sphere', armaments)
        self.assertIn('PREMULT:1,[PREABILITY:1,CATEGORY=Wraith Wraith Haunt,Wraith Object Ride],'
                      '[PREABILITY:1,CATEGORY=Wraith Haunt Path,Wraith Path of the Poltergeist]', armaments)
        for name, level in (('Ghost Glide (requires wraith 7)', 7),
                            ('Ghost Glide - Improved (requires wraith 11)', 11),
                            ('Share Wraith Form', 3)):
            haunt = next(line for line in abilities.splitlines() if line.startswith('Wraith ' + name + '\t'))
            self.assertIn(f'PREVARGTEQ:SPHERES_WRAITH_LEVEL,{level}', haunt)
            self.assertNotIn('MOVE:', haunt)
        for key, skill in (('Path of the Despoiler', 'Heal'), ('Path of the Anima - Nature', 'Knowledge (Nature)')):
            path = next(line for line in abilities.splitlines() if line.startswith('Wraith ' + key + '\tCATEGORY:Wraith Haunt Path\t'))
            self.assertIn('CSKILL:' + skill, path)
            self.assertIn('SPHERES_WRAITH_LEVEL-floor(SPHERES_WRAITH_LEVEL*3/4)', path)
            self.assertNotIn('SPHERES_WRAITH_LEVEL-SPHERES_CASTER_LEVEL', path)
            self.assertIn(f'BONUS:SKILL|{skill}|floor(SPHERES_WRAITH_LEVEL/2)|TYPE=Insight|PREVARGTEQ:SPHERES_WRAITH_LEVEL,4', path)
        self.assertIn('DEFINE:SPHERES_WRAITH_FORCED_FORM_COUNT|0', classes)
        forced = next(line for line in abilities.splitlines() if line.startswith('Wraith Forced Wraith Form '))
        self.assertIn('PREABILITY:1,CATEGORY=Wraith Wraith Haunt,Wraith Share Wraith Form', forced)
        self.assertIn('PREVARLT:SPHERES_WRAITH_FORCED_FORM_COUNT,2', forced)
        self.assertIn('BONUS:VAR|SPHERES_WRAITH_FORCED_FORM_COUNT|1', forced)
        self.assertNotIn('DEFINE:', forced)
        extra = next(line for line in abilities.splitlines() if line.startswith('Wraith Extra Incorporeality\t'))
        for tag in ('PREVARGTEQ:SPHERES_WRAITH_LEVEL,3', 'MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                    'BONUS:VAR|SPHERES_WRAITH_FORM_ROUNDS|4|PREVARLT:SPHERES_WRAITH_LEVEL,20'):
            self.assertIn(tag, extra)

    def test_commander_logistics_reference_values_do_not_apply_party_bonuses(self):
        from spheres_commander import option_tags
        specialist = option_tags('Commander Logistic Specialty', 'Call In A Specialist')
        self.assertIn('DEFINE:SPHERES_COMMANDER_SPECIALIST_ARRIVAL_HOURS|max(1,24-SPHERES_COMMANDER_LEVEL)', specialist)
        self.assertIn('DEFINE:SPHERES_COMMANDER_SPECIALIST_MAX_DAYS|floor(SPHERES_COMMANDER_LEVEL/2)', specialist)
        self.assertIn('DEFINE:SPHERES_COMMANDER_SPECIALIST_LEVEL|SPHERES_COMMANDER_LEVEL-3', specialist)
        feeding = option_tags('Commander Logistic Specialty', 'Field Feeding')
        self.assertIn('DEFINE:SPHERES_COMMANDER_FIELD_FEEDING_ADDITIONAL_CREATURES|10*SPHERES_COMMANDER_LEVEL', feeding)
        self.assertFalse(any(tag.startswith('BONUS:') for tag in specialist + feeding))
        cavalry = option_tags('Commander Logistic Specialty', 'Call In the Cavalry')
        self.assertIn('DEFINE:SPHERES_COMMANDER_CAVALRY_WEEKS|1+floor((SPHERES_COMMANDER_LEVEL-7)/4)', cavalry)
        self.assertIn('DEFINE:SPHERES_COMMANDER_CAVALRY_MOUNTS|SPHERES_COMMANDER_LEVEL', cavalry)
        self.assertFalse(any(tag.startswith(('MOVE:', 'BONUS:MOVE', 'COMPANION:')) for tag in cavalry))

    def test_commander_resources_have_level_gates(self):
        _, abilities, _, _ = generate('commander')
        self.assertIn('BONUS:VAR|SPHERES_COMMANDER_GROUP_FOCUS_USES|max(0,1+floor((SPHERES_COMMANDER_LEVEL-5)/6))', abilities)
        self.assertIn('BONUS:VAR|SPHERES_COMMANDER_ACTIVE_ENHANCED_TACTICS|if(SPHERES_COMMANDER_LEVEL<2,0,if(SPHERES_COMMANDER_LEVEL<10,1,if(SPHERES_COMMANDER_LEVEL<20,2,3)))', abilities)

    def test_commander_terrain_bonuses_are_situational(self):
        from spheres_commander import option_tags
        for title in ('Desert', 'Jungle', 'Mountain (including hills)', 'Plains',
                      'Urban', 'Underground', 'Water (above and below the surface)'):
            tags = option_tags('Commander Battlefield Specialist', title)
            self.assertTrue(any(tag.startswith('BONUS:SITUATION|') for tag in tags))
            self.assertFalse(any(tag.startswith('BONUS:SKILL|') for tag in tags))
        self.assertIn('BONUS:SITUATION|Survival=Scavenge food in plains terrain|max(1,max(CHA,INT))|TYPE=Competence',
                      option_tags('Commander Battlefield Specialist', 'Plains'))

    def test_commander_options_require_the_feature_level(self):
        _, abilities, _, _ = generate('commander')
        for category, level in (("Enhanced Tactic", 2), ("Battlefield Specialist", 3),
                                ("Logistic Specialty", 7)):
            records = [line for line in abilities.splitlines()
                       if f'CATEGORY:Commander {category}\t' in line]
            self.assertTrue(records)
            for record in records:
                self.assertIn(f'PREVARGTEQ:SPHERES_COMMANDER_LEVEL,{level}\t', record)

    def test_expert_coordinator_grants_repeatable_teamwork_choices(self):
        _, abilities, categories, _ = generate('commander')
        record = next(line for line in abilities.splitlines() if line.startswith('Commander Expert Coordinator\t'))
        for tag in ('MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                    'BONUS:ABILITYPOOL|Commander Teamwork Feat|1'):
            self.assertIn(tag, record)
        self.assertIn('ABILITYCATEGORY:Commander Teamwork Feat\tCATEGORY:FEAT\tTYPE:Teamwork', categories)

    def test_feytouched_is_level_twenty_and_does_not_change_race(self):
        classes, abilities, _, _ = generate('fey-adept')
        grant = 'ABILITY:Special Ability|AUTOMATIC|Fey Adept Feytouched'
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines() if grant in line], ['20'])
        record = next(line for line in abilities.splitlines() if line.startswith('Fey Adept Feytouched\t'))
        self.assertIn('DR:10/cold iron', record)
        self.assertIn('BONUS:SAVE|ALL|2|TYPE=Luck', record)
        self.assertNotIn('RACETYPE:', record)
        self.assertNotIn('TEMPLATE:', record)
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines()
                          if 'ABILITY:Special Ability|AUTOMATIC|Fey Adept See in Darkness' in line], ['14'])
        self.assertIn('VISION:See in Darkness\t', abilities)
        vision = next(line for line in classes.splitlines() if line.startswith('2\t'))
        self.assertIn("VISION:Darkvision (30')", vision)
        self.assertIn('BONUS:VISION|Darkvision|30', vision)
        self.assertIn(',max(1,CHA+floor(SPHERES_FEY_ADEPT_LEVEL/2)))', abilities)
        self.assertIn('BONUS:VAR|SPHERES_FEY_ADEPT_SHADOWMARK_PENALTY|1+floor((max(SPHERES_FEY_ADEPT_LEVEL,SPHERES_HEDGEWITCH_UMBRAL_LEVEL,SPHERES_SURREAL_STRIKE_LEVEL)-1)/6)', abilities)
        self.assertIn('BONUS:VAR|SPHERES_FEY_ADEPT_MASTER_ILLUSIONIST_ROUNDS|max(1,floor(SPHERES_FEY_ADEPT_LEVEL/2))', abilities)

    def test_umbral_shadowmark_and_scoped_secrets(self):
        classes, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        self.assertIn('Fey Adept Shadowmark Dice (Reference)', records['Hedgewitch Umbral'])
        eyes = records['Hedgewitch Umbral Eyes of Black']
        self.assertIn('VISION:Darkvision (SPHERES_HEDGEWITCH_LEVEL*5)|PREABILITY:', eyes)
        self.assertIn('BONUS:VISION|Darkvision|SPHERES_HEDGEWITCH_LEVEL*5|PREABILITY:', eyes)
        sculptor = records['Hedgewitch Umbral Improved Shadow Sculptor']
        self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', sculptor)
        self.assertIn('PREVARLT:SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS,2', sculptor)
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS|0', classes)
        self.assertNotIn('DEFINE:', sculptor)
        self.assertNotIn('BONUS:VAR|SPHERES_CASTER_LEVEL', sculptor)
        self.assertIn('ABILITYCATEGORY:Hedgewitch Shadowstuff Feat', generate('hedgewitch')[2])
        self.assertIn('BONUS:ABILITYPOOL|Hedgewitch Shadowstuff Feat|1', records['Hedgewitch Umbral Shadowstuff'])

    def test_exorcism_capacities_are_not_global_combat_bonuses(self):
        classes, abilities, _, _ = generate('hedgewitch')
        records = {line.split('\t')[0]: line for line in abilities.splitlines()}
        self.assertIn('SPHERES_CASTING_ABILITY+4+2*(SPHERES_HEDGEWITCH_LEVEL-1)', records['Hedgewitch Exorcism'])
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_SANCTION_ROUNDS|0', classes)
        ward = records['Hedgewitch Exorcism Warding Sanction']
        self.assertIn('PREABILITY:1,CATEGORY=Spheres Magic Talent,Protection Sphere', ward)
        self.assertIn('BONUS:VAR|SPHERES_HEDGEWITCH_WARD_ENABLED|1', ward)
        self.assertNotIn('BONUS:VAR|SPHERES_HEDGEWITCH_WARD_CL', ward)
        self.assertIn('DEFINE:SPHERES_HEDGEWITCH_WARD_CL|if(SPHERES_HEDGEWITCH_WARD_ENABLED>0,SPHERES_CL_PROTECTION+SPHERES_HEDGEWITCH_LEVEL-floor(SPHERES_HEDGEWITCH_LEVEL*3/4),0)', generate('hedgewitch')[0])
        self.assertNotIn('BONUS:VAR|SPHERES_CL_PROTECTION', ward)
        for name, grand in (('Enduring Exorcism', False), ('Greater Sanction', True), ('Moral High-Ground', True)):
            record = records['Hedgewitch Exorcism ' + name]
            self.assertIn('|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Exorcism', record)
            self.assertNotIn('BONUS:COMBAT', record)
            self.assertNotIn('MULT:YES', record)
            if grand:
                self.assertIn('PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10', record)

    def test_symbiat_defenses_use_upstream_progression(self):
        classes, _, _, _ = generate('symbiat')
        levels = {line.split('\t')[0]: line for line in classes.splitlines()}
        for level, ability in ((2, 'Evasion'), (3, 'Trap Sense'), (4, 'Uncanny Dodge ~ Base'), (9, 'Improved Evasion')):
            self.assertIn('ABILITY:Special Ability|AUTOMATIC|' + ability, levels[str(level)])
        self.assertIn('BONUS:VAR|TrapSenseBonus|floor(SPHERES_SYMBIAT_LEVEL/3)', levels['3'])
        self.assertIn('BONUS:SKILL|Sense Motive,Perception|floor(SPHERES_SYMBIAT_LEVEL/2)', levels['2'])
        self.assertIn('BONUS:MOVEADD|TYPE=Walk|10*min(6,floor(SPHERES_SYMBIAT_LEVEL/3))', levels['3'])
        self.assertNotIn('BONUS:SKILL|Sense Motive,Perception', levels['1'])
        self.assertNotIn('BONUS:MOVEADD', levels['2'])
        self.assertIn('BONUS:SITUATION|Perception=Avoid being surprised|floor(SPHERES_SYMBIAT_LEVEL/3)', levels['3'])
        for level in (4, 8):
            self.assertIn('BONUS:VAR|UncannyDodgeLVL|1', levels[str(level)])
        self.assertEqual(classes.count('BONUS:VAR|UncannyDodgeFlankingLevel|SPHERES_SYMBIAT_LEVEL'), 1)

    def test_sentinel_reserve_and_second_wind_are_not_permanent_hp(self):
        classes, abilities, _, _ = generate('sentinel')
        grant = 'ABILITY:Special Ability|AUTOMATIC|Sentinel Second Wind'
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines() if grant in line], ['3'])
        self.assertIn('DEFINE:SPHERES_SENTINEL_SECOND_WIND_DICE|floor(SPHERES_SENTINEL_LEVEL/2)', abilities)
        self.assertIn('DEFINE:SPHERES_SENTINEL_SECOND_WIND_BONUS|WIS', abilities)
        self.assertIn('BONUS:VAR|SPHERES_SENTINEL_RESERVE_TEMPORARY_HP|2*BAB+WIS', abilities)
        self.assertNotIn('BONUS:HP', abilities)

    def test_sentinel_wise_reflexes_is_capped_optional_replacement(self):
        classes, abilities, _, _ = generate('sentinel')
        grant = 'ABILITY:Special Ability|AUTOMATIC|Sentinel Wise Reflexes'
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines() if grant in line], ['1'])
        record = next(line for line in abilities.splitlines() if line.startswith('Sentinel Wise Reflexes\t'))
        for target in ('COMBAT|INITIATIVE', 'SAVE|Reflex'):
            self.assertIn(f'BONUS:{target}|max(0,min(WIS,SPHERES_SENTINEL_LEVEL)-DEX)|TYPE=Ability', record)

    def test_sentinel_damage_reduction_is_additive(self):
        classes, abilities, _, _ = generate('sentinel')
        grant = 'ABILITY:Special Ability|AUTOMATIC|Sentinel Dedicated Defense'
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines() if grant in line], ['2'])
        record = next(line for line in abilities.splitlines() if line.startswith('Sentinel Dedicated Defense\t'))
        self.assertIn('DR:0/-', record)
        self.assertIn('BONUS:DR|-|1+floor((SPHERES_SENTINEL_LEVEL-2)/4)', record)

    def test_thaumaturge_fixture_honors_ability_score(self):
        from pcgen_thaumaturge import character_fixture
        for score in (3, 7, 10, 18, 30):
            lines = character_fixture(2, score).splitlines()
            self.assertEqual([line for line in lines if line.startswith('STAT:INT|')],
                             [f'STAT:INT|SCORE:{score}'])
            self.assertIn('STAT:WIS|SCORE:10', lines)
        for score in (2, 31):
            with self.assertRaises(ValueError):
                character_fixture(2, score)

    def test_thaumaturge_persistent_benefits_and_master_choices(self):
        classes, abilities, categories, _ = generate('thaumaturge')
        grant = 'ABILITY:Special Ability|AUTOMATIC|Thaumaturge Occult Knowledge'
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines() if grant in line], ['2'])
        self.assertIn('BONUS:SKILL|TYPE.Knowledge,Spellcraft,Use Magic Device|min(5,1+floor((SPHERES_THAUMATURGE_LEVEL-2)/4))', abilities)
        self.assertIn('10+floor(SPHERES_THAUMATURGE_LEVEL/2)+SPHERES_CASTING_ABILITY', abilities)
        choices = [line for line in abilities.splitlines() if line.startswith('Thaumaturge Master Invoker - ')]
        self.assertEqual(len(choices), 11)
        self.assertFalse(any('Rebuke Death' in line for line in choices))
        for line in choices:
            self.assertIn('PREVARGTEQ:SPHERES_THAUMATURGE_LEVEL,20', line)
            self.assertIn('PREABILITY:1,CATEGORY=Thaumaturge Invocations,Thaumaturge ', line)
        category = next(line for line in categories.splitlines() if line.startswith('ABILITYCATEGORY:Thaumaturge Master Invoker\t'))
        self.assertIn('POOL:if(SPHERES_THAUMATURGE_LEVEL>=20,2,0)', category)

    def test_invocations_are_fixed_level_grants_not_choices(self):
        from spheres_thaumaturge import INVOCATION_LEVELS, invocation_records
        source = json.loads((SNAPSHOTS / 'thaumaturge.json').read_text())
        options = source_options(source, 'Invocations')
        classes, abilities, categories, _ = generate('thaumaturge')
        levels = {line.split('\t')[0]: line for line in classes.splitlines()}
        for title, at in INVOCATION_LEVELS.items():
            self.assertIn(f'ABILITY:Thaumaturge Invocations|AUTOMATIC|Thaumaturge {title}', levels[str(at)])
            record = next(line for line in abilities.splitlines() if line.startswith(f'Thaumaturge {title}\t'))
            self.assertIn(f'PREVARGTEQ:SPHERES_THAUMATURGE_LEVEL,{at}', record)
        category = next(line for line in categories.splitlines() if line.startswith('ABILITYCATEGORY:Thaumaturge Invocations\t'))
        self.assertIn('EDITABLE:NO', category)
        self.assertIn('POOL:0', category)
        self.assertNotIn('ABILITY:Thaumaturge Invocations|TYPE:NORMAL', fixture('thaumaturge', 20))
        for bad in (options[:-1], options + [options[0]],
                    [(title, body.replace('At 3rd level,', 'At 4th level,')) for title, body in options]):
            with self.assertRaises(ValueError):
                invocation_records(bad)

    def test_gravewalker_grants_immunity_without_changing_creature_type(self):
        classes, abilities, _, _ = generate('soul-weaver')
        grant = 'ABILITY:Special Ability|AUTOMATIC|Soul Weaver Gravewalker'
        self.assertEqual([line.split('\t')[0] for line in classes.splitlines() if grant in line], ['20'])
        record = next(line for line in abilities.splitlines() if line.startswith('Soul Weaver Gravewalker\t'))
        self.assertIn('Supernatural.Immunity', record)
        self.assertIn('ASPECT:Immunity|Nonlethal Damage, Ability Drain, Energy Drain', record)
        self.assertNotIn('TEMPLATE:', record)
        self.assertNotIn('RACETYPE:', record)

    def test_blessings_follow_channel_polarity_and_class_level(self):
        from spheres_soul_weaver import blessing_records
        source = json.loads((SNAPSHOTS / 'soul-weaver.json').read_text())
        positive = source_options(source, 'List of Blessings')
        negative = source_options(source, 'List of Blights')
        _, abilities, _, _ = generate('soul-weaver')
        records, grants = blessing_records(positive, negative)
        self.assertEqual(len(records), 10)
        for polarity, options in (('Positive', positive), ('Negative', negative)):
            channel = next(line for line in abilities.splitlines()
                           if line.startswith(f'Soul Weaver {polarity} Channel\t'))
            for (title, _), level in zip(options, (2, 6, 10, 14, 18)):
                self.assertIn(f'ABILITY:Special Ability|AUTOMATIC|Soul Weaver {title}|'
                              f'PREVARGTEQ:SPHERES_SOUL_WEAVER_LEVEL,{level}', channel)
            self.assertEqual(len(grants[polarity]), 5)
        for bad in (positive[:-1], list(reversed(positive)),
                    [(title, body.replace('At 6th level,', 'At 5th level,')) for title, body in positive]):
            with self.assertRaises(ValueError):
                blessing_records(bad, negative)

    def test_nexus_powers_are_automatic_at_their_source_levels(self):
        from spheres_soul_weaver import NEXUS_LEVELS, nexus_records
        source = json.loads((SNAPSHOTS / 'soul-weaver.json').read_text())
        options = source_options(source, 'Bound Nexus (Su)')
        classes, abilities, categories, _ = generate('soul-weaver')
        levels = {line.split('\t')[0]: line for line in classes.splitlines()}
        for name, at in NEXUS_LEVELS.items():
            grant = 'ABILITY:Soul Weaver Nexus Powers|AUTOMATIC|Soul Weaver ' + name
            self.assertIn(grant, levels[str(at)])
            record = next(line for line in abilities.splitlines() if line.startswith('Soul Weaver ' + name + '\t'))
            self.assertIn(f'PREVARGTEQ:SPHERES_SOUL_WEAVER_LEVEL,{at}', record)
        category = next(line for line in categories.splitlines() if line.startswith('ABILITYCATEGORY:Soul Weaver Nexus Powers\t'))
        self.assertIn('EDITABLE:NO', category)
        self.assertIn('POOL:0', category)
        for bad in (options[:-1], options + [options[0]],
                    [(name, body.replace('At 4th level,', 'At 5th level,')) for name, body in options]):
            with self.assertRaises(ValueError):
                nexus_records(bad)

    def test_soul_weaver_resource_modifiers_are_distinct(self):
        classes, abilities, _, _ = generate('soul-weaver')
        self.assertIn('BONUS:VAR|SPHERES_SOUL_WEAVER_CHANNEL_USES|max(1,3+CHA)', abilities)
        self.assertIn('BONUS:VAR|SPHERES_SOUL_WEAVER_CHANNEL_DC|10+floor(SPHERES_SOUL_WEAVER_LEVEL/2)+CHA', abilities)
        self.assertIn('BONUS:VAR|SPHERES_SOUL_WEAVER_NEXUS_DC|10+floor(SPHERES_SOUL_WEAVER_LEVEL/2)+SPHERES_CASTING_ABILITY', abilities)
        self.assertIn('BONUS:VAR|SPHERES_SOUL_WEAVER_BOUND_SOULS|max(1,3+SPHERES_CASTING_ABILITY)', abilities)
        first = next(line for line in classes.splitlines() if line.startswith('1\t'))
        self.assertIn('Soul Weaver Channel Uses (Reference)', first)
        self.assertIn('Soul Weaver Bound Souls (Reference)', first)

    def test_extra_feat_feature_markers_start_at_second_level(self):
        for slug, name, feature in (("mageknight", "Mageknight", "Mystic Combat"),
                                    ("shifter", "Shifter", "Bestial Trait")):
            classes, abilities, categories, metadata = generate(slug)
            marker = name + " " + feature + " Feature"
            levels = {line.split('\t')[0]: line for line in classes.splitlines()}
            self.assertNotIn(marker, levels['1'])
            self.assertIn('ABILITY:Special Ability|AUTOMATIC|' + marker, levels['2'])
            self.assertIn('TYPE:SpheresClassFeature.Spheres' + feature.replace(' ', ''), abilities)

    def test_sphere_mastery_preserves_other_classes_caster_levels(self):
        for slug, sphere in (('shifter', 'ALTERATION'), ('eliciter', 'MIND')):
            abilities = generate(slug)[1]
            level = 'SPHERES_' + slug.upper() + '_LEVEL'
            self.assertIn(f'BONUS:VAR|SPHERES_CL_{sphere}|{level}-floor({level}*3/4)', abilities)
            self.assertNotIn(f'{level}-SPHERES_CASTER_LEVEL', abilities)

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
        class_lines, feature_lines, _, _ = generate('eliciter')
        markers = [line for line in feature_lines.splitlines() if 'TYPE:SpheresClassFeature.SpheresEmotion' in line]
        self.assertEqual(len(markers), 1)
        self.assertTrue(markers[0].startswith('Eliciter Class Features 2\t'))
        levels = {line.split('\t')[0]: line for line in class_lines.splitlines()}
        self.assertNotIn('Eliciter Class Features 2', levels['1'])
        self.assertIn('ABILITY:Special Ability|AUTOMATIC|Eliciter Class Features 2', levels['2'])
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

    def test_technician_trapfinding_is_situational_only_for_perception(self):
        records = generate('technician')[1]
        line = next(line for line in records.splitlines()
                    if line.startswith('Technician Trapfinding (Reference)\t'))
        self.assertIn('BONUS:SKILL|Disable Device|SPHERES_TECHNICIAN_TRAPFINDING|TYPE=Trapfinding', line)
        self.assertIn('BONUS:SITUATION|Perception=Trapfinding|SPHERES_TECHNICIAN_TRAPFINDING|TYPE=Trapfinding', line)
        self.assertNotIn('BONUS:SKILL|Perception', line)
        self.assertNotIn('BONUS:SKILL|Disable Device', generate('technician')[0])

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
        armored = striker_tags('Armored Striker')
        for tag in ('MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                    'PREVARLT:SPHERES_STRIKER_ARMORED_COUNT,2',
                    'BONUS:VAR|SPHERES_STRIKER_ARMORED_COUNT|1'):
            self.assertIn(tag, armored)
        self.assertIn('DEFINE:SPHERES_STRIKER_ARMORED_COUNT|0', striker_resources())
        self.assertEqual(striker_tags('Unarmored Striker'), [
            'PREVARGTEQ:SPHERES_STRIKER_LEVEL,2',
            'ABILITY:Spheres Combat Talent|AUTOMATIC|Equipment - Unarmored Training'])
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
                     [number(row[j]) + (2 if slug == 'fey-adept' and level == 20 else 0) for j in (2, 3, 4)])
                    self.assertEqual(result["talents"] - (2 if details["magic"] else 0)
                                     - (slug == "mageknight"), number(row[headers.index("Magic Talents") if "Magic Talents" in headers else headers.index("Talents") if details["magic"] else headers.index("Combat Talents")]))
                    if details["magic"]:
                        self.assertEqual(result["caster_level"], number(row[headers.index("Caster Level")]))
                        self.assertEqual(result["spell_points"], level + (level // 2 if slug == 'hedgewitch' else 0))
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
        self.assertIn('DEFINE:SPHERES_MAGE_FEINT_CL|max(SPHERES_CASTER_LEVEL,SPHERES_CL_ILLUSION)+'
                      'SPHERES_MAGEKNIGHT_LEVEL-floor(SPHERES_MAGEKNIGHT_LEVEL/2)', option_tags('Weirding Adept'))
        self.assertFalse(any(t.startswith('BONUS:VAR|SPHERES_CL_ILLUSION|') for t in option_tags('Weirding Adept')))


if __name__ == "__main__":
    unittest.main()