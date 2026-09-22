# TN8 direct-roll candidates — 2026-09-22

Follow-up: `docs/profile-analysis.md` evaluates the revised specialization objective
using absolute probabilities. The parity/direction diagnostics below describe the
earlier objective and are retained for comparison, not as primary acceptance criteria.

Opt-in experiments, not a replacement for the locked baseline. All use
`dice = max(1, final modifier)`, 8+ on d10, and
`required = ceil((AC_or_DC - offset) / divisor)`. No cancellations or explosions.

| CLI model | Offset | Divisor | 660-case MAE | Mean signed delta |
|---|---:|---:|---:|---:|
| tn8-7-4 | 7 | 4 | 9.443pp | -7.685pp |
| tn8-8-4 | 8 | 4 | 7.882pp | -3.539pp |
| tn8-10-5 | 10 | 5 | 15.646pp | +13.941pp |

Every model was run over the same 660 level/profile/type/difficulty scenarios.
CSV files are generated under `build/`, and can be reproduced with the scenarios
command. No fitting or per-row best-pool selection occurred.

## Shape, not just error

Reports now count LOW cases strictly above d20, AVERAGE cases within 5 percentage
points, and HIGH/VERY_HARD cases strictly below d20. The 5pp tolerance is a labeled
diagnostic convention, not a user-approved balance criterion. Equal probabilities
do not pass the strict easy/hard directional tests, including saturated 0/100% cases.
The aggregate count is not a quality ranking: an excessively harsh model can pass
many hard-case direction checks while failing the rest.

| Model | Low improved / 180 | Average within 5pp / 180 | High lower / 180 | Very hard lower / 120 |
|---|---:|---:|---:|---:|
| tn8-7-4 | 36 | 59 | 135 | 78 |
| tn8-8-4 | 64 | 65 | 109 | 63 |
| tn8-10-5 | 137 | 28 | 26 | 24 |

None achieves the desired shape consistently. The 7/4 model works well for the
specific +11 vs AC15/18/21 example: 88.701%, 68.726%, 43.044% versus d20's
85%, 70%, 55%. The earlier discussion's approximate 91% for two successes was
too high; the implemented binomial calculation gives 88.701%.

## Scope and unresolved usability

These are direct rolled checks in contexts where take 10/20 is unavailable, by
scenario assumption. There is no character/ability eligibility detector. The
same skill can still appear when rolled under the stipulated conditions.

The minimum-one-die rule is provisional: -5 through +1 all produce one die.
Therefore +1 = +1 die only above that floor. AC/DC rounding still creates plateaus.
Nonpositive requirements retain existing automatic-success semantics; no hidden
minimum-success clamp was added. In particular the 10/5 candidate is literally
ceil((DC-10)/5), NOT the different '+1 success at DC10' table discussed previously.
These distinctions are documented rather than silently choosing new rules.

Pool p95 is 25 dice and maximum 32 in this corpus, relevant to table handling.
No conclusion about psychological feel is claimed without playtesting.

## Verification

CandidateTest covers all three models' bonus scaling from -5..50, boundaries,
full-grid determinism, CLI validation, and unchanged baseline conversion.
655 scenario checks and 21,147 original regression checks still pass.
Runtime runs generated each complete 660-row CSV and the level-5 example.
No upstream libraries or licensing files were changed.