# Spheres current implementation status — October 3, 2026

Full implementation remains **open**. Catalog presence, nonempty mechanics tags,
successful parsing, and testing one choice are different acceptance levels.

Continuation: Possess Armaments now requires Enhancement **and** either Object
Ride or Path of the Poltergeist. Its historical record key incorrectly spells
these as three alternatives; the key is retained for character compatibility,
but no longer controls qualification. The pinned source's semicolon and its
alternate comma-form heading agree on this conjunction. Wraith 6 live
save/reload passes in `build/pcgen-spheres-_yykax_g`, checking both legal routes,
each insufficient prerequisite alone, prerequisite removal and pool restoration.
The option is exercised for qualification, not retained as a saved selection;
possession/enhancement execution remains table-resolved. The 36 class-catalog
tests, generated-class consistency and structural package checks also pass.
Reactive Possession now requires either selected Possess Armaments or
Poltergeist with Wraith level 8 (improved path possession). Both routes,
prerequisite loss and the level 7/8 boundary pass live save/reload in
`build/pcgen-spheres-z5xv5xuk` and `build/pcgen-spheres-h87viqul`.
Armaments is selected and removed within each phase, not retained as a saved
choice. The full build passes with 36 class-catalog tests, 59 feat tests,
655 scenario checks and 21,147 engine checks; this is not full Spheres completion.
Improved Expanded Path Possession also now checks Wraith 12 and its base haunt.
The level 11/12 boundary and base-haunt removal pass save/reload in
`build/pcgen-spheres-o7x9ecq0` and `build/pcgen-spheres-ikv1wi35`.
Expanded-path target selection, matching improved targets and sphere ownership
for those targets remain unimplemented; these gates alone do not finish that
option family. The existing records and keys are preserved.

## Scope and invariants

Plague continuation: the five published Plague feats now use a source-guarded
adapter for four complete entry branches. Blood/Death require their own sphere
CL 5; Duelist/Alchemy require BAB 5. Shared Virulent Ailment, character-level,
and Death/Shroud requirements remain outside the OR. Unknown source changes
raise an error rather than silently retaining old prerequisites. Live Power
save/reload in `build/pcgen-spheres-7030f2rj` and Might save/reload in
`build/pcgen-spheres-0o35pz7y` exercise all four routes, prerequisite loss and
refunds. Rotten Hordes now grants and refunds its spell point. Pathology offers
the twelve published diseases and spends one feat for two choices; selection
and full refund pass in both Power phases. These Plague choices are removed
within each phase in that initial fixture. Retained-disease persistence now
passes in `build/pcgen-spheres-lumhx8by`: Blood, Virulent and Pathology remain
in the saved character, and reload verifies the exact Blinding sickness and
Mindfire choices before removal. Repeated selections also pass in
`build/pcgen-spheres-2c9116nt` save/reload:
four distinct diseases cost two feats, previously selected diseases are excluded,
and removing one selection refunds one feat while retaining two diseases.
Disease execution remains table-resolved.
That checkpoint passed the full build and 49 feat tests with 400 unresolved
feat records. The subsequent channel/bound-nexus/blessing pass reduces that count to 386.

Channel-energy prerequisites now check actual ability identity: upstream
`ChannelEnergy`/`Channel Energy`/polarity types, or the selected Soul Weaver channel record.
Class levels alone do not qualify. Generic and positive/negative predicates
are supported. Ten feat prerequisite reviews are resolved,
including Energized Spell's explicit positive-or-negative alternative.
Soul Weaver live save/reload passed in `build/pcgen-spheres-3wybot5g`;
Core Cleric live save/reload passed in `build/pcgen-spheres-tvrpj6_a`.
Core Paladin's channel uses the spaced type rather than Cleric's unspaced
type; its generic qualification and retained feat save/reload pass in
`build/pcgen-spheres-jbmpobnu`.
Both test selection, prerequisite loss, refunds and retained Channel Luck.
Core Cleric does not incorrectly receive Soul Weaver's Life/Death grants.
The full build and 51 feat tests pass. Incanter's matching channel types were
inspected, but its specialization lifecycle was not exercised by this harness.
Dice thresholds now require one recognized pool with enough d6s, never a sum
of independent pools. Core branches check die size as well as count. Soul Weaver
level 7 (`build/pcgen-spheres-9hltnd0i`), Cleric level 6
(`build/pcgen-spheres-44012uoe`) and Paladin level 7
(`build/pcgen-spheres-xco2mkpq`) pass save/reload, testing the 4d6 boundary
and feature loss where the channel is a selection. Unknown channel providers
remain fail-closed. The Cleric 5/Soul Weaver 5 save/reload fixture in
`build/pcgen-spheres-xljd1sey` retains both positive channels and rejects
Pulsing Channel: two independent 3d6 pools do not satisfy 4d6. Incanter dice
checks still have structural rather than dedicated live coverage. Channel feat tactical effects remain
table-resolved.

Soul Weaver now exposes separate channel-use and bound-soul capacities:
`max(1,3+CHA)` and `max(1,3+SPHERES_CASTING_ABILITY)`, respectively.
INT-based casting with CHA 3 passes save/reload in
`build/pcgen-spheres-9udmv1ib` (one channel use versus seven souls).
CHA 18 at level 7 passes in `build/pcgen-spheres-k7iaaehj`.
These are capacities, not automatic spending/replenishment or soul movement.
Nineteen class-catalog tests and the full build pass after this change.
Bound-nexus prerequisites now recognize the actual Soul Weaver resource feature.
Extra Nexus Powers grants two souls per repeated selection, not more nexus-power
choices. Save/reload in `build/pcgen-spheres-wr8fee8v` verifies two grants,
partial/full refunds, one retained selection and its saved nine-soul capacity.
Core Cleric save/reload in `build/pcgen-spheres-m71s9ym2` verifies that channel
energy alone cannot qualify. All 52 feat tests and the full build pass.
Ensouled Illuminations/Vision prerequisites are resolved by this feature check;
their tactical effects remain unautomated.

Soul Weaver bound nexus now grants all fifteen powers automatically at their
published levels (1/4/8/12/16/20), rather than offering a pool of choices.
The existing ability keys and category are retained; the category is now
noneditable with a zero selection pool. **Migration:** remove obsolete manually
purchased nexus selections from existing characters; no automatic PCG migration
or deletion of user choices is performed. New-character save/reload passes at
levels 8 (`build/pcgen-spheres-oxayku57`), 12
(`build/pcgen-spheres-2jt2ih0z`), 16 (`build/pcgen-spheres-vf67ihn3`) and 20
(`build/pcgen-spheres-122myvap`). Nexus DC uses casting ability; channel DC uses
Charisma. The level-12 fixture verifies unequal modifiers with CHA 3.

