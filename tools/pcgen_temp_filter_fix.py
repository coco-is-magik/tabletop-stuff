"""Clear a removed temporary effect's disabled filter in pinned PCGen."""
import argparse
from pathlib import Path
import subprocess
import tempfile

from pcgen_movement_fix import rebuild_jar
from pcgen_spheres_smoke import JAVA, ROOT, PCGEN, classpath

OLD = '\t\tappliedTempBonuses.removeElement(tempBonus);'
NEW = '''\t\t// A later application of this effect must not inherit its disabled state.
\t\ttheCharacter.unsetTempBonusFilter(tempBonus.toString());
''' + OLD


def patched_source(text):
    if text.count(NEW) == 1 and text.count(OLD) == 1:
        return text
    if text.count(OLD) != 1 or 'unsetTempBonusFilter(tempBonus.toString());\n\t\tappliedTempBonuses' in text:
        raise ValueError('Unexpected temporary-effect removal; review pinned patch')
    return text.replace(OLD, NEW, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    relative = 'pcgen/gui2/facade/CharacterFacadeImpl'
    source = PCGEN / 'code/src/java' / (relative + '.java')
    original = source.read_text()
    fixed = patched_source(original)
    if not args.apply:
        if fixed != original:
            raise ValueError('Temporary-effect filter fix is not applied; run with --apply')
        print('PASS: temporary-effect filter source fix present (does not verify jar)')
        return
    jar = PCGEN / 'build/libs/pcgen-6.09.06.jar'
    with tempfile.TemporaryDirectory(prefix='pcgen-temp-filter-', dir=ROOT / 'build') as directory:
        work = Path(directory)
        temporary_source = work / 'CharacterFacadeImpl.java'
        temporary_source.write_text(fixed)
        subprocess.run([str(JAVA.with_name('javac')), '--enable-preview', '--release', '16',
                        '-cp', classpath(), '-d', str(work), str(temporary_source)],
                       stdin=subprocess.DEVNULL, timeout=30, check=True)
        classes = sorted(work.glob(relative + '*.class'))
        if not classes or len(classes) > 40:
            raise ValueError('Unexpected character-facade compilation output')
        replacement = work / jar.name
        rebuild_jar(jar, replacement, {str(path.relative_to(work)): path.read_bytes() for path in classes})
        replacement.chmod(jar.stat().st_mode)
        replacement.replace(jar)
        source.write_text(fixed)
    print('PASS: rebuilt temporary-effect filter fix; run live removal/reapplication gates')


if __name__ == '__main__':
    main()