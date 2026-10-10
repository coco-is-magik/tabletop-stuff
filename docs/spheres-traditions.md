# Custom Spheres traditions — 2026-09-24

The `/bigdisk/programming/pathfinder1e/data/spheres/spheres.pcc` dataset includes
custom-tradition choices alongside the existing Spheres class and talent pools.
The source text is pinned in
`/bigdisk/programming/pathfinder1e/testdata/spheres/catalog-source/casting-traditions.json`
and `/bigdisk/programming/pathfinder1e/testdata/spheres/catalog-source/martial-traditions.json`.

## Casting

Select **Custom Casting Tradition** with a casting class, then choose a casting
ability from the existing INT/WIS/CHA pool. The new general-drawback pool has
five points, with the original fourteen drawback choices: Verbal Casting,
Somatic Casting (one copy), Focus Casting, Magical Signs, Prepared Caster,
Draining Casting, Addictive Casting, Area Bound, Bonded Casting, Charged
Spells, Mental Focus, Terrain Casting, Unsettling Casting, and Vampiric
Casting (the last eight added 2026-09-25 so feat prerequisites can reference
them; several are third-party-sourced — see their records). Extended Casting
now costs and awards two points, and has a separately gated second selection
for four total points. Somatic Casting also has a separately gated second
selection, costing and awarding one additional point. Existing first-selection
keys remain unchanged. The original choices each provide one point in the
casting-boon pool. Easy Focus, Fortified
Casting (requires Draining Casting), and Metamagic Expert each cost two points.
Unspent drawback points give bonus spell points according to the Ultimate
1–5-point table; removing choices reverses the pool and spell-point awards.
Remove dependent boons before removing the drawbacks that funded them.
No custom tradition is required to cast: characters can keep their existing
class casting ability and pool without selecting one.

This is **partial** coverage. Charged Spells now supplies its additional
boon-only credit. Boon purchases use that credit before ordinary credits;
unused boon-only credits never increase spell points.
Prepared Caster and Charged Spells are now mutually exclusive in either
selection order.

