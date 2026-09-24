# Implementation log

## 2026-09-23 — Thin Conscript class

Added separate Conscript class/categories/features to the existing campaign,
without changing Incanter data. Added class skills and practitioner choices,
talent/feat progression, specialization forfeiture and ten bounded specialization
implementations. External talents/traditions/sphere specializations are explicitly
manual records, not claimed sphere automation. Added PCGen controller round-trip
and refund coverage and all-level Python fixture tests. Exact evidence and limits:
`/bigdisk/programming/pathfinder1e/docs/conscript-class.md`.

## 2026-09-23 — Thin Incanter class completion

Superseded the extended-source completion contract with the user's class-only
scope. Preserved existing class/campaign keys and optional data. No new spheres,
domains, bloodlines, favored-race options or external subsystems were added.
Existing class data already supplies the thin chassis; added a dedicated real-PCGen
acceptance runner for BAB/saves, casting/resource progression, all six specialization
budget tiers, bonus feat effects, class grants, save/reload and post-reload refunds.
Verified levels 1/5/10/20 across INT/WIS/CHA and budgets 0–5, plus existing feat,
specialization, low-INT and Core isolation gates. Exact cases and timeout exclusions:
`/bigdisk/programming/pathfinder1e/docs/incanter-class.md`.

## 2026-09-23 — Orc Movement Burst favored choice

Added the Orc favored-class choice for the Destruction specialization's
Movement Burst, distinct from Halfling's choice. Two selections add one daily
use; eligibility requires the Orc race and the granted ability. Controller
gates cover prerequisites, race isolation, accumulation and removal; a
save/reload gate checks six selections, three added uses and the free
Destruction sphere. The Orc fixture's Intelligence penalty reduces its casting
modifier, spell points and Destruction DC independently of this reward.
Other eligible Orc specialization and domain abilities remain unimplemented.

## 2026-09-23 — Halfling Movement Burst favored choice

Added a separate Halfling favored-class reward for the Destruction specialization's
Movement Burst (3 + casting modifier uses/day). Two selections add one use; the
reward requires the granted ability and does not change Channel Energy uses.
PCGen controller gates verify availability, fractional accumulation, removal and
Channel Energy isolation; a specialized character save/reload gate verifies the
chosen ability, six reward selections, three extra uses and the free Destruction
sphere. The existing Channel Energy choice and Destruction gate remain unchanged.
Other eligible Halfling abilities and the remainder of Incanter are incomplete.

## 2026-09-23 — Favored-class regression follow-up

PCGen's `getTotalBonusTo` reports a double; corrected the Aasimar gate's
Spellcraft baseline declaration and reran its live controller gate. The
Half-Orc bloodline-strength and Halfling channel-use gates also pass locally.
The broader PCGen run encountered a startup timeout on its first fixture;
that run is not acceptance evidence. The remaining class options and
specialized round-trip checks remain incomplete.

## 2026-09-23 — Sword Birth edition-boundary correction

The Ultimate Armorist explicitly permits repeat Combat Feat trick choices; the
Lingchi prohibition quoted earlier belongs to its Original section. Restored
repeatable Combat Feat and added a level-20 two-choice pool gate. Removed
Finesse, which is only listed in the Original Armorist section.

## 2026-09-23 — Admixture Adept edition-boundary verification

The Ultimate Admixture Adept paragraph grants Admixture without an alternative;
the already-owned alternative appears in the Original paragraph farther down
the same wiki page. The existing Ultimate-only data should not import that
Original rule. This corrects the conflicting intermediate audit note.

## 2026-09-23 — Gnome favored Destruction DC and gate repair

Fixed the PCGen controller gate's Spellcraft baseline type (PCGen reports a
double) and verified the Aasimar, Tiefling, Elf, Dwarf and Human gates again.
Added a Destruction-specific Gnome favored-class bonus with a six-selection
threshold, prerequisite, removal and no general caster-level change. The live
Gnome gate and specialized PCGen save/reload pass. Other Gnome sphere choices and the remainder of the class
are not implemented; see `incanter-completion-audit.md`.

## 2026-09-23 — Tiefling favored concentration variable

