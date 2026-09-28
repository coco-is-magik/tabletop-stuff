# Spheres implementation depth audit — 2026-09-25

Repository: `/nas/contents/Projects/Programming Projects/Java/tabletop-stuff`.
Scope audited: the PCGen Spheres of Power/Might dataset under `data/spheres`
and its generators/tests. Method: inventoried every documented partial area,
then measured the two largest ones (feat prerequisites and talent mechanics)
against the pinned source snapshots. This audit supersedes no prior document;
it consolidates their partial-scope statements and drives the corrections below.

## What is solid (do not regress)

- Base-sphere/talent selection, pools, prerequisites, refunds, save/reload —
  verified by live production-controller gates for all 53 spheres.
- Incanter/Conscript/17 base classes: source-table progressions, verified by
  live gates (class effects beyond tables remain manual by design).
- Feat catalog: 1,201 entries, exact-match prerequisite compiler with
  fail-closed adjudication escape hatch.
- Custom traditions builder (6 drawbacks), custom Spellcrafting compiler
  (2026-09-25) with live two-gate verification.
- Core Fighter isolation: Spheres data never leaks into core-only characters.

## Finding 1: feat prerequisites — 584 of 1,201 feats fail-closed

Every feat with any unrecognized clause requires a manual `Reviewed - <feat>`
adjudication record. Analysis of all unresolved clauses against the pinned
snapshots shows three large *compilable* families that were being rejected
only because the parser could not express them:

