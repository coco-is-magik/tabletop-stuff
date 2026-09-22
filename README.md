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

## Accepted dice-pool conversion model

Roll d10s equal to the character's final PF1e modifier, with a minimum of 1 die.
Each die showing **8+** is one success. Convert AC/DC to required successes with
`ceil((AC or DC - 8) / 4)`: 8–12 needs 1, 13–16 needs 2, 17–20 needs 3,
21–24 needs 4, 25–28 needs 5, 29–32 needs 6, 33–36 needs 7, and 37–40 needs 8.
Example: **+11 vs AC 18** rolls **11d10** and needs **3 successes**.

Expected model shape across the current scenario corpus:

| Profile | Low difficulty | Average | High | Very hard |
|---|---:|---:|---:|---:|
| LOW | 40.56% | 11.58% | 1.53% | 0.06% |
| TYPICAL | 79.99% | 58.38% | 33.71% | 16.79% |
| HIGH | 92.59% | 81.32% | 61.60% | 40.73% |

This makes investment matter more strongly than d20: weak areas are real weaknesses,
typical investment has meaningful risk at average difficulty, and high investment
is reliable without making high or very-hard checks automatic.

## Run

### Absolute probability / specialization report

```sh
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --model tn8-8-4 --report profiles
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --model tn8-8-4 --report profiles --type ATTACK --min-level 16 --max-level 20 --format csv
```

This opt-in report groups by profile/difficulty and shows absolute mean/median,
p10/p90 and range, with d20 context. Use type/level filters for detailed slices.
All values in this report are percentages; percentiles describe variation across
scenario probabilities, not outcomes of a single roll. Existing row output is unchanged.

The current profiles are synthetic bonus curves, **not validated investment tiers**.
TN8-8-4 yields LOW/low mean 40.56%, TYPICAL/average 58.38%, HIGH/average 81.32%,
but these hide substantial type/level differences. Findings and current handoff:
`/bigdisk/programming/pathfinder1e/docs/profile-analysis.md`.
No conversion coefficients were changed and no model is declared balanced.

### Candidate and raw-row reports

New opt-in, direct-roll candidates: `--model tn8-7-4`, `tn8-8-4`, or `tn8-10-5`.
They roll one die per final bonus (provisional minimum one), count 8+, and convert
DC using the named offset/divisor. Named models cannot be mixed with coefficient
flags. The original default remains unchanged. Take-10/take-20 contexts are outside
these experiments; eligibility is assumed, not detected.

```sh
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --model tn8-7-4 --level 5 --type ATTACK --bonus 11
python3 /bigdisk/programming/pathfinder1e/tools/build.py run scenarios --model tn8-8-4 --format csv
```

Full-corpus findings: `/bigdisk/programming/pathfinder1e/docs/tn8-experiment.md`.
None consistently achieved the earlier parity/direction objective. Raw-row reports
retain those diagnostics, now secondary to the absolute specialization analysis above.

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