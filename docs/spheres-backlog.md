# Spheres continuation backlog — September 29, 2026

## Contract

Complete magic/martial traditions, feat-based Ultimate Spellcrafting, feats,
traits, alternate racial traits, spheres, and base/prestige classes. Reuse
PCGen's existing ability, feat, trait, racial replacement, equipment and class
systems; do not invent substitute game rules. Preserve saved ability keys,
existing pools and the standalone dice-pool experiment. Descriptive catalog
coverage is not mechanical completion. Archetypes were excluded by the earlier
scope; prestige classes are explicitly included in this continuation.

## Orientation evidence

Inspected the current generators, campaign records, depth audit and subsystem
documentation rather than relying on the previous conversation's results.
The current files include Mageknight/Armorist/Armiger feat choices, Eliciter
emotion tiers, Blacksmith/Scholar/Technician/Striker adapters, associated-skill
grants, Tech limits and removal-safe repeat counters. Spellcrafting already
has a reviewed recipe compiler and separate Spellbook Mastery access records.
These are existing implementations to retain, not new work in this session.
The baseline nine Spellcrafting regression tests passed locally.

## Remaining acceptance work

| Area | Current boundary | Completion work |
| --- | --- | --- |
| Casting traditions | Original fourteen choices plus weighted Extended Casting and second-tier Extended/Somatic choices, three boons | Remaining weighted/repeated drawbacks, incompatibilities, other drawbacks/boons, named traditions, sphere-specific grants and casting modifier effects |
| Martial traditions | Custom Conscript only | Source-named traditions, other eligible classes, proficiency trades and alternative structures |
| Spellcrafting | Existing feat-driven recipe and repertoire system | Source-backed timing, advanced prerequisites when supported, temporary talents, inventory access and forgetting lifecycle |
| Feats | Catalog and reviewed prerequisite/effect compiler | Resolve remaining prerequisites using loaded systems and audit persistent effects individually |
| Traits | Shared PCGen Traits pool | Remaining prerequisites/effects, category and prerequisite-loss checks |
| Alternate racial traits | Not loaded by this campaign | Source inventory, reuse upstream racial replacement categories, enforce replacement conflicts and refunds |
| Spheres | 53 sphere catalogs plus reviewed mechanics | Advanced/legendary talents, persistent effects, packages, companion/equipment integration |
| Base classes | Progressions and selected option mechanics | Remaining option gates, grants, resources and existing subsystem integrations |
| Prestige classes | No campaign records | Source inventory, entry requirements, class-specific advancement and multiclass round trips |

## Verification policy

Run focused offline tests before broader tests. Test real PCGen selection,
rejection, partial/full refunds, dependent qualification and save/reload for
changed pools and grants. Do not treat old evidence directories as new passes.
Do not replace unresolved prerequisites with permissive guesses. Retain source
edition boundaries: pinned pages can contain both Ultimate and Original text.

## September 29 implementation and verification

- Added Extended Casting (two points) and its second selection (four total),
  plus second Somatic Casting. Retained existing first-selection keys and used
  existing ability pools rather than adding a new tradition subsystem.
- Enforced Prepared Caster/Charged Spells incompatibility symmetrically.
- Charged Spells' extra boon-only credit is still incomplete. A direct pool
  increase was rejected because the shared spell-point formula subtracts two
  normal drawback points per boon; it cannot allocate different credit types.
  Numerical behavior remains unchanged and the description now states the gap.
- Added three offline tests and live controller assertions. Both power gates
  passed in `build/pcgen-spheres-ocyio46v`. New choices are exercised and refunded
  in each gate; the saved character still uses the legacy fixture choices.
- The first full build failed because `spheres_power_life.lst` lacked the
  Invigorate mechanics already present in the current generator and tests.
  Comparison identified this as the only stale generated LST. Ran the existing
  generator; all 55 deterministic files now match. No new Life rules were designed.
  The existing Java Life harness has no Python runner here, so no new live Life
  verification is claimed.
- Final full build passed: 108 offline dataset tests, profile and candidate
  checks, 655 scenario checks and 21,147 engine regression checks. Package
  structure and deterministic catalog checks also passed.
- External Ultimate Spellcrafting review confirmed that the existing compiler
  uses the published feat, complexity table and minimum-cost convention. No
  replacement Spellcrafting system was introduced.

The full content backlog remains open. Next implement separate boon-only credit
accounting with allocation/refund tests, then expand traditions from pinned
Ultimate sections. Alternate racial traits and prestige classes still require
source inventories and adapters to existing PCGen mechanisms.

## Continuation: implemented work (supersedes older boundaries above)

- Charged Spells has separate boon-only accounting and refund assertions.
- Expanded casting records and feat prerequisite recognition; added the repeatable
  Drawback Feat boon using the existing FEAT category and prerequisite engine.
- Added 50 named martial traditions with fixed grants, restricted choices,
  discipline filtering and fixed-package accounting. All currently use the
  Conscript tradition slot. Remaining named traditions and other class eligibility
  are still open; cataloged Equipment talents remain partially mechanical.
- Five alternate racial traits reuse upstream replacement FACTs; Tempestarii
  has independent prestige progression. These are not full racial/prestige coverage.
- Prestige source inventory now distinguishes `spheres-archwizard` from the
  unrelated conventional `archwizard`; Alternate Justicar was also snapshotted.
- Latest full build passed 122 offline tests, profile/candidate checks,
  655 scenario checks and 21,147 engine checks before the final discipline-choice
  expansion. Focused and live verification of that expansion follows separately.

