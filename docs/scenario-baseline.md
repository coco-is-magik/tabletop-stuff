# PF1e scenario baseline v1 — current scope

Accepted scope, 2026-09-22: compare d20 and d10-pool success probabilities for
meaningful PF1e AC/DC scenarios across levels 1–20. This document supersedes the
PCGen-first delivery requirements in the original plan and earlier handoff.
The original plan and upstream archive are preserved for reference, not prerequisites.

## Locked contract

Scope clarification: scenarios represent direct rolls where take 10/20 is
unavailable. Eligibility is an input assumption, not inferred from character data.
Opt-in TN8 experiments are documented in `docs/tn8-experiment.md`; the default
baseline formula and scenario values remain unchanged.

- No character builder, PCGen installation, upstream build, network or third-party
  runtime libraries are required for scenario reports or tests.
- Exact d20 and binomial probabilities, with existing natural-roll semantics preserved.
- Equal-CR targets (CR = scenario level); three AC bands and four DC bands.
- ATTACK, SAVE and SKILL remain separate categories.
- Every result includes level, type, bonus profile, difficulty, final bonus, target,
  pool parameters, both probabilities and signed/absolute percentage-point error.
- Default model is a candidate to evaluate, not a claim of successful conversion.
- Stable ordering, repeatable output, CSV export and grouped metrics.
- Existing commands and tests remain supported. No damage, critical, full-combat,
  character import or career-corpus work is required to complete this baseline.

## Sources versus assumptions

Reference checked 2026-09-22: PF1e Bestiary, Monster Creation, Table: Monster
Statistics by CR, CR1–20 (AC and Primary Ability DC columns):
`https://legacy.aonprd.com/bestiary/monsterCreation.html`

Those values are guidelines, not empirical percentiles. Average AC uses the table;
low/high AC use average minus/plus 3 (configurable). Average save DC uses primary
ability DC; low/high/very-hard use offsets -5/+5/+10 (configurable step).
These difficulty bands are our scenario definitions, not official categories.

Skill average DC = 10 + level; other bands use -5/+5/+10. This is explicitly a
synthetic level-scaled stress curve, NOT a universal PF1e skill DC rule or a PF2e
table. For an actual task use the existing probability command with its actual DC.
The scenario level is a comparison index, not a complete encounter simulation.

Bonus profiles are synthetic inputs, not calculated characters or measured player
averages. Integer divisions below round down. L = level:

| Type | LOW | TYPICAL | HIGH |
|---|---|---|---|
| ATTACK | floor(L/2)+2 | floor(3L/4)+3+floor(L/4) | L+4+floor(L/4) |
| SAVE | floor(L/3)+1 | 2+floor(L/2)+2 | 2+floor(L/2)+5+floor(L/4) |
| SKILL | floor(L/2)+1 | L+5 | L+7+floor(L/4) |

Use `--bonus` for a known final modifier; it replaces all synthetic profiles with
one CUSTOM profile. A supplied bonus stays constant across a requested level range.
No gear/feat/buff contributions are inferred. No claim is made that these profiles
cover optimized builds. Pool coefficients remain independently configurable.

## Scope acceptance tests

Default report: 20 levels × 3 profiles × (3 attack + 4 save + 4 skill bands) =
660 rows. Tests lock reference targets, profile curves, difficulty offsets,
probability boundaries, selected hand-calculated outputs, deterministic output,
filters, CSV schema/counts, invalid input rejection and preservation of old tests.
Table output shows percentages; CSV probability columns are fractions and error
columns are percentage points. Positive delta means the pool succeeds more often.
Groups are equally weighted per scenario, not weighted by encounter frequency.

## Deliberately rejected approaches

Waiting for PCGen blocked useful work with unrelated dependencies. Per-scenario
best-fit matching could hide flaws in a global conversion formula, so scenario
reports use one explicit model; the separate matching tool remains diagnostic.
Difficulty bands are not presented as measured monster distributions.