Added the Ultimate Tiefling +1/2-per-selection favored-class option. Local
PCGen controller gates check race and favored-class eligibility, fractional
accumulation, refund and save/reload of a concentration-check variable based
on caster level and the selected casting ability. PCGen does not yet execute
Spheres concentration checks using that variable; it is not a certified
end-to-end concentration feature. Incanter remains incomplete.

## 2026-09-23 — Admixture edition boundary

The Ultimate section grants Admixture without an already-owned replacement;
the alternative Destruction talent appears in the Original section. Do not
import the Original alternative into Ultimate. The full pool/use interaction
still needs acceptance coverage. "Master of Creation" is also the name of a
level-8 Ultimate Creation specialization power, not a separate Ultimate
specialization; the Original section must not be used to infer one.

## 2026-09-23 — Aasimar Incanter favored Spellcraft bonus

Added the Ultimate Aasimar +1/2 Spellcraft per favored-class reward, with
race/favored-class prerequisites and a cumulative bonus derived from the
selection count. The PCGen `aasimar-favored` gate exercises six selections,
the bonus at odd and even counts, wrong-race rejection, and removal; the
`aasimar-favored-save` gate checks the six picks and Spellcraft bonus after
PCGen saves and reloads the character. The fixture loads PCGen's existing
Aasimar support campaign; it does not add a
homebrew Aasimar race. Incanter is not complete.

## 2026-09-23 — Partial favored class bonuses; local PCGen validation

Added Human and Half-Elf Incanter favored class bonus options using the
existing per-level favored class reward pool. Six selections grant one magic
talent, and removing selections refunds it. Elf's six selections grant a
metamagic feat in a separate feat pool; tested the Extend Spell choice and
its removal without spending a general feat. Separate race gates prevent a
Half-Elf from taking the Human version despite PCGen matching Human as an
ancestry. Human, Half-Elf and Elf race gates pass against the locally built
pinned PCGen JAR; the Human bonus also passes specialized save/reload with
the additional talent. A Dwarf item-creation feat reward now passes its
six-selection pool and removal gate, but the actual item-creation feat choice
is not yet validated: Core feats use spellcaster prerequisites not currently
mapped to spheres casting. Other favored class bonuses remain unsupported;
Incanter remains incomplete.
The full controller gate suite and Sword Birth specialization save/reload
have passed using the vendored Java 16 runtime and local PCGen build.

## 2026-09-22 — Sword Birth ordinary arsenal trick and PCGen save/reload

Added the ordinary Armorist Combat Feat trick to Sword Birth using its own
combat-feat pool. Added a contract test and controller gate for the feat
pool grant, isolation and refund. Built the local pinned PCGen JAR with the
vendored JDK 16 and ran the Sword Birth gates at levels 1, 5 and 20. A new
specialized Sword Birth save/reload check verifies active specialization,
Combat Feat and the chosen Improved Initiative bonus feat survive loading.
Finesse was checked against the Armorist page but belongs to Original, not
Ultimate; it was not retained in the Ultimate Sword Birth list.
The full ordinary Armorist trick catalog is still unsupported.

## 2026-09-22 — Sword Birth Extra Arsenal Trick increment

Added repeatable Extra Arsenal Trick for active Sword Birth from level 5,
when it first gains the arsenal trick class feature, with one arsenal
trick pool grant per feat and no Incanter bonus-feat eligibility. Added data
contract and targeted controller gate for qualification, grant and removal.
The PCGen sword1, sword5 and sword20 gates now pass locally; the class remains incomplete.

## 2026-09-22 — Incanter completion audit started

Added `docs/incanter-completion-audit.md` to distinguish Ultimate and Original
wiki rules, enumerate the missing sphere specializations/sub-specializations,
and establish mechanical plus save/reload completion gates. User confirmed
that all normal-game Ultimate wiki options, including tagged variants, are in
scope. Removed the fixed ten-LST package limit so additional Incanter data
sources can be validated without disabling duplicate/missing-source checks.
No new Incanter mechanics or PCGen integration claim. Local Python
checks are not a substitute for the ThinkPad-only PCGen controller gates.

## 2026-09-22 — Current Spheres handoff refreshed

