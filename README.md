# Pathfinder 1e dice-pool experiment

> This repository contains two separate projects. **Part 1** is the dice-pool
> comparison tool described first. **Part 2** is a verified Spheres of Power/Might
> dataset for PCGen; jump to
> [Spheres of Power and Might for PCGen](#spheres-of-power-and-might-for-pcgen).

A standalone **PF1e d20 versus d10-pool scenario comparison tool**. The locked v1
scope is `docs/scenario-baseline.md`, superseding
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
python3 tools/build.py run scenarios --model tn8-8-4 --report profiles
python3 tools/build.py run scenarios --model tn8-8-4 --report profiles --type ATTACK --min-level 16 --max-level 20 --format csv
```

This opt-in report groups by profile/difficulty and shows absolute mean/median,
p10/p90 and range, with d20 context. Use type/level filters for detailed slices.
All values in this report are percentages; percentiles describe variation across
scenario probabilities, not outcomes of a single roll. Existing row output is unchanged.

The current profiles are synthetic bonus curves, **not validated investment tiers**.
TN8-8-4 yields LOW/low mean 40.56%, TYPICAL/average 58.38%, HIGH/average 81.32%,
but these hide substantial type/level differences. Findings and current handoff:
`docs/profile-analysis.md`.
No conversion coefficients were changed and no model is declared balanced.

### Candidate and raw-row reports

New opt-in, direct-roll candidates: `--model tn8-7-4`, `tn8-8-4`, or `tn8-10-5`.
They roll one die per final bonus (provisional minimum one), count 8+, and convert
DC using the named offset/divisor. Named models cannot be mixed with coefficient
flags. The original default remains unchanged. Take-10/take-20 contexts are outside
these experiments; eligibility is assumed, not detected.

```sh
python3 tools/build.py run scenarios --model tn8-7-4 --level 5 --type ATTACK --bonus 11
python3 tools/build.py run scenarios --model tn8-8-4 --format csv
```

Full-corpus findings: `docs/tn8-experiment.md`.
None consistently achieved the earlier parity/direction objective. Raw-row reports
retain those diagnostics, now secondary to the absolute specialization analysis above.

Requires Java/Javac 17+ and Python 3.12+. Run these from the repository root:

```sh
python3 tools/build.py test
python3 tools/build.py run scenarios --level 5 --type ATTACK --bonus 11
python3 tools/build.py run scenarios --level 10 --type SKILL --profile HIGH
python3 tools/build.py run scenarios --format csv > build/scenario-baseline-v1.csv
python3 tools/build.py run help
python3 tools/build.py run match --probability 0.55
python3 tools/build.py run table
python3 tools/build.py run simulate --system d20 --type ATTACK --bonus 12 --dc 24 --iterations 100000 --seed 12345
python3 tools/build.py run simulate --system pool --dice 7 --target 6 --successes 4 --seed 12345
python3 tools/build.py run benchmark --type ATTACK > build/attack-grid.csv
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

## Spheres of Power and Might for PCGen

A machine-readable, source-backed implementation of **Spheres of Power** and
**Spheres of Might** for PCGen 6.08.00RC10 (Ultimate-tab rules). It is a PCGen
campaign dataset, not a character builder, combat simulator or rules engine of its
own — it emits PCGen records and relies on PCGen to enforce them.

### What exists

- **53 base spheres** (26 Power, 27 Might), generated from pinned source snapshots:
  **2,330 basic talents** and **411 advanced talents**.
- **Feats (1,201)** and **traits (161)** with a fail-closed prerequisite compiler;
  unresolved clauses require an explicit adjudication ability rather than being
  guessed. Alternate racial traits.
- **Casting and martial traditions**, **Spellcrafting** recipes, and **base and
  prestige classes** (Incanter, Conscript, Elementalist, Armorist, Hedgewitch and
  more, plus five prestige classes) at "thin class" fidelity: progression tables
  and named features, with per-option mechanics incomplete.
- **Reference mechanics**: ~800 basic talents expose their scaling quantity
  (caster level, base attack bonus, practitioner modifier, skill ranks, Hit Dice)
  as PCGen variables for the sheet to read; **advanced talents compile their
  published prerequisites into real `PRE` tokens**, and unresolvable clauses are
  gated behind GM approval.

### Scope

- **In:** Power and Might spheres, basic and advanced talents, feats, traits,
  casting/martial traditions, Spellcrafting, base and prestige classes, alternate
  racial traits.
- **Out:** legendary talents, Original Power rules, archetypes, Guile.

### How it is verified

- Deterministic generators; every generated file is checked for staleness.
- Offline suites (the Java engine plus 22 Python suites) via `build.py test`.
- **Live PCGen gates** driven through PCGen's production character controller:
  selection, effect, removal/refund, and save/reload round trips, plus a
  reference-variable gate that asserts the value PCGen computes, and an
  advanced-talent gate that asserts PCGen's own prerequisite check accepts a met
  set and rejects a missing one. The full sweep is 42 gates.

### What the tests do and do not prove

- They prove the dataset is deterministic, internally consistent, loadable, and
  that **PCGen honors the prerequisites, variables and pools we encode**.
- They do **not** prove the mechanics match the printed rules. There is no
  independent oracle for rules-text-to-mechanic mapping, most talents carry
  prerequisites and descriptions rather than automated effects, and coverage
  counters count records, not verified rules. Exact limits:
  `docs/spheres-current-status.md` and `docs/spheres-depth-audit.md`.

### Requirements and commands

Java 17+ (the build compiles with `--release 17`; JDK 25 works) and Python 3.12+.
PCGen source is vendored under `vendor/upstream/`; no online access is needed.
Run these from the repository root:

```sh
python3 tools/build.py test
python3 tools/spheres.py check
python3 tools/pcgen_spheres_gates.py all
python3 tools/pcgen_catalog_variables.py save
python3 tools/pcgen_advanced_talents.py save
```

## Dependencies and boundaries

The current Spheres work is summarised in
[Spheres of Power and Might for PCGen](#spheres-of-power-and-might-for-pcgen) above;
the notes below are the deeper detail and historical record.

### Incanter class — thin scope

Conscript is also available under the same class-only boundary. Implementation,
manual external-option limits and real-PCGen checks:
`docs/conscript-class.md`.

The thin classes remain separate from sphere catalog completion.
Incanter class acceptance and commands:
`docs/incanter-class.md`.
The extended-package inventory below does not define class completion.

The first-party source at `data/spheres`
contains thin classes and a Power/Might catalog (basic and advanced talents).
Catalog coverage is 53
base spheres, 2,330 basic talents and 411 advanced talents; **full
talent-specific mechanical automation is incomplete**. Supported behavior and
remaining requirements:
`docs/sphere-catalog.md`.
Power/Might feat records and selected mechanics are also available. This is not
complete feat automation; unresolved prerequisites require explicit adjudication.
Coverage, tests and limitations: `docs/spheres-feats.md`.
The September 30 continuation inventory, verified fixes and remaining content
backlog are recorded in `docs/spheres-backlog.md`.
Reviewed direct feat-equivalence mappings and Versatile Fighter's active stance
choices now reuse PCGen's existing mechanisms. Conditional equivalences and
complete configurable companion/transformation and class mechanics remain open;
the backlog distinguishes passed controller checks from pending persistence checks.
Incanter has level 1-20
base progression, mental casting choices, bonus-feat support, several
specializations, Core domain/bloodline adapters, Admixture, Destruction
specialization and Sword Birth data. Conscript's thin class is implemented.
Manual records remain compatible; catalog descriptions do not imply that every
listed effect is automated.
Offline PCGen source compilation is verified with a JDK 17-compatible toolchain
(JDK 25 works; the build targets bytecode 17) and the vendored PCGen 6.08.00RC10
harness runs on the bundled `vendor/jdk16`. If `javac`/`java` resolve to a stale
eselect VM, point them at a real one (`eselect java-vm set user openjdk-25`, or
`export GENTOO_VM=openjdk-25`). The targeted
Incanter 1/INT18, Incanter 2/INT18 and Incanter 1/INT7 fixtures load Core + Spheres,
verify two spent talents, and match all ten exports before and after PCGen
save/reload. Run the smoke command with `all` to check all three.
Targeted prerequisite enforcement, duplicate rejection, and core Fighter isolation
also pass via PCGen's production selection controller. Run
`python3 tools/pcgen_spheres_gates.py all`.
The full live sweep currently passes 42/42 gates; the reference-variable gate
(`tools/pcgen_catalog_variables.py`) verifies 39 computed values and the
advanced-talent gate (`tools/pcgen_advanced_talents.py`) verifies prerequisite
acceptance, rejection, refund and save/reload.
Broad upstream tests, GUI and packaging are not
current gates; do not debug `datatest` to proceed. The standalone dice-pool tool
remains unchanged. Current implementation status, exact compile command,
acceptance fixtures, and historical extended-package inventory:
`docs/spheres.md`.

```sh
python3 tools/spheres.py check
python3 tools/pcgen_spheres_smoke.py incanter1-int18
python3 tools/build.py test
```

### Existing comparison-tool baseline

Verified baseline: **655 scenario checks + 21,147 existing regression checks pass**.
The default model's 660-case MAE is **17.069 percentage points**, so model tuning
is still needed. The scope, scenario definitions and output contract are locked by
tests; the candidate model's balance is not claimed.

- First-party source: `src/`
- First-party tooling: `tools/`
- Third-party archive and checksum: `vendor/`
- Upstream extraction: `vendor/upstream/`
- Synthetic fixture: `testdata/synthetic-fighter.properties`
- Architecture and numerical conventions: `docs/architecture.md`

PCGen 6.08.00RC10 source is vendored unchanged with original licenses/notices.
Verify it with:

```sh
python3 tools/vendor.py verify
```

This is preserved reference material, not a runtime/build requirement. Its
transitive dependencies are **not vendored**. Earlier upstream task discovery failed
offline on missing plugins; a bounded online attempt timed out during configuration.
No upstream tests or real-character exports have passed. The first-party engine does
not depend on that build and does not reimplement character-generation rules.

Snapshots and their explicitly synthetic fixture remain supported for compatibility.
Character generation/import, opposed checks, critical models, full combat, and damage
conversion are outside this baseline. No further PCGen work is needed to use it.
The current handoff is `docs/implementation-log.md`.