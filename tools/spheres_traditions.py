"""Compile reviewed general casting options from the pinned Ultimate section.

Published action restrictions remain rules text; persistent grants use PCGen.
Oathbound Casting is modeled through its pinned Oaths: each oath consumes
drawback points equal to its published oath point value.
"""
import argparse
import json
import re

from spheres import DATA
from spheres_catalog_source import SNAPSHOTS

OUTPUT = DATA / 'spheres_casting_options.lst'
LEGACY = {'Verbal Casting', 'Somatic Casting', 'Focus Casting', 'Magical Signs',
          'Prepared Caster', 'Draining Casting', 'Addictive Casting', 'Area Bound',
          'Bonded Casting', 'Charged Spells', 'Mental Focus', 'Terrain Casting',
          'Unsettling Casting', 'Vampiric Casting', 'Extended Casting'}
DEFERRED = {'Card Casting', 'Singular Pool', 'Catastrophic Failure'}
# Oathbound Casting is a zero-point wrapper; each Oath is itself the costed
# drawback, consuming drawback points equal to its published oath point value.
# The Oathbound Casting drawback names five Oaths directly; every other published
# Oath needs GM permission ("With GM permission, other Oaths or paladin/antipaladin
# codes can be selected as well").
OATHS_CORE = ('Oath against Harm', 'Oath against Mercy', 'Oath of Loyalty',
              'Oath of Secrecy', 'Oath of Silence')
OATH_DRAW = 'Tradition - Oathbound Casting'
OATH_ADJUDICATION = DATA / 'spheres_oath_adjudication.lst'
OATH_CATEGORIES = DATA / 'spheres_categories_oaths.lst'
DOUBLE = {'Diagram Magic', 'Dedicated Wright', 'Narcoleptic Casting', 'Planebound Magic', 'Unstable Storage'}
REPEATED = {'Bonded Casting', 'Consciousness Linked', 'Coy Caster', 'Skilled Casting',
            'Substantial Magic', 'Unreliable Replenishment', 'Vampiric Casting'}
CONFLICTS = (
    ('Age of Reason', 'Clarke Compliance'),
    ('Bonded Casting', 'Center Of Power'), ('Bonded Casting', 'Focus Casting'),
    ('Bonded Casting', 'Galvanized'), ('Bonded Casting', 'Spell Stand-In'),
    ('Charged Spells', 'Diagram Magic'), ('Charged Spells', 'Prepared Caster'),
    ('Dreamlost Casting', 'Narcoleptic Casting'),
    ('Focus Casting', 'Center Of Power'), ('Focus Casting', 'Galvanized'),
    ('Galvanized', 'Center Of Power'), ('Magical Signs', 'Witchmarked'),
    ('Madness Mantra', 'Emotional Casting'),
    ('Madness Mantra - Variant', 'Emotional Casting'),
    ('Spell Tokens', 'Extended Casting'),
)
TACTICAL_BOONS = {'Alien Source', 'Atmoturgy', 'Confluent Casting', 'Deathful Magic',
                  'Draw Magic', 'Empowered Abilities', 'Overcharge', 'Overconsumption',
                  'Overwhelming Power', 'Sanguine Empowerment', 'Unbound Magic',
                  'Virtuoso', 'Wild Surge'}
# Boons whose grants are modeled directly rather than left as pure rules text.
EXTRA_BOONS = {'Bound Creature', 'Wild Will'}
# Sphere-specific drawbacks that grant a specific talent chosen by sphere rather
# than a free talent in the drawback's own sphere.
SPHERE_DRAW_DEFERRED = {'Striker'}
SPHERE_DRAW_OUTPUT = DATA / 'spheres_sphere_drawbacks.lst'
SPHERE_DRAW_CATEGORIES = DATA / 'spheres_categories_sphere_drawbacks.lst'
SPHERE_DRAW_RESTRICTIONS = DATA / 'spheres_sphere_drawback_restrictions.lst'
# Clauses that forbid acquiring a talent, and drawbacks that pin the bonus talent.
ACQUIRE = re.compile(
    r'(?:cannot|can not|may not|nor can (?:you|they|it))\s+'
    r'(?:gain|take|select|choose|learn)\b', re.I)
