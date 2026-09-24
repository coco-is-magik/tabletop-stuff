# Incanter — thin class contract

Scope fixed by the user on 2026-09-23. This supersedes the broad source-package audit.

## Class deliverable

- Levels 1–20: d6 HD, half BAB, good Will, poor Fortitude/Reflex,
  four base skill points, class skills and simple weapon proficiency.
- High caster level and magic skill bonus; INT/WIS/CHA casting selection.
- Spell points and magic talents, including the two initial casting talents.
- Bonus feat progression; Extra Magic Talent and Extra Spell Points are usable,
  repeatable choices. Class bonus feats do not consume general feat slots.
- Five specialization purchase points, tiered bonus-feat forfeiture, separate
  activation budget, prerequisites, duplicate/overspend rejection and refunds.
- Existing class-specific grants and calculated resources, with class selections
  and their effects preserved through PCGen save/reload.

Keep the saved-character class key `Incanter (Spheres Prototype)` and campaign key
`Spheres PF1e - Architecture Prototype` unchanged for compatibility.

## Not part of completion

No new sphere catalogs, domains, bloodlines, favored-race catalogs, companions,
archetypes, casting-tradition catalogs, Sword Birth equipment machinery, third-party
variants, other classes or general rules/action engine. Existing optional records
remain available without a claim that their external subsystems are complete.
PCGen class grants/descriptions do not claim combat simulation.

## Acceptance

The bounded class runner tests real PCGen class math, specialization forfeiture,
bonus feat effects and pool isolation, Master of Mysteries grants when purchased,
save/reload, and post-reload removal/refunds. It exports BAB and saves independently
of the class variables. Select one budget per invocation on constrained machines:

```sh
python3 /bigdisk/programming/pathfinder1e/tools/test_spheres.py
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_incanter_class.py --level 1 --points 0
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_incanter_class.py --level 5 --points 1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_incanter_class.py --level 10 --casting WIS --points 3
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_incanter_class.py --level 20 --casting CHA --points 5
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py incanter1
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py incanter20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py specializations3
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py specializations20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_spheres_gates.py isolation
```

The runner accepts any level 1–20, any mental casting ability, and budgets 0–5.
Omitting `--points` runs all six budgets sequentially. The existing gates' `all`
command also runs optional catalogs: it is deliberately **not** the class finish line.

## Verified completion — 2026-09-23

Thin class milestone complete. Live PCGen round trips passed for:

| Level | Casting | Specialization points |
| --- | --- | --- |
| 1 | INT | 0 |
| 5 | INT | 1 |
| 10 | INT | 2 |
| 10 | WIS | 3 |
| 20 | INT | 4 |
| 20 | CHA | 5 |

All six purchase tiers, all three casting choices, class bonus feats, calculated
grants and post-reload refunds are covered across these cases. Existing level-1
and level-20 feat gates, level-3/20 specialization gates, low-INT spell-pool
save/reload, and Core Fighter isolation also passed. The Python suite includes
class-fixture checks across all 20 levels; this is not a claim that every level
and budget combination was independently run through PCGen.

Four concurrent all-budget runs exceeded the outer 120-second limit during PCGen
startup/reload; those are not counted as passes. The bounded single-budget cases
above were subsequently run successfully. No catalog expansion was performed.