The ten blessing/blight abilities are now automatic grants from the chosen
channel polarity at levels 2/6/10/14/18. They are not purchased options and do
not depend on alignment. The controller verifies opposite-polarity exclusion,
grant removal when channel selection is removed, and retained negative-channel
grants after save/reload at levels 10 (`build/pcgen-spheres-h45vycz4`) and 18
(`build/pcgen-spheres-eqp48gbo`). Twenty-one class-catalog tests and the full
build pass. Effects on targets, summoned spirit construction, and
Blessing/Blight Versatility's opposite-polarity progression remain unfinished.
Blessing/Blight Mastery now requires an actually granted Blessing or Blight,
not merely channel energy or Soul Weaver class levels. Both polarities and
prerequisite loss pass at level 6 (`build/pcgen-spheres-wzhxdc8k`); Core Cleric
remains ineligible (`build/pcgen-spheres-8_xpo3vx`). Level-1 rejection and level-2
qualification pass save/reload in `build/pcgen-spheres-lssq2qeh` and
`build/pcgen-spheres-v0comk9m`. The low-level fixture limits repeated Extra Nexus
purchases to its available feat budget; earlier over-budget reload runs failed
and are not acceptance evidence. Fifty-three feat regressions and the full
build pass. Versatility still requires unresolved Versatile Channeler support
and remains fail-closed.
Gravewalker now has a level-20 supernatural ability record with PCGen immunity
metadata for nonlethal damage, ability drain and energy drain. It does not
automatically apply an undead type or ghost template. Ghost return and undead
reactions remain table-resolved. Level-19 absence and level-20 presence survive
save/reload (`build/pcgen-spheres-_4ej09zo`, `build/pcgen-spheres-c7d4o3gs`).
Twenty-two class-catalog tests, 53 feat tests, generated-data checks and the full
build pass, including 655 scenario and 21,147 engine regression checks.

Thaumaturge invocations had the same fixed-grant/choice error: all twelve
records were selectable from level 1, despite explicit level restrictions in
their descriptions. They now grant automatically at levels 1/3/7/11/15/19;
the existing category and keys remain, with an uneditable zero pool. The class
fixture no longer purchases Lingering Blessing. Remove obsolete manually
purchased invocation records from old characters; existing files are not
silently rewritten. Live class-table/export/save/reload checks pass at levels
2 (`build/pcgen-spheres-1412c2ww`), 3 (`build/pcgen-spheres-2himcsp9`),
18 (`build/pcgen-spheres-jzpnym_w`) and 19 (`build/pcgen-spheres-bh_isfhk`),
checking presence and absence of every invocation and the zero choice pool.
Twenty-three class-catalog tests and the full build pass. Temporary invocation
effects, Flexible Caster's temporary talent selection, resource expenditure,
and bonus-feat filtering remain unfinished. The snapshot also contains an old
invocation-use paragraph; this change preserves the existing current-rule
capacity formula rather than combining old and current versions.

Latest continuation: Cautious, Expedited and Solitary Incantation now enforce
their single-skill rank prerequisites. The loaded Core/Spheres `Base` skill type
is used; a name wildcard was rejected after live testing showed that this
PCGen version stops at the first matching skill even when its ranks are too low.
Power feat save/reload passes in `build/pcgen-spheres-9w1aqf73`, checking ranks
0/2/3/4/5 and removal. Two skills below threshold cannot combine their ranks.
Expedited selection/refund is tested; incantation execution and Cautious's
chosen-skill effect remain manual. Ritualistic Perseverance now counts two
distinct qualifying skills using CHECKMULT. Live checks explicitly reject six
ranks in one skill as a replacement for three ranks in each of two skills.
Final save/reload evidence: `build/pcgen-spheres-67z3e_pt`; full build and 45
feat regressions pass. Perseverance's chosen-skill effect remains manual.
Cautious Incantation now uses a rank-filtered skill chooser rather than free
text. Live gates verify only the two skills with three ranks are offered,
one feat point is spent, and removal refunds it. Save/reload gates pass in
`build/pcgen-spheres-5fh1y7sv`; the chooser is exercised and removed in each
phase, not retained in that fixture. The extended gate also passes repeated
distinct selections and partial/full refunds in `build/pcgen-spheres-p755_moc`.
Retained-choice persistence now also passes in `build/pcgen-spheres-_bgfkwwz`:
the fixture keeps Cautious and three Climb ranks, then verifies the actual Climb
association before removal on reload. Full build and 46 feat regressions pass.
Vigilant Skeptic now enforces `(Perception 5 AND Sense Motive 5) OR Alertness`.
Unknown skills in the conjunction still fail closed. Both qualification routes,
single-skill rejection, removal and refunds pass live save/reload in
`build/pcgen-spheres-wfpxaiv2`, alongside the retained Cautious choice.
Latest full build and 47 feat regressions pass. Vigilant's tactical benefit is
not automated by this prerequisite correction.

The contract remains in `spheres-backlog.md`: Power/Might spheres, magic/martial
traditions, Ultimate feat-based Spellcrafting, feats, traits, alternate racial
traits, base classes and prestige classes. Archetypes are excluded. Preserve
saved keys, existing pools, upstream PCGen subsystems and the dice-pool experiment.
Tactical adjudication is distinct from persistent character-building automation.

## Reproducible inventory

Run `python3 tools/spheres_coverage.py` to check the committed structured report
in `docs/spheres-coverage.json`; use `--write` after changing its catalog inputs.
The normal build tests check that report for staleness.

| Inventory | Current count | What the count means |
| --- | ---: | --- |
| Power / Might spheres | 26 / 27 | Basic catalog scope |
| Generated basic talent review records | 2,326 | Excludes four pre-existing Destruction talents |
| Generated talent records with recorded mechanics | 16 | Review-array contents, not all generator-emitted mechanics |
| Feats | 1,201 | Catalog entries |
| Feats with unresolved prerequisite clauses | 400 | Require adjudication; exact keys/clauses are in the report |
| Feats with recorded mechanics | 86 | Includes reference variables and partial effects |
| Traits | 161 | Includes drawbacks |
| Traits with unresolved prerequisites | 38 | Includes setting/GM requirements |
| Traits with recorded mechanics | 20 | Not necessarily complete traits |

The earlier conversational claim that only three feats had unresolved
prerequisites was incorrect: it searched prose rather than the structured
`unresolved_prerequisites` field. The measured baseline was 464. Exact good,
evil and non-good alignment checks resolved eight reviews. Ambiguous non-neutral
and patron-matching requirements remain fail-closed.

