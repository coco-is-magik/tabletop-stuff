# Power/Might feats — implementation status

This is a **partial implementation, not completion of all feat mechanics**.

The pinned inventory contains 1,201 distinct feat names from 29 feat pages and
the 53 existing Power/Might sphere pages. It includes third-party and crossover
entries present on those pages; their presence is not a claim that their external
systems are implemented. Original-tab entries without current TOC anchors are
excluded. First current occurrence wins when pages duplicate a feat. Source URLs,
headings, rules, compiled prerequisites and unresolved clauses are retained in
`/bigdisk/programming/pathfinder1e/data/spheres/feat-catalog.json`.

## Supported

- Normal feat selection and Combat/Teamwork/Metamagic/ItemCreation types.
- Exact recognized stat, level, BAB, magic skill bonus, skill rank, sphere,
  talent, package and feat prerequisites. Fully recognized OR clauses remain OR.
- Existing Extra Magic Talent, Extra Spell Points and Extra Arsenal Trick keys
  remain unchanged. Extra Combat Talent is no longer incorrectly Conscript-only.
- Sphere Focus and Combat Sphere Focus have separate per-sphere records and
  apply their DC bonus only to that sphere.
- Combat Sphere Specialization changes the selected sphere's effective BAB,
  capped at character level, without changing attack BAB. Existing calculated
  combat resources use that sphere BAB. Other prose effects remain manual.
- Counterspell chain qualification, range and additional-effect/burst variables.
- Great Focus qualification and focus-capacity variable.
- Basic Magic Training grants casting core, CL/MSB 1, one spell point and a
  separate base-sphere-only choice, without two free caster talents.
- Advanced Magic Training scales CL/MSB and spell points for the currently
  supported Incanter/noncaster class model. A partial custom tradition builder
  exists separately; it does not complete feat-driven tradition qualification.
- Fixed metamagic spell-point surcharges are exposed as feat variables, not
  permanently subtracted from the spell pool.
- Selected additional resource grants in
  `/bigdisk/programming/pathfinder1e/data/spheres/feat-mechanics.json`.
- Explicit unlimited and second-selection repeatability patterns.

## Unfinished / manual

584 feats have unresolved prerequisite clauses. They are blocked until their
specific zero-cost **Manual Feat Prerequisite Approval** is selected. Approval
does not grant the feat, its prerequisite abilities, or its effects. Recognized
clauses remain enforced. This is an explicit adjudication escape hatch, **not
automatic prerequisite implementation**.

Most feat-specific persistent effects, choices, grants, companion changes,
crafting workflows and external class mechanics are still unautomated. All
generated descriptions warn of this. Repeatable distinct targets use manual
text choices unless separate sphere records exist; target legality and special
repeat exceptions need further implementation. Class bonus-feat eligibility
uses source types and a conservative prerequisite-based Incanter classifier;
this is not a complete per-feat eligibility audit.

Basic Magic Training must be manually exchanged for Extra Magic Talent when
gaining a casting class. No automatic retraining or generalized multiclass
casting engine is claimed. Casting ability defaults to existing core behavior;
tradition-driven casting ability selection outside Incanter remains incomplete.
Core-name collisions receive a `(Spheres)` suffix instead of overwriting Paizo
feats. Cross-system equivalence with the original Core feat is not automated.

## Reproduction and validation

```sh
python3 /bigdisk/programming/pathfinder1e/tools/spheres_feats.py --write
python3 /bigdisk/programming/pathfinder1e/tools/test_feats.py
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_feats.py power
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_feats.py might
```

The live tests cover representative production-controller selection, rejection,
refund, resource math and save/reload; they do not test every feat individually.
Source fetching is separate from offline generation and character loading.

Verified September 24, 2026: 55 Python tests (10 feats, 8 catalog, 34 Spheres,
3 Conscript), package structure, both feat-controller round trips and Core
Fighter isolation passed. Early concurrent feat runs timed out and are not
counted as passes; the corrected, sequential runs passed.