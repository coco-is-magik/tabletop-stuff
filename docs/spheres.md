# Spheres PCGen prototype — current handoff

## Current workflow: targeted export only (2026-09-22)

Broad upstream `datatest`, `slowtest`, `inttest`, distribution packaging and GUI
checks are NOT prerequisites. Their historical diagnostics below are retained,
but the JUnit discovery issue is deliberately not being fixed. Do not return to
that detour unless a specific Spheres failure requires it. No upstream files were
deleted; unused tasks are excluded from our workflow.

Run this ThinkPad-only check using the already-built PCGen JAR/plugin files:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_smoke.py incanter1-int18
```

Verified twice through actual PCGen batch export. Latest successful output/log:
`/bigdisk/programming/pathfinder1e/build/pcgen-spheres-xe_b0j3u`.
PCGen loaded Core Rulebook and Spheres PF1e - Architecture Prototype, loaded the
hand-authored PCG fixture, and exported all ten values matching expected.json:
talents 4, CL 1, casting modifier 4, MSB 1, spell points 5, Destruction CL 1,
DC 14, blast dice 1, boosted dice 2, range 25. No SEVERE/LSTERROR diagnostics.
Nonzero DEFINE deprecation warnings remain; they did not prevent this export.

The wrapper uses the private JDK and cached JavaFX 16 Linux JARs on the ThinkPad.
It invokes the existing PCGen batch API through
`/bigdisk/programming/pathfinder1e/tools/PcgenSpheresExport.java`, not a replacement
rules engine. Each invocation creates fresh isolated settings/output/logs under
the project build directory, has a 90-second subprocess limit, rejects load errors,
and compares the actual export. It does not invoke Gradle, download dependencies,
package PCGen, run JUnit, or touch personal PCGen settings. The existing JAR is
named pcgen-6.09.06.jar by the pinned source's build metadata despite the RC10 tag.
Rebuild it explicitly if upstream source changes; this wrapper does not rebuild it.

Initial narrow-path failures and fixes: CLI output-file validation rejected a
new output path (use the batch API instead); the config loader required a basename
relative to the isolated working directory; startup required the upstream preview
directory; the PCG format requires `Pathfinder_RPG` even though PCCs use Pathfinder.
All these fixes are first-party wrapper/fixture changes, not upstream patches.

All three calculation fixtures are now implemented. Run them sequentially with:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_smoke.py all
```

Each case now asserts via PCGen that Destruction Sphere and Searing Blast are
present and exactly two talent points are spent. PCGen saves to a fresh PCG file;
a second Java process reloads that saved file, repeats the pool/ability assertions,
and exports the same ten expected values. Each subprocess has a 90-second limit.
Verified on the ThinkPad on 2026-09-22:

| Case | CL | Modifier | Spell points | DC | Evidence directory under project build |
| --- | ---: | ---: | ---: | ---: | --- |
| incanter1-int18 | 1 | 4 | 5 | 14 | pcgen-spheres-3k495989 |
| incanter2-int18 | 2 | 4 | 6 | 15 | pcgen-spheres-lul8z5cj |
| incanter1-int7 | 1 | -2 | 1 | 8 | pcgen-spheres-xkqmz06f |

The hand-authored fixtures leave unrelated character choices unfinished. This is
not a complete Incanter. Interactive prerequisite enforcement, duplicate rejection,
and core-only isolation still require targeted acceptance checks. Those are next,
before traditions, martial progression or catalog expansion; broad upstream tests
remain out of scope. Spheres of Might is not implemented.

Eight first-party tool tests cover fixture coverage, exact selection evidence,
missing/oversized/mismatched-export,
load-error and unsupported-case rejection coverage. These are separate from the
actual PCGen smoke result above.

## Contract (2026-09-22)

The new phase follows `/bigdisk/programming/pathfinder1e/planning and docs/spheresplan.md`.
It supplements, rather than replaces, the locked dice-pool tool. PCGen owns character
construction and formula evaluation. First-party LST data lives in
`/bigdisk/programming/pathfinder1e/data/spheres`; upstream source is not patched.
No replacement Spheres character engine or general LST evaluator is being built.

## Implemented scope

An experimental source, a Magic Talent category, shared casting variables, a
fixed-INT Incanter calculation slice capped at level 2, Destruction, Searing Blast,
Epicenter and Gather Energy. Talents require the base sphere and spend the same
pool. Core values are granted by the prototype class, not globally to every PF
character. The two initial casting talents belong to one shared automatic ability;
future multiclass support must verify this grant is applied once.