`catalog-mechanics.json` contains base-sphere overrides as well as talent
overrides. Its entry count is not the number of completed talents. Other
generators also emit grants, packages, choices and bonuses outside the review
arrays. No completion percentage is justified by these counters.

Tempestarii is a five-level **prestige** class, not a base class. Its short
feature file is not evidence of missing base-class levels. The current prestige
generator implements Tempestarii; snapshot inventory alone is not implementation
of the other prestige classes.

## October 3 corrections and evidence

- Reviewed reversed threshold forms (`+3 base attack bonus`, `3rd level`,
  `Sense Motive ranks 3`, `monk 3`) and `1 or more metamagic feats` now compile
  to the existing predicates. Four additional feats no longer require review.
  Tentacle Novice still requires review for the two-tentacle requirement;
  Unerring Eye retains its unsupported sphere requirements. Malformed values
  and unsupported counts remain rejected. Reversed global thresholds retain
  the existing hoisting behavior after OR branches. Dimensional Archer's Warp
  requirement, sufficient BAB, selection, prerequisite loss and refunds pass in
  both live phases in `build/pcgen-spheres-47fhwya_`; that feat is exercised and
  removed, not persisted. Other new forms have offline coverage only. Feat
  effects remain separate work.

- Explicit `Blood/Bear/Illusion/Divination sphere caster level N` clauses now
  require the named sphere and its own caster level, never global CL or another
  prerequisite sphere's CL. Unknown and martial spheres remain rejected for
  this grammar. Three feats no longer require review; Glimpse The Flow retains
  review for its unmodeled sense-talent requirement. All four exact forms and
  malformed alternatives have offline regressions. No live feat-effect or
  sphere-specific CL-modifier test is claimed for this change.

- Unarmored Striker now automatically grants Equipment - Unarmored Training,
  without granting the Equipment sphere, its free talent, or spending a paid
  combat talent. Selection/removal/refund checks and retained art/talent
  save/reload pass at Striker 2 in `build/pcgen-spheres-cecp2c9x`.
  The talent's conditional armor bonus remains unimplemented; this correction
  completes the class-option grant, not the underlying Equipment mechanic.
  Class-catalog regressions, generated-file checks and the full build pass
  (including 655 scenario and 21,147 engine checks).
- Armored Striker can now be selected twice, not just once, and rejects a
  third selection. Its shared count survives partial removal and refunds;
  level-12 controller save/reload checks pass in `build/pcgen-spheres-05z4q8yx`.
  The two Armored selections are exercised and removed during each phase;
  Unarmored Striker is retained in this fixture. Applying the class AC bonus
  under medium/heavy armor remains a separate outstanding mechanic.

- Destructive Talent provides a blast-only, level-scaled trait damage variable,
  shown in the Destruction ability summary. It does not increase weapon damage;
  removing Destruction disables the bonus, and restoring the sphere restores it.
  Live selection, prerequisite loss/restoration and refund checks passed at
  levels 10 and 20, with save/reload evidence in `build/pcgen-spheres-g4aw0dta`
  and `build/pcgen-spheres-_zznk1o5`. A dedicated `destructive` profile actually
  retains the trait and verifies its bonus immediately on reload; both phases
  passed at level 10 in `build/pcgen-spheres-gyx5160v`. Level-1 save/reload also
  passed in `build/pcgen-spheres-748rosor`. Mixed-blast damage-type choice and
  application to a target remain table-resolved.

- Extra Blended Training Talent now funds one shared allocation per paid feat
  selection, spent on either the existing magic or combat talent pool. The
  original feat key is retained. Earlier saved selections need their new
  allocations chosen; no existing talents are silently reassigned. Initial live
  save/reload in `build/pcgen-spheres-j9q3ukyg` verifies repeated feats, mixed and
  repeated allocations, partial/full refunds, and both retained allocations.
  Expanded save/reload passes in `build/pcgen-spheres-hvsj2ktl`: exhausted-pool
  rejection and losing/restoring martial focus disable/restore both grants.
  Remove purchased talents and allocations before refunding the parent feat;
  automatic dependent-choice deletion is not implemented.

- Extra Emotion grants one Eliciter Emotion choice per selection and spends a
  feat each time. Elicit Strike and Extra Emotion require the actual level-2
  Emotion feature, not an already selected power. Tier gates remain unchanged.
  Live save/reload passes at levels 1, 2 and 12: respectively
  `build/pcgen-spheres-efysn1cu`, `build/pcgen-spheres-grtk2ucj`, and
  `build/pcgen-spheres-0okml0wd`. Tests cover pre-feature rejection, repeated
  grants, partial/full refunds and a retained Extra Emotion feat on reload.
  Elicit Strike's attack delivery remains table-resolved.

- Extra Mystic Combat now requires the actual class-feature marker granted at
  Mageknight level 2 and adds one choice per paid feat selection to the existing
  Mystic Combat pool. Normal option prerequisites still apply. Live level-1
  rejection/save/reload: `build/pcgen-spheres-3c3no3jz`; level-2 repeated grants,
  option purchase, partial/full refunds and two retained feat selections:
  `build/pcgen-spheres-cucgtenu` (save and reload both passed).
  Extra Arsenal Trick was investigated but NOT extended: its existing record
  serves Incanter Sword Birth. A generated Armorist override was skipped by the
  legacy-key exclusion and failed live qualification. That attempted extension
  was removed; existing Incanter behavior remains unchanged. Completion requires
  one choice per feat between eligible class pools, not a grant to both pools,
  and compatibility tests for already-saved Incanter feat selections.

- Parenthesis-aware OR parsing now handles complete sphere/talent alternatives
  and single-list talent alternatives without splitting descriptor parentheses.
  Every alternative must resolve; malformed parentheses and unknown branches
  remain fail-closed. Catty Observer's Life/Diagnose and Protection/Status
  alternatives pass independently, with its global MSB requirement retained.
  Level-2 save/reload rejects both despite complete sphere/talent pairs
  (`build/pcgen-spheres-6tnxbxgt`); level-10 accepts both. Shape Expert accepts
  either Energy Wall or Explosive Orb, but not Destruction alone. Combined
  level-10 save/reload evidence: `build/pcgen-spheres-38oyzxza`. The same gate
  verifies that each of Skillful Force's three enumerated talents independently
  qualifies and refunds correctly; comma lists without OR remain conjunctions.
  Empty or unbalanced parenthesized prerequisites remain fail-closed. These tests
  check qualification and refunds, not automation of the feats' effects.

