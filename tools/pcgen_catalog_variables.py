"""Live reference-variable arithmetic, selection and save/reload round trips.

Each case selects a base sphere and one talent, then asserts the value PCGen
computes for a reference variable at the level-20 INT Incanter fixture (CL 20).
This exercises select -> calculate -> remove -> save/reload for the reference
mechanics, which the catalog round trip only covers at the base-sphere level.
"""
import argparse
import subprocess
from pathlib import Path

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture as magic_fixture

# (base sphere, talent, reference variable, expected value at CL 20)
CASES = (
    ("War Sphere", "War - Totem Of Speed", "SPHERES_WAR_TOTEM_SPEED_FEET", 25),
    ("War Sphere", "War - Mass Rally", "SPHERES_WAR_MASS_RALLY_ADDITIONAL_TARGETS", 10),
    ("War Sphere", "War - Totem Of Courage", "SPHERES_WAR_COURAGE_ATTACK", 3),
    ("Blood Sphere", "Blood - Piercing Blood", "SPHERES_BLOOD_PIERCING_BLOOD_D6", 10),
    ("Destruction Sphere", "Destruction - Sculpt Blast", "SPHERES_DESTRUCTION_SCULPT_BLAST_RADIUS", 30),
    ("Dark Sphere", "Dark - Edge Of Night", "SPHERES_DARK_EDGE_OF_NIGHT_D6", 6),
    ("Death Sphere", "Death - Vampiric Strike", "SPHERES_DEATH_VAMPIRIC_STRIKE_D6", 10),
    ("Light Sphere", "Light - Sunstroke", "SPHERES_LIGHT_SUNSTROKE_D4", 10),
    ("Mana Sphere", "Mana - Ignition", "SPHERES_MANA_IGNITION_D8", 7),
    ("Mind Sphere", "Mind - Esteem", "SPHERES_MIND_ESTEEM_BONUS", 10),
    ("Nature Sphere", "Nature - Repress Element", "SPHERES_NATURE_REPRESS_ELEMENT_RADIUS", 25),
    ("Time Sphere", "Time - Eject", "SPHERES_TIME_EJECT_ROUNDS", 20),
    ("Warp Sphere", "Warp - Wormhole", "SPHERES_WARP_WORMHOLE_SQUARES", 11),
    ("Creation Sphere", "Creation - Lengthened Creation", "SPHERES_CREATION_LENGTHENED_HOURS", 20),
    ("Divination Sphere", "Divination - Augury", "SPHERES_DIVINATION_AUGURY_CHANCE", 90),
    ("Protection Sphere", "Protection - Armored Magic", "SPHERES_PROTECTION_ARMORED_MAGIC_SHIELD", 5),
    ("Illusion Sphere", "Illusion - Blur", "SPHERES_ILLUSION_BLUR_MISS_CHANCE", 50),
    ("Fate Sphere", "Fate - Strength", "SPHERES_FATE_STRENGTH_BONUS", 7),
    ("Fallen Fey Sphere", "Fallen Fey - Fey Beauty", "SPHERES_FALLENFEY_FEY_BEAUTY", 5),
    ("Enhancement Sphere", "Enhancement - Bestow Intelligence", "SPHERES_ENHANCEMENT_BESTOW_INTELLIGENCE_SCORE", 16),
    ("War Sphere", "War - Absolute Totem", "SPHERES_WAR_ABSOLUTE_TOTEM_HARDNESS", 20),
    ("Dark Sphere", "Dark - Snagging Darkness", "SPHERES_DARK_SNAGGING_CMB", 24),
    ("Protection Sphere", "Protection - Spell Ward", "SPHERES_PROTECTION_SPELL_WARD_SR", 30),
    ("Mana Sphere", "Mana - Control Resistance", "SPHERES_MANA_CONTROL_RESISTANCE_SR", 31),
    ("Weather Sphere", "Weather - Squamish", "SPHERES_WEATHER_SQUAMISH_CMB", 24),
    ("Protection Sphere", "Protection - Energy Resistance", "SPHERES_PROTECTION_ENERGY_RESISTANCE_REDUCTION", 30),
    ("Protection Sphere", "Protection - Missile Shield", "SPHERES_PROTECTION_MISSILE_SHIELD_REDUCTION", 25),
    ("Protection Sphere", "Protection - Obstruction", "SPHERES_PROTECTION_OBSTRUCTION_DR", 10),
    ("Light Sphere", "Light - Periscope", "SPHERES_LIGHT_PERISCOPE_DETECT_DC", 40),
    ("Light Sphere", "Light - Encompassing Light", "SPHERES_LIGHT_ENCOMPASSING_SIZE_STEPS", 2),
    ("Dark Sphere", "Dark - Shadow Coterie", "SPHERES_DARK_SHADOW_COTERIE_ADDITIONAL", 4),
    ("Fate Sphere", "Fate - The Fool", "SPHERES_FATE_THE_FOOL_PENALTY_REDUCTION", 2),
    ("Mana Sphere", "Mana - Friction", "SPHERES_MANA_FRICTION_EXTRA_COST", 2),
    ("Creation Sphere", "Creation - Potent Alteration", "SPHERES_CREATION_POTENT_ALTERATION_DAMAGE", 20),
    ("Illusion Sphere", "Illusion - Swift Figments", "SPHERES_ILLUSION_SWIFT_FIGMENTS_SPEED", 75),
    ("Fallen Fey Sphere", "Fallen Fey - Summon Fairy", "SPHERES_FALLENFEY_SUMMON_FAIRY_CR", 6),
    ("War Sphere", "War - Tactical Totem", "SPHERES_WAR_TACTICAL_TOTEM_FEATS", 2),
    ("Technomancy Sphere", "Technomancy - Compound Hacking", "SPHERES_TECHNOMANCY_COMPOUND_HACKING", 6),
    ("Technomancy Sphere", "Technomancy - Sprite Legion", "SPHERES_TECHNOMANCY_SPRITE_LEGION", 10),
)


