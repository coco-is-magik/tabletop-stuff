"""Reviewed Hedgewitch path skills, persistent benefits and general secrets."""
import re


def path_tags(text, title=""):
    """Compile explicit path skills and reviewed benefits, not embedded secrets."""
    match = re.search(r"Class Skills:\s*(.*?)\s*Path Benefit\b", text, re.S)
    if not match:
        raise ValueError("Hedgewitch path lacks a reviewed class-skill block")
    skills = []
    for entry in match[1].rstrip(". \n").split(","):
        name = re.sub(r"\s*\((?:Str|Dex|Con|Int|Wis|Cha)\)", "", entry).strip()
        if name.startswith("Knowledge ("):
            name = name.title()
        if not re.fullmatch(r"[A-Za-z ]+(?: \([A-Za-z ]+\))?", name):
            raise ValueError("Unreviewed Hedgewitch path skill: " + entry)
        skills.append(name)
    tags = ["PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1", "CSKILL:" + "|".join(skills)]
    if title == "Academia":
        tags.extend(["BONUS:VAR|SPHERES_SPELL_POINTS|floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:ABILITYPOOL|Hedgewitch Secret|1",
                     "BONUS:ABILITYPOOL|Hedgewitch Academia Mastery|1|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,20"])
    if title == "Combat":
        tags.append("BONUS:ABILITYPOOL|Hedgewitch Combat Mastery|1|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,20")
    if title == "Charlatanism":
        tags.extend(["BONUS:ABILITYPOOL|Versatile Performance|1",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_GUILE|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_GUILE_SKILL_BONUS|if(SPHERES_HEDGEWITCH_LEVEL>=20,6,if(SPHERES_HEDGEWITCH_LEVEL>=10,4,2))",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_GUILE_SNEAK_DICE|ceil(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_GUILE_SNEAK_DIE_SIZE|if(SPHERES_HEDGEWITCH_LEVEL>=20,8,6)"])
    if title.lower() == "font of inspiration":
        tags.extend(["ABILITY:Spheres Magic Talent|AUTOMATIC|Divination Sphere",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_INSPIRATION|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_STUDIED_BONUS|floor(SPHERES_HEDGEWITCH_LEVEL/2)|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,5",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_STUDIED_ROUNDS|max(1,SPHERES_CASTING_ABILITY)|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,5"])
    if title == "Exorcism":
        tags.extend([
            "BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_ROUNDS|SPHERES_CASTING_ABILITY+4+2*(SPHERES_HEDGEWITCH_LEVEL-1)",
            "BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_DC|10+floor(SPHERES_HEDGEWITCH_LEVEL/2)+SPHERES_CASTING_ABILITY",
            "BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_RADIUS|30+5*floor((SPHERES_HEDGEWITCH_LEVEL-1)/4)",
            "BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_LIMIT|1+floor((SPHERES_HEDGEWITCH_LEVEL-1)/4)",
            "BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_PUSH|SPHERES_HEDGEWITCH_LEVEL+SPHERES_CASTING_ABILITY"])
        for skill in ("Arcana", "Dungeoneering", "Engineering", "Geography", "History", "Local", "Nature", "Nobility", "Planes", "Religion"):
            tags.append(f"BONUS:SITUATION|Knowledge ({skill})=Identify Creatures|floor(SPHERES_HEDGEWITCH_LEVEL/2)|TYPE=Competence")
    if title == "Umbral":
        tags.append("BONUS:SKILL|Stealth,Disguise|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))")
        tags.extend(["BONUS:VAR|SPHERES_HEDGEWITCH_UMBRAL_LEVEL|SPHERES_HEDGEWITCH_LEVEL",
                     "ABILITY:Special Ability|AUTOMATIC|Fey Adept Shadow Points (Reference)|Fey Adept Shadowmark Dice (Reference)|Fey Adept Shadowmark Die Size (Reference)|Fey Adept Shadowmark Penalty (Reference)"])
    if title == "Astrology":
        tags.extend(["ABILITY:Spheres Magic Talent|AUTOMATIC|Light Sphere",
                     "BONUS:ABILITYPOOL|Hedgewitch Celestial Aura|2",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_AURA_ACTIVE_LIMIT|1",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_AURA_EFFECTIVE_LEVEL|SPHERES_HEDGEWITCH_LEVEL+if(SPHERES_HEDGEWITCH_LEVEL>=20,5,0)"])
    if title == "Green Magic":
        tags.extend(["ABILITY:Special Ability|AUTOMATIC|Wild Empathy|Druid ~ Woodland Stride",
                     "BONUS:VAR|WildEmpathyLVL|SPHERES_HEDGEWITCH_LEVEL"])
    if title == "Tinker [CotS]":
        tags.extend(["BONUS:SKILL|Disable Device|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))|TYPE=Trapfinding",
                     "BONUS:SITUATION|Perception=Trapfinding|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))|TYPE=Trapfinding"])
    if title == "Temporal Traveler":
        tags.extend(["ABILITY:Spheres Magic Talent|AUTOMATIC|Time Sphere",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_INSIGHT_CAPACITY|max(1,SPHERES_CASTING_ABILITY)"])
    if title == "Covenant":
        from spheres_covenant import path_tags
        tags.extend(path_tags())
    if title == "Transmuter":
        tags.extend(["BONUS:VAR|SPHERES_HEDGEWITCH_TRANSMUTATIONS|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_TRANSMUTATION_DC|10+floor(SPHERES_HEDGEWITCH_LEVEL/2)+SPHERES_CASTING_ABILITY",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_CREATE_ENABLED|1|PREABILITY:1,CATEGORY=Spheres Magic Talent,Creation Sphere"])
    if title == "Herbology":
        tags.extend(["ABILITY:FEAT|AUTOMATIC|Distill Compound",
                     "ABILITY:Special Ability|AUTOMATIC|Assassin ~ Poison Use",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_CONCOCTIONS|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_CONCOCTION_HOURS|1",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_CONCOCTION_DC|10+floor(SPHERES_HEDGEWITCH_LEVEL/2)+SPHERES_CASTING_ABILITY",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_CONCOCTION_HEALING_DICE|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))"])
    if title == "Black Magic":
        tags.extend(["BONUS:VAR|SPHERES_HEDGEWITCH_CURSES|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_CURSE_DC|10+floor(SPHERES_HEDGEWITCH_LEVEL/2)+SPHERES_CASTING_ABILITY"])
    if title == "Spiritualism":
        tags.extend(["BONUS:VAR|SPHERES_HEDGEWITCH_SPIRIT_USES|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                     "BONUS:VAR|SPHERES_HEDGEWITCH_SPIRIT_TALENT_LIMIT|if(SPHERES_HEDGEWITCH_LEVEL>=20,SPHERES_HEDGEWITCH_SPIRIT_USES,1+if(SPHERES_HEDGEWITCH_LEVEL>=5,1,0)+if(SPHERES_HEDGEWITCH_LEVEL>=13,1,0))"])
    return tags


def secret_tags(title, grand=False):
    name = re.split(r" \[", title)[0]
    tags = (["PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10"] if grand else
            ["PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1",
             "PREMULT:1,[PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,2],"
             "[PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia]"])
    if name in ("Champion", "Combat Talent", "Magical Skill"):
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE"])
        if name == "Combat Talent":
            tags.append("BONUS:VAR|SPHERES_COMBAT_TALENTS|1")
        else:
            tags.append(f"BONUS:ABILITYPOOL|Hedgewitch {name} Feat|1")
    if name == "Familiar":
        tags.extend(["DEFINE:FamiliarMasterLVL|0",
                     "ABILITY:Internal|AUTOMATIC|Standard Familiar List",
                     "BONUS:VAR|FamiliarMasterLVL|SPHERES_HEDGEWITCH_LEVEL|TYPE=Base.STACK",
                     "FOLLOWERS:Familiar|1"])
    if name == "Metamagic Master":
        tags.extend(["PREFEAT:1,TYPE=Metamagic", "MULT:YES", "STACK:NO",
                     "CHOOSE:FEAT|TYPE=Metamagic,PC"])
    if name == "Arcane Builder":
        tags.extend(["MULT:YES", "STACK:NO",
                     "CHOOSE:NUMCHOICES=9|STRING|Armor|Weapons|Potions|Scrolls|Wands|Rods|Staves|Rings|Wondrous Items",
                     "BONUS:SITUATION|Spellcraft=Craft %LIST|4"])
    return tags


def feat_categories():
    categories = [f"ABILITYCATEGORY:Hedgewitch {name} Feat\tCATEGORY:FEAT\tTYPE:{types}\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Feats"
            for name, types in (("Champion", "Champion"),
                                ("Magical Skill", "ItemCreation.Metamagic.HedgewitchMagicalSkill"),
                                ("Combat", "Combat"), ("Tactician", "Teamwork"),
                                ("Touch of Darkness", "Surreal"),
                                ("Metamagic Knowledge", "Metamagic"),
                                ("Grit", "Grit.Panache"))]
    categories.append("ABILITYCATEGORY:Hedgewitch Shadowstuff Feat\tCATEGORY:FEAT\tABILITYLIST:Extra Shadowstuff\t"
                      "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Feats")
    return categories


def path_secret_records():
    """Reviewed embedded secrets; do not infer mechanics from arbitrary prose."""
    records = ["Hedgewitch Academia Extra Spell Points\tCATEGORY:Hedgewitch Secret\t"
            "PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1\t"
            "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia\t"
            "MULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE\t"
            "BONUS:VAR|SPHERES_SPELL_POINTS|2|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia\t"
            "DESC:Increase your spell pool by 2 spell points. This secret can be taken multiple times; its effects stack."]
    for path, name, pool, grand, repeat in (
            ("Academia", "Metamagic Knowledge", "Metamagic Knowledge", True, False),
            ("Combat", "Combat Feat", "Combat", False, True),
            ("Combat", "Tactician", "Tactician", False, True),
            ("Umbral", "Touch of Darkness", "Touch of Darkness", False, True),
            ("Temporal Traveler", "Grit Feats", "Grit", False, True)):
        tags = secret_tags(name, grand)
        tags.append(f"PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}")
        if repeat:
            tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE"])
        tags.append(f"BONUS:ABILITYPOOL|Hedgewitch {pool} Feat|1")
        tags[-1] += f"|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}"
        if name == "Tactician":
            tags.extend(["DEFINE:SPHERES_HEDGEWITCH_TACTICIAN_USES|0",
                         "BONUS:VAR|SPHERES_HEDGEWITCH_TACTICIAN_USES|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Combat"])
        records.append(f"Hedgewitch {path} {name}\tCATEGORY:Hedgewitch Secret\t" + "\t".join(tags) +
                       "\tDESC:Select a qualifying bonus feat in the matching Hedgewitch feat category. " +
                       ("Sharing lasts 3 + half Hedgewitch level rounds; activation and daily expenditure are player tracked."
                        if name == "Tactician" else "Refund dependent feat selections before removing this secret. " +
                        ("On rest, refund and replace the selected metamagic feat." if grand else "")))
    records.append("Hedgewitch Umbral Shadow Sculptor\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Shadow Sculptor")) +
                   "\tPREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Umbral\t"
                   "ABILITY:FEAT|AUTOMATIC|Shadow Magic\tDESC:Gain Shadow Magic without needing its prerequisites.")
    umbral = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Umbral"
    records.append("Hedgewitch Umbral Shadowstuff\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Shadowstuff") + [umbral]) +
                   "\tMULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE\t"
                   "BONUS:ABILITYPOOL|Hedgewitch Shadowstuff Feat|1|" + umbral +
                   "\tDESC:Select Extra Shadowstuff in the dedicated bonus feat category for each selection of this secret. Umbral already grants the shadow pool and shadowmark; do not grant a second pool. Refund the bonus feat before refunding its secret.")
    records.append("Hedgewitch Umbral Hide in Plain Sight\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Hide in Plain Sight", True) + [umbral]) +
                   "\tDESC:May use Stealth while observed and without cover while within 10 feet of dim light, but cannot hide in your own shadow. Lighting, positioning and Stealth execution are table-resolved.")
    records.append("Hedgewitch Umbral Eyes of Black\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Eyes of Black") + [umbral]) +
                   "\tVISION:Darkvision (SPHERES_HEDGEWITCH_LEVEL*5)|" + umbral +
                   "\tBONUS:VISION|Darkvision|SPHERES_HEDGEWITCH_LEVEL*5|" + umbral +
                   "\tDESC:Darkvision 10 feet per Hedgewitch level, or extend another source by 5 feet per level if better. Spend a shadow point to penetrate magical darkness for one minute per Hedgewitch level; activation is player tracked.")
    records.append("Hedgewitch Umbral Improved Shadow Sculptor\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Improved Shadow Sculptor", True) + [umbral]) +
                   "\tMULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE\t"
                   "PREVARLT:SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS,2\t"
                   "BONUS:VAR|SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS|1|" + umbral +
                   "\tDESC:Add the listed effective caster-level bonus only to effects produced by Shadow Magic, not to all sphere effects. May be selected twice.")
    for path, name, grand, effects, description in (
            ("Academia", "Scholarship", False,
             ["BONUS:SKILL|TYPE=Knowledge|1+floor(SPHERES_HEDGEWITCH_LEVEL/5)|TYPE=Competence|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia"],
             "Gain +1 competence to Knowledge checks, +1 per 5 Hedgewitch levels. Knowledge checks may be attempted untrained; library research takes half the usual time (player tracked)."),
            ("Combat", "Greater Aid", False,
             ["DEFINE:SPHERES_HEDGEWITCH_AID_BONUS|0",
              "BONUS:VAR|SPHERES_HEDGEWITCH_AID_BONUS|3+floor(SPHERES_HEDGEWITCH_LEVEL/6)|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Combat"],
             "Aid another grants the ally the listed bonus instead of +2; do not apply this bonus to your own checks."),
            ("Combat", "Armor Training", True, ["UNENCUMBEREDMOVE:HeavyArmor"],
             "Medium and heavy armor do not reduce movement speed. Encumbrance from carried weight still applies."),
            ("Temporal Traveler", "Trapfinding", False,
             ["BONUS:SKILL|Disable Device|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))|TYPE=Trapfinding|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Temporal Traveler",
              "BONUS:SITUATION|Perception=Trapfinding|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))|TYPE=Trapfinding|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Temporal Traveler"],
             "Gain rogue trapfinding, including the ability to disarm magical traps."),
            ("Transmuter", "Transformations", False,
             ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|SPHERES_HEDGEWITCH_TRANSMUTATIONS|2"],
             "Gain two additional transmuter path power uses per day. Repeatable; effects stack. Uses and transformations are player tracked."),
            ("Transmuter", "Practiced Transmutation", False,
             ["BONUS:VAR|SPHERES_HEDGEWITCH_TRANSMUTATION_SIZE_STEPS|1|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Transmuter"],
             "Increase the allowable size of target and resulting objects/creatures by one step; this does not increase your own size."),
            ("Transmuter", "Ranged Transmutation", False,
             ["BONUS:VAR|SPHERES_HEDGEWITCH_TRANSMUTATION_RANGE|25+5*floor(SPHERES_HEDGEWITCH_LEVEL/2)|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Transmuter"],
             "Use the transmuter path power at close range rather than touch."),
            ("Transmuter", "Greater Transformation", True,
             ["BONUS:VAR|SPHERES_HEDGEWITCH_TRANSMUTATION_HD_BONUS|1+floor((SPHERES_HEDGEWITCH_LEVEL-10)/3)|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Transmuter|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,10"],
             "Increase the maximum Hit Dice permanently transformed from or into by the listed bonus. Apply this to the applicable base path limit, not to your own Hit Dice."),
            ("Transmuter", "Implanted Training", False, [],
             "An animal created or transformed by the path power may know Combat Training, Fighting, Guarding, Heavy Labor, Hunting, Performance or Riding for the transformation's duration. Choose training for each transformed animal."),
            ("Transmuter", "Expanded Transformation", True, [],
             "May also target or create aberrations, constructs, outsiders, magical beasts and vermin, using the humanoid size limits."),
            ("Transmuter", "New Life", True, [],
             "After failing the transformation save, a living target attempts a Will save or forgets its previous life for the transformation's duration. Memory returns when the effect ends."),
            ("Black Magic", "Curses", False,
             ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|SPHERES_HEDGEWITCH_CURSES|2"],
             "Bestow two additional curses per day. Uses and curse effects are player tracked."),
            ("Spiritualism", "Extra Spirit", False,
             ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|SPHERES_HEDGEWITCH_SPIRIT_USES|2"],
             "Channel two additional talents per day. Each temporary talent consumes one use; this does not add permanent talents."),
            ("Green Magic", "Venom Immunity", True,
             ["ABILITY:Special Ability|AUTOMATIC|Immunity to Poison|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Green Magic"],
             "Become immune to all poisons."),
            ("Green Magic", "Wild Vitality", True,
             ["ABILITY:Special Ability|AUTOMATIC|Immunity to Disease|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Green Magic"],
             "Become immune to all diseases."),
            ("Green Magic", "Bestial Bonds", False,
             ["ABILITY:Spheres Combat Talent|AUTOMATIC|Beastmastery Sphere|Beastmastery - Focusing Connection|PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Green Magic"],
             "Gain Beastmastery and Focusing Connection. When using Focusing Connection with the Green Magic animal companion, concentrate on a magic sphere effect as part of that action. Companion targeting and action execution are table-resolved."),
            ("Herbology", "Extra Concoctions", False,
             ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:VAR|SPHERES_HEDGEWITCH_CONCOCTIONS|2"],
             "Create two additional concoctions per day. Repeatable; effects stack. Prepared concoctions and expenditure are player tracked.")):
        tags = secret_tags(name, grand)
        tags.append(f"PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}")
        records.append(f"Hedgewitch {path} {name}\tCATEGORY:Hedgewitch Secret\t" +
                       "\t".join(tags + effects) + "\tDESC:" + description)
    for name, grand, dependency, description in (
            ("Potent Concoctions", False, None, "Concoctions remain potent for one hour per Hedgewitch level instead of one hour."),
            ("Store Potion", False, None, "Store one consumed potion, poison or concoction without applying it. Transfer it by touch as a standard action; concoction expiration still applies."),
            ("Surgeon", False, None, "Treat deadly wounds in 10 minutes, healing 2 hit points per target Hit Die."),
            ("Swift Poison", False, None, "Apply poison to a weapon as a move action."),
            ("Instant Poison", True, "Swift Poison", "Apply poison to a weapon as a swift action."),
            ("Miracle Man", True, "Surgeon", "Begin treating a dead target within 10 minutes; work for 4 hours and spend three concoction uses or prepared healing concoctions. Heal DC is 10 plus the magnitude of negative hit points. Success restores the target one hit point above death with two temporary negative levels for 24 hours. Missing vital parts prevent revival.")):
        gate = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Herbology"
        tags = secret_tags(name, grand) + [gate]
        if dependency:
            tags.append("PREABILITY:1,CATEGORY=Hedgewitch Secret,Hedgewitch Herbology " + dependency)
        if name == "Potent Concoctions":
            tags.append("BONUS:VAR|SPHERES_HEDGEWITCH_CONCOCTION_HOURS|SPHERES_HEDGEWITCH_LEVEL-1|" + gate)
        records.append(f"Hedgewitch Herbology {name}\tCATEGORY:Hedgewitch Secret\t" +
                       "\t".join(tags) + "\tDESC:" + description)
    return records