1. **OR of multi-clause AND branches** (~59 clauses). Example: 14 squadron
   feats require "War sphere, Squadron Commander; or Warleader sphere,
   Troop Commander". Both branches resolve to existing catalog records; the
   parser bailed on any clause starting with "or". Trailing global
   requirements ("character level 10th", "caster level 5th or 5 ranks in
   Diplomacy") after the last branch are hoisted to apply to all branches —
   the stricter, fail-safe reading.
2. **Casting-tradition drawbacks** (~60 feats). Eight drawback names appear
   in feat prerequisites and in the pinned `casting-traditions.json` General
   Drawbacks section, but only six drawbacks had selectable records:
   Addictive Casting, Area Bound, Bonded Casting, Charged Spells,
   Mental Focus, Terrain Casting, Unsettling Casting, Vampiric Casting.
   Clause forms "X drawback", "X (drawback)" and bare "X" all occur; no feat
   name collides with any drawback name, so bare-name mapping is safe.
3. **Skill-rank forms** (~20 clauses). The whitelist lacked parenthesized
   skills (Craft (alchemy), Knowledge (planes), Perform (dance), ...) and the
   reversed "5 ranks in Diplomacy" form.

Deliberately left fail-closed (no honest representation in this dataset):
spheres from other supplements (Performance, Communication, Bluster, Faction,
Navigation), racial types/subtypes, core class features (bardic performance,
channel energy), tension pools, "ability to gain martial focus" (no common
practitioner marker exists yet — a shared marker across the seven
SPHERES_COMBAT_TALENTS classes is future work), "N ranks in any N skills",
and the Card Casting deck subsystem.

## Finding 2: talent mechanics — 18 overrides for 2,330 talents

`catalog-mechanics.json` automates 18 talents; the rest carry rules text only.
This is correct for tactical actions but means most persistent effects
(skill ranks beyond the ten implemented grants, conditional bonuses, free
grants, companion/gizmo construction) are not character-builder automated.
Full automation is a per-talent audit, not a generator change; no blanket
correction is honest. Not changed in this pass.

## Finding 3: traditions — 6 of ~50 general drawbacks selectable

The custom casting tradition builder implemented only 6 drawbacks. The eight
added for Finding 1 are selectable records with source descriptions; their
drawback *effects* remain sheet rules, same as the original six.

## Corrections applied in this pass

- `tools/spheres_feats.py`: multi-clause OR branches with global-requirement
  hoisting; "one of X, Y, or Z" alternatives; "N ranks in X" skill form;
  extended skill whitelist; drawback clause mapping (fail-closed preserved:
  any unresolvable branch or clause rejects the whole expression).
- `data/spheres/spheres_traditions.lst`: eight new drawback records, one
  point each, consistent with the existing six.
- Regression tests in `tools/test_feats.py` for every new pattern.

Measured result: unresolved feat prerequisites dropped from 584 to 496
(88 feats, -15%). Verified 2026-09-25: 16 feat tests, 34 Spheres tests,
catalog/conscript/class suites, and live PCGen gates all pass — feat
power save+reload (build/pcgen-spheres-pfd2nfi2), feat might save+reload
(build/pcgen-spheres-frj0ygsw), and tradition power save+reload with the
expanded drawback list (build/pcgen-spheres-t_gwb1mp). The feat gates prove
the new nested-PREMULT and drawback-prerequisite records parse and run in the
production selection controller without LSTERROR.

## Remaining known partial areas after the September 25 pass

- Per-talent mechanical audit (Finding 2) — largest remaining body of work.
- Shared martial-focus marker for practitioner classes.
- Class feature automation beyond level tables (documented per class).
- Spellbook Mastery casting bypass and Spellcrafting lifecycle automation.
- Advanced/legendary talents, archetypes, Guile, multiclass casting engine.

## September 27 continuation: martial-focus eligibility

Completed one bounded part of the backlog, not the entire Spheres implementation.
The pinned `using-spheres-of-might.json` Martial Focus section explicitly grants
eligibility through combat training, Extra Combat Talent, or a martial tradition
or combat progression. The shared `Spheres Martial Focus` automatic ability now
represents eligibility, with baseline capacity 1. It does not represent current
focus or automatically spend/regain focus during encounters.

- Conscript and the seven generated practitioner classes grant the shared ability.
  Their training records carry `SpheresCombatTraining`; the feat compiler no
  longer incorrectly treats Conscript as the only combat-training class.
- Extra Combat Talent and both existing martial-tradition records also grant
  eligibility, without granting the combat-training class feature.
- Exact focus prerequisite forms compile to the shared ability. Unsupported
  alternatives (for example skill leverage) still require adjudication.
- Generated feat prerequisites now leave 487 unresolved, down from 496. This
  measures prerequisite coverage, not mechanical implementation of those feats.
- Great Focus remains capacity 2; removal restores capacity 1. Current focus
  remains a player-tracked encounter resource.

Verification: 18 feat, 4 class-catalog, 34 Spheres, 8 catalog and 3 Conscript
tests passed. Live feat save and reload gates passed for both Power and Might
(`build/pcgen-spheres-3vvfnw_e` and `build/pcgen-spheres-gnqt9sd8`). They exercise
focus eligibility grant/removal on a non-practitioner, practitioner eligibility,
capacity, Great Focus removal, and replay after reload. All seven generated
class grants are checked offline; they were not individually live-tested here.
The build test target separately passed 6 spellcrafting tests, 34 Spheres tests,
655 scenarios and 21,147 engine regressions. It does not run every dataset suite.

### Still open; do not describe these as finished

| Area | Remaining implementation and acceptance work |
| --- | --- |
| Talent mechanics | Per-talent persistent effects, repeat effects, choices and grants; compare generated character values against source rules, including removal and stacking. Existing override coverage is not full mechanics coverage. |
| Class features | Named option prerequisite validation, choice-dependent skills/feats, bound equipment, companions/inventions, resources and multiclass stacking. Armiger practitioner-ability choice remains descriptive. |
| Traditions | Remaining general drawbacks and their mechanical effects; legal choice combinations, starting proficiency trades and grants for classes other than Conscript. |
| Feats | 487 unresolved prerequisite sets plus descriptive-only feat effects; unknown clauses must remain fail-closed. |
| Spellcrafting | Spellbook Mastery book-casting path, mishaps, forgetting/acquisition lifecycle and prerequisite-change handling. |
| Martial focus | Encounter-state expenditure/recovery and non-class talent-progression conversions are not automated. |
| Scope extensions | Advanced/legendary imports need permission and prerequisite handling. Archetypes and Guile are excluded by the existing dataset scope, not completed implementations. |

The next passes must preserve core-character isolation, paid versus free talent
pools, refunds and save/reload. Source descriptions alone are not acceptance
evidence for mechanics.

## September 27 continuation: Mageknight Mystic Combat

Implemented in `tools/spheres_mageknight.py`, called by the existing class
generator. Existing option keys are unchanged to preserve saved selections.
All explicit `requires` clauses in the pinned Mystic Combat headings now have
enforced gates: class level, base-class Marked/Mystic Defense/Resist Magic
availability, Life/War/Protection sphere ownership, and Shadowblade/Spell Shield
ownership. Unknown heading prerequisite grammar aborts generation rather than
silently creating an unrestricted option. These class-feature level checks are
for the supported base class, not archetypes that trade those features away.

Black Dog Companion requires level 4 and an explicit zero-cost
`Reviewed - Black Dog Companion Curse Talent` record in the new Mystic Combat
Review category. The dataset cannot yet verify curse descriptors, so the GM must
confirm the qualifying talent and remove the attestation when it is lost. This
does not automate the animal companion itself.

Magic Power and Combat Talent now grant one talent per selection and support
repeated selection. Whirl of Blows, Sunder The Veil and Weirding Initiate grant
their specified feats automatically, without those feats' ordinary prerequisites.
Removing the option removes its grant. Their other effects remain descriptive.

Verification: six class-catalog tests, including new prerequisite and grant
regressions. New production-controller harness `tools/pcgen_mageknight.py` ran
save/reload gates at levels 2, 6 and 12. Evidence directories respectively:
`build/pcgen-spheres-hdtt2icw`, `build/pcgen-spheres-ih8jlmoa`, and
`build/pcgen-spheres-j8f7gybc`. Checks cover rejected choices, class-level gates,
sphere and option removal revoking qualification, descriptor review, duplicate
rejection, repeated grants and partial/full refunds, bonus feat grant/removal,
and persistence of both repeated talent options at level 12. A live regression
found that defining the combat pool on the repeated option lost the remaining
grant on partial removal; the pool definition now lives on the class instead.

Still partial within Mageknight: Champion/Greater Combatant feat choice pools,
conditional Weirding grants, companion construction, temporary talent/feat
choices, and tactical effects. Prerequisite loss revokes qualification but does
not cascade-delete the dependent selected option. Other classes' option
prerequisites still need their own source-reviewed passes.

## September 27 continuation: persistent skill training

Added reviewed mechanics for Fencing's Read Foe and Leadership's Military
Training using the pinned source texts: Sense Motive and Profession (Soldier)
receive sphere-scaled ranks capped at total Hit Dice. The existing PCGen skill
keys are reused; no new skill definitions or dependencies were introduced.
Leadership now grants its half-BAB competence bonus to Diplomacy only while
Warleader is also owned. The shared typed rank grants do not stack. Removing
Warleader removes the overlap bonus. This covers the two Diplomacy-granting
spheres currently in the catalog, not future sphere imports.

Two offline regressions were added to the catalog suite (10 tests total), and
the suite is now included in the normal build test command. Generated catalog
records and the mechanical review manifest were regenerated.
The new production-controller runner `tools/pcgen_skill_training.py` passed
save/reload at levels 3 and 11, including base-sphere rejection, rank caps,
selection/removal, original sphere-skill scaling, refunds, nonstacking overlap
ranks, overlap bonus removal, and saved overlap bonus restoration. Evidence:
`build/pcgen-spheres-zyj08t1v` and `build/pcgen-spheres-cdylhqkq`.

Still manual: retraining previously purchased ranks, temporary-talent lifecycle
restrictions, and other associated-skill overlap conversions. Ace Pilot's
Profession (pilot) grant needs a reviewed skill definition (the loaded Core
dataset does not provide that skill). Equipment's selectable Craft training and
Tech's mechanical skill also require separate passes. This closes three
persistent-effect gaps, not the full talent-mechanics backlog.

## September 27 extended continuation: skills, Tech, Mageknight and Armorist

Completed across several passes rather than stopping after one correction:

- Added Core-compatible Profession (Pilot) and Craft (Mechanical) definitions,
  Ace Pilot training, Tech/Tinker training and the default Tinker skill-overlap
  bonus. The skills include class-skill and Skill Focus bonuses. The supported
  load remains Core + Spheres; Technology Guide and Iron Gods define Mechanical
  too, and cross-campaign duplicate-definition integration remains open.
- Corrected Alchemy/Trap/Tech DCs to use actual associated skill ranks. Tech
  now supplies a separate free gadget selection, charge/recharge/prepared-gadget
  capacities, gadget-talent counting, and repeatable Extra Gadgets effects.
  Actual charges, prepared inventories, drone construction and alternate Tinker
  associated skills are not tracked.
- Craftsman now chooses one Craft skill and grants HD-scaled ranks. Live tests
  exercise the actual chooser, selected-skill persistence and removal. Rank
  retraining and crafting elapsed time remain player-managed.
- Mageknight Champion/Greater Combatant now provide repeatable filtered feat
  pools with ordinary prerequisites, rather than description-only grants.
- Armorist now enforces Arsenal Trick heading prerequisites and base feature
  levels, supplies repeatable Combat Talent and Combat/Champion/Crafter feat
  pools, applies equipped armor-training adjustments, supports repeatable
  Greater Armor Training and increments Additional Binding's capacity.
  Base-class prerequisite assumptions do not cover feature-trading archetypes.

Validation: catalog and class-catalog regressions cover generated tags and
unknown-prerequisite rejection. The normal build now runs all eight offline
dataset suites rather than silently omitting feat/class regressions.
Live evidence includes Mageknight levels 6/16 (`pcgen-spheres-68egxtjw`,
`pcgen-spheres-r_8fjh37`), Armorist levels 2/12 (`pcgen-spheres-e9vfytcp`,
`pcgen-spheres-8vpjwu0s`), and the expanded skill/Tech/Craftsman level-11 suite
(`pcgen-spheres-57ku7yu0`), all under `build/`, with save and reload markers.
Earlier focused skill checks passed at level 6, but the combined harness now
requires level 8+ to afford all retained and temporary paid talent selections;
it does not inflate the character's pools to make tests pass.

Remaining class limitations: conditional Weirding grants, other classes' option
prerequisites, item/companion construction and automated dependent-choice cleanup.
The existing Spellcrafting lifecycle, advanced/legendary imports, temporary
talents, tradition effects and most per-talent mechanics also remain open.

### Armiger follow-through

The next pass enforces all pinned Prowess heading prerequisites, grants Great
Focus for Extra Focus, adds a repeatable Champion feat pool, and implements
Deadly Prowess's three distinct prerequisite-free feat choices. Regression
testing rejected both a generic selected-feat grant (orphaned a feat on removal)
and option-owned conditional grants (lost remaining grants on partial removal).
Class-owned, per-choice conditional grants pass partial/full refunds and
save/reload at level 6 (`build/pcgen-spheres-mwrgwdxk`). Other Prowess grants,
weapon configuration and conditional effects remain open. These are base-class
checks, not support for archetypes that exchange the required features.

Updated the older Armorist class-progression harness's expected bound capacity:
its fixture selects Additional Binding, which now contributes a real extra item.

### Eliciter and spellbook continuation

Eliciter's emotion parser now preserves introductory text before the four tiers
without weakening ordered-tier validation. The completed production harness
checks tier costs, prerequisite loss, level rejection, Persuasive skill and DC
bonuses, and save/reload at levels 2 and 12 (`build/pcgen-spheres-sbaqvo7y`,
`build/pcgen-spheres-reslo89p`). Emotion effects themselves remain descriptive.

Ultimate Spellbook Mastery now has separate deciphering, accessible-copy and
book-casting records. Book casting bypasses component requirements without
learning or spending repertoire slots; distinct missing spheres/basic talents
contribute 10 percent each to a computed mishap chance. Mastery, deciphering and
access are enforced. Advanced/unclassified talent recipes remain rejected.
The compiler has nine regression tests, including component deduplication,
feat bypass and fail-closed advanced talent handling. Live save/reload passed
in `build/pcgen-spheres-hc6b08ub`, including 20/10/0-percent transitions and
access/feat removal. Physical inventory linkage, spell-point expenditure,
actual casting and GM-selected mishaps remain manual. These changes do not
solve acquisition/forgetting cleanup or temporary talent integration.

### Catalog repeatability and counter lifetime

A new live assertion reproduced a shared bug: removing one repeated Extra
Gadgets selection erased its counter while another selection remained. All
generated repeat counters now belong to the base sphere rather than individual
selections; the existing Destruction sphere receives its counter through a
category-qualified `.MOD` record. Offline coverage checks every generated
counter's ownership. Live checks prove partial/full refunds, capped-selection
rejection after removal/reselection, and counter persistence after reload.

Companion Vessel is no longer incorrectly capped at its second-selection
milestone. Explicit `up to 2 times` and `more than once` wording now recognizes
Nature's Ranged Geomancy and Leadership's Talented. Extendo Appendage enforces
10 Mechanical ranks for its second selection. Range Amplifier supports one
initial selection plus one per five Mechanical ranks, with removal-safe counters.
These changes govern selection, not companion creation or gadget application.

Live combined skill/catalog save/reload evidence at level 11:
`build/pcgen-spheres-a399q39w`. The level-8 save gate passed in
`build/pcgen-spheres-af0ic5oy`; this covers rejection below Extendo's threshold
and Range Amplifier's lower cap. Full build passed all eight dataset suites,
655 scenario checks and 21,147 engine checks. Conditional repeat rules outside
this reviewed subset still need individual implementation; generic repeated
wording must not be interpreted as evidence that all such conditions are enforced.

The Tech Drone/Artificial Intelligence cap is now shared (four combined
selections), including repeatable AI selections and removal-safe shared counters.
Dedicated production-controller save/reload passed in
`build/pcgen-spheres-7s5gtpwb`: four Drone, four AI, mixed selections, cross-family
replacement, over-cap rejection, full paid-pool refunds and persistence. This
does not build drone/AI stat blocks or enforce active HD/level inventories.
The expanded level-8 skill/catalog reload also passed in
`build/pcgen-spheres-af0ic5oy`.
