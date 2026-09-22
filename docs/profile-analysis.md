# Absolute probability / specialization analysis — 2026-09-22

## Purpose and scope

Evaluate absolute success probabilities rather than treating d20 parity as the
primary objective. No conversion coefficients, reference targets, or synthetic
bonus curves changed. LOW/TYPICAL/HIGH are still synthetic bonus profiles, NOT
validated investment tiers. A final modifier alone cannot establish how much a
character invested. No new target matrix has been accepted as a pass/fail rule.
Only direct rolls in situations excluding take 10/20 are represented.

## Report contract

Use `scenarios --report profiles` with existing model/type/profile/bonus/level
filters and table or CSV output. Each profile/difficulty group reports pool mean,
median, p10, p90, minimum and maximum, plus d20 comparison statistics. CSV carries
d20 mean/median/p10/p90; the compact table shows d20 mean. All report numbers are
percentages, unlike the original row CSV's probability fractions.

Percentiles use nearest rank, ceil(q*n); even-sized medians average the two middle
values. These describe variation BETWEEN scenario success probabilities, not the
success-count distribution of one roll. Rows are equally weighted. No Monte Carlo
sampling is involved. Default groups have 60 rows, or 40 for VERY_HARD because
attacks have no very-hard band. Use type and level filters to avoid hiding variation.

Pure statistics live in `src/main/java/dicepool/ProfileAnalysis.java`; rendering is
isolated in `ProfileReport.java`. Existing row reports remain the default.

## Measured results

Each model was evaluated on the existing 660 scenarios using the new CLI report.
Selected pool mean probabilities:

| Model | LOW/low | LOW/average | TYPICAL/average | HIGH/average | HIGH/high |
|---|---:|---:|---:|---:|---:|
| tn8-7-4 | 32.49% | 7.32% | 51.93% | 76.85% | 56.38% |
| tn8-8-4 | 40.56% | 11.58% | 58.38% | 81.32% | 61.60% |
| tn8-10-5 | 64.92% | 34.20% | 80.38% | 93.35% | 83.04% |

The 8/4 model's aggregate pattern resembles the proposed specialization direction,
but the distribution is wide: LOW/low median is 35.04%, p10–p90 is 9.88–75.99%,
and full range is 3.86–100%. TYPICAL/average median is 52.61%, p10–p90 is
35.04–85.07%. A mean near a desired band is not evidence that most cases fit it.

### TN8-8-4 by type and level band

Values below are mean pool success probabilities for five levels per cell.

| Profile / difficulty / type | 1–5 | 6–10 | 11–15 | 16–20 |
|---|---:|---:|---:|---:|
| LOW / low / attack | 50.41% | 25.45% | 11.51% | 7.85% |
| LOW / low / save | 70.60% | 44.53% | 34.21% | 22.33% |
| LOW / low / skill | 86.28% | 60.86% | 43.64% | 29.04% |
| TYPICAL / average / attack | 43.66% | 47.08% | 41.16% | 49.08% |
| TYPICAL / average / save | 57.26% | 49.14% | 41.98% | 42.44% |
| TYPICAL / average / skill | 83.99% | 82.88% | 80.34% | 81.58% |
| HIGH / average / attack | 64.73% | 70.73% | 68.31% | 76.74% |
| HIGH / average / save | 82.17% | 80.17% | 78.87% | 81.88% |
| HIGH / average / skill | 92.08% | 92.84% | 92.76% | 94.56% |

These slices were also inspected read-only from the existing candidate CSV.

## Interpretation and unresolved choices

- LOW does not represent stable relative competence across levels: its bonus
  growth falls behind the level-scaled low targets. The aggregate 40.56% hides
  deteriorating high-level participation, particularly attacks.
- TYPICAL does not represent comparable competence across check types. Its skill
  curve is substantially more successful than its attack/save curves.
- HIGH attacks, rather than TYPICAL attacks, currently land around the proposed
  60–80% average-task band. This is evidence about these synthetic formulas, not
  proof about actual Pathfinder investment patterns.
- Minimum-one-die and nonpositive-success thresholds remain provisional. Some
  low targets need zero successes, producing 100% even for tiny pools.
- A 40–50% chance means meaningful participation, not reliable success on a single
  attempt. Distinguish that from the desired reliability of specialists.

Next design decision: define what uninvested/low/medium/specialist means in final
modifiers by level AND check type, independently of the desired pool probabilities.
Do not adjust profile values merely to make a candidate look successful. Do not
adopt a base pool or retune the model until that input interpretation is settled.
The old MAE and directional checks remain available as secondary diagnostics;
their earlier conclusions are not automatic verdicts under the revised objective.

## Verification

ProfileTest passed mean/median/nearest-rank, single-element, invalid probability,
empty-input, deterministic replay, filtered CLI, CSV shape and invalid-option tests.
Candidate tests, 655 scenario checks and 21,147 original regression checks pass.
All three full-corpus profile reports were run successfully. No dependencies,
upstream source or LICENSE files changed.