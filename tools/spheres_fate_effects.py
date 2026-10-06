"""Received Fate effects; targeting and aura membership remain player-managed."""


def additional_effects():
    lines = []
    lines.append('\t'.join([
        'Fate Effect - Swords - Discharged Confirmation Only', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|TOHIT|max(1,floor(%CHOICE/2))',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
        'TEMPDESC:Enable ONLY for the single critical confirmation roll chosen '
        'during the one-minute Swords discharge. Disable immediately afterward; '
        'ordinary attacks do not benefit. Cannot combine with an ability that '
        'automatically threatens a critical hit. The player tracks the once-only '
        'use, discharge and expiration. Does not change threat range, damage, '
        'or automatically ignore concealment. Remove the ongoing motif separately.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    lines.append('\t'.join([
        'Fate Effect - The Knight - Condition Initiative Penalties', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|INITIATIVE|%CHOICE',
        'TEMPVALUE:MIN=0|MAX=100|TITLE=Choose total initiative penalties from conditions',
        'TEMPDESC:While receiving The Knight, enter only the total magnitude of '
        'initiative penalties caused by conditions such as deafened, entangled '
        'or exhausted. Keep the original conditions active: this offsets their '
        'initiative penalties only. Recalculate when conditions change; use zero '
        'when none apply. Does not cancel other initiative penalties, restore '
        'Dexterity, or suppress other condition effects. Remove when the motif '
        'ends or is discharged. Metamagic discharge and action costs are '
        'player-managed.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    lines.append('\t'.join([
        'Fate Effect - The Lovers - Adjacent Allies', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SAVE|ALL|%CHOICE|TYPE=Insight',
        'TEMPVALUE:MIN=0|MAX=100|TITLE=Choose adjacent allies capped at 2 plus floor(caster level/5)',
        'TEMPDESC:Enter the lesser of adjacent ally count and 2 + floor(caster '
        'level/5). Replace this value whenever adjacency changes; zero allies '
        'grants zero bonus. This is not caster level and does not count nearby '
        'nonadjacent allies. Uses normal insight stacking. Remove on expiration '
        'or discharge. Damage transfer, willing ally selection and its close '
        'range are resolved at the table; this record does not reduce damage.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Damage', 'COMBAT|DAMAGE'),
                          ('Save', 'SAVE|ALL'), ('Skill', 'SKILL|ALL'),
                          ('Initiative', 'COMBAT|INITIATIVE')):
        lines.append('\t'.join([
            'Fate Effect - The Page - Discharged Morale - ' + target, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|2*%CHOICE|TYPE=Morale',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the existing morale bonus for this roll',
            'TEMPDESC:Enable ONLY for the single die roll benefiting from The Page '
            'discharge. Enter the existing applicable morale bonus, not caster level. '
            'Leave that original bonus active: this doubled morale bonus replaces '
            'it through normal same-type stacking. Do not use without an existing '
            'morale bonus. Select only the applicable roll category and disable '
            'immediately afterward. Initiative represents an ability check; other '
            'ability checks remain table-resolved. Does not extend durations, '
            'spend actions or automatically remove the ongoing motif.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Damage', 'COMBAT|DAMAGE'),
                          ('Save', 'SAVE|ALL'), ('Skill', 'SKILL|ALL'),
                          ('Initiative', 'COMBAT|INITIATIVE')):
        lines.append('\t'.join([
            'Fate Effect - The Emperor - Discharged Insight - ' + target, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|%CHOICE|TYPE=Insight',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the magnitude of the ignored external penalty',
            'TEMPDESC:Enable only for rolls affected by the ONE penalty effect '
            'ignored by The Emperor discharge. Disable that original penalty '
            'separately; this record does not cancel it. Do not use this bonus '
            'for penalties from your own abilities, actions or choices (including '
            'Power Attack, forbidden lore backlash or The Hanged Man). Those '
            'penalties may be ignored but grant no insight bonus. Select only '
            'the affected roll categories; remove after caster-level rounds. '
            'Initiative represents an ability check; others remain table-resolved. '
            'Penalty identity, suppression and duration are player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
        lines.append('\t'.join([
            'Fate Effect - The Emperor - Penalty Reduction - ' + target, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|%CHOICE',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the actual penalty reduction for this roll',
            'TEMPDESC:Enable ONLY for a penalized roll while receiving The Emperor. '
            'Enter the lesser of 1 + floor(caster level/10) and the total penalty '
            'magnitude minus 1. Do not apply when the penalty is zero or -1. '
            'Leave the original penalty active; this offsets only its eligible '
            'part and must never turn a penalty into a bonus. Disable immediately '
            'after the roll and recalculate when penalties change. Initiative '
            'represents an ability check; other ability checks remain table-resolved. '
            'This is not the discharge benefit.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for category, bonuses in (
            ('1 - Attack and Damage', ('COMBAT|TOHIT,DAMAGE',)),
            ('2 - Saves', ('SAVE|ALL',)),
            ('3 - Initiative and Skills', ('COMBAT|INITIATIVE', 'SKILL|ALL')),
            ('4 - Concentration and Maneuvers', ('CONCENTRATION|ALLSPELLS',
                'VAR|SPHERES_CONCENTRATION_CHECK', 'COMBAT|CMB,CMD'))):
        lines.append('\t'.join([
            'Fate Effect - The Wheel - Ongoing - ' + category, 'VISIBLE:NO',
            *('TEMPBONUS:ANYPC|' + bonus + '|%CHOICE|TYPE=Insight' for bonus in bonuses),
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose this category total bonus including repeated results',
            'TEMPDESC:Use only for a category rolled when granting The Wheel. '
            'Enter (1 + floor(caster level/10)) times the number of occurrences '
            'of this category among the original d4 rolls. Apply each category '
            'at most once using its total; repeated results stack inside this '
            'total, not with other insight bonuses. Roll 1 + floor(caster level/10) '
            'dice at the table. Remove all ongoing categories when the motif '
            'expires or is discharged. Does not roll dice or grant unrolled categories.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for target, bonuses in (
            ('Attack', ('COMBAT|TOHIT',)),
            ('Save', ('SAVE|ALL',)),
            ('Skill', ('SKILL|ALL',)),
            ('Initiative', ('COMBAT|INITIATIVE',)),
            ('Concentration', ('CONCENTRATION|ALLSPELLS', 'VAR|SPHERES_CONCENTRATION_CHECK'))):
        lines.append('\t'.join([
            'Fate Effect - The Wheel - Discharged - ' + target, 'VISIBLE:NO',
            *('TEMPBONUS:ANYPC|' + bonus + '|2*%CHOICE|TYPE=Insight' for bonus in bonuses),
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the sum of the motif d4 results',
            'TEMPDESC:Enable before ONE chosen roll when discharging The Wheel. '
            'Input the SUM of the original d4 results, not caster level or the '
            'number of dice. Remove immediately after the roll. Initiative also '
            'represents Dexterity ability checks; other ability checks are '
            'table-resolved. Does not grant damage or CMD bonuses. Random rolls, '
            'discharging the ongoing motif and roll eligibility remain player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - The King', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|CONCENTRATION|ALLSPELLS|1+floor(%CHOICE/10)|TYPE=Insight',
        'TEMPBONUS:ANYPC|VAR|SPHERES_CONCENTRATION_CHECK|1+floor(%CHOICE/10)|TYPE=Insight',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
        'TEMPDESC:Received The King motif. Insight bonus applies to spell and '
        'sphere concentration checks, not caster level, magic skill checks or '
        'spell DCs. Remove when discharged or expired. Transfer of a magic '
        'effect, target eligibility and its Will save remain player-managed.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    lines.append('\t'.join([
        'Fate Effect - Perfect - CHA - One Round Diplomacy', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SKILL|Diplomacy|-10',
        'TEMPDESC:Enable ONLY when using Perfect choosing Charisma to influence '
        'a creature attitude in one round. Apply alongside the Perfect CHA '
        'record, which supplies the separate +1 Charisma skill bonus. Disable '
        'immediately after the accelerated check. Ordinary Diplomacy checks '
        'are not penalized. Does not change ranks, attitude or action economy '
        'automatically; eligibility and the check result remain player-managed.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    lines.append('\t'.join([
        'Fate Effect - Malice - Accumulated Bonus', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|TOHIT,DAMAGE|%CHOICE',
        'TEMPBONUS:ANYPC|SAVE|ALL|%CHOICE',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose current accumulated Malice bonus (not caster level)',
        'TEMPDESC:Enter the current total from ONE Malice word. Each qualifying '
        'trigger adds 1 plus floor(caster level/10), at most once per round, '
        'up to the casting ability modifier. Remove and reapply with the new '
        'total when triggers or expirations change it; do not add copies. '
        'Bonuses from different Malice words do not stack. Each bonus lasts '
        'casting ability modifier rounds. Changing the victim resets the bonus. '
        'Direct damage or successful maneuvers trigger it, not ongoing damage; '
        'the alternate single-creature mode triggers when that creature is harmed. '
        'Victim saves, trigger eligibility, cap, durations and casting costs '
        'remain player-managed. Remove when no bonus remains.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for strength, penalty in (('Strong', 1), ('Overwhelming', 2)):
        lines.append('\t'.join([
            'Fate Effect - Enmity - ' + strength + ' Opposing Aura', 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|SAVE|Will|-' + str(penalty),
            'TEMPDESC:Enable ONLY for the Will save against Enmity when the '
            'recipient has a ' + strength.lower() + ' alignment aura opposing the '
            'caster. Use only the strongest opposing aura; do not combine both '
            'records. Remove immediately after the save. Alignment steps, aura '
            'strength and the subsequent consecutive conditions remain '
            'player-managed. This does not penalize other saves or alter alignment.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Save', 'SAVE|ALL'),
                          ('Skill', 'SKILL|ALL'), ('Initiative', 'COMBAT|INITIATIVE')):
        for positive in (True, False):
            mode = 'Bonus' if positive else 'Penalty'
            formula = '10+floor(%CHOICE/2)|TYPE=Luck' if positive else '-10-floor(%CHOICE/2)'
            lines.append('\t'.join([
                'Fate Effect - Tug Fate - ' + mode + ' - ' + target, 'VISIBLE:NO',
                'TEMPBONUS:ANYPC|' + bonus + '|' + formula,
                'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the consecration caster level',
                'TEMPDESC:Enable ONLY for an actual d20 roll of 10 inside Tug Fate. '
                'Does not apply when taking 10. Choose one bonus or penalty for '
                'the triggering roll, then remove immediately. Initiative represents '
                'an ability check; other ability checks remain table-resolved. '
                'Aura membership, caster choice, spell points, concentration, '
                'natural 1/20 conversion and its saving throw remain player-managed.',
                'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
            ]))
    lines.append('\t'.join([
        'Fate Effect - Pain', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SKILL|STAT.INT,STAT.WIS,STAT.CHA|-4',
        'TEMPDESC:Received Pain word. Applies -4 to mental skill checks only. '
        'Remove after one round or when the ongoing word ends. Nonlethal damage, '
        'repeat damage, spell points and the magic skill check required to cast '
        'remain player-managed. This does not alter ability scores, skill ranks, '
        'physical skill checks or all casting checks indiscriminately.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Save', 'SAVE|ALL'),
                          ('Combat Maneuver', 'COMBAT|CMB'), ('Skill', 'SKILL|ALL'),
                          ('Initiative', 'COMBAT|INITIATIVE')):
        lines.append('\t'.join([
            'Fate Effect - The Hanged Man - Discharged - ' + target, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|max(1,floor(%CHOICE/2))|TYPE=Insight',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose damage paid (lesser of target Hit Dice and caster level)',
            'TEMPDESC:Enable ONLY for the single chosen roll after discharging '
            'The Hanged Man and taking damage equal to the lesser of recipient '
            'Hit Dice and caster level. Enter that damage amount, NOT caster '
            'level or remaining hit points. Remove immediately after the roll. '
            'Choose only one roll category. Initiative represents a Dexterity '
            'check; other ability checks use the same bonus at the table without '
            'altering ability scores. Damage payment, discharge and eligibility '
            'remain player-managed. This does not grant damage or CMD bonuses.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for maneuver in ('BullRush', 'Overrun', 'Trip'):
        lines.append('\t'.join([
            'Fate Effect - Perfect - STR - ' + maneuver + ' Already Safe', 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|VAR|CMB_' + maneuver + '|2+floor(%CHOICE/4)',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the word caster level',
            'TEMPDESC:Enable ONLY while receiving Perfect choosing Strength '
            'and already able to perform this maneuver without provoking '
            'attacks of opportunity independently of Perfect. This is the '
            'alternative benefit, not a bonus for all recipients. Remove when '
            'the word ends or that independent ability is lost. Does not '
            'grant a feat, CMD bonus or general attack bonus. Apply alongside '
            'the STR skill record. Eligibility is player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for stat in ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'):
        bonuses = ['TEMPBONUS:ANYPC|SKILL|STAT.' + stat + '|1']
        if stat == 'DEX':
            bonuses.append('TEMPBONUS:ANYPC|COMBAT|INITIATIVE|1')
            bonuses.append('TEMPBONUS:ANYPC|MOVEADD|TYPE.All|10+5*floor(%CHOICE/5)')
        if stat == 'WIS':
            bonuses.append('TEMPBONUS:ANYPC|COMBAT|INITIATIVE|1+floor(%CHOICE/5)')
        lines.append('\t'.join([
            'Fate Effect - Perfect - ' + stat, 'VISIBLE:NO', *bonuses,
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the word caster level',
            'TEMPDESC:Received Perfect choosing ' + stat + '. Choose only ONE '
            'ability per casting. Adds 1 to skills based on that ability, not '
            'the ability score. Apply +1 to corresponding ability checks at '
            'the table; Dexterity includes initiative. Wisdom also includes '
            'its separate scaling initiative bonus. Dexterity increases all '
            'existing movement speeds without granting new movement modes. '
            'Other benefits (maneuvers, temporary hit points, effective training and special '
            'actions) are not supplied by this record. Remove when the word '
            'ends. Concentration and spell points remain player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - Perfect - INT - Trained Check Only', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SKILL|ALL|2+floor(%CHOICE/5)',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the word caster level',
        'TEMPDESC:Enable ONLY for a trained skill check while receiving Perfect '
        'with Intelligence selected; disable immediately afterward. Apply '
        'alongside the INT record, which separately grants +1 to INT skills. '
        'Do not enable for untrained skills. Does not grant actual skill ranks '
        'or qualify the recipient for prerequisites. Effective untrained use '
        'and duration remain player-managed.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    lines.append('\t'.join([
        'Fate Effect - Villainy - Paid Ally Bonus', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|TOHIT,DAMAGE|1+floor(%CHOICE/3)',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the word caster level',
        'TEMPDESC:Enable ONLY against the creature marked by Villainy after the '
        'caster spends the additional spell point to grant this ally the bonus. '
        'Use only if the ally has no qualifying adversary-marking ability or '
        'chooses not to use it. Damage bonus applies to weapons only; disable '
        'for nonweapon damage and other targets. Remove when the word ends. '
        'This does not grant smite, change alignment, spend points, or automate '
        'the target saving throw, duration or target identity.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    lines.append('\t'.join([
        'Fate Effect - The Sun - Discharged', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|AC|%CHOICE|TYPE=Insight',
        'TEMPBONUS:ANYPC|SAVE|ALL|%CHOICE|TYPE=Insight',
        'TEMPVALUE:MIN=-10|MAX=100|TITLE=Choose the caster casting ability modifier',
        'TEMPDESC:Received one-round discharge defense after succeeding on a '
        'non-harmless save while below 50 percent of maximum hit points. Enter '
        'the CASTING ABILITY MODIFIER, not caster level or recipient modifier. '
        'No minimum is specified. Remove after one round. Resolve healing equal '
        'to caster level plus casting ability modifier and the normal motif '
        'rerolls at the table. Does not change hit points, enforce the trigger, '
        'or automatically discharge another effect.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    return lines


def templates():
    lines = ['# Generated by tools/spheres_catalog_lst.py; OGC: catalog-OGL.txt']
    lines.append('\t'.join([
        'Fate Effect - Serendipity', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|TOHIT,INITIATIVE|1|TYPE=Luck',
        'TEMPBONUS:ANYPC|SKILL|ALL|1|TYPE=Luck',
        'TEMPBONUS:ANYPC|SAVE|ALL|1|TYPE=Luck',
        'TEMPDESC:Received Serendipity while an ally inside its consecration. '
        'Disable on leaving the area or when the effect ends. Initiative is an '
        'ability check; apply the +1 luck bonus to other ability checks at the '
        'table. Does not grant AC or damage. Concentration and spell points '
        'remain player-managed.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for kind in ('Sacred', 'Profane'):
        lines.append('\t'.join([
            'Fate Effect - Hallow - ' + kind + ' - Opposed Alignment Only', 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|COMBAT|TOHIT,AC|1+floor(%CHOICE/10)|TYPE=' + kind,
            'TEMPBONUS:ANYPC|SAVE|ALL|1+floor(%CHOICE/10)|TYPE=' + kind,
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the word caster level',
            'TEMPDESC:Enable ONLY against a target of the alignment opposed to '
            'the alignment chosen by the caster. Disable immediately afterward. '
            'Use sacred for a good caster, profane for an evil caster; a caster '
            'neither good nor evil chooses their sphere bonus type. Choose only '
            'the applicable version. Mental-control protection, new saves and '
            'suppression are resolved at the table. Does not grant immunity tags.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - Greater Serendipity - Enemy', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|TOHIT,INITIATIVE|-%CHOICE',
        'TEMPBONUS:ANYPC|SKILL|ALL|-%CHOICE',
        'TEMPBONUS:ANYPC|SAVE|ALL|-%CHOICE',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the actual allied Serendipity bonus',
        'TEMPDESC:Enemy inside Greater Serendipity only. Enter the bonus granted '
        'to allies, NOT caster level. Disable on leaving the consecration or when '
        'it ends. This is a curse penalty, not a luck bonus. Other ability checks '
        'and immunity to curses remain table-resolved. Does not penalize AC or damage.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for category, bonus in (
            ('Attack Rolls', 'COMBAT|TOHIT'),
            ('Saving Throws', 'SAVE|ALL'),
            ('Skill Checks', 'SKILL|ALL'),
            ('Ability Checks', 'COMBAT|INITIATIVE')):
        lines.append('\t'.join([
            'Fate Effect - Borrow Trouble - ' + category, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|4',
            'TEMPDESC:Apply AFTER the Borrow Trouble reroll, only to the category '
            'rerolled. Remove after a subsequent success in that category. Success '
            'on the initial reroll does not end this effect. Ability Checks changes '
            'initiative only; apply +4 to other ability checks at the table, not '
            'ability scores. Reroll, spell-point cost and ending trigger remain '
            'player-managed. This is an untyped bonus, not a luck bonus.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
        lines.append('\t'.join([
            'Fate Effect - Borrow Luck - ' + category, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|-4',
            'TEMPDESC:Apply AFTER the Borrow Luck reroll, only to the category '
            'rerolled. Remove after a subsequent qualifying failure in that category. '
            'Failure of the initial reroll, deliberate failure, harmless saves, and '
            'attacks against objects or allies do not end it. Ability Checks changes '
            'initiative only; apply -4 to other ability checks at the table, not '
            'ability scores. Reroll, cost and ending trigger remain player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for name, bonus, context in (
            ('The Star', 'COMBAT|AC|2+floor(%CHOICE/5)|TYPE=Insight',
             'against attacks of opportunity'),
            ('The Chariot', 'SAVE|ALL|2+floor(%CHOICE/10)|TYPE=Insight',
             'against effects that prevent acting or cause staggered'),
            ('The Moon', 'SAVE|ALL|2+floor(%CHOICE/10)|TYPE=Insight',
             'against mind-affecting effects'),
            ('The Hierophant', 'SAVE|ALL|2+floor(%CHOICE/5)|TYPE=Insight',
             'against mind-affecting effects while within 30 feet of an allied '
             'motif bearer OTHER than yourself')):
        lines.append('\t'.join([
            'Fate Effect - ' + name + ' - Conditional', 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus,
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
            'TEMPDESC:Enable ONLY ' + context + '. Disable immediately afterward. '
            'Remove when the motif expires or is discharged. Does not execute the '
            'discharge, grant immunity, or remove conditions. Duration, targeting '
            'and discharge actions remain player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - Strength', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|COMBAT|CMB,CMD|2+floor(%CHOICE/4)|TYPE=Insight',
        'TEMPBONUS:ANYPC|SKILL|STAT.STR|2+floor(%CHOICE/4)|TYPE=Insight',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
        'TEMPDESC:Received Strength motif. Apply the same insight bonus to '
        'Strength checks at the table; Strength score is unchanged. Remove when '
        'the motif expires or is discharged. Fear retaliation, saves, actions '
        'and duration remain player-managed.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for penalized in ('Fortitude', 'Reflex', 'Will'):
        improved = ','.join(save for save in ('Fortitude', 'Reflex', 'Will') if save != penalized)
        lines.append('\t'.join([
            'Fate Effect - The Hanged Man - Penalize ' + penalized, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|SAVE|' + improved + '|2+floor(%CHOICE/10)|TYPE=Insight',
            'TEMPBONUS:ANYPC|SAVE|' + penalized + '|-2',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
            'TEMPDESC:Use only ONE Hanged Man choice at a time. Remove the old '
            'choice before selecting another, or disable it to take neither bonus '
            'nor penalty. The penalty does not scale. The once-per-round free '
            'action choice, duration, discharge damage and discharge bonus remain '
            'player-managed. Remove when the motif expires or is discharged.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - Pain - Mental Skills', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SKILL|STAT.INT,STAT.WIS,STAT.CHA|-4',
        'TEMPDESC:Received Pain mental-skill penalty only. Remove after its '
        'one-round duration or when the maintained word ends. Nonlethal damage, '
        'repeated damage, and the magic skill check to cast remain table-resolved. '
        'Does not reduce ability scores, saves, or physical skill checks.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for name, stats, divisor, context in (
            ('Justice', 'TOHIT,DAMAGE', 5,
             'against the hostile creature that damaged you, for one round after that damage'),
            ('The Devil - Discharged', 'TOHIT,AC', 4,
             'against enemies assessed with this motif, after discharge and within its caster-level rounds')):
        lines.append('\t'.join([
            'Fate Effect - ' + name + ' - Conditional', 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|COMBAT|' + stats + '|2+floor(%CHOICE/' + str(divisor) + ')|TYPE=Insight',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
            'TEMPDESC:Enable ONLY ' + context + '. Disable immediately for other '
            'targets. Target identity, triggering damage, assessment, discharge '
            'and duration are player-managed. This does not implement damage '
            'transfer or grant the bonus against all enemies.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - The World - Conditional Skills', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SKILL|ALL|2+floor(%CHOICE/5)|TYPE=Insight',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
        'TEMPDESC:Enable ONLY while taking 10 or taking 20 on a skill check, or '
        'resolving this motif discharge. Disable immediately afterward. This does '
        'not allow taking 10 or 20 where otherwise prohibited. Discharge permits '
        'taking 15 under the talent rules; training eligibility, effective ranks '
        'at caster level 20, actions and duration remain player-managed. Does not '
        'grant permanent skill ranks.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for target, bonus, context in (
            ('Attacks of Opportunity', 'COMBAT|TOHIT', 'resolving an attack of opportunity'),
            ('Untrained Skills', 'SKILL|ALL', 'resolving an untrained skill check')):
        lines.append('\t'.join([
            'Fate Effect - The Magician - ' + target, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|2+floor(%CHOICE/5)|TYPE=Insight',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
            'TEMPDESC:Enable ONLY while ' + context + '. Disable immediately '
            'afterward. Does not permit trained-only skills to be used untrained, '
            'grant skill ranks, increase attacks of opportunity, or grant Combat '
            'Reflexes. Surprise-round actions from discharge, training status, '
            'duration and targeting remain player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - The High Priestess - Discharged', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SAVE|ALL|floor(%CHOICE/2)|TYPE=Insight',
        'TEMPVALUE:MIN=5|MAX=100|TITLE=Choose the motif caster level',
        'TEMPDESC:Received discharge benefit for an ally within 30 feet of the '
        'motif target. Remove after one round. Does not grant this bonus to the '
        'bearer, share other motifs automatically, or discharge the linked motif. '
        'Link selection, eligibility, distance and discharge timing remain '
        'player-managed. Enter caster level when cast, not recipient level.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Defense', 'COMBAT|AC'),
                          ('Skill', 'SKILL|ALL')):
        lines.append('\t'.join([
            'Fate Effect - The Hermit - Self Aid - ' + target, 'VISIBLE:NO',
            'TEMPBONUS:ANYPC|' + bonus + '|3+floor(%CHOICE/5)',
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
            'TEMPDESC:Enable ONLY for the roll or defense aided by your successful '
            'swift-action self aid. Disable immediately outside that context. '
            'Do not combine with aid from another creature in the same round. '
            'This replaces the normal aid bonus, not an additional bonus on top '
            'of it. The aid check, action, target and duration remain player-managed. '
            'Discharge flanking and ally threat restrictions are not automated.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    for target, bonus in (('Attack', 'COMBAT|TOHIT'), ('Weapon Damage', 'COMBAT|DAMAGE'),
                          ('Save', 'SAVE|ALL'), ('Skill', 'SKILL|ALL'),
                          ('Initiative', 'COMBAT|INITIATIVE')):
        for discharge in (False, True):
            if discharge and target == 'Weapon Damage':
                continue
            mode = 'Discharge' if discharge else 'Spend'
            formula = '5+floor(%CHOICE/4)' if discharge else '%CHOICE'
            minimum = '0' if discharge else '1'
            prompt = 'remaining motif points before discharge' if discharge else 'points spent on this roll'
            lines.append('\t'.join([
                'Fate Effect - The Empress - ' + mode + ' - ' + target, 'VISIBLE:NO',
                'TEMPBONUS:ANYPC|' + bonus + '|' + formula + '|TYPE=Insight',
                'TEMPVALUE:MIN=' + minimum + '|MAX=100|TITLE=Choose ' + prompt,
                'TEMPDESC:Enable ONLY for the single eligible roll, then remove. '
                'Enter ' + prompt + ', NOT caster level. Initial pool is 1 plus '
                'caster level; ordinary spending per roll is at most max(1, '
                'floor(caster level/5)) and cannot exceed remaining points. '
                'Track points and subtract expenditure at the table. Discharge '
                'ends the motif and cannot boost weapon damage. Do not combine '
                'spend and discharge on one roll. Initiative represents an ability '
                'check; other ability checks remain table-resolved. Skill/save '
                'effects apply only for the selected check, not all future rolls. '
                'Weapon Damage must be disabled for nonweapon damage.',
                'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
            ]))
    for name, bonus in (
            ('Cups', 'SKILL|STAT.INT,STAT.WIS,STAT.CHA|2+floor(%CHOICE/10)'),
            ('Swords', 'COMBAT|TOHIT|1+floor(%CHOICE/10)'),
            ('Wands', 'COMBAT|INITIATIVE|2+floor(%CHOICE/10)'),
            *(("Pentacles - " + save, 'SAVE|' + save + '|1+floor(%CHOICE/10)')
              for save in ('Fortitude', 'Reflex', 'Will'))):
        lines.append('\t'.join([
            'Fate Effect - ' + name, 'VISIBLE:NO', 'TEMPBONUS:ANYPC|' + bonus,
            'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
            'TEMPDESC:Received ' + name + ' cast as its own motif ONLY. '
            'Do not apply when attached as an arcana to another motif; attached '
            'arcana grants only its discharge benefit. Enter caster level when cast. '
            'Remove when expired or discharged. Pentacles affects only the save '
            'chosen when granted; do not apply multiple Pentacles choices for one '
            'motif. This bonus is untyped, not insight. Arcana selection limits, '
            'duration, retained dice, rerolls, concealment and extended bonuses '
            'from discharge remain player-managed.',
            'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
        ]))
    lines.append('\t'.join([
        'Fate Effect - The Fool', 'VISIBLE:NO',
        'TEMPBONUS:ANYPC|SAVE|ALL|-max(0,3-floor(%CHOICE/10))',
        'TEMPVALUE:MIN=1|MAX=100|TITLE=Choose the motif caster level',
        'TEMPDESC:Received The Fool saving-throw penalty. Roll each save twice '
        'and take the better result at the table. Discharge uses three rolls '
        'with this same penalty, then remove the effect. May also end as a free '
        'action without discharge. The decreasing penalty never becomes a bonus. '
        'Duration and rerolls are player-managed; ability scores are unchanged.',
        'SOURCEPAGE:https://spheresofpower.wikidot.com/fate',
    ]))
    return '\n'.join(lines + additional_effects()) + '\n'