MUST_SELECT = re.compile(r'You must select ([^.,]+?)(?: (?:advanced )?talent)?(?: with|,|\.)', re.I)


def strip_tags(heading):
    return re.sub(r'\s*\[[^]]+\]', '', heading).strip()


def sphere_drawbacks():
    """Sphere-Specific Drawbacks grouped by their sphere heading."""
    source = json.loads((SNAPSHOTS / 'casting-traditions.json').read_text())
    rows = source['sections']
    start = next(i for i, row in enumerate(rows)
                 if row['heading'] == 'Sphere-Specific Drawbacks')
    end = next(i for i in range(start + 1, len(rows))
               if rows[i]['level'] <= rows[start]['level'])
    grouped = {}
    sphere = None
    for row in rows[start + 1:end]:
        if row['level'] == 3:
            sphere = strip_tags(row['heading'])
            grouped[sphere] = []
        elif row['level'] == 4:
            grouped[sphere].append(row)
    return grouped


def sphere_drawback_key(drawback_name):
    return 'Sphere Drawback - ' + strip_tags(drawback_name)


def catalog_talents():
    """{sphere: set of catalog talent names} covering basic and advanced talents."""
    source = json.loads((DATA / 'catalog.json').read_text())
    found = {}
    for row in source:
        names = [t['name'] for t in row['talents']]
        names += [t['name'] for t in row.get('advanced', [])]
        found[row['sphere']] = set(names)
    return found


def forbidden_talents(row, names):
    """Catalog talents the drawback forbids acquiring, from 'cannot gain/take/select'."""
    found = []
    for clause in re.split(r'(?<=[.;])\s+|,\s+(?:and|nor|but)\s+', row['text']):
        if not ACQUIRE.search(clause):
            continue
        for name in names:
            if re.search(r'\b' + re.escape(name) + r'\b', clause) and name not in found:
                found.append(name)
    return sorted(found)


def pinned_bonus_talent(row, names):
    """The single catalog talent a drawback requires for its bonus talent, if any."""
    match = MUST_SELECT.search(row['text'])
    if not match:
        return None
    token = re.sub(r'^(?:the|a|an)\s+', '', match.group(1).strip(), flags=re.I)
    if '[' in token or ' or ' in token.lower() or ' and ' in token.lower():
        return None
    return token if token in names else None


def sphere_incompatibility_names(row, canon):
    """Resolvable 'Incompatible:' names; unresolvable text stays rules-only."""
    match = re.search(r'Incompatible:([^\n]*)', row['text'])
    if not match:
        return []
    found = []
    for token in re.split(r',| and ', match.group(1)):
        token = re.sub(r'\([^)]*\)', '', token).strip().rstrip('.')
        other = canon.get(token.lower())
        if other and other != strip_tags(row['heading']) and other not in found:
            found.append(other)
    return found


def mutual_incompatibilities(grouped):
    """Every incompatible pair in both directions, so exclusion is symmetric."""
    canon = {}
    for entries in grouped.values():
        for row in entries:
            canon[strip_tags(row['heading']).lower()] = strip_tags(row['heading'])
    declared = {}
    for entries in grouped.values():
        for row in entries:
            declared[strip_tags(row['heading'])] = sphere_incompatibility_names(row, canon)
    mutual = {name: set(others) for name, others in declared.items()}
    for name, others in declared.items():
        for other in others:
            if other in declared:
                mutual.setdefault(other, set()).add(name)
    return declared, mutual