def charlatan_records():
    """Guile remains a conditional resource, never unconditional sneak attack."""
    gate = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Charlatanism"
    records = []
    exceptional = secret_tags("Exceptional Skill") + [gate, "MULT:YES", "STACK:NO", "CHOOSE:NUMCHOICES=1|SKILL|!TYPE=Perform,!TYPE=SkillUse",
                       "BONUS:SKILL|%LIST|floor(SPHERES_HEDGEWITCH_LEVEL/2)|" + gate,
                       "BONUS:VAR|HedgewitchExceptional %LIST|1|" + gate]
    for performance, skills in (("Act", ("Bluff", "Disguise")), ("Comedy", ("Bluff", "Intimidate")),
                               ("Dance", ("Acrobatics", "Fly")), ("Keyboard Instruments", ("Diplomacy", "Intimidate")),
                               ("Oratory", ("Diplomacy", "Sense Motive")), ("Percussion Instruments", ("Handle Animal", "Intimidate")),
                               ("Sing", ("Bluff", "Sense Motive")), ("String Instruments", ("Bluff", "Diplomacy")),
                               ("Wind Instruments", ("Diplomacy", "Handle Animal"))):
        for skill in skills:
            exceptional.append(f"BONUS:SKILL|{skill} (Perform ({performance}))|floor(SPHERES_HEDGEWITCH_LEVEL/2)|{gate}|PREVARGTEQ:HedgewitchExceptional {skill},1")
    records.append("Hedgewitch Charlatanism Exceptional Skill\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(exceptional) +
                   "\tDESC:Choose one skill other than Perform. Gain half Hedgewitch level to that skill, including when using versatile performance on its behalf.")
    for name, effects, repeat, description in (
            ("Extra Guile", ["BONUS:VAR|SPHERES_HEDGEWITCH_GUILE|2"], True,
             "Two additional guile points; effects stack."),
            ("Evasion", ["ABILITY:Special Ability|AUTOMATIC|Evasion"], False,
             "Gain evasion as the rogue class feature."),
            ("Trapfinding", ["BONUS:SKILL|Disable Device|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))|TYPE=Trapfinding",
                             "BONUS:SITUATION|Perception=Trapfinding|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))|TYPE=Trapfinding"], False,
             "Gain rogue trapfinding, including the ability to disable magical traps."),
            ("Versatile Performance", ["BONUS:ABILITYPOOL|Versatile Performance|1"], True,
             "Select another versatile performance using the existing bard performance choices.")):
        tags = secret_tags(name) + [gate]
        if repeat:
            tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE"])
        tags.extend(effect + "|" + gate for effect in effects)
        records.append(f"Hedgewitch Charlatanism {name}\tCATEGORY:Hedgewitch Secret\t" +
                       "\t".join(tags) + "\tDESC:" + description)
    return records


