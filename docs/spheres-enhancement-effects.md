# Received Enhancement effects

The native PCGen temporary-bonus selector now offers received Physical and
Mental Enhancement, Staunch Resistance, Enhance Focus, and Superior Reflexes effects. Select the
affected statistic and enter the caster level at casting, not the recipient's
level. Remove the effect when it expires. The selector does not grant talents,
spend spell points, or validate another character's casting permission.

Enhance Focus includes the loaded Core skill records and local Spheres skills.
It does not enumerate skills from other campaigns. Staunch Resistance's bonus
is untyped, as in the pinned source, rather than a resistance bonus. Physical,
Mental, and Focus bonuses use the enhancement type.

Superior Reflexes applies initiative and records its extra attacks as the bonus
`VAR.SPHERES_RECEIVED_SUPERIOR_REFLEXES_AOO`. It does not grant Combat Reflexes
or change that feat's Dexterity-based allowance. The flat-footed permission and
attack expenditure are described but player-managed.

Spectral Enhancement offers a **Conditional Saves** toggle for its upgraded
ghost-touch armor benefit. Apply it only against possession or negative energy,
and only when the extra spell point was paid. It grants the source's circumstance
bonus, not resistance or general armor. CL1/4/5/9/10/20 application and removal
pass in both phases of `build/pcgen-spheres-45x1v9yi`. This toggle is removed
before saving; it does not construct ghost-touch armor or grant energy resistance.

Cripple now has a received temporary effect for attack, save, skill, and initiative
penalties. Initiative is a Dexterity check; other ability checks remain
player-managed rather than incorrectly reducing ability scores. CL1/4/5/9/10/20
application and complete removal pass in both phases of
`build/pcgen-spheres-2trjh3kt`. Cripple is removed before saving in this fixture.
The full build passes with 41 catalog tests, 104 feat tests, 655 scenario checks,
and 21,147 engine checks.
Retained Cripple CL10 persistence and post-reload removal also pass in
`build/pcgen-spheres-53xdeb4s`, including its combined initiative penalty with
Superior Reflexes and restoration of unaffected skill bonuses.

Duration, concentration, target legality, Dual Enhancement's additional spell
point and number of targets remain player-managed. These are received-effect
records, not a complete casting transaction system.

## Received Protection effects

The same selector offers Deflection, Armored Magic (armor or shield), and
Resistance aegises with their own bonus types and caster-level scaling.
Breathless, Inner Peace, Deathless, and Fateless additionally offer explicitly
named **Conditional Saves** toggles. Enable those only for a qualifying save
and disable immediately afterward. They apply a +4 morale bonus, not a permanent
bonus to all saves; PCGen does not identify an incoming effect automatically.
These toggles do not implement the aegises' immunity or additional-save rules.

Save/reload passed in `build/pcgen-spheres-y1yt_csk`, including morale
non-stacking, disable/reactivate, and removal preserving another morale source.
The conditional toggles are exercised and removed within each phase, not retained
in the saved character. The four unconditional aegises are retained across saves.

Slippery now applies enhancement bonuses to Acrobatics, Escape Artist, and CMD,
without changing AC or CMB. Caster-level boundaries, removal, and retained CL10
save/reload pass in `build/pcgen-spheres-pc5jntqn`. Its immediate-action escape
attempt is not executed automatically.

Resist Transformation has a conditional +4 morale save toggle. Eyeless and
Stabilize have conditional +4 morale AC/save toggles; Iron Shield has the source's
untyped +4 AC/save toggle. Their descriptions retain the source exclusions
(disbelief, Bludgeon attacks, vacuum, and generic electricity respectively).
All must be disabled outside the qualifying incoming effect. Both live phases
pass in `build/pcgen-spheres-z_tuy11h`, including stacking distinctions and
inactive effects restoring ordinary defenses. These conditional effects are
not retained in the saved character and do not infer attacker identity.

Destructionless now has the same explicit conditional-defense interface for ray
attacks, evocation/Destruction effects, breath weapons, and elemental sources.
Its +4 morale AC/save bonuses, non-stacking with morale saves, deactivation and
removal pass in both phases of `build/pcgen-spheres-917x9zu7`. It is not retained
in the saved fixture and does not automatically recognize an incoming attack.

Guardian has an attacker-side conditional attack penalty. It must be applied to
the hostile attacker, not the aegis bearer, and disabled outside attacks covered
by the ten-foot range and target restrictions. CL1/4/5/9/10/20 checks pass in
both phases of `build/pcgen-spheres-jmu5nfjj`, including disable, reactivate,
remove-while-disabled, and reapply. This requires the filter correction below.

