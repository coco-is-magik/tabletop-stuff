"""Fixed invocation availability; activation and temporary effects are separate."""
import re

INVOCATION_LEVELS = {
    'Lingering Blessing': 1, 'Lingering Pain': 1, 'Meditation': 1,
    'Empowered Attack': 3, 'Empowered Defense': 3,
    'Channel Punishment': 7, 'Defensive Invocation': 7,
    'Item Lore': 11, 'Soulfire': 11,
    'Empowered Resistance': 15, 'Flexible Caster': 15, 'Rebuke Death': 19,
}


def invocation_records(options):
    if len(options) != len(INVOCATION_LEVELS) or {name for name, _ in options} != set(INVOCATION_LEVELS):
        raise ValueError('Invocation inventory changed; review fixed grants')
    records = []
    for title, body in options:
        level = INVOCATION_LEVELS[title]
        match = re.match(r'At (\d+)(?:st|rd|th) level,', body)
        if not match or int(match[1]) != level:
            raise ValueError('Invocation level changed: ' + title)
        description = ' '.join(body.split()).replace('|', '/')
        records.append(f'Thaumaturge {title}\tCATEGORY:Thaumaturge Invocations\t'
                       f'PREVARGTEQ:SPHERES_THAUMATURGE_LEVEL,{level}\tDESC:{description}')
    return records


def master_records():
    category = ('ABILITYCATEGORY:Thaumaturge Master Invoker\tCATEGORY:Thaumaturge Master Invoker\t'
                'EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\t'
                'POOL:if(SPHERES_THAUMATURGE_LEVEL>=20,2,0)\tPLURAL:At-will Invocations\tDISPLAYLOCATION:Spheres')
    records = []
    for title in INVOCATION_LEVELS:
        if title == 'Rebuke Death':
            continue
        records.append(f'Thaumaturge Master Invoker - {title}\tCATEGORY:Thaumaturge Master Invoker\t'
                       'PREVARGTEQ:SPHERES_THAUMATURGE_LEVEL,20\t'
                       f'PREABILITY:1,CATEGORY=Thaumaturge Invocations,Thaumaturge {title}\t'
                       f'DESC:Use {title} without expending daily invocation uses. '
                       'All activation conditions and the one-invocation-per-roll restriction still apply.')
    return category, records