Updated `/bigdisk/programming/pathfinder1e/docs/spheres.md` with current status
for Incanter, Conscript and Power/Might sphere implementation. Added the explicit
remaining checklist required before Incanter can be called complete. Documentation
only; no data or tool behavior changed.

## 2026-09-22 — Destruction specialization and Sword Birth data

Added Destruction specialization grants/scaling and Sword Birth arena data,
enhancement budgets, trick pool and ten Lingchi-specific tricks. Direct PCGen
gates passed at Destruction levels 1/3/8/20 and Sword Birth levels 1/5/20.
Two new first-party data-contract tests pass. Full Incanter completion remains
outstanding, including ordinary arsenal tricks and arena property choices;
see the current handoff for explicit implementation limits. No upstream changes.

## 2026-09-22 — Incanter Core domains, Core bloodlines and Admixture

Added 33 domain and ten power-only bloodline adapters plus Admixture Adept and
its bonus talent. PCGen controller checks passed for Air/Fire together and
Aberrant/Admixture at levels 1 and 20 on the ThinkPad. Generator consistency and
forbidden-grant regression tests added. No upstream or toolchain changes.
The full class remains incomplete; see the explicit remaining list in spheres.md.

## 2026-09-22 — Incanter channeling, healing, familiar and activation

Added Channel Energy, Lay on Hands, Merciful Healer and standard Familiar data,
reusing core mercy and familiar data where applicable. Separated specialization
purchase from activation, including the existing Master of Mysteries, to enforce
level-based activation limits. Actual PCGen gates passed at levels 1, 3 and 20.
Remaining class omissions and the Master of Mysteries compatibility change are
listed in `/bigdisk/programming/pathfinder1e/docs/spheres.md`. Class is not complete.

## 2026-09-22 — Incanter bonus feats implemented

Implemented class bonus-feat pool, repeatable Extra Magic Talent/Extra Spell Points,
specialization-cost formula and first specialization (Master of Mysteries).
Real PCGen controller tests passed at levels 1 and 20, including grant/removal,
pool isolation and overspend rejection; level 1 tested specialization purchase,
forfeiture and removal. This is implemented data, not completion of Incanter.
See `/bigdisk/programming/pathfinder1e/docs/spheres.md` for remaining class work.

## 2026-09-22 — User narrows implementation order

Finish Incanter, then Conscript, then Power/Might spheres, then remaining classes.
Defer multiclassing until all classes are implemented; exclude Guile. Log and
skip disproportionately complex spheres rather than blocking catalog progress.
Updated the authoritative handoff in `/bigdisk/programming/pathfinder1e/docs/spheres.md`.
This is a scope/order update, not new implemented character mechanics.

## 2026-09-22 — Incanter progression to 20 and mental casting choices

Extended the existing prototype class key to level 20 without changing the
established high-caster progression formula. Added INT/WIS/CHA selection data
with an INT compatibility fallback and a single-choice pool. Generated PCG
fixtures cover levels 1–20 with independent talent-budget table expectations.
Actual PCGen level20/WIS18 and level3/CHA18 export/save/reload checks passed.
All three selection/isolation gates passed; 11 unit tests and the existing
profile/candidate/655 scenario/21,147 regression checks passed. No toolchain or
upstream Java modifications. Bonus feats, specializations, traditions and the
remaining Destruction catalog are still missing; this is not class completion.


## 2026-09-22 — Immediate Spheres selection/isolation gates complete

Added `/bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py` and a
first-party Java driver exercising PCGen's actual CharacterAbilities controller.
All three talents reject missing Destruction and accept its presence; duplicate
attempts for the sphere and all three talents reject without spending. Removal
refunds points and revokes prerequisites. The same core Fighter fixture has
identical checked exports/state with Core alone and with Spheres loaded, gains no
Spheres resources/abilities and cannot select Destruction. All three gates passed
on the ThinkPad. No upstream Java, JDK, LST rules or broad tooling changes.
Exact coverage, evidence and command: `/bigdisk/programming/pathfinder1e/docs/spheres.md`.
Final gate rerun passed (selection `pcgen-spheres-l2ptitwa`, Core
`pcgen-spheres-6d6oq67t`, augmented `pcgen-spheres-ej_yya8_`). Ten tool tests,
package checks and all existing profile/candidate/655 scenario/21,147 regression
checks passed. The combined smoke rerun hit the outer 120-second command budget
after passing level-1/INT18; remaining cases were split into individual bounded
runs and both passed, including save/reload. This was not a reported gate failure.


