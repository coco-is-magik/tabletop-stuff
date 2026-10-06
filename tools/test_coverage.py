"""Coverage accounting must not silently turn missing metadata into completion."""
import json
import unittest

from spheres_coverage import DATA, REPORT, build, render, summarize


class CoverageTests(unittest.TestCase):
    def test_received_effects_are_separate_from_talent_completion(self):
        report = build()
        effects = report['received_effect_templates']
        self.assertIn('Protection Effect - Slippery', effects['spheres_protection_effects.lst'])
        self.assertIn('Enhancement Effect - Physical Enhancement - STR',
                      effects['spheres_enhancement_effects.lst'])
        for keys in effects.values():
            self.assertEqual(keys, sorted(set(keys)))
        self.assertEqual(report['generated_basic_talents']['records'],
                         len(json.loads((DATA / 'catalog-review.json').read_text())))

    def test_generated_report_current(self):
        self.assertEqual(REPORT.read_text(), render())

    def test_unresolved_counts_use_structured_fields_not_prose(self):
        rows = [{"key": "Example", "mechanics": [], "text": "All fine",
                 "unresolved_prerequisites": ["Unmodeled requirement"]}]
        result = summarize(rows, unresolved=True)
        self.assertEqual(result["records_with_unresolved_prerequisites"], 1)
        self.assertEqual(result["unresolved_prerequisites"],
                         {"Example": ["Unmodeled requirement"]})
        self.assertEqual(result["records_with_recorded_mechanics"], 0)

    def test_duplicate_and_missing_fields_fail(self):
        row = {"key": "Example", "mechanics": []}
        with self.assertRaises(ValueError):
            summarize([row, row])
        with self.assertRaises(KeyError):
            summarize([{"key": "Example"}])
        with self.assertRaises(KeyError):
            summarize([row], unresolved=True)

    def test_every_referenced_variable_is_defined_in_the_campaign(self):
        # A DEFINE that references an undefined SPHERES_ variable silently resolves
        # to 0 in PCGen, so a typo would quietly disable a mechanic. Every variable
        # used by a recorded mechanic must be defined by some campaign record.
        import re
        defined = set()
        for path in DATA.glob("*.lst"):
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("#"):
                    continue
                defined.update(re.findall(r"DEFINE:([A-Za-z_][A-Za-z0-9_]*)", line))
                defined.update(re.findall(r"BONUS:VAR\|([A-Za-z_][A-Za-z0-9_]*)", line))
        self.assertIn("SPHERES_CASTER_LEVEL", defined)
        missing = {}
        for name in ("catalog-mechanics.json", "feat-mechanics.json", "trait-mechanics.json"):
            overrides = json.loads((DATA / name).read_text())
            for key, tags in overrides.items():
                for tag in tags:
                    for variable in re.findall(r"(?<![A-Za-z0-9_])(SPHERES_[A-Za-z0-9_]+)", tag):
                        if variable not in defined:
                            missing.setdefault(variable, set()).add(key)
        self.assertEqual(missing, {})

    def test_partition_and_determinism(self):
        report = build()
        self.assertEqual(render(), render())
        for name in ("generated_basic_talents", "feats", "traits"):
            group = report[name]
            self.assertEqual(group["records"], group["records_with_recorded_mechanics"]
                             + len(group["records_without_recorded_mechanics"]))
        self.assertEqual(sum(g["records"] for g in report["talents_by_sphere"].values()),
                         report["generated_basic_talents"]["records"])
        feats = json.loads((DATA / "feat-catalog.json").read_text())
        self.assertEqual(report["feats"]["records_with_unresolved_prerequisites"],
                         sum(bool(row["unresolved_prerequisites"]) for row in feats))


if __name__ == "__main__":
    unittest.main()