def build_sphere_drawbacks():
    grouped = sphere_drawbacks()
    _declared, mutual = mutual_incompatibilities(grouped)
    rows = ['# Generated by tools/spheres_traditions.py from pinned Ultimate rules.',
            '# Sphere-specific drawbacks grant a bonus talent in their own sphere.']
    categories = ['# Generated by tools/spheres_traditions.py.']
    restrictions = ['# Generated by tools/spheres_traditions.py from pinned drawback text.',
                    '# Talents a sphere drawback forbids acquiring.']
    talents = catalog_talents()
    categories.append(
        'ABILITYCATEGORY:Custom Sphere Drawback\tCATEGORY:Custom Sphere Drawback'
        '\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY'
        '\tPOOL:SPHERES_MAGIC_TALENTS\tPLURAL:Sphere-Specific Drawbacks'
        '\tDISPLAYLOCATION:Spheres')
    for sphere, entries in grouped.items():
        if sphere == 'Universal':
            continue
        categories.append(
            f'ABILITYCATEGORY:Custom {sphere} Drawback Talent\tCATEGORY:Spheres Magic Talent'
            f'\tTYPE:SpheresBasicTalent.{sphere}\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO'
            f'\tVISIBLE:QUALIFY\tPOOL:0\tPLURAL:{sphere} Drawback Talents\tDISPLAYLOCATION:Spheres')
        for row in entries:
            drawback = strip_tags(row['heading'])
            if drawback in SPHERE_DRAW_DEFERRED:
                continue
            key = sphere_drawback_key(drawback)
            pinned = pinned_bonus_talent(row, talents.get(sphere, set()))
            granted = (f'ABILITY:Spheres Magic Talent|AUTOMATIC|{sphere} - {pinned}'
                       if pinned else f'BONUS:ABILITYPOOL|Custom {sphere} Drawback Talent|1')
            rows.append('\t'.join([
                key, 'CATEGORY:Custom Sphere Drawback',
                'COST:0',
                f'PREABILITY:1,CATEGORY=Spheres Magic Talent,{sphere} Sphere',
                granted,
                'BONUS:VAR|SPHERES_SPHERE_DRAWBACKS|1',
                *['!PREABILITY:1,CATEGORY=Custom Sphere Drawback,'
                  + sphere_drawback_key(other)
                  for other in sorted(mutual.get(drawback, set()))
                  if other not in SPHERE_DRAW_DEFERRED],
                'DESC:' + description(row)
                + (' This drawback pins its bonus talent.' if pinned else '')
                + ' Removing it costs a magic talent from that sphere.',
                'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#'
                + row['anchor']]))
            for talent in forbidden_talents(row, talents.get(sphere, set())):
                restrictions.append('\t'.join([
                    f'CATEGORY=Spheres Magic Talent|{sphere} - {talent}.MOD',
                    f'!PREABILITY:1,CATEGORY=Custom Sphere Drawback,{key}']))
    return ('\n'.join(rows) + '\n', '\n'.join(categories) + '\n',
            '\n'.join(restrictions) + '\n')



def name(heading):
    return re.sub(r'\s*\[[^]]+\]', '', heading).strip().replace(',', ' -')


def sections(heading):
    source = json.loads((SNAPSHOTS / 'casting-traditions.json').read_text())
    rows = source['sections']
    start = next(i for i, row in enumerate(rows) if row['heading'] == heading)
    end = next(i for i in range(start + 1, len(rows))
               if rows[i]['level'] <= rows[start]['level'])
    result = {}
    for row in rows[start + 1:end]:
        if row['level'] != 4:
            continue
        key = name(row['heading'])
        if key in result:
            raise ValueError('Duplicate Ultimate tradition option: ' + key)
        result[key] = row
    return result


def conflicts(key):
    return ['!PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - ' + other
            for pair in CONFLICTS if key in pair for other in pair if other != key]


