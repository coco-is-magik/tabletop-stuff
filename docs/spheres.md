# Spheres PCGen prototype — current handoff

## Reference mechanics and four prestige classes — 2026-10-06

Recorded-mechanics basic talents rose from 97 to 804 via caster-level reference
variables (War totem/rally/momentum plus area, duration and damage-dice
references across Blood, Dark, Death, Destruction, Mana, Light, Nature, Warp,
Conjuration, Creation, Enhancement, Illusion, Life, Time, Weather, Fallen Fey,
Alteration and Bear). Reference values are exposed as `DEFINE`/`BONUS:VAR` only;
they never add `BONUS:COMBAT`/`SAVE`/`SKILL`/`HP`, and repeatable talents never
own a `DEFINE` so removing one selection cannot undefine a shared counter. Both
invariants have regressions in `tools/test_catalog.py`.

Four prestige classes now have generated progressions: Tempestarii, Forest Lord,
Waking Sleeper and Spheres Archwizard (`tools/spheres_prestige.py`). Class
feature *effects* beyond the reference variables remain sheet rules. The
remaining prestige classes in the pinned inventory depend on subsystems absent
from this dataset (crew/airship, Kismet, Card Casting, conventional spell slots,
psionics, Guile/advanced catalogs) and are not implemented.

The full requested mechanical completion is still open. Most remaining talents
are conditional or multi-part and intentionally stay text-only; descriptions are
not automation. See `docs/spheres-current-status.md` for the measured inventory.

## Spellcrafting — 2026-09-25

An initial custom-spell recipe compiler, acquisition/repertoire records and
Spellcrafting feat chain are present. This is partial support, not complete
Spellcrafting automation. See
`/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/docs/spheres-spellcrafting.md`
for supported checks, usage and live PCGen verification results.

## Base classes — 2026-09-24

Incanter and Conscript retain their thin-class contracts. Elementalist remains
**partial**; see `/bigdisk/programming/pathfinder1e/docs/elementalist-class.md`.
The remaining 17 Power/Might base classes now have source-table level 1–20
records and limited class-specific choice support. They are **not** full
mechanical implementations: see `/bigdisk/programming/pathfinder1e/docs/spheres-classes.md`
for tested behavior and the substantial manual adjudication boundary. Do not
treat source descriptions or free-text slots as automated combat mechanics.

## Custom traditions — 2026-09-24

Custom casting and martial tradition builders now have selectable records; supported
choices and manual boundaries are documented in
`/bigdisk/programming/pathfinder1e/docs/spheres-traditions.md`.
They are not a complete tradition catalog or an enforcement engine.

## Feat catalog — 2026-09-24

1,201 source feat names are inventoried, with selected mechanical implementations
and fail-closed qualification for unsupported prerequisite clauses. This is not
completion of all feat mechanics. Details and live-controller commands:
`/bigdisk/programming/pathfinder1e/docs/spheres-feats.md`.

## Basic sphere catalog — 2026-09-24

Power/Might catalog records now cover 53 base spheres and 2,330 basic talents.
This supersedes the older statements below that no combat catalog exists.
Full talent-specific mechanical automation is **not complete**. Exact supported
behavior, verification and remaining requirements:
`/bigdisk/programming/pathfinder1e/docs/sphere-catalog.md`.

## Conscript class-only implementation — 2026-09-23

Conscript now has its thin class data and dedicated PCGen acceptance runner.
Scope, tested features and explicit manual boundaries:
`/bigdisk/programming/pathfinder1e/docs/conscript-class.md`.
No combat sphere catalog or unrelated subsystem was added.

## Active milestone: thin Incanter class only — 2026-09-23

The class contract and bounded acceptance commands are in
`/bigdisk/programming/pathfinder1e/docs/incanter-class.md`.
Levels, casting resources, talent/feat pools, specialization accounting, class
grants, removal and save/reload are the finish line. Full spheres, domains,
bloodlines, favored-class catalogs, companions, traditions and archetypes are not.
Existing optional data is preserved, not expanded. The older broad checklist below
is historical inventory and is explicitly superseded, not work to resume.

## Historical extended-package status — superseded scope

Current scope remains **Power + Might for normal PF1e games from the Spheres Wiki**.
Guile, mythic, gestalt, broad upstream PCGen tests, GUI polish, packaging and
performance work are out of scope for now.

### Incanter status

Implemented and directly exercised through the targeted PCGen controller/export
path:

