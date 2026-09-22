The scope should be: build a standalone PCGen data package that adds Ultimate Spheres of Power and Spheres of Might to Pathfinder 1e, while modifying PCGen Java only when the LST/data system cannot express a Spheres mechanic. PCGen explicitly supports custom datasets through `.pcc` and `.lst` files, including a homebrew dataset framework, so most of this should be a data project rather than a PCGen fork. ([GitHub][1])

The Spheres Wiki is the best source specification. It states that it hosts material released under OGL 1.0a, identifies Product Identity separately, and defaults to Ultimate Spheres of Power rather than the legacy version. That gives us a reasonably clean target: **Ultimate Spheres of Power + Spheres of Might, using the wiki's OGL material as the rules specification.** ([Spheres of Power Wiki][2])

### Phase 1: Define exactly what PCGen has to represent

Do not start by entering hundreds of talents. First implement the underlying Spheres character model.

For Spheres of Power, PCGen needs to understand at minimum:

```text
Spherecaster
    |
    +-- Casting Tradition
    |
    +-- Casting Ability Modifier
    |
    +-- Casting Skill Modifier
    |
    +-- Spell Pool
    |
    +-- Magic Skill Bonus
    |
    +-- Caster Level
    |      |
    |      +-- general CL
    |      +-- sphere-specific CL modifiers
    |
    +-- Magic Talents
           |
           +-- Base Spheres
           +-- Talents
           +-- Drawbacks
           +-- Advanced Talents
```

This distinction matters because Spheres multiclassing differs substantially from normal PF spellcasting. Magic talents, spell points, and caster levels from multiple spherecasting classes can stack, and sphere effects derive things such as saving throws from this system. ([Spheres of Power Wiki][3])

For Spheres of Might, the parallel model should be:

```text
Practitioner
    |
    +-- Martial Tradition
    |
    +-- Martial Talent progression
    |
    +-- Practitioner Modifier
    |
    +-- Base Attack Bonus
    |
    +-- Martial Spheres
           |
           +-- Base Spheres
           +-- Talents
           +-- Drawbacks
           +-- Legendary Talents
```

The Spheres Wiki provides the SoM rules and associated content as part of its OGL-hosted material. ([Spheres of Power Wiki][4])

### Phase 2: Create an empty PCGen Spheres source

Make Spheres its own PCGen data source rather than putting it directly into Pathfinder core data.

Something approximately like:

```text
data/
└── spheres/
    ├── spheres.pcc
    ├── spheres_abilities.lst
    ├── spheres_classes.lst
    ├── spheres_feats.lst
    ├── spheres_kits.lst
    ├── spheres_templates.lst
    └── ...
```

PCGen's existing homebrew framework is specifically intended for creating datasets like this. `.lst` files contain the actual game objects and the dataset is tied together through the PCGen data-source infrastructure. ([GitHub][1])

Initially, `spheres.pcc` should load successfully alongside Pathfinder and do absolutely nothing.

That is milestone 1.

### Phase 3: Prototype one tiny vertical slice

Do not implement every sphere.

Implement enough Spheres of Power to construct one trivial spherecaster.

For example:

```text
Incanter 1

Casting ability: INT

Magic talents:
    Destruction Sphere
    one Destruction talent

Derived:
    caster level
    spell points
    save DC
```

You want PCGen to correctly answer:

```text
How many talents do I have?

What spheres/talents can I select?

What is my caster level?

What is my casting ability modifier?

How many spell points do I have?

What is my sphere DC?
```

The important test is not whether PCGen can actually "cast" the ability. PCGen is primarily serving as the character-building and calculation engine.

For example, the Spheres rules derive saves and effects from caster level and casting ability, while individual sphere abilities can introduce their own calculations. ([Spheres of Power Wiki][3])

### Phase 4: Determine how to encode talents

I would strongly investigate representing spheres and talents as PCGen abilities.

Conceptually:

```text
ABILITYCATEGORY:Magic Talent

ABILITY:Destruction Sphere

ABILITY:Searing Blast

ABILITY:Energy Sphere

...
```

and separately:

```text
ABILITYCATEGORY:Martial Talent

ABILITY:Fencing Sphere

ABILITY:Footwork

ABILITY:Fatal Thrust

...
```

This gives PCGen a natural mechanism for selections, prerequisites, grants, and progression.

Then classes don't need to know what every sphere is. A class simply grants:

```text
BONUS:ABILITYPOOL|Magic Talent|1
```

or the appropriate PCGen equivalent.

That separation is essential because dozens of classes, archetypes, feats, traditions, and other abilities can grant talents.

### Phase 5: Implement the shared Spheres variables

Before adding lots of content, establish canonical internal variables.

Something conceptually like:

```text
SPHERES_MAGIC_TALENTS

SPHERES_MARTIAL_TALENTS

SPHERES_CASTER_LEVEL

SPHERES_MAGIC_SKILL_BONUS

SPHERES_SPELL_POINTS

SPHERES_CASTING_ABILITY

SPHERES_PRACTITIONER_MODIFIER
```

Then define sphere-specific values where necessary:

