# Pathfinder 1e dice-pool experiment

A standalone **PF1e d20 versus d10-pool scenario comparison tool**. The locked v1
scope is `/bigdisk/programming/pathfinder1e/docs/scenario-baseline.md`, superseding
the original plan's PCGen-first requirements. No character builder is required.

Compare levels 1–20 against low/average/high AC and low/average/high/very-hard DCs,
using synthetic low/typical/high bonus profiles or a known final bonus. Reports
include both success probabilities, percentage-point differences, and grouped
error/pool-size metrics. Default coverage is 660 equally weighted scenarios.

**Important:** AC and save-DC centers use PF1e Bestiary equal-CR guidelines.
Difficulty offsets, bonus profiles and the level-scaled skill DC curve are explicit
experimental assumptions—not measured population averages or universal skill rules.
The default d10 formula is a candidate, not an approved balanced conversion.

## Run

Requires Java/Javac 17+ and Python 3.12+. Commands may be run from any directory:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/build.py test
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --level 5 --type ATTACK --bonus 11
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --level 10 --type SKILL --profile HIGH
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --format csv > /bigdisk/programming/pathfinder1e/build/scenario-baseline-v1.csv
python3 /bigdisk/programming/pathfinder1e/tools/build.py run help
python3 /bigdisk/programming/pathfinder1e/tools/build.py run match --probability 0.55
python3 /bigdisk/programming/pathfinder1e/tools/build.py run table
python3 /bigdisk/programming/pathfinder1e/tools/build.py run simulate --system d20 --type ATTACK --bonus 12 --dc 24 --iterations 100000 --seed 12345
python3 /bigdisk/programming/pathfinder1e/tools/build.py run simulate --system pool --dice 7 --target 6 --successes 4 --seed 12345
python3 /bigdisk/programming/pathfinder1e/tools/build.py run benchmark --type ATTACK > /bigdisk/programming/pathfinder1e/build/attack-grid.csv
```

Run the test/build command once before redirecting reports into the build directory.
Table output goes to stdout; settings and aggregate metrics go to stderr.
Use `--min-level`/`--max-level` for a range, `--ac-spread`/`--dc-spread` to adjust
difficulty bands, and conversion flags such as `--bonus-per-die` or
`--dc-per-success` to compare candidate formulas against the same scenarios.
Pool notation `10d10/6/3` means ten dice, each succeeding on 6+, requiring three successes.

The build driver compiles with Java 17 compatibility and warnings treated as errors.
First-party compilation/testing is offline and requires no external packages.
Default d20 check type is SKILL; choose ATTACK or SAVE when natural 1/20 applies.
Benchmark writes 3,136 cases plus header to CSV and prints aggregate error and
pool-size metrics to stderr. Model coefficients are configurable via CLI flags;
they are experimental and have not been fitted to Pathfinder character careers.

## Dependencies and boundaries

Verified baseline: **655 scenario checks + 21,147 existing regression checks pass**.
The default model's 660-case MAE is **17.069 percentage points**, so model tuning
is still needed. The scope, scenario definitions and output contract are locked by
tests; the candidate model's balance is not claimed.

- First-party source: `/bigdisk/programming/pathfinder1e/src/`
- First-party tooling: `/bigdisk/programming/pathfinder1e/tools/`
- Third-party archive and checksum: `/bigdisk/programming/pathfinder1e/vendor/`
- Upstream extraction: `/bigdisk/programming/pathfinder1e/vendor/upstream/`
- Synthetic fixture: `/bigdisk/programming/pathfinder1e/testdata/synthetic-fighter.properties`
- Architecture and numerical conventions: `/bigdisk/programming/pathfinder1e/docs/architecture.md`

PCGen 6.08.00RC10 source is vendored unchanged with original licenses/notices.
Verify it with:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/vendor.py verify
```

This is preserved reference material, not a runtime/build requirement. Its
transitive dependencies are **not vendored**. Earlier upstream task discovery failed
offline on missing plugins; a bounded online attempt timed out during configuration.
No upstream tests or real-character exports have passed. The first-party engine does
not depend on that build and does not reimplement character-generation rules.

Snapshots and their explicitly synthetic fixture remain supported for compatibility.
Character generation/import, opposed checks, critical models, full combat, and damage
conversion are outside this baseline. No further PCGen work is needed to use it.
The current handoff is `/bigdisk/programming/pathfinder1e/docs/implementation-log.md`.