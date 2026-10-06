# Spheres current implementation status — October 3, 2026

Full implementation remains **open**. Catalog presence, nonempty mechanics tags,
successful parsing, and testing one choice are different acceptance levels.

## Live acceptance increment — 2026-10-06

The vendored live harness (`vendor/jdk16` + built PCGen JAR + JavaFX cache) runs
on this machine once the Gentoo user VM points at an installed JDK; the project
builds and the full test gate passes with the system OpenJDK 25 (`--release 17`,
bytecode major version 61).

Live PCGen immediately caught a real defect: the generated Waking Sleeper class
record used bare `Craft`/`Profession` CSKILL tokens and a nonexistent
`Simple Weapon Prof ~ All` internal ability, which aborted the whole character
load with `Unconstructed Reference` SEVEREs. Fixed to `TYPE=Craft`,
`TYPE=Profession` and `Weapon Prof ~ Simple|Weapon Prof ~ Martial`. The campaign
now loads, and `pcgen_spheres_smoke.py incanter1-int18` passes.

Two guards were added:

- `tools/test_class_tokens.py` validates every `spheres_*_class.lst` CSKILL token
  against the Core Rulebook skills plus the campaign's own skills, internal
  proficiency names against PCGen's `CATEGORY:Internal` prof abilities, and
  granted named abilities against the Core/Spheres ability records. It reproduces
  the Waking Sleeper defect offline, so live runs stay a confirmation step.
- `tools/pcgen_catalog_variables.py` (`tools/PcgenCatalogVariables.java`) selects
  a base sphere and talent, asserts the reference variable PCGen computes at the
  level-20 INT Incanter fixture, removes both and checks the pool refund, then
  retains one case through save/reload. Each case is asserted on its own because
  the level-20 talent pool cannot hold every case at once. It covers 39 reference
  values across War, Blood, Destruction, Dark, Death, Light, Mana, Mind, Nature,
  Time, Warp, Creation, Divination, Protection, Illusion, Fate, Fallen Fey,
  Weather, Enhancement and Technomancy. Both phases pass
  (`variables-save` and `variables-reload`, 39 values, reload exit 0).

The full live gate sweep (`tools/pcgen_spheres_gates.py all`) passes 42/42 gates
with `exit=0`, including the Incanter level 1/20, specialization, domain,
bloodline, healer, Destruction, Sword, and every favored-class and burst save/
reload gate. The offline build (`tools/build.py test`, JDK 25 with `--release 17`)
passes with `exit=0`: all 21 Python suites `OK`, 655 scenario baseline checks and
21,147 regression checks. All generators reproduce byte-identical output, so the
committed data is deterministic.

The catalog round trip (`tools/PcgenCatalog.java`) now also asserts the War
base-sphere references (`SPHERES_WAR_TOTEM_RADIUS_FEET` etc.) against the live
controller.

## Reference-mechanics and prestige increment

Added persistent reference mechanics (caster-level and practitioner-modifier
scaling variables exposed as `DEFINE`/`BONUS:VAR` values, never applied as
unconditional character bonuses) for the War totem/rally/momentum subsystem and
for area, duration and damage-dice references across Blood, Dark, Death,
Destruction, Mana, Light, Nature, Warp, Conjuration, Creation, Enhancement,
Illusion, Life, Time, Weather, Fallen Fey and Bear. Recorded-mechanics talent
records rose from 97 to 804. A new catalog test enforces that no reference
override grants `BONUS:COMBAT`/`SAVE`/`SKILL`/`HP`, and that repeatable talents
never own a `DEFINE` (removing one selection must not undefine a shared counter).

Added five prestige-class generators (Tempestarii, Forest Lord, Waking Sleeper,
Spheres Archwizard, Magemage) with pinned prerequisites, per-level magic-talent
grants and reference variables. Class-feature *effects* beyond those variables,
trap/trigger resolution, charm/compulsion application and companion construction
remain manual. The remaining prestige snapshots lack pinned class-skill/HD detail,
so they stay unstarted rather than guessed.

`tools/test_feats.py::test_all_mechanics_overrides_resolve_to_feats` and
`tools/test_traits.py::test_all_mechanics_overrides_resolve_to_traits` now require
every `feat-mechanics.json` / `trait-mechanics.json` key to name a real catalog
record. This caught a bogus `Blinding Flash` override that would otherwise have
been ignored silently, and `test_reference_only_feat_mechanics_apply_no_unconditional_bonus`
guards the new reference-only feat entries against acquiring an unconditional
`BONUS:`. Two entries (`Amateur Striker`, `Necrotic Heart`) were dropped or
narrowed after those guards showed they already carried real mechanics.

`tools/test_coverage.py::test_every_referenced_variable_is_defined_in_the_campaign`
now enforces that all 1,036 `SPHERES_` variables referenced by recorded talent,
feat and trait mechanics are defined by a campaign record. An undefined reference
silently resolves to 0 in PCGen, so a typo would otherwise disable a mechanic
without failing any test.

Mass Aegis now exposes additional-target capacity (not total targets) and its
reduced ten-minutes-per-CL duration. Caster-level boundaries, minimum one and
removal pass both phases of `build/pcgen-spheres-jeg0ssf1`; the talent is removed
before saving. It does not select targets, spend the extra spell point or create
the separate per-target aegises. Catalog tests pass (49).

Helping Hand's received skill-reroll bonus now uses an explicitly conditional
temporary effect with minimum-one rounding and circumstance typing. Both phases
in `build/pcgen-spheres-7t4ufrag` verify CL1/3/4/7/8/20, disabling and removal.
It neither sacrifices aegises nor executes rerolls; ability-check bonuses remain
table-applied. Catalog tests pass (48).

Ablating, Ray Deflection and Painful Aegis now expose caster-side reference
values: initial ablation chance, capped ray-deflection chance, and minimum-one
nonlethal retaliation damage. These use general Protection CL, not ward-only
bonuses. Both phases in `build/pcgen-spheres-ijtedp9v` check rounding, the two
different 50-percent cap thresholds, and removal. The three talents are exercised
and removed before saving. Miss rolls, ablation depletion, automatic-hit ray
exceptions, retaliation triggers and target damage are not automated.

Exclusion now has a received attacker-only temporary penalty, explicitly gated
by player-confirmed material and outside-to-inside ward crossing. It does not
grant occupant AC or penalize attacks wholly inside. Caster levels 1/5/10/20,
activation, deactivation and removal pass both phases in
`build/pcgen-spheres-3cify0d_`; the Exclusion modifier itself is removed before
save. Material configuration, entry Strength checks and ward placement remain
table-managed. Catalog tests pass (46).

Durable Barrier now exposes its barrier-only damage reduction using ward caster
level, including the minimum of one. It does not give the caster personal DR.
The normal bludgeoning/piercing/slashing scope and the additional-spell-point
all-damage upgrade remain damage-resolution decisions, not automatically spent
resources. Live save/reload in `build/pcgen-spheres-brject8r` verifies ward-only
bonuses, removal, and a retained talent. Catalog tests pass (44). Received-effect
save/reload was also rerun successfully in `build/pcgen-spheres-w_qq_812`.

Protection now distinguishes ward radius, paid ward duration in rounds, aegis
duration in hours, and separate ward/aegis casting ranges. Enduring Protection
changes paid ward duration to minutes without extending aegises. Distant
Protection advances through close, medium and long range with partial refunds;
zero range denotes self-centered wards or touch aegises, not ranged casting.
Live save/reload `build/pcgen-spheres-hut3otcg` exercises all three selections,
partial refunds, retained long range and Enduring duration, plus different ward
and aegis caster levels under Graphomancy/Wardlord bonuses.
The full build passes with 45 catalog tests, 104 feat tests, 655 scenarios and
21,147 engine checks. Duration countdowns, concentration and spell-point spending
are not automated by these formulas.

Protection barrier reference values now use ward-specific caster level for HP,
break DC, weight capacity, Greater Barrier's paid upgrade, Buttressing repair,
and Shaped Ward cubes. Greater Barrier ownership changes cube HP from 5 to
4 + ward CL and refunds correctly. Live save/reload in
`build/pcgen-spheres-9v8y7kya` exercises Graphomancy/Wardlord rank bonuses and
their shared HD cap without changing general Protection CL. These are construction
references, not placed barriers or damage/repair transactions. The three selected
talents are removed before save; the ward feats remain saved. A dependent VAR
bonus initially caused recursive evaluation; replacing it with a separate
ownership flag and derived formula passed both phases. Catalog tests pass (43).

Received Enhancement effects now include native temporary ability-score, skill,
and saving-throw bonuses with caster-level selection, removal and persistence.
See `spheres-enhancement-effects.md` for tested scope and the required guarded
PCGen bonus-cache correction. This does not complete the casting lifecycle.

Received Protection effects include the four unconditional AC/save aegises and
explicit conditional-save toggles for Breathless, Inner Peace, Deathless, and
Fateless. These require the player to enable them only for an eligible incoming
effect. Live save/reload (`build/pcgen-spheres-y1yt_csk`) checks morale stacking,
activation and removal; immunity and additional-save rules remain table-resolved.
Slippery's received skill/CMD enhancement bonuses also pass boundaries, removal,
and retained save/reload in `build/pcgen-spheres-pc5jntqn`; its immediate-action
escape remains player-managed.

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
| Generated talent records with recorded mechanics | 804 | Review-array contents, not all generator-emitted mechanics |
| Feats | 1,201 | Catalog entries |
| Feats with unresolved prerequisite clauses | 297 | Require adjudication; exact keys/clauses are in the report |
| Feats with recorded mechanics | 224 | Includes reference variables and partial effects |
| Traits | 161 | Includes drawbacks |
| Traits with unresolved prerequisites | 38 | Includes setting/GM requirements |
| Traits with recorded mechanics | 44 | Not necessarily complete traits |
| Prestige classes implemented | 5 | Tempestarii, Forest Lord, Waking Sleeper, Spheres Archwizard, Magemage |

The earlier conversational claim that only three feats had unresolved
prerequisites was incorrect: it searched prose rather than the structured
`unresolved_prerequisites` field. The measured baseline was 464. Exact good,
evil and non-good alignment checks resolved eight reviews. Ambiguous non-neutral
and patron-matching requirements remain fail-closed.

`catalog-mechanics.json` contains base-sphere overrides as well as talent
overrides. Its entry count is not the number of completed talents. Other
generators also emit grants, packages, choices and bonuses outside the review
arrays. No completion percentage is justified by these counters.

Five prestige classes now have generated progressions: **Tempestarii** (Weather,
5 levels), **Forest Lord** (Nature plant, 5 levels), **Waking Sleeper** (5 levels),
**Spheres Archwizard** (10 levels) and **Magemage** (10 levels, low-caster aligned
to the Mageknight class). They are independent-advancement or aligned-class records
with pinned prerequisites, per-level magic-talent grants and reference variables;
class feature *effects* beyond those variables remain sheet rules. Snapshot
inventory alone is not implementation of the other prestige classes
(`aeronaut-captain`, `bokor`, `cyborg`, `hive`, `kingking`,
`realmwalker`, `renowned-warrior`, `great-mind`,
`master-of-vagueries`, `alternate-justicar`, `ascendant-vanguard`,
`superintelligence`, `trinity-angel`, `trinity-knight`), several of which depend
on subsystems absent from this dataset (crew/airship, Kismet pool, Card Casting,
conventional spell-slot advancement, psionics, and the Guile/advanced catalogs).

Tempestarii is a five-level **prestige** class, not a base class. Its short
feature file is not evidence of missing base-class levels.

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

### Shifter prerequisite and persistent-trait continuation

The dedicated `tools/spheres_shifter.py` adapter now compiles the pinned
bestial-trait heading prerequisites, including class levels, prerequisite
traits, Endurance, darkvision, size, and alternative dependencies. Unknown
dependency names stop generation instead of silently dropping a requirement.
Existing ability keys are retained.

Persistent implementations include repeated Animal Hide, Bestial Speed,
Combat Talent and Champion grants; Quick Healing daily capacity; Animal
Trainer/Track Master/Jumper bonuses; climb/swim/burrow movement; selected
senses; Run/Multiattack/Evasion grants; and Learned Behavior's Mimicry grant.
Improved Adaptation grants the five energy resistances; Greater Adaptation
has distinct energy choices and conditional immunity grants. Fortification
has a level-dependent repeat cap (one/two/three at 6/12/18) and a percentage
reference, not automatic combat damage negation or stacking with equipment.
Baseline class grants now include Wild Empathy advancement, Endurance at 3,
inherent Constitution at 7/13/19, poison immunity at 8 and disease immunity
at 12.

Verification: 40 class-catalog tests; live Shifter saves at levels 1, 2, 6,
10, 12, 13, 18 and 19 across this implementation; save/reload of repeated
natural armor and spent trait slots at levels 10, 13 and 18. Latest complete
trait harness save/reload evidence: `build/pcgen-spheres-xrodmara` (18);
level-12 boundary save: `build/pcgen-spheres-5dmi6dca`. Tests exercise
dependency loss, combat/Champion pool refunds, energy choice and removal,
Fortification caps/refunds, actual movement totals, healing capacity and
baseline grants. Greater Adaptation's selected Acid immunity and all five
spent trait slots now also pass explicit save/reload assertions at level 10
(`build/pcgen-spheres-rwbyfr4w`). The full build passed again after these
changes, including 655 scenario checks and 21,147 engine regressions.

Flight now grants its speed and clumsy maneuverability; Perfect Flight adds
level-scaled maneuverability steps, and Skillful Flight provides distinct
Flyby Attack/Hover/Wingover choices. Level-6 selection/removal passes in
`build/pcgen-spheres-9ox_xz54` after the movement-cache engine fix below.

Natural Bite, Claws and Gore now grant size-qualified native weapons. The first
template-based attempt incorrectly left Small attacks at Medium damage and was
replaced, not retained. Small-race and temporary enlargement assertions pass
in `build/pcgen-spheres-rqhwtfjr`; this tests grants, damage and removal, not
saved natural weapons or all full-attack combinations. The generated helper file
is `data/spheres/spheres_shifter_natural_weapons.lst`. Its dice progression matches
the pinned Pathfinder game mode.

Fast Healing now has its Quick Healing/level-10 prerequisites, two-selection
cap, native healing-rate progression (1, then half class level), and partial/full
refund tests. The complete harness including natural weapons and Fast Healing
passes save/reload at level 10 (`build/pcgen-spheres-w268nqry`). These temporary
test selections are removed before saving; their own persistence still needs
dedicated saved assertions. Class-catalog suite now has 41 tests.

Not complete: remaining natural-attack options and attack-combination behavior, permanent-size target choices and
stat changes, mixed-source flight maneuverability, trait-specific target choices, remaining
conditional and tactical effects, per-effect post-selection invalidation,
multiclass Wild Empathy/Constitution interactions. Tested removal of an option is not
evidence that its choices survive saving. Scent's underwater extension and
Learned Behavior's temporary borrowing remain table-resolved.

#### Required local PCGen movement-cache correction

#### Natural-weapon persistence correction

Saved Bite plus both Fast Healing selections now survive reload and refund
correctly at level 18, including a Small-race save/reload
(`build/pcgen-spheres-eb2uab55`). A Human round trip also checks that ordinary
inventory retains its separate equipped copy (`build/pcgen-spheres-rtash002`).
This supersedes the earlier unverified-persistence note, not the remaining
full-attack/size/other-trait limitations.