- Normalized `Alchemy sphere (formulae) package` to the existing package
  prerequisite grammar, retaining both sphere and package requirements.
  Unknown packages remain fail-closed. Tech/Alchemy live save/reload passes
  in `build/pcgen-spheres-co9ve0z6`: Tech alone, missing Ammo Spitter, absent
  Formulae and the Poison package do not qualify Technologically Alchemical
  Ammo; restoring the required selections qualifies it and removing them
  revokes qualification. Feat effects and ammunition inventory remain manual.

- Daysense grants +1 to both Geography and Survival, but only the selected
  skill becomes a class skill. Its bounded skill chooser, duplicate restriction,
  bonus removal and pool refunds pass the trait controller gates. The separate
  `--profile daysense` save/reload profile retains the Survival selection and
  verifies its class-skill effect and both bonuses before removal. Evidence:
  `build/pcgen-spheres-v_rgf37g`. This is additional coverage, not a replacement
  for the Aura/Technophile persistence profile. Time-of-day awareness remains
  table-resolved.
- Learned Readiness, Industrial Worker and Higher Calling now grant their
  specified class skills. Prepared Casting assignment, gathering project
  materials, and weekly augury respectively remain unautomated; these records
  do not manufacture unconditional bonuses for those effects. Offline and live
  selection/removal/refund checks pass. The extended Daysense save/reload run
  also passes in `build/pcgen-spheres-7uaj8tau`; these three additional traits
  are exercised during each phase but are not saved selections.
- Compassion remains open: its optional Charisma-for-Heal substitution must
  not stack with Scholar's optional Intelligence-for-Heal substitution. A
  shared mutually exclusive ability choice is needed before adding this effect.
- Weird Virtuoso now exposes the +1 trait bonuses for subtle somatic casting
  through Perform (Dance) and whispered verbal casting through Perform (Oratory)
  or Perform (Sing). Ordinary Perform checks receive no bonus. These situational
  bonuses and refunds are checked in both phases of
  `build/pcgen-spheres-50rhclvt`; the trait is not retained in that saved fixture.
  Actual component concealment checks remain player-resolved.
- Impersonator and Guardian Of The Real retain their class-skill grants and
  now also grant their +2 situational bonuses for impersonation and monster
  identification respectively. No general Bluff/Planes bonus is added. Live
  application/removal checks pass in both phases of
  `build/pcgen-spheres-k_4o0f_c`; neither is a saved selection in that fixture.
- Scarred by War now grants native PCGen DR 1/piercing in addition to its
  Intimidate class skill. The controller checks the piercing bypass entry and
  restores the prior damage-reduction state and trait pool after removal.
  Both phases pass in `build/pcgen-spheres-6w5u1whi`; Scarred by War is exercised
  and removed in each phase, not retained for persistence.
- Steel Body grants its HD-scaled HP bonus through PCGen's native HP field.
  Selection/removal checks pass at levels 1, 2, 3 and 4 in
  `build/pcgen-spheres-clrgjy5e`, `build/pcgen-spheres-ilq2d0zs`,
  `build/pcgen-spheres-jzb6olan` and `build/pcgen-spheres-26ploe6d` respectively.
  Level-3 reload also passes. The trait is exercised and refunded in each phase,
  not retained in those saved fixtures. Additional `--profile steel` level-4
  save/reload in `build/pcgen-spheres-7mi__0_t` retains Steel Body and verifies
  its HP grant and removal on reload. Level-up/down with it retained is untested.
- Abrasive now exposes its -5 Diplomacy penalties for improving attitudes,
  entertaining and impressive displays as separate situations, not a general
  Diplomacy penalty. The motivation requirement and effects on allies remain
  table-resolved. Penalty application/removal and the existing drawback pool
  accounting pass in both phases of `build/pcgen-spheres-ls142nh5`; Abrasive is
  exercised and removed, not persisted in that Steel Body/Aura fixture.
- Bountiful Charm now adds +2 only to Diplomacy's Recruit cohorts situation;
  its existing Diplomacy class-skill grant is retained. Adapting it to a
  replacement recruitment skill remains manual. Selection/removal and absence
  of a general Diplomacy bonus pass in both phases of
  `build/pcgen-spheres-v5be9mwo`, alongside the retained Steel Body fixture.
- Bare Drone prerequisites resolve only with an explicit Tech sphere clause.
  Five clauses are resolved; four feats no longer require manual prerequisite
  review (Technical Compatibility still has another unresolved requirement).
  Drone stat blocks and these feats' effects remain separate work. Tech live
  save/reload passes in `build/pcgen-spheres-l3imgkcv`, checking that Tech alone
  and AI alone do not qualify, Drone does, and removing the last Drone revokes
  qualification. These are qualification checks, not feat-grant persistence.
- Trait persistence assertions now query the parent ability category, as required
  by upstream `hasAbilityKeyed`. Aura and Technophile actually remain in the
  saved character and their bonuses are checked before removal on reload.
  Corrected save/reload evidence: `build/pcgen-spheres-yfd3olre`.
- Corpse Watcher grants +3 only to Heal's information-gathering situation;
  Colloquial Terms grants +4 only to Linguistics without a shared language.
  Neither changes the general skill bonus. Skeptical grants +1 Sense Motive;
  its conditional Will save remains table-resolved. Selection, removal and
  pool/bonus refunds pass in both trait gate phases above. These three traits
  are exercised then removed, not retained for persistence assertions.
- Hubris Style, Defiance and Triumph now enforce nonlawful alignment and exact
  BAB-or-Monk-class-level thresholds. Unknown classes remain fail-closed.
  Offline tests cover all three thresholds and malformed alternatives. Live
  Power feat tests cover all nine alignments, the BAB route, prerequisite loss,
  refunds and rejection of character level as a substitute for class level.
  A positive Monk-level alternative still needs its own live fixture.
- Life's CL-dependent bonus formulas could cache caster level as zero during
  PCGen bonus-map rebuilding, rejecting otherwise valid subsequent selections.
  Reproduced in feat reload and the new dedicated Life gate. Healing outputs
  now use derived definitions and static talent-presence counters; there are no
  harness cache-reset workarounds or upstream changes. Level-10 Life save/reload
  passes in `build/pcgen-spheres-mgp4oq4e`, including explicit recalculation,
  all three modifying talents retained in the saved character, individual
  removals, duplicate/prerequisite rejection and full pool refunds.
  Level-2 save/reload also passes in `build/pcgen-spheres-6xsv2obs`.
  Level-2 INT 7 save/reload passes in `build/pcgen-spheres-emt4u62h`, retaining
  the negative casting modifier rather than silently clamping it.
  Power feat save/reload passed in `build/pcgen-spheres-fri4bna_` after the base
  Life correction; Spellcrafting save/reload passed in
  `build/pcgen-spheres-thbs2fex`. Failed earlier runs are not acceptance evidence.