def run(phase, work=None):
    if phase == 'reload' and (work is None or not (work / 'saved.pcg').is_file()):
        raise ValueError('Reload requires --work with a saved.pcg')
    work = work or workspace()
    cp = classpath()
    print('Catalog variable evidence:', work, flush=True)
    char = work / 'variables.pcg'
    cat = 'Spheres Magic Talent'
    raw = magic_fixture(20, 'INT')
    char.write_text('\n'.join(line for line in raw.splitlines()
                              if not line.startswith('ABILITY:' + cat + '|')) + '\n')
    case_file = work / 'variables.tsv'
    case_file.write_text('\n'.join('\t'.join(str(f) for f in case) for case in CASES) + '\n')
    (work / 'export.txt').write_text('level=|TOTALLEVELS|\n')
    sources = [ROOT / 'tools/PcgenSpheresGates.java', ROOT / 'tools/PcgenCatalogVariables.java']
    with (work / 'compile.log').open('w') as stream:
        subprocess.run([str(JAVA.with_name('javac')), '--enable-preview', '--release', '16', '-cp', cp,
                        '-d', str(work), *map(str, sources)],
                       stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    saved = work / 'saved.pcg'
    gate = 'variables-' + phase
    log = work / (gate + '.log')
    command = [str(JAVA), '--enable-preview', '-Djava.awt.headless=true', f'-Dpcgen.config={work}',
               '-cp', cp + ':' + str(work), 'pcgen.gui2.facade.PcgenCatalogVariables',
               str(char if phase == 'save' else saved), str(work / 'export.txt'),
               str(work / (gate + '.txt')), 'config.ini', gate, str(saved), str(case_file), cat]
    with log.open('w') as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                       stderr=subprocess.STDOUT, timeout=180, check=True)
    validate_gate(log, gate)
    print('PASS:', gate, '-', len(CASES), 'reference values')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('save', 'reload'))
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if (args.phase == 'reload') != (args.work is not None):
        parser.error('--work is required only for reload')
    run(args.phase, args.work)