- base Incanter chassis and unspecialized level 1-20 progression;
- Intelligence, Wisdom and Charisma casting-ability choices;
- magic talent and spell-point progression fixtures;
- Incanter bonus-feat pool;
- repeatable Extra Magic Talent and Extra Spell Points support;
- five-point specialization purchase budget and bonus-feat forfeiture formula;
- separate active-specialization budget/order model;
- Master of Mysteries;
- Channel Energy, positive/negative choice, uses, dice and DC;
- Lay on Hands, level-2 grant and scaling;
- Merciful Healer, using PCGen's existing mercy selections and prerequisites;
- standard Familiar, using PCGen's existing familiar support and master level;
- Admixture Adept, bonus Admixture talent and admixture pool;
- 33 Core cleric domain adapters, powers only, no domain spells;
- 10 Core sorcerer bloodline adapters, powers only, no arcana/spells/bonus feats/class skills;
- Destruction sphere specialization, including +1 sphere CL and level-gated powers;
- Sword Birth arena data, enhanced armory budget, trick pool, ten Lingchi-specific tricks, ordinary Combat Feat arsenal trick, and repeatable Extra Arsenal Trick feat (PCGen gates at levels 1, 5 and 20, plus specialized save/reload);
- Human and Half-Elf favored class magic talent options (six selections per talent; controller gates and removal, plus Human save/reload); Elf favored class metamagic feat (six selections per feat, choice, removal); Aasimar favored class Spellcraft bonus (two selections per +1, controller gate and save/reload); Tiefling favored concentration variable (two selections per +1, controller gate and save/reload; not wired to an actual concentration-check action); Gnome's Destruction-specific DC bonus (six selections per +1, gate and save/reload); Half-Orc's Aberrant bloodline-strength bonus (five selections per +1, gate and save/reload); Halfling's Channel Energy and Destruction Movement Burst use bonuses (two selections per +1, separate controller, removal and save/reload gates); Orc's Destruction Movement Burst use bonus (two selections per +1, controller, removal and save/reload gates). Dwarf item creation reward has a tested pool, but no validated eligible crafting feat choice.

The extended source package is **not complete**. The following historical list is
**not required for thin Incanter class completion**:

The option-by-option completion contract, Ultimate-vs-Original boundary and
dependency inventory are tracked in [incanter-completion-audit.md](incanter-completion-audit.md).

1. **Special familiars** — add choices, prerequisites/costs, master-level scaling and save/reload coverage.
2. **Remaining sphere specializations** — implement every current wiki sphere specialization after or alongside its underlying sphere data.
3. **Sphere sub-specializations** — add all sub-specialization selections, exclusivity, prerequisites and level gates.
4. **Sword Birth ordinary Armorist arsenal tricks** — add the ordinary arsenal tricks usable through Sword Birth, not only Lingchi-specific tricks.
5. **Sword Birth arena weapon/property selection** — record legal arena weapons/properties, enforce enhancement budgets and avoid applying arena-only properties to normal equipment.
6. **Non-Core domain and subdomain choices** — add current normal-game options from the wiki corpus; do not grant domain spells unless explicitly granted.
7. **Non-Core bloodline choices** — add current normal-game options and required subchoices; grant powers only unless explicitly granted.
8. **Casting traditions integration** — implement traditions, drawbacks and boons needed for legal Incanter builds, including casting ability and resource changes.
9. **Spheres feat eligibility and grants** — add remaining current Spheres feats, tag valid Incanter bonus-feat choices, and implement persistent grants/prerequisites.
10. **Archetypes** — add current normal-game Incanter archetypes and class-feature replacements/conflicts.
11. **Favored class options** — add remaining Incanter favored-class bonuses and verify per-level effects and reload; Human, Half-Elf, Elf, Dwarf (pool only), Aasimar, Tiefling (variable only), Gnome (Destruction only), Half-Orc (Aberrant bloodline only), Halfling (Channel Energy and Movement Burst only) and Orc (Destruction Movement Burst only) choices have targeted controller gates.
12. **Specialized character save/reload coverage** — existing Sword Birth, domain, Core bloodline, mercy/channel and selected favored-class builds have gates; add special familiar, other sphere specialization, traditions, archetypes and remaining choices.
13. **Completion audit** — compare data against current wiki page(s), record any intentionally skipped ambiguous/unusable option, then mark complete.

### Conscript status

This historical missing-class status is superseded by the thin Conscript class
implementation documented above. Full Spheres of Might content remains outside scope.