The reload test exposed a pinned PCGen parser defect: restored natural equipment
sets cloned their granted weapon, so source removal could leave an equipped
orphan. `tools/pcgen_natural_equipment_fix.py --apply` preserves the grant object
for natural equipment only; ordinary equipment still uses a clone. Apply this
helper to each checkout's ignored vendor tree. It rebuilds the parser classes in
the existing local jar without downloading dependencies. The default check
verifies source, not jar contents. Two idempotence/rejection tests are included
in the normal build. Core Fighter isolation passed after the correction
(`build/pcgen-spheres-jf7k_4b7`, `build/pcgen-spheres-obbt7ro0`). Full build passed
655 scenario and 21,147 engine checks. Broader independently customized natural
equipment and multi-equip-set scenarios are not yet covered.

#### Movement-cache correction details

Live flight-removal assertions exposed stale movement values in upstream
`MovementResultFacet`: recalculation populated an existing map without clearing
removed movement sources. A one-line correction clears the map before rebuilding.
The reproducible, pinned-source helper is `tools/pcgen_movement_fix.py --apply`.
It compiles only the affected classes using the existing private JDK and replaces
them in the local jar; it also updates the extracted source so subsequent builds
retain the fix. No dependencies are downloaded. Other checkouts must apply this
helper to their own ignored vendor tree; first-party data files alone do not fix
the engine. Its default check verifies source only, not the jar.

Three offline tests cover patch idempotence, unexpected-source rejection and
preservation of shaded-jar duplicate resources. The original live failure is
recorded in `build/pcgen-spheres-p51389rl`; the corrected removal test passes in
`build/pcgen-spheres-9ox_xz54`. The expanded Shifter harness then passed save/reload
at level 18 (`build/pcgen-spheres-qffjze8_`). Core Fighter isolation passed with
the patched engine (`build/pcgen-spheres-e3cvdoir` and `build/pcgen-spheres-mbr3re8o`),
and the full build passed including the new patch tests. This isolation gate is
not a complete Core movement matrix.

## Remaining acceptance ledger

### Hedgewitch general-secret continuation

Current path follow-up supersedes the earlier general-secret level gate:
all 21 snapshotted paths now grant their explicit class skills. Academia grants
one bonus secret at level 1 and one spell point per two Hedgewitch levels;
general secrets allow level-1 Academia characters while grand secrets retain
level 10. This follows the current **List of Paths** section, not the legacy
tradition section's different Academia power. The separate Secrets class-feature
marker still begins at level 2; this change does not grant Extra Secret feat
eligibility early.

Umbral grants its minimum-1 half-level Stealth/Disguise bonuses. Green Magic
grants upstream Wild Empathy advancement and Woodland Stride. Tinker grants
typed Disable Device and trap-only Perception bonuses, not general Perception.
These are partial path effects: crafting/ritual caster level,
Umbral shadow-pool stacking, Green Magic companion construction, Tinker gadgets
and trapfinding feature equivalence, other path powers, and embedded path secrets
remain open. No path is marked complete by these grants.

Live evidence: level-1 save `build/pcgen-spheres-qf3hgwet`, level-1 class-table
save/reload `build/pcgen-spheres-kmy3405q`, and level-10 controller save/reload
`build/pcgen-spheres-6b3145mo`. Checks include overlapping class-skill sources,
removal/refunds, the first-level Academia secret, scaled spell points and skill
bonuses, retained paths and retained general secrets. Offline class tests now
number 46; the full build passes 655 scenarios and 21,147 engine checks.

Academia mastery now offers one +2 mental-ability choice at level 20. Both
selection and the actual bonus require the path and level, so removing the path
suppresses the bonus without silently deleting the stored choice. Level-20
save/reload verifies the retained choice, slot, bonus, removal and restoration
(`build/pcgen-spheres-7u6jspaf`); level-19 rejection is verified separately
(`build/pcgen-spheres-tslzqny7`).

Academia's embedded Extra Spell Points secret is now a selectable, repeatable
secret granting two spell points per selection. It checks actual Academia path
ownership and spends the shared secret pool. Level-10 live checks verify repeat
and partial/full refunds (`build/pcgen-spheres-vnnrr2vb`); level-1 save/reload
retains the selected secret, spell points and spent slot
(`build/pcgen-spheres-2utkb0zv`). Amateur Hedgewitch qualification is not yet
implemented; this record does not pretend that owning the descriptive Amateur
record establishes a specific path benefit.

General secrets require level 2 or the level-1 Academia path grant; grand secrets
retain level 10.
Champion, Combat Talent and Magical Skill grant repeatable pools with refunds.
Magical Skill uses a dedicated feat family for mandatory casting or magic-sphere
prerequisites, plus item-creation and metamagic feats; unsupported alternative
prerequisite expressions are not automatically certified by this filter.
Familiar grants the native familiar list, follower allowance and stacking master
level. This is not proof of a complete generated familiar character.
Extra Secret now checks the actual level-2 secrets feature and grants one slot
per repeat. Feat prerequisite-review count is now 374, not 375.

Live save/reload at level 6 (`build/pcgen-spheres-k7uj9c3j`) retains Familiar,
Combat Talent, Magical Skill and its selected Extend Spell feat, checks their
spent slots and refunds, and exercises repeated Extra Secret grants. Level-1
rejection passes in `build/pcgen-spheres-3h0bapyf`; level-10 grand-secret boundary
passed in `build/pcgen-spheres-b17hrw7n`. Extra Secret itself was removed before
saving and does not yet have a retained-feat assertion. Full build passes with
43 class-catalog tests, 61 feat tests, 655 scenarios and 21,147 engine checks.
Metamagic Master now selects only a possessed metamagic feat, allows distinct
repeated selections, and requires level 10 plus an owned metamagic feat. Arcane
Builder now records its selected standard item type and grants a conditional
+4 Spellcraft crafting bonus, never an unconditional skill bonus. Their actual
selected targets survive save/reload (`build/pcgen-spheres-ehfm8cs0`); level-9
grand-secret rejection passes (`build/pcgen-spheres-amh8k9q7`). Metamagic spell-point
spending, the minimum-one cost, crafting-time reduction and alternate crafting
skills remain table-applied; these selectors do not implement a casting or
crafting transaction engine. Nonstandard item types need a source-reviewed
extension rather than silently being grouped into a standard type.

Path-specific secrets, Amateur Hedgewitch benefits, remaining grand-secret effects,
Skillful Insights/skill talents and remaining general-secret effects stay open.
Dependent feat selections still require manual refunds before removing their
granting secret; familiar multiclass stacking needs a dedicated live fixture.

Shifter Breath Weapon now has a bounded configuration category containing the
eight legal energy/shape combinations. Its damage dice, casting-ability-based
Reflex DC, range, improved die size and improved range derive from the selected
traits. The improved trait retains its level-4/base-trait prerequisites. Saved
Fire/Cone configuration and both spent trait slots pass explicit save/reload at
level 4 (`build/pcgen-spheres-1jqfsacl`); level 3 passes the lower-boundary harness
(`build/pcgen-spheres-srz2i315`). Tests cover exclusive configuration, alternative
line range, removal and prerequisite loss. Damage resolution and cooldown are
table actions. Removing the parent requires refunding its dependent configuration
manually, consistent with other nested PCGen selections. Full build passes with
42 class-catalog tests, 655 scenario checks and 21,147 engine checks.

Saved natural Bite and repeated Fast Healing now have explicit level-18
persistence assertions (`build/pcgen-spheres-xlzyqvup`). Reload checks the weapon,
healing rate, nine spent trait slots, partial healing refunds and complete weapon
removal. The loaded equipment view requires `setCalcEquipmentList()` after
removing its granting trait; the master grant is removed correctly. This test
uses the normal equipment-recalculation API, not manual weapon deletion.
Immediate GUI refresh without equipment recalculation has not been verified.


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

### Wraith path talent and expanded possession selections — October 4, 2026

Ghostly Talent now grants repeatable, sphere-filtered talent slots belonging to
the selected haunt path instead of a descriptive-only haunt. Changing/removing
the path removes its slot grant. The original haunt and path keys are retained.
Live selection, spending, repeated grants, partial/full refunds and saved talent
persistence pass at level 12; the first-haunt level 3 also passes.

Expanded Path Possession and its improved haunt now grant separate target-choice
pools. Base targets require their path sphere and exclude the character's own
path; improved targets require the same selected base target, the improved haunt
and Wraith level 12. Neither target grants the original path's free sphere,
caster-level progression or class skill. Source: pinned Wraith snapshot.
Selection and prerequisite-loss checks run in both phases of
`build/pcgen-spheres-5w6h0xpw`; level-11 save checks pass in
`build/pcgen-spheres-5qbgq5ab`. Expanded target persistence itself is not yet
asserted across saves (the harness removes those targets before saving).

Remaining lifecycle limits: PCGen does not cascade-remove spent target/talent
selections when their granting haunt/path is removed; users must refund dependent
selections. Existing saved expanded haunts need targets assigned in the new
categories. Possession effects are still table-resolved. Full build passes with
38 class-catalog tests, 655 scenario checks and 21,147 engine checks; generated
class-data consistency and package checks pass.

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

### Shifter familiar, Snatch and natural-attack improvements

Follow-up persistence evidence: a fresh Small (Halfling) level-6 save/reload in
`build/pcgen-spheres-s6qk2v8l` retains Bite, Improved Natural Attack and Magical
Attacks, their three spent slots and exported damage. An attempted reload from
an older failed-save workspace had no `saved.pcg`; it is not passing evidence.

Animal Advisor now grants the upstream familiar list, one familiar slot and
additive familiar-master advancement. A level-2 save/reload retains the trait,
its spent slot and its level; removal refunds advancement. Independent-source
stacking and removal are tested with a separate defining source
(`build/pcgen-spheres-9v56_5fi`). Familiar construction itself still uses PCGen's
companion workflow and is not exercised by this harness. Snatch now grants the
upstream feat; Huge-size qualification, size loss and refund are live-tested.

Magical Attacks now supplies level-scaled enhancement bonuses to natural attack
and damage rolls, not manufactured weapons. Live checks cover the level-5
boundary, removal and nonstacking with another enhancement source
(`build/pcgen-spheres-v0fjl4fn`). Improved Natural Attack now offers possessed
natural weapon proficiencies, permits distinct selections and increases the
selected weapon's exported damage die. Live level-6 checks cover Bite, Claw and
Gore and refunds (`build/pcgen-spheres-7_kk8wkj`). Temporary reassignment after
shapeshifting is still manual; these checks do not implement transformation
execution. A fresh level-20 natural-weapon/breath/healing save/reload passed
before these additions (`build/pcgen-spheres-hvh34iay`).


### Hedgewitch embedded path secrets and Astrology selections

Reviewed against the pinned Hedgewitch source snapshot. Added separate qualifying
feat-choice pools for Combat Feat, Tactician, Touch of Darkness and the level-10
Metamagic Knowledge grand secret. Repeatable secrets grant repeatable slots;
Tactician also tracks daily-use capacity. Shadow Sculptor grants Shadow Magic
without requiring the feat prerequisites. Scholarship supplies its level-scaled
competence bonus; untrained permission and library time remain player tracked.
Greater Aid exposes the ally bonus without adding it to the caster's own checks.
Armor Training removes medium/heavy armor movement penalties, not carried-load
penalties. Green Magic's Bestial Bonds grants Beastmastery and Focusing Connection
without spending normal combat talents; Venom Immunity and Wild Vitality require
level 10 and grant the upstream immunity abilities.

Astrology now grants its missing Light sphere and two separately selected known
auras. Extra Aura grants an additional slot. Heaven's Reach is repeatable twice,
with 30/40/50-foot radius accounting and partial refunds. Known auras deliberately
do not grant permanent combat bonuses: activation, consciousness, ally range,
light level, temporary HP refresh and dismissal remain table-resolved. These
records do not implement Celestial Revelation, nor substitute for the
remaining path-power/resource and companion work. Duplicate-sphere substitution
and dependent-choice cascade removal remain open. Refund chosen feats and auras
before removing the granting secret or path.

Verification: 48 class-catalog tests; full build with 655 scenario and 21,147
engine checks; generated consistency, coverage and package checks. Fresh live
level-12 save/reload (`build/pcgen-spheres-lipsufu5`) covers metamagic-secret feat
persistence, known aura persistence, prerequisites, grants/refunds, aura repeat
cap, armor movement, immunity and bonus talent selection. Level-1 save/reload
(`build/pcgen-spheres-exfvbxnx`) retains Academia's early secret and known auras.
Not every new feat-category filter has a dedicated live dependent-feat test.

Syzygy now has its level-10/path gates and raises simultaneous aura capacity
from one to two; removing the path suppresses that capacity. Astrology mastery
adds five to the reference effective aura level at level 20. Wax and Wane is
selectable with its source-described lighting behavior. No aura is silently
activated by selecting these records. Live level-20 save/reload
(`build/pcgen-spheres-0rphhk2k`) and level-9 save
(`build/pcgen-spheres-smhgjybn`) cover capacity, mastery and grand-secret gates.

Temporal Traveler now grants its missing Time sphere and insight capacity with
the minimum-one rule; its Trapfinding secret supplies scoped trap bonuses.
Transmuter now exposes daily transformation capacity and save DC, with the
repeatable Transformations secret adding two uses. These are capacity/reference
values, not spend/recovery automation, grit equivalence, deed activation, actual
transformation construction or create-only caster-level substitution. Live
level-12 save/reload (`build/pcgen-spheres-rs1v55d6`) checks selection/removal;
these two paths are not retained in the saved fixture, so their own persistence
was not separately asserted by that fixture. A dedicated `resources` profile now
retains both paths and repeated Transformations selections. Level-6 save/reload
(`build/pcgen-spheres-pkx0bs7c`) passes saved capacity, spent slots, partial refunds,
path loss, and Intelligence 7/10/18 modifier checks. Level-1 save
(`build/pcgen-spheres-zkpbiv0f`) passes the no-secrets boundary.
Latest offline suite has 49 class-catalog tests;
full build again passed 655 scenarios and 21,147 engine checks.

### Hedgewitch Herbology and spirit resource continuation

Herbology now grants the existing Core Poison Use ability as well as Distill
Compound. Added selectable Potent Concoctions, Store Potion, Surgeon, Swift
Poison, Instant Poison and Miracle Man secrets. Grand secrets require level 10
and their named prerequisite secret; all require Herbology. Potent Concoctions
changes the preparation expiration reference from one hour to class-level hours,
not the duration of an applied concoction's effect.

Black Magic now exposes curse capacity and save DC; its repeatable Curses secret
adds two uses. Spiritualism exposes daily talent-use capacity and simultaneous
talent limits at levels 1/5/13/20, with repeatable Extra Spirit. These records do
not grant permanent talents or execute temporary-talent selection, curses,
oracle curses, hexes, alchemist discoveries, treatment, poison application or
resource spending. Those systems remain backlog items.

Verification: 51 class-catalog tests, generated consistency, coverage and package
checks pass. Full build passed 655 scenarios and 21,147 engine checks. Resource
controller checks pass at level 9 and save/reload at levels 10 and 20
(`build/pcgen-spheres-kms0oim0`, `build/pcgen-spheres-tzc3t2tp`). Dedicated retained
Herbology/Transmuter save/reload at level 10 (`build/pcgen-spheres-meigu0dt`) and
Black Magic/Spiritualism at level 20 (`build/pcgen-spheres-yw20kuck`) verify saved
path keys, spent secret slots, repeated capacities, partial refunds, path loss,
restoration and automatic Herbology grants. Herbology action secrets are
selectable rules records, not automated combat/downtime actions. Their own
retained-choice persistence is not separately tested by these resource profiles.