Class contributions add to general CL, magic skill bonus, spell-pool levels and
talent budget. The casting modifier enters the pool formula once. Destruction
has a separate CL adjustment and derived DC, range and damage counts. Blast type
selection is an available option, not a permanent modification to every blast.
Talent descriptions report options; they do not simulate actions or spend points.

This is NOT a complete legal character builder: bonus feats, specializations,
tradition selection, drawbacks, boons, fractional BAB/saves, multiclassing and
levels 3–20 are not supported. INT is an explicit test fixture, not an imposed
rule for real traditions. Martial categories/progressions and Spheres of Might
content remain pending the plan's magic-slice acceptance gate. Champions is excluded.
Only four selections exist; level 2 intentionally leaves at least one talent unspent.

## Sources and provenance

Checked 2026-09-22; use the Ultimate tabs, not Original or later third-party additions:

```text
https://spheresofpower.wikidot.com/using-spheres-of-power
https://spheresofpower.wikidot.com/incanter
https://spheresofpower.wikidot.com/destruction
```

The Incanter talent count includes the class progression, odd-level bonus and
one-time casting grant. Expected numbers are hand-calculated acceptance values,
not captured PCGen output. No rulebook prose, artwork or bulk wiki copy is included.
Source attribution does not establish distribution permission: license/notice
review is a release gate before publishing a complete dataset. No existing license
files are changed and no first-party project license is selected here.

LST patterns were inspected in the pinned PCGen tree's Pathfinder homebrew
campaign/category examples and Core Rulebook classes, abilities and categories.
Pin remains 6.08.00RC10; do not substitute current master syntax blindly.

## Verification and blocker

2026-09-22 earlier bounded upstream attempt:

```sh
timeout 30s /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10/gradlew --offline --no-daemon -p /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10 compileJava --console=plain
```

FAILED during configuration at build.gradle:221: required Java 16 toolchain was
not available locally; offline auto-download could not resolve the cached resource.
That blocker is now resolved on the ThinkPad only; the failure remains historical
evidence for other machines that lack the private toolchain/cache described below.

2026-09-22 ThinkPad-only compile verification:

```sh
timeout 120s env JAVA_HOME=/home/danbo/.local/lib/jvm/temurin-16.0.2+7 /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10/gradlew --offline --no-daemon --no-build-cache --rerun-tasks -Dorg.gradle.java.installations.paths=/home/danbo/.local/lib/jvm/temurin-16.0.2+7 -Dorg.gradle.java.installations.auto-download=false -p /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10 compileJava -x downloadJRE -x downloadJavaFXModules --console=plain
```

PASSED on the ThinkPad: `BUILD SUCCESSFUL in 43s`, with `:copyMasterSheets` and
`:compileJava` executed. `compileJava` printed `Args for for compileJava are
[--enable-preview]`; deprecation and unchecked-operation notes did not fail the
task. This verifies offline source compilation of the vendored PCGen 6.08.00RC10
checkout in that environment only. Required local setup: private Temurin JDK 16 at
`/home/danbo/.local/lib/jvm/temurin-16.0.2+7`, local Gradle dependency cache, and
the retained download-task deferral patch. Continue excluding both eager download
tasks for compile-only checks: `-x downloadJRE -x downloadJavaFXModules`.

Do not generalize this setup to other machines. Tests, application startup,
packaging, dataset load, talent selection, save/reload and character export remain
unverified until run separately.

## Acceptance procedure

1. On the ThinkPad, reuse the verified compile command above for compile-only
   checks. On any other machine, first provision an equivalent Java 16 toolchain,
   local Gradle cache and retained download-task deferral patch. Then run PCGen
   data tests separately; compile success does not verify tests.
2. Copy the prototype data directory to a separate PCGen user-data directory;
   leave the vendored tree untouched. Load it alongside Pathfinder Core Rulebook.
   Require zero parse/unresolved-reference errors. A core-only character must
   retain identical statistics before/after loading this source.
3. Build human prototype Incanters at levels 1 and 2 with final INT 18, then a
   level-1 case with final INT 7. Use ordinary progression rules, no equipment,
   traits, specializations, or external CL bonuses. Select Destruction first.
   Verify the other three talents are unavailable without it, become selectable
   with it, cost one each, and cannot be selected twice. Check pool remaining.
4. Save/reload and export through `spheres_export.txt`. Compare to the corresponding
   case in `/bigdisk/programming/pathfinder1e/testdata/spheres/expected.json` using
   the first-party verifier. The export exposes total talent budget, not remaining
   selections; selection behavior requires the separate checks above.
5. Only after actual PCGen evidence passes, expand traditions, a complete
   Destruction sphere, then a representative martial sphere as the plan requires.

