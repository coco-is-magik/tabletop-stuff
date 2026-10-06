"""Live level-limited extra-option feat caps, refunds and saved selections."""
import argparse
import json
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from pcgen_class_catalog import fixture
from spheres_extra_options import OPTIONS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gate', choices=('save', 'reload'))
    parser.add_argument('--work', type=Path)
    parser.add_argument('--class-name', choices=[row[0] for row in OPTIONS.values()], default='Striker')
    parser.add_argument('--level', type=int, choices=range(1, 21), default=17)
    args = parser.parse_args()
    if (args.gate == 'reload') != (args.work is not None):
        parser.error('--work is required only for reload')
    work = args.work if args.work else workspace()
    cp = classpath()
    print('Extra options evidence:', work, flush=True)
    saved = work / 'saved.pcg'
    source = saved
    if args.gate == 'save':
        name, (_, category, levels) = next((name, row) for name, row in OPTIONS.items() if row[0] == args.class_name)
        cap = sum(args.level >= minimum for minimum in levels)
        (work / 'options.json').write_text(json.dumps([name, category, str(cap),
                                                      'SPHERES_EXTRA_' + args.class_name.upper() + '_OPTIONS']))
        source = work / 'options.pcg'
        source.write_text(fixture(args.class_name.lower(), args.level))
        (work / 'export.txt').write_text('level=|TOTALLEVELS|\n')
        with (work / 'compile.log').open('w') as stream:
            subprocess.run([str(JAVA.with_name('javac')), '--enable-preview', '--release', '16',
                            '-cp', cp, '-d', str(work), str(ROOT / 'tools/PcgenSpheresGates.java'),
                            str(ROOT / 'tools/PcgenExtraOptions.java')], stdout=stream,
                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    gate = 'extra-options-' + args.gate
    log = work / (gate + '.log')
    with log.open('w') as stream:
        subprocess.run([str(JAVA), '--enable-preview', '-Djava.awt.headless=true',
                        f'-Dpcgen.config={work}', '-cp', cp + ':' + str(work),
                        'pcgen.gui2.facade.PcgenExtraOptions', str(source), str(work / 'export.txt'),
                        str(work / (gate + '.txt')), 'config.ini', gate, str(saved),
                        *json.loads((work / 'options.json').read_text())],
                       cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, timeout=110, check=True)
    validate_gate(log, gate)
    print('PASS:', gate)


if __name__ == '__main__':
    main()