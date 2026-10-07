# Sphere catalog implementation — work record

2026-09-24. Scope: PF1 Power and Might base spheres, basic talents and advanced
talents, not legendary talents, Guile, other classes or a combat simulator.

Preserve existing class/campaign/ability keys, manual saved choices, distinct magic
and combat pools, Core isolation, and PCGen as the only runtime rules evaluator.
Required acceptance: real choices, prerequisites, grants, persistent bonuses,
calculated resources, tactical descriptions, refunds and save/reload.

Current evidence: existing data has five Destruction entries and no combat sphere
catalog. Source inventory uses the wiki Power/Might navigation, including its
separately listed supplemental spheres. Original Power variants must not override
Ultimate rules. Need inspect heading boundaries before extracting basic talents.
The wiki declares applicable rules Open Game Content under OGL 1.0a; retain its
license and notices with any derived catalog, without changing the repo LICENSE.

Rejected: guessed talent names, cloning descriptions across spheres, and calling a
name-only list or manually entered text a complete implementation.

## Implemented and verified so far

Pinned 53 source inventories (26 Power, 27 Might), 2,330 basic talent entries,
including four preserved Destruction keys; 2,326 additional generated records.
The source bounds stop before legendary headings and exclude Original
tabs, feats, archetypes, and unrelated sections. Generated records contain actual
rules text, source attribution, basic-sphere prerequisites and separate pool types.
A later scope extension adds the 411 Ultimate-tab advanced talents in the same
files, tagged `SpheresAdvancedTalent` with compiled or approval-gated prerequisites.
The source manifest is not evidence that every talent mechanic is automated.

Live production-controller round trips have exercised each of the 53 base spheres
and one basic talent per sphere: missing-base rejection, duplicate base rejection,
pool spending, removal/refund, saving and reloading. Additional gates exercise
Athletics package selection/save, Equipment free talent/save, Finesse Fighting's
repeat count/cap/refund, and Fencing's 5/10 skill-rank scaling. Core Fighter
isolation passed after loading the catalog. Python class regressions: 34 + 3 pass.
Eight new catalog integrity tests pass.

Failures retained: four concurrent five-sphere runs exceeded their 50-second JVM
limits; replaced with sequential two/three-sphere runs, which passed. Initial
comma-bearing keys caused LST warnings; generated keys now remove commas. DESC
parentheses are escaped as brackets to avoid PCGen delimiter interpretation.
A campaign reference test wrongly required a final newline; changed to compare
reference lines. No selection test was weakened. An Incanter command without
`--points` ran all budgets and hit its outer 120-second limit after budgets 0–2;
do not count that as a complete class regression run.

Subsequent bounded Incanter level-10/WIS/budget-3 and Conscript
level-10/WIS/budget-3 commands passed. Corrected Athletics expansion to grant two
packages and Beastmastery expansion to match Extra Beastmastery Package. Corrected
Duelist bleed and Shield active-defense formulas directly against pinned rules;
runtime level-20 checks now cover these plus Berserker, Boxing and Sniper resources.
Generated descriptions explicitly label automation as partial, rather than
implying that all remaining effects are merely tactical.

## Not complete: remaining mechanical acceptance

Most talent-specific effects currently remain in sheet rules text. This is correct
for tactical actions but NOT sufficient for all persistent character-builder
effects. Equipment weapon/armor proficiencies beyond Shield Training/Finesse
Fighting, talent-specific bonuses, some free talent grants (including Conjuration
companion forms), all package-specific edge cases, all repeatability conditions,
and companion/gizmo stat construction still need explicit mechanical treatment
and targeted runtime tests. Skill grants currently cover eight base spheres and
Athletics/Beastmastery packages, not all associated skills. Traditions and real
class sphere-specialization adapters are not implemented by this catalog pass.
Do not label the user's full requested implementation complete.

Final verification correction: Equipment's free-choice category was narrowed from
the sphere-wide Equipment type to EquipmentTalent. This prevents the free slot
from listing the Equipment base sphere itself. The production-controller Equipment
save/reload gate passed with this correction (evidence directory
`/bigdisk/programming/pathfinder1e/build/pcgen-spheres-z9ma_q97`). An offline test
protects the category boundary; another verifies that every mechanical override
resolves to a real catalog record rather than being silently unused.