The entire backlog is not complete. In particular, aligned-class advancement,
advanced/legendary talents, remaining persistent feat/trait/class effects,
named casting traditions and Spellcrafting lifecycle work remain open. Do not
interpret imported source snapshots or descriptions as implemented mechanics.

### Further lifecycle verification and racial expansion

- Spellcrafting save and reload both pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-zw77iteh`, including
  acquisition, forgetting/relearning, prerequisite loss, deciphering retention,
  book access loss, and missing-talent mishap counts. The initial outer timeout
  was insufficient; the full runner completed successfully.
- The racial generator now emits eleven reviewed replacements, including
  Halfling Clever Combatant and Half-Orc Brutally Trained/Trained Berserk.
  Half-Orc replacement FACT names correctly use upstream's `HalfOrc` prefix.
- Added Iron Breaker Style without granting an unlisted Equipment sphere or
  its free talent. It uses the same restricted choice pools as other traditions.
- Added racial live controller cases for default-trait removal/restoration,
  free sphere grants, refunds, and persistence. Do not regenerate campaign data
  while a live PCGen process is loading: an initial concurrent run encountered
  mixed old categories/new abilities and was rejected by the log validator.
  Clean reruns use immutable generated inputs.
- Clean save/reload gates passed for martial traditions in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-sct6smaz`, Halfling in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-x83kreav`, and Half-Orc in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-2lzbnren`.
- The full build passes after these changes, including the existing scenario
  and engine regression suites. This does not close the remaining content gaps.

### Conditional martial branches

- Added Bushido Warrior, Imperialist, and Knightly Arts, bringing the named
  martial generator to 54 of the 66 pinned traditions. Their Beastmastery
  branches grant Ride and consume its free package slot; other branches do not.
  Dedicated branch abilities prevent independently purchased Beastmastery from
  activating a tradition's Ride grant.
- Seven martial generator tests pass. Live selection, package refunds and
  save/reload pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-0ui7j8kz`.
- The live parser rejected ABILITYLIST on parent categories during development;
  the generator now emits that filter only for child categories. The corrected
  campaign passed both live gates. Earlier timed-out runs are not counted as passes.
- Added Free Runner with Run and Leap fixed packages, one remaining package
  choice from Expanded Training, Wall Stunt and a restricted Athletics talent
  choice. It grants no Equipment sphere. Named coverage is now 55 of 66.
  The expanded live save/reload gates pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-a2l6wo4r`, including
  package refunds. The full build passes 126 offline tests, 655 scenario checks,
  21,147 engine checks, and profile/candidate checks after this change.
- Added Highlander with linked sphere/talent branches: choosing Scout opens
  only the Scout talent pool; choosing Dual Wielding opens only its talent pool.
  Branch removal refunds that pool. Coverage is now 56 of 66 named traditions.
  Eight martial tests and the full build (127 offline tests) pass. Live save and
  reload pass in `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-9h74bj7z`.
- Added Janjaweed's mutually exclusive paired branches: two Beastmastery
  talents or both Barrage and Sniper, with the fixed Ride package. Coverage is
  now 57 of 66 named traditions. Nine martial tests, 128 full-build offline
  tests, and the scenario/engine suites pass. Live save/reload, both branches,
  and pool/grant refunds pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-8kxbtyn9`.
- Added Elf and Half-Elf Dreamless Sleep using the upstream Elven Immunities
  replacement FACT. Somnambulance accepts this published racial exception for
  its second purchase without granting Scout. Its counters are defined on the
  racial option so they work without the base sphere. Thirteen reviewed racial
  replacements are now generated. Live Elf selection, first-rank accounting,
  prerequisite loss, default-trait restoration and save/reload pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-bscl460e`.
  The full build passes 129 offline tests plus the scenario and engine suites.
- Added Embodiment's substance choice and single-boon limit using the existing
  casting boon pool. Conditional material interactions remain published rules,
  not a global caster-level modifier. Eight casting tests and the full build
  (130 offline tests) pass. Casting save/reload and campaign parsing pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-4a79m0f8`; this gate does
  not yet drive Embodiment's free-text chooser.
- Added Wandering Martial Artist's discipline-or-Improved-Unarmed-Strike branch
  and Athletics-or-Gladiator choice, reusing the existing feat. Its explicitly
  granted Force Redirection Technique remains tagged legendary and cannot leak
  into basic-talent choice lists; its conditional AC substitution is sheet text,
  not an unconditional bonus. Named coverage is 58 of 66. Ten martial tests,
  the full build (131 offline tests), and live martial save/reload pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-6ody3895`.
- Added Elven Duelist with two Finesse Fighting ranks. Automatic grants are
  deduplicated and its second rank contributes to the existing repeat counter;
  live tests reject a third rank and verify full refunds without paid-pool use.
- Added Tattooed Warrior using the existing Dragon’s Tattoos and Zodiac Tattoos
  feats and level-scaled ranks restricted to Craft (Tattoos). Added that missing
  Core-compatible skill record after the live parser identified the unresolved
  reference. Named martial coverage is now 60 of 66, not mechanically complete:
  tattoo enchantment effects still use the existing feats' partial implementation.
  Twelve martial tests and the full build (133 offline tests, 655 scenarios and
  21,147 engine checks) pass. Corrected martial save/reload gates pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-p1zex9zc`.
- Rechecked feat-based Spellcrafting acquisition, prerequisite loss, book access,
  missing-sphere mishaps and repertoire refunds in live save/reload gates at
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-r5fi93a2`. The earlier
  timed-out run is not counted as a pass.