- Counterspell now exposes its own magical skill check total. Counterspell
  Mastery's +2 affects that check only, not global MSB. Its immediate-action
  timing and spell-point spending remain table-resolved. Final Power feat
  save/reload gates pass in `build/pcgen-spheres-4qph2mbd`, including the Hubris
  gates and Life caster-level invariant. Mastery is exercised then removed;
  the saved selections remain the existing focus/counterspell chain.

- Exact good/evil/non-good prerequisites now use upstream alignment predicates.
  Live Power feat save/reload tests cover all nine alignments, good-feat selection
  and rejection, refunds, and evil/non-good qualification with required spheres
  and the actual Terrain Casting tradition prerequisite selected.
  Evidence: `build/pcgen-spheres-bjlz2ln2`.
- Enforced Terrain Defiler/Terrain Focus and Specialist Defiler/Terrain Focus
  exclusions without replacing primary prerequisites. The extended live gate
  tests Terrain Defiler/Focus in both selection orders, including target choice,
  qualification restoration and refunds. Both phases passed in
  `build/pcgen-spheres-768nr9_j`. Specialist Defiler's reciprocal restriction has
  offline coverage; its full prerequisite chain was not exercised live.
- Aura grants its Religion class skill and +1 trait bonus. Its light is still
  table-resolved. Spatial Awareness grants its Engineering class skill; its
  situational Creation attack modifier is not applied indiscriminately.
- Technophile grants +2 Craft (Mechanical) and +2 Tech charge capacity only while
  Tech is present. No charge pool is created without Tech. Trait live gates
  exercise bonuses, removals/refunds and prerequisite loss in both phases.
  Initial evidence: `build/pcgen-spheres-4yl_e5pt` exercised and removed the
  traits. The newer retained-selection evidence is recorded above.
- Added coverage regressions for duplicate/missing metadata, deterministic
  output, partition totals, and structured unresolved-prerequisite accounting.
- Latest full build passed 175 Python tests, profile/candidate suites, 655 scenario
  checks and 21,147 engine checks. Package/generated-data checks passed. These
  passes certify the tested slices, not completion of the remaining ledger.

### Fey Adept vision continuation

Darkvision now grants 60 feet at level 2 and extends an existing range of at
least 30 feet by 30 feet, using a 30-foot base minimum and a 30-foot vision
bonus. Live tests cover external ranges 0, 20, 30, 60 and 120 feet and removal
of each external source. Both phases pass at levels 1 and 2:
`build/pcgen-spheres-44nl5v3w` and `build/pcgen-spheres-c8_eovcq`.
See in Darkness's level 13/14 boundary also passes both phases:
`build/pcgen-spheres-215kxcz8` and `build/pcgen-spheres-k5zfybm0`.
External templates are temporary test inputs, not persisted character choices;
the class-granted vision survives reload. The fixture commits parsed vision
tokens before adding each template. Earlier uncommitted-template and incorrect
VisionType API runs failed and are not acceptance evidence.
The full build passes, including 30 class-catalog tests, 56 feat tests,
655 scenario checks and 21,147 engine checks. This closes these vision effects,
not Fey Adept's remaining illusion/constructed-entity mechanics.

### Commander option eligibility continuation

Commander options no longer all qualify at level 1: Enhanced Tactics require
level 2, Battlefield Specialist level 3, and Logistic Specialty level 7.
All generated options have offline coverage. Representative predicates pass
before and after reload at levels 1, 2, 3, 6 and 7, respectively:
`build/pcgen-spheres-p75iuab0`, `build/pcgen-spheres-lrsyc4vw`,
`build/pcgen-spheres-0cxy18xh`, `build/pcgen-spheres-jyai1_3a`, and
`build/pcgen-spheres-b1_p0xzp`. These checks verify eligibility and existing pool
progression, not controller purchases of these options.

Expert Coordinator now grants one dedicated qualifying teamwork-feat slot per
selection and is repeatable. Controller tests at level 7 verify two grants,
partial/full refunds, unchanged ordinary feat budget, and both retained grants
after reload: `build/pcgen-spheres-ay6xfnar`. Extended checks in
`build/pcgen-spheres-llv8lnl_` select Twilight Adept using a temporary Light
sphere source, verify dedicated-slot spending and prerequisite loss, and remove
parents with a spent child. PCGen retains that feat and exposes a negative pool;
removing the orphaned choice restores zero. Automatic cascade removal is not
implemented. The child feat is exercised then removed, not persisted; both
parent selections are retained. Ally sharing remains table-resolved.
The class runner now compiles its harness before
launching so package-private controller APIs use the same class loader. Fey
Adept level 2 and Symbiat/Rogue stacking round trips still pass with the updated
harness (`build/pcgen-spheres-w09g3iz3`, `build/pcgen-spheres-5su0bd64`).

Commander terrain options now expose self-only situational skill modifiers for
Desert, Jungle, Mountain, Plains, Urban, Underground and Water. No unconditional
skill bonuses or ally bonuses are applied. Offline checks protect scope and
bonus type; level-7 controller tests exercise Plains selection, minimum-one
bonus, unchanged general Survival, removal and pool refund in both phases:
`build/pcgen-spheres-7xo9df1l`. These terrain selections are not retained in the
saved character; other terrain effects (movement, defenses, vision and allies)
remain unautomated. The option adapter is `tools/spheres_commander.py`.

Commander now exposes level-gated Group Focus daily capacity and simultaneous
Enhanced Tactic capacity without granting permanent ally bonuses or spending
resources. Both phases pass at levels 1, 5, 10, 17 and 20:
`build/pcgen-spheres-xkiibmnf`, `build/pcgen-spheres-5yqrf23w`,
`build/pcgen-spheres-7adftebh`, `build/pcgen-spheres-upqai4vl`,
`build/pcgen-spheres-2ikswpsl`. These are sheet reference capacities, not combat
state tracking. Class-catalog offline coverage now contains 34 tests.

### Commander logistics continuation

Call In A Specialist now exposes arrival hours, maximum service days and
specialist class level. Field Feeding exposes the DC and additional-creature
capacity. Call In the Cavalry exposes mount count, maximum HD, movement reference
and loan duration. These are reference values, not created NPCs, automatic
Survival success, mount inventory or modifications to the commander's speed.
Settlement eligibility, weekly use, death-related cooldowns, specialist services,
feeding checks and mount behavior still require table resolution.