Follow-up level-14 Herbology save/reload (`build/pcgen-spheres-menrw3s7`) now
retains Potent Concoctions, Swift Poison and Instant Poison alongside repeated
resource secrets. It verifies the saved expiration value, dependent secret keys,
path-loss suppression/restoration and loss of Swift Poison qualification. This
closes persistence coverage for those three selections, not for every action
secret or the execution of their effects.

Combat path mastery now offers a single Strength, Dexterity or Constitution
choice at level 20. Its +2 bonus is suppressed if the granting path is removed;
the retained selection still needs to be refunded before changing paths. Live
general-profile level-20 save/reload (`build/pcgen-spheres-q6h1k99s`) tests grant,
path loss, restoration and refund; level-19 save (`build/pcgen-spheres-mnxylv6i`)
tests rejection. The Combat mastery choice is removed before saving, so this is
not a claim of dedicated Combat mastery persistence coverage. Academia's existing
retained mastery checks continue to pass. The final suite has 52 class-catalog
tests; full build again passed 655 scenarios and 21,147 engine checks.

Dedicated Combat mastery profile now passes level-20 save/reload
(`build/pcgen-spheres-vwfe6e1w`), including the retained Constitution selection,
spent slot, and all three physical-stat choices' application, suppression and
refund. This closes the Combat mastery persistence gap described above.
The spirits profile also passes level-1 save (`build/pcgen-spheres-r8qbqsmo`),
where no secret slots or extra-use selections are available.

Umbral now grants the same shadow-pool record used by Fey Adept, preserving its
existing key and Extra Shadowstuff integration. Umbral alone receives
3 + half Hedgewitch level; multiclass Umbral/Fey Adept combines levels before
rounding and uses the greater of 3 and Charisma modifier. Removing Umbral restores
the ordinary Fey Adept formula, or removes the pool if no source remains. This
does not yet implement Umbral shadowmark, create reality or the Shadowstuff
secret, and it does not claim compatibility with every other shadow-pool class.
Live save/reload passes for Hedgewitch 5 (`build/pcgen-spheres-_n9qg8qm`),
Hedgewitch 5/Fey Adept 3 (`build/pcgen-spheres-3q40qfkz`), and the existing Fey Adept
feat regression (`build/pcgen-spheres-d_iq5dpp`). Tests cover Charisma 3/10/20,
odd-level rounding, one application of Extra Shadowstuff, source loss, refunds
and retained selections. Offline class suite now contains 53 tests.

### Umbral shadowmark and additional path secrets

Umbral now grants the shared shadowmark dice, die-size and Will-penalty records.
Shadowmark uses the higher granting class level, rather than incorrectly adding
the levels that combine specifically for shadow-point capacity. Source removal
restores Fey Adept-only values or removes the ability without a remaining source.
Eyes of Black supplies scaling darkvision and stacks with existing darkvision;
its magical-darkness activation is still player tracked. Improved Shadow Sculptor
has its grand-secret gate, two-selection cap and a Shadow Magic-only CL reference
bonus, not a global caster-level bonus. Shadowstuff supplies repeatable bonus-feat
slots restricted to Extra Shadowstuff, including correct coexistence with purchased
copies. Hide in Plain Sight is selectable with its grand-secret gate and explicit
lighting/positioning restrictions, not an unconditional Stealth bonus.

Live Umbral level-12 save/reload (`build/pcgen-spheres-h6jshdrj`) retains Eyes of
Black and the Shadowstuff secret/bonus feat. Tests verify shared capacities,
scoped bonuses, partial refunds, source loss and restoration. Multiclass
Hedgewitch 5/Fey Adept 3 save/reload (`build/pcgen-spheres-5he5vdz3`) and the
Fey Adept regression (`build/pcgen-spheres-uyo2snhh`) also pass; the older
multiclass fixture predates retaining the Shadowstuff secret. Create reality,
illusion execution, and full compatibility with other shadow-pool classes remain
open. Improved Shadow Sculptor is removed before saving, so its repeat-selection
persistence still needs a retained fixture.

### Exorcism capacities and secrets

Exorcism now exposes sanction rounds, DC, radius, simultaneous-sanction limit and
the class-level-based push modifier. Creature-identification bonuses are scoped
to Knowledge situations, not all Knowledge rolls. Enduring Exorcism, Greater
Sanction and Moral High-Ground affect the corresponding capacities, with path
loss suppression and the level-10 grand-secret gates. Nemesis Sanction and
Rattling Sanction expose their separate range/damage/target quantities.
Irresistible Force affects only the sanction-push reference, not general CMB.
Subtle Sanction, Kinslayer, Threat of Force, Bloodlust, Remove Defenses and
Counterspelling Sanction have selectable rules records with appropriate gates;
their target-dependent actions are not automatically executed.

Live level-10 save/reload (`build/pcgen-spheres-biloqdba`) retains Enduring
Exorcism, Greater Sanction and Moral High-Ground; checks include grants, refunds,
path loss/restoration, conditional Knowledge bonuses and temporary selection of
Nemesis/Rattling. Level-1, level-9 and level-17 save checks also pass. Warding
Sanction, individual sanction-effect execution and conditional mastery defenses
remain open. The current offline suite has 55 class-catalog tests; full build
passes 655 scenarios and 21,147 engine regression checks.

Exorcism follow-up: Warding Sanction is now selectable with its Protection-sphere
prerequisite and a ward-only caster-level reference. It replaces only Hedgewitch's
mid-caster contribution, preserving other class contributions without changing
aegis or general Protection CL. Hedgewitch 10/Fey Adept 3 save/reload
(`build/pcgen-spheres-umoodou1`) checks qualification, Protection removal and
the scoped formula; level-2 save (`build/pcgen-spheres-98icmy8h`) passes too.
Warding Sanction is removed before saving and needs a dedicated retained fixture.
This supersedes the preceding statement that Warding Sanction is unimplemented.
Actual ward/sanction execution and conditional mastery defenses remain manual.

Green Magic follow-up: existing Bestial Bonds, Venom Immunity and Wild Vitality
grants now explicitly suppress their effects when their granting path is removed.
Level-12 general-profile save (`build/pcgen-spheres-u3uqkc2t`) verifies bonus-talent
and immunity suppression/restoration; companion construction remains unimplemented.
The full build passes after these changes.

The retained-fixture gaps above are now closed for Improved Shadow Sculptor
and Warding Sanction: Umbral level-12 save/reload
(`build/pcgen-spheres-7tvzmivk`) retains both sculptor selections and checks a
partial refund after reload. Exorcism Hedgewitch 10/Fey Adept 3 save/reload
(`build/pcgen-spheres-b8rxw0f3`) retains Protection and Warding Sanction and
checks the saved ward-only caster level before refunding/reselecting them.

### Charlatanism persistent benefits and secrets

Charlatanism now grants one upstream versatile-performance selection and exposes
guile capacity, conditional skill bonus, conditional sneak-attack dice and the
level-20 die-size improvement. These do not grant unconditional sneak attack or
an always-active skill bonus. Extra Guile is repeatable with partial refunds;
Evasion, Trapfinding and extra Versatile Performance are selectable secrets.
Path removal suppresses their implemented effects.

Exceptional Skill offers one non-Perform, non-synthetic skill, applies its bonus
to the ordinary skill and the corresponding upstream versatile-performance
substitutions, and refunds both. Level-10 save/reload
(`build/pcgen-spheres-bly7rik6`) retains the Bluff choice, Act performance and
two Extra Guile selections. Level-1, 9 and 20 capacity checks pass. The suite has
56 class-catalog tests; full build passes 655 scenarios and 21,147 engine checks.

Charlatanism is not complete: shared guile pools from other classes, Great
Performance/masterpieces, Trickery/advanced rogue talents and their effective
levels remain open. Guile expenditure and conditional attacks are table-resolved.
Other path resources, constructed entities and the broader backlog remain open.

### Font of Inspiration and Transmuter follow-up

Font of Inspiration grants Divination, its inspiration capacity and repeatable
Extra Inspiration. Studied-combat bonus/duration references start at level 5;
they do not apply unconditional attack or damage bonuses. Level-5 save/reload
(`build/pcgen-spheres-b8f9u4xp`) retains both Extra Inspiration selections;
level-1 and level-4 saves test the early boundary. Removal/refunds pass.
Investigator multiclass stacking, investigator/rogue choices, alternate
divinations and the mastery remain open. The snapshot contains conflicting
mastery wording: the path version increases casting ability **score** by 2,
whereas the older tradition version increases its **modifier** by 2. No mastery
bonus was silently selected between those versions.

Transmuter's Creation benefit now exposes a create-only caster level, replacing
only the Hedgewitch mid-caster contribution. Alter and general Creation CL stay
unchanged. Hedgewitch 6/Fey Adept 3 save/reload (`build/pcgen-spheres-ggxc5chc`)
retains Creation, verifies the scoped caster level, and checks suppression on
sphere/path removal. Actual creation/transmutation execution remains manual.
The current class-catalog suite has 57 passing tests.

### Temporal Traveler feat slots and zero-progression sphere selection

The repeatable Grit Feats secret now grants a separate Grit/Panache-filtered
feat pool. It requires Temporal Traveler and the normal secret level gate;
removing the path suppresses the granted slots. Level-6 save/reload
(`build/pcgen-spheres-jr1gh3se`) checks retained secret cost, repeated grants,
partial refunds and path removal/restoration. This does not import upstream
grit/panache feat supplements or implement insight equivalence for their
prerequisites. Selecting actual supplement feats remains unverified.

The resource harness exposed a shared selection bug: first-level mid/low
casters have zero base caster-level progression but must still be able to
spend their magic talents. Power base spheres now require Spheres Casting Core
rather than positive caster level, including the hand-maintained Destruction
record. Caster-level arithmetic was deliberately left unchanged: globally
flooring sphere CL before class-specific adjustments would double-count the
first-level contribution of paths/classes that replace their progression.
Level-1 Temporal Traveler/Transmuter save/reload
(`build/pcgen-spheres-8x81re3w`) now retains the selected Creation sphere and
checks create-only CL 1 while general progression remains 0. Minimum effective
CL in other individual sphere effects still needs a separate arithmetic audit.

The current offline suites pass 58 class-catalog and 19 catalog tests. The
remaining path abilities, insight prerequisite equivalence, constructed entities,
and the wider backlog are not complete.

### Covenant dice qualification and channel-feat secrets

Covenant now contributes an independent channel-dice prerequisite branch, gated
by both the retained Covenant path and an energy selection. Dice are not added
to other channel pools. The existing strict Nd6 policy rejects Covenant's d8
mastery for an Nd6 prerequisite rather than silently treating different dice as
equivalent. Level-7/8 and level-20 live tests passed; level-8 save/reload evidence:
`build/pcgen-spheres-23yuv_cm`.

Channel Feats is now a repeatable Covenant secret granting a separate feat slot.
Generated Spheres feats receive the selection type only when a mandatory
compiled channel prerequisite is present; the broad Channeling label alone is
not sufficient. Other prerequisites are still checked. Selection, slot spending,
repeat grants, partial refunds, and suppression on path removal pass live checks.
Upstream Core channel feats have not yet been added to this filtered category;
their effect/eligibility adapters remain a separate open task. Divine Portfolio,
Mercy and Greater Divinity remain incomplete; Smite activation remains manual. No channel action execution
or automatic resource spending is claimed.

Offline verification: 62 feat tests, 59 class-catalog tests, generated consistency,
package checks, and full build (655 scenarios; 21,147 engine checks) pass.

Channel Feats persistence now passes with a retained Channel Luck selection and
spent bonus-feat slot (`build/pcgen-spheres-nam3flsm`). The harness queries the
shared FEAT category for the granted feat, while checking expenditure against
the distinct granting category. Level-1 rejection also passes.

Covenant Smite is now a level-10 grand secret with repeatable daily-use capacity,
partial refunds and suppression on path loss. Level-9/10 live checks pass
(`build/pcgen-spheres-jt9ilj9z`, `build/pcgen-spheres-v4u3to6k`). It does not
apply target-dependent modifiers to every attack. Alignment detection, smite
target selection, execution and expenditure remain table-resolved.

### Path-loss suppression for bonus-feat secrets

The older Academia Metamagic Knowledge, Combat Combat Feat/Tactician and Umbral
Touch of Darkness secrets now suppress their granted slots when their granting
path is removed, matching the newer Temporal Traveler/Covenant behavior.
Tactician daily uses are also suppressed. Existing purchased feats are not
silently deleted: their now-unsupported slot is visible as overspending and must
be refunded explicitly. Live level-12 tests verify a spent Combat slot becomes
-1 on path removal and returns to zero when the path is restored, and that
Tactician slots/uses disappear. Evidence: `build/pcgen-spheres-cid30quy`.
The class-catalog suite now has 60 tests.

The same retained-path checks now guard Academia Extra Spell Points/Scholarship,
Combat Greater Aid, and Temporal Traveler Trapfinding bonuses. Resource secrets
whose source explicitly grants uses without the base power were not blanket-
changed. Scholarship and Greater Aid suppression/restoration pass live level-12
save/reload (`build/pcgen-spheres-1uakssd2`); offline tests check every affected
bonus tag. The final full build, package and generated-data checks pass.

Covenant's explicitly stated lay-on-hands/touch-of-corruption feat equivalence
is now parsed with polarity-specific choices and exact upstream feature keys
(the upstream shared LayOnHands type includes antipaladin corruption and is
therefore unsafe as a positive-healing check). Succor is no longer behind
manual prerequisite approval; unrelated unresolved alternatives still fail
closed. Live level-10 save/reload (`build/pcgen-spheres-nsdsfqtz`) verifies
positive eligibility, negative rejection and the independent War requirement.
Current counts: 63 feat tests, 60 class-catalog tests, 373 unresolved feat
prerequisites. The full build and deterministic generation checks pass.

Smite now also has explicit retained-selection save/reload evidence at level 10
(`build/pcgen-spheres-59jplyls`), alongside the retained bonus channel feat and
Extra Healing selections. Reload asserts the Smite use capacity and its refund.

### Tension prerequisites, Amateur Striker and extra class-option feats

Tension-pool prerequisites now recognize Striker or Amateur Striker, independently
of current tension or the level-20 unlimited pool's zero finite-capacity value.
Amateur Striker enforces Constitution 13 and excludes Striker levels. Unknown
alternative resource requirements still fail closed. Striker level-2 and level-20
checks pass, including metamagic prerequisite loss; level-20 save/reload evidence:
`build/pcgen-spheres-aazr2cvd`.

Amateur Striker now grants one of three generation methods, one of eleven base
tension techniques, and a Constitution-based capacity. Both choices persist,
consume their slots, require the feat, and become visibly overspent on feat loss.
Combat tension, technique execution, retraining and the optional feat exchange
on gaining Striker levels remain player-managed. The method/technique records
do not apply temporary bonuses permanently. Save/reload:
`build/pcgen-spheres-a26nj_b1`; BAB-five Extra Striker Art eligibility and its
slot/refund are additionally checked by `build/pcgen-spheres-vcoyaaxb`.

Extra Battlefield Specialization, Extra Prowess, Extra Scholar’s Knack, Extra
Smithing Insight, Extra Striker Art and Extra Technical Insight now grant actual
option slots, with source repeat caps at 5/11/17 or 7/15 rather than an unrestricted
text chooser. Counters are defined by the owning class (or Amateur Striker), so
partial removal cannot discard the remaining counter definition. Existing feat
keys are preserved. Saves from the old free-text implementation need their old
associations reviewed; no automatic saved-file migration is claimed.