def oaths():
    """Every published Oath with its oath-point value."""
    source = json.loads((SNAPSHOTS / 'oaths.json').read_text())
    found = {}
    for row in source['sections']:
        match = re.match(r'^(Oath [^(\[]*?)\s*\((\d+)\s+Oath Points?\)', row['heading'])
        if match:
            found[match.group(1).strip()] = (int(match.group(2)), row)
    missing = [oath for oath in OATHS_CORE if oath not in found]
    if missing:
        raise ValueError('Unpinned Oaths: ' + ', '.join(missing))
    # Forbidden Knowledge is worth 2 or 4 oath points depending on the severity.
    forbidden = next((row for row in source['sections']
                      if row['heading'].startswith('Forbidden Knowledge')), None)
    if forbidden is None:
        raise ValueError('Unpinned Oath: Forbidden Knowledge')
    found['Forbidden Knowledge (lesser severance)'] = (2, forbidden)
    found['Forbidden Knowledge (greater severance)'] = (4, forbidden)
    return found


def oath_key(oath, points):
    """Oath key carrying its value, so the points are visible in the ability list."""
    unit = 'drawback point' if points == 1 else 'drawback points'
    return f'Tradition - Oathbound Casting: {oath} ({points} {unit})'


def oath_approval(oath):
    return 'Reviewed - ' + oath


def oath_rows():
    """Oaths grant drawback credits; they never consume drawback points."""
    all_oaths = oaths()
    names = sorted(all_oaths)
    keys = {name: oath_key(name, all_oaths[name][0]) for name in names}
    rows = []
    for oath in names:
        points, row = all_oaths[oath]
        unit = 'drawback point' if points == 1 else 'drawback points'
        tags = [
            keys[oath], 'CATEGORY:Custom Casting Drawback',
            'COST:0',
            'PREABILITY:1,CATEGORY=Custom Casting Drawback,' + OATH_DRAW,
            # Exactly one Oath is sworn, so the Oaths are mutually exclusive.
            *['!PREABILITY:1,CATEGORY=Custom Casting Drawback,' + keys[other]
              for other in names if other != oath],
            'BONUS:ABILITYPOOL|Custom Casting Boon|' + str(points),
            'BONUS:VAR|SPHERES_TRADITION_DRAWBACKS|' + str(points),
        ]
        if oath not in OATHS_CORE:
            tags.append('PREABILITY:1,CATEGORY=Spheres Oath Adjudication,'
                        + oath_approval(oath))
        rows.append('\t'.join(tags + [
            'DESC:Grants ' + str(points) + ' ' + unit
            + ' (counts as ' + str(points) + ' drawbacks and costs none). '
            + description(row)
            + ' Breaking, forsaking, or lacking this oath suspends spellcasting until'
            ' atonement or a new 8-hour oath.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/oaths#' + row['anchor']]))
    return rows


def build_oath_adjudication():
    """GM approval records for the Oaths the drawback does not name directly."""
    rows = ['# Generated by tools/spheres_traditions.py.',
            '# The Oathbound Casting drawback names five Oaths; the others need permission.']
    for oath in sorted(oaths()):
        if oath in OATHS_CORE:
            continue
        rows.append('\t'.join([
            'Reviewed - ' + oath, 'CATEGORY:Spheres Oath Adjudication', 'COST:0',
            'DESC:GM approval required: Oathbound Casting names only five Oaths, so '
            + oath + ' needs permission, as the source allows: "With GM permission,'
            ' other Oaths or paladin/antipaladin codes can be selected as well."']))
    categories = ['# Generated by tools/spheres_traditions.py.',
                  'ABILITYCATEGORY:Spheres Oath Adjudication'
                  '\tCATEGORY:Spheres Oath Adjudication\tEDITABLE:YES\tEDITPOOL:NO'
                  '\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:YES'
                  '\tPLURAL:Manual Oath Approvals\tDISPLAYLOCATION:Spheres']
    return '\n'.join(rows) + '\n', '\n'.join(categories) + '\n'


def description(row):
    return ' '.join(row['text'].replace('|', '/').replace('%', ' percent')
                    .replace('(', '[').replace(')', ']').split())


