"""Tool regression tests. Synthetic exports are not PCGen integration evidence."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from spheres import DATA, ROOT, check_package, compare_export
from pcgen_spheres_smoke import CASES, smoke, validate_result, validate_selection
from pcgen_spheres_gates import compare_core, run_gate, validate_gate
from spheres_progression_fixtures import fixture, expected as progression_expected, TALENTS
from spheres_incanter_domains import render as render_domains, OUTPUT as DOMAIN_OUTPUT
from spheres_incanter_bloodlines import render as render_bloodlines, OUTPUT as BLOODLINE_OUTPUT


class SpheresToolTest(unittest.TestCase):
    def test_sword_birth_contract(self):
        records = (DATA / "spheres_incanter_sword.lst").read_text().splitlines()
        tricks = [line for line in records if "CATEGORY:Incanter Arsenal Trick\t" in line]
        self.assertEqual(len(tricks), 10)
        self.assertEqual(len({line.split("\t")[0] for line in tricks}), 10)
        ultimate = next(line for line in tricks if line.startswith("Ultimate Arena\t"))
        self.assertIn("PREVARGTEQ:SPHERES_INCANTER_LEVEL,14", ultimate)
        self.assertIn("PREABILITY:2,CATEGORY=Incanter Arsenal Trick,Arena Burst,Bound Armory", ultimate)
        self.assertNotIn("BONUS:WEAPON", "\n".join(records))

    def test_destruction_specialization_contract(self):
        records = (DATA / "spheres_incanter.lst").read_text().splitlines()
        purchase = next(line for line in records if line.startswith("Sphere Specialization (Destruction)\t"))
        active = next(line for line in records if line.startswith("Active Sphere Specialization (Destruction)\t"))
        self.assertIn("COST:3", purchase)
        self.assertIn("COST:2", active)
        self.assertIn("ABILITY:Spheres Magic Talent|AUTOMATIC|Destruction Sphere", active)
        for level in (3, 8, 20):
            self.assertIn(f"PREVARGTEQ:SPHERES_INCANTER_LEVEL,{level}", active)

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