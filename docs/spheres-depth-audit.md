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