Historical next action (superseded): enable JUnit Platform for `datatest`.
That task is now explicitly out of scope; use the targeted workflow above.
Do not mass-import talents or introduce Java changes on the assumption LST fails.

## 2026-09-22 — First actual upstream data-test attempt (ThinkPad)

Inspected PCGen's `DataLoadTest`, `PcgenFtlTestCase`, and Gradle test tasks before
attempting the existing data-load harness. No first-party integration test has
been added yet. The upstream basic-source test does not itself include our external
Spheres source; it is a prerequisite harness check, not Spheres acceptance.

```sh
timeout 120s env JAVA_HOME=/home/danbo/.local/lib/jvm/temurin-16.0.2+7 /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10/gradlew --offline --no-daemon -Dorg.gradle.java.installations.paths=/home/danbo/.local/lib/jvm/temurin-16.0.2+7 -Dorg.gradle.java.installations.auto-download=false -p /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10 datatest --tests pcgen.persistence.lst.DataLoadTest -x downloadJRE -x downloadJavaFXModules --console=plain
```

FAILED in 25s at `:compileSlowtestJava`, resolving `:testCompileClasspath`, before
any tests ran. Reported missing offline coordinates:

```text
org.junit.platform:junit-platform-runner:1.9.2
org.junit.platform:junit-platform-launcher:1.9.2
org.junit.jupiter:junit-jupiter-api:5.9.1
org.junit.jupiter:junit-jupiter-params:5.9.2
org.hamcrest:hamcrest:2.2
org.testfx:testfx-junit5:4.0.16-alpha
org.testfx:openjfx-monocle:jdk-12.0.1+2
org.xmlunit:xmlunit-matchers:2.9.1
```

This list is the observed compile-classpath failure, not a complete inventory of
transitive/runtime test dependencies. The later test runtime may need additional
artifacts. No dependency installation or online resolution was attempted.

`:compileJava` was up-to-date; resource processing, plugin JAR tasks and `:jar`
ran before the failure (72 actionable tasks: 71 executed, 1 up-to-date). The JAR
task emitted duplicate-entry warnings. This does not establish that distribution
packaging or startup works. The exclusions in this diagnostic bypass runtime
download tasks; they are not a validated test/runtime/packaging fix.

Full local diagnostic log:
`/bigdisk/programming/pathfinder1e/build/pcgen-datatest.log`.
Preserve the working private JDK and download-task deferral patch. Populate only
the pinned test dependencies and their transitives before retrying this harness;
do not replace the working compiler to address a test-cache failure.

## First-party checks completed

### 2026-09-22 — ThinkPad offline recheck

Re-ran the exact data-test command above after the user populated the cache.
Log: `/bigdisk/programming/pathfinder1e/build/pcgen-datatest-recheck.log`.
The original failure log is preserved separately. This attempt failed in 19s
at `:datatest` with `No tests found for given includes`, not missing dependencies.
77 actionable tasks: 69 executed, 8 up-to-date. `compileSlowtestJava` and
`compileTestJava` were UP-TO-DATE, not newly compiled in this run.

Confirmed the compiled `DataLoadTest.class` exists in the slowtest output.
Its source uses Jupiter `@ParameterizedTest` and `@MethodSource`. The pinned
`datatest` task lacks `useJUnitPlatform()`, unlike `test`, `itest` and `slowtest`.
This identifies the discovery configuration mismatch to correct next. No test
cases ran and no Spheres loading/export was verified. Preserve the private JDK
and download deferral patch; no further package installation is indicated by
this failure. A narrow first-party Gradle init script configuring only `datatest`
is a possible next fix without editing upstream Java. It has not been applied.

The earlier missing-dependency list is historical on the ThinkPad, not a current
installation request. This result does not certify every test/runtime dependency
or any other machine's setup.

`python3 /bigdisk/programming/pathfinder1e/tools/test_spheres.py` passed four
tool tests (packaging, fixture/export field agreement, malformed/duplicate/missing
export rejection, missing-file/prerequisite rejection). Synthetic test strings
exercise the verifier only; they do not verify the LST calculations.
`python3 /bigdisk/programming/pathfinder1e/tools/spheres.py check` passed.
The normal build-driver test command also passed all existing profile/candidate
tests, 655 scenario checks and 21,147 regression checks.

For an actual PCGen export saved at the following path, compare with:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/spheres.py verify incanter1-int18 /bigdisk/programming/pathfinder1e/build/incanter1-int18.txt
```

The old fixed output path above is illustrative. The smoke wrapper now generates
real exports in unique build subdirectories; expected JSON remains the oracle.