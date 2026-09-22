"""Tool regression tests. Synthetic exports are not PCGen integration evidence."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from spheres import DATA, ROOT, check_package, compare_export
from pcgen_spheres_smoke import CASES, smoke, validate_result, validate_selection


class SpheresToolTest(unittest.TestCase):
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