# Power / Might base classes (September 24, 2026)

Load `/bigdisk/programming/pathfinder1e/data/spheres/spheres.pcc` with the Pathfinder Core Rulebook. This campaign provides class records at levels 1–20 for **Armorist, Eliciter, Fey Adept, Hedgewitch, Mageknight, Shifter, Soul Weaver, Symbiat, Thaumaturge, Wraith, Armiger, Blacksmith, Commander, Scholar, Sentinel, Striker and Technician**. The earlier Incanter, Conscript and partial Elementalist remain available. Prestige classes and archetypes are not added.

The wiki also lists **Savant (Class Version)** among its practitioners, but describes it as technically a Thaumaturge archetype. It is deliberately excluded under the requested no-archetypes boundary (https://spheresofpower.wikidot.com/savant-class).

The 17 new classes are **not fully automated**. Their Hit Dice, class skills, proficiencies (with some equipment-specific exceptions), BAB, saves, talents, caster levels, spell pools and level-table feature records come from snapshots of their individual class pages under `/bigdisk/programming/pathfinder1e/testdata/spheres/catalog-source/`. Magic classes share the two initial magic talents. Class-granted spheres are present for Eliciter (Mind), Fey Adept (Illusion), Shifter (Alteration), Symbiat (Mind and Telekinesis), Soul Weaver (Life or Death), Wraith (path-dependent, including separate Nature and Weather choices for Anima), Commander (Warleader), Scholar (Alchemy and Scout), Sentinel (Guardian), Striker (one of Boxing/Brute/Open Hand) and Technician (Trap). The Mageknight's additional level-one magic talent is counted separately.

Selection pools record source-level option counts. Named option records include source descriptions for the repeating class selections (such as arsenal tricks, emotions, secrets, mystic combats, bestial traits, nexus powers, invocations, haunts, prowesses, smithing insights, specializations, scholar's knacks, impositions, striker arts and technical insights). Hedgewitch paths, Wraith haunt paths, and Soul Weaver channel alignment are selectable. Armiger customized weapons, Technician inventions and Blacksmith equipment specialist selections have bounded manual-record slots; an Armiger's *per-weapon* talents do **not** increase their general combat-talent pool. Several class-dependent quantities are available as reference variables rather than indiscriminate bonuses.

**Manual adjudication remains necessary:** named option prerequisites, effects, targets, limited-use resources, conditional attack/defense modifiers, summons, possessions, inventions and improvement statistics, bound equipment and its enhancement allocation, maintenance, choice-dependent class skills and feats, damage, actions and initiative, tradition grants, duplicate-sphere substitution, favored-class variants and multiclass stacking. A descriptive feature is **not** a working PCGen automation of that feature. Wraith's Anima path offers Nature *or* Weather as separate choices; its other path effects remain manual. Blacksmith's free Equipment talent is a separate manual record; it does not consume a class talent. Thaumaturge's bonus feat category is a broad filter, not full casting-prerequisite validation, and choosing an extra magic talent there needs manual accounting. The reference variables do not automatically change conditional attacks, AC, equipment, or spell effects. Check all unsupported choices against the individual source pages before play.

To reproduce the source-table files, verify generated output, and exercise real PCGen loading and save/reload (Java 16 and the local PCGen build are required for the last step):

```sh
python3 /bigdisk/programming/pathfinder1e/tools/spheres_class_catalog.py --check
python3 /bigdisk/programming/pathfinder1e/tools/test_class_catalog.py
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_class_catalog.py armorist --level 20
python3 /bigdisk/programming/pathfinder1e/tools/pcgen_class_catalog.py wraith --level 1
```

The live gate accepts any of the 17 class slugs and levels 1–20. It checks table arithmetic, granted spheres for supported examples, class choice pools, some reference variables, and the persistence of representative path/channel/ability selections across save/reload. It does not exercise each named option's combat effect. The generator intentionally fails on missing or malformed pinned class tables rather than extrapolating data.

## Mageknight selection corrections (September 27, 2026)

Mystic Combat heading prerequisites are now enforced, including class-feature
levels, required spheres and required Mystic Combat options. Black Dog Companion
also needs a GM curse-talent attestation; curse descriptor detection and companion
construction remain manual. Magic Power and Combat Talent are repeatable and
grant actual talent slots. Whirl of Blows, Sunder The Veil and Weirding Initiate
automatically grant their named feats. These corrections are exceptions to the
general manual-feature limitations above, not full Mageknight combat automation.

The dedicated runner is
`/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/tools/pcgen_mageknight.py`:
run `save --level 12`, then `reload --work <absolute evidence directory>`.
Levels 2, 6 and 12 have passed save/reload tests. See the depth audit for tested
behaviors and remaining limitations; saved option keys have not been renamed.

Champion and Greater Combatant now grant separate bonus-feat choice pools and
support repeated selection. Normal feat prerequisites remain enforced. Live
checks at levels 6 and 16 cover pool refunds and invalid feat rejection; level
16 also covers a selected combat feat's save/reload persistence.

## Armorist corrections (September 27, 2026)

Arsenal Trick heading prerequisites now enforce base-class feature levels and
required tricks, including the alternative materials requirements of Bound
Companion. Unknown heading prerequisite grammar fails generation. These checks
assume the base class, not archetypes that replace its class features.

Combat Talent grants repeatable combat-talent slots. Champion, Combat Feat and
Crafter grant distinct repeatable feat-choice pools with ordinary prerequisites.
Additional Binding increases the bound-item capacity. Greater Armor Training is
repeatable and adds to the base armor-training progression. Equipped armor now
receives the maximum-Dexterity and armor-check adjustments; medium/heavy armor
movement abilities are granted at levels 3/7. Equipment construction, companions,
Advanced Armor Training feat selection and conditional arsenal effects remain
manual. Capacity increases do not themselves construct bound equipment.

Runner: `/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/tools/pcgen_armorist.py`.
Save/reload checks passed at levels 2 and 12. The armor checks assert equipped
bonus values and unequip removal, not every sheet format or movement output.

Removing a parent option refunds its pool, but does not automatically delete a
chosen feat: remove dependent feat choices when removing their granting option.

## Armiger corrections (September 27, 2026)

Prowess heading requirements now enforce Armiger levels, base-class Rapid
Assault/Enhanced Customization availability, and both Leadership and its Cohort
package for Share Customized Weapon. Extra Focus grants Great Focus. Champion
grants a repeatable Champion-feat pool. Deadly Prowess chooses up to three distinct
feats, bypassing their normal prerequisites as specified, at one prowess slot
per selection. Partial removal preserves the other grants; full removal removes
the feats and refunds the slots. Its grants live on the class with per-choice
conditions to avoid upstream repeated-option removal bugs.

Runner: `/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/tools/pcgen_armiger.py`.
Other explicit Prowess grants (including Spell Dabbler and sphere-choice grants),
customized weapon configuration and conditional combat effects remain partial.