Live Commander save/reload at levels 10, 11 and 19 verifies the loan-duration
boundary, option selection/removal, disappearance of removed reference values,
pool refunds and retained Cavalry selection. Evidence respectively:
`build/pcgen-spheres-h4taqf4q`, `build/pcgen-spheres-q_oiazoc`, and
`build/pcgen-spheres-frazqsop`. Specialist and Feeding are exercised and removed
in each phase; they are not the retained selections. The earlier logistics
reference checks also passed at levels 7 and 20 before Cavalry was added.

Friends In Close Places now requires Leadership, its Followers package and
Call In A Specialist. It exposes a separate half-arrival-time reference (including
fractional hours) and a follower-only skill-check bonus, not a personal Diplomacy
bonus. The level-11 round trip in `build/pcgen-spheres-jkcoy78a` verifies the
5-rank +2 value, 6.5-hour arrival, prerequisite loss and refunds. The feat is
exercised and removed in both phases, not persisted. Broader follower construction
and conditional application remain table-resolved.
The extended round trip in `build/pcgen-spheres-wmpuvf2v` also verifies the
10-rank +4 threshold with a separate rank-grant fixture. Full build and generated
consistency checks pass after this addition (57 feat and 35 class-catalog tests,
655 scenario checks and 21,147 engine checks). The current structured report
contains 382 unresolved feat prerequisite reviews and 90 feat mechanic records;
these counts are not a completion percentage.

### Loaded practitioner class prerequisite continuation

Exact Commander, Armiger, Scholar, Blacksmith, Striker and Technician level
clauses now compile to named-class prerequisites rather than total character
level. Unknown classes and invalid levels remain blocked. Six feat reviews are
resolved; their extra-option benefits and repetition rules still need separate
implementation. Live Commander level 4/5 round trips verify the threshold and
reject a Striker-specific feat on a Commander:
`build/pcgen-spheres-dl5wtye_`, `build/pcgen-spheres-o1cmbvi8`.
Other five class mappings have offline coverage, not individual live matrices.
Full build passes with 58 feat tests; current unresolved feat count is 376.

Repeat-limit decision still required: the published Extra Battlefield
Specialization, Extra Prowess, Extra Striker Art and Extra Technical Insight
text says second selection at 11th and third at 17th level without explicitly
repeating the class qualifier. Extra Scholar's Knack and Extra Smithing Insight
similarly permit a second selection at 15th. Initial named-class prerequisites
are enforced; repeatable pool grants are not implemented yet. Confirm whether
these repeat thresholds mean total character level or named-class level before
implementing multiclass behavior. Keep initial class thresholds separate from
repeat thresholds and test both single-class and mixed-class boundaries.

### Wraith base references continuation

Added daily form rounds, an explicit level-20 unlimited flag, haunt/possession
DCs and simultaneous possession capacity. Possession references are disabled
before level 2; multiple-target capacity starts at level 10 with a minimum of
two. Unlimited rounds do not automatically activate incorporeality or change
the character's subtype. Host stat replacement, durations by target CR, paths,
haunt effects and Strengthened Possession are still incomplete.

Live save/reload passes at levels 1, 2, 9, 10, 19 and 20, respectively:
`build/pcgen-spheres-gpr5c2up`, `build/pcgen-spheres-ks2ticuj`,
`build/pcgen-spheres-s3iak4hg`, `build/pcgen-spheres-ptan345s`,
`build/pcgen-spheres-5pa3d_9o`, `build/pcgen-spheres-f4p286gl`.
Full build passes with 36 class-catalog and 58 feat tests, plus 655 scenario
checks and 21,147 engine checks. These base reference tests do not certify
unimplemented haunt prerequisites or possession execution.

### Wraith repeatable selections continuation

Extra Wraith Haunt now requires a class feature granted at Wraith level 3,
and each selection adds one haunt slot while spending one normal feat slot.
Extra Incorporeality adds four daily form rounds per selection; level 20 keeps
the existing zero/unlimited representation instead of creating a finite cap.
Forced Wraith Form requires Share Wraith Form and permits at most two selections.
Its counter is defined on the class, so partial removal preserves the remaining
selection. Actual attacks, saves and application to targets remain table-resolved.

Live level-3 save/reload passes in `build/pcgen-spheres-c824fb8u`, covering
repeated feat grants, haunt spending, prerequisite loss, third-selection rejection,
partial/full refunds and persisted repeated Extra Incorporeality selections.
Forced Wraith Form is exercised and removed in each phase, not retained.
Level-2 rejection and level-20 unlimited-round persistence passed in
`build/pcgen-spheres-dz_fc2v9` and `build/pcgen-spheres-snm0s2rb` before the
Forced Wraith Form extension. Full build passes: 59 feat and 36 class tests,
655 scenario checks and 21,147 engine checks. Current feat metadata has 375
unresolved prerequisite reviews and 91 records with mechanics; these are not
completion percentages. Remaining Wraith paths, haunt prerequisites/effects,
host construction and Strengthened Possession remain open.

### Wraith path skills and multiclass correction

Path records now grant their listed class skill and, from Wraith level 4,
an insight bonus of half Wraith level. Missing skill declarations stop generation.
The path-sphere boost now replaces only the Wraith class's medium-caster
contribution, not the entire character's caster level. This preserves levels
from other casting classes instead of cancelling them.

Level-3 save/reload passes in `build/pcgen-spheres-u8lxftul`; Wraith 4/Fey Adept 3
save/reload passes in `build/pcgen-spheres-8t2xfi2e`. The latter verifies Death
caster level 7, retained Despoiler path, Heal class skill, +2 insight bonus,
and removal/refund. An initial test queried Life instead of Despoiler's Death
sphere; its failed logs are not evidence of the stacking bug. The corrected
formula is protected by offline tests and the successful mixed-class gate.
Full build and generated class checks pass. Path possession implementations,
duplicate-sphere replacements and other classes' mastery stacking still need work.

## Remaining acceptance ledger


### Fey Adept Feytouched

Extra Shadowstuff now enforces the actual shadow-point resource and adds two
points per repeat. Greater Shadowmark requires the shadowmark feature and dice
threshold; it changes die size from d6 to d8 without adding dice. Both feats
retain their grants on reload. Live gates test two repeats, partial/full refunds,
duplicate rejection, isolation from spell points and a non-Fey-Adept negative
fixture: `build/pcgen-spheres-juzmmdu6` and `build/pcgen-spheres-d4svpi3e`.
Unresolved feat reviews are now 383; 89 feats have recorded mechanical tags.