### Sphere implementation status

Spheres of Power is represented only by a narrow Destruction slice:

- Destruction Sphere;
- Searing Blast;
- Epicenter;
- Gather Energy;
- Admixture;
- prototype Destruction variables/export fields.

All other Power spheres are missing. Destruction itself is incomplete; most blast
types, blast shapes, advanced talents, drawbacks, prerequisites and detailed
interactions are not yet implemented.

Spheres of Might spheres are **not implemented**. There is no practitioner engine,
combat talent pool, martial tradition model, Might sphere data, Conscript class,
or Might fixture yet.

### Current verified commands

ThinkPad-only checks using the private JDK/toolchain setup documented below:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_smoke.py all
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py all
python3 /bigdisk/programming/pathfinder1e/tools/build.py test
```

Additional targeted Incanter gates currently available:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py incanter1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py incanter20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py specializations3
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py specializations20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py domains1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py domains20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py bloodline1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py bloodline20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction3
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction8
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py sword1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py sword5
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py sword20
```

The combined broad gate command intentionally remains narrow: it covers selection,
duplicate rejection and core isolation only. It does not imply Incanter completion.

## Destruction specialization and Sword Birth — 2026-09-22

Added Destruction specialization: three-point purchase, two-unit activation,
automatic base sphere, sphere-only +1 caster level, Intense Magic at 3,
Penetrating Blast at 8, and Indestructible at 20. Direct PCGen gates passed at
levels 1, 3, 8 and 20, checking free sphere grants, CL isolation, level gates,
resource scaling, duplicate rejection and removal. Precision immunity and the
negative-HP death threshold are included in the capstone description; core
critical-hit and sneak-attack immunities are automatic grants. The altered death
threshold is not wired into a general HP/death calculation.

Added Sword Birth purchase/activation, armory arena parameters and action
progression, enhanced-armory budget, one arsenal-trick choice per five levels,
and all ten Lingchi-specific tricks. Direct PCGen gates passed at levels 1, 5
and 20 for budgets, prerequisites, grants, overspending and removal.
This does NOT yet include the ordinary Armorist arsenal trick catalog or a
weapon/property selection path for created arena weapons. Arena effects are
recorded as situational abilities rather than bonuses to unrelated equipment.

Commands (ThinkPad only):

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction3
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction8
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py destruction20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py sword1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py sword5
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py sword20
```

Incanter is still incomplete: special familiars, other sphere specializations
and sub-specializations (which need their underlying spheres), ordinary arsenal
tricks and arena weapon properties, non-Core domain/bloodline choices, traditions,
feat eligibility, archetypes and favored-class choices. New specialization
save/reload is not covered by these controller gates. Earlier completion claims
must not be inferred from passing the narrower prototype tests.

## Incanter domain, bloodline and Admixture increment — 2026-09-22

Added 33 Core domain adapters, ten Core bloodline adapters, and Admixture Adept.
Adapters reuse vendored abilities without granting domain spells or bloodline
arcana, spells, bonus feats, or class skills. Domain purchases cost one point;
bloodlines and Admixture cost two. Each requires a separate activation selection.
No multiclass implementation is added.

Actual ThinkPad PCGen checks passed for paired Air/Fire domains at levels 1 and
20: powers, DC/uses, independent level scaling, capstones, duplicate rejection,
and removal. Aberrant bloodline checks passed at levels 1 and 20: power level
gates, casting modifier, no prohibited grants, second-bloodline restriction,
and removal. Admixture checks cover automatic talent grant, pool scaling and
removal without increasing the ordinary talent budget. Other domain/bloodline
choices are generated and parsed but their individual powers and companion
subchoices have NOT all been integration-tested. Specialized save/reload remains
unverified. This is not full Incanter completion.

Commands (ThinkPad setup only):

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py domains1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py domains20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py bloodline1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py bloodline20
```

Still missing: non-Core domains/subdomains and bloodlines, special familiars,
Sword Birth, sphere specializations/sub-specializations, casting traditions,
remaining feat eligibility, archetypes and favored-class choices. These remain
implementation work, not completed or silently excluded options.

## Incanter specialization implementation — 2026-09-22

Implemented Channel Energy (positive/negative choice, dice, uses and DC), Lay on
Hands (level-2 grant and level-scaled healing/uses), Merciful Healer (existing
PCGen mercy options, level prerequisites and pool), and standard Familiar (existing
PCGen familiar list/master-level support). Master of Mysteries remains implemented.
Rules checked against the Ultimate section of the wiki Incanter page on this date.

