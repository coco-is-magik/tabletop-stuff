"""Invalidate cached sums when the pinned PCGen active bonus map changes."""
import argparse
from pathlib import Path
import subprocess
import tempfile

from pcgen_movement_fix import rebuild_jar
from pcgen_spheres_smoke import JAVA, ROOT, PCGEN, classpath

OLD = '''\tprivate static void totalBonusesForType(Map<String, String> nonStackMap, Map<String, String> stackMap,'''
NEW = OLD.replace('private static void', 'private void')
OLD_WRITE = '\t\tputActiveBonusMap(fullyQualifiedBonusType, String.valueOf(FullValue), targetMap);'
NEW_WRITE = OLD_WRITE + '''
\t\t// Formula evaluation can cache a subtotal while this map is being built.
\t\tif (targetMap == activeBonusMap)
\t\t{
\t\t\tcachedActiveBonusSumsMap.clear();
\t\t}'''


def patched_source(text):
    if text.count(NEW) == 1 and text.count(NEW_WRITE) == 1 and OLD not in text:
        return text
    if text.count(OLD) != 1 or text.count(OLD_WRITE) != 1 or NEW_WRITE in text or NEW in text:
        raise ValueError('Unexpected bonus implementation; review the pinned patch')
    return text.replace(OLD, NEW, 1).replace(OLD_WRITE, NEW_WRITE, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    relative = 'pcgen/core/BonusManager'
    source = PCGEN / 'code/src/java' / (relative + '.java')
    original = source.read_text()
    fixed = patched_source(original)
    if not args.apply:
        if original != fixed:
            raise ValueError('Bonus cache fix is not applied; run with --apply')
        print('PASS: bonus-cache source fix present (does not verify jar)')
        return
    jar = PCGEN / 'build/libs/pcgen-6.09.06.jar'
    with tempfile.TemporaryDirectory(prefix='pcgen-bonus-cache-', dir=ROOT / 'build') as directory:
        work = Path(directory)
        temporary_source = work / 'BonusManager.java'
        temporary_source.write_text(fixed)
        subprocess.run([str(JAVA.with_name('javac')), '--enable-preview', '--release', '16',
                        '-cp', classpath(), '-d', str(work), str(temporary_source)],
                       stdin=subprocess.DEVNULL, timeout=30, check=True)
        classes = sorted(work.glob(relative + '*.class'))
        if not classes or len(classes) > 10:
            raise ValueError('Unexpected bonus-class compilation output')
        replacement = work / jar.name
        rebuild_jar(jar, replacement, {str(path.relative_to(work)): path.read_bytes() for path in classes})
        replacement.chmod(jar.stat().st_mode)
        replacement.replace(jar)
        source.write_text(fixed)
    print('PASS: rebuilt bonus-cache fix; run live stacking/save/reload gates')


if __name__ == '__main__':
    main()