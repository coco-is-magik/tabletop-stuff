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
Only narrow unconditional tags in `data/spheres/trait-mechanics.json` are
applied; bonuses conditioned on a particular target, sphere, circumstance,
once-per-day use, or action are deliberately not generalized. Apply remaining
effects at the table. In particular no blanket caster-level, spell-point,
combat maneuver, DR, hit-point scaling, or conditional skill bonus is inferred
from the text. Source-specific variants with the same name are one selectable
trait; review the linked text if a campaign uses the other wording.