def inspiration_records():
    gate = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Font Of Inspiration"
    return ["Hedgewitch Font Of Inspiration Extra Inspiration\tCATEGORY:Hedgewitch Secret\t" +
            "\t".join(secret_tags("Extra Inspiration") + [gate, "MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                "BONUS:VAR|SPHERES_HEDGEWITCH_INSPIRATION|2|" + gate]) +
            "\tDESC:Two additional inspiration uses per day. This secret may be selected multiple times; its effects stack."]


def exorcism_records():
    """Sanction resources and secrets, not automatic effects on nearby creatures."""
    gate = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Exorcism"
    records = []
    protection = "PREABILITY:1,CATEGORY=Spheres Magic Talent,Protection Sphere"
    records.append("Hedgewitch Exorcism Warding Sanction\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Warding Sanction") + [gate, protection]) +
                   "\tBONUS:VAR|SPHERES_HEDGEWITCH_WARD_ENABLED|1|" + gate + "|" + protection +
                   "\tBONUS:VAR|SPHERES_PROTECTION_WARD_CLASS_BONUS|SPHERES_HEDGEWITCH_LEVEL-floor(SPHERES_HEDGEWITCH_LEVEL*3/4)|" + gate + "|" + protection +
                   "\tDESC:Use the listed caster level only for Protection wards, replacing Hedgewitch mid-caster progression with full class level and retaining other caster-level sources. A full-round action may create a ward and activate a sanction. Aegis and other Protection effects keep their normal caster level.")
    for name, grand, effects, description in (
            ("Enduring Exorcism", False, ["BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_ROUNDS|6"],
             "Six additional sanction rounds per day."),
            ("Greater Sanction", True, ["BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_RADIUS|20"],
             "Increase sanction radius by 20 feet."),
            ("Moral High-Ground", True, ["BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_DC|2"],
             "Increase sanction saving throw DC by 2."),
            ("Nemesis Sanction", False, ["BONUS:VAR|SPHERES_HEDGEWITCH_NEMESIS_RANGE|30+5*(SPHERES_HEDGEWITCH_LEVEL-1)"],
             "Focus a sanction on one target in the listed range, including your own creature type. The target remains sanctioned regardless of subsequent location and becomes entangled on a failed save. Each sanction still consumes its own round of the daily resource."),
            ("Rattling Sanction", False, ["BONUS:VAR|SPHERES_HEDGEWITCH_RATTLING_DICE|floor(SPHERES_HEDGEWITCH_LEVEL/2)",
                                         "BONUS:VAR|SPHERES_HEDGEWITCH_RATTLING_TARGETS|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))"],
             "Standard action: deal the listed d8 nonlethal damage to one sanctioned creature, ignoring nonlethal immunity. Spend one spell point to affect up to the listed number of sanctioned creatures instead."),
            ("Irresistible Force", True, ["BONUS:VAR|SPHERES_HEDGEWITCH_SANCTION_PUSH|10"],
             "Gain +10 when pushing a creature out of your sanctioned area using the sanction, bull rush or an ability working as bull rush; not a general CMB bonus."),
            ("Counterspelling Sanction", True, [],
             "Counterspell a sanctioned creature's spell, spell-like or sphere ability as an immediate action as though you had Counterspell Mastery. With Counterspell, this becomes a free action; this does not grant either feat globally."),
            ("Subtle Sanction", False, [], "Use and maintain sanctions without speech or a free hand."),
            ("Kinslayer", False, [], "May sanction your own creature type; gain +2 insight to sanction DC against that type and exempt any number of creatures from that sanction."),
            ("Threat of Force", False, [], "Allies adjacent to creatures affected by your sanctions are considered to flank them."),
            ("Bloodlust", True, [], "When activating a sanction, a held weapon may gain bane against its creature type while the sanction lasts; choose a subtype when required."),
            ("Remove Defenses", True, [], "A creature failing its sanction save loses damage reduction and resistance to spell damage until the beginning of its next turn.")):
        tags = secret_tags(name, grand) + [gate]
        tags.extend(effect + "|" + gate for effect in effects)
        records.append(f"Hedgewitch Exorcism {name}\tCATEGORY:Hedgewitch Secret\t" +
                       "\t".join(tags) + "\tDESC:" + description + " Activation, targets and expenditure remain table-resolved.")
    return records


