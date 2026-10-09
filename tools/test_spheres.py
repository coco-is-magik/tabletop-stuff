"""Tool regression tests. Synthetic exports are not PCGen integration evidence."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from spheres import DATA, ROOT, check_package, compare_export
from pcgen_spheres_smoke import CASES, smoke, validate_result, validate_selection, classpath
from pcgen_spheres_gates import FEATURE_GATES, compare_core, run_gate, validate_gate
from spheres_progression_fixtures import fixture, expected as progression_expected, TALENTS
from spheres_incanter_domains import render as render_domains, OUTPUT as DOMAIN_OUTPUT
from spheres_incanter_bloodlines import render as render_bloodlines, OUTPUT as BLOODLINE_OUTPUT
from pcgen_incanter_class import class_fixture, expected_chassis, validate_chassis, PURCHASES


class SpheresToolTest(unittest.TestCase):
    def test_destruction_summary_exposes_trait_damage(self):
        text = (DATA / "spheres_destruction.lst").read_text()
        sphere = next(line for line in text.splitlines() if line.startswith("Destruction Sphere\t"))
        self.assertIn("DEFINE:SPHERES_DESTRUCTION_TRAIT_DAMAGE|0", sphere)
        self.assertIn("Add %4 trait damage to either blast", sphere)
        self.assertTrue(sphere.endswith("|SPHERES_DESTRUCTION_TRAIT_DAMAGE"))

    def test_incanter_chassis_and_casting_selection(self):
        text = (DATA / "spheres_classes.lst").read_text()
        for tag in ("HD:6", "MAXLEVEL:20", "STARTSKILLPTS:4",
                    "CSKILL:Appraise|TYPE=Craft|Fly|TYPE=Knowledge|Linguistics|TYPE=Profession|Spellcraft",
                    "AUTO:WEAPONPROF|TYPE=Simple"):
            self.assertIn(tag, text)
        self.assertNotIn("AUTO:ARMORPROF", text)
        categories = (DATA / "spheres_categories.lst").read_text()
        self.assertIn("POOL:min(1,SPHERES_SPELL_POOL_LEVELS)", categories)
        core = (DATA / "spheres_core.lst").read_text()
        self.assertIn("DEFINE:SPHERES_CASTING_ABILITY|INT", core)
        self.assertIn("BONUS:VAR|SPHERES_CASTING_ABILITY|WIS-INT", core)
        self.assertIn("BONUS:VAR|SPHERES_CASTING_ABILITY|CHA-INT", core)

    def test_thin_class_acceptance_contract(self):
        self.assertEqual(len(PURCHASES), 6)
        for level in range(1, 21):
            for casting in ("INT", "WIS", "CHA"):
                for points in range(6):
                    text = class_fixture(level, casting, points)
                    self.assertEqual(text.count("ABILITY:Incanter Specialization|"), len(PURCHASES[points]))
                    self.assertNotIn("KEY:Sorcerer Bloodline", text)
                expected = expected_chassis(level, casting)
                validate_chassis("\n".join(f"{key}={value:+d}" for key, value in expected.items()), expected)
        for args in ((0, "INT", 0), (21, "INT", 0), (1, "STR", 0), (1, "INT", -1), (1, "INT", 6)):
            with self.assertRaises(ValueError):
                class_fixture(*args)
        for invalid in ("", "level=+1\nlevel=+1", "level=|TOTALLEVELS|", "level=+2"):
            with self.assertRaises(ValueError):
                validate_chassis(invalid, {"level": 1})

    def test_ultimate_admixture_does_not_import_original_alternative(self):
        audit = (ROOT / "docs/incanter-completion-audit.md").read_text()
        self.assertIn("already-owned alternative occurs only in Original", audit)
        active = next(line for line in (DATA / "spheres_incanter.lst").read_text().splitlines()
                      if line.startswith("Active Admixture Adept\t"))
        self.assertIn("ABILITY:Spheres Magic Talent|AUTOMATIC|Admixture", active)
        self.assertNotIn("BONUS:ABILITYPOOL|Spheres Magic Talent", active)

    def test_half_orc_favored_bloodline_does_not_advance_power_unlocks(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        self.assertIn("BONUS:VAR|BloodlineLVL|floor(SPHERES_INCANTER_HALF_ORC_BLOODLINE_COUNT/5)", text)
        reward = next(line for line in text.splitlines() if line.startswith("Incanter Half-Orc Bloodline Power\t"))
        self.assertIn("PRERACE:1,Half-Orc", reward)
        self.assertIn("PREVARGTEQ:BloodlineLVL,1", reward)
        self.assertNotIn("BONUS:VAR|BloodlineProgressionLVL", reward)

    def test_halfling_favored_channel_is_fractional_and_gated(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        reward = next(line for line in text.splitlines() if line.startswith("Incanter Halfling Channel Uses\t"))
        self.assertIn("PRERACE:1,Halfling", reward)
        self.assertIn("PREVARGTEQ:SPHERES_CHANNEL_USES,1", reward)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_HALFLING_CHANNEL_COUNT|1", reward)
        self.assertIn("BONUS:VAR|SPHERES_CHANNEL_FAVORED_USES|floor(SPHERES_INCANTER_HALFLING_CHANNEL_COUNT/2)", text)
        channel = (DATA / "spheres_incanter.lst").read_text()
        self.assertEqual(channel.count("BONUS:VAR|SPHERES_CHANNEL_USES|3+SPHERES_CASTING_ABILITY+SPHERES_CHANNEL_FAVORED_USES"), 2)

    def test_halfling_favored_movement_burst_is_independent_of_channel(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        burst = next(line for line in text.splitlines() if line.startswith("Incanter Halfling Movement Burst Uses\t"))
        self.assertIn("PRERACE:1,Halfling", burst)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", burst)
        self.assertIn("PREABILITY:1,CATEGORY=Special Ability,Incanter Movement Burst", burst)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_HALFLING_BURST_COUNT|1", burst)
        self.assertIn("DEFINE:SPHERES_INCANTER_HALFLING_BURST_COUNT|0", text)
        self.assertIn("BONUS:VAR|SPHERES_MOVEMENT_BURST_FAVORED_USES|floor(SPHERES_INCANTER_HALFLING_BURST_COUNT/2)", text)
        movement = next(line for line in (DATA / "spheres_incanter.lst").read_text().splitlines()
                        if line.startswith("Incanter Movement Burst\t"))
        self.assertIn("DEFINE:SPHERES_MOVEMENT_BURST_FAVORED_USES|0", movement)
        self.assertIn("BONUS:VAR|SPHERES_MOVEMENT_BURST_USES|3+SPHERES_CASTING_ABILITY+SPHERES_MOVEMENT_BURST_FAVORED_USES", movement)
        self.assertNotIn("SPHERES_CHANNEL_FAVORED_USES", movement)

    def test_orc_favored_movement_burst_requires_specialization_ability(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        reward = next(line for line in text.splitlines() if line.startswith("Incanter Orc Movement Burst Uses\t"))
        self.assertIn("PRERACE:1,Orc", reward)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", reward)
        self.assertIn("PREABILITY:1,CATEGORY=Special Ability,Incanter Movement Burst", reward)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_ORC_BURST_COUNT|1", reward)
        self.assertIn("DEFINE:SPHERES_INCANTER_ORC_BURST_COUNT|0", text)
        self.assertIn("BONUS:VAR|SPHERES_MOVEMENT_BURST_FAVORED_USES|floor(SPHERES_INCANTER_ORC_BURST_COUNT/2)", text)

    def test_orc_air_domain_reward_is_independent_of_movement_burst(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        reward = next(line for line in text.splitlines() if line.startswith("Incanter Orc Lightning Arc Uses\t"))
        self.assertIn("PRERACE:1,Orc", reward)
        self.assertIn("PREABILITY:1,CATEGORY=Special Ability,Domain Power ~ Lightning Arc", reward)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_ORC_AIR_COUNT|1", reward)
        self.assertIn("BONUS:VAR|LightningArcTimes|floor(SPHERES_INCANTER_ORC_AIR_COUNT/2)", text)
        self.assertIn("Incanter Air Domain Favored Uses", (DATA / "spheres_classes.lst").read_text())
        self.assertNotIn("SPHERES_INCANTER_ORC_BURST_COUNT", reward)

    def test_human_favored_class_bonus_counts_once_per_six(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        self.assertIn("TYPE:FavoredClass\tVISIBLE:DISPLAY", text)
        self.assertIn("TYPE:FavoredClass\tVISIBLE:DISPLAY\tPREVARGTEQ:SPHERES_INCANTER_LEVEL,1", text)
        self.assertIn("BONUS:ABILITYPOOL|Favored Class Bonus|SPHERES_INCANTER_LEVEL", text)
        self.assertEqual(text.count("BONUS:VAR|SPHERES_MAGIC_TALENTS|floor(SPHERES_INCANTER_HUMAN_FCB_COUNT/6)+floor(SPHERES_INCANTER_HALF_ELF_FCB_COUNT/6)"), 1)
        human = next(line for line in text.splitlines() if line.startswith("Incanter Human Magic Talent\t"))
        self.assertIn("PRERACE:1,Human", human)
        self.assertIn("!PRERACE:1,Half-Elf", human)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", human)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_HUMAN_FCB_COUNT|1", human)
        self.assertNotIn("BONUS:VAR|SPHERES_MAGIC_TALENTS", human)

    def test_aasimar_favored_class_bonus_requires_two_selections(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        self.assertIn("BONUS:SKILL|Spellcraft|floor(SPHERES_INCANTER_AASIMAR_FCB_COUNT/2)|TYPE=FavoredClass", text)
        aasimar = next(line for line in text.splitlines() if line.startswith("Incanter Aasimar Spellcraft\t"))
        self.assertIn("PRERACE:1,Aasimar", aasimar)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", aasimar)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_AASIMAR_FCB_COUNT|1", aasimar)
        self.assertIn('double baseline = pc.getTotalBonusTo("SKILL", "Spellcraft");',
                      (ROOT / "tools/PcgenSpheresGates.java").read_text())
        half_elf = next(line for line in text.splitlines() if line.startswith("Incanter Half-Elf Magic Talent\t"))
        self.assertIn("PRERACE:1,Half-Elf", half_elf)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", half_elf)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_HALF_ELF_FCB_COUNT|1", half_elf)
        self.assertIn("ABILITYCATEGORY:Incanter Elf Favored Metamagic\tCATEGORY:FEAT\tTYPE:Metamagic", (DATA / "spheres_categories_incanter.lst").read_text())
        elf = next(line for line in text.splitlines() if line.startswith("Incanter Elf Metamagic Feat\t"))
        self.assertIn("PRERACE:1,Elf\t!PRERACE:1,Half-Elf", elf)
        self.assertIn("BONUS:ABILITYPOOL|Incanter Elf Favored Metamagic|floor(SPHERES_INCANTER_ELF_FCB_COUNT/6)", text)
        dwarf = next(line for line in text.splitlines() if line.startswith("Incanter Dwarf Item Creation Feat\t"))
        self.assertIn("PRERACE:1,Dwarf", dwarf)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", dwarf)
        self.assertIn("ABILITYCATEGORY:Incanter Dwarf Favored Crafting\tCATEGORY:FEAT\tTYPE:ItemCreation", (DATA / "spheres_categories_incanter.lst").read_text())
        self.assertIn("BONUS:ABILITYPOOL|Incanter Dwarf Favored Crafting|floor(SPHERES_INCANTER_DWARF_FCB_COUNT/6)", text)

    def test_tiefling_favored_concentration_uses_canonical_casting_ability(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        tiefling = next(line for line in text.splitlines() if line.startswith("Incanter Tiefling Concentration\t"))
        self.assertIn("PRERACE:1,Tiefling", tiefling)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", tiefling)
        self.assertIn("BONUS:VAR|SPHERES_INCANTER_TIEFLING_FCB_COUNT|1", tiefling)
        self.assertIn("BONUS:VAR|SPHERES_CONCENTRATION_FAVORED|floor(SPHERES_INCANTER_TIEFLING_FCB_COUNT/2)", text)
        self.assertIn("DEFINE:SPHERES_CONCENTRATION_CHECK|SPHERES_CASTER_LEVEL+SPHERES_CASTING_ABILITY+SPHERES_CONCENTRATION_FAVORED",
                      (DATA / "spheres_core.lst").read_text())
        gate_source = (ROOT / "tools/pcgen_spheres_gates.py").read_text()
        self.assertIn("PCGen's default Tiefling grants +2 Intelligence", gate_source)
        self.assertIn('if gate == "tiefling-favored-save":\n            # PCGen', gate_source)

    def test_gnome_favored_bonus_is_sphere_specific_and_requires_sphere(self):
        text = (DATA / "spheres_incanter_favored.lst").read_text()
        gnome = next(line for line in text.splitlines() if line.startswith("Incanter Gnome Destruction DC\t"))
        self.assertIn("PRERACE:1,Gnome", gnome)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_FAVORED,1", gnome)
        self.assertIn("PREABILITY:1,CATEGORY=Spheres Magic Talent,Destruction Sphere", gnome)
        self.assertIn("BONUS:VAR|SPHERES_DC_DESTRUCTION|floor(SPHERES_INCANTER_GNOME_DESTRUCTION_COUNT/6)", text)
        self.assertNotIn("BONUS:VAR|SPHERES_CASTER_LEVEL|floor(SPHERES_INCANTER_GNOME_DESTRUCTION_COUNT/6)", text)

    def test_all_includes_every_feature_gate(self):
        self.assertEqual(len(FEATURE_GATES), len(set(FEATURE_GATES)))
        self.assertEqual(FEATURE_GATES, (
            "incanter1", "incanter20", "specializations3", "specializations20",
            "spherespec1", "spherespec3", "spherespec20", "spherespec-owned", "spheredraw",
            "domains1", "domains20", "domains-save", "bloodline1", "bloodline20", "bloodline-save", "healer-save",
            "destruction1", "destruction3", "destruction8", "destruction20",
            "sword1", "sword5", "sword20", "sword-save", "human-favored", "half-elf-favored", "human-favored-save", "elf-favored", "dwarf-favored", "aasimar-favored", "aasimar-favored-save", "tiefling-favored", "tiefling-favored-save", "gnome-favored", "gnome-favored-save", "halfling-favored", "halfling-favored-save", "halfling-burst", "halfling-burst-save", "orc-burst", "orc-burst-save", "orc-air-favored", "orc-air-favored-save", "half-orc-favored", "half-orc-favored-save",
        ))

    def test_local_pcgen_runtime_fallback(self):
        # The local vendor installation must resolve the same pinned PCGen JAR.
        jar = ROOT / "vendor/upstream/pcgen-6.08.00RC10/build/libs/pcgen-6.09.06.jar"
        if jar.is_file():
            self.assertIn(str(jar), classpath())

    def test_sword_birth_contract(self):
        records = (DATA / "spheres_incanter_sword.lst").read_text().splitlines()
        tricks = [line for line in records if "CATEGORY:Incanter Arsenal Trick\t" in line]
        self.assertEqual(len(tricks), 11)
        self.assertEqual(len({line.split("\t")[0] for line in tricks}), 11)
        ultimate = next(line for line in tricks if line.startswith("Ultimate Arena\t"))
        for name, level in (("Arena Patrol", 6), ("Material Arena", 6),
                            ("Dancing Arena", 14), ("Ultimate Arena", 14)):
            record = next(line for line in tricks if line.startswith(name + "\t"))
            self.assertIn(f"PREVARGTEQ:SPHERES_INCANTER_LEVEL,{level}", record)
        self.assertIn("PREABILITY:2,CATEGORY=Incanter Arsenal Trick,Arena Burst,Bound Armory", ultimate)
        self.assertNotIn("BONUS:WEAPON", "\n".join(records))

    def test_arsenal_combat_feat_uses_separate_feat_pool(self):
        categories = (DATA / "spheres_categories_incanter.lst").read_text()
        self.assertIn("ABILITYCATEGORY:Incanter Arsenal Combat Feat\tCATEGORY:FEAT\tTYPE:Combat", categories)
        trick = next(line for line in (DATA / "spheres_incanter_sword.lst").read_text().splitlines()
                     if line.startswith("Combat Feat\t"))
        self.assertIn("MULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE", trick)
        self.assertIn("BONUS:ABILITYPOOL|Incanter Arsenal Combat Feat|1", trick)
        self.assertNotIn("BONUS:ABILITYPOOL|Incanter Bonus Feat", trick)
        self.assertNotIn("Finesse\tCATEGORY:Incanter Arsenal Trick", (DATA / "spheres_incanter_sword.lst").read_text())

    def test_extra_arsenal_trick_requires_active_sword_birth(self):
        feats = (DATA / "spheres_feats.lst").read_text().splitlines()
        extra = next(line for line in feats if line.startswith("Extra Arsenal Trick\t"))
        self.assertIn("PREABILITY:1,CATEGORY=Incanter Active Specialization,Active Sword Birth", extra)
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_LEVEL,5", extra)
        self.assertIn("MULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE", extra)
        self.assertIn("BONUS:ABILITYPOOL|Incanter Arsenal Trick|1", extra)
        self.assertNotIn("IncanterBonus", extra)

    def test_destruction_specialization_contract(self):
        records = (DATA / "spheres_incanter.lst").read_text().splitlines()
        purchase = next(line for line in records if line.startswith("Sphere Specialization (Destruction)\t"))
        active = next(line for line in records if line.startswith("Active Sphere Specialization (Destruction)\t"))
        self.assertIn("COST:3", purchase)
        self.assertIn("COST:2", active)
        # Taking the specialization grants the sphere and its caster level; the paired
        # "- Already Known" variant grants a talent instead. Activation only brings the
        # specialization abilities into effect.
        self.assertIn("ABILITY:Spheres Magic Talent|AUTOMATIC|Destruction Sphere", purchase)
        self.assertIn("BONUS:VAR|SPHERES_CL_DESTRUCTION|1", purchase)
        self.assertIn("Sphere Specialization (Destruction) - Already Known", purchase)
        known = next(line for line in records
                     if line.startswith("Sphere Specialization (Destruction) - Already Known\t"))
        self.assertIn("BONUS:ABILITYPOOL|Incanter Destruction Specialization Talent|1", known)
        self.assertNotIn("ABILITY:Spheres Magic Talent|AUTOMATIC|Destruction Sphere", known)
        self.assertNotIn("ABILITY:Spheres Magic Talent|AUTOMATIC|Destruction Sphere", active)
        self.assertNotIn("BONUS:VAR", active)
        self.assertIn("Incanter Intense Magic|Incanter Movement Burst", active)
        self.assertIn("Incanter Elemental Wall|PREVARGTEQ:SPHERES_INCANTER_LEVEL,8", active)
        self.assertNotIn("Incanter Penetrating Blast", active)
        self.assertNotIn("Incanter Indestructible", active)
        intense = next(line for line in records if line.startswith("Incanter Intense Magic\t"))
        self.assertIn("At level 20 roll twice", intense)

    def test_bloodline_adapters(self):
        text = render_bloodlines()
        self.assertEqual(BLOODLINE_OUTPUT.read_text(), text)
        self.assertEqual(text.count("CATEGORY:Incanter Specialization\t"), 10)
        for forbidden in ("BloodlineArcana", "BloodlineSpells", "BloodlineClassSkill", "BONUS:ABILITYPOOL"):
            self.assertNotIn(forbidden, text)
        self.assertIn("max(CHA,SPHERES_CASTING_ABILITY)", text)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                render_bloodlines(Path(directory))

    def test_domain_adapters(self):
        text = render_domains()
        self.assertEqual(DOMAIN_OUTPUT.read_text(), text)
        self.assertEqual(text.count("CATEGORY:Incanter Specialization\t"), 33)
        self.assertEqual(text.count("CATEGORY:Incanter Active Specialization\t"), 33)
        self.assertNotIn("SPELLLEVEL:", text)
        self.assertNotIn("PREDEITY:", text)
        self.assertNotIn("Death (Pharasma)", text)
        self.assertIn("BONUS:VAR|DomainAirDC|SPHERES_CASTING_ABILITY-CHA", text)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                render_domains(Path(directory))

    def test_incanter_specialization_purchase_activation_contract(self):
        records = (DATA / "spheres_incanter.lst").read_text().splitlines()
        for name, cost in (("Channel Energy", 2), ("Lay on Hands", 2),
                           ("Merciful Healer", 2), ("Familiar", 1), ("Master of Mysteries", 2)):
            purchase = next(line for line in records if line.startswith(name + "\t"))
            active = next(line for line in records if line.startswith("Active " + name + "\t"))
            self.assertIn(f"COST:{cost}", purchase)
            self.assertIn("PREVAREQ:SPHERES_INCANTER_LEVEL,1", purchase)
            self.assertIn(f"PREABILITY:1,CATEGORY=Incanter Specialization,{name}", active)
            self.assertIn(f"COST:{cost}", active)
            self.assertNotIn("BONUS:VAR|SPHERES_INCANTER_SPECIALIZATION_POINTS", active)
        category = (DATA / "spheres_categories_incanter.lst").read_text()
        self.assertIn("POOL:2*floor((SPHERES_INCANTER_LEVEL+1)/2)", category)

    def test_incanter_bonus_data_contract(self):
        categories = (DATA / "spheres_categories.lst").read_text()
        self.assertIn("ABILITYCATEGORY:Incanter Bonus Feat\tCATEGORY:FEAT", categories)
        self.assertIn("POOL:5*min(1,SPHERES_INCANTER_LEVEL)", categories)
        feats = (DATA / "spheres_feats.lst").read_text().splitlines()
        for key in ("Extra Magic Talent", "Extra Spell Points"):
            record = next(line for line in feats if line.startswith(key + "\t"))
            self.assertIn("MULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE", record)
            self.assertIn("TYPE:General.IncanterBonus", record)
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "spheres"
            shutil.copytree(DATA, data)
            (data / "spheres_feats.lst").unlink()
            with self.assertRaises(OSError):
                check_package(data)

    def test_progression_fixtures(self):
        self.assertEqual(len(TALENTS), 20)
        self.assertEqual(TALENTS[0], 4)  # Ultimate: class talent, odd-level bonus, two casting talents.
        self.assertEqual(TALENTS[-1], 32)
        for level in range(1, 21):
            for casting in ("INT", "WIS", "CHA"):
                text = fixture(level, casting)
                self.assertEqual(text.count("CLASSABILITIESLEVEL:"), level)
                self.assertIn(f"STAT:{casting}|SCORE:18", text)
                self.assertEqual(text.count("ABILITY:Spheres Casting Ability|"), 1)
            self.assertEqual(progression_expected(level)["magic_talents"], TALENTS[level - 1])
        for level in (0, 21):
            with self.assertRaises(ValueError):
                fixture(level)
            with self.assertRaises(ValueError):
                progression_expected(level)
        with self.assertRaises(ValueError):
            fixture(1, "STR")

    def test_gate_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "pcgen.log"
            for gate, marker in (("selection", "prerequisites and duplicates"),
                                 ("core-only", "core-only"),
                                 ("core-with-spheres", "core-with-spheres")):
                log.write_text(f"SPHERES_GATES_OK: {marker}\n")
                validate_gate(log, gate)
                for invalid in ("", "SPHERES_GATES_OK: wrong", "SEVERE: failure\n",
                                "LSTERROR: failure\n"):
                    log.write_text(invalid)
                    with self.assertRaises(ValueError):
                        validate_gate(log, gate)
            with self.assertRaises(ValueError):
                run_gate("../unknown")

    def test_core_isolation_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.txt"
            augmented = Path(directory) / "augmented.txt"
            export = "level=1\nbab=1\nhp=12\nfortitude=+4\nreflex=+1\nwill=+0\nac=11\n"
            for path in (baseline, augmented):
                path.write_text(export)
                path.with_name(path.name + ".snapshot").write_text("level=1\nbab=1\n")
            compare_core(baseline, augmented)
            for invalid in ("", export.replace("hp=12", "hp=13"), "hp=|HP|\n"):
                augmented.write_text(invalid)
                with self.assertRaises(ValueError):
                    compare_core(baseline, augmented)
            augmented.write_text(export)
            augmented.with_name(augmented.name + ".snapshot").write_text("level=2\n")
            with self.assertRaises(ValueError):
                compare_core(baseline, augmented)
            augmented.with_name(augmented.name + ".snapshot").unlink()
            with self.assertRaises(OSError):
                compare_core(baseline, augmented)

    def test_selection_evidence_required(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "pcgen.log"
            for text in ("", "SPHERES_SELECTION_OK:",
                         "SPHERES_SELECTION_OK: Destruction Sphere, Searing Blast; spent=0"):
                log.write_text(text)
                with self.assertRaises(ValueError):
                    validate_selection(log)
            log.write_text("SPHERES_SELECTION_OK: Destruction Sphere, Searing Blast; spent=2\n")
            validate_selection(log)

    def test_smoke_result_requires_fresh_valid_output_and_no_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "export.txt"
            log = Path(directory) / "pcgen.log"
            log.write_text("INFO: Loaded character\n")
            with self.assertRaises(ValueError):
                validate_result(output, log, {"a": 1})
            output.write_text("a=1\n")
            validate_result(output, log, {"a": 1})
            for error in ("SEVERE: load failed", "LSTERROR: bad source"):
                log.write_text(error)
                with self.assertRaises(ValueError):
                    validate_result(output, log, {"a": 1})
            log.write_text("INFO: Loaded character\n")
            output.write_text("a=2\n")
            with self.assertRaises(ValueError):
                validate_result(output, log, {"a": 1})
            output.write_text("x" * 16385)
            with self.assertRaises(ValueError):
                validate_result(output, log, {"a": 1})

    def test_smoke_rejects_unimplemented_case(self):
        with self.assertRaises(ValueError):
            smoke("../unknown")

    def test_package(self):
        self.assertIn("PASS", check_package())

    def test_package_accepts_additional_incanter_sources_but_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "spheres"
            shutil.copytree(DATA, data)
            source = "spheres_incanter_extra.lst"
            (data / source).write_text("# New Incanter options\nExample\tCATEGORY:Special Ability\n")
            package = data / "spheres.pcc"
            package.write_text(package.read_text().rstrip("\n") + f"\nABILITY:{source}\n")
            self.assertIn("PASS", check_package(data))
            package.write_text(package.read_text() + f"ABILITY:{source}\n")
            with self.assertRaises(ValueError):
                check_package(data)
            package.write_text(package.read_text().removesuffix(f"ABILITY:{source}\n"))
            (data / source).unlink()
            with self.assertRaises(OSError):
                check_package(data)
            (data / source).write_text("Example\tCATEGORY:Special Ability\n")
            package.write_text(package.read_text().replace("ABILITY:spheres_incanter_sword.lst\n", ""))
            with self.assertRaises(ValueError):
                check_package(data)

    def test_smoke_fixture_coverage(self):
        expected = json.loads((ROOT / "testdata/spheres/expected.json").read_text())
        self.assertEqual(set(CASES), set(expected))
        for case in CASES:
            text = (ROOT / f"testdata/spheres/{case}.pcg").read_text()
            self.assertIn("GAMEMODE:Pathfinder_RPG", text)
            self.assertIn("KEY:Destruction Sphere", text)

    def test_cases_and_export_contract(self):
        cases = json.loads((ROOT / "testdata/spheres/expected.json").read_text())
        template_keys = {line.split("=", 1)[0] for line in
                         (DATA / "spheres_export.txt").read_text().splitlines()}
        for case in cases.values():
            self.assertEqual(template_keys, set(case))
            compare_export("\n".join(f"{k}={v}" for k, v in case.items()), case)

    def test_bad_exports(self):
        for text in ("", "a=2", "a=1\na=1", "a=|VAR.A|", "a=1\nb=2", "a=1.0"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                compare_export(text, {"a": 1})

    def test_missing_reference_and_prerequisite(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "spheres"
            shutil.copytree(DATA, data)
            talents = data / "spheres_destruction.lst"
            talents.write_text(talents.read_text().replace("PREABILITY:", "BROKEN:"))
            with self.assertRaises(ValueError):
                check_package(data)
            talents.unlink()
            with self.assertRaises(OSError):
                check_package(data)


if __name__ == "__main__":
    unittest.main()