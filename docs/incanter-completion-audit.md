# Historical extended-option inventory — not the class completion contract

## Scope superseded on 2026-09-23

The user explicitly replaced the broad inventory below with **thin Incanter class
completion**: levels 1–20, casting ability/resources, talent and feat progression,
specialization purchase/activation accounting, class grants, removal and save/reload.
The current acceptance contract is in `/bigdisk/programming/pathfinder1e/docs/incanter-class.md`.

Everything below is historical reference, **not an implementation backlog or a
completion prerequisite**. Do not resume sphere catalogs, domain/bloodline catalogs,
favored-race catalogs, companions, archetypes, traditions or third-party variants
without a separate request. Existing optional data stays in place for compatibility.

Source: https://spheresofpower.wikidot.com/incanter, Ultimate tab, inspected
2026-09-22. The page also contains **Original** rules; do not combine the two
versions. Existing coverage is documented in [spheres.md](spheres.md). This
inventory is not a claim that the class or the linked sphere catalogs are done.

## Superseded extended-source contract

- Scope: normal, single-class Pathfinder 1e Incanter using Ultimate Spheres of
  Power. No Guile, mythic, gestalt, or multiclass support in this milestone.
- A listed option is complete only if PCGen can select it legally, calculate its
  mechanical effects (including required sphere effects), remove it cleanly,
  and preserve it through save/reload. Text-only abilities do not qualify.
- A source option without a working underlying sphere, archetype replacement,
  companion, or requisite sourcebook data remains **blocked**, not implemented.
- All normal-game Ultimate wiki options, including tagged third-party and
  homebrew variants (`[3PP]`, `[LG]`, `[EO3]`, `[DRS]`, `[TS]`, etc.), are in
  scope per the user's 2026-09-22 decision. Verify the source/license and
  mechanics of each before including any external text or dependencies.
- The current talent formula and fixtures match Ultimate: one talent each
  level, an additional talent at every odd level (including 1st), and two
  initial talents from casting. Do not remove the level-1 bonus talent.
- The source page is a moving target. Recheck it and linked rules pages before
  certifying the final inventory; record the source revision/date and skipped
  options. Do not substitute the Original section for missing Ultimate rules.

## Base chassis and specializations

| Options | Current state | Required acceptance work |
| --- | --- | --- |
| Levels 1–20, high caster progression, bonus talents, spell pool, INT/WIS/CHA | Prototype with fixtures | Verify against Ultimate rules and tradition interactions; preserve existing fixtures. |
| Bonus feats and forfeiture, specialization purchase and activation | Partial | Audit all eligible feats, level-1 choices, order, refund and saved character behavior. |
| Admixture Adept | Partial | Verify bonus talent and full pool/use interaction. Ultimate grants Admixture directly; the already-owned alternative occurs only in Original. |
| Channel Energy, Lay on Hands, Merciful Healer, Master of Mysteries | Partial | Check linked sphere dependencies, complete gates and specialized save/reload. |
| Familiar | Standard familiar only | Add Fey Servant and Omnimental as mutually exclusive 2-point alternatives; implement companion-side effects, scaling and save/reload. |
| Cleric domains/subdomains | 33 Core adapters | Inventory all normal-game sources and subchoices; powers only; verify each adapter. |
| Sorcerer bloodlines | 10 Core adapters | Inventory non-Core options and subchoices; powers only; verify each adapter. |
| Sword Birth | Arena/trick prototype; ordinary Combat Feat trick and specialized save/reload gate pass locally | Add remaining legal Ultimate ordinary arsenal tricks, arena weapon/property choices and budgets; do not enhance unrelated equipment or import Original-only tricks. |

The Ultimate page specifies Fey Servant's animal-to-fey change, DR/cold iron
from level 4, fey-only Improved Familiar at level 8, and a level-10
fey-blessing share (3 + casting modifier uses/day within 30 ft while fey-link
is active). Omnimental requires an actual omnimental companion (without
speak-with-animals-of-its-kind) and blast range and line of sight originating
from its position from level 6. Merely granting the ordinary familiar or
putting these effects in a description is insufficient.

## Sphere specialization inventory

Only **Destruction** has a partial specialization implementation. The following
names are taken from the Ultimate page contents; their actual abilities,
prerequisites, replacement rules and sphere prerequisites still need individual
rules audits and PCGen gates. Listing a name does not imply an implemented base
sphere or a functioning specialization.

