# Custom Spheres traditions — 2026-09-24

The `/bigdisk/programming/pathfinder1e/data/spheres/spheres.pcc` dataset includes
custom-tradition choices alongside the existing Spheres class and talent pools.
The source text is pinned in
`/bigdisk/programming/pathfinder1e/testdata/spheres/catalog-source/casting-traditions.json`
and `/bigdisk/programming/pathfinder1e/testdata/spheres/catalog-source/martial-traditions.json`.

## Casting

Select **Custom Casting Tradition** with a casting class, then choose a casting
ability from the existing INT/WIS/CHA pool. The new general-drawback pool has
five slots, with six individually selectable drawbacks: Verbal Casting, Somatic
Casting (one copy), Focus Casting, Magical Signs, Prepared Caster, and Draining
Casting. Each provides one point in the casting-boon pool. Easy Focus, Fortified
Casting (requires Draining Casting), and Metamagic Expert each cost two points.
Unspent drawback points give bonus spell points according to the Ultimate
1–5-point table; removing choices reverses the pool and spell-point awards.
Remove dependent boons before removing the drawbacks that funded them.
No custom tradition is required to cast: characters can keep their existing
class casting ability and pool without selecting one.

This is **partial** coverage. The other general drawbacks and boons, doubled
drawbacks, repeats (including a second Somatic Casting), sphere-specific
drawbacks, other casting modifiers, source incompatibilities, GM approval,
concentration/action restrictions, and bonus effects of listed boons are not
automated. Do not use these records to represent an unsupported combination;
record and adjudicate it with your GM instead. Tradition choices belong at
first casting-class level under the source rules; the PCGen record does not
enforce the timing of a later respec. The list is capped at five *selected*
drawbacks, not a full modeling of every possible five-point tradition.

## Martial

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

## Live checks

Run from any working directory:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_traditions.py power
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_traditions.py might
```

The real PCGen selection controller checks purchase limits, a rejected choice,
drawback/boon spell points, free martial grants, removal/refunds, and save/reload
for each sample. This does not verify the many unimplemented tradition options.