"""Named martial traditions using existing combat abilities and choice pools."""
import argparse
import json

from spheres import DATA, records
from spheres_catalog_source import SNAPSHOTS
from spheres_catalog import inventory
from spheres_traditions import name, description

# Fixed grants and independent variable slots. A trailing '*' is a sphere's
# existing basic-talent list, not permission to select advanced talents.
TRADITIONS = {
    'Tattooed Warrior': (['Equipment - Unarmed Training', 'Equipment - Unarmored Training'], []),
    'Elven Duelist': (['Equipment - Elvish Heritage', 'Equipment - Finesse Fighting', 'Equipment - Finesse Fighting'], [(1, ['Duelist Sphere', 'Fencing Sphere'])]),
    'Wandering Martial Artist': (['Equipment - Force Redirection Technique', 'Equipment - Unarmored Training'], [(1, ['Equipment discipline*']), (1, ['Athletics Sphere', 'Gladiator Sphere'])]),
    'Janjaweed': (['Equipment - Firearm Proficiency', 'Beastmastery Sphere'], [(1, ['Barrage Sphere', 'Beastmastery*'])]),
    'Highlander': (['Equipment - Gallowglass Training', 'Duelist Sphere'], [(1, ['Dual Wielding Sphere', 'Scout Sphere'])]),
    'Free Runner': (['Athletics Sphere', 'Athletics - Expanded Training', 'Athletics - Wall Stunt'], [(1, ['Athletics*'])]),
    'Bushido Warrior': (['Equipment - Armor Training', 'Equipment - Bushido Training', 'Duelist Sphere'], [(1, ['Beastmastery Sphere', 'Duelist - Draw Cut'])]),
    'Imperialist': (['Equipment - Firearm Proficiency', 'Equipment - Knightly Training', 'Duelist Sphere'], [(1, ['Beastmastery Sphere', 'Warleader Sphere'])]),
    'Knightly Arts': (['Equipment - Armor Training', 'Equipment - Knightly Training', 'Equipment - Shield Training'], [(1, ['Beastmastery Sphere', 'Warleader Sphere', 'Shield Sphere'])]),
    'Iron Breaker Style': (['Open Hand Sphere', 'Berserker Sphere', 'Berserker - Greater Sunder'], [(1, ['Equipment - Unarmored Training', 'Berserker*', 'Open Hand*'])]),
    'Cunning Leader': (['Fencing Sphere', 'Fencing - Expert Feint', 'Warleader Sphere'], [(1, ['Equipment discipline*'])]),
    'Pursuer': (['Duelist Sphere', 'Scout Sphere'], [(1, ['Equipment discipline*']), (1, ['Duelist*', 'Scout*'])]),
    'Weapon Master': (['Dual Wielding Sphere'], [(2, ['Equipment discipline*']), (1, ['Dual Wielding*'])]),
    'Gladiator': (['Equipment - Gladiator Training', 'Gladiator Sphere'], [(1, ['Equipment - Armor Training', 'Equipment - Shield Training', 'Equipment - Gladiator Training']), (1, ['Gladiator*'])]),
    'Mixed Duelist': (['Equipment - Duelist Training', 'Dual Wielding Sphere', 'Dual Wielding - Impossible Reload', 'Dual Wielding - Mixed Assault'], []),
    'Phalanx Soldier': (['Equipment - Shield Training', 'Equipment - Spear Dancer', 'Shield Sphere'], [(1, ['Equipment - Finesse Fighting', 'Shield*'])]),
    'Pirate': (['Equipment - Pirate Training', 'Equipment - Unarmored Training', 'Fencing Sphere'], [(1, ['Duelist Sphere', 'Athletics Sphere'])]),
    'Gearhead': (['Equipment - Techmaniac', 'Equipment - Toolkit Training', 'Tech Sphere'], [(1, ['Tech - Tech Savvy', 'Trap Sphere'])]),
    'Animal Trainer': (['Equipment - Bounty Hunter’s Tools', 'Beastmastery Sphere'], [(2, ['Beastmastery*', 'Equipment*'])]),
    'Chemist': (['Equipment - Fast Draw', 'Alchemy Sphere', 'Barroom Sphere'], [(1, ['Barroom*', 'Alchemy*'])]),
    'Commando': (['Equipment - Rogue Weapon Training', 'Leadership Sphere', 'Scout Sphere'], [(1, ['Equipment*', 'Scout*'])]),
    'Militia': (['Equipment - Peasant Training', 'Beastmastery Sphere', 'Scout Sphere'], [(1, ['Equipment*'])]),
    'Noble': (['Equipment - Duelist Training', 'Equipment - Finesse Fighting', 'Leadership Sphere'], [(1, ['Duelist*', 'Leadership*'])]),
    'Guild Training': (['Equipment - Finesse Fighting', 'Equipment - Rogue Weapon Training', 'Alchemy Sphere'], [(1, ['Fencing Sphere', 'Duelist Sphere'])]),
    'Steppe Rider': (['Equipment - Outrider Training', 'Equipment - Shortbow Mastery', 'Beastmastery Sphere'], [(1, ['Barrage Sphere', 'Sniper Sphere'])]),
    'Ruin Delver': (['Equipment - Toolkit Training', 'Athletics Sphere', 'Athletics - Rope Swing'], [(1, ['Equipment*'])]),
    'All-Thrower': (['Equipment - Caber Toss', 'Equipment - Rock Toss', 'Berserker Sphere'], [(1, ['Barroom Sphere', 'Berserker - Barbaric Throw'])]),
    'Barbarian': (['Equipment - Tribal Training', 'Berserker Sphere', 'Scout Sphere'], [(1, ['Barroom Sphere', 'Beastmastery Sphere'])]),
    'Buccaneer': (['Equipment - Duelist Training', 'Equipment - Firearm Proficiency', 'Dual Wielding Sphere'], [(1, ['Athletics Sphere', 'Fencing Sphere', 'Dual Wielding*'])]),
    'Challenging Knight': (['Equipment - Armor Training', 'Equipment - Knightly Training', 'Gladiator Sphere'], [(1, ['Guardian Sphere', 'Gladiator*'])]),
    'Courtesan': (['Equipment - Dancer Training', 'Equipment - Unarmored Training', 'Fencing Sphere'], [(1, ['Dual Wielding Sphere', 'Fencing*'])]),
    'Crushing Juggernaut': (['Equipment - Armor Training', 'Brute Sphere'], [(1, ['Brute*']), (1, ['Equipment*'])]),
    'Daring Scholar': (['Equipment - Staff Mastery', 'Alchemy Sphere', 'Scout Sphere'], [(1, ['Alchemy*', 'Scout*'])]),
    'Decisive Fist': (['Equipment - Critical Genius', 'Boxing Sphere', 'Open Hand Sphere'], [(1, ['Equipment - Finesse Fighting', 'Equipment - Unarmed Training', 'Equipment - Unarmored Training'])]),
    'Dedicated Lancer': (['Equipment - Pikeman Training', 'Equipment - Spear Dancer', 'Lancer Sphere'], [(1, ['Guardian Sphere', 'Lancer*'])]),
    'Drunken Brawler': (['Equipment - Unarmed Training', 'Barroom Sphere', 'Wrestling Sphere'], [(1, ['Barroom*', 'Wrestling*'])]),
    'Dual Blade Beast': (['Equipment - Dual Blade Savant', 'Dual Wielding Sphere'], [(1, ['Equipment - Bushido Training', 'Equipment - Duelist Training']), (1, ['Duelist Sphere', 'Dual Wielding*'])]),
    'Fearless Thrower': (['Equipment - Huntsman Training', 'Equipment - Throwing Mastery'], [(1, ['Equipment - Crushing Thrower', 'Equipment - Thrower’s Reflexes']), (1, ['Barrage Sphere', 'Berserker Sphere'])]),
    'Giant': (['Equipment - Rock Toss', 'Brute Sphere'], [(1, ['Brute*']), (1, ['Equipment*'])]),
    'Professional Wrestler': (['Equipment - Unarmored Training', 'Gladiator Sphere', 'Wrestling Sphere'], [(1, ['Wrestling*', 'Gladiator*'])]),
    'Retiarius': (['Equipment - Gladiator Training', 'Equipment - Net Master', 'Gladiator Sphere'], [(1, ['Duelist Sphere', 'Lancer Sphere'])]),
    'Rogue Gunner': (['Equipment - Firearm Proficiency', 'Equipment - Expert Reloading', 'Scoundrel Sphere'], [(1, ['Athletics Sphere', 'Scoundrel*'])]),
    'Mechanic': (['Equipment - Expert Reloading', 'Trap Sphere'], [(1, ['Equipment - Firearm Proficiency', 'Equipment - Mechanical Training']), (1, ['Barrage Sphere', 'Sniper Sphere'])]),
    'Warden': (['Equipment - Armor Training', 'Equipment - Shield Training', 'Guardian Sphere', 'Shield Sphere'], []),
    'Staff Master': (['Equipment - Finesse Fighting', 'Equipment - Spear Dancer', 'Equipment - Staff Mastery', 'Equipment - Unarmored Training'], []),
    'Armored Dreadnought': (['Equipment - Armor Training', 'Equipment - Shield Training'], [(2, ['Equipment*'])]),
    'Combat Gunner': (['Equipment - Firearm Proficiency', 'Equipment - Gun Kata', 'Open Hand Sphere'], [(1, ['Barrage Sphere', 'Sniper Sphere'])]),
    'Monastic Path': (['Equipment - Monk Weapon Training', 'Equipment - Staff Mastery', 'Open Hand Sphere'], [(1, ['Athletics Sphere', 'Dual Wielding Sphere'])]),
    'Ninjutsu': (['Equipment - Finesse Fighting', 'Equipment - Monk Weapon Training', 'Scoundrel Sphere'], [(1, ['Scout Sphere', 'Trap Sphere'])]),
    'Canny Hunter': (['Equipment - Huntsman Training', 'Scout Sphere', 'Sniper Sphere'], [(1, ['Equipment*', 'Scout*'])]),
    'Heavy Armsman': (['Equipment - Dwarven Heritage', 'Equipment - Armor Training', 'Berserker Sphere'], [(1, ['Equipment*', 'Berserker*'])]),
    'Pit Fighter': (['Equipment - Unarmed Training', 'Boxing Sphere', 'Gladiator Sphere'], [(1, ['Boxing*', 'Gladiator*'])]),
    'Street Fighter': (['Equipment - Unarmed Training', 'Brute Sphere', 'Scoundrel Sphere'], [(1, ['Brute*', 'Scoundrel*'])]),
    'Stone Thrower': (['Equipment - Halfling Heritage', 'Equipment - Sling Combatant', 'Barrage Sphere'], [(1, ['Barrage*'])]),
    'Thief': (['Equipment - Rogue Weapon Training', 'Scoundrel Sphere', 'Fencing Sphere'], [(1, ['Equipment*', 'Scoundrel*', 'Fencing*'])]),
    'Dedicated Duelist': (['Equipment - Duelist Training', 'Equipment - Finesse Fighting'], [(1, ['Duelist Sphere', 'Fencing Sphere']), (1, ['Equipment - Gauntlet Shield', 'Equipment - Unarmored Training'])]),
    'Bolt Juggler': (['Equipment - Mechanical Training', 'Dual Wielding Sphere'], [(1, ['Equipment - Expert Reloading', 'Equipment - Mechanical Savant']), (1, ['Dual Wielding - Impossible Reload', 'Dual Wielding - Mixed Assault'])]),
    'Pikeman': (['Equipment - Pikeman Training', 'Equipment - Polearm Mastery', 'Lancer Sphere'], [(1, ['Guardian Sphere', 'Lancer*'])]),
    'Shield Master': (['Equipment - Shield Training', 'Shield Sphere'], [(1, ['Brute Sphere', 'Equipment*']), (1, ['Shield*'])]),
    'Tempest Dancer': (['Equipment - Double Weapon Training', 'Dual Wielding Sphere'], [(1, ['Equipment - Armor Training', 'Equipment - Unarmored Training', 'Equipment - Finesse Fighting']), (1, ['Dual Wielding*'])]),
}
PACKAGES = {
    'Janjaweed': ('Beastmastery', 'Ride'),
    'Animal Trainer': ('Beastmastery', 'Handle Animal'),
    'Chemist': ('Alchemy', 'Formulae'), 'Commando': ('Leadership', 'Cohort'),
    'Militia': ('Beastmastery', 'Handle Animal'), 'Noble': ('Leadership', 'Followers'),
    'Guild Training': ('Alchemy', 'Poison'), 'Steppe Rider': ('Beastmastery', 'Ride'),
    'Ruin Delver': ('Athletics', 'Climb'),
}