All six classes pass live save/reload: Striker `build/pcgen-spheres-wqaf1a10`,
Scholar `build/pcgen-spheres-p6kt_l3i`, Commander `build/pcgen-spheres-thi_sl0m`,
Armiger `build/pcgen-spheres-gr_fxl99`, Blacksmith `build/pcgen-spheres-gg6et6vp`,
Technician `build/pcgen-spheres-00cieqhx`. Below-entry and before-next-repeat
checks also pass at Technician 4 and Scholar 14. The Amateur Striker equivalence
applies to selecting Extra Striker Art only; it does not waive individual arts'
class-level prerequisites. Expanded Tension Technique's target validation,
archetype-specific techniques and current combat resource tracking remain open.
Current accounting: 66 feat tests; 370 unresolved feat prerequisites and 99 feats
with recorded mechanics. Those counts are not claims of full feat completion.

Sentinel reserve prerequisites now recognize the existing Reserve Points feature,
not a positive current resource balance. Defender’s Bonds retains its independent
Beastmastery and character-level-three requirements, and Covenant equivalence
remains positive-only. Live Sentinel level-2/3 save/reload checks verify rejection,
qualification and loss of Beastmastery (`build/pcgen-spheres-6jg5xs0i` and
`build/pcgen-spheres-8_pg04gq`). Current accounting is 67 feat tests and 369
unresolved feat prerequisites. Amateur Striker BAB-five extra-art checks also
pass reload (`build/pcgen-spheres-vcoyaaxb`). The full build after the extra-option
changes passes 655 scenario checks and 21,147 engine regressions.

### Expanded tension choices and Customized Bond entry routes

Expanded Tension Technique now buys repeatable slots for the eleven base tension
techniques. Amateur Strikers cannot select their existing technique, nor can they
subsequently choose an expanded technique as their Amateur technique. Base
Strikers already know these techniques and cannot select them again. Archetype
techniques are not imported; no substitute or unrestricted text choice is used.
The feat's same-turn restriction and tension spending remain table-resolved.
Live retained-choice save/reload, partial feat refunds, slot overspending on feat
loss, and tension-source loss pass in `build/pcgen-spheres-6t0cdwdk`.

Customized Bond now requires both actual feature records (Armorist bound equipment
and Armiger customized weapons). The arsenal trick and prowess each enforce the
other class's feature and grant the feat automatically. Shifting Style retains
Transformation as an independent prerequisite. Mixed Armorist/Armiger save/reload
and both bonus-feat/refund routes pass in `build/pcgen-spheres-vviaplgw`;
single-class rejection passes in `build/pcgen-spheres-z7roai8p` and
`build/pcgen-spheres-0msk9yqt`. The feat's enhancement-level stacking and actual
bound/customized weapon construction remain unimplemented, not implicitly granted
by these prerequisite corrections.

After these changes: 69 feat tests, 60 class-catalog tests, 367 unresolved feat
prerequisites, and 100 feats with recorded mechanics. The full build passes
655 scenario checks and 21,147 engine regressions. Recorded mechanics are not a
claim that all effects of those feats are complete.

Armiger Spell Dabbler now grants a restricted feat pool containing Basic Magic
Training, Advanced Magic Training and Extra Magic Talent. It is repeatable up to
three times, preserves the selected feat's ordinary prerequisites, and grants
actual casting/talent benefits through the existing feat records. Live save/reload
retains all three feats, verifies the extra talent, and checks partial slot
refunds/overspending (`build/pcgen-spheres-sp0mtfoi`). Basic Magic Training's
later-class retraining lifecycle remains a separate open issue. Latest full build:
70 feat tests, 60 class-catalog tests, 655 scenario checks, 21,147 engine regressions.

Reviewed family prerequisites now resolve Creation material talents, War momentum
talents and Berserker adrenaline talents to explicit catalog members with the
corresponding heading descriptor. Sphere ownership remains independently required;
a talent merely mentioning momentum or adrenaline does not qualify. Unknown
families remain fail-closed. Seven more feats no longer need adjudication for
these requirements (360 unresolved remain). Power and Might save/reload checks
verify rejection without a sphere, rejection with an unrelated talent, valid
member eligibility and eligibility loss on removal:
`build/pcgen-spheres-yxk8x5oi`, `build/pcgen-spheres-ig68lx2v`.
Latest full build passes 71 feat tests, 60 class-catalog tests, 655 scenarios and
21,147 engine regressions. Feat effects have not been inferred from eligibility.

Descriptor-family qualification now also covers Destruction blast-type talents
and Nature spirit talents. Comma-separated heading descriptors are matched as
exact members: `(blast type, acid)` qualifies, `(blast shape)` does not, and
`(water, geomancing, spirit)` qualifies without treating every geomancing talent
as a spirit talent. Damage-type restrictions remain fail-closed. Live Power
save/reload verifies positive, negative and removal cases in
`build/pcgen-spheres-uhgvk5on`. The martial prerequisite in that fixture uses an
explicit temporary test capacity, not an extra feat purchased from an already
spent saved-character feat pool.

Gather Shadowstuff and Shadowblast now require the existing shadowmark feature
record rather than manual adjudication. Fey Adept positive save/reload and
non-Fey rejection pass in `build/pcgen-spheres-1vumyvra` and
`build/pcgen-spheres-shq8aw0y`. This does not implement those feats' combat effects.
Current unresolved feat-prerequisite count is 355; 73 feat tests and the full
build pass, including 655 scenarios and 21,147 engine regressions.

Cross-sphere strike and stance prerequisites now enumerate only catalog records
with the explicit `[strike]` or `(stance)` heading descriptor. This resolves six
additional feats without treating mentions in effect text as qualification or
inventing support for multiple-descriptor/count requirements. Live Power and
Might save/reload validate selection, removal and negative cases in
`build/pcgen-spheres-g7250ugs` and `build/pcgen-spheres-ayfoj7nh`.
Latest totals: 349 unresolved feat prerequisites, 74 feat tests; generated-data
checks and the full build pass (655 scenarios, 21,147 engine regressions).
Spell Attack execution, stance duration changes and the other feat effects are
not implemented by these prerequisite corrections.

Primal Blast now resolves its any-Nature-package prerequisite to the six actual
package selections, not the package capacity variable. Owning Nature with an
unspent package slot does not qualify. Selection and refund checks pass in live
Power save/reload (`build/pcgen-spheres-bgen23jz`). Primal Blast's conditional
attack/damage ability substitution is still not automated. Latest verification:
75 feat tests, 348 unresolved feat prerequisites, full build green (655 scenarios,
21,147 engine regressions), generated feat/trait/coverage checks and package
structure check green.

### Extra Bestial Trait and multiclass sphere mastery

Extra Bestial Trait now requires the actual level-2 Shifter feature marker and
grants a repeatable bestial-trait slot. Live level-1 rejection and level-2
save/reload cover repeated purchases, spending the granted slots, partial refunds,
and feat costs (`build/pcgen-spheres-artnd0e8`, `build/pcgen-spheres-cuiemocl`).
It does not bypass individual trait prerequisites.

Shifter Alteration and Eliciter Mind mastery previously subtracted the character's
entire caster level, canceling other casting classes. A new live regression
reproduced Alteration CL 5 instead of 9 on Shifter 5 / Eliciter 3 / Fey Adept 2
before the fix (`build/pcgen-spheres-uylxbfog`). Each mastery now replaces only
its own class's three-quarter contribution. Ordinary CL and unrelated sphere CL
are unchanged. Mixed-class save/reload passes at 5/3/2 and 1/1/1
(`build/pcgen-spheres-wta2kdbb`, `build/pcgen-spheres-x48f_jrr`); standalone
Eliciter 5 passes (`build/pcgen-spheres-23yqx91l`). This is not completion of the
broader multiclass, prestige advancement, temporary bonus, or effective-CL audit.

Verification: 76 feat tests, 61 class-catalog tests, generated-file checks,
package validation, and full build (655 scenarios, 21,147 engine regressions).
Current unresolved feat prerequisite count: 347. The broader backlog remains open.

The same cancellation bug also affected Elementalist Weave Energy. The new
four-class fixture reproduced Destruction CL 3 instead of 10 before correction
(`build/pcgen-spheres-9pwiqogu`). Weave Energy now replaces only Elementalist's
own mid-caster contribution. Shifter 5 / Eliciter 3 / Fey Adept 2 / Elementalist 3
passes save/reload with ordinary CL 9, Alteration CL 11, Mind CL 10 and
Destruction CL 10 (`build/pcgen-spheres-o31_ewzw`). Standalone Elementalist 1
also passes (`build/pcgen-spheres-c4_zsx9p`). Elementalist offline tests and the
full build pass after the correction. No saved-character keys changed.

### Inspiration feature prerequisites

Deduction, Rigorous Defense and Studied Scout now recognize Font of Inspiration's
actual feature availability. Inspiration requires the path; studied combat also
requires Hedgewitch level 5. The parser preserves the upstream Investigator
resource routes and Studied Scout's Slayer alternative, rather than treating
all Hedgewitches as owners of those features. Life, War and Scout remain
independent requirements. These changes implement eligibility, not the feats'
tactical effects or Investigator/Hedgewitch multiclass resource stacking.

Live Hedgewitch level-5 save/reload (`build/pcgen-spheres-xqjkt2sl`) and level-4
save (`build/pcgen-spheres-6fg9m2g4`) pass sphere rejection, the studied-combat
boundary, and path removal. Upstream Investigator/Slayer routes were inspected
against the vendored data but were not exercised in these live fixtures.
77 feat tests, generated coverage checks, package validation and the full build
pass (655 scenarios, 21,147 engine regressions). Unresolved feat prerequisites:
344. The broader backlog remains open.

### Scoped caster-level reference recursion

The six-class mastery fixture reproduced Transmuter's create-only reference
reducing Creation CL from 12 to 9 (`build/pcgen-spheres-mclkte87`). Moving its
derived total out of BONUS evaluation into a guarded DEFINE fixes that recursion.
Warding Sanction used the same unsafe structure and now uses the same separation:
selection supplies only an enable flag; the reference computes the scoped total.
Neither feature increases general Creation/Protection CL. Path or sphere removal
still disables the corresponding reference. Existing public variable names and
saved selection keys remain unchanged.

Shifter 5 / Eliciter 3 / Fey Adept 2 / Elementalist 2 / Wraith 3 / Hedgewitch 3
passes save/reload, including retained Despoiler, Transmuter, Exorcism and Warding
Sanction (`build/pcgen-spheres-zllezmor`). Ordinary CL remains 12, create-only and
ward-only CL are 13, and unrelated effects retain ordinary progression. The
level-1-each six-class fixture passed before the ward extension
(`build/pcgen-spheres-1u4x0kyo`). Existing resource save/reload passed
(`build/pcgen-spheres-le8q9toc`); Exorcism level-6 save passed
(`build/pcgen-spheres-5b9vaq28`). 61 class-catalog tests, generator consistency,
package checks and full build pass. This is scoped regression coverage, not a
claim that all multiclass or prestige combinations are complete.

### Surreal feat shadow pools and seven-class scoped progression

All catalog surreal feats now contribute one point to the shared shadow-point
capacity, including characters without Fey Adept or Umbral. This implements the
pinned Illusion page's Surreal Feats rule, not their individual tactical effects.
Shadow-pool prerequisites accept the class resource or another surreal feat;
a feat cannot supply its own prerequisite. Shadow Magic also accepts its
independent Illusion + Shadow Infusion entry route. Loss of that route revokes
qualification unless another pool source remains.

Live Fey Adept save/reload verifies Greater Shadowmark's point stacks with class
capacity and repeated Extra Shadowstuff (`build/pcgen-spheres-0tjsqo4g`).
Non-class save/reload retains Shadow Shield and verifies its standalone point
and removal (`build/pcgen-spheres-ihbulnyp`); the same harness checks both entry
routes, two distinct surreal feats, prerequisite loss and no self-qualification.
Umbral level-12 save passes (`build/pcgen-spheres-glxf6m9e`).

The seven-class fixture including Mageknight 3 passes save/reload after
regenerating the previously stale Mage Feint derived reference
(`build/pcgen-spheres-1y5tvvhi`). Full build passes: 79 feat tests, 61
class-catalog tests, 655 scenarios and 21,147 engine checks. Generator and
coverage consistency pass. Unresolved feat prerequisites: 342; 113 feats have
recorded mechanics, which is not a completeness measure. Surreal Strike's
shadowmark grant, individual surreal effects and the broader backlog remain open.

### Surreal Strike shadowmark source

Surreal Strike now grants the existing shadowmark dice, die-size and Will-penalty
records using character level minus four (minimum one). Existing Fey Adept and
Umbral sources use the strongest effective level, not summed dice. The feat
grants only its surreal shadow point, never a second class-sized shadow pool.
Greater Shadowmark qualification appears and disappears with the source.

Live Fey Adept and non-Fey save/reload checks pass
(`build/pcgen-spheres-5s6f66m5`, `build/pcgen-spheres-nk3vyr__`), including
add/remove, stronger-source preservation and capacity refunds. Non-Fey level-1
and level-20 saves pass (`build/pcgen-spheres-eswv_ch6`,
`build/pcgen-spheres-3yl8le59`). Those fixtures exercise Surreal Strike through
add/remove; retained Surreal Strike persistence still needs its own assertion.
Full build and generated consistency pass. Shadowmark attack execution and
other surreal feats' tactical effects remain table-resolved.

Retained Surreal Strike persistence is now verified at level 20
(`build/pcgen-spheres-uwgbvfs7`): saved dice, penalty, standalone pool and
source removal pass. This supersedes the retained-selection gap above.

Create reality now has a level-6 class-feature marker used by the prerequisite
compiler. Emulation Expert accepts Shadow Magic or that actual feature, while
Illusion and Manipulate Aura remain independently required. Level-5 and level-6
Fey Adept save/reload pass both alternatives and source-removal checks
(`build/pcgen-spheres-i0zesy6_`, `build/pcgen-spheres-cgm4pwe_`).
80 feat tests, the full build, and generated consistency pass; unresolved feat
prerequisites now number 340. This does not execute create-reality effects.

Shadow Shield now exposes temporary-HP dice, range and conditional damage
reduction magnitude. Improved Shadow Shield supplies the per-level flat HP and
all-damage-reduction marker only while Shadow Shield is present; no permanent
HP, AC or DR is granted. Shadowstuff Armament exposes simultaneous-object
capacity, not constructed inventory. Level-1 save and level-20 save/reload
checks pass (`build/pcgen-spheres-8fvs3cdy`, `build/pcgen-spheres-mauik_5j`).
81 feat tests and the full build pass. Activation, expenditure, temporary HP
tracking, target assignment and created equipment remain unresolved at the table.

### Wild Magic feat capacities and thresholds

All 14 catalogued WildMagic feats now contribute to a shared owned-feat count.
The generator exposes their count-dependent capacities and thresholds: Careful
Caster reduction, Blood Dampening burn/major-event eligibility, Inspired Surge
temporary-talent capacity, Manipulate Result uses, Overpower Resistance's
conditional check bonus, Risk Management rerolls, Shift Effect major-event
eligibility, Rhythmic Chaos chance increase, and Spectacular Surge event count.
Shift Cost records its level-10 boundary. These are available-effect values, not
automatic activation, permanent talents, global MSB bonuses or spell-point
discounts. Chaotic Counter adds its unconditional +1 only to the existing
counterspell-check bonus. Its unresolved dispel-magic alternative still requires
prerequisite adjudication; tests explicitly attest that prerequisite.

