"""Tool regression tests. Synthetic exports are not PCGen integration evidence."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from spheres import DATA, ROOT, check_package, compare_export


class SpheresToolTest(unittest.TestCase):
    def test_package(self):
        self.assertIn("PASS", check_package())

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