def sources():
    rows = json.loads((SNAPSHOTS / 'martial-traditions.json').read_text())['sections']
    start = next(i for i, row in enumerate(rows) if row['heading'] == 'Martial Traditions')
    end = next(i for i in range(start + 1, len(rows)) if rows[i]['heading'] == 'Sphere-Specific Drawbacks')
    return {name(row['heading']): row for row in rows[start + 1:end] if row['anchor']}


def catalog():
    return {row.split('\t')[0]: row for path in DATA.glob('spheres_might_*.lst')
            for row in records(path) if '\tCATEGORY:Spheres Combat Talent\t' in row}


def expand(options, abilities):
    result = set()
    for option in options:
        if option == 'Equipment discipline*':
            equipment = inventory(['equipment-sphere'])[0]
            result.update('Equipment - ' + talent['name'].replace(',', '')
                          for talent in equipment['talents'] if '(discipline)' in talent['heading'].lower())
        elif option.endswith('*'):
            result.update(key for key, row in abilities.items()
                          if key.startswith(option[:-1] + ' - ') and 'TYPE:SpheresBasicTalent.' in row)
        elif option in abilities:
            result.add(option)
        else:
            raise ValueError('Unknown tradition grant: ' + option)
    if not result:
        raise ValueError('Empty tradition choice')
    return sorted(result)