| Group | Options | State |
| --- | --- | --- |
| Main sphere specializations | Alteration, Bear, Blood, Conjuration, Creation, Dark, Death, Divination, Enhancement, Fallen Fey, Fate, Illusion, Life, Light, Mana, Mind, Nature, Protection, Technomancy [LG], Telekinesis, Time, War, Warp, Weather | Missing |
| Existing partial specialization | Destruction | Partial: grants, level gates and removal tested; underlying Destruction catalog incomplete. |
| Guide of the Dead explanatory section | Lingering Spirits and Housed Souls | Audit as part of Guide of the Dead, not a separately purchasable specialization. |
| Alteration variant | Bioreaver [EO3] | Missing |
| Death variant | Guide of the Dead [Gravecaller's HB] | Missing |
| Divination variants | Precognition [3PP], Recollection [3PP], Tactician | Missing |
| Nature variants | Aeromancer [EO3], Ferromancer [EO3], Hydromancer [EO3], Phytomancer [EO3], Pyromancer [EO3], Terramancer [EO3] | Missing |
| Protection variant | Lattice Weaver | Missing |
| Technomancy variant | Energy [LG] | Missing |
| Time variant | Acceleration [3PP] | Missing |

For every included entry: check purchase cost, activation cost/order, free
base sphere or alternative talent if already owned, sphere-only CL, powers at
all level thresholds, replacement/exclusivity, resources, removal and reload.
An inert base-sphere marker is not enough to certify an Incanter build.

## Shared dependencies and other choices

| Area | Current state | Completion gate |
| --- | --- | --- |
| Casting traditions, drawbacks, boons | Missing | Single authoritative casting ability, legal tradition choices, effects on talents/spell points, incompatible-choice rejection and reload. |
| Spheres feats | Extra Magic Talent and Extra Spell Points; Extra Arsenal Trick controller gates pass locally | Inventory eligible casting, drawback, proxy and theurge feats; prerequisites, repeated selections, persistent grants and bonus-feat pool isolation. |
| Favored class bonuses | Human and Half-Elf 1/6 talent, Elf 1/6 metamagic feat, Aasimar 1/2 Spellcraft, Tiefling 1/2 concentration-variable, Gnome's Destruction-specific 1/6 DC, Half-orc's Aberrant bloodline strength, Halfling's Channel Energy and Movement Burst uses, and Orc's Destruction Movement Burst uses have controller gates; Human, Aasimar, Tiefling, Gnome, Half-orc, both Halfling choices and Orc Movement Burst also have save/reload gates. Dwarf 1/6 item-creation feat pool has a gate but actual Core feat eligibility is not verified. | Ultimate also lists Alraun (Mind talent), Cecaelia (water talent), Cherufe (fire talent), Created (Creation Craft checks), Goblin (sphere CL and wild-magic risk), Leshy (plant talent), Merfolk (lingering effects), Sidhier (Fallen Fey DC), and Skinwalker (Alteration DC). Complete Gnome's per-sphere choices, Half-orc's other bloodlines, Halfling's other eligible abilities and Orc's remaining domain/specialization abilities. Tiefling's check variable still needs integration with an actual concentration-check execution path. Audit race data and implement effects, fractional accumulation, per-sphere/per-ability choices, and save/reload. |
| Archetypes | Missing | Audit Ultimate-page archetypes, their source tags, replaced features and mutual conflicts; do not reuse Original-only archetypes. |
| Incanter-specific feat | Missing | Audit Hybridized Specialty and its prerequisites and effects. |
| Listed class equipment | Missing | Inventory tagged items separately for the full source package; equipment is not an Incanter class-feature completion prerequisite. |
| Full sphere effects | Destruction slice only | Provide real prerequisite spheres/talents needed by each supported specialization, not just a name and a description. Full Power catalog is a separate later milestone, but legal Incanter options cannot be certified without their needed sphere effects. |
| Specialized save/reload | Unspecialized fixtures, Sword Birth (Combat Feat), domain, Core bloodline, channel/mercy, Human favored talent, Aasimar Spellcraft, Tiefling concentration-variable, Gnome Destruction DC, Half-orc Aberrant strength, Halfling Channel Energy/Movement Burst and Orc Movement Burst round trips | Both special familiars, remaining Sword Birth choices, specializations/sub-specializations, tradition, other feats, other favored class and archetype builds. |

## Execution and evidence order

1. Verify tagged-source rules and audit the exact Ultimate option lists and
   linked rules (including companion and arsenal trick/property rules).
2. For each bounded feature group, add a failing deterministic contract/gate,
   implement data, run the narrow gate, then test removal and save/reload.
3. Add casting traditions and the minimum **functional** underlying sphere
   mechanics required by the specializations. Track catalog completion separately.
4. Implement remaining options and archetype replacements only after their
   dependencies work; rerun Core Fighter isolation and old Incanter fixtures.
5. Reconcile the audit with the current source, record each explicit exclusion,
   run the full targeted suite, then and only then update the completion claim.

The PCGen controller and reload checks described in
[spheres.md](spheres.md) are required acceptance evidence. Python package
checks and first-party unit tests alone cannot certify LST parsing, companion
behavior or character mechanics.

### Favored-class inventory against the Ultimate page

The currently selectable and controller-tested entries are Aasimar, Dwarf
(pool only, not a selectable item-creation feat), Elf, Gnome (Destruction DC
only), Half-elf, Half-orc (Aberrant bloodline only), Halfling (Channel Energy
and Destruction Movement Burst only), Human, Orc (Destruction Movement Burst
only), and Tiefling (calculated variable only; concentration-check integration
unverified).
The other published Ultimate entries remain missing: Alraun (Mind talent),
Cecaelia (water talent), Cherufe (fire talent), Created (Creation-sphere
Craft bonus), Gnome (remaining chosen-sphere DCs), Goblin (chosen-sphere CL and
wild-magic chance), Half-orc (other bloodline powers/DC validation), Halfling
(other chosen 3 + CAM/day ability uses), Leshy (plant talent), Merfolk (chosen-sphere
duration), Orc (other domain or specialization ability uses), Sidhier (Fallen Fey
DC), and Skinwalker (Alteration DC). These are **not**
covered by the existing favored-class gates. Multiple entries depend on
missing sphere mechanics; do not mark them complete merely by tracking a
fractional variable.