The spell-point-pool spelling now uses the existing spell-pool predicate, so
Manipulate Result and Shift Effect compile their pool-or-casting alternative.
84 feat tests pass. Live level-10 save/reload and level-9 save pass
(`build/pcgen-spheres-m4nhcb1t`, `build/pcgen-spheres-5xt_mblm`), including
retained six-feat counts, 4/5/6-feat thresholds, removals, slot refunds and no
global MSB increase. Activation, risk accumulation, event tables, ability burn,
temporary talent selection/expiration and daily expenditure remain unimplemented.

### Core class-feature prerequisite interoperability

Rage, favored enemy and ki-pool prerequisites now recognize upstream feature
records instead of requiring manual approval. They test actual abilities, not
class levels or remaining resource quantities. Roiling Anger adds one ki point
and three standard-rage rounds; its conditional in-combat extension remains
table-resolved. Enmity Ward and Rage Of The Grave still require their spheres
independently. Triage accepts its casting-or-ki alternative.

85 feat tests and the full build pass. Power feat save/reload
(`build/pcgen-spheres-1cq5f66w`) exercises source removal, independent sphere
requirements and Roiling Anger's capacity grants/refunds. These use temporary
fixtures granting the actual upstream abilities; they do not certify every
multiclass or archetype combination. The reload fixture now preserves its
previously saved Life sphere when testing bardic performance and supplies a
temporary test-only feat slot for the ki/rage test, avoiding interference with
saved selections. Current measured unresolved feat prerequisites: 324.

### Racial predicates and additional upstream feature gates

The exact Construct/Fey/Plant "type or subtype" predicate now runs before
generic OR splitting. Previously the dedicated code was unreachable. Live
tests exercise both alternatives, unrelated human rejection, and source removal.
Construct/Plant subtype-only predicates remain distinct from racial types;
native outsiders require both Outsider type and Native subtype. Ancestor/patron
alignment still requires review. Greater Created also retains explicit review
for its character-creation-only restriction: level 1 alone does not establish
acquisition timing. Its creation-point benefit remains unautomated.

Favored Terrain and Improved Evasion prerequisites now recognize the upstream
abilities. Live checks reject ordinary Evasion and revoke qualification on
feature removal. Localized Arcana's terrain-conditional benefits and Superior
Rebuff's ally effects remain table-resolved.

88 feat tests, generated-file checks, and the full build pass (655 scenario
checks and 21,147 engine checks). Power save/reload evidence:
`build/pcgen-spheres-rpyttqvo`. Racial/feature fixtures test upstream records;
they do not certify every race or multiclass combination. Current measured
unresolved feat prerequisites: 315. This is not completion of the broader backlog.

Channel Resistance now grants the character's upstream defensive ability and
adds two to its channel-resistance value. Live Power save/reload
(`build/pcgen-spheres-yqzgv2d5`) verifies stacking with an independent source and
refunds. The feat's benefit for reanimated undead still needs companion/entity
propagation; it is not claimed as implemented. 89 feat tests, the full build,
generated-file checks and package checks pass. 132 feats now have recorded
mechanics; that count does not mean all effects of those feats are complete.

### Permanent defenses and Necrosis scaling

Resistant Veins now grants MSB-scaled natural armor, using the highest ordinary
natural-armor source rather than stacking indiscriminately. Live Power checks
verify Anemic qualification, removal, and both weaker/stronger independent armor
(`build/pcgen-spheres-hefmxyra`, save/reload).

All eleven catalog Necrosis feats now contribute to an explicit count. Cold Heart
grants its stated spell point and permanent cold/electricity resistance only at
four feats. Optional resistance/duration values do not activate the effect.
Banshee’s Sotto Voce, Between Two Worlds, Deathknight’s Purchase, Hemomancy, and
Wandering Spirit now grant their explicitly stated spell point. Selected resource
values expose conditional durations, temporary-HP dice, bleeding-only sense range,
and phylactery durability without granting unconditional vision or constructing
a phylactery. Necrotic Heart receives no blanket spell-point grant.

Dedicated live save/reload (`build/pcgen-spheres-nq64j8s7`) retains four feats,
tests the three/four threshold, refunds, spell points, and non-stacking energy
resistance. Additional five-feat tests run after both loads but do not retain
those additional five choices. 91 feat tests, generated checks, package checks,
and the full build pass (655 scenarios and 21,147 engine regression checks).

Remaining Necrosis work (cross-family counting completed below): Necrotic Heart's
conditional Fortitude interaction,
activation/spending, energy reversal, and entity propagation. The older appended
Magical Infusion text is not applied as an extra universal spell-point grant.
141 feats have recorded mechanics, including count-only entries; this is not
141 fully implemented feats, nor completion of the broader backlog.

Deadened Flesh now grants its permanent half-strength natural armor and DR/- at
four Necrosis feats. The live harness checks threshold loss and retained-selection
save/reload (`build/pcgen-spheres-odenn0gw`). The DR formula uses multiplication
by 0.5 because slash is the PCGen DR-token delimiter, not safe inside that
formula. Optional full-strength activation is still manual. The full build and
91 feat tests pass after this addition.

Scholar Of Past And Future now grants its History bonus with the ten-rank
threshold. Its divine-only caster-level bonus is exposed separately, rounded
up and capped at remaining HD headroom; ordinary Divination CL is unchanged.
Power save/reload checks (`build/pcgen-spheres-c2fd9kat`) cover 1/9/10 ranks,
missing ranks, refunds, full-CL zero headroom, and a reduced-CL fixture. This
does not certify an actual multiclass build or automate divine execution.
92 feat tests and the full build pass; 142 feats now have recorded mechanics.

Inhuman Defiler cross-family counting is now verified with retained selections
across save/reload (`build/pcgen-spheres-vbczz9jb`). Each distinct feat contributes
once to the union, including Inhuman Defiler itself. Tests cover the three/four
feat spell-point threshold, odd-count rounding, reciprocal counts, removal of
the bridge feat, explicit spell-point refunds, and restoration. The prerequisite
drawback is persisted in the fixture rather than supplied by an unsaved template.

Terrain Defiler had two current anchored source entries: the earlier drawback-only
entry suppressed the reviewed Cataclysm revision. The generator now explicitly
uses that revision's Defiler/Drawback types and four-feat benefit while retaining
its original key and source references. This is a narrow reviewed override, not
a blanket last-entry-wins rule. Live checks cover its union contribution/refund.
94 feat tests, generated consistency checks, package checks and the full build
pass (655 scenarios; 21,147 engine regression checks). 154 feats have recorded
mechanics, including count-only records; this is not a completion count.

### Cure-only and ward-only skill feats

Studied Healing now modifies a separate cure caster level, using rounded-up
half Heal ranks capped at total Hit Dice. Deeper Healing and Restore Health
consume that value; ordinary Life CL and invigorate remain unchanged. Existing
CL above HD is not reduced. Live level-10 save/reload and level-2 save pass
(`build/pcgen-spheres-2ugjyhj3`, `build/pcgen-spheres-4wrpjm19`), including
rank changes, zero-rank rejection, odd/even rounding, removal and persisted feat.

Graphomancy and Wardlord now contribute to a shared ward-only CL reference.
Their rank bonuses share the HD ceiling; Warding Sanction contributes its
class-specific progression separately. General Protection/aegis CL is unchanged.
Live retained-feat save/reload passes (`build/pcgen-spheres-9oiuxv1m`). Tests
cover independent prerequisites, rank changes, combined bonuses and refunds.
Wardlord's activated shout/tactic delivery remains table-resolved. These are
reference calculations, not execution of healing or ward actions.

Surgeon’s Trade Secrets now exposes its blood-control-only Heal bonus, with
+3/+6 at the ten-rank boundary. Live checks confirm general Heal is unchanged
and removal refunds the situational bonus. Skill Focus equivalence and the
activated blood art remain unimplemented. The Life harness passes save/reload
with Studied Healing retained (`build/pcgen-spheres-aijqitk_`); Surgeon is tested
through add/remove, not claimed as a retained selection. Shared Warding Sanction
CL passes the Exorcism harness (`build/pcgen-spheres-uasro47a`).
95 feat tests, 21 catalog tests, 61 class-catalog tests, deterministic generators,
package validation, and the full build pass (655 scenarios; 21,147 engine checks).
The overall backlog remains open; recorded-mechanics counts are not completion
counts.

Reviewed non-choice feat equivalences now work for Liberating Triumph (Great
Fortitude, Lightning Reflexes, Iron Will) and Combatant Caster (Combat Casting).
Live save/reload (`build/pcgen-spheres-hsl825ec`) verifies qualification and
removal without granting the imitated save bonuses. Combatant Caster's activated
weapon/concentration conditions are not automated. Liberating Triumph is the
retained selection; Combatant Caster uses a test-only drawback and add/remove
checks. Skill Focus (Heal) equivalence was tested separately and rejected:
SERVESAS loaded but did not satisfy the skill-specific prerequisite. No ineffective
mapping was retained. 96 feat tests and the full build pass; generators and
package checks remain clean. 160 feat records contain some mechanics, not 160
fully completed feats.

### Skill-effect persistence follow-up

Life and Ward harnesses used an incorrect Incanter class key when assigning
skill ranks. PCGen accepted the transient ranks but omitted their null class
owner when saving. Both now use the loaded prototype class and assert its
existence. Life save/reload explicitly retains Heal ranks and Surgeon’s Trade
Secrets’ situational bonus (`build/pcgen-spheres-_6yxyys4`); Ward save/reload
retains five Craft ranks and verifies Graphomancy still qualifies
(`build/pcgen-spheres-kqfcx4l9`). Earlier retained-feat tests alone did not prove
rank persistence. This was a test-fixture defect, not evidence of player skill
purchases being lost.

Vigilant Skeptic now exposes its rank-based figment interaction radius and
level-based Perception/Sense Motive bonuses only for targets benefiting from
glamers. Analyze Caster adds its Detect Spellcaster-specific Spellcraft bonus,
not a general skill bonus. Live retained-feat/rank save/reload passes
(`build/pcgen-spheres-uaruaahq`), including refunds and independent sphere/talent
requirements. Level-eight rejection and level-nine acceptance of Analyze Caster
are tested. Actual detection, action costs, target information and interaction
execution remain table-resolved. Surgeon’s Skill Focus equivalence remains open.
98 feat tests and generated-data/package checks pass; 162 feat records now
contain some mechanics, not complete automation. The broader backlog is open.

### Surgeon equivalence and Telekinesis formulas

Surgeon's Skill Focus (Heal) equivalence is now expanded by the Spheres
prerequisite compiler only. A global SERVESAS mapping activated upstream general
Heal bonuses and was rejected. Live Life save/reload verifies the skill-specific
alternative, loss on removal, retained Heal ranks, and unchanged general Heal.
Upstream non-Spheres prerequisites are not rewritten by this solution.

Telekinesis now exposes its movement speed, lift-size index, range, skill-use
penalties, tool bonus, maneuver CMB/CMD, and crush dice. Skillful Force changes
only the appropriate telekinetic skill-use references. Divided Mind, Dampening
Field, Dancing Weapon, Gravity Ward/Well and Telekinetic Push expose scoped
target counts, defenses, damage and movement values without modifying the
caster's ordinary skills, armor, weapon damage or movement.

Lift-size index uses Fine=0, Diminutive=1, through Colossal=8 and successive
Colossal categories above that. Powerful Telekinesis adds one category; the
lightweight/weightless target adjustments remain target-specific and manual.
Increased Range progresses close/medium/long and never invents a fourth range
band. Live boundary tests cover CL 1–60, repeated range refunds and Powerful
Telekinesis removal. This does not implement target selection, attack resolution,
concentration, spell-point spending or temporary target effects.

Fresh retained-selection save/reload passes at
`build/pcgen-spheres-yem5arhu`, including repeated Increased Range, Powerful
Telekinesis, Greater Speed, Skillful Force, Surgeon and persisted Heal ranks.
The earlier low-level/negative-modifier fixture also passes
(`build/pcgen-spheres-6qoyq3ci`). The full build passes with 24 catalog tests,
98 feat tests, 61 class-catalog tests, 655 scenario checks and 21,147 engine
checks. Generated-file and package checks pass. These are verified formula and
selection improvements, not completion of Telekinesis or the broader backlog.

Forceful Telekinesis now contributes its +2 only to telekinetic maneuver and
defense references, including Steal and Gravity Ward/Well. Its bludgeon-size
increase is separate from lift capacity and ordinary weapon size. Live add/remove
checks pass within the fresh save/reload at `build/pcgen-spheres-i8jwkwek`;
ordinary CMB remains unchanged. Target weapon construction remains open.

Kinetic Field now provides radius, friction damage, displacement, and second-pick
wall/cube dimensions. Quick Reactions' catch-field duration requires Kinetic
Field. Repeated selections do not double the first-pick effects, and partial
refunds preserve the first selection while removing alternate shapes. Live
checks pass in `build/pcgen-spheres-44gjgnq6` (save and reload); these particular
talents are exercised through add/remove, not retained across saves. The full
build passes with 25 catalog tests. Field activation and target application
remain manual; no permanent movement penalty or damage is applied to the caster.

The expanded retained-selection fixture now also saves both Kinetic Field picks
and Quick Reactions. Save/reload passes in `build/pcgen-spheres-wkoo36nx`, with
explicit saved-count, alternate-shape, duration and partial-refund assertions.

Fresh persistence verification also passes in `build/pcgen-spheres-ihcippp7`.
Gravity Shift now exposes its area radius; Homing exposes its pursuit duration;
Pantomime Cage exposes duration and escape DC. These are scoped effect references,
not permanent movement or combat bonuses. Their selection/removal checks pass
within the save/reload harness at `build/pcgen-spheres-m7zqxfzg`; these three
selections are not retained in the saved fixture. Catalog regression tests pass
(27 tests), as do generated coverage and package checks. Target application,
concentration, attacks, and escape resolution remain table-resolved.

Enhancement now exposes its equipment bonus (capped at +5, or +6 with Greater
Enhance Equipment), ordinary duration, equipment-specific duration, Deep
Enhancement's lingering rounds, and Mass Enhancement's additional targets.
Deep Enhancement and Greater Enhance Equipment combine to give equipment
60 minutes per caster level without extending unrelated enhancements that far.
Selection/removal checks pass in both phases of `build/pcgen-spheres-405yx99e`;
Enhancement selections are exercised but not retained. No equipped item or
character receives an unconditional enhancement bonus. Catalog tests pass
(28 tests). Actual target/item selection and temporary effect application remain
open; these reference calculations do not complete the sphere.

Enhancement retained-selection save/reload now passes at
`build/pcgen-spheres-r8r8r8c1`: sphere, Deep Enhancement, and Greater Enhance
Equipment are persisted and their ordinary/equipment durations verified on
reload. Live caster-level boundary checks at 1, 3, 4, 7, 8, 11, 12, 15, 16,
20, and 25 verify both equipment caps and refunds. The full build passes with
28 catalog tests, 98 feat tests, 61 class-catalog tests, 655 scenario checks,
and 21,147 engine checks. Target application remains open.

Enhancement target-effect references now also cover Alter Movement, Bestow
Intelligence, Cripple, Deadly Weapon, Emphasize Belief, Mental Enhancement,
Physical Enhancement, and Ragged Edges. Live checks exercise caster-level
boundaries through 25, including rounding, minimums, and removal; none grants
unconditional stats, movement, damage reduction, or weapon bonuses to the caster.
Bestow Intelligence's reference is the bestowed score floor, not a replacement
for a higher existing target score. Alignment DR still requires a suitable
target alignment and temporary application.