def build():
    source, abilities = sources(), catalog()
    rows, categories = ['# Generated by tools/spheres_martial_traditions.py'], []
    # This published tradition explicitly grants a legendary talent. Keep it
    # outside the basic-talent filters used by ordinary tradition choices.
    equipment_source = json.loads((SNAPSHOTS / 'equipment-sphere.json').read_text())
    force = next(row for row in equipment_source['sections']
                 if row['heading'] == 'Force Redirection Technique [Youxia HB]')
    force_key = 'Equipment - Force Redirection Technique'
    force_record = '\t'.join([
        force_key, 'CATEGORY:Spheres Combat Talent', 'TYPE:SpheresLegendaryTalent.Equipment',
        'PREABILITY:1,CATEGORY=Spheres Combat Talent,Equipment Sphere',
        'BONUS:VAR|SPHERES_EQUIPMENT_TALENTS|1',
        'DESC:' + description(force) + ' Apply the chosen ability substitution only while enabled; this is not an unconditional AC bonus.',
        'SOURCEPAGE:' + equipment_source['url'] + '#' + force['anchor']])
    abilities[force_key] = force_record
    rows.append(force_record)
    for title, (fixed, choices) in TRADITIONS.items():
        expand(fixed, abilities)
        key = 'Martial Tradition - ' + title
        tags = [key, 'CATEGORY:Conscript Martial Tradition',
                'PREVARGTEQ:SPHERES_CONSCRIPT_LEVEL,1',
                'ABILITY:Special Ability|AUTOMATIC|Spheres Martial Focus',
                'ABILITY:Spheres Combat Talent|AUTOMATIC|' + '|'.join(dict.fromkeys(fixed))]
        if title == 'Elven Duelist':
            # Automatic ability grants are sets, not repeated purchases. Account
            # for the second published rank without granting a duplicate key.
            tags += ['BONUS:VAR|SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT|1',
                     'BONUS:VAR|SPHERES_EQUIPMENT_TALENTS|1']
        if title == 'Tattooed Warrior':
            tags += ['ABILITY:FEAT|AUTOMATIC|Dragon’s Tattoos|Zodiac Tattoos',
                     'BONUS:SKILLRANK|Craft (Tattoos)|TL']
        if title not in ('Iron Breaker Style', 'Free Runner'):
            tags += ['ABILITY:Spheres Combat Talent|AUTOMATIC|Equipment Sphere',
                # A fixed Equipment talent occupies the Equipment sphere's free
                # first talent. Do not grant a fifth talent with the base sphere.
                'BONUS:ABILITYPOOL|Spheres Equipment Bonus Talent|-1']
        if title in PACKAGES:
            sphere, package = PACKAGES[title]
            tags += ['ABILITY:Spheres ' + sphere + ' Package|AUTOMATIC|' + sphere + ' Package - ' + package,
                     'BONUS:ABILITYPOOL|Spheres ' + sphere + ' Package|-1']
        if title == 'Free Runner':
            tags += ['ABILITY:Spheres Athletics Package|AUTOMATIC|Athletics Package - Run|Athletics Package - Leap',
                     'BONUS:ABILITYPOOL|Spheres Athletics Package|-2']
        for index, (count, options) in enumerate(choices, 1):
            category = title + ' Tradition Choice ' + str(index)
            allowed = expand(options, abilities)
            choice_category = 'Spheres Combat Talent'
            if title == 'Wandering Martial Artist' and index == 1:
                choice_category = category
                branch_keys = []
                for grant in allowed:
                    branch = category + ' - ' + grant
                    branch_keys.append(branch)
                    rows.append('\t'.join([
                        branch, 'CATEGORY:' + category,
                        'PREABILITY:1,CATEGORY=Conscript Martial Tradition,' + key,
                        'ABILITY:Spheres Combat Talent|AUTOMATIC|' + grant]))
                unarmed = category + ' - Improved Unarmed Strike'
                branch_keys.append(unarmed)
                rows.append('\t'.join([
                    unarmed, 'CATEGORY:' + category,
                    'PREABILITY:1,CATEGORY=Conscript Martial Tradition,' + key,
                    'ABILITY:FEAT|AUTOMATIC|Improved Unarmed Strike']))
                allowed = branch_keys
            if title == 'Janjaweed':
                choice_category = category
                mounted = category + ' - Mounted Training'
                gunmanship = category + ' - Gunmanship'
                allowed = [mounted, gunmanship]
                bonus_category = 'Janjaweed Beastmastery Talents'
                categories.append('\t'.join([
                    'ABILITYCATEGORY:' + bonus_category, 'CATEGORY:Spheres Combat Talent',
                    'ABILITYLIST:' + '|'.join(expand(['Beastmastery*'], abilities)),
                    'EDITABLE:YES', 'EDITPOOL:NO', 'FRACTIONALPOOL:NO',
                    'VISIBLE:QUALIFY', 'POOL:0', 'PLURAL:' + bonus_category,
                    'DISPLAYLOCATION:Spheres']))
                prerequisite = 'PREABILITY:1,CATEGORY=Conscript Martial Tradition,' + key
                rows += ['\t'.join([mounted, 'CATEGORY:' + category, prerequisite,
                                    'BONUS:ABILITYPOOL|' + bonus_category + '|2']),
                         '\t'.join([gunmanship, 'CATEGORY:' + category, prerequisite,
                                    'ABILITY:Spheres Combat Talent|AUTOMATIC|Barrage Sphere|Sniper Sphere'])]
            if title in ('Bushido Warrior', 'Imperialist', 'Knightly Arts', 'Highlander'):
                # Branch wrappers distinguish the tradition's Ride selection
                # from Beastmastery bought independently with class talents.
                choice_category = category
                branch_keys = []
                for grant in allowed:
                    branch = category + ' - ' + grant
                    branch_keys.append(branch)
                    branch_tags = [branch, 'CATEGORY:' + category,
                                   'PREABILITY:1,CATEGORY=Conscript Martial Tradition,' + key,
                                   'ABILITY:Spheres Combat Talent|AUTOMATIC|' + grant]
                    if grant == 'Beastmastery Sphere':
                        branch_tags += ['ABILITY:Spheres Beastmastery Package|AUTOMATIC|Beastmastery Package - Ride',
                                        'BONUS:ABILITYPOOL|Spheres Beastmastery Package|-1']
                    if title == 'Highlander':
                        sphere = grant.removesuffix(' Sphere')
                        bonus_category = 'Highlander ' + sphere + ' Talent'
                        categories.append('\t'.join([
                            'ABILITYCATEGORY:' + bonus_category, 'CATEGORY:Spheres Combat Talent',
                            'ABILITYLIST:' + '|'.join(expand([sphere + '*'], abilities)),
                            'EDITABLE:YES', 'EDITPOOL:NO', 'FRACTIONALPOOL:NO',
                            'VISIBLE:QUALIFY', 'POOL:0', 'PLURAL:' + bonus_category,
                            'DISPLAYLOCATION:Spheres']))
                        branch_tags.append('BONUS:ABILITYPOOL|' + bonus_category + '|1')
                    rows.append('\t'.join(branch_tags))
                allowed = branch_keys
            categories.append('\t'.join([
                'ABILITYCATEGORY:' + category, 'CATEGORY:' + choice_category,
                *(['ABILITYLIST:' + '|'.join(allowed)] if choice_category != category else []),
                'EDITABLE:YES', 'EDITPOOL:NO',
                'FRACTIONALPOOL:NO', 'VISIBLE:QUALIFY', 'POOL:0',
                'PLURAL:' + category, 'DISPLAYLOCATION:Spheres']))
            tags.append('BONUS:ABILITYPOOL|' + category + '|' + str(count))
        tags += ['DESC:' + description(source[title]),
                 'SOURCEPAGE:https://spheresofpower.wikidot.com/martial-traditions#' + source[title]['anchor']]
        rows.append('\t'.join(tags))
    return {DATA / 'spheres_martial_traditions.lst': '\n'.join(rows) + '\n',
            DATA / 'spheres_categories_martial_traditions.lst': '\n'.join(categories) + '\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for path, content in build().items():
        if args.write:
            path.write_text(content)
        elif path.read_text() != content:
            raise ValueError('Stale martial traditions: ' + str(path))
    print('PASS: deterministic named martial traditions')


if __name__ == '__main__':
    main()