Level 20 automatically grants DR 10/cold iron and a +2 luck bonus on all three
saves. Spell/effect-only treatment as fey is documented, not implemented as a
global creature-type replacement. Level 19 and 20 save/reload passes:
`build/pcgen-spheres-yeu3aqmx` and `build/pcgen-spheres-nbkre3de`.
The exported save totals include the capstone bonus independently of the base
class table. Full build passes with 30 class-catalog regressions. Shadowstuff,
constructed illusions, vision stacking and other class mechanics remain open.
Shadow point capacity now uses Charisma (not casting ability), with a minimum
of one; Shadowmark's target-only Will penalty and Master Illusionist's residual
duration have separate references. They do not alter the caster's saves or
automatically spend points. Live save/reload tests vary CHA through 3, 10 and
18, restoring it before saving. Levels 1, 7 and 20 pass in
`build/pcgen-spheres-orb6158b`, `build/pcgen-spheres-n6zuhy0x`, and
`build/pcgen-spheres-5rysbqf1`. Full build passes after these additions.

### Symbiat defensive feature integration (current evidence)

Symbiat now grants upstream Evasion at level 2, Trap Sense at level 3,
Uncanny Dodge at level 4, Improved Uncanny Dodge at level 8, and Improved
Evasion at level 9. TrapSenseBonus scales by one per three class levels;
UncannyDodgeLVL and the per-class flanking contribution reuse upstream stacking
mechanisms instead of inventing independent ability names. The four-level
flanking offset applies only once Improved Uncanny Dodge exists.

Single-class save/reload gates pass at levels 1, 3, 4, 8 and 9, respectively:
`build/pcgen-spheres-37jjgjh5`, `build/pcgen-spheres-8p9rhvtx`,
`build/pcgen-spheres-lit2m8vq`, `build/pcgen-spheres-ix3rple4`, and
`build/pcgen-spheres-zyphrxgq`. Full build passes with 29 class-catalog tests.
Symbiat 4/Rogue 4 save/reload now passes in `build/pcgen-spheres-f_764mzv`:
Trap Sense totals +2, Improved Uncanny Dodge unlocks through both classes,
and the flanking threshold is 12. A stale generated class file initially
failed the Danger Sense check; regenerated output now confines that bonus to
Perception checks to avoid surprise. ESP separately grants its general
half-class-level Perception and Sense Motive bonuses from level 2.
Pushed Movement adds 10 feet of walking speed per three class levels from
level 3, capped at 60 feet. Updated single-class save/reload evidence at levels
2, 3 and 20: `build/pcgen-spheres-gbssuhhg`, `build/pcgen-spheres-rsuswqps`,
and `build/pcgen-spheres-dtjuplqm`. Full build and generated checks pass.
Armor/helplessness and
trap-specific application remain table-resolved, not unconditional save or AC
bonuses. This does not complete psionic effects or the remaining class features.

### Sentinel persistent defense and recovery references

Dedicated Defense is an additive DR/- adjustment, not a competing standalone
maximum. Live checks add and remove an independent DR 3/- template and verify
that the baseline returns. Wise Reflexes uses the better of Dexterity and
Wisdom capped at Sentinel level, rather than adding both modifiers. Live tests
cover high Wisdom at low level, negative modifiers, ties, and Dexterity winning.
The initiative bonus API excludes the base Dexterity contribution; the test
adds that contribution when checking the final modifier, while SAVE already
includes it.

Second Wind now has a level-3 automatic record with separate d6-count and
Wisdom-modifier references. Reserve temporary HP is also exposed separately
from daily reserve capacity. Neither grants permanent HP or performs healing.
The half-maximum-HP ceiling, focus recovery, spending and level-7 exception
remain table-resolved. Guardian's compulsory challenge package and duplicate
sphere substitution remain open; this is not a completed Sentinel class.

Save/reload evidence: level 1 `build/pcgen-spheres-r5s26chd` and level 18
`build/pcgen-spheres-9p826sqw` for Wise Reflexes and DR; level 2
`build/pcgen-spheres-zazyfaje` and level 3 `build/pcgen-spheres-m__p13ad`
also cover the Second Wind boundary and reserve formulas. Ability scores are
varied during both phases and restored before saving. Full build passes with
28 class-catalog tests, 655 scenario checks and 21,147 engine checks.

The reviewed `any one Admixture feat` and `at least one Proxy feat` clauses
now compile to existing feat-type predicates, resolving four more records.
Unknown families and unsupported counts remain fail-closed. Power feat
save/reload passed in `build/pcgen-spheres-bbyiqx3i`: Selective Admixture requires
an actual Admixture feat, unlocks through Curative Admixture, loses qualification
when that feat is removed, and refunds both talent and feat pools. These choices
are exercised and removed in each phase, not retained in the saved fixture.
The subsequent Proxy gate exposed self-qualification: Maintain Proxy counted
itself after its supporting feat was removed. Family predicates on a member of
that family now enumerate other loaded members, excluding the selected feat.
Both Admixture and Proxy selection, loss and refund gates pass on save/reload in
`build/pcgen-spheres-v29m70jk`. These temporary test selections are not persisted.
Full build and generated-file checks pass; this is prerequisite coverage, not
automation of these feats' effects. Multiple mutually dependent retained feats
still require a dependency-cycle audit; excluding self is not cycle detection.

Additional exact forms (`any Admixture feat`, `any one teamwork feat`,
`at least one metamagic feat`, and `MSB +N`) resolve five more feat records.
MSB uses magic skill bonus, never caster level, and remains a global requirement
after an OR branch just like its unabbreviated spelling. Unknown families,
unsupported counts and malformed values remain fail-closed. Offline regressions
and the full build pass; no new live selection claim is made for these five feats.

Spell Proxy's Special paragraph forbids Personal Magics, an unmodeled
sphere-specific drawback. It now requires explicit prerequisite adjudication
instead of silently accepting that restriction, bringing the unresolved count
back to 420. Overrides can add unresolved Special requirements without discarding
ordinary prerequisites. The final Proxy/Admixture save/reload run passes in
`build/pcgen-spheres-cxa7ddgy`, including review grant/removal and family loss.
Full build passes with 39 feat regressions. This deliberately exposes an existing
gap; it does not implement Personal Magics or claim complete Proxy rules.