Save/reload passes at `build/pcgen-spheres-y113rgcd`. The eight new talents are
tested through selection/removal in both phases, not retained in the save.
The Enhancement boundary matrix uses a temporary test-only talent budget because
the reload fixture retains other spheres; that budget is removed and bonuses
recalculated before ordinary pool-refund tests. The full build passes with 30
catalog tests, 98 feat tests, 61 class-catalog tests, 655 scenario checks and
21,147 engine checks. These are scoped calculations, not completion of target
selection, effect activation, duration tracking, or the overall backlog.

The next Enhancement pass adds scoped Energize Body carrying/endurance values,
Energy Enhancement's weapon/item damage references, Harden/Weaken's hardness/DR
changes, Supply Vigor's ignored/reduced ability damage, and Traveling Weapon's
cover reduction. Ranged Enhancement now computes close/medium/long range from
its existing repeated-selection counter. Live caster-level boundary tests and
partial range refunds pass in both phases of `build/pcgen-spheres-69sqdytv`.
These choices are exercised rather than retained; caster attributes and equipment
remain unchanged until an actual target effect is modeled. Catalog tests and
generated coverage/package checks pass. Coverage lists 56 generated basic talents
with recorded mechanics, which is not a count of mechanically complete talents.

Ranged Enhancement's two selections now persist in
`build/pcgen-spheres-k1exi9da`, with explicit saved counter, long-range and
partial-refund assertions. The test-only two-slot allowance is removed before
saving, deliberately leaving an overspent test fixture; this proves persistence
of the selections, not validity of that fixture's overall talent budget.
Additional live assertions cover secondary damage/endurance/DR references.

Ravenous Weapon now exposes its miss-triggered damage dice; Spectral Enhancement
exposes its empowered armor's negative-energy resistance and scoped saving-throw
bonus. Animate Object exposes the total controlled-HD budget and the published
maximum-size, individual-HD, and construction-point table through caster level
42. Its size index uses Fine=0, Tiny=2, Colossal=8; larger objects continue the
index rather than resizing the caster. These are reference calculations, not
constructed companions or activated equipment effects.

Live selection/removal and boundary checks pass in both phases of
`build/pcgen-spheres-kzifvhas`. Every animated-object table threshold is checked
at the threshold and immediately below it. These three new talents are exercised
in both phases but are not retained in the saved fixture. Ranged Enhancement's
retained two-pick and partial-refund tests still pass. Catalog tests pass (31).
Generated coverage now records 59 basic talents with some mechanics; this does
not mean 59 mechanically complete talents. Object construction qualities/flaws,
GM decisions, controlled-object inventory, target application, and expenditure
remain open.

Enhance Potency's optional replacement save DC, Disable Device DC, and DC
reduction now have scoped references. Boundary and removal checks pass in both
phases of `build/pcgen-spheres-8d_mh114`; the selection is exercised, not retained.
The replacement DC must still be compared against the target item's existing DC;
it is not an unconditional override. Generated coverage records 60 basic talents
with some mechanics. This does not complete item targeting or temporary effects.

Lighten now exposes separate half-weight, weightless, and floating size limits
from its own published table, plus the 20-foot vertical movement rate. Limits
are capped at Colossal, the final published size, rather than extrapolated from
Animate Object. Improved Flexibility exposes its level 6/12/18 squeezing
thresholds. These are target-effect references, not permanent caster changes.
Live checks cover every caster level from 1 through 43, removal, and retained
Lighten save/reload in `build/pcgen-spheres-j9qjgq6w`.

Animate Object now exposes the size-based bonus HP for the largest permitted
object. Durable Objects modifies that reference by one size step below Colossal
and by 30 HP at Colossal and above, without increasing HD. Complex Animations
adds one construction point. Tests cover both feats' prerequisites, every
animated-object table threshold and the level below it, and removal. Both live
phases pass in `build/pcgen-spheres-4_xki010`; these feats are exercised in each
phase but are not retained in the saved fixture. An explicit zero-defined flag
with a bonus is used for Durable Objects after live tests exposed unreliable
results from a dependent conditional bonus.

The full build passes (32 catalog tests, 99 feat tests, 655 scenario checks,
21,147 engine regression checks). Coverage records 62 basic talents and 164
feats with some mechanics, not completed implementations. Choosing actual
objects, their size-specific stats, GM-assigned construction qualities/flaws,
target application, and spell-point expenditure remain open. Animated Arsenal
and Enchanted Animation still require the object-construction/casting lifecycle;
no unrestricted caster bonus has been substituted for those effects.

Retained Animate Object, Complex Animations, and Durable Objects subsequently
pass save/reload and post-reload bonus removal in
`build/pcgen-spheres-s5u6_rgt`. This supersedes the non-retention limitation of
the earlier animation-feat test run, not the missing object-builder lifecycle.

Exceptional Ally now accepts the reviewed `(enhance)` talent family while still
requiring both Conjuration and Enhancement. Base Enhancement and utility talents
are not counted as purchased `(enhance)` talents. Unsupported counts remain
fail-closed. Offline tests pass (100 feat tests); live positive and missing-sphere
checks pass in both phases of `build/pcgen-spheres-ymo_3m1w`. Unresolved feat
prerequisites decrease from 315 to 314. The feat's companion application remains
part of the outstanding companion/target-effect work.

Expanded Exceptional Ally live checks additionally reject the two base spheres
alone and Deep Enhancement, accept Lighten and Animate Object independently,
and revoke qualification when the last qualifying talent is removed. Both phases
pass in `build/pcgen-spheres-h372zz8_`. The final full build also passes with
100 feat tests and the unchanged 655 scenario/21,147 engine checks.

Careful Magic now exposes the casting-modifier bonus (minimum +1) specifically
for countering/dispelling the caster's effects, not as general magic defense.
Live checks exercise modifiers -4/0/1/5, missing Extended Casting, prerequisite
loss, selection, and removal in both phases of `build/pcgen-spheres-rj1752lj`.
The feat is exercised rather than retained. Its additional-spell-point reroll
effect still requires the temporary-effect/counterspell lifecycle. Feat tests
pass (101); coverage now records 165 feats with some mechanics, with 314
unresolved prerequisite records unchanged.

Solid Illusions' reviewed two-selection Illusionary Touch requirement now uses
the existing removal-safe repeat counter. Base-sphere-only and one-selection
characters are rejected; two selections qualify, and a partial refund revokes
qualification. Unsupported repeat counts remain fail-closed. Both phases pass
in `build/pcgen-spheres-py4hjtlo`; feat tests pass (102). Regeneration reports
311 unresolved feat records. This does not implement enhancing illusion targets.

Mutagenic Enhancements now recognizes the base sphere's Enhance Equipment as an
`(enhance) ability`, without confusing that wording with Exceptional Ally's
purchased-talent requirement. Alteration is still independently required.
Positive and prerequisite-loss tests pass in both phases of
`build/pcgen-spheres-rlf_xfz_`; 103 feat tests pass. Unknown ability wording stays
fail-closed. Coverage reports 310 unresolved feats; Might Of The Grave remains
blocked by its separate reanimate-ability requirement. Applying polymorph traits
to enhanced targets remains unimplemented.

Object Familiar's acquisition prerequisite now uses PCGen's existing
`FamiliarMasterLVL` advancement variable, shared by Core familiar selection and
the implemented Shifter/Hedgewitch familiar grants. It still independently
requires Animate Object. Both phases of `build/pcgen-spheres-ot83fb0f` pass
zero/one advancement, missing Animate Object, and advancement-removal checks
using a controlled template fixture, not an actual familiar character. The
constructed-object familiar remains unimplemented. Feat tests pass (104);
unresolved feat records decrease to 309.

### Received Protection energy resistance

The native temporary-effect list now includes acid, cold, electricity, fire,
and sonic Energy Resistance aegises. Each uses the caster level entered when
cast (10 + CL), affects only its chosen energy, and takes the highest resistance
instead of adding independent sources. These are recipient effects, not bonuses
granted by owning the talent. The area ward, secondary attack effects, casting
costs and expiration remain player-managed.

`build/pcgen-spheres-ek76dlmr` passes save/reload, levels 1/5/12/20, weaker and
stronger overlapping resistance, independent energy checks, removal, and retained
CL12 fire resistance. All 50 catalog tests and generated-file checks pass.

### Received Alter Movement increases

Added temporary enhancement bonuses to existing Walk, Climb, Swim, Fly, and
Burrow speeds. A separate explicitly conditional skill toggle applies only while
using the enhanced speed; no unconditional skill bonus or new movement mode is
granted. The decreasing-speed option remains open.

`build/pcgen-spheres-vjqw982h` passes both phases, walking-speed boundaries
1/4/5/9/10/20, removal, rejecting creation of flight, conditional skill disabling,
and retained CL10 walking-speed removal after reload. Other existing movement
modes still need individual live fixtures. Full build passes with 51 catalog,
104 feat, 655 scenario and 21,147 engine regression checks after regenerating
the temporary-effect coverage inventory.

Follow-up `build/pcgen-spheres-_3nprmgf` closes the individual movement-mode
fixture gap: Climb/Swim/Fly/Burrow each pass weaker/stronger enhancement stacking,
preservation of the original speed bonus, and removal in both phases. Those
fixtures are exercised rather than retained; walking remains the persisted case.

Lighten now has explicit recipient CMD context toggles for half weight (-2) and
weightless/floating (-4), only against bull rush, drag, or reposition. These do
not modify ordinary CMD, AC, CMB, body weight, armor, or movement automatically;
the user enables the selected state only for the relevant maneuver. Both phases
of `build/pcgen-spheres-h95hy02o` exercise both penalties, disabling, removal,
and AC/CMB isolation. These conditional toggles are not retained in that fixture.
Full build passes with 52 catalog tests, 104 feat tests, 655 scenarios and 21,147
engine checks; generated catalog and coverage are current.

Lighten's levitating weapon-attack penalty now has a bounded 1–5 temporary
modifier. The player advances/replaces it after attacks and resets it after the
full-round stabilization action; it is disabled for nonweapon attacks. Both
phases of `build/pcgen-spheres-tio420x7` pass the 1/2/3/4/5/1 sequence, disabling,
removal, and damage isolation. These transitions are exercised, not persisted.
All 53 catalog tests pass; generated files and coverage are current.

Spell Ward recipient SR remains blocked: `PlayerCharacter.calcSR` adds
`MISC|SR` bonuses to racial/equipment SR rather than taking the greater value.
An ordinary temporary SR bonus would therefore implement incorrect stacking.
Use a native SR-source representation with lifecycle tests before enabling it;
do not substitute additive SR or a general magic-defense bonus.

### Received Fate base effects

Added native temporary recipient modifiers for Serendipity (luck bonuses to
attacks, saves, skills and initiative) and Hallow (sacred/profane attack, AC and
save bonuses against the opposed alignment only). Aura membership, alignment
eligibility, other ability checks, mental-control suppression, concentration,
costs and duration remain player-managed. Hallow is explicitly a context toggle,
not unconditional defense or immunity.

`build/pcgen-spheres-d3vndx8p` passes both phases: Serendipity application,
highest-luck stacking and removal; both Hallow types at CL1/9/10/19/20 and
disabling outside context. These effects are exercised, not retained in the
saved fixture. All 54 catalog tests and package/generated-file checks pass.

### Received Fate penalties and persisted mixed effects

Greater Serendipity now supplies a recipient enemy penalty equal to the actual
allied bonus entered by the player (not caster level). Borrow Luck supplies four
separate roll-category penalties applied after the reroll. Ability checks affect
initiative in PCGen; other ability checks remain table-resolved. Neither effect
changes ability scores, damage, or AC. Aura membership, curse immunity, rerolls,
costs, and qualifying subsequent failures are still player-managed.

Both phases of `build/pcgen-spheres-d6qbtkry` pass roll-category isolation,
Greater Serendipity penalties 1/3/5, toggling, removal, and a saved Borrow Luck
attack penalty alongside Serendipity and Cripple. Corrected the stale pre-save
test expectation: Serendipity +1 and Cripple -4 total -3, not -4. All 55 catalog
tests and generated-file checks pass.

Energize Body carrying capacity remains blocked: the engine's `LOADMULT|TYPE=SIZE`
adds to its size multiplier rather than multiplying final capacity. Using that
bonus directly would produce incorrect results across sizes and other load
adjustments. No inaccurate carrying-capacity bonus was introduced.

The Star and The Chariot motifs now have explicitly conditional recipient
modifiers: insight AC against attacks of opportunity, and insight saves against
effects preventing actions or causing staggered, respectively. Discharge and
condition suppression remain table-resolved. `build/pcgen-spheres-uxo9ozdu`
passes both phases, including CL1/4/5/9/10/19/20, highest-insight stacking,
disabling outside context, and removal. Motif effects are exercised rather than
retained in the saved fixture. Full build passes with 56 catalog tests, 104 feat
tests, 655 scenarios and 21,147 engine checks; coverage regenerated.

Strength motif now applies insight bonuses to CMB, CMD, and Strength-based skills
through native `SKILL|STAT.STR`, without changing Strength or ordinary attacks.
Both phases of `build/pcgen-spheres-86f_oi22` pass CL1/3/4/7/8/20 and removal,
including actual Climb/Swim modifiers. It is exercised, not retained across the
save. Strength checks and fear discharge remain table-resolved. All 57 catalog
tests and package checks pass; generated coverage updated.

The Hanged Man now provides three recipient choices, each improving two saves
and penalizing the third by a fixed -2. Only the insight bonus scales. The player
must remove the previous choice before switching, or disable it to choose neither;
the temporary-bonus UI does not enforce that mutual exclusion. Both phases of
`build/pcgen-spheres-zlnr15ve` exercise all three choices at CL1/9/10/19/20 and
disable/remove transitions. These choices are not retained in the saved fixture.
Discharge remains table-resolved. All 58 catalog tests and generation checks pass.

The Moon and The Hierophant now provide conditional mind-affecting save bonuses,
with their distinct CL/10 and CL/5 scaling. Hierophant's description explicitly
limits receipt to allies within 30 feet other than its bearer. Aura membership
and mind-affecting context are player-managed; neither record grants immunity or
executes a discharge. Both phases of `build/pcgen-spheres-2wjlnnlx` pass the
scaling, insight stacking and disable/remove matrix. Full build passes with
59 catalog tests, 104 feat tests, 655 scenarios and 21,147 engine checks.

Pain now supplies its received -4 mental-skill penalty through Intelligence,
Wisdom and Charisma skill selectors. Both phases of
`build/pcgen-spheres-vymkil59` verify Spellcraft, Sense Motive and Bluff penalties,
unchanged Climb/Acrobatics, no ability-score or save penalty, and removal.
Damage, ongoing damage and the casting magic-skill check remain table-resolved.
The effect is exercised rather than persisted. All 60 catalog tests and
generated-file checks pass; coverage regenerated.

Justice's triggered attack/damage bonus and The Devil's discharged attack/AC
bonus now have target-conditional recipient toggles. Target identity, damage
trigger, assessment, expiry and discharge remain player-managed. Both phases of
`build/pcgen-spheres-w1o5ejxg` exercise CL1/3/4/5/9/10/20, disabling for another
target, and removal; these toggles are not retained across saves. Full build
passes with 61 catalog tests, 104 feat tests, 655 scenarios and 21,147 engine
checks. No general always-on attack or defense bonus is granted by owning them.