Specializations now separate level-1 purchase from activation. Purchase spends the
five-point budget and forfeits bonus feats. Activation requires the corresponding
purchase and spends from two activation units at level 1, four at 3, six at 5.
Current one-point specializations use one unit; two-point specializations use two.
This allows choosing the activation order while preventing simultaneous benefits
before they unlock. Future three-point sphere/sword specializations must consume
TWO activation units, not three. No multiclass handling is added.

Compatibility: an older saved Master of Mysteries purchase must now also select
Active Master of Mysteries to receive its benefits. This deliberately fixes the
old automatic-activation behavior; no saved file is rewritten automatically.

Actual PCGen gates passed at levels 1, 3 and 20. They cover purchase/activation
prerequisites, inactive level-1 lay on hands, activation-budget rejection,
positive/negative channel choices, channel scaling, familiar master levels,
mercy selection/prerequisite scaling, five-point feat forfeiture and removal.
Evidence under project build: `pcgen-spheres-915cujeb`, `pcgen-spheres-arjfbhqu`,
`pcgen-spheres-d2rr2bqp`. New controller tests do not yet certify specialized
character save/reload or familiar companion-file generation.

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py specializations3
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py specializations20
```

Incanter is still incomplete: non-Core domains/subdomains and bloodlines,
special familiars, Sword Birth, sphere specializations/sub-specializations,
traditions, remaining feat eligibility, archetypes and favored-class choices.
Existing generic-class feat prerequisites may also need adaptation for Incanter
grants. These are unfinished, not deliberately skipped spheres.

## Implemented Incanter bonus-feat increment — 2026-09-22

Added the class bonus-feat pool (level 1 and every even level), independently of
ordinary character feats. Added repeatable Extra Magic Talent and Extra Spell
Points with actual talent/spell-point grants and removal. The pool admits tagged
Incanter feats and existing item-creation/metamagic feats; the rest of the eligible
Spheres feat catalog is still pending. Extra Magic Talent currently requires our
casting core; Basic Magic Training is not yet implemented.

Added a five-point specialization pool, the cumulative specialization-cost
bonus-feat forfeiture formula, and Master of Mysteries with daily-round calculation
and level-dependent rules description. Only this specialization is implemented;
multiple-specialization activation ordering is still pending. Its selection is
restricted to level 1; saved selections persist rather than being reselected at
higher levels. This is not yet a complete specialization system or Incanter.

Rules checked against the current wiki Incanter and Extra Feats pages on this date.
Targeted actual PCGen gates passed at levels 1 and 20: bonus-pool budgets, no
ordinary-feat spending, repeatable talent grants, removal/refunds, spell-point
grants/removal, and level-1 overspend rejection. Level 1 additionally verified
Master of Mysteries costs two specialization points, forfeits the first bonus
feat, provides five daily rounds with modifier +4, and restores the feat on removal.
Evidence under project build: `pcgen-spheres-9jqv4woq`, `pcgen-spheres-27ooyidj`.

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py incanter1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py incanter20
```

Remaining Incanter work includes other specializations, their activation ordering,
traditions, eligible feat coverage, archetypes and favored-class choices. No claim
that the entire class is complete. Multiclassing remains deferred.

## Authoritative work order — user revision, 2026-09-22

This supersedes earlier implementation-order recommendations in this document
and the original plan:

1. Finish Incanter completely, including its normal-game class choices and the
   casting/resource support needed for single-class characters.
2. Finish Conscript completely, including its normal-game class choices and the
   martial/resource support needed for single-class characters.
3. Implement the Power and Might sphere catalogs.
4. Only then address the remaining classes.
5. Defer multiclass implementation and verification until every class is implemented.

Guile is excluded. Continue using current/newest normal-game wiki options;
mythic and gestalt remain excluded. UX, performance work, packaging and broad
upstream tool repair are not tasks. Implement shared mechanics only as required
by the current class or sphere, not as a separate generalized-engine project.

If a particular sphere is disproportionately complicated, record its name,
specific unimplemented mechanics, blocking reason and any partial coverage here,
then skip it and continue the catalog. A deferred sphere is not complete.

### Deferred spheres

None explicitly deferred yet. Unimplemented catalog entries are not automatically
classified as deferred; record an entry when a concrete sphere is skipped.

## Current implementation increment — 2026-09-22

