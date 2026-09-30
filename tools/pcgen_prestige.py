"""Live multiclass prestige arithmetic and save/reload using the existing harness."""
import argparse
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_class_catalog import fixture
from spheres import compare_export


def run(level, phase, work=None):
    work = workspace() if work is None else work
    print('Prestige evidence:', work, flush=True)
    saved = work / 'saved.pcg'
    character = work / 'prestige.pcg'
    template = work / 'export.txt'
    if phase == 'save':
        raw = fixture('fey-adept', 5)
        raw += f'CLASS:Tempestarii|LEVEL:{level}|SKILLPOOL:0\n'
        raw += ''.join(f'CLASSABILITIESLEVEL:Tempestarii={n}|HITPOINTS:6|SKILLSGAINED:0|SKILLSREMAINING:0\n'
                       for n in range(1, level + 1))
        raw += 'ABILITY:Spheres Magic Talent|TYPE:NORMAL|CATEGORY:Spheres Magic Talent|KEY:Weather Sphere\n'
        character.write_text(raw)
        template.write_text('level=|TOTALLEVELS|\nbab=|VAR.BAB.INTVAL|\n'
                            'fortitude=|CHECK.FORTITUDE.TOTAL|\nreflex=|CHECK.REFLEX.TOTAL|\n'
                            'will=|CHECK.WILL.TOTAL|\ncl=|VAR.SPHERES_CASTER_LEVEL.INTVAL|\n'
                            'sp=|VAR.SPHERES_SPELL_POINTS.INTVAL|\n'
                            'talents=|VAR.SPHERES_MAGIC_TALENTS.INTVAL|\n'
                            'steps=|VAR.SPHERES_TEMPESTARII_WEATHER_STEPS.INTVAL|\n')
    output, log = work / (phase + '.txt'), work / (phase + '.log')
    command = [str(JAVA), '--enable-preview', '-Djava.awt.headless=true', f'-Dpcgen.config={work}',
               '-cp', classpath(), '--source', '16', str(ROOT / 'tools/PcgenClassCatalog.java'),
               str(character if phase == 'save' else saved), str(template), str(output), 'config.ini',
               'M:Weather', 'Special Ability:Tempestarii Rapid Weather', '-']
    if phase == 'save':
        command.append(str(saved))
    with log.open('w') as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                       stderr=subprocess.STDOUT, timeout=90, check=True)
    diagnostics = log.read_text()
    if 'LSTERROR:' in diagnostics or 'SEVERE:' in diagnostics:
        raise ValueError('Prestige load errors: ' + str(log))
    compare_export(output.read_text().replace('=+', '='),
                   {'level': 5 + level, 'bab': 2 + level // 2,
                    'fortitude': 1 + (level + 1) // 3, 'reflex': 1 + (level + 1) // 3,
                    'will': 4 + (level + 1) // 2, 'cl': 5 + level, 'sp': 5 + level,
                    'talents': 7 + level, 'steps': 1 + level})
    print('PASS: Tempestarii multiclass ' + phase)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('save', 'reload'))
    parser.add_argument('--level', type=int, choices=range(1, 6), default=5)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if (args.phase == 'reload') != (args.work is not None):
        parser.error('Only reload requires --work from a save run')
    run(args.level, args.phase, args.work)