def academia_mastery(path="Academia"):
    if path not in ("Academia", "Combat"):
        raise ValueError("Unsupported Hedgewitch ability-score mastery")
    category = (f"ABILITYCATEGORY:Hedgewitch {path} Mastery\tCATEGORY:Hedgewitch {path} Mastery\t"
                "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Spheres")
    records = []
    stats = (("Intelligence", "INT"), ("Wisdom", "WIS"), ("Charisma", "CHA")) if path == "Academia" else (("Strength", "STR"), ("Dexterity", "DEX"), ("Constitution", "CON"))
    for name, stat in stats:
        gate = f"PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch {path}"
        records.append(f"Hedgewitch {path} Mastery - {name}\tCATEGORY:Hedgewitch {path} Mastery\t"
                       f"PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,20\t{gate}\t"
                       f"BONUS:STAT|{stat}|2|PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,20|{gate}\t"
                       f"DESC:{path} path mastery grants +2 to {name}.")
    return category, records


def astrology_records():
    """Known auras and source quantities, not automatically active auras."""
    category = ("ABILITYCATEGORY:Hedgewitch Celestial Aura\tCATEGORY:Hedgewitch Celestial Aura\t"
                "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Spheres")
    path = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Astrology"
    records = []
    for name, description in (
            ("Moon", "Fortitude bonus 1 + floor(effective level/5); temporary HP 1 + floor(effective level/2), refreshed each turn while in the aura."),
            ("Planet", "Cold or fire resistance 5 + effective level, chosen when projecting the aura."),
            ("Star", "Perception and initiative bonus 1 + floor(effective level/5)."),
            ("Sun", "Weapon damage gains (1 + floor(effective level/5))d4 fire damage.")):
        records.append(f"Hedgewitch Celestial Aura - {name}\tCATEGORY:Hedgewitch Celestial Aura\t"
                       f"PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1\t{path}\t"
                       f"DESC:Known aura, not an always-active bonus. {description} Effective level increases by 5 at Hedgewitch level 20. Projection, ally range, consciousness and dismissal are player tracked.")
    for name, effects in (
            ("Extra Aura", ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "BONUS:ABILITYPOOL|Hedgewitch Celestial Aura|1"]),
            ("Heaven's Reach", ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                                "PREVARLT:SPHERES_HEDGEWITCH_AURA_REACH_COUNT,2",
                                "BONUS:VAR|SPHERES_HEDGEWITCH_AURA_REACH_COUNT|1",
                                "BONUS:VAR|SPHERES_HEDGEWITCH_AURA_RADIUS|10"])):
        records.append(f"Hedgewitch Astrology {name}\tCATEGORY:Hedgewitch Secret\t" +
                       "\t".join(secret_tags(name) + [path] + effects))
    records.append("Hedgewitch Astrology Syzygy\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Syzygy", True) + [path]) +
                   "\tBONUS:VAR|SPHERES_HEDGEWITCH_AURA_ACTIVE_LIMIT|1|" + path +
                   "\tDESC:You may project two different known celestial auras at once, rather than one. This selection does not activate an aura.")
    records.append("Hedgewitch Astrology Wax and Wane\tCATEGORY:Hedgewitch Secret\t" +
                   "\t".join(secret_tags("Wax and Wane") + [path]) +
                   "\tDESC:As a free action, adjust your celestial aura to increase light by up to two steps (maximum bright light) or shed no light. Resolve light conditions during play.")
    return category, records