def build():
    rows = ['# Generated by tools/spheres_traditions.py from pinned Ultimate rules.']
    # Basic Magic Training grants the casting feature without class spell-pool
    # levels. Keep the saved tradition key but qualify by the feature, not levels.
    rows.append('CATEGORY=Custom Casting Tradition|Custom Casting Tradition.MOD\t'
                'PRE:.CLEAR\tPREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core')
    drawbacks = sections('General Drawbacks')
    for key, row in drawbacks.items():
        if key in LEGACY | DEFERRED:
            continue
        if key == 'Oathbound Casting':
            # Zero-point wrapper; the chosen Oath is itself a costed drawback.
            rows.append('\t'.join([
                'Tradition - ' + key, 'CATEGORY:Custom Casting Drawback', 'COST:0',
                'PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
                'DESC:' + description(row)
                + ' The selected Oath consumes drawback points equal to its oath point'
                ' value. See the "Tradition - Oathbound Casting:" selections.',
                'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#'
                + row['anchor']]))
            continue
        weight = 2 if key in DOUBLE else 1
        grants = {'Benefactor': ['ABILITY:Spheres Magic Talent|AUTOMATIC|Mana Sphere|Mana - Gift Of Knowledge'],
                  'Spell Stand-In': ['ABILITY:Spheres Magic Talent|AUTOMATIC|Conjuration Sphere|Conjuration - Spell Conduit',
                                    'ABILITY:FEAT|AUTOMATIC|Spell Channel']}
        tags = ['Tradition - ' + key, 'CATEGORY:Custom Casting Drawback',
                'COST:' + str(weight),
                'PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
                *conflicts(key),
                'BONUS:ABILITYPOOL|Custom Casting Boon|' + str(weight),
                'BONUS:VAR|SPHERES_TRADITION_DRAWBACKS|' + str(weight),
                *grants.get(key, []),
                'DESC:' + description(row) + ' Resolve casting restrictions and situational effects at the table.',
                'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#' + row['anchor']]
        rows.append('\t'.join(tags))
    for key in sorted(REPEATED):
        row = drawbacks[key]
        rows.append('\t'.join([
            'Tradition - ' + key + ' Second Selection', 'CATEGORY:Custom Casting Drawback',
            'PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
            'PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - ' + key,
            *conflicts(key), 'BONUS:ABILITYPOOL|Custom Casting Boon|1',
            'BONUS:VAR|SPHERES_TRADITION_DRAWBACKS|1',
            'DESC:Second selection. ' + description(row),
            'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#' + row['anchor']]))
    for key, row in sections('Boons').items():
        if key not in TACTICAL_BOONS | EXTRA_BOONS:
            continue
        tags = ['Tradition - ' + key, 'CATEGORY:Custom Casting Boon', 'COST:2',
                'PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
                'BONUS:VAR|SPHERES_TRADITION_BOONS|1']
        if key == 'Overconsumption':
            tags.append('PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Vampiric Casting')
        if key == 'Virtuoso':
            tags += ['PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - Skilled Casting']
            tags += ['!PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - ' + other
                     for other in ('Center Of Power', 'Magical Signs', 'Witchmarked')]
        if key == 'Bound Creature':
            # Grants the Conjuration sphere (or Extra Companion if already owned).
            tags.append('ABILITY:Spheres Magic Talent|AUTOMATIC|Conjuration Sphere')
        if key == 'Wild Will':
            tags += ['MULT:YES', 'STACK:YES',
                     'CHOOSE:USERINPUT|1|TITLE=Favored terrain environment']
        tags += ['DESC:' + description(row) + ' Apply conditional effects only in the published circumstances.',
                 'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#' + row['anchor']]
        rows.append('\t'.join(tags))
    # Add the reverse restrictions to existing legacy records without changing keys.
    for key in sorted(LEGACY):
        if conflicts(key):
            rows.append('\t'.join(['CATEGORY=Custom Casting Drawback|Tradition - ' + key + '.MOD',
                                   *conflicts(key)]))
    rows += [
        'CATEGORY=Custom Casting Drawback|Tradition - Addictive Casting.MOD\tCOST:2\tBONUS:ABILITYPOOL|Custom Casting Boon|1\tBONUS:VAR|SPHERES_TRADITION_DRAWBACKS|1\tDESC:.CLEAR\tDESC:' + description(drawbacks['Addictive Casting']),
        'CATEGORY=Custom Casting Drawback|Tradition - Vampiric Casting.MOD\tCOST:2\tBONUS:ABILITYPOOL|Custom Casting Boon|1\tBONUS:VAR|SPHERES_TRADITION_DRAWBACKS|1\tDESC:.CLEAR\tDESC:' + description(drawbacks['Vampiric Casting']),
        'CATEGORY=Custom Casting Drawback|Tradition - Bonded Casting.MOD\tDESC:.CLEAR\tDESC:' + description(drawbacks['Bonded Casting']),
    ]
    fortified = ['CATEGORY=Custom Casting Boon|Tradition - Fortified Casting.MOD']
    for stat, selected in (('INT', None), ('WIS', 'Wisdom Casting'), ('CHA', 'Charisma Casting')):
        bonus = 'BONUS:VAR|SPHERES_CASTING_ABILITY|max(0,CON-' + stat + ')'
        if selected:
            bonus += '|PREABILITY:1,CATEGORY=Spheres Casting Ability,' + selected
        else:
            bonus += '|!PREABILITY:1,CATEGORY=Spheres Casting Ability,Wisdom Casting,Charisma Casting'
        fortified.append(bonus)
    rows.append('\t'.join(fortified))
    feat = sections('Boons')['Drawback Feat']
    rows.append('\t'.join([
        'Tradition - Drawback Feat', 'CATEGORY:Custom Casting Boon', 'COST:2',
        'PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
        'MULT:YES', 'STACK:YES', 'CHOOSE:NOCHOICE',
        'BONUS:VAR|SPHERES_TRADITION_BOONS|1',
        'BONUS:ABILITYPOOL|Casting Tradition Drawback Feat|1',
        'DESC:' + description(feat),
        'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#' + feat['anchor']]))
    embodiment = sections('Boons')['Embodiment']
    rows.append('\t'.join([
        'Tradition - Embodiment', 'CATEGORY:Custom Casting Boon', 'COST:2',
        'PREABILITY:1,CATEGORY=Custom Casting Tradition,Custom Casting Tradition',
        'MULT:YES', 'STACK:NO',
        'CHOOSE:USERINPUT|1|TITLE=Substance embodied',
        'PREVARLT:SPHERES_TRADITION_EMBODIMENT,1',
        'DEFINE:SPHERES_TRADITION_EMBODIMENT|0',
        'BONUS:VAR|SPHERES_TRADITION_EMBODIMENT|1',
        'BONUS:VAR|SPHERES_TRADITION_BOONS|1',
        'DESC:Embodied substance: %1. ' + description(embodiment) + '|%LIST',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/casting-traditions#' + embodiment['anchor']]))
    rows += oath_rows()
    return '\n'.join(rows) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    drawbacks, categories, restrictions = build_sphere_drawbacks()
    adjudication, oath_categories = build_oath_adjudication()
    outputs = {OUTPUT: build(), SPHERE_DRAW_OUTPUT: drawbacks,
               SPHERE_DRAW_CATEGORIES: categories,
               SPHERE_DRAW_RESTRICTIONS: restrictions,
               OATH_ADJUDICATION: adjudication,
               OATH_CATEGORIES: oath_categories}
    for path, text in outputs.items():
        if args.write:
            path.write_text(text)
        elif not path.is_file() or path.read_text() != text:
            raise ValueError('Generated tradition data differs: ' + path.name)
    print('PASS: deterministic casting options')


if __name__ == '__main__':
    main()