```text
SPHERES_CL_DESTRUCTION

SPHERES_CL_LIFE

SPHERES_CL_TELEKINESIS
```

The names themselves are arbitrary. The important part is having one standardized internal representation.

Everything else should manipulate those values rather than independently calculating them.

### Phase 6: Implement traditions

Once the fundamental variables work, implement Casting Traditions and Martial Traditions.

Treat them as structured packages.

For example:

```text
Casting Tradition
    |
    +-- casting ability
    +-- drawbacks
    +-- boons
    +-- bonus talents
    +-- other modifiers
```

and:

```text
Martial Tradition
    |
    +-- starting spheres
    +-- starting talents
    +-- proficiencies
    +-- other abilities
```

A tradition should therefore grant existing PCGen abilities rather than contain an independent implementation of those abilities.

That keeps your data normalized.

### Phase 7: Implement one complete sphere

Now implement exactly one sphere completely.

Destruction is a reasonable SoP test case because it exercises caster level, save DCs, talents, spell points and calculated effects.

Implement:

```text
Destruction Sphere

all basic Destruction talents

prerequisites

drawbacks

advanced talents

CL modifications

spell-point interactions
```

Then build several characters and compare their PCGen output manually against the Spheres rules.

Do not proceed until this works.

### Phase 8: Implement one complete martial sphere

Repeat the process with a representative SoM sphere.

You want one that exercises enough Pathfinder integration to expose architectural problems:

```text
attack rolls
BAB
combat maneuvers
weapon properties
talent prerequisites
action types
damage
```

At this point you'll learn whether PCGen's normal ability/bonus system can represent SoM cleanly.

### Phase 9: Build automated validation

This is particularly important given the simulator you've already built.

Create known characters:

```text
Incanter 1
Incanter 5
Incanter 10

Conscript 1
Conscript 5
Conscript 10

mixed PF/Spheres character

multiclass spherecaster
```

For each, assert things like:

```text
magic talents == X
martial talents == X
spell points == X
caster level == X
Destruction CL == X
sphere DC == X
attack bonus == X
```

Now every subsequent data import has regression coverage.

### Phase 10: Expand the sphere catalog

Only after the architecture passes those tests should we do the boring bulk work.

At that point:

```text
Alteration
Conjuration
Creation
Dark
Death
Destruction
Divination
Enhancement
...
```

becomes predominantly data entry.

The current Spheres Wiki provides the sphere hierarchy and distinguishes magic, combat and other sphere systems. ([Spheres of Power Wiki][2])

### Phase 11: Add Spheres classes

Then implement the actual classes.

The order matters.

If we implement classes first, each class will tempt us to invent its own special implementation.

Instead:

```text
Spheres engine
      ↓
talents
      ↓
spheres
      ↓
classes
```

means that something like Incanter can mostly say:

```text
HD = ...
BAB = ...
saves = ...

casting progression = high

talents = progression table

class features = ...
```

rather than containing the implementation of Spheres itself.

### Phase 12: Add archetypes and Champions interactions last

Do not initially include Champions of the Spheres.

Get:

```text
Ultimate Spheres of Power

+

Spheres of Might
```

working independently first.

Hybrid material dramatically increases the number of interactions you need to validate.

### The major technical question

Before doing significant data entry, we need to answer one question:

> **Can PCGen's existing LST language represent the Spheres resource/progression model without Java changes?**

I suspect most of it can. PCGen's data architecture already supports custom abilities, ability categories, prerequisites, variables, bonuses, classes and optional Pathfinder rule subsystems. Its Pathfinder game mode itself exposes optional rules through data configuration. ([GitHub][1])

But we should prove it with the tiny Incanter/Destruction prototype rather than assume it.

If something cannot be expressed, the preferred order should be:

```text
1. Existing PCGen LST functionality
            ↓
2. Clever composition of existing PCGen objects
            ↓
3. Small generic PCGen extension
            ↓
4. Spheres-specific Java code
```

Number 4 should be the last resort.

The immediate next task is therefore very concrete: **create a minimal PCGen source containing only the Spheres core variables, a Magic Talent ability category, Incanter levels 1-2, the Destruction sphere, and two or three Destruction talents.**

If that successfully handles talent selection, caster level, spell points and DC calculation, we've validated the architecture before committing to encoding hundreds of Spheres options.

[1]: https://github.com/PCGen/pcgen/blob/master/data/35e/homebrew/my_homebrew/how_to_use_this.txt?utm_source=chatgpt.com "pcgen/data/35e/homebrew/my_homebrew/how_to_use_this.txt at master · PCGen/pcgen · GitHub"
[2]: https://spheresofpower.wikidot.com/?utm_source=chatgpt.com "Spheres of Power Wiki Home Page - Spheres of Power Wiki"
[3]: https://spheresofpower.wikidot.com/using-spheres-of-power?utm_source=chatgpt.com "Using Spheres Of Power - Spheres of Power Wiki"
[4]: https://spheresofpower.wikidot.com/spheres-of-might?utm_source=chatgpt.com "Spheres Of Might - Spheres of Power Wiki"