Persistence follow-up `build/pcgen-spheres-mw9g32gh` passes both phases with
Strength CL8, Pain and Hanged Man CL20 retained alongside the existing received
effects. Reload checks prove their maneuver, actual skill, insight-save and
fixed-penalty contributions are removed independently without discarding other
modifiers. This supersedes the earlier exercised-only limitation for those
three effects; target-conditional motifs still have no automatic target state.

The World now supplies its insight skill bonus as an explicitly conditional
recipient effect for taking 10/20 or resolving its discharge. Both phases of
`build/pcgen-spheres-fcvlk9r2` pass CL1/4/5/9/10/19/20, actual Spellcraft
modifiers, highest-insight stacking, disabling for ordinary rolled checks, and
removal. The effect is exercised rather than retained in the saved fixture.
Discharge eligibility and its effective-rank substitution remain table-resolved;
no permanent ranks or permission to take 10/20 are granted. All 62 catalog tests
and package checks pass. The combat-motif regression now selects records by key
rather than relying on their position at the end of the generated file.

The Magician now has separate conditional recipient modifiers for attacks of
opportunity and untrained skill checks. Both phases of
`build/pcgen-spheres-n5rsl9ik` pass CL1/4/5/9/10/19/20, roll-category isolation,
highest-insight stacking, disabling and removal. These effects are exercised,
not retained across saves. Neither permits trained-only skills, grants ranks or
Combat Reflexes, or executes surprise-round actions. Full build passes with
63 catalog tests, 104 feat tests, 655 scenarios and 21,147 engine checks.

Persistence follow-up `build/pcgen-spheres-1kmdrwkt` passes both phases with
The World CL20 active and The Magician CL10 attack modifier inactive at save.
Reload verifies actual skill-bonus removal, preservation of the inactive state,
reactivation, and removal without losing the independently persisted penalties.
This supersedes the exercised-only limitation for The World and The Magician's
attack modifier; its untrained-skill modifier is still exercised only.

The High Priestess discharge now supplies the one-round, half-caster-level
insight save bonus to eligible allies as a received effect. Both phases of
`build/pcgen-spheres-zz0_4nqv` pass CL5/6/9/10/19/20, highest-insight stacking,
save-only scope, disabling and removal. Its effect is exercised, not persisted.
The initial test incorrectly assumed the recipient had no base AC; corrected it
to check unchanged baseline AC. Motif linking, sharing, range, eligibility and
discharge timing remain player-managed. All 64 catalog tests pass and generated
files, coverage and package checks are current.

Aligned Attacks now enforces a non-neutral alignment axis by excluding true
neutral, rather than excluding every alignment containing a neutral component.
Its caster-level prerequisite remains intact. Both phases of
`build/pcgen-spheres-3zummh9h` verify all nine alignments; 104 feat tests pass.
This corrects qualification only: choosing the attack alignment and applying it
to natural-weapon damage reduction remain unimplemented. Current regeneration
reports 307 unresolved feat records; this is not mechanical completion.

The Hermit's self-aid bonus now has separate received attack, defense and skill
modifiers. These replace ordinary aid, with explicit restrictions against aid
from another creature in the same round. Both phases of
`build/pcgen-spheres-3zsika_d` exercise CL1/4/5/9/10/19/20, disable/reactivate,
removal, and exclusion of damage and saves. The effects are not retained in that
saved fixture. Aid checks, swift actions, target/context enforcement and
discharge flanking remain player-managed. All 65 catalog tests pass; package
and generated coverage checks pass. This is not completion of the Fate sphere.

The Empress now offers separate received spending/discharge modifiers for each
eligible roll category. Discharge excludes weapon damage and supports zero
remaining points; its bonus is 5 plus one per four remaining points, not caster
level. Both phases of `build/pcgen-spheres-gwlzenb_` pass point boundaries,
disable/removal and unchanged ability scores. Pool bookkeeping, per-roll limits
and eligible-roll enforcement remain player-managed and explicitly described;
these records do not implement a resource ledger. Full build passes with 66
catalog tests, 104 feat tests, 655 scenarios and 21,147 engine checks.

Persistence follow-up `build/pcgen-spheres-mnsu5o85` passes both phases with
Hermit CL10 attack self-aid inactive and Empress three-point weapon damage active
at save. Reload proves independent reactivation/removal; the live matrix also
verifies Empress uses the highest insight bonus rather than stacking. This
supersedes the exercised-only limitation for these two specific recipient
choices, not automatic aid or point spending.

Cups, Pentacles, Swords and Wands now have received motif bonuses with their
untyped bonuses preserved. Cups affects only mental-stat skills; Pentacles
offers separate save choices; Swords does not add damage. Both phases of
`build/pcgen-spheres-6s_7unsp` pass CL1/9/10/19/20 and removal, including actual
mental and physical skill comparisons. These arcana are exercised, not retained
in the saved fixture. Discharges and motif selection limits remain manual.
The expanded temporary-effect matrix exceeded 110 seconds twice after character
load; its bounded runner now allows 180 seconds and both phases complete. All
67 catalog tests and generated-file/package checks pass.

Arcana descriptions and regression assertions explicitly exclude attachment to
another motif: attached arcana supplies only discharge benefits, not its normal
bonus. The recipient records are for standalone casting only. The full build
also passed with 67 catalog tests, 104 feat tests, 655 scenarios and 21,147
engine checks; description-only regeneration passed all 67 catalog tests.

The Fool now provides its received save penalty, decreasing at CL10/20 and
stopping at zero rather than granting a bonus. Both phases of
`build/pcgen-spheres-ty5xy4gh` exercise CL1/9/10/19/20/29/30/40, all saves,
unchanged attack/ability statistics and removal. Rerolls, discharge and timing
remain player-managed; this effect is not retained in the saved fixture. All
68 catalog tests and generated-data/package checks pass.

Persistence follow-up `build/pcgen-spheres-ax85bska` passes both phases with
Cups CL20 and Wands CL10 retained alongside the existing effects. Actual
Spellcraft and initiative removal checks demonstrate their independent saved
contributions. This supersedes the exercised-only limitation for Cups/Wands;
Pentacles, Swords and The Fool still have exercised-only coverage. The full
build passes with 68 catalog tests, 104 feat tests, 655 scenarios and 21,147
engine checks. Generated catalog, coverage and package checks pass.

Persistence follow-up `build/pcgen-spheres-568bt2zh` also retains Swords CL20,
Pentacles Fortitude CL10 and The Fool CL10. Both phases pass; reload checks
isolate their attack, chosen-save and penalty contributions before exercising
the complete matrix. This closes the remaining exercised-only coverage noted
above for those recipient effects, not their discharge or casting lifecycles.

Villainy's paid ally bonus and The Sun's discharged defense now use received
temporary effects. Villainy preserves the untyped CL/3 progression and explicitly
requires the additional spell point, marked target and weapon-damage context.
The Sun accepts the caster's signed casting modifier (not caster level), changes
AC/saves only and uses highest-insight stacking. Neither executes its trigger,
healing, targeting or expiration automatically. The dedicated bounded harness
`tools/pcgen_fate_effects.py` avoids expanding the already-large Enhancement
matrix. Both phases of `build/pcgen-spheres-yjqk0f68` pass boundaries, negative/
zero modifiers, removal, cancellation, stacking and retained-effect persistence.
All 70 catalog tests pass.

Perfect now offers received skill modifiers for each chosen ability without
altering ability scores, plus its Dexterity/Wisdom initiative modifiers and a
separately gated Intelligence trained-check bonus. Both phases of
`build/pcgen-spheres-4ydxvdyd` exercise all six choices at CL1/4/5/10/20, removal
and disabling the trained-only bonus. These Perfect records are exercised, not
retained in that save. Movement, maneuver benefits, temporary HP, effective
untrained ranks and action changes are still open; descriptions explicitly say
which benefits are not supplied. All 71 catalog tests pass. The first full build
detected stale generated coverage; regenerated it rather than relaxing the test.

Perfect follow-up adds the Dexterity speed increase to all existing movement
modes, without creating flight or other absent modes, and separate Strength
bonuses for bull rush, overrun and trip when independently non-provoking.
Both phases of `build/pcgen-spheres-kkhl_8ri` pass movement boundaries, existing
walk/climb/swim/fly/burrow, maneuver-specific CMB, unchanged CMD/ordinary attack,
and removal. These choices are exercised rather than persisted. Eligibility for
the alternative maneuver bonus remains an explicit player-managed condition;
the records do not grant Improved maneuver feats. This supersedes the missing
movement/maneuver numerical benefits above, not action/trigger automation.
All 72 catalog tests pass; coverage was regenerated.

Borrow Trouble now has post-reroll received bonuses for attack rolls, saves,
skills and ability checks (initiative only for the latter). Both phases of
`build/pcgen-spheres-oi_7srmz` verify category isolation, unchanged AC/damage/
ability scores, disabling, removal and a retained skill bonus across save/reload.
Rerolls, spell-point expenditure and the subsequent-success expiration trigger
remain player-managed. The live Fate harness now uses the actual four-argument
CharacterAbilities constructor; the earlier three-argument call did not compile
against this checkout. Full build passes: 73 catalog tests, 106 feat tests,
655 scenario checks and 21,147 engine checks.

### Tug Fate triggered roll modifiers

Eight received-effect records separate attack/save/skill/initiative choices and
positive luck bonuses from untyped penalties. They use 10 + half caster level
rounded down, and explicitly exclude taking 10. The player applies only the
chosen modifier to the triggering roll and removes it immediately afterward.
Natural 1/20 conversion, its save, aura membership and casting costs remain
table-resolved. Both phases of `build/pcgen-spheres-sms6et04` pass CL1/2/3/10/19/20,
competing luck bonuses, penalty coexistence, AC/damage isolation, disabling and
removal. These records are exercised in both phases, not retained across saves.
All 76 catalog tests pass; generated coverage and package checks pass.

Malice now supplies one received accumulated-total modifier to attacks, damage
and saves, without incorrectly treating caster level as the current bonus.
The player tracks once-per-round triggers, the casting-modifier cap, individual
bonus expiration and victim changes, replacing rather than duplicating the
record. Both phases of `build/pcgen-spheres-etot_3ay` pass totals 1/2/4/3/1,
reset/removal, AC/skill isolation and a persisted +3 alongside other effects.
All 78 catalog tests pass; package and generated coverage checks pass. This is
recipient arithmetic, not automated trigger or duration tracking.

Fate caster-side references now include consecration radius, close/medium/long
word range, Echoing Word additional targets, Bargain delay, Harm damage, and
Consequences damage/roundly trigger limit. All use Fate caster level. Both
phases of `build/pcgen-spheres-xju80ixp` exercise CL1/2/4/5/9/10/20, Resounding
Word's two-selection cap and partial/full refunds, and talent-owned reference
removal. These caster selections are exercised, not retained in the saved
fixture. Target selection, damage application and elapsed rounds remain manual.
All 79 catalog tests and deterministic/package checks pass; coverage regenerated.

Undo Harm's healing ceiling and second-selection condition limit now use
base-sphere-owned formulas, so refunding one repeated selection cannot erase
the surviving healing benefit. Both phases of `build/pcgen-spheres-ykxf8lgs`
pass absent/one/two selections, partial/full refunds and caster-level boundaries.
These are ceilings, not automatic healing: damage since the preceding turn,
creation time, death/destruction, condition eligibility and spell-point payment
remain table-resolved. Full build passes (79 catalog tests, 106 feat tests,
655 scenario checks, 21,147 engine checks).

Enmity's strong/overwhelming opposing-aura Will penalties now have separate
received records, explicitly limited to that saving throw and the strongest
applicable aura. Both phases of `build/pcgen-spheres-o2_44rzd` verify -1/-2,
Fortitude/Reflex isolation, disabling and removal. These records are exercised,
not retained in the save. Alignment comparison and consecutive conditions remain
manual. Full build passes with 77 catalog tests, 106 feat tests, 655 scenario
checks and 21,147 engine checks.

The Hanged Man discharge has separate received attack, save, maneuver, skill
and initiative bonuses. Input is damage paid (lesser of recipient HD and caster
level), with half rounded down and a minimum +1 insight bonus. Both phases of
`build/pcgen-spheres-krf58poj` pass damage 1/2/3/4/7/20, highest-insight stacking,
removal, damage/CMD exclusion and persistence of the seven-damage maneuver
choice. Damage payment, choosing the single roll and discharge remain manual.
All 74 catalog tests and generated-file/package checks pass.

Pain now applies its received -4 mental-skill penalty without changing physical
skills, ability scores or saves. Both phases of `build/pcgen-spheres-msi9iig8`
test actual Spellcraft, Survival, Bluff, Climb and Acrobatics modifiers, removal
and retained-effect persistence. Nonlethal damage and the casting magic-skill
check remain manual. Full build passes with 75 catalog tests, 106 feat tests,
655 scenario checks and 21,147 engine checks.

Perfect's Charisma option now includes a separate one-round Diplomacy penalty
record. It combines with the existing CHA skill benefit for a net -9, without
penalizing Bluff or ordinary Diplomacy. Both phases of
`build/pcgen-spheres-_88l39qe` test actual skill modifiers, disabling and removal.
The accelerated record is exercised, not retained across the save. Attitude
changes, eligibility and action expenditure remain player-managed. All 80
catalog tests and the package check pass.

The King now supplies its received insight bonus to native spell concentration
and the Spheres concentration variable. Both phases of
`build/pcgen-spheres-e4tsya1s` pass CL1/9/10/19/20, highest-insight stacking,
unchanged caster level, disabling and removal. These effects are exercised,
not retained across the save. Transferring an effect on discharge remains
player-managed. Full build passes with 81 catalog tests, 106 feat tests,
655 scenario checks and 21,147 engine checks.

King persistence follow-up: `build/pcgen-spheres-hj3_820x` retains the CL20 motif
in the saved character and verifies both concentration bonuses and their removal
after reload. Both phases pass; this closes the retained-effect gap noted above.

The Wheel's discharge now has separate attack, save, skill, initiative and
concentration records using twice the original d4 sum. Both phases of
`build/pcgen-spheres-47laekme` pass sums 1/4/5/8/12, disabling, removal and
damage/CMD exclusion. The new records are exercised rather than retained.
The ongoing random-category benefits, dice rolls and discharge lifecycle are
not automated. All 82 catalog tests and package checks pass.

Wheel follow-up adds the four ongoing category records. Each takes the total
for that rolled category, including repeated results, and competes normally
with other insight bonuses instead of stacking them. Both phases of
`build/pcgen-spheres-fgk_hljw` pass totals 1/2/4/6/9, category isolation,
highest-insight stacking, unchanged AC and removal. The records are exercised,
not retained. Dice rolling, computing each category total and removing ongoing
categories on discharge remain player-managed. This supersedes the missing
ongoing modifiers above, not the lifecycle limitation. Full build passes with
83 catalog tests, 106 feat tests, 655 scenarios and 21,147 engine checks.

Wheel persistence follow-up: both phases of `build/pcgen-spheres-rs3hq9qo`
retain and remove an ongoing +6 attack/damage category and a discharged +16
skill modifier (sum eight), alongside the other saved motifs. This closes the
retained-choice coverage gap for both Wheel input models.

The Emperor's ongoing penalty reduction now has conditional attack, damage,
save, skill and initiative records. Input is the actual eligible reduction,
not caster level; original penalties remain active and the result must retain
at least -1. Both phases of `build/pcgen-spheres-gqk6r2z4` test CL1/9/10/20
against -2/-3/-6 penalties, removal and unchanged AC. These records are exercised,
not retained. Selecting eligible penalties and recalculating the reduction
remain player-managed; this is not automatic penalty interception. Discharge
is still open. All 84 catalog tests and package checks pass.

