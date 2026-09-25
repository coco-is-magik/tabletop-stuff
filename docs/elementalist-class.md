# Elementalist — partial base-class support (2026-09-24)

Rules: https://spheresofpower.wikidot.com/elementalist, Ultimate class section.
The pinned page is `testdata/spheres/catalog-source/elementalist.json`.

The `Elementalist` class key is enabled in the existing Spheres campaign. PCGen
calculates the 1–20 d8 / 3/4 BAB / three good saves chassis, class skills,
mid-caster level and magic skill bonus, class-level spell pool, 3/4-level
magic talents plus the two initial talents, free Destruction sphere, and
class-level Destruction caster level. It grants light armor, simple and martial
weapon proficiency, evasion/improved evasion, a separate combat-feat pool at
levels 2/6/10/14/18, dodge AC, four energy resistances (5/10/15/20),
DR 10/magic at level 20, and movement choices at levels 7/13/19. Manual
favored-element records can be selected at levels 3/9/15; these and movement
choices are saved through PCGen. Ordinary casting-ability choices and existing
Spheres magic talents use the shared categories.

**Not complete:** Favored-element blast-type groups are user-entered and not
validated against known groups; damage is not automatically applied to matching
blasts. Swim/fly/burrow movement is recorded as a calculated speed in the
selected ability's description and variable, not wired to PCGen's movement
types. Energy resistance and the capstone's critical/sneak-attack immunity are
rules text and are not applied automatically to incoming damage. Martial/casting
tradition grants and prerequisites, talent-specific effects and qualification,
race-specific favored class bonuses and multiclass behavior need adjudication.
Existing combat-feat prerequisites remain PCGen's responsibility. This slice
does not finish Elementalist. The other base classes now have
separate, partially automated records; see
`/bigdisk/programming/pathfinder1e/docs/spheres-classes.md`.
Regression and live checks:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/test_elementalist.py
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_elementalist_class.py --level 7
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_elementalist_class.py --level 20
```