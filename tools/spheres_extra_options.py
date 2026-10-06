"""Level-limited extra class-option feats; each selection buys one real slot."""

OPTIONS = {
    'Extra Battlefield Specialization': ('Commander', 'Commander Battlefield Specialist', (5, 11, 17)),
    'Extra Prowess': ('Armiger', 'Armiger Prowess', (5, 11, 17)),
    'Extra Scholar’s Knack': ('Scholar', "Scholar Scholar'S Knack", (7, 15)),
    'Extra Smithing Insight': ('Blacksmith', 'Blacksmith Smithing Insight', (7, 15)),
    'Extra Striker Art': ('Striker', 'Striker Striker Art', (5, 11, 17)),
    'Extra Technical Insight': ('Technician', 'Technician Technical Insight', (5, 11, 17)),
}


def rules(name):
    if name not in OPTIONS:
        return None
    klass, category, levels = OPTIONS[name]
    level = 'SPHERES_' + klass.upper() + '_LEVEL'
    count = 'SPHERES_EXTRA_' + klass.upper() + '_OPTIONS'
    cap = '+'.join(f'if({level}>={minimum},1,0)' for minimum in levels)
    prerequisites = [f'PREVARLT:{count},{cap}']
    if klass == 'Striker':
        branches = []
        for limit, minimum in enumerate(levels, 1):
            eligible = (f'PREMULT:1,[PRECLASS:1,Striker={minimum}],'
                        f'[PREMULT:2,[PREFEAT:1,Amateur Striker],[PREATT:{minimum}]]')
            branches.append(f'[PREMULT:2,[{eligible}],[PREVARLT:{count},{limit}]]')
        prerequisites = ['PREMULT:1,' + ','.join(branches)]
    else:
        prerequisites.insert(0, f'PRECLASS:1,{klass}={levels[0]}')
    return prerequisites, ['MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
                           f'BONUS:VAR|{count}|1', f'BONUS:ABILITYPOOL|{category}|1']