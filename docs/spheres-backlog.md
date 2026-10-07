# Spheres continuation backlog — September 29, 2026

Current measured status and corrections are in `spheres-current-status.md`.
The deterministic record-level inventory is `spheres-coverage.json`. Dated
sections below are historical and must not be read as a single current snapshot.

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

### Feat-granted casting choices — September 30 continuation

- Basic Magic Training now exposes the existing casting-ability and custom
  casting-tradition selectors when no spherecasting class supplies their pools.
  The selectors qualify by the existing casting feature, rather than requiring
  class spell-pool levels. No parallel tradition or casting system was added.
- Corrected the earlier Advanced Magic Training class exclusion to use all
  spherecasting spell-pool levels rather than only Incanter levels. Offline
  regression coverage exists. Armorist 4/Fighter 6 live save/reload now passes in
  `build/pcgen-spheres-nbfn01kr`: Advanced Training adds three caster levels and
  six magic-skill-bonus points, leaves spell points unchanged, rejects Basic
  Training, and refunds cleanly. Existing class selector allowances remain one.
- 21 feat tests, nine tradition tests and 34 Spheres tests pass. Live Might feat
  save/reload passed in `build/pcgen-spheres-52ihoak9`, including selector grants,
  refunds and prerequisite loss. Those initial gates exercised then removed the
  selectors. The expanded gate actually persisted both selectors and passed
  save/reload in `build/pcgen-spheres-jsk3a75f`. Generated feat/tradition checks
  and package structure checks also passed.
- Basic Magic Training's required exchange for Extra Magic Talent when gaining
  a spherecasting class is not automated. Do not interpret this fix as complete
  multiclass lifecycle support. Other outstanding content remains open.
- Full build after these changes passed 150 Python tests, profile/candidate
  suites, 655 scenario checks and 21,147 engine checks.

### Configurable Alternative-Brew continuation

Final verification for this continuation: the complete build test command passed
147 Python tests, profile/candidate suites, 655 scenario checks and 21,147 engine
checks. These tests cover the implemented slices, not all requested content.

- Added a one-choice Alternative-Brew selector over existing Core/Spheres Craft
  and Profession skills. No bonus talent is awarded. It replaces Alchemy's
  granted Craft ranks, supplies associated ranks to existing DC/capacity and
  prerequisite formulas, and excludes Field Medic's fixed Heal exception in
  both directions. Removing Alchemy disables retained skill-rank grants.
- Live inspection exposed that PCGen skillinfo can return zero for skills not
  in the character's displayed skill list despite granted bonus ranks. The
  associated-rank formula now preserves the known training minimum with max,
  rather than adding it twice. No upstream engine change was made.
- Two focused tests and eighteen catalog/nineteen feat tests pass. Field Medic
  regression save/reload passed in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-rb36oua1`.
  Separate configurable Craft-to-Profession choice/refund/persistence checks
  passed in `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-7zccb50n`.
- GM permission for selecting/changing/removing the drawback remains explicit
  tabletop approval, not an invented automatic qualification. Additional-source
  and user-created skills are not automatically discovered by this compiler.

### September 30 Liturgist and configurable weapon training

- All 66 named martial traditions now have generated records. Liturgist grants
  Custom Training, Leadership with Followers, the existing Basic Magic Training
  feat, a Death/Fate/Life choice, and Base Of Operations or an Equipment talent.
  Its restricted magic choice replaces the feat's ordinary free sphere allowance.
  This is catalog coverage, not certification of every tradition interaction.
- Custom Training has a repeatable five-point weapon allowance using actual Core
  proficiency keys. Simple/martial weapons cost one; exotic weapons cost two,
  including those tagged both Martial and Exotic. Choices are unique. Retained
  choices cease granting proficiency when the parent talent is removed.
- Two Custom Training, seventeen martial and eighteen catalog tests pass.
  Live save/reload passed in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-1qyn5lo2`, including actual
  proficiency grants/removal, duplicate rejection, weighted costs, additional
  talent purchase/refund, restricted magic allowance and paid-pool isolation.