## 2026-09-22 — Three Spheres fixtures and actual PCGen save/reload

Added level-2/INT18 and level-1/INT7 PCG fixtures and an `all` smoke option.
The Java batch bridge now checks that both selected talents exist and consume
exactly two points, then saves through PCGen. A fresh Java process reloads the
saved PCG and repeats export and selection checks. All three cases passed on the
ThinkPad; paths and results are in `/bigdisk/programming/pathfinder1e/docs/spheres.md`.
No upstream tooling, private JDK, LST rules or dice-pool engine changes.
This closes calculation-fixture and persistence checks, not the entire Spheres
plan. Prerequisite/duplicate enforcement and core-only isolation remain next.

## 2026-09-22 — Targeted Spheres export passes; tooling detour stopped

User-approved workflow ignores broad upstream tests/packaging/GUI as gates.
Added one first-party PCG fixture, Python smoke wrapper and minimal Java batch-API
bridge. Fixed only direct-path setup issues (CLI output validation, config basename,
preview path, PCG game-mode name). No upstream source or rules changes.
Actual PCGen exports matched all ten incanter1-int18 expected values twice; latest
evidence: `/bigdisk/programming/pathfinder1e/build/pcgen-spheres-xe_b0j3u`.
Nonzero DEFINE deprecation warnings remain, with no SEVERE/LSTERROR messages.
Six tool tests passed. The private JDK/download patch are retained, ThinkPad only.
Current command, limitations and next work: `/bigdisk/programming/pathfinder1e/docs/spheres.md`.
Do not fix `datatest` next; extend only the targeted fixtures/selection checks.

## 2026-09-22 — ThinkPad test cache recheck; discovery mismatch

Approved offline DataLoadTest retry passed the earlier dependency-resolution
failure but failed at `:datatest`: no tests found. Test compilation tasks were
UP-TO-DATE. Compiled DataLoadTest exists and uses Jupiter annotations, while
`datatest` lacks `useJUnitPlatform()`. Next fix is test discovery configuration,
not the JDK or additional Gentoo packages. No test cases ran. Full evidence:
`/bigdisk/programming/pathfinder1e/build/pcgen-datatest-recheck.log`.
Details and next step: `/bigdisk/programming/pathfinder1e/docs/spheres.md`.
No upstream code, system setup, JDK or download patch changed in this recheck.

## 2026-09-22 — PCGen data-test harness blocked by test dependencies

Inspected the pinned upstream data-load and character-export test harnesses and
attempted offline `datatest --tests pcgen.persistence.lst.DataLoadTest` with the
ThinkPad private JDK and both download tasks excluded. Failed in 25s at
`:compileSlowtestJava` on missing `:testCompileClasspath` artifacts; no tests ran.
The eight reported coordinates and exact command are recorded in
`/bigdisk/programming/pathfinder1e/docs/spheres.md`; full local output is in
`/bigdisk/programming/pathfinder1e/build/pcgen-datatest.log`. Compilation remains
verified; this is a separate test dependency gap. Plugin JARs and the JAR task ran
with duplicate-entry warnings, not a validated distribution. No Spheres data
changes or integration tests were added, and no online downloads were attempted.


## 2026-09-22 — ThinkPad PCGen offline compile verified

Re-ran the patched, compile-only PCGen command with the private ThinkPad JDK at
`/home/danbo/.local/lib/jvm/temurin-16.0.2+7`, `--offline`, `--no-build-cache`,
`--rerun-tasks`, explicit `org.gradle.java.installations.paths`, auto-download
disabled and both eager download tasks excluded (`-x downloadJRE -x downloadJavaFXModules`).
Observed `BUILD SUCCESSFUL in 43s`; `:copyMasterSheets` and `:compileJava` executed,
and `compileJava` printed `[--enable-preview]`. This supersedes the earlier Java 16
toolchain blocker for the ThinkPad only. It does not verify upstream tests,
application startup, packaging, Spheres data loading, talent selection, save/reload
or character export. Current details and exact command: `docs/spheres.md`.

## 2026-09-22 — Spheres phase, first prototype (not accepted integration)

The new user request activates `planning and docs/spheresplan.md` while preserving
the dice-pool baseline. Added first-party PCGen data under `data/spheres`, an
export template, hand-calculated expectations and Python package/export checks.
Four new tool tests and all existing first-party tests passed. No upstream Java
changes were made. At this point, offline upstream compile still failed on the
missing Java 16 toolchain after plugin configuration progressed; the later
ThinkPad-only entry above records the compile recovery. Actual data loading and
character exports remain unverified; static tests are not a substitute. Full
scope, source references, limitations and next acceptance steps:
`/bigdisk/programming/pathfinder1e/docs/spheres.md`.
Spheres of Might content awaits the magic prototype gate in the supplied plan.


## 2026-09-22 — README accepted-model summary

Added a concise dedicated README section for the accepted `tn8-8-4` model: roll
final modifier in d10s, minimum 1 die, 8+ succeeds, AC/DC maps by
`ceil((AC or DC - 8) / 4)`. The section includes the required-success table and
the verified aggregate profile/difficulty probabilities from the profile report.
README was updated after implementation and working-doc updates.

## 2026-09-22 — Absolute profile diagnostics

Added opt-in `scenarios --report profiles` with absolute probabilities, median,
nearest-rank p10/p90, range and d20 context. Existing type/level filters provide
breakdowns without altering the scenario corpus. No model or profile changes.
New ProfileTest and all prior suites passed. Ran reports for all three TN8 models;
inspected TN8-8-4 type/level slices. Findings: pooled means hide declining LOW
participation with level and major type differences in TYPICAL competence.
Current handoff and measured tables: `docs/profile-analysis.md`. Investment-tier
definitions remain unresolved; no speculative target-band acceptance tests added.

## 2026-09-22 — Opt-in TN8 experiment

Added named 1:1 bonus/dice candidates (offset/divisor 7/4, 8/4, 10/5), preserving
the baseline and five-argument ConversionModel constructor. Minimum dice is now
explicit configuration; the candidates use the provisional one-die floor.
Added direction/parity diagnostics without changing the existing CSV schema.
All candidate tests, 655 scenario checks and 21,147 regression checks passed.
Executed all three full-corpus reports and the example attack report. None
consistently achieves the requested curve shape; findings and limitations are in
`docs/tn8-experiment.md`. No take-10/20 mechanics, cancellations or explosions added.

## 2026-09-22 — Scope reset: scenario baseline

The user's latest requirement supersedes the PCGen-first plan: the deliverable is
PF1e d20 versus d10 probabilities across meaningful level/AC/DC scenarios. The
current contract is `docs/scenario-baseline.md`. Earlier blockers below are retained
as history, not active prerequisites. Existing upstream code is preserved, unused.

Implemented `Scenarios` (pure generation/comparison), `ScenarioReport` (table/CSV),
and the `scenarios` CLI. Source-backed equal-CR AC/primary ability DC centers are
separated from explicitly synthetic modifier profiles and configurable difficulty
offsets. No character validity or empirical percentile claims are made. Existing
math and commands are unchanged. The report evaluates one global conversion model
rather than selecting a different best-fit pool for each row.

Verified: 655 targeted scenario checks and all 21,147 original regression checks
pass with warnings-as-errors compilation. Runtime level-5/+11 attack table passed;
full 660-row CSV generated at `build/scenario-baseline-v1.csv`. Deterministic replay
and CSV schema/count are covered by ScenarioTest. No upstream installation occurred.

Default model measured MAE 17.069pp, RMSE 21.607pp, maximum error 51.875pp;
28.18% of cases are within 5pp. These results are evidence that the comparison
tool works, not that the conversion is balanced. Full results are reproducible
with `scenarios --format csv`. Source table values were checked against the PF1e
legacy PRD Monster Creation table. The next useful work is choosing/tuning a model
against this frozen scenario contract, not extending PCGen integration.

## 2026-09-22 — Requirements and investigation

The authoritative supplied specification is `planning and docs/plan.md`; it is unchanged.
The workspace initially contained no implementation or build configuration. Java 17,
Python 3.14 and curl are available; no system Gradle executable was found.

### Constraints

- PCGen owns character construction. Never calculate classes, feats or equipment here.
- First-party code is separate from unchanged third-party archives under `vendor/`.
- Exact mathematics precedes seeded random simulations. Engines perform no I/O.
- Attack/save natural rolls differ from skills. Damage conversion, combat rounds,
  exploding dice and cancelling ones are excluded from the initial implementation.
- Fixed TN6 is the initial conversion model; matching may search other thresholds.
- Synthetic fixtures must never be represented as PCGen-validated characters.
- Original plan remains intact. No upstream licensing files will be edited.

### Evidence and decisions

PCGen 6.08.00RC10 is a deliberately pinned baseline, not a claim about the latest
release. Its upstream build.gradle specifies Java 16, Gradle plugins and external
dependencies. Its Main.java exposes batch export (`-E`, `-c`, `-o`, settings directory)
and `loadCharacterAndExport`. Use exports as the narrow adapter boundary.
Sources inspected locally: the pinned archive's build.gradle and Main.java.
Main.java was also checked against the upstream raw source at that tag.
The command-line arguments are defined in Main.java.

Use Java 17 standard-library-only first-party code with a small Python build driver;
avoid a new dependency manager solely to compile the independent experiment.
Upstream build and dependencies remain a separately verified concern.

### Verification plan

Exhaustive d20 face checks; small-pool enumeration; degenerate probabilities;
seed replay; input rejection; snapshot round trips; matching order; CSV grid and
metrics checks; CLI smoke tests. Attempt upstream build separately and record its
actual outcome. Later stages (real career corpora, critical/pool model fitting,
opposed conversion and damage) must be explicitly tracked if not completed.

### First verification

Java compilation with `--release 17 -Xlint:all -Werror` passed. Initial test run:
21,143 checks passed. Seed 12345 / 100,000 attack checks (+12 vs AC24) yielded
45,041 successes versus analytical probability 0.45.

PCGen archive SHA-256 is recorded in `vendor/manifest.json`. Inspection found
16,524 entries / 216,498,927 unpacked bytes. First safe extraction attempt rejected
upstream's `checkstyle.xml` symbolic link before writing any files. The extractor
was refined to allow only links resolving within the extraction destination,
while retaining Python's data extraction filter and refusing overwrite.

### Integration blocker and handoff

Extraction subsequently passed. The upstream wrapper downloaded Gradle 7.3 despite
`--offline` (that flag controls dependency resolution, not wrapper bootstrap).
Offline task discovery failed on the uncached SpotBugs 5.0.13 plugin. An online,
120-second bounded task-discovery attempt reached project configuration but timed
out. Do not describe PCGen as built or tested. Transitive upstream dependencies and
the Gradle distribution are not vendored; the wrapper used its normal user cache.
No upstream source or LICENSE files were edited.

Final first-party regression run at this point: 21,147 checks pass, including
snapshot round-trip/schema rejection and the full benchmark CSV row count.
Snapshot interchange is implemented; a real PCGen export adapter is NOT implemented.

Next steps in plan order:
1. Resolve/pin upstream build dependencies and Java 16 toolchain, then run upstream
   tests and confirm available Pathfinder integration tasks.
2. Implement and validate a first-party export template or adapter using one real
   PF1e PCG character. Preserve attack modes/iterative bonuses explicitly.
3. Add the real-character/career corpus and character-directory benchmark command.
4. Compare the three modifier-conversion families; current CLI only implements a
   parameterized fixed-target family. Coefficients are experimental, not calibrated.
5. Implement opposed checks, d20 critical distributions and candidate pool critical
   models as separate categories. Damage conversion remains intentionally deferred.

The engine supports complete pool success-count distributions but does not attach
game effects to degrees of success. The initial snapshot is intentionally small:
BAB, CMB/CMD, caster levels and spell DCs remain to be added with actual export evidence.