"""Live sphere-specific caster-level stacking across casting classes and paths."""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from pcgen_class_catalog import fixture
from pcgen_elementalist_class import fixture as elementalist_fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gate', choices=('save', 'reload'))
    parser.add_argument('--work', type=Path)
    parser.add_argument('--shifter', type=int, choices=range(0, 11), default=5)
    parser.add_argument('--eliciter', type=int, choices=range(0, 11), default=3)
    parser.add_argument('--adept', type=int, choices=range(0, 11), default=2)
    parser.add_argument('--elementalist', type=int, choices=range(0, 11), default=0)
    parser.add_argument('--wraith', type=int, choices=range(0, 11), default=0)
    parser.add_argument('--hedgewitch', type=int, choices=range(0, 11), default=0)
    parser.add_argument('--mageknight', type=int, choices=range(0, 11), default=0)
    args = parser.parse_args()
    if (args.gate == 'reload') != (args.work is not None):
        parser.error('--work is required only for reload')
    if args.gate == 'save' and not 1 <= args.shifter + args.eliciter + args.adept + args.elementalist + args.wraith + args.hedgewitch + args.mageknight <= 20:
        parser.error('Total levels must be 1-20')
    work = args.work if args.work is not None else workspace()
    print('Sphere mastery evidence:', work, flush=True)
    cp = classpath()
    saved = work / 'saved.pcg'
    source = saved
    if args.gate == 'save':
        source = work / 'mastery.pcg'
        lines = []
        for slug, level in (('shifter', args.shifter), ('eliciter', args.eliciter), ('fey-adept', args.adept),
                            ('elementalist', args.elementalist), ('wraith', args.wraith), ('hedgewitch', args.hedgewitch),
                            ('mageknight', args.mageknight)):
            if not level:
                continue
            character = elementalist_fixture(level) if slug == 'elementalist' else fixture(slug, level)
            text = [line for line in character.splitlines() if not line.startswith('ABILITY:')]
            lines.extend(text if not lines else [line for line in text if line.startswith(('CLASS:', 'CLASSABILITIESLEVEL:'))])
        source.write_text('\n'.join(lines) + '\n')
        (work / 'export.txt').write_text('level=|TOTALLEVELS|\n')
        with (work / 'compile.log').open('w') as stream:
            subprocess.run([str(JAVA.with_name('javac')), '--enable-preview', '--release', '16',
                            '-cp', cp, '-d', str(work), str(ROOT / 'tools/PcgenSpheresGates.java'),
                            str(ROOT / 'tools/PcgenSphereMastery.java')], stdout=stream,
                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    gate = 'mastery-' + args.gate
    log = work / (gate + '.log')
    with log.open('w') as stream:
        subprocess.run([str(JAVA), '--enable-preview', '-Djava.awt.headless=true',
                        f'-Dpcgen.config={work}', '-cp', cp + ':' + str(work),
                        'pcgen.gui2.facade.PcgenSphereMastery', str(source), str(work / 'export.txt'),
                        str(work / (gate + '.txt')), 'config.ini', gate, str(saved)],
                       cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=110, check=True)
    validate_gate(log, gate)
    print('PASS:', gate)


if __name__ == '__main__':
    main()