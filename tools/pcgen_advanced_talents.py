"""Live advanced-talent eligibility, selection, refund and save/reload.

Each case adds a base sphere and optional prerequisite talent, then asserts that
PCGen's own prerequisite check accepts or rejects the advanced talent, that the
sphere talent counter includes it, and that removal refunds the pool. The first
selectable case is retained through save/reload.
"""
import argparse
import subprocess
from pathlib import Path

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture as magic_fixture

# (base sphere, prerequisite talent or '-', advanced talent, select|blocked,
#  counter variable, expected counter value at the level-20 INT Incanter)
CASES = (
    ("Alteration Sphere", "Alteration - Greater Changes", "Alteration - Extreme Changes",
     "select", "SPHERES_ALTERATION_TALENTS", 3),
    ("Alteration Sphere", "-", "Alteration - Fusion", "blocked", "SPHERES_ALTERATION_TALENTS", 1),
    ("War Sphere", "-", "War - Penetrating Totems", "select", "SPHERES_WAR_TALENTS", 2),
    ("Conjuration Sphere", "-", "Conjuration - Channel Companion", "select",
     "SPHERES_CONJURATION_TALENTS", 2),
    ("Blood Sphere", "-", "Blood - Essence Manipulation", "blocked", "SPHERES_BLOOD_TALENTS", 1),
    ("Alteration Sphere", "-", "Alteration - Energy Manipulation", "blocked",
     "SPHERES_ALTERATION_TALENTS", 1),
    ("Creation Sphere", "-", "Creation - Fleshcraft", "blocked", "SPHERES_CREATION_TALENTS", 1),
)


def run(phase, work=None):
    if phase == 'reload' and (work is None or not (work / 'saved.pcg').is_file()):
        raise ValueError('Reload requires --work with a saved.pcg')
    work = work or workspace()
    cp = classpath()
    print('Advanced talent evidence:', work, flush=True)
    char = work / 'advanced.pcg'
    cat = 'Spheres Magic Talent'
    raw = magic_fixture(20, 'INT')
    char.write_text('\n'.join(line for line in raw.splitlines()
                              if not line.startswith('ABILITY:' + cat + '|')) + '\n')
    case_file = work / 'advanced.tsv'
    case_file.write_text('\n'.join('\t'.join(str(field) for field in case) for case in CASES) + '\n')
    (work / 'export.txt').write_text('level=|TOTALLEVELS|\n')
    sources = [ROOT / 'tools/PcgenSpheresGates.java', ROOT / 'tools/PcgenAdvancedTalents.java']
    with (work / 'compile.log').open('w') as stream:
        subprocess.run([str(JAVA.with_name('javac')), '--enable-preview', '--release', '16', '-cp', cp,
                        '-d', str(work), *map(str, sources)],
                       stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                       timeout=30, check=True)
    saved = work / 'saved.pcg'
    gate = 'advanced-' + phase
    log = work / (gate + '.log')
    command = [str(JAVA), '--enable-preview', '-Djava.awt.headless=true', f'-Dpcgen.config={work}',
               '-cp', cp + ':' + str(work), 'pcgen.gui2.facade.PcgenAdvancedTalents',
               str(char if phase == 'save' else saved), str(work / 'export.txt'),
               str(work / (gate + '.txt')), 'config.ini', gate, str(saved), str(case_file), cat]
    with log.open('w') as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                       stderr=subprocess.STDOUT, timeout=200, check=True)
    validate_gate(log, gate)
    print('PASS:', gate, '-', len(CASES), 'advanced-talent cases')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('save', 'reload'))
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if (args.phase == 'reload') != (args.work is not None):
        parser.error('--work is required only for reload')
    run(args.phase, args.work)
