"""Reviewed direct Core feat equivalences; never grant the feat's effects.

Conditional, weapon-specific and rank-dependent associations are not inferred.
Waiving other prerequisites in a dependent feat requires separate qualification
logic; these tags represent only the associated feat itself.
"""

ASSOCIATED = {
    'Barroom Sphere': ('Throw Anything',),
    'Dual Wielding Sphere': ('Two-Weapon Fighting',),
    'Gladiator Sphere': ('Dazzling Display',),
    'Sniper Sphere': ('Precise Shot',),
    'Alchemy - Hypervigilance Serum': ('Blind-Fight',),
    'Athletics - Mobile Striker': ('Spring Attack',),
    'Athletics - Mobility': ('Mobility',),
    'Athletics - Moving Target': ('Wind Stance',),
    'Barroom - Barroom Expert': ('Improvised Weapon Mastery',),
    'Barroom - Surprise': ('Catch Off-Guard',),
    'Barroom - Menacing Belch': ('Dazzling Display',),
    'Berserker - Barbaric Throw': ('Throw Anything',),
    'Berserker - Deathless': ('Diehard',),
    'Berserker - Greater Sunder': ('Improved Sunder',),
    'Brute - Break Defenses': ('Greater Bull Rush', 'Greater Overrun'),
    'Brute - Greater Brute': ('Improved Bull Rush', 'Improved Overrun'),
    'Dual Wielding - Mercurial Flow': ('Double Slice',),
    'Duelist - Greater Disarm': ('Improved Disarm',),
    'Duelist - Finger Cutter': ('Improved Disarm',),
    'Equipment - Dagger Dancer': ('Critical Focus',),
    'Equipment - Expert Reloading': ('Rapid Reload',),
    'Equipment - Thrower’s Reflexes': ('Snatch Arrows',),
    'Equipment - Versatile Shield': ('Shield Master',),
    'Equipment - Huntsman Training': ('Far Shot',),
    'Equipment - Outrider Training': ('Mounted Archery',),
    'Equipment - Shield Training': ('Shield Proficiency', 'Tower Shield Proficiency'),
    'Fencing - Expert Feint': ('Greater Feint',),
    'Fencing - Fast Feint': ('Improved Feint',),
    'Fencing - Footwork': ('Step Up',),
    'Fencing - Lunge': ('Lunge',),
    'Gladiator - Dullahan’s Call': ('Critical Focus',),
    'Guardian - Stand Still': ('Stand Still',),
    'Open Hand - Greater Trip': ('Improved Trip',),
    'Shield - Bashing Shield': ('Improved Shield Bash',),
    'Wrestling - Greater Grapple': ('Greater Grapple',),
    'Wrestling - Iron Grip': ('Improved Grapple',),
}


def equivalence_tags(key):
    feats = ASSOCIATED.get(key, ())
    return ['SERVESAS:ABILITY=FEAT|' + '|'.join(feats)] if feats else []