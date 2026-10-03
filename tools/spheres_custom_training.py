"""Custom Training choices reference existing Core weapon proficiencies."""
from spheres import ROOT, records

CATEGORY = 'Spheres Custom Training Weapon'
PROFICIENCIES = ROOT / 'vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game/core_rulebook/cr_profs_weapon.lst'


def weapons():
    result = {}
    for row in records(PROFICIENCIES):
        fields = row.split('\t')
        if fields[0].endswith('.MOD'):
            continue
        key = next((tag[4:] for tag in fields if tag.startswith('KEY:')), fields[0])
        types = {value for tag in fields if tag.startswith('TYPE:')
                 for value in tag[5:].split('.')}
        if types.intersection({'Simple', 'Martial', 'Exotic'}):
            result[key] = 2 if 'Exotic' in types else 1
    return result


def build():
    category = '\t'.join([
        'ABILITYCATEGORY:' + CATEGORY, 'CATEGORY:' + CATEGORY,
        'EDITABLE:YES', 'EDITPOOL:NO', 'FRACTIONALPOOL:NO', 'VISIBLE:QUALIFY',
        'POOL:0', 'PLURAL:Custom Training weapon choices', 'DISPLAYLOCATION:Spheres'])
    prerequisite = 'PREABILITY:1,CATEGORY=Spheres Combat Talent,Equipment - Custom Training'
    choices = ['\t'.join([
        'Custom Training - ' + key, 'CATEGORY:' + CATEGORY, 'COST:' + str(cost),
        prerequisite, 'AUTO:WEAPONPROF|' + key + '|' + prerequisite,
        'DESC:Proficiency in ' + key + '. Exotic weapons cost two of the five training points.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/equipment-sphere#toc86'])
        for key, cost in sorted(weapons().items())]
    return category, choices