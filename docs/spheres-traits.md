# PF1 Spheres traits

The Spheres dataset adds 161 distinct trait choices from pinned `traits` and
`practitioner-traits` pages. Source snapshots and generated records live at
`testdata/spheres/catalog-source/` and `data/spheres/trait-catalog.json`.
Regenerate without network access using `python3 tools/spheres_traits.py --write`;
run `python3 -m unittest discover -s tools -p test_traits.py` and
`python3 tools/pcgen_traits.py` to check catalog integrity and PCGen selection.
The source's unanchored Original appendix supplies additional unique traits;
duplicate names prefer the anchored current entry. Eight legacy traits use
their *trait names*, not the retired-hero scenario headings. Practitioner
equipment-package descriptions are not additional traits.

Load alongside the PF1 **Core Rulebook**. Load **Advanced Player's Guide** to
receive its normal two-trait starting pool; this dataset does not manufacture
trait points. Records use PCGen's shared Traits pool and basic-trait types,
including category restrictions. Five Spheres drawback traits spend one shared
slot and grant two shared slots (net one extra ordinary trait); only one Spheres
drawback trait is permitted. This does **not** automatically limit drawbacks
from other datasets or substitute for the GM's drawback approval.

Campaign, legacy, and tradition traits require explicit manual approval in
the **Spheres Trait Adjudication** category, as do eight source prerequisites
the loader cannot prove automatically. An approval marker does not grant the
trait. Setting, faith, ancestry, traditions, timing, alternate prerequisite
routes, and situational target choices require GM review; PCGen's ability
controller does not enforce removal if a prerequisite is lost later.

Most effects are recorded as source rules text, **not** automated bonuses.
Nineteen traits have reviewed mechanics in `data/spheres/trait-mechanics.json`;
this is not a count of fully implemented traits. Specific current additions:

- Daysense grants +1 to Geography and Survival and a choice of one as a class
  skill. Its time awareness remains table-resolved.
- Corpse Watcher, Colloquial Terms, Weird Virtuoso, Impersonator and Guardian Of
  The Real expose their circumstance-specific bonuses through PCGen situations,
  not unconditional skill bonuses. Existing class-skill grants are retained.
- Scarred by War grants native DR 1/piercing and Intimidate as a class skill.
- Steel Body grants +1 HP plus +1 per two additional Hit Dice through PCGen's
  normal HP field. Levels 1 and 2 grant +1; levels 3 and 4 grant +2.
- Abrasive applies -5 to its three specified Diplomacy situations. Its
  motivation requirement and effects on allies remain table-resolved.
- Bountiful Charm grants +2 to Diplomacy when recruiting cohorts. Its optional
  adaptation to a replacement recruitment skill remains manual.
- Learned Readiness, Industrial Worker and Higher Calling grant their class
  skills only. Prepared spell-point assignment, project-material gathering and
  weekly augury respectively remain unautomated.
- Skeptical's Sense Motive bonus is automated; its conditional Will save is not.
- Technophile increases the Tech charge capacity only while Tech is present;
  it does not create an independent charge pool.

Aura and Technophile are retained in the default live fixture and verified on
reload. The `--profile daysense` fixture retains Aura and Daysense, including its
selected Survival class skill. Run `save --profile daysense`, then
`reload --profile daysense --work <printed-evidence-directory>`. Other tested
traits are selected and removed during each gate, not persisted selections,
except `--profile steel`, which retains Steel Body and Aura. Use `--level` on
save to exercise HP scaling at a specific level; reload reads the saved level.
Evidence directories and the remaining acceptance ledger are recorded in
`spheres-current-status.md`.

Compassion's Charisma-for-Heal option remains open because it must not stack
with Scholar's Intelligence-for-Heal substitution. Caster-level caps, optional
ability substitutions, resource lifecycles and conditional effects must not be
inferred from descriptions. Source-specific variants with the same name are one
selectable trait; review the linked text if a campaign uses the other wording.