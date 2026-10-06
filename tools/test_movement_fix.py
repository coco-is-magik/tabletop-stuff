"""Pinned patch safety and idempotence regression tests."""
import unittest
import tempfile
from pathlib import Path
import warnings
import zipfile

from pcgen_movement_fix import OLD, NEW, patched_source, rebuild_jar


class MovementFixTests(unittest.TestCase):
    def test_single_site_and_idempotence(self):
        original = "before\n" + OLD + "\nafter"
        fixed = patched_source(original)
        self.assertEqual(fixed, "before\n" + NEW + "\nafter")
        self.assertEqual(patched_source(fixed), fixed)

    def test_rejects_missing_duplicate_and_ambiguous_sites(self):
        for source in ("", OLD + OLD, NEW + NEW, OLD + NEW):
            with self.subTest(source=source), self.assertRaises(ValueError):
                patched_source(source)

    def test_jar_preserves_duplicate_resources_and_replaces_only_target(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'original.jar'
            fixed = Path(directory) / 'fixed.jar'
            with zipfile.ZipFile(original, 'w') as jar, warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                jar.writestr('META-INF/LICENSE', 'first')
                jar.writestr('META-INF/LICENSE', 'second')
                jar.writestr('Target.class', b'old')
            rebuild_jar(original, fixed, {'Target.class': b'new'})
            with zipfile.ZipFile(fixed) as jar:
                self.assertEqual([jar.read(entry) for entry in jar.infolist()],
                                 [b'first', b'second', b'new'])
            with self.assertRaises(ValueError):
                rebuild_jar(original, fixed, {'Unknown.class': b'new'})


if __name__ == "__main__":
    unittest.main()