Mettle has a critical-confirmation-only toggle using the supplied caster level.
Live checks at CL1, 5, 10, 20, and 100 pass in both phases of
`build/pcgen-spheres-zrhlqqna`; deactivation restores ordinary AC and saves are
unaffected. This toggle is not retained in that saved fixture.

The coverage report now lists received-effect template keys separately from
talent mechanics, so adding target effects does not inflate completed-talent
counts. There are still no automatic duration or incoming-attack classifiers.

Inner Peace also has a received situational-skill effect for concealing emotions,
relaying secret messages, and calming creatures. These are native SITUATION
bonuses, not general Bluff/Diplomacy bonuses. Application and removal pass in
both phases of `build/pcgen-spheres-_ilfaqvz`; the effect is removed before save.

Exclusion has an **Attacker Penalty** toggle. Use it only on an attacker whose
attack is composed of the excluded material and crosses into the ward from
outside. Enter the ward caster level, and disable the modifier immediately after
that attack. It does not model the boundary or material choice, enforce entry
Strength checks, or grant AC to occupants. Caster-level scaling, toggling and
removal pass in both phases of `build/pcgen-spheres-3cify0d_`; this effect is not
retained in that saved fixture.

Helping Hand has a **Skill Reroll Only** toggle for its minimum-one circumstance
bonus. Enable only for the rerolled skill check, then disable it. The second
result must be taken; sacrificing an aegis and rolling again remain manual.
Ability-check rerolls use the same bonus at the table, not a change to ability
scores. Both live phases pass CL1/3/4/7/8/20 boundaries, disabled removal and
reapplication in `build/pcgen-spheres-7t4ufrag`. This toggle is removed before save.

## Required engine correction

Live reload testing reproduced a PCGen bonus-cache bug: a +6 temporary Strength
enhancement was incorrectly reported as +4 after adding a weaker enhancement.
Both active bonus entries and their formula values were correct. A subtotal
cached during formula evaluation survived later updates to the active map.

`tools/pcgen_bonus_cache_fix.py --apply` applies a guarded, idempotent source
patch and recompiles only BonusManager into the existing private PCGen jar.
Run it after rebuilding or replacing that jar. It clears cached aggregate sums
when updating the active bonus map; separate partial-stat maps are unaffected.
No downloaded dependencies or source archives are changed. Unexpected source
layouts are rejected. Without `--apply`, the tool checks source only, not bytecode.

## Verification

### Temporary-effect disabled-filter correction

Removing a disabled temporary bonus left its name in PCGen's suppression filter,
so a later application appeared selected but contributed no bonus. Guardian's
second application reproduced this in `build/pcgen-spheres-eiujbdnt`.
`tools/pcgen_temp_filter_fix.py --apply` applies a guarded, idempotent correction
to CharacterFacadeImpl: removal clears that effect's filter after removing its
bonuses. It recompiles the facade and its nested classes into the private jar.
Reapply after replacing the jar. Without `--apply`, only source is checked.
The upstream facade emits unchecked/preview compiler notes; this was not a
warning-free upstream build. The application's own build retains `-Werror`.

Patch scope, idempotence, malformed/partial input checks are in
`tools/test_temp_filter_fix.py`, included in the normal build. Both live phases
pass in `build/pcgen-spheres-jmu5nfjj`; full build passes with 42 catalog tests,
104 feat tests, 655 scenario checks and 21,147 standalone engine checks.

- `tools/test_bonus_cache_fix.py`: patch scope, idempotence, malformed and partial
  source rejection; included in the standard build tests.
- `tools/test_catalog.py`: deterministic effect records, bonus types, skills,
  and exclusion of source headers from skill options.
- `tools/pcgen_enhancement_effects.py`: production temporary-bonus application,
  boundaries, cancellation, removal, enhancement stacking, and saved external
  caster levels. Save/reload passed in `build/pcgen-spheres-7uyhzp44`, including
  Superior Reflexes, skill enhancement non-stacking, and untyped save bonuses
  stacking with resistance bonuses while preserving them on removal.
- The failing pre-fix reload in `build/pcgen-spheres-hbs_z5c7` passed unchanged
  after the engine correction.
- Existing Life/Enhancement reload also passed in
  `build/pcgen-spheres-ot83fb0f` with the corrected engine.

The full offline build passed, including 33 catalog tests, 104 feat tests,
655 scenario checks, and 21,147 engine regression checks. Those standalone
engine checks are not the upstream PCGen test suite; the latter was not run.