Scope is normal-game PF1e Spheres options on the wiki, preferring current/newest
versions. Mythic, gestalt, UX polish and unrelated tooling remain excluded.

Incanter's unspecialized caster/talent/spell-pool progression now extends through
level 20. The existing class key is retained for saved-character compatibility.
The current Ultimate Incanter table and Magic Talents/Spell Pool sections were
checked at `https://spheresofpower.wikidot.com/incanter` on 2026-09-22.
This is NOT yet a complete Incanter: bonus-feat choices, specializations,
traditions and other class options still need implementation.

Added a one-choice Casting Ability pool with Intelligence, Wisdom and Charisma
options. Existing fixtures without a selection keep their INT fallback. This is
the ability-choice component, not an implemented casting tradition system.

Actual PCGen exports, talent spending and save/reload passed for level 20/WIS18
and level 3/CHA18 (with different INT scores to detect accidentally retained INT).
Evidence: project build directories `pcgen-spheres-6agf405e` and
`pcgen-spheres-qffw3rjz`. Level 20 exports CL20, 32 talents, 24 spell points and
Destruction DC24; level 3 exports CL3, 7 talents, 7 spell points and DC15.
Generated fixtures support every level 1–20 and each mental casting ability;
that availability is not a claim all 60 combinations were run through PCGen.

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_smoke.py progression --level 20 --casting WIS
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_smoke.py progression --level 3 --casting CHA
```

Eleven first-party tests and all existing regression suites passed. Selection,
duplicate and core-isolation gates passed again. ThinkPad setup remains unchanged.
Next: implement Incanter bonus-feat grants and casting traditions, then remaining
class options and Destruction content. Multiclass/low/mid-caster models remain
unimplemented; the expanded high-caster calculation is not proof of those models.

Earlier dated entries below describe previous prototype limitations and evidence.

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
not a complete Incanter. The immediate selection/isolation gates below are now
complete for this slice; traditions, martial progression and catalog expansion
remain separate work. Broad upstream tests remain out of scope. Spheres of Might
is not implemented.

Ten first-party tool tests cover gate evidence, isolation comparisons, fixture coverage, exact selection evidence,
missing/oversized/mismatched-export,
load-error and unsupported-case rejection coverage. These are separate from the
actual PCGen smoke result above.

### Immediate gates completed — 2026-09-22, ThinkPad only

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py all
```

This first-party driver uses the existing PCGen batch loader and the production
`CharacterAbilities` selection controller used by the character facade, not a
replacement eligibility implementation or the upstream JUnit harness. The Java
driver is compiled into the isolated build directory with the private JDK; no
vendored Java is edited. A recording console delegate captures only expected
selection rejection messages and verifies their exact PCGen message keys.

Verified gates:

- **Prerequisites:** Searing Blast, Epicenter and Gather Energy are each rejected
  without Destruction, with zero grants/spending. After buying Destruction, each
  qualifies, is added successfully, and costs one point. Removing talents refunds
  points; removing Destruction revokes the prerequisite. A core Fighter cannot
  select Destruction itself (caster-level prerequisite).
- **Duplicates:** repeated Destruction, Searing Blast, Epicenter and Gather Energy
  attempts each produce PCGen's duplicate rejection, with unchanged selection
  count and spending. Tests deliberately leave points available so lack of points
  cannot masquerade as duplicate enforcement.
- **Core isolation:** the same Human Fighter 1 is loaded in separate processes
  with Core alone and Core plus Spheres. Both exports match the fixed baseline:
  level 1, BAB 1, HP 12, Fort +4, Reflex +1, Will +0, AC 11. Snapshots of stats,
  modifiers, save/AC bonuses and feat pools also match. Neither gains Spheres
  caster level, talents, spell points or the casting-core ability. The augmented
  run proves the Spheres category was loaded but has zero pool/selected talents.

Initial passing evidence under `/bigdisk/programming/pathfinder1e/build`:
`pcgen-spheres-eggcfbsx` (selection), `pcgen-spheres-zshi3gef` (Core), and
`pcgen-spheres-hvstr5wz` (Core + Spheres). Subsequent runs print fresh paths.

Scope: controller-level enforcement without opening GUI windows; not validation
of deliberately malformed PCG imports. Isolation covers this representative
core fixture and recorded fields, not every core class or every possible statistic.
No new game-rule behavior was needed to pass these gates.

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
   Selectable Spheres character traits are documented separately in
   `docs/spheres-traits.md` (partial automation and manual approvals).
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