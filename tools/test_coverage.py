"""Coverage accounting must not silently turn missing metadata into completion."""
import json
import unittest

from spheres_coverage import DATA, REPORT, build, render, summarize


class CoverageTests(unittest.TestCase):
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