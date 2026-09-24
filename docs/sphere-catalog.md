# Power and Might basic catalog

## Status — 2026-09-24

**Catalog coverage implemented; full requested mechanical implementation incomplete.**

The campaign loads 53 base spheres: 26 Power and 27 Might, including the separately
listed supplemental spheres. There are 2,330 basic talent entries, of which four
retain their existing Destruction records and 2,326 are new generated records.
Names are sphere-qualified to avoid collisions. Existing character/class keys and
manual records remain unchanged. Advanced/legendary talents, Original Power rules,
feats, archetypes and Guile catalogs are not imported.

Each new talent has its source rules description, source attribution, base-sphere
prerequisite and the appropriate magic/combat selection category. Tactical actions
remain table-resolved. **That does not mean all persistent effects have been
implemented.** Full rules descriptions must not be mistaken for automation.

### Currently automated

- Base and talent selection through the existing PCGen pools; duplicate rejection
  for nonrepeatable records, spending/refunds and character persistence.
- Explicitly recognized repeatable wording and repeat caps; special repeat
  prerequisites still need a complete per-talent audit.
- Eight package pools: Alchemy, Athletics, Beastmastery, Guardian, Leadership,
  Nature, Tinker and Pilot. Expansion talents contribute package choices.
- Equipment's free talent pool, separate from ordinary combat talent spending.
- Base skill-rank grants for Alchemy, Fencing, Gladiator, Scoundrel, Scout, Trap,
  Warleader and Leadership; Athletics and Beastmastery package skill ranks.
- Per-Power-sphere CL/DC variables, selected combat resource formulas, Life cure
  formulas, Shield Training and Finesse Fighting grants, and selected base feats.

### Still required to satisfy the full request

- Complete talent-by-talent persistent mechanical effects, including Equipment
  proficiency groups/armor, unarmed damage progression, skill/stat bonuses and
  associated-skill overlap rules.
- All free grants, subchoices, package edge cases and special repeat conditions.
- Companion/gizmo/veil character-building choices and derived statistics where
  required; tactical resolution remains outside PCGen.
- Real tradition grants and class sphere-specialization integration from the
  approved plan. Existing manual class records have not been replaced.
- Runtime tests for those mechanics. Testing one ordinary talent per sphere is
  not certification of every talent.

## Reproducibility and verification

Source snapshots and their hashes are under
`/bigdisk/programming/pathfinder1e/testdata/spheres/catalog-source`.
Explicit Ultimate/basic section bounds and the deterministic manifest are managed
by `/bigdisk/programming/pathfinder1e/tools/spheres_catalog.py`.
Reviewed mechanical overrides are in
`/bigdisk/programming/pathfinder1e/data/spheres/catalog-mechanics.json`.
Generation uses only local snapshots; character loading never accesses the wiki.
OGC attribution/license notices are retained in
`/bigdisk/programming/pathfinder1e/data/spheres/catalog-OGL.txt`.
The repository LICENSE was not changed.

```sh
python3 /bigdisk/programming/pathfinder1e/tools/spheres_catalog_lst.py
python3 /bigdisk/programming/pathfinder1e/tools/test_catalog.py
python3 /bigdisk/programming/pathfinder1e/tools/test_spheres.py
python3 /bigdisk/programming/pathfinder1e/tools/test_conscript.py
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_catalog.py might --offset 0 --count 3
```

Run JVM cases sequentially; each catalog command has save and reload processes.
Use offsets/counts to cover 26 Power or 27 Might spheres, at most five per command.
All 53 spheres have passed base plus one-talent controller round trips. Dedicated
checks also cover Athletics package persistence, Equipment free talent persistence,
Finesse Fighting repeat cap/refund and Fencing 5/10 skill ranks. Selected combat
resource formulas have controller checks. Eight catalog tests and the existing
34+3 Python tests pass. Core Fighter isolation and bounded level-10 Incanter WIS
budget-3 and Conscript WIS budget-3 regressions passed with the catalog loaded.

Failures, remaining work and evidence notes:
`/bigdisk/programming/pathfinder1e/docs/sphere-catalog-work.md`.