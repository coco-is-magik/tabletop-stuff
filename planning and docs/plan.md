# PF1e d20-to-d10 Dice Pool Conversion: Implementation Plan

## 1. Project goal

Build an experimental Pathfinder First Edition rules simulator that reuses an existing PF1e character/rules implementation rather than recreating the Pathfinder ruleset from scratch.

The simulator should be able to take a valid PF1e character, calculate ordinary PF1e statistics, resolve checks using both the original d20 system and an experimental d10 dice-pool system, and compare their probability distributions.

The initial objective is not to convert every Pathfinder rule. It is to answer a narrower question:

> Can PF1e's d20 resolution mechanic be replaced by a d10 dice-pool mechanic while retaining approximately the same success probabilities across the range of characters and difficulties encountered in actual play?

The project should ultimately support automated experiments across many characters, levels, bonuses, ACs, DCs, and candidate dice-pool formulas.

---

# 2. Use PCGen as the PF1e reference implementation

Start with the open-source [PCGen repository](https://github.com/PCGen/pcgen?utm_source=chatgpt.com).

PCGen is preferable to implementing Pathfinder character calculation yourself because it already contains PF1e character data and machinery for calculating statistics derived from classes, ability scores, feats, equipment, levels, and other character features.

The important architectural principle is:

```text
Do not convert PCGen to d10 yet.

Use PCGen to answer:

"What are this character's Pathfinder statistics?"

Then let a separate experimental engine answer:

"What happens if those statistics are resolved differently?"
```

This keeps the experiment isolated from the much larger problem of rewriting Pathfinder.

---

# 3. Establish a clean development environment

Fork PCGen into your own GitHub account and clone the fork locally.

Create a dedicated branch:

```bash
git checkout -b dicepool-experiment
```

Verify that the unmodified project builds.

Run its existing automated tests, particularly the Pathfinder integration tests.

The PCGen repository currently documents Gradle tasks including:

```bash
./gradlew test
./gradlew pfinttest
./gradlew datatest
```

The exact available tasks should be checked against the version of PCGen you clone, since the repository can change over time.

Record the commit hash you initially work against:

```bash
git rev-parse HEAD
```

This gives the experiment a reproducible PCGen baseline.

---

# 4. Learn only the parts of PCGen necessary for the experiment

Do not begin by trying to understand the entire PCGen architecture.

Trace one simple statistic through the program.

For example:

```text
Level 5 Fighter
Strength 18
BAB +5
+1 longsword
Weapon Focus

        ↓

PCGen

        ↓

melee attack bonus
```

Determine where PCGen exposes the final calculated values for things such as:

```text
level
BAB
ability scores
ability modifiers
AC
saving throws
skill modifiers
weapon attack bonuses
weapon damage
CMB
CMD
spell DCs
caster level
```

The first milestone is simply being able to programmatically ask PCGen for these values.

You do not yet need a dice roller.

---

# 5. Define a neutral character-state representation

Create a small intermediate representation between PCGen and your experimental resolution engines.

For example:

```java
class CharacterSnapshot {
    String name;
    int level;

    int strength;
    int dexterity;
    int constitution;
    int intelligence;
    int wisdom;
    int charisma;

    int fortitude;
    int reflex;
    int will;

    int armorClass;
    int touchArmorClass;
    int flatFootedArmorClass;

    List<AttackSnapshot> attacks;
    Map<String, Integer> skills;
}
```

An attack might contain:

```java
class AttackSnapshot {
    String name;
    int attackBonus;
    String damageExpression;
    int criticalMinimum;
    int criticalMultiplier;
}
```

The important rule is that this representation describes the **result of Pathfinder character construction**, not how that result was obtained.

For example:

```text
Longsword attack bonus = +16
```

rather than:

```text
BAB +8
STR +5
enhancement +2
Weapon Focus +1
```

You can expose the individual components later if necessary.

---

# 6. Build the original d20 resolver

Before implementing the experimental mechanic, implement a tiny reference resolver.

Conceptually:

```java
interface ResolutionEngine {
    CheckResult resolve(Check check);
}
```

Then:

```java
class D20ResolutionEngine implements ResolutionEngine
```

For an ordinary check:

$$
d20+B\ge DC
$$

For attacks:

$$
d20+\text{Attack Bonus}\ge AC.
$$

Initially support only a few check types:

```text
attack vs AC
saving throw vs DC
skill check vs DC
```

Do not initially implement combat rounds, initiative, attacks of opportunity, grappling, spells, conditions, or other subsystems.

The purpose is to create a mathematically controlled testing environment.

---

# 7. Implement an exact probability calculator

Do not rely solely on random simulations.

For ordinary d20 checks, calculate the exact probability analytically.

Ignoring automatic-success/failure rules:

$$
P=
\frac{21-(DC-B)}{20}
$$

bounded to the interval \([0,1]\).

Where PF1e's natural-1/natural-20 rules apply, implement those separately because attacks and saving throws have different edge behavior from ordinary skill checks. Pathfinder's core rules distinguish those cases. [Pathfinder 1e rules reference at Archives of Nethys](https://www.aonprd.com/Rules.aspx?utm_source=chatgpt.com)

Your program should therefore eventually distinguish:

```text
ATTACK
SAVE
SKILL
ABILITY_CHECK
CMB
OTHER
```

rather than treating every `d20 + bonus vs DC` expression identically.

---

# 8. Implement the generic d10 dice-pool calculator

Do not hard-code one proposed conversion.

Represent a dice-pool rule as parameters.

For example:

```java
class DicePoolRule {
    int dice;
    int dieSides = 10;
    int successThreshold;
    int requiredSuccesses;

    boolean explodingTens;
    boolean cancelOnes;
}
```

Start with both special rules disabled:

```text
explodingTens = false
cancelOnes = false
```

A basic roll then looks like:

```text
Roll N d10.
Each die ≥ T produces one success.
At least S successes are required.
```

If the probability that one die succeeds is \(p\), then the number of successes is binomial:

$$
X\sim\operatorname{Binomial}(N,p)
$$

and:

$$
P(X\ge S)=
\sum_{k=S}^{N}
{N\choose k}p^k(1-p)^{N-k}.
$$

Implement this exact calculation before implementing random rolling.

---

# 9. Build the probability-matching tool

Now create the first genuinely useful experimental program.

Give it a Pathfinder probability:

```text
55%
```

and have it search possible dice-pool configurations.

For example, search:

```text
dice:                 1-20
success threshold:    2-10
required successes:   1-N
```

For every candidate calculate:

$$
E=
|P_{\text{pool}}-P_{\text{d20}}|.
$$

Then sort by error.

Example CLI:

```bash
./gradlew run --args="match --probability 0.55"
```

Possible output:

```text
Target probability: 55.000%

Dice   TN   Required   Probability   Error
------------------------------------------------
...
```

Do this for every ordinary d20 probability:

```text
5%
10%
15%
20%
...
90%
95%
```

This produces your first d20-to-dice-pool equivalence table.

---

# 10. Add Monte Carlo simulation

Once the exact mathematics works, implement actual rolling.

For example:

```bash
dicepool simulate \
    --system d20 \
    --bonus 12 \
    --dc 24 \
    --iterations 1000000
```

and:

```bash
dicepool simulate \
    --system pool \
    --dice 7 \
    --target 6 \
    --successes 4 \
    --iterations 1000000
```

Report both theoretical and observed probabilities:

```text
Iterations:            1,000,000

Expected probability: 45.000%
Observed probability: 45.037%
Difference:             0.037%
```

Monte Carlo simulation is not a replacement for the analytical calculation. It is a test that your roller behaves according to the analytical model.

---

# 11. Make random tests reproducible

Allow the random-number generator to accept a seed:

```bash
dicepool simulate \
    --seed 12345 \
    --iterations 1000000
```

Two executions using the same seed should produce the same sequence.

This will make debugging substantially easier.

---

# 12. Separate three concepts

At this point, explicitly separate:

```text
Character generation

        ↓

PF1e statistics

        ↓

Resolution system
```

For example:

```text
PCGen
  |
  | CharacterSnapshot
  v
+---------------------------+
|                           |
v                           v
D20 Engine             Dice Pool Engine
|                           |
v                           v
Results                  Results
 \                         /
  \                       /
   +---- Comparison -----+
```

This separation is central to the project.

PCGen remains responsible for Pathfinder character rules.

Your code becomes responsible for experimental resolution mechanics.

---

# 13. Create synthetic Pathfinder tests

Before introducing real characters, test mathematical scenarios.

Generate:

$$
B=-5,\ldots,+50
$$

and:

$$
DC=5,\ldots,60.
$$

For each pair calculate:

$$
P_{\text{d20}}(B,DC).
$$

Then calculate whatever dice-pool system currently corresponds to that situation.

Store:

```text
bonus
DC
d20 probability
pool size
pool target
required successes
pool probability
absolute error
```

Export the results as CSV.

For example:

```text
bonus,dc,d20_probability,pool_probability,error
5,15,0.55,0.546875,0.003125
5,16,0.50,0.500000,0.000000
5,17,0.45,0.453125,0.003125
```

---

# 14. Define global error measurements

Do not evaluate a conversion based on one check.

Measure its performance across the entire test space.

Useful metrics include mean absolute error:

$$
MAE=
\frac1N
\sum_i
|P_{d20,i}-P_{pool,i}|
$$

root mean squared error:

$$
RMSE=
\sqrt{
\frac1N
\sum_i
(P_{d20,i}-P_{pool,i})^2
}
$$

and maximum error:

$$
E_{\max}
=
\max_i
|P_{d20,i}-P_{pool,i}|.
$$

Also report how often the conversion falls within:

```text
±1 percentage point
±2.5 percentage points
±5 percentage points
±10 percentage points
```

These measurements make comparisons between candidate systems objective.

---

# 15. Start experimenting with conversion formulas

Only now should you begin designing the actual replacement mechanic.

Test families rather than individual arbitrary configurations.

For example:

```text
Model A

Pool = bonus-derived value
TN = 6
Required successes = DC-derived value
```

versus:

```text
Model B

Pool = character competence
TN = difficulty
Required successes = fixed
```

versus:

```text
Model C

Pool = competence
TN = fixed
Required successes = difficulty
```

versus:

```text
Model D

Pool = competence + situational modifiers
TN = fixed
Required successes = opposition
```

Run exactly the same probability suite against every model.

---

# 16. Prefer fixed target numbers initially

Start with something like:

$$
d10\ge6
$$

as a success.

Do not initially use variable target numbers, exploding 10s, or 1s cancelling successes.

A fixed target means each die has a constant success probability:

$$
p=0.5.
$$

That makes the resulting distribution easy to understand:

$$
X\sim\operatorname{Binomial}(N,0.5).
$$

Once the basic conversion works, introduce additional mechanics one at a time.

---

# 17. Investigate modifier conversion

This is likely to become one of the central design problems.

PF1e has enormous numbers of modifiers:

```text
+1
+2
-2
+4
etc.
```

On a d20, each ordinary +1 shifts the success probability by five percentage points while the roll remains inside the uncapped range.

A dice pool does not naturally behave that way.

Test at least three approaches.

```text
+1 PF modifier
        ↓
fractional/accumulated bonus dice
```

```text
+1 PF modifier
        ↓
change required successes
```

```text
+1 PF modifier
        ↓
change per-die target number
```

Measure the consequences instead of choosing based solely on intuition.

---

# 18. Add degrees of success

Once binary probabilities approximately align, investigate the information available from additional successes.

For example:

```text
0 successes below requirement = failure
requirement met              = success
requirement + 1              = strong success
requirement + 2              = exceptional success
```

Do not immediately attach Pathfinder effects to these categories.

First study how frequently they occur.

You may discover that the dice-pool conversion provides useful degrees of success that can later replace PF1e mechanics such as critical confirmation or margin-based effects.

---

# 19. Add real PCGen characters

Once the synthetic tests are stable, connect the test harness to PCGen character data.

Create a controlled suite such as:

```text
Fighter 1
Fighter 5
Fighter 10
Fighter 15
Fighter 20

Rogue 1
Rogue 5
...

Wizard
Cleric
Monk
Paladin
Ranger
Barbarian
```

Initially use deliberately simple builds.

Avoid highly optimized characters until the baseline works.

Extract each character's actual calculated statistics through the `CharacterSnapshot` layer.

---

# 20. Create representative opponents

Create test targets appropriate to various levels.

You want combinations such as:

```text
Fighter 5 attack vs low AC
Fighter 5 attack vs moderate AC
Fighter 5 attack vs high AC

Wizard 5 Will save vs low DC
Wizard 5 Will save vs moderate DC
Wizard 5 Will save vs high DC

Rogue 5 skill vs easy DC
Rogue 5 skill vs moderate DC
Rogue 5 skill vs difficult DC
```

This produces realistic tests rather than purely mathematical ones.

---

# 21. Compare entire character careers

For each class, compare levels 1 through 20.

Produce data such as:

```text
Level
PF bonus
Typical DC
PF success %
Pool success %
Difference
Pool size
```

This is where you will see whether the conversion preserves Pathfinder's progression.

A model might work extremely well at levels 1 through 5 and become pathological at level 15.

That is important information.

---

# 22. Test extreme PF1e characters

After ordinary characters work, deliberately test Pathfinder's pathological cases.

Examples include:

```text
very high skill modifiers
very high AC
poor saving throws
extremely high saving throws
large attack bonuses
large buff stacks
large penalties
multiple attacks
```

PF1e permits large numerical spreads, particularly at high levels.

Your dice-pool model needs a defined behavior when Pathfinder would produce something like:

```text
+38 skill
+27 attack
+3 save
AC 44
DC 31
```

This may reveal that an apparently good conversion requires impractically large pools.

---

# 23. Measure dice-pool size

Track not only probability error but physical usability.

For every model calculate:

```text
average dice rolled
median dice rolled
95th percentile pool
maximum pool
```

A system that reproduces Pathfinder perfectly but regularly requires:

```text
27d10
```

may be mathematically successful and practically undesirable.

You therefore have at least two optimization objectives:

$$
\text{minimize probability error}
$$

and

$$
\text{minimize pool size}.
$$

---

# 24. Test opposed checks separately

Do not assume opposed checks behave like static DCs.

PF1e can produce:

$$
d20+A
$$

against:

$$
d20+B.
$$

That probability distribution is different from:

$$
d20+A\ge DC.
$$

Create a separate experimental category for opposed checks.

Possible dice-pool equivalents include:

```text
both sides roll pools
highest success count wins
```

or:

```text
defender's statistic determines required successes
```

Compare these experimentally.

---

# 25. Handle attacks and criticals separately

Once ordinary attack probability works, investigate critical hits.

PF1e uses threat ranges and, ordinarily, confirmation rolls, so weapons such as:

```text
20/x4
19-20/x2
18-20/x2
```

have distinct probability structures. The PF1e combat rules define these mechanics separately from ordinary attack success. [Archives of Nethys combat rules](https://www.aonprd.com/Rules.aspx?Category=Combat&utm_source=chatgpt.com)

Do not simply declare extra dice-pool successes to be critical hits without comparing the resulting probabilities.

Calculate:

$$
P(\text{normal hit})
$$

$$
P(\text{critical hit})
$$

$$
P(\text{miss})
$$

under both systems.

Then search for a dice-pool interpretation that produces acceptable distributions.

---

# 26. Add damage later

Keep damage outside the initial project.

Phase one asks:

> Did the attack succeed?

Phase two asks:

> Was it a critical?

Only after those are understood should you investigate converting:

```text
1d8+7
2d6+12
4d6 sneak attack
```

into another resolution model.

You may ultimately decide that Pathfinder damage dice should remain unchanged.

There is no requirement that converting the resolution mechanic also means converting every die in the game.

---

# 27. Add batch experiments

The CLI should eventually support something like:

```bash
dicepool benchmark \
    --characters testdata/characters \
    --model models/fixed-tn6.json \
    --iterations 100000
``
```
