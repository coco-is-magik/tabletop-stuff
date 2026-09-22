# Experimental resolution engine

Current delivery scope is defined by `docs/scenario-baseline.md`: the scenario
comparison tool is standalone, and PCGen integration is not a prerequisite.
`Scenarios` generates immutable level-indexed comparisons without I/O;
`ScenarioReport` renders tables/CSV and grouped metrics. Reference target arrays
are separate from synthetic bonus formulas and configurable difficulty offsets.

## Ownership

`src/main/java/dicepool` is first-party Java 17. `tools` contains first-party Python
standard-library build and archive-management tools. `vendor` contains the pinned
PCGen archive, provenance manifest and extracted upstream tree. Upstream licenses
and notices remain in the archive and extracted source. No first-party license was
chosen on the user's behalf.

PCGen alone owns character construction. `CharacterSnapshot` stores final values,
not build recipes. `SnapshotIO` reads/writes version-1 UTF-8 Java properties via
caller-provided readers/writers; callers must choose UTF-8 for files. It is not a
PCG parser and is not yet wired to PCGen exports. Unknown properties are ignored
for forward compatibility; unknown schema versions are rejected. Properties use
standard Java escaping and duplicate keys follow Properties' last-value behavior.

`D20Engine`, `PoolEngine`, `Matching`, `ConversionModel`, `Benchmark` and `Simulation`
perform no I/O. Randomness is explicitly supplied or created from an explicit seed
using `java.util.Random`. `Main` and `SnapshotIO` are boundary adapters.

## Mathematics and limits

D20 resolution uses integer totals without overflow, with natural 1/20 overrides
for attacks, saves and CMB; skills, ability checks and OTHER do not get overrides.
Context-specific exceptions (immunity, concealment, take 10/20, etc.) are not modeled.
Pool distributions use binomial convolution in double precision, not Monte Carlo
estimates; floating-point rounding still applies. Pool size is 0..200, d10 target
1..11 (including always/never successful dice), and required successes can be any
integer. Nonpositive requirements succeed, requirements above pool size fail.
No exploding dice or cancelling ones are silently approximated.

Matching searches 1..maxDice, TN2..10, required 1..N. Sort order is error, dice,
target, requirement. Thus 0/100% targets need not have a perfect matching candidate.

Initial experimental model:

```
N = max(0, diceOffset + floor(bonus / bonusPerDie))
S = ceil((DC - dcOffset) / dcPerSuccess)
TN = target (default 6)
```

Default coefficients are 5, 2, 10, 3, respectively. They are a starting experiment,
not a recommended conversion. No attack-specific probability floors are imposed
on pools: differences must remain visible in benchmark error. Oversized pools fail
rather than silently clipping. The grid includes -5..50 bonuses and 5..60 DCs.

CSV goes to stdout; model and aggregate metrics go to stderr. Error units and
within-tolerance fractions are probabilities (0.01 = one percentage point).
Pool p95 uses nearest rank and median averages the two middle values for even N.
Simulation is bounded to 10 million iterations / 100 million pool die rolls.

## Test coverage

`EngineTest` independently enumerates all d20 faces across each type and grid pair,
enumerates small d10 pools, checks boundary inputs and distribution normalization,
replays seeded rolls, verifies matching order, metrics invariants, CSV cardinality,
snapshot immutability/round trips, and CLI failures. Tests require no downloaded
libraries. See `implementation-log.md` for observed outcomes and unfinished work.