Emperor discharge follow-up adds separately typed insight records for the
affected roll categories. Descriptions exclude self-imposed penalties from
the bonus and require separate suppression of the original penalty. Both phases
of `build/pcgen-spheres-pq_jbodr` test magnitudes 1/3/6, competing insight and
removal; the records are exercised rather than retained. Automatic selection,
suppression and restoration of the original penalty remain open. Full build
passes with 85 catalog tests, 106 feat tests, 655 scenarios and 21,147 engine
checks.

Emperor persistence follow-up: both phases of `build/pcgen-spheres-q1_y3bvr`
retain an inactive +2 initiative penalty-reduction choice and an active +7
discharged save choice. Reload verifies reactivation, independent removal and
highest-insight interaction with the saved Sun bonus. This closes the retained
input/activation coverage gap, not automatic penalty suppression. The initial
run exposed stale generated feat data for Sacrosanct Firewall; regenerating from
the existing reviewed Hallow parser fixed that mismatch. All 107 feat tests pass;
the regenerated inventory reports 303 unresolved feats.

The Page discharge now has attack, damage, save, skill and initiative recipient
records that double the entered existing morale bonus using `TYPE=Morale`, not
an additive untyped bonus. Both phases of `build/pcgen-spheres-q7m6w6wq` verify
inputs 1/2/5, same-type replacement rather than tripling, disabling, removal and
unchanged AC. These effects are exercised, not retained across the save. The
player must identify the eligible roll and existing bonus; duration extension,
discharge actions and automatic expiration remain table-resolved. Full build
passes with 86 catalog tests, 107 feat tests, 655 scenarios and 21,147 engine
checks.

Page persistence follow-up: both phases of `build/pcgen-spheres-aofbvos5` retain
an inactive skill discharge with input three. Reload verifies the inactive state,
reactivation to +6 morale and independent removal alongside saved insight and
untyped modifiers. This supersedes the exercised-only limitation for that choice;
eligibility and discharge lifecycle are still player-managed.

The Lovers now supplies its received insight save bonus using the player-entered
adjacent ally count capped at 2 + floor(caster level/5). Both phases of
`build/pcgen-spheres-fjvg0hk9` pass zero/one/two/six allies, decreasing counts,
highest-insight stacking, unchanged AC/attack and removal. This record is
exercised, not retained in the saved fixture. Adjacency, cap calculation and
damage transfer are still player-managed; no damage reduction is granted.
All 87 catalog tests and generated-file/coverage/package checks pass.

Lovers persistence follow-up: `build/pcgen-spheres-99796ru6` passes both phases
with an eight-ally capped recipient bonus retained. Reload removes it and restores
the lower saved Emperor insight contribution rather than losing all save bonuses.
This tests a received effect from a sufficiently high-level external caster,
not the recipient's own casting eligibility. Full build passes with 87 catalog
tests, 107 feat tests, 655 scenarios and 21,147 engine checks.

The Knight now has a received initiative-only offset for condition penalties.
Both phases of `build/pcgen-spheres-eicvxdbt` verify inputs 0/2/3/4/6, preserving
an unrelated -1 initiative penalty and a condition's -2 attack penalty, and
restoring all initiative penalties on removal. The player supplies the eligible
condition total; this does not detect conditions, restore Dexterity or execute
metamagic discharge. It is exercised rather than retained. All 88 catalog tests
and generated-file/coverage/package checks pass.

Tower, Queen, Page and Lovers now expose caster-side numerical references for
DR/hardness bypass and weapon-discharge dice, fear-duration reduction and
triggered damage reduction, morale-duration extension, and the adjacent-ally cap.
These do not grant permanent caster defenses or perform damage/duration changes.
Both phases of `build/pcgen-spheres-mismlsfy` exercise caster-level scaling and
talent removal; these talents are not retained in the fixture. Full build passes
with 89 catalog tests, 107 feat tests, 655 scenarios and 21,147 engine checks.
Recorded talent-mechanics keys increase to 79, which is not a completion count.

Arcana discharge references now expose Cups' retained-d20 count, Pentacles'
reroll allowance, Swords' one-use confirmation bonus, and all four arcana's
discharge durations. Swords remains one minute rather than scaling with caster
level. Both phases of `build/pcgen-spheres-w817dpg7` exercise caster levels
1/2/4/5/6/7/9/10/13/14/20/21 and removal of each owning talent. These selections
are exercised, not retained across saves. Dice results, spent rerolls and
expiration remain player-managed. The expanded matrix exceeded its 110-second
bound after loading; the runner now permits 180 seconds, matching the existing
temporary Enhancement harness. Full build passes (89 catalog tests, 107 feat
tests, 655 scenarios, 21,147 engine checks). Recorded mechanics keys are now 83.

Swords discharge now provides a confirmation-only recipient toggle, with the
minimum-one half-caster-level bonus. Ordinary attacks must leave it disabled;
once-only use, automatic-threat exclusions, concealment and the one-minute
expiration remain player-managed. Both phases of `build/pcgen-spheres-df2r1bm5`
pass CL1/2/3/4/9/10/19/20, damage/AC isolation, disabling and removal. This
recipient choice is exercised rather than retained in that save. The live
fixture is now Fey Adept 12: its retained nine-talent matrix exceeded the former
level-2 pool and failed to retain both Resounding Word selections. No production
pool checks were bypassed. Full build passes with 90 catalog tests, 107 feat
tests, 655 scenarios and 21,147 engine checks.

Persistence follow-up `build/pcgen-spheres-bdz3wp7v` passes both phases with
inactive Swords CL10 confirmation and Knight input four retained. Reload checks
reactivation and independent removal alongside the other saved motifs. This
closes their retained-choice gaps, not automatic confirmation eligibility or
condition detection. Generated catalog, coverage and package checks pass.

Mana `(amp)` prerequisite families now resolve reviewed purchased talents with
the descriptor, accepting both “any” and “at least one” wording. The base sphere
and non-amp manipulations do not qualify; unknown descriptors remain fail-closed.
Both phases of `build/pcgen-spheres-2rjmag43` test Favorite Boost with no sphere,
base Mana, Bulwark, two different amp members and member removal. Its selected
amp choice and cost adjustment remain open. All 108 feat tests pass; unresolved
feat records decrease to 301. Trait and coverage regeneration and package checks
pass; Amplifying Adjustment still requires its unsupported Spellhacking sphere.

Divination prerequisites now distinguish base Read Magic (a sense ability) from
a purchased `(sense)` talent. The three Precogniscent feats accept the former;
Glimpse The Flow requires the latter and retains its Divination-specific CL6
gate. Both phases of `build/pcgen-spheres-jts2w0kc` check Precogniscent Protection
before/after base-sphere selection and removal. Offline tests protect purchased
descriptor membership and sphere-specific caster level. Active-sense tracking
and these feats' benefits remain open. Full build passes with 109 feat tests,
90 catalog tests, 655 scenarios and 21,147 engine checks; unresolved feats now
number 297, not a measure of completed effects.

Sensory Overload now has a received -2 Fortitude/Will modifier restricted to
mindless targets saving against that effect. It does not penalize Reflex or
change Intelligence. Both phases of `build/pcgen-spheres-0ubdah8n` verify
application, disabling, removal and an inactive choice retained across reload.
The dedicated Divination runner keeps this matrix separate from Enhancement.
Mindless eligibility, nonlethal damage, flat-footed state, action restrictions
and concentration remain player-managed. Full build passes with 92 catalog
tests, 109 feat tests, 655 scenarios and 21,147 engine checks.

Divine Future now supplies separate received one-roll attack, save, skill,
initiative and maneuver modifiers. Input is the rolled d4 plus floor(caster
level/5), not caster level. Both phases of `build/pcgen-spheres-gc6nvy5y` test
results 1/4/5/7/8, category isolation, actual skill modifiers, unchanged damage
and AC, disabling/removal and a retained seven-point maneuver choice. Dice,
use capacity/refresh, ally eligibility and non-initiative ability checks remain
player-managed. All 93 catalog tests and generated-file/package checks pass.

Divine Future's explicit five-selection maximum now takes precedence over its
“multiple times” wording in the repeat parser. Both phases of
`build/pcgen-spheres-36rj1k19` reject selection without Divination and a sixth
purchase, verify every partial refund and full pool restoration, and retain all
five selections across reload. The fixture uses a legal Fey Adept 12 talent pool.
This enforces capacity, not spending or daily refreshing of uses. All 94 catalog
tests and deterministic/package checks pass.

Precogniscent Protection, Resistance and Smite now use a single explicit active
Divination sense count with their separate Hit-Dice caps and insight/resistance
types. The temporary state does not grant feats or senses. Both phases of
`build/pcgen-spheres-s6ff4vn9` exercise counts 0/1/2/3/4/10, zero benefits from
known-but-inactive senses, caps at HD12, state disabling, feat removal and the
remaining feat's shared-counter behavior. These feats/state are exercised, not
retained in that save. Sense lifecycle, spell points, immediate actions, critical
conversion, rerolls and Smite's miss-chance discharge remain player-managed.
All 110 feat tests and 94 catalog tests pass; recorded feat-mechanics entries
increase to 168, not a count of complete feats.

Precogniscent persistence follow-up: both phases of
`build/pcgen-spheres-x098jg34` retain all three feats and the active-sense count
alongside the five Divine Future purchases and received modifiers. Reload
verifies the count and removal of Protection's capped bonus. Competing +6
insight/resistance sources take the higher bonus rather than adding together.
This closes the retained-state gap above. Full build passes with 94 catalog
tests, 110 feat tests, 655 scenarios and 21,147 engine checks.

Divine Capability now has a conditional circumstance modifier for skill checks
to assess or identify a successfully divined target. Both phases of
`build/pcgen-spheres-iog1jxir` verify CL1/2/3/10/11/20, actual Spellcraft and
Sense Motive modifiers, attack/save isolation, disabling/removal and a retained
inactive CL11 choice. Target eligibility and assessment remain player-managed;
the modifier must be disabled for unrelated checks. Full build passes with 95
catalog tests, 110 feat tests, 655 scenarios and 21,147 engine checks.

Rapid Response now supplies competence initiative and separate two-/three-
selection Reflex recipient bonuses. Both phases of
`build/pcgen-spheres-i4xja9kz` exercise CL1/2/3/10/11/20, highest-competence
stacking, disabling and removal. These choices are exercised, not retained in
the saved fixture. Surprise actions, evasion/uncanny-dodge upgrades and checking
the external caster's purchase count remain player-managed; no permanent class
features are granted. All 102 catalog tests and package checks pass.

Ghost Sight and Unhooded Sight now provide conditional recipient modifiers for
their specific Perception/disbelief checks. Both phases of
`build/pcgen-spheres-kg1u523u` exercise CL1/2/3/4/9/10/20, actual Perception,
Will and magic-skill bonuses, unchanged Fortitude/Reflex/caster level, disabling
and removal. These senses are exercised rather than retained in the save.
Revealing targets, line of sight, illusion eligibility and effect lifetimes
remain player-managed. All 96 catalog tests and deterministic/package checks pass.

Sniper's Eye now offers separate distance-Perception and ranged-attack penalty
offsets. Input is the actual eligible reduction, capped by caster level or half
caster level respectively; original penalties/DC increases remain in force.
Both phases of `build/pcgen-spheres-_t8z_jpj` exercise CL1/2/3/10/20 against
penalties 0/2/6/15, restoration on removal, no net positive bonus and unchanged
damage. Eligibility and recalculation remain player-managed; these offsets are
exercised, not retained. The same save retains inactive Unhooded Sight CL9 and
verifies its reactivation/removal. All 97 catalog tests and package checks pass.

Discern Individual now supplies its minimum-one, half-caster-level insight
bonus for monster lore through a conditional recipient modifier. Both phases
of `build/pcgen-spheres-rmdfe9u9` verify all six monster-identification Knowledge
skills at CL1/2/3/4/11/20, exclude History and Spellcraft, exercise disabling and
removal, and retain an inactive CL11 selection for reload. Other Knowledge
checks must not use it. Permission to attempt monster lore untrained remains
table-resolved; no ranks or general untrained Knowledge access are granted.
All 98 catalog tests and deterministic generation checks pass.

Divination now exposes its medium divine range and sense duration using the
sphere-specific caster level. Greater Divine switches only divine range to
long; Lingering Divination adds two rounds after concentration ends. Both
phases of `build/pcgen-spheres-5pblu7np` test CL1/2/5/11/20 and talent refunds.
These talents are exercised, not retained in that save. Concentration, elapsed
time, visibility/barriers and casting actions remain player-managed. All 99
catalog tests pass; coverage reports 87 basic talents with recorded mechanics.

Shared Perception now calculates two targets plus one per five sphere caster
levels and its independent long-range link distance. Viewing exposes sensor
detection DC 20 plus sphere caster level. Both phases of
`build/pcgen-spheres-z37o6olw` verify CL1/2/4/5/9/10/11/20 and removal; the
shared link does not require Greater Divine. These are calculated limits, not
sensor placement, target selection, communication or automatic sense sharing.
All 99 catalog tests pass; 89 basic talents now have recorded mechanics.

Time now calculates touch/close/medium/long casting range separately from its
concentration-maintenance distance, released duration, repeated Temporal Trap
capacity, Mass Time additional targets and Augment Healing's fast-healing rate.
Native recipient modifiers cover Haste attack, separately toggleable dodge
AC/Reflex, existing movement modes, and Slow attack/AC/Reflex penalties.
Both phases of `build/pcgen-spheres-arp5hrmt` verify range/refund boundaries,
three retained ranged/trap purchases, received bonus boundaries, walking-speed
removal, and an inactive CL20 Haste attack effect retained across reload.
All 100 catalog tests pass. Slow speed halving, Improved Haste attacks,
staggered state, healing execution, countering checks, target selection and
trap placement/lifecycle remain open. Haste/Slow must not simply be combined:
their opposed magic skill check determines whether they cancel. Range zero
denotes touch, not permission to target a square at zero feet.

Improved Haste now supplies separate received full-attack and additional
opportunity-attack choices. Both phases of `build/pcgen-spheres-hp5hprzq` verify
the extra attack's enhancement-type nonstacking, CL1/4/5/9/10/20 opportunity
capacity and refunds. The save retains active CL20 opportunity capacity and an
inactive full-attack choice; reload verifies both independently. The player must
enforce the mutually exclusive per-round options and track expenditure. The
capacity is a temporary bonus, queried through PCGen's bonus API rather than an
undefined character variable. This supersedes the missing Improved Haste
numerical benefits above, not action execution or Slow movement handling.

Timeline Bridge now supplies its received insight Knowledge bonus and separate
single-attack AC/single-save choices. Both phases of
`build/pcgen-spheres-lr5r38ij` test CL1/2/3/10/11/20, actual Knowledge versus
Spellcraft, disabling and removal. Active CL11 Knowledge and Rapid Response
initiative choices are retained and independently removed after reload.
Untrained-check permission, spending the immediate action/spell point and
ending the ongoing effect remain player-managed; no ranks are granted.
All 103 catalog tests and deterministic/package checks pass.

Broken Time now applies its received half-caster-level penalties to attacks and
skills, without penalizing saves, damage or ability scores. Both phases of
`build/pcgen-spheres-3hnjexko` exercise CL1/2/3/9/10/11/20, disabling and removal,
and retain an inactive CL11 choice for independent reactivation on reload.
Initial and subsequent Will saves, concentration checks against caster MSD,
duration and casting costs remain player-managed. Full build passes with 101
catalog tests, 110 feat tests, 655 scenarios and 21,147 engine checks.
