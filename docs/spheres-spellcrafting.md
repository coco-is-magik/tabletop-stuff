# Ultimate Spellcrafting — initial increment, 2026-09-25

This is a **partial data-first implementation**, not a finished graphical builder
or full spellcasting engine. Source: the Ultimate tab of
https://spheresofpower.wikidot.com/spellcrafting (checked September 25, 2026).
Original Spellcrafting rules are not used.

## Definitions and generation

Repository root: `/nas/contents/Projects/Programming Projects/Java/tabletop-stuff`.
Edit `/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/data/spheres/custom-spells.json`
and run:

```sh
python3 '/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/tools/spheres_spellcrafting.py' --write
python3 '/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/tools/test_spellcrafting.py'
```

The JSON contains reviewed spell recipes. Each component names a loaded PCGen
sphere, talent or feat, the particular effect used, and its spell-point cost.
Multiple distinct effects from one component count separately. Exact duplicate
effects, unknown keys, unsupported schema fields and malformed inputs fail closed.
The base sphere and each talent's base sphere must be listed as components.

`changes` lists complexity alterations, using the keys in `CHANGES` in the
compiler. `duration_cost_adjustment` records the reviewed duration adjustment;
the compiler does **not** infer it from prose. `review` is required but is an
attestation, not proof that a GM approved the spell. Effect costs and alterations
must be checked against the constituent rules. Costs are never reduced below one
spell point in this increment. Arbitrary GM numeric overrides are not supported.

Generation calculates complexity, its spell-point surcharge and casting-time
increase count, total SP cost, learning hours, research check DC, spellbook pages,
writing hours and deciphering DC. Base-sphere CL/DC use existing character
variables. It does not permanently spend spell points or talents.

The included Restoring Shield recipe is a published Ultimate example, not a new
house rule: Protection base, Life plus Protection prerequisites, complexity two,
three SP, full-round action. Effect resolution remains at the table.

## Character workflow

The campaign loads Spellcrafting and Spellbook Mastery feat records. Spellcrafting
requires the existing Spheres Casting Core marker; Mastery additionally requires
Spellcrafting. This follows the existing project's casting-feature representation.

After GM review and completed downtime, select either `Learned - <name>` or
`Researched - <name>` under Completed Spell Learning or Research. Research requires
Spellcrafting; learning does not. Both require all recipe components. These are
zero-cost attestations, not automatic rolls or elapsed-time tracking. Spellbook
learning also requires deciphering at the table before recording acquisition.

Then select the spell in Spell Repertoire. Every selection requires the components
and an acquisition record, and spends one slot. Capacity is the nonnegative
casting ability modifier. It is not the magic-talent pool. Remove a spell to
refund its slot; **also remove its acquisition record when forgetting it**.
Relearning requires downtime again. PCGen does not automate this lifecycle or
delete dependent records after a prerequisite or modifier is removed.

## Spellbook casting

Each recipe also produces three zero-cost records, separate from the repertoire:

1. `Deciphered - <name>` records successful deciphering. Resolve the check or
   qualifying magical method before selecting it; no die roll is automated.
2. `Accessible Book - <name>` records current access to a deciphered written
   copy. Remove it when the copy is unavailable; deciphering knowledge persists.
3. `Book Casting - <name>` requires both records and Spellbook Mastery, but does
   not require learning or a repertoire slot. It computes missing distinct
   spheres/basic talents and the resulting 10-percent-per-component mishap
   chance, capped at 100 percent. Repeated effects from the same component do
   not multiply the missing-component count. Component feats are bypassed for
   book casting and do not add to that chance; Spellbook Mastery itself remains
   required. Ordinary learning and research still require component feats.

Book casting adds one round to the spell's ordinary casting time. Resolve casting,
spell-point expenditure and any GM-selected mishap at the table. Access records
are player attestations, not links to inventory items. Loss of access or Mastery
revokes qualification but does not delete an already-selected casting record.
The compiler explicitly rejects advanced and unclassified talent components,
including if such records are later added to the campaign.

## Remaining work and verification limits

- No GUI recipe editor; recipes are compiled offline before campaign loading.
- Duration compatibility, actual casting-time steps, research days, special
  alignment/CL/package prerequisites and tactical effects require review. Do not
  encode spells with unsupported extra prerequisites as if fully enforced.
- Advanced talents are now catalogued as `SpheresAdvancedTalent` records, but
  spellcrafting recipes still reject them: recipes use basic talents only.
- Temporary talents, physical book inventories, automatic access updates,
  actual casting and mishap resolution are not automated.
- Acquisition/forgetting and post-selection invalidation need stronger lifecycle
  integration. Existing shared casting-modifier limitations remain unchanged.

The real controller runner is
`/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/tools/pcgen_spellcrafting.py`.
Run it with no arguments for both gates on fast disks. On slow network
filesystems each PCGen process needs up to ~110 seconds, so run the gates in
separate invocations and reuse the workspace printed by the save run:

```sh
python3 tools/pcgen_spellcrafting.py save
python3 tools/pcgen_spellcrafting.py reload --work <workspace from the save run>
```

Verified September 25, 2026 on this machine: both live gates passed against the
real production ability controller. The checks cover rejection without
prerequisites, learning without the Spellcrafting feat, research and Spellbook
Mastery feat gating, repertoire slot spend/refund, duplicate rejection,
prerequisite removal revoking qualification, and save/reload persistence.
Evidence is in
`/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/build/pcgen-spheres-fr7hzm9l`.

September 27 continuation: nine offline tests cover the added book records,
deduplicated missing components, component-feat bypass and rejection of advanced
or unclassified talents. Live book-casting save/reload checks passed in
`/nas/contents/Projects/Programming Projects/Java/tabletop-stuff/build/pcgen-spheres-hc6b08ub`:
deciphering/access persistence, Mastery/access gates, 20/10/0-percent mishap
changes as spheres are restored, and repertoire-pool isolation.
