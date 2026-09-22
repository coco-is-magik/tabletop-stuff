# Spheres PCGen prototype — current handoff

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

2026-09-22 bounded upstream attempt:

```sh
timeout 30s /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10/gradlew --offline --no-daemon -p /bigdisk/programming/pathfinder1e/vendor/upstream/pcgen-6.08.00RC10 compileJava --console=plain
```

FAILED during configuration at build.gradle:221: required Java 16 toolchain is
not available locally; offline auto-download cannot resolve the cached resource.
Unlike the earlier attempt, plugin configuration progressed. No upstream build,
dataset load, talent selection, save/reload or character export has passed.
Do not claim milestone 1 or the vertical slice is accepted from static checks.

## Acceptance procedure

1. Provision the pinned build's Java 16 toolchain/dependencies without changing
   upstream sources. Build PCGen and run its data tests.
2. Copy the prototype data directory to a separate PCGen user-data directory;
   leave the vendored tree untouched. Load it alongside Pathfinder Core Rulebook.
   Require zero parse/unresolved-reference errors. A core-only character must
   retain identical statistics before/after loading this source.
3. Build human prototype Incanters at levels 1 and 2 with final INT 18, then a
   level-1 case with final INT 7. Use ordinary progression rules, no equipment,
   traits, specializations, or external CL bonuses. Select Destruction first.
   Verify the other three talents are unavailable without it, become selectable
   with it, cost one each, and cannot be selected twice. Check pool remaining.
4. Save/reload and export through `spheres_export.txt`. Compare to the corresponding
   case in `/bigdisk/programming/pathfinder1e/testdata/spheres/expected.json` using
   the first-party verifier. The export exposes total talent budget, not remaining
   selections; selection behavior requires the separate checks above.
5. Only after actual PCGen evidence passes, expand traditions, a complete
   Destruction sphere, then a representative martial sphere as the plan requires.

Next action: resolve the toolchain blocker and validate the LST with real PCGen.
Do not mass-import talents or introduce Java changes on the assumption LST fails.

## First-party checks completed

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

That export has not yet been generated. The expected JSON is not an export.