- Still open: Liturgist's deity/philosophy-favored weapon constraint is displayed
  but not mechanically enforced. Custom Training lists Core weapons, not arbitrary
  additional-source proficiencies. Basic Magic Training multiclass limitations
  remain. General Alternative-Brew configurability, companion/transformation
  builders, class mechanics and other listed backlog areas remain incomplete.

### September 30 Field Medic continuation

- Added Field Medic with its fixed Formulae package/Salve, Scout and Fast Draw,
  plus a configurable Alchemy-or-Scout talent choice. Alternative-Brew's published
  Heal exception replaces granted Craft (Alchemy) ranks and drives Alchemy DCs
  through an associated-ranks variable. Unrelated crafting prerequisites are not
  changed; directly Alchemy-required feat prerequisites use that variable.
- Added the missing general Formulae package free-talent pool, restricted to
  formulae. Field Medic's Salve consumes that allowance. Toxins now require the
  Poison package; formula capacity, crafting batch size and poison persistence
  use associated ranks. Crafting actions and material resolution remain tabletop.
- Sixteen martial tests, eighteen catalog tests and nineteen feat tests pass.
  Live level-1 grants, Heal/Craft substitution and restoration, formula capacity,
  toxin rejection, free formula selection/refund, paid-pool isolation and
  save/reload pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-bw_ysoks`.
- Named tradition coverage is 65 of 66; Liturgist remains open. Alternative-Brew
  still needs its general configurable Craft/Profession selector; this specific
  published Heal exception is not represented as completion of that subsystem.

### September 30 Ace continuation

- Added Ace with a configurable Fly/Run/Swim starting package, its published
  Athletics talent choice, and Driver's Ace Pilot grant. No Equipment sphere
  or additional unrestricted starting package is granted. Driver suppresses
  Athletics package skill ranks without removing package ownership; Ace Pilot
  continues to grant Profession (Pilot) ranks through its existing implementation.
- Fifteen martial tests and eighteen catalog tests pass. Live level-1 selection,
  paid-pool isolation, package-rank suppression, Pilot ranks, removal and
  save/reload pass in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-aq7m7973`.
  The earlier level-10 attempt timed out during loading, not an assertion pass.
- Named martial coverage is 64 of 66; Field Medic and Liturgist remain open.
  This does not complete configurable sphere drawbacks, companions,
  transformations, feat prerequisites, or the class-mechanics backlog.

### September 30 resumed verification and martial work

- The expanded Equipment active-stance persistence test now passes both save and
  reload in `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-wwl5_wp1`.
  This supersedes the pending status recorded below, without treating the earlier
  timeouts as passes. Offensive Style and Dagger Dancer survive persistence;
  removing them removes their associated feat qualifications.
- Added Expedition Spotter, Sergeant and Hacker with their published choice
  pools and drawback grants. Named martial coverage is now 63 of 66. Remaining
  names: Ace, Field Medic and Liturgist. This is not full mechanical coverage.
- Dismantler grants Trap Finder; Squad Leader grants Squad and Sergeant fixes
  the Cohort package. Hacker fixes Remote Control as its first gadget, consumes
  the existing free gadget slot and grants the existing Remote Hacking feat.
  Unsecured excludes Improved User Interface, including rejection of Hacker
  when the incompatible talent is already present. No gadget-only saving throw
  penalty is incorrectly applied to the character.