**Sphere-specific drawbacks** (2026-10-07) are generated from the same pinned source
by `tools/spheres_traditions.py` into `spheres_sphere_drawbacks.lst` and
`spheres_categories_sphere_drawbacks.lst`: 161 records across 24 spheres. Each record
requires its base sphere (`PREABILITY:...Spheres Magic Talent,<Sphere> Sphere`) and
grants one talent restricted to that sphere through a generated per-sphere pool
(`Custom <Sphere> Drawback Talent`, `TYPE:SpheresBasicTalent.<Sphere>`), so the
granted talent cannot be spent on another sphere. Where the source *pins* the bonus
talent ("you must select the Hemokinesis talent with the bonus talent"), the
drawback grants that exact talent automatically instead of leaving a free pick.
Declared incompatibilities are
compiled to symmetric `!PREABILITY` tags when their names resolve to another
generated drawback; incompatibility prose that names no record (for example "Any
Conjuration drawback that affects the summon ability") is left to the table rather
than guessed. `Striker` is deferred: it grants a specific talent chosen by a sphere
the character already has, which needs a choose-sphere mechanic.

Drawbacks that forbid acquiring talents ("you cannot take the Ranged Enhancement
talent", "you may not select … Undead Whisperer or Master's Presence") are
enforced: `tools/spheres_traditions.py` scans each drawback's pinned text for
clauses containing an acquisition denial (*cannot / can not / may not / nor can you*
+ *gain / take / select / choose / learn*), matches them against the catalog's real
talent names for that sphere, and emits
`CATEGORY=Spheres Magic Talent|<Sphere> - <Talent>.MOD` lines carrying the
`!PREABILITY` blocking tag (`spheres_sphere_drawback_restrictions.lst`). Only names
that resolve to a real record are encoded, so tag-based and prose restrictions
("[space] talent", "talents that alter an aspect of weather", "only [cognition]
talents") stay rules text.

Incompatibility is symmetric: every declared `Incompatible:` pair is emitted in
**both** directions (`tools/test_traditions.py::test_incompatibilities_are_symmetric`),
so a drawback is excluded whether the character takes it first or second.

Boons are now complete against the source (all 20 publish a record, including the
newly added Bound Creature, which grants the Conjuration sphere, and Wild Will,
which is repeatable with a chosen environment). **Oathbound Casting** is modeled
through the complete pinned Oath list, not just the five it names inline: the
wrapper is the drawback itself (`COST:0`), and all 24 published Oaths **grant**
drawback points equal to their oath-point value — from Oath of Loyalty (1) and
Oath against Mercy (2) up to Oath of Offerings (7) and Oath of Poverty (10).
`Forbidden Knowledge`, whose value is "2 or 4 by severance", is emitted as two
records. An Oath counts as that many drawbacks ("counts as a number of drawbacks
equal to the number of oath points they are usually worth"), so it adds to the
drawback total and to the boon credits; it never *costs* drawback points. The
Oaths are mutually exclusive, since exactly one Oath is sworn. The five the
drawback names (Harm, Mercy, Loyalty, Secrecy, Silence) are freely selectable; the
other 19 require a `Reviewed - <Oath>` record in `Spheres Oath Adjudication`,
matching the source's "With GM permission, other Oaths or paladin/antipaladin codes
can be selected as well." Values come from
`tools/spheres_traditions.py::oaths`, pinned from the Oaths page rather than
hard-coded, so a changed
source raises rather than silently drifting. Three general drawbacks remain
deliberately excluded because their mechanics need subsystems rather than a record:
Card Casting (deck allocation), Singular Pool
(pool coupling) and Catastrophic Failure (reroll denial plus an eligibility check).
Other casting modifiers, GM approval, concentration/action restrictions, and bonus
effects of listed boons remain rules text. Do not use these records to represent an unsupported combination;
record and adjudicate it with your GM instead. Tradition choices belong at
first casting-class level under the source rules; the PCGen record does not
enforce the timing of a later respec. General drawbacks are **not capped**: the
selection pool is larger than the total published drawback cost, because the
source caps only the *spell-point benefit* at five drawbacks, not the number a
caster may take. Boons cost two drawback points each and any number may be taken
while points remain. This is not a full modeling of all source traditions. Remove
second-tier selections
before their first tiers; prerequisite loss does not delete dependent choices.

## Martial

Alchemy users can choose an existing Craft or Profession skill under
`Alternative-Brew associated skill (GM approval)`. This is a configurable
drawback, not a named-tradition preset. It awards no talent and changes granted
ranks and the associated-rank input to Alchemy calculations. Field Medic's Heal
exception is mutually exclusive. Obtain GM permission before choosing, changing
or removing it; the selector does not adjudicate that permission.

For a Conscript, select **Custom Martial Tradition** instead of the existing
**Martial Tradition (Manual)** record. It grants Equipment Sphere automatically;
that sphere already grants one free Equipment talent. Choose one more from
Custom Martial Equipment, one base sphere from Custom Martial Sphere, and a
thematic base sphere or basic talent from Custom Martial Theme. The three
additional grants and the Equipment sphere's free talent do not consume paid
Conscript combat talents. These pools use the existing talent records, including
their sphere prerequisites. The theme must match the approved concept; this is
not enforced by PCGen. The base-sphere pool does not itself exclude Equipment,
so choose a non-Equipment base sphere in accordance with the source guidelines.

Only Conscript's existing first-level tradition slot is wired here. Other
practitioner classes, alternative martial-tradition structures, GM exceptions,
starting-equipment/proficiency trades, and individual talent effects still
require manual adjudication. Do not select both the custom and manual Conscript
tradition records.

### Named traditions and expanded casting options

September 30 update: all 66 named martial traditions have generated records.
Liturgist reuses Basic Magic Training with a Death/Fate/Life selection instead
of an unrestricted sphere, Followers, weighted Custom Training weapon choices,
and Base Of Operations or an Equipment talent. Core weapon choices, costs,
removal and persistence are verified; the required favored weapon of the deity
or philosophy still requires player/GM verification. This count is not a claim
of complete tradition mechanics. Current evidence and limitations are recorded
in `/bigdisk/programming/pathfinder1e/docs/spheres-backlog.md`.

The campaign now loads 50 named martial traditions generated by
`/bigdisk/programming/pathfinder1e/tools/spheres_martial_traditions.py`.
Fixed grants and restricted variable choices reuse existing combat abilities.
Fixed Equipment talents consume the sphere's free first-talent allowance;
fixed packages likewise replace, rather than supplement, the free package.
Discipline choices are derived from published discipline headings. These
traditions use Conscript's existing tradition slot; they do not yet implement
other classes' proficiency exchanges or missing Equipment talent effects.
The remaining source traditions need linked choices, drawback adapters,
feat substitutions, or repeated fixed grants and are not silently approximated.

`/bigdisk/programming/pathfinder1e/tools/spheres_traditions.py` adds general
drawbacks, seven second selections, conditional boons, symmetric incompatibilities,
weighted Addictive/Vampiric Casting, Benefactor and Spell Stand-In grants, and
Fortified Casting's higher-Constitution modifier. The repeatable Drawback Feat
boon opens a separate pool of existing drawback feats, retaining prerequisites.
Oathbound Casting selects one of the complete pinned Oath list, named
`Tradition - Oathbound Casting: <Oath> (<N> drawback point[s])` so the value is
visible in the ability list and the choices sort beside their wrapper. The
description also leads with the grant, e.g. "Grants 10 drawback points (counts as
10 drawbacks and costs none)". Each Oath grants its published number of drawback
points (it costs none) and the Oaths are mutually exclusive. The five the drawback
names are freely
selectable; the other 19 require GM approval through a `Reviewed - <Oath>` record
in `Spheres Oath Adjudication`. Card Casting,
Singular Pool and Catastrophic Failure remain excluded until their variable credits
or eligibility checks are represented. Conditional boon effects and casting action
restrictions remain table rules.

Live power gates passed in
`/bigdisk/programming/pathfinder1e/build/pcgen-spheres-yuyst9o3` and martial gates in
`/bigdisk/programming/pathfinder1e/build/pcgen-spheres-fyisbzi4`.
They cover grants, paid-pool isolation, fixed-package accounting, invalid feat
prerequisites and refunds. The saved fixtures retain the original custom choices;
named choices are exercised and removed in both phases, not persisted themselves.

## Live checks

Run from any working directory:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_traditions.py power
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_traditions.py might
```

The real PCGen selection controller checks purchase limits, a rejected choice,
drawback/boon spell points, free martial grants, removal/refunds, and save/reload
for each sample. This does not verify the many unimplemented tradition options.

September 29, 2026: three offline tradition regressions were added to the normal
build. The live power save/reload gates passed in
`/bigdisk/programming/pathfinder1e/build/pcgen-spheres-ocyio46v`, covering weighted
Extended Casting awards/refunds, second-tier prerequisites, duplicate rejection,
two Somatic selections and both preparation-incompatibility selection orders.
The saved fixture retains the original Verbal/Somatic/Easy Focus combination;
the new choices are exercised and removed during each gate, not persisted.