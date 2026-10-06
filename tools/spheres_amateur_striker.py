"""Amateur Striker's permanent choices; combat tension remains player-tracked."""
import json
import re
from pathlib import Path

FEAT = 'PREFEAT:1,Amateur Striker'
ELIGIBLE = '!PRECLASS:1,Striker=1'
CATEGORIES = ('Amateur Striker Method', 'Amateur Striker Technique')
EXPANDED = 'Expanded Tension Technique'


def expanded_tags():
    return ['MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
            'BONUS:ABILITYPOOL|' + EXPANDED + '|1']


def feat_tags():
    return ['DEFINE:SPHERES_AMATEUR_STRIKER_CAPACITY|0', 'DEFINE:SPHERES_EXTRA_STRIKER_OPTIONS|0',
            'BONUS:VAR|SPHERES_AMATEUR_STRIKER_CAPACITY|max(0,CON)|' + ELIGIBLE] + [
                'BONUS:ABILITYPOOL|' + category + '|1|' + ELIGIBLE for category in CATEGORIES]


def records():
    source = json.loads((Path(__file__).resolve().parents[1] /
                         'testdata/spheres/catalog-source/striker.json').read_text())
    sections = {section['heading']: section['text'] for section in source['sections']}
    methods = ('Offensive Pressure', 'Defensive Determination', 'Maneuvering Momentum')
    techniques = ('Expert Guard', 'Fiery Offense', 'Light Step', 'Stalwart Form',
                  'Timely Dodge', 'Critical Knuckle', 'Perfect Offensive', 'Swift Focus',
                  'Rapid Pummel', 'Second Chance', 'Speed Step')
    abilities, categories = [], []
    for category, names, heading in zip(CATEGORIES, (methods, techniques),
                                        ('Tension (Ex)', 'Tension Techniques (Ex)')):
        categories.append(f'ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\t'
                          'EDITPOOL:NO\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tDISPLAYLOCATION:Spheres')
        for name in names:
            match = re.search(r'^' + re.escape(name) + r': (.+)$', sections[heading], re.M)
            if not match:
                raise ValueError('Missing pinned tension rule: ' + name)
            description = match[1].replace('|', '/')
            abilities.append(f'Amateur Striker - {name}\tCATEGORY:{category}\t{FEAT}\t{ELIGIBLE}\t'
                             f'DESC:{description} Tension expenditure and combat conditions are player-tracked. '
                             'The technique choice is permanent unless retraining is approved.')
            if category == CATEGORIES[1]:
                abilities[-1] += ('\t!PREABILITY:1,CATEGORY=' + EXPANDED + ',Expanded Tension - ' + name)
    return abilities, categories


def expanded_records():
    """Base techniques only: base Strikers already know every one of these."""
    amateur, _ = records()
    abilities = []
    for record in amateur:
        if '\tCATEGORY:' + CATEGORIES[1] + '\t' not in record:
            continue
        name = record.split('\t')[0].removeprefix('Amateur Striker - ')
        description = record.split('\tDESC:', 1)[1].split('\t', 1)[0]
        abilities.append(f'Expanded Tension - {name}\tCATEGORY:{EXPANDED}\tPREFEAT:1,{EXPANDED}\t'
                         f'{FEAT}\t{ELIGIBLE}\t!PREABILITY:1,CATEGORY={CATEGORIES[1]},Amateur Striker - {name}\t'
                         f'DESC:{description} Cannot be used on the same turn as another tension technique.')
    category = (f'ABILITYCATEGORY:{EXPANDED}\tCATEGORY:{EXPANDED}\tEDITABLE:YES\tEDITPOOL:NO\t'
                'POOL:0\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tDISPLAYLOCATION:Spheres')
    return abilities, [category]