- Fourteen martial regression tests pass, as do deterministic generation and
  campaign structure checks. Live controller save/reload passed in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-ssbhcxz8`, exercising
  Hacker's grants/refunds and incompatibility, Spotter's grants/refunds, and
  Sergeant's package, equipment choice spend, paid-pool isolation and persistence.
  Trap placement, recruitment restrictions and gadget control resolution remain
  table effects. Configurable sphere drawback selection beyond these grants,
  transformation/companion construction and remaining class mechanics are open.

### September 30 continuation in progress

The latest acceptance requirement is configurable traditions, spells,
transformations and companions, not a collection of presets, with complete
class mechanics and prerequisite/associated-feat enforcement. Existing custom
spell definitions already accept user-supplied recipes; transformation and
companion construction still need inspection and implementation. No completion
claim is made for them.

Investigated the pinned catalog and PCGen's existing `SERVESAS` implementation.
Direct associated-feat equivalences were absent from the catalog generator.
Adding reviewed direct Core associations through that existing token rather
than automatically granting the real feats and their bonuses. Package-,
weapon-, stance- and repeated-rank-dependent associations, and prerequisite
waivers on dependent feats, remain distinct work. Initial patch application
failed without changing files; the corrected patch was applied. Tests and
live validation recorded below.

- Implemented 36 reviewed direct Core feat associations through `SERVESAS`.
  Four focused offline tests verify source declarations, loaded targets,
  no automatic feat-effect grants, and guarded stance choices.
- Versatile Fighter now has three selectable active stances in a one-slot
  existing PCGen ability pool. Each supplies its published feats only while the
  talent remains present; removing the talent revokes benefits even if the
  stale stance selection has not been deleted. This does not implement action
  timing or the conditional on-hit riders, nor cross-sphere stance exclusion.
- Equipment live save/reload passed in
  `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-20gw1rum`.
  Checks exercise `PREFEAT` and upstream `PREABILITY` equivalence, removal,
  refunds, inactive/active stance effects and prerequisite-loss revocation.
  The runner now supports separate save/reload phases. Initial 50-second runs
  timed out; inspection showed the second reached character saving, not a
  failed assertion. Separate phases with a bounded 95-second JVM limit passed.
- Post-change verification passed all 137 offline tests across the 13 suites.
  The aggregate build's 120-second wrapper expired during traits; traits,
  racial and prestige suites were subsequently run separately and passed.
  Profile/candidate checks, 655 scenario checks and 21,147 engine checks also
  passed separately. Generated-file consistency, Python compilation and package
  structure checks passed. A category-count assertion initially failed because
  of the newly added stance category; it now explicitly checks that category's
  non-editable zero baseline pool rather than omitting the new category.
- Expanded the Equipment fixture to save an active Offensive Style and Dagger
  Dancer, then assert their feat qualifications after reload and remove them.
  **This expanded persistence fixture is not yet verified.** Later runs exceeded
  their time bounds during loading/selection without reaching a saved character.
  Evidence: `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-wwl5_wp1`.
  Host process inspection showed concurrent C++ compilation; that is a possible
  contributor, not a proven cause. No unrelated processes were stopped.
  The earlier successful gates exercise stance transitions and refund behavior,
  but did not persist an active stance across processes. Do not conflate these.
- The runner skips compilation only when both harness class files are newer
  than their source files. Equipment-only fixtures now use Conscript 10;
  other sphere resource-scaling fixtures remain level 20. The next validation
  step is the expanded Equipment save/reload fixture, not another feature claim.
- Complete class mechanics, configurable transformations/conjuration, remaining
  traditions and other listed areas are still open; these results do not
  certify them. No eight-hour unattended execution or full completion claim is
  supported by this session's evidence.

| Area | Current boundary | Completion work |
| --- | --- | --- |
| Casting traditions | Original fourteen choices plus weighted Extended Casting and second-tier Extended/Somatic choices, three boons | Remaining weighted/repeated drawbacks, incompatibilities, other drawbacks/boons, named traditions, sphere-specific grants and casting modifier effects |
| Martial traditions | Custom Conscript only | Source-named traditions, other eligible classes, proficiency trades and alternative structures |
| Spellcrafting | Existing feat-driven recipe and repertoire system | Source-backed timing, advanced prerequisites when supported, temporary talents, inventory access and forgetting lifecycle |
| Feats | Catalog and reviewed prerequisite/effect compiler | Resolve remaining prerequisites using loaded systems and audit persistent effects individually |
| Traits | Shared PCGen Traits pool | Remaining prerequisites/effects, category and prerequisite-loss checks |
| Alternate racial traits | Not loaded by this campaign | Source inventory, reuse upstream racial replacement categories, enforce replacement conflicts and refunds |
| Spheres | 53 sphere catalogs plus reviewed mechanics | Legendary talents, persistent effects, packages, companion/equipment integration |
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
legendary talents, remaining persistent feat/trait/class effects,
named casting traditions and Spellcrafting lifecycle work remain open. Do not
interpret imported source snapshots or descriptions as implemented mechanics.
Advanced talents are now imported, but each still needs per-talent mechanical
automation; only their source prerequisites are compiled.

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