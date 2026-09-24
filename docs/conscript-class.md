# Conscript — thin class implementation

Class key: `Conscript`. Load Core Rulebook and the existing Spheres campaign.
Rules checked against https://spheresofpower.wikidot.com/conscript on 2026-09-23.

## Implemented boundary

- Levels 1–20, d10 HD, full BAB, good Fortitude/Reflex, poor Will, four base
  skill ranks, listed class skills plus three selected additional class skills.
- Simple weapons, light armor and bucklers; INT/WIS/CHA practitioner choice.
- Expert combat talents plus odd-level bonus talents; combat/teamwork bonus feat
  pool; repeatable Extra Combat Talent without spending ordinary feat slots.
- Five specialization points and the class's forfeiture table. Choices are made
  at level 1; unlike Incanter, no separate activation currency is introduced.
- Gear Training, Indomitable Will, Evasion, Fast Movement, Banner, Inspiration,
  Armor Training, Resolve, Sneak Attack and Studied Target. Permanent grants and
  numeric resources are calculated; target/action-specific effects remain descriptions.
- Named manual combat-talent and martial-tradition records persist in PCG files.
  Ordinary talents spend the class pool; tradition grants are recorded separately.
- Manual sphere specialization records account for three specialization points;
  the additional delayed specialization deducts the five specified bonus talents.

## Explicit limits — no catalog expansion

Manual means manual: sphere/talent prerequisites and effects, tradition grants,
sphere-only bonuses and specialization powers are not automatically evaluated.
No combat sphere catalog, companion engine, external class feature catalog,
archetypes or favored-race catalog was added. Other specialization options are not
implemented. This is a thin class implementation, not every published Conscript
option or a combat simulator. Multiclass interaction is outside this milestone.

## Verified PCGen evidence

Save/reload and refund cases: level 1 WIS / 0 points; level 5 INT / 1;
level 6 CHA / 2; level 10 WIS / 3; level 3 WIS / 4; level 20 CHA / 5;
level 1 WIS / 5. These cover three practitioner choices and all six budget tiers.
Additional level-20 profiles exercise Banner/Inspiration/Armor/Resolve and
Sneak Attack/Studied Target. The tests inspect actual selected class skills,
named manual records, feat/talent spending, proficiency and evasion level gates,
and removal/refunds. Python fixture tests cover every level 1–20.

```sh
python3 /bigdisk/programming/pathfinder1e/tools/test_conscript.py
python3 /bigdisk/programming/pathfinder1e/tools/test_spheres.py
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_conscript_class.py --level 1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_conscript_class.py --level 20 --mental CHA --points 5
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_conscript_class.py --level 20 --points 4 --features resources
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_conscript_class.py --level 20 --points 4 --features precision
```

The existing Incanter level-10 WIS/3-point round trip was rerun successfully with
Conscript loaded. Core Fighter isolation is retained; the isolation gate also
checks that non-Conscript characters receive no combat talent or class-feat pools.