Mystic Choreography's exact enumeration of three loaded casting drawbacks now
compiles to a single-choice ability predicate while retaining Enhancement,
Circle Casting and Spell Proxy prerequisites. Unknown/duplicate drawback names
and unsupported counts are rejected. Qualification before, during and after
Verbal Casting selection passes in both live phases in
`build/pcgen-spheres-0ttwrypu`; the feat is not a persisted selection. The full
build passes with 40 feat regressions, 655 scenario checks and 21,147 engine
checks. Current unresolved feat count is 419.

### Extra Arsenal Trick compatibility finding

The live Armorist extension failed before selection: the loaded legacy feat in
`data/spheres/spheres_feats.lst` requires Incanter Active Sword Birth and grants
the Incanter Arsenal Trick pool. The catalog compiler intentionally skips that
key, so adding Armorist mechanics to catalog metadata does not change the loaded
feat. Failed evidence: `build/pcgen-spheres-ngmpk_cv` and
`build/pcgen-spheres-0l6otu82`. The attempted Armorist-only override was removed;
existing Incanter behavior is preserved. These failures are not acceptance passes.

Remaining work: model a destination choice for each feat selection, preserve
old Incanter selections on load, restrict available destinations to owned class
features, and test mixed Incanter/Armorist builds, repeated selections, partial
refunds and persistence. Do not grant both pools from one feat or silently move
existing saved grants. Catalog metadata alone must not certify legacy records.

### Thaumaturge persistent benefits and mastery selections

Occult Knowledge now grants its level-2/6/10/14/18 skill bonuses rather than
remaining descriptive. Invocation DC is calculated independently of uses.
Master Invoker has two level-20 slots, eleven eligible invocation records and
no Rebuke Death option. These selections record at-will use without increasing
the daily pool available to other invocations. Activation and target effects
remain table-resolved.

The previously unused SpheresCasting feat type now identifies generated feats
with a mandatory top-level casting-core prerequisite, and the legacy Extra
Magic Talent explicitly belongs to it. This fixes its absence from Thaumaturge's
bonus category. OR alternatives that merely mention casting are not certified.
This is deliberately conservative, not a complete eligibility classifier for
all sphere-dependent feats. Final live save/reload in
`build/pcgen-spheres-yt8oay2h` checks repeated extra talents, partial/full refunds
and isolation from the ordinary feat pool. Those bonus-feat selections are
removed during each phase, while the two mastery selections remain saved.

Live save/reload: `build/pcgen-spheres-_vyfc4qw` (level 20, exact retained choices,
duplicate rejection, partial/full refunds, daily-use isolation) and
`build/pcgen-spheres-ru4mss1x` (level 2, INT 10; the original INT override
did not match the fixture and therefore did not test INT 7). Save-only boundaries:
`build/pcgen-spheres-r8h6ywul` (level 1) and `build/pcgen-spheres-zuao_5ys`
(level 19). Extra Invocations selection/removal is checked in each gate.
After correcting the fixture's INT override, actual level-2 INT 7 save/reload
passes in `build/pcgen-spheres-apmix7gk`; level-20 INT 18 save/reload passes in
`build/pcgen-spheres-h_oo0sln`. These supersede the earlier ability-score claim.
The full build passes, including 24 class-catalog tests, 655 scenario checks and
21,147 engine checks. Rules are checked against the pinned Thaumaturge snapshot
and its published class page. No upstream PCGen source changes were needed.

Forbidden lore prerequisites now check the actual granted reference feature,
not generic casting or a numeric caster-level bonus. Tainted Manabond is no
longer adjudication-gated; its Mana requirement remains enforced. Selection,
prerequisite loss and refunds pass in both phases of
`build/pcgen-spheres-03bnh6n0`. Its shared casting/backlash effect remains
table-resolved. Latest full build passes with 55 feat tests and 24 class tests.

These are workstreams, not claims that each item has already received a
source-by-source audit. Use the report's exact record lists to drive that audit.

1. **Talents:** classify every basic talent as tactical-only or requiring
   persistent mechanics. Complete prerequisite gates, bonuses, rank grants,
   repeat caps, subchoices, grants, package substitutions and associated-feat
   equivalence. Review advanced/legendary scope and source boundaries before
   importing those records; the current basic-only generator excludes them.
2. **Feats:** resolve the 375 prerequisite reviews using loaded subsystems where
   possible; retain genuine narrative/unsupported checks. Audit persistent
   effects, special restrictions, repeatability, feat equivalence and grants
   independently of prerequisite completion. Reference cost variables alone do
   not implement metamagic behavior.
3. **Traits/racial replacements:** finish prerequisites, bonuses, choices and
   replacement conflicts. Complete racial source inventory beyond the reviewed
   subset, and test upstream replacement behavior. Trait review metadata does
   not measure racial coverage.
4. **Traditions:** finish named casting traditions, special drawback credit
   accounting, conditional boons, incompatibilities and unsupported options.
   Finish named martial linked choices and proficiency exchanges across eligible
   classes, not only Conscript. Recheck newer implementations rather than using
   older append-only notes as the current truth.
5. **Base classes:** finish each option's prerequisites and effects, including
   bonus choices, resource formulas, class/sphere specialization, duplicate-sphere
   substitution and favored-class alternatives. Existing detailed adapters do
   not complete their classes. Untouched option families need individual audits.
6. **Prestige classes:** implement remaining snapshotted classes with exact entry
   gates and advancement models; test independent casting separately from
   aligned-class advancement. Do not infer missing levels from file size.
7. **Multiclass lifecycle:** verify additive/fractional advancement, shared
   initial talents, casting modifiers, traditions, focus, pools, prerequisite
   loss and Basic Magic Training's required conversion when gaining casting.
8. **Constructed entities:** companions/cohorts, drones/AI, inventions/gizmos,
   customized weapons, bound equipment, vehicles, traps/formula inventories and
   veils need choices and derived statistics, not just capacity variables.
9. **Spellcrafting:** complete supported timing/duration and special prerequisite
   validation; integrate temporary talents, book access/inventory, forgetting
   and post-selection invalidation. Preserve the existing research/learning/
   repertoire/book distinctions. Advanced components currently fail closed.
10. **Verification:** add boundary, invalid-selection, stacking, partial/full
    refund, prerequisite-loss and actual persistence tests for each implemented
    mechanic. Run broader suites and Core isolation checks. Old evidence paths
    and tests which exercise then remove a choice are not persistence proof.
11. **Documentation:** reconcile historical statements and old-machine paths in
    subsystem docs. Preserve dated evidence but separate it from current status.
    Do not label an entire class or sphere complete after testing one feature.

Completion requires resolving these workstreams against source rules and real
PCGen behavior. This document and report make the unfinished work visible; they
do not close it.