# Implementation log

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