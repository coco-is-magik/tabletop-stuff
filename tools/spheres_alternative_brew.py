"""Configurable Alternative-Brew reuses loaded Core and Spheres skills."""
from spheres import ROOT, DATA, records

CATEGORY = 'Spheres Alchemy Associated Skill'


def key(skill):
    return 'Alternative-Brew - ' + skill.replace(' (', ' - ').replace(')', '')


def skills():
    paths = [ROOT / 'vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game/core_rulebook/cr_skills.lst',
             DATA / 'spheres_skills.lst']
    return sorted({row.split('\t')[0] for path in paths for row in records(path)
                   if row.startswith(('Craft (', 'Profession (')) and '.MOD\t' not in row})


def build():
    category = '\t'.join([
        'ABILITYCATEGORY:' + CATEGORY, 'CATEGORY:' + CATEGORY,
        'EDITABLE:YES', 'EDITPOOL:NO', 'FRACTIONALPOOL:NO', 'VISIBLE:QUALIFY',
        'POOL:1', 'PLURAL:Alternative-Brew associated skill (GM approval)',
        'DISPLAYLOCATION:Spheres'])
    parent = 'PREABILITY:1,CATEGORY=Spheres Combat Talent,Alchemy Sphere'
    choices = []
    for skill in skills():
        choices.append('\t'.join([
            key(skill), 'CATEGORY:' + CATEGORY, 'TYPE:SpheresAlternativeBrew', parent,
            '!PREABILITY:1,CATEGORY=Special Ability,Martial Drawback - Alternative-Brew (Heal)',
            'BONUS:SKILLRANK|' + skill + '|min(TL,5*SPHERES_ALCHEMY_TALENTS)|TYPE=SpheresTraining|' + parent,
            'DESC:With GM approval use ' + skill + ' for Alchemy checks, ranks, DCs and Alchemy-specific prerequisites. '
            'No bonus talent. Removal or a change of skill requires GM permission.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/martial-traditions#toc71']))
    return category, choices