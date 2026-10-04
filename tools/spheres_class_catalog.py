"""Generate PF1 Spheres base-class progressions from pinned class tables.

Only class-table numbers and grants are automated. Descriptions explicitly retain
the source's context-dependent features without pretending to run combat actions.
"""
import argparse
import json
import re

from spheres_catalog_source import ROOT, SNAPSHOTS
from spheres_mageknight import (option_tags as mageknight_tags, review_records as mageknight_review,
                               feat_categories as mageknight_feat_categories)
from spheres_armorist import option_tags as armorist_tags, feat_categories as armorist_feat_categories
from spheres_armiger import option_tags as armiger_tags, feat_category as armiger_feat_category
from spheres_blacksmith import option_tags as blacksmith_tags, feat_category as blacksmith_feat_category
from spheres_scholar import option_tags as scholar_tags, medical_records, medical_resources
from spheres_technician import option_tags as technician_tags, class_tags as technician_class_tags
from spheres_eliciter import emotion_records
from spheres_commander import option_tags as commander_tags
from spheres_striker import (option_tags as striker_tags, resource_tags as striker_resources,
                             training_records as striker_training)

NAMES = "armorist eliciter fey-adept hedgewitch mageknight shifter soul-weaver symbiat thaumaturge wraith armiger blacksmith commander scholar sentinel striker technician".split()
DATA = ROOT / "data/spheres"


def class_name(slug):
    return {"fey-adept": "Fey Adept", "soul-weaver": "Soul Weaver"}.get(slug, slug.title())


def table(snapshot):
    matches = [section["text"] for section in snapshot["sections"]
               if section["text"].startswith("Table:") and
               ("| Level |" in section["text"].splitlines()[0] or
                "| Class Level |" in section["text"].splitlines()[0])]
    if not matches:
        raise ValueError(f"Missing class table: {snapshot['url']}")
    lines = matches[0].splitlines()
    headers = [part.strip() for part in lines[0].split("|")[1:]]
    rows = [[part.strip() for part in line.strip().strip("|").split("|")] for line in lines[1:]
            if re.match(r"\|\s*\d+(?:st|nd|rd|th)?\s*\|", line)]
    if len(rows) != 20 or any(len(row) != len(headers) for row in rows):
        raise ValueError(f"Expected 20 complete class rows: {snapshot['url']}")
    for i, row in enumerate(rows, 1):
        if int(re.match(r"\d+", row[0]).group()) != i:
            raise ValueError(f"Wrong class level {i}: {snapshot['url']}")
    return headers, rows


def number(cell):
    match = re.match(r"\+?(\d+)", cell)
    if not match:
        raise ValueError(f"Not a numerical progression: {cell!r}")
    return int(match.group(1))


def source_options(snapshot, heading):
    """Return only the first base-class option section, before archetypes."""
    sections = snapshot["sections"]
    end = next((i for i, section in enumerate(sections) if section["heading"] in ("Favored Class Bonuses", "Archetypes")), len(sections))
    start = next((i for i, section in enumerate(sections[:end]) if section["heading"] == heading), None)
    if start is None:
        return []
    end = next((i for i in range(start + 1, end) if sections[i]["level"] <= sections[start]["level"]), end)
    return [(entry["heading"], entry["text"]) for entry in sections[start + 1:end]
            if entry["level"] > sections[start]["level"]]


def option_abilities(slug, category, section, snapshot):
    """Publish source-named choices with their rules text but no speculative automation."""
    options = source_options(snapshot, section)
    if not options:
        raise ValueError(f"No {section} options in {slug} source")
    if category == "Eliciter Emotion":
        return emotion_records(options)
    names = set()
    lines = []
    for title, text in options:
        key = re.sub(r"\s*\[[^]]+\]", "", title).strip()
        key = key.replace(",", " -").replace(";", " or").replace(":", " -")
        if key in names:
            continue
        names.add(key)
        body = re.sub(r"\s+", " ", text).replace("|", "/").replace("\t", " ").replace("%", "percent")
        # The wiki includes examples with unmatched punctuation; PCGen's DESC
        # parser requires balanced parentheses even for descriptive prose.
        body = body.replace("(", "[").replace(")", "]")
        if not body:
            body = f"Consult the {slug} class source for this choice."
        slug_key = "SPHERES_" + slug.upper().replace(" ", "_") + "_LEVEL"
        tags = mageknight_tags(title) if category == "Mageknight Mystic Combat" else [f"PREVARGTEQ:{slug_key},1"]
        if category == "Armorist Arsenal Trick":
            tags = armorist_tags(title)
        if category == "Armiger Prowess":
            tags = armiger_tags(title)
        if category == "Blacksmith Smithing Insight":
            tags = blacksmith_tags(title)
        if category == "Scholar Scholar'S Knack":
            tags = scholar_tags(title)
        if category == "Technician Technical Insight":
            tags = technician_tags(title)
        if category == "Striker Striker Art":
            tags = striker_tags(title)
        if slug == "Commander":
            tags = commander_tags(category, title)
        if category == "Wraith Wraith Haunt":
            tags = ["PREVARGTEQ:SPHERES_WRAITH_LEVEL,3"]
            requirement = re.search(r"\(requires wraith ([1-9]\d*)\)$", title)
            if requirement:
                tags = [f"PREVARGTEQ:SPHERES_WRAITH_LEVEL,{max(3, int(requirement[1]))}"]
            if title.startswith("Possess Armaments ("):
                # The historical key flattened the source's semicolon into OR.
                # Preserve that key for saved characters, not its incorrect logic.
                tags.extend([
                    "PREABILITY:1,CATEGORY=Spheres Magic Talent,Enhancement Sphere",
                    "PREMULT:1,[PREABILITY:1,CATEGORY=Wraith Wraith Haunt,Wraith Object Ride],"
                    "[PREABILITY:1,CATEGORY=Wraith Haunt Path,Wraith Path of the Poltergeist]",
                ])
            if title.startswith("Reactive Possession ("):
                tags.append(
                    "PREMULT:1,[PREABILITY:1,CATEGORY=Wraith Wraith Haunt,"
                    "Wraith Possess Armaments (requires Enhancement sphere or object ride or path of the poltergeist)],"
                    "[PREMULT:2,[PREABILITY:1,CATEGORY=Wraith Haunt Path,Wraith Path of the Poltergeist],"
                    "[PREVARGTEQ:SPHERES_WRAITH_LEVEL,8]]")
            if title.startswith("Expanded Path Possession, Improved ("):
                tags = ["PREVARGTEQ:SPHERES_WRAITH_LEVEL,12",
                        "PREABILITY:1,CATEGORY=Wraith Wraith Haunt,"
                        "Wraith Expanded Path Possession (requires haunt path - path sphere of the selected path)"]
        if category == "Wraith Wraith Haunt" and title == "Extra Incorporeality":
            tags = ["PREVARGTEQ:SPHERES_WRAITH_LEVEL,3", "MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                    "BONUS:VAR|SPHERES_WRAITH_FORM_ROUNDS|4|PREVARLT:SPHERES_WRAITH_LEVEL,20"]
        if category == "Wraith Wraith Haunt" and title == "Forced Wraith Form (requires share wraith form)":
            tags = ["PREVARGTEQ:SPHERES_WRAITH_LEVEL,3",
                    "PREABILITY:1,CATEGORY=Wraith Wraith Haunt,Wraith Share Wraith Form",
                    "MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                    "PREVARLT:SPHERES_WRAITH_FORCED_FORM_COUNT,2",
                    "BONUS:VAR|SPHERES_WRAITH_FORCED_FORM_COUNT|1"]
        lines.append(f"{slug} {key}\tCATEGORY:{category}\t" + "\t".join(tags) + f"\tDESC:{body}")
    return lines


def skills(intro):
    match = re.search(r"Class Skills:\s*(.*?)\s*Skill Ranks (?:Per|per) Level:\s*(\d+)",
                      intro, re.S)
    if not match:
        raise ValueError("Missing class skills or skill ranks")
    entries = re.findall(r"([\w][\w ’'-]*(?:\([^)]*\))?)\s*\((?:Str|Dex|Con|Int|Wis|Cha)\)", match[1])
    result = []
    for item in entries:
        item = item.strip().replace("’", "'")
        item = re.sub(r"^.*?class skills are\s+", "", item, flags=re.I)
        item = re.sub(r"^and\s+", "", item, flags=re.I)
        if item in ("Craft", "Profession", "Perform", "Knowledge"):
            item = "TYPE=" + item
        elif item.startswith("Knowledge ("):
            item = "TYPE=Knowledge" if item.lower() == "knowledge (all)" else item.title().replace("Knowledge (", "Knowledge (")
        result.append(item)
    if len(result) < 5:
        raise ValueError("Could not parse class skills")
    return "|".join(dict.fromkeys(result)), int(match[2])


def proficiencies(snapshot, magic):
    sections = snapshot["sections"]
    text = next((s["text"] for s in sections if s["heading"].startswith("Weapon and Armor")), "")
    if not text:
        text = sections[0]["text"].split("Proficiencies:", 1)[-1].split("In addition,", 1)[0].split("\n", 1)[0]
    grants = ["Weapon Prof ~ Simple"] if "simple" in text.lower() else []
    if "martial weapons" in text.lower():
        grants.append("Weapon Prof ~ Martial")
    if "light armor" in text.lower() and "no armor" not in text.lower():
        grants.append("Armor Prof ~ Light")
    if "medium armor" in text.lower() and "no armor" not in text.lower() and "not proficient" not in text.lower():
        grants.append("Armor Prof ~ Medium")
    if "heavy armor" in text.lower() and "no armor" not in text.lower() and "not proficient" not in text.lower():
        grants.append("Armor Prof ~ Heavy")
    if "shields" in text.lower() and "no shields" not in text.lower() and "no armor" not in text.lower():
        grants.append("Shield Prof")
    tags = ["ABILITY:Internal|AUTOMATIC|" + "|".join(grants)] if grants else []
    if "buckler" in text.lower() and "shields" not in text.lower():
        tags.append("AUTO:SHIELDPROF|Buckler")
    if "shields" in text.lower() and "no shields" not in text.lower() and "no armor" in text.lower():
        tags.append("ABILITY:Internal|AUTOMATIC|Shield Prof")
    if magic and snapshot["url"].rsplit("/", 1)[-1] in ("eliciter", "symbiat"):
        tags.append("AUTO:WEAPONPROF|Longsword|Rapier|Sap|Sword (Short)|Shortbow|Whip")
    if magic and snapshot["url"].endswith("/wraith"):
        tags.append("AUTO:WEAPONPROF|Scythe")
    return tags


def choice_features(name, rows):
    """Slot only explicitly recurring selections, never action effects or scaling bonuses."""
    groups = {
        "Armorist": ("arsenal trick",), "Eliciter": ("emotion",),
        "Hedgewitch": ("secret",), "Mageknight": ("mystic combat",),
        "Shifter": ("bestial trait",), "Soul Weaver": ("nexus powers", "blessing/blight"),
        "Thaumaturge": ("invocations",),
        "Wraith": ("wraith haunt",), "Armiger": ("prowess",),
        "Blacksmith": ("smithing insight",), "Commander": ("battlefield specialist", "logistic specialty"),
        "Scholar": ("scholar’s knack", "material imposition"),
        "Striker": ("striker art",), "Technician": ("technical insight",),
    }
    result = {}
    for group in groups.get(name, ()):
        levels = []
        for level, row in enumerate(rows, 1):
            # Avoid counting a similarly named progression boost as a new choice.
            if re.search(r"(?:^|,\s*)" + re.escape(group) + r"(?:\s*\([^)]*\))?(?:,|$)",
                         row[5].lower()):
                levels.append(level)
        if levels:
            result[group] = levels
    return result


def numeric_features(name, prefix):
    """Class-level-derived values whose combat application needs no assumptions."""
    level = prefix + "_LEVEL"
    mapping = {
        "Wraith": (("Form Rounds", f"if({level}>=20,0,{level}+SPHERES_CASTING_ABILITY)", "daily wraith form rounds; zero denotes unlimited only when Form Unlimited is one"),
                   ("Form Unlimited", f"if({level}>=20,1,0)", "unlimited wraith form at level 20; activation remains required"),
                   ("Haunt DC", f"10+floor({level}/2)+SPHERES_CASTING_ABILITY", "save DC for wraith haunts that call for saves"),
                   ("Possession DC", f"if({level}<2,0,10+floor({level}/2)+SPHERES_CASTING_ABILITY)", "possession save DC from level 2; host effects are table-resolved"),
                   ("Possession Targets", f"if({level}<2,0,if({level}<10,1,max(2,SPHERES_CASTING_ABILITY)))", "simultaneously possessed creatures; actions are shared, not multiplied")),
        "Commander": (("Group Focus Uses", f"max(0,1+floor(({level}-5)/6))", "daily group focus uses from level 5; recovery and ally effects are table-resolved"),
                      ("Active Enhanced Tactics", f"if({level}<2,0,if({level}<10,1,if({level}<20,2,3)))", "maximum simultaneous enhanced tactics; activation and switching remain table-resolved")),
        "Eliciter": (("Persuasive", f"2+floor({level}/6)", "bonus to Mind sphere and eliciter DCs, Bluff, Diplomacy and Intimidate"),
                     ("Hypnotism Uses", f"3+floor({level}/2)", "uses per day; DC includes the persuasive bonus")),
        "Armorist": (("Bound Items", f"1+floor({level}/5)", "pieces of bound equipment"),
                     ("Armor Training", f"max(0,floor(({level}+1)/4))", "armor check penalty reduction and increase to maximum Dexterity bonus while wearing armor")),
        "Soul Weaver": (("Channel Dice", f"floor(({level}+1)/2)", "d6 channel energy; positive or negative channel is a permanent choice"),
                        ("Channel DC", f"10+floor({level}/2)+CHA", "saving throw DC for channel energy; Charisma-based"),
                        ("Nexus DC", f"10+floor({level}/2)+SPHERES_CASTING_ABILITY", "saving throw DC when a bound nexus power requires a save"),
                        ("Channel Uses", "max(1,3+CHA)", "channel uses per day; Charisma-based, not casting-ability-based"),
                        ("Bound Souls", "max(1,3+SPHERES_CASTING_ABILITY)", "souls replenished when resting to regain spell points; spending and movement remain table-resolved")),
        "Blacksmith": (("Thunderous Blows Dice", f"floor(({level}+1)/2)", "d6 conditional damage on qualifying attacks or sunders"),),
        "Technician": (("Trapfinding", f"max(1,floor({level}/2))", "bonus to locating traps and Disable Device checks"),),
        "Sentinel": (("Reserve Points", f"max(1,floor({level}/2)+WIS)", "daily reserve points; spending and recovery are table-resolved"),
                     ("Reserve Temporary HP", "2*BAB+WIS", "temporary hit points per reserve point; lasts one minute or until lost, not a permanent HP increase")),
        "Mageknight": (("Resist Magic", f"1+floor(({level}-1)/4)", "saving throw bonus against spells, spell-like abilities, and magic sphere effects"),),
        "Symbiat": (("Psionics Rounds", f"4+INT+2*({level}-1)", "rounds per day of psionic effects"),),
        "Thaumaturge": (("Invocation Uses", f"SPHERES_CASTING_ABILITY+floor({level}/2)", "uses per day of invocations; only one invocation per roll"),
                        ("Invocation DC", f"10+floor({level}/2)+SPHERES_CASTING_ABILITY", "saving throw DC for invocations"),
                        ("Forbidden Lore", f"2+floor(({level}-1)/4)", "caster-level increase on one qualifying effect when invoked, subject to backlash; not a permanent caster-level increase")),
        "Fey Adept": (("Shadowmark Dice", f"floor(({level}+1)/2)", "d6 shadowmark damage when its conditions are met"),
                      ("Shadowmark Die Size", "6", "sides per shadowmark damage die; modified by Greater Shadowmark"),
                      ("Shadow Points", f"max(1,CHA+floor({level}/2))", "shadow point capacity; Charisma-based; refills when all spell points are regained"),
                      ("Shadowmark Penalty", f"1+floor(({level}-1)/6)", "magnitude of target Will penalty against your sphere effects for one minute; does not stack with itself"),
                      ("Master Illusionist Rounds", f"max(1,floor({level}/2))", "rounds an illusion remains after concentration ends"),
                      ("Truesight Uses", f"floor({level}/4)", "uses per day of truesight from level 4")),
    }
    features = []
    for key, formula, context in mapping.get(name, ()):
        variable = prefix + "_" + re.sub(r"\W+", "_", key.upper())
        features.append(f"{name} {key} (Reference)\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t"
                        f"DEFINE:{variable}|0\tBONUS:VAR|{variable}|{formula}\t"
                        f"DESC:%{variable} {context}; apply to qualifying rolls or uses only.")
        if name == "Technician" and key == "Trapfinding":
            features[-1] += (f"\tBONUS:SKILL|Disable Device|{variable}|TYPE=Trapfinding"
                             f"\tBONUS:SITUATION|Perception=Trapfinding|{variable}|TYPE=Trapfinding")
        if name == "Armorist" and key == "Armor Training":
            features[-1] += (f"\tBONUS:MISC|MAXDEX|{variable}|PREEQUIP:1,TYPE=Armor"
                             f"\tBONUS:MISC|ACCHECK|{variable}|PREEQUIP:1,TYPE=Armor"
                             f"\tABILITY:Special Ability|AUTOMATIC|Armorist Medium Armor Movement|PREVARGTEQ:{level},3"
                             f"\tABILITY:Special Ability|AUTOMATIC|Armorist Heavy Armor Movement|PREVARGTEQ:{level},7")
        if name == "Eliciter" and key == "Persuasive":
            features[-1] += (f"\tBONUS:SKILL|Bluff,Diplomacy,Intimidate|{variable}"
                             f"\tBONUS:VAR|SPHERES_DC_MIND|{variable}"
                             "\tDEFINE:SPHERES_ELICITER_CLASS_DC|0"
                             f"\tBONUS:VAR|SPHERES_ELICITER_CLASS_DC|10+floor({level}/2)+CHA+{variable}")
    return features


def table_values_feature(name, prefix, key, values, context):
    """Pin nonuniform numeric progressions to the actual twenty-row table."""
    variable = prefix + "_" + key.upper().replace(" ", "_")
    steps = []
    previous = 0
    for level, value in enumerate(values, 1):
        if value < previous:
            raise ValueError(f"{key} decreases in {name} table")
        if value != previous:
            steps.append(f"{value-previous}*if({prefix}_LEVEL>={level},1,0)")
        previous = value
    formula = "+".join(steps) if steps else "0"
    return (f"{name} {key} (Reference)\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t"
            f"DEFINE:{variable}|0\tBONUS:VAR|{variable}|{formula}\t"
            f"DESC:%{variable} {context}; consult class rules before applying in play.")


def generate(slug):
    if slug not in NAMES:
        raise ValueError(f"Unsupported base class: {slug}")
    source = json.loads((SNAPSHOTS / f"{slug}.json").read_text())
    headers, rows = table(source)
    name = class_name(slug)
    prefix = "SPHERES_" + slug.replace("-", "_").upper()
    magic = "Magic Talents" in headers or "Talents" in headers and "Combat Talents" not in headers
    talent_column = headers.index("Magic Talents") if "Magic Talents" in headers else headers.index("Talents") if magic else headers.index("Combat Talents")
    caster_column = headers.index("Caster Level") if magic else None
    intro = source["sections"][0]["text"]
    skill_list, ranks = skills(intro)
    hd = number(re.search(r"Hit Die:\s*d(\d+)", intro)[1])
    bab = [number(row[1]) for row in rows]
    saves = [[number(row[j]) for row in rows] for j in (2, 3, 4)]
    if bab not in [[level for level in range(1, 21)], [level * 3 // 4 for level in range(1, 21)], [level // 2 for level in range(1, 21)]]:
        raise ValueError(f"Unexpected BAB: {name}")
    for save in saves:
        if save not in [[2 + level // 2 for level in range(1, 21)], [level // 3 for level in range(1, 21)]]:
            raise ValueError(f"Unexpected save: {name}")
    formula = "CL" if bab[-1] == 20 else "floor(CL*3/4)" if bab[-1] == 15 else "floor(CL/2)"
    class_tags = [f"HD:{hd}", "TYPE:Base.PC", "MAXLEVEL:20", f"STARTSKILLPTS:{ranks}", f"CSKILL:{skill_list}",
                  f"BONUS:COMBAT|BASEAB|{formula}|TYPE=Base.REPLACE", f"DEFINE:{prefix}_LEVEL|0", f"BONUS:VAR|{prefix}_LEVEL|CL"]
    for save_name, values in zip(("Fortitude", "Reflex", "Will"), saves):
        class_tags.append(f"BONUS:SAVE|BASE.{save_name}|" + ("2+floor(CL/2)" if values[0] == 2 else "floor(CL/3)"))
    if magic:
        caster = [number(row[caster_column]) for row in rows]
        if caster not in [[level for level in range(1, 21)], [level * 3 // 4 for level in range(1, 21)], [level // 2 for level in range(1, 21)]]:
            raise ValueError(f"Unexpected caster level: {name}")
        cl_formula = "CL" if caster[-1] == 20 else "floor(CL*3/4)" if caster[-1] == 15 else "floor(CL/2)"
        class_tags.extend((f"BONUS:VAR|SPHERES_CASTER_LEVEL,SPHERES_MAGIC_SKILL_BONUS|{cl_formula}",
                           "BONUS:VAR|SPHERES_SPELL_POOL_LEVELS|CL"))
    else:
        class_tags.append("DEFINE:SPHERES_COMBAT_TALENTS|0")
        class_tags.append("DEFINE:SPHERES_PRACTITIONER_MOD|0")
    raw_talents = [number(row[talent_column]) for row in rows]
    if any(b < a for a, b in zip(raw_talents, raw_talents[1:])):
        raise ValueError(f"Talents decrease: {name}")
    lines = [f"# {source['url']} ({source['retrieved']}); numeric progression from the source table.",
             f"CLASS:{name}\t" + "\t".join(class_tags)]
    abilities = ["# Class-table features are rules text unless an explicit PCGen numeric grant is present."]
    numeric = numeric_features(name, prefix)
    if name == "Symbiat":
        numeric.extend((table_values_feature(name, prefix, "Pushed Movement Feet",
                                             [number(row[headers.index("Pushed Movement")]) for row in rows],
                                             "feet of bonus movement when pushed movement is active"),
                        table_values_feature(name, prefix, "Battlefield AC",
                                             [number(row[headers.index("AC Bonus")]) for row in rows],
                                             "AC bonus only when battlefield sense conditions are satisfied")))
    if name == "Armiger":
        numeric.append(table_values_feature(name, prefix, "Talents Per Customized Weapon",
                                            [number(row[headers.index("Talents Granted per Customized Weapon")]) for row in rows],
                                            "talents assigned separately to each customized weapon; do not add to the general combat talent pool"))
    if name == "Technician":
        numeric.append(table_values_feature(name, prefix, "Improvements Per Invention",
                                            [max((number(match.group(1)) for previous_row in rows[:i]
                                                  if (match := re.search(r"improvements\s*\((\d+)\)", previous_row[5], re.I))),
                                                 default=1)
                                             for i in range(1, 21)],
                                            "improvements available to each invention"))
    abilities.extend(numeric)
    choices = choice_features(name, rows)
    for level, row in enumerate(rows, 1):
        grants = []
        if name == "Symbiat":
            if level == 2:
                grants.append("BONUS:SKILL|Sense Motive,Perception|floor(SPHERES_SYMBIAT_LEVEL/2)")
            if level == 3:
                grants.append("BONUS:MOVEADD|TYPE=Walk|10*min(6,floor(SPHERES_SYMBIAT_LEVEL/3))")
            if level in (2, 9):
                grants.append("ABILITY:Special Ability|AUTOMATIC|" + ("Evasion" if level == 2 else "Improved Evasion"))
            if level == 3:
                grants.extend(["ABILITY:Special Ability|AUTOMATIC|Trap Sense",
                               "BONUS:VAR|TrapSenseBonus|floor(SPHERES_SYMBIAT_LEVEL/3)",
                               "BONUS:SITUATION|Perception=Avoid being surprised|floor(SPHERES_SYMBIAT_LEVEL/3)"])
            if level in (4, 8):
                grants.append("BONUS:VAR|UncannyDodgeLVL|1")
                if level == 4:
                    grants.extend(["ABILITY:Special Ability|AUTOMATIC|Uncanny Dodge ~ Base",
                                   "BONUS:VAR|UncannyDodgeFlankingLevel|SPHERES_SYMBIAT_LEVEL|TYPE=EachClass.REPLACE"])
        if name == "Fey Adept" and level == 2:
            grants.extend(["VISION:Darkvision (30')", "BONUS:VISION|Darkvision|30"])
        if name == "Fey Adept" and level == 14:
            grants.append("ABILITY:Special Ability|AUTOMATIC|Fey Adept See in Darkness")
            abilities.append("Fey Adept See in Darkness\tCATEGORY:Special Ability\t"
                             "TYPE:SpheresClassFeature.SpecialQuality.Supernatural\tVISION:See in Darkness\t"
                             "DESC:See perfectly in darkness of any kind, including magical darkness.")
        if name == "Fey Adept" and level == 20:
            grants.append("ABILITY:Special Ability|AUTOMATIC|Fey Adept Feytouched")
            abilities.append("Fey Adept Feytouched\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t"
                             "DR:10/cold iron\tBONUS:SAVE|ALL|2|TYPE=Luck\t"
                             "DESC:Treated as fey for spells and magical effects only; "
                             "this does not globally replace creature type.")
        if name == "Soul Weaver" and level == 20:
            grants.append("ABILITY:Special Ability|AUTOMATIC|Soul Weaver Gravewalker")
            abilities.append("Soul Weaver Gravewalker\tCATEGORY:Special Ability\t"
                             "TYPE:SpheresClassFeature.SpecialQuality.Supernatural.Immunity\t"
                             "ASPECT:Immunity|Nonlethal Damage, Ability Drain, Energy Drain\t"
                             "DESC:Immune to nonlethal damage, ability drain and energy drain. "
                             "Unintelligent undead ignore you unless provoked. On death you may "
                             "choose to rise as a ghost 2d4 days later; resolve this choice at the table. "
                             "This feature does not change your creature type or apply a ghost template.")
        if name == "Striker" and level in (3, 12):
            grants.append("BONUS:VAR|UncannyDodgeLVL|1")
            if level == 3:
                grants.append("BONUS:VAR|UncannyDodgeFlankingLevel|SPHERES_STRIKER_LEVEL|TYPE=EachClass.REPLACE")
        if name == "Blacksmith" and level == 2:
            grants.append("BONUS:SKILL|Profession (Blacksmith)|max(1,floor(SPHERES_BLACKSMITH_LEVEL/2))|TYPE=Competence")
        if name == "Blacksmith" and level in (3, 5):
            grants.append("ABILITY:FEAT|AUTOMATIC|" +
                          ("Craft Wondrous Item" if level == 3 else "Craft Magic Arms and Armor"))
        if level == 1:
            if name == "Striker":
                grants.extend(striker_resources())
            if name in ("Mageknight", "Armorist"):
                # Keep the pool definition alive when one repeated Combat Talent
                # selection is removed; PCGen removes that selection's DEFINE.
                grants.append("DEFINE:SPHERES_COMBAT_TALENTS|0")
            grants += proficiencies(source, magic)
            grants.append("ABILITY:Special Ability|AUTOMATIC|" + ("Spheres Casting Core" if magic else f"{name} Combat Training"))
            grants += ["ABILITY:Special Ability|AUTOMATIC|" + entry.split("\t", 1)[0] for entry in numeric]
        feature_key = f"{name} Class Features {level}"
        grants.append("ABILITY:Special Ability|AUTOMATIC|" + feature_key)
        special = row[5].replace("|", "/").replace("\t", " ") or "No new class-table feature"
        feature_type = "SpheresClassFeature"
        if name == "Eliciter" and level == 2:
            feature_type += ".SpheresEmotion"
        abilities.append(f"{feature_key}\tCATEGORY:Special Ability\tTYPE:{feature_type}\tDESC:Level {level}: {special}. See {source['url']} for effects, timing and prerequisites.")
        delta = raw_talents[level - 1] - (raw_talents[level - 2] if level > 1 else 0)
        if delta:
            grants.append(f"BONUS:VAR|{'SPHERES_MAGIC_TALENTS' if magic else 'SPHERES_COMBAT_TALENTS'}|{delta}")
        lines.append(f"{level}\t" + "\t".join(grants))
    if not magic:
        practitioner = {"Blacksmith": "CON", "Striker": "CON", "Sentinel": "WIS", "Scholar": "INT", "Technician": "INT",
                        "Commander": "max(CHA,INT)"}.get(name)
        abilities.append(f"{name} Combat Training\tCATEGORY:Special Ability\tTYPE:SpheresInternal.SpheresCombatTraining\t"
                         "ABILITY:Special Ability|AUTOMATIC|Spheres Martial Focus\t"
                         "DEFINE:SPHERES_PRACTITIONER_DC|0\t" +
                         (f"BONUS:VAR|SPHERES_PRACTITIONER_MOD|{practitioner}\t" if practitioner else
                          f"DESC:Choose Intelligence, Wisdom or Charisma as the {name} practitioner modifier.\t") +
                         f"BONUS:VAR|SPHERES_PRACTITIONER_DC|10+floor({prefix}_LEVEL/2)+SPHERES_PRACTITIONER_MOD")
    else:
        free = {"Eliciter": "Mind", "Fey Adept": "Illusion", "Shifter": "Alteration"}.get(name)
        if free:
            bonus = (f"\tBONUS:VAR|SPHERES_CL_{free.upper()}|{prefix}_LEVEL-SPHERES_CASTER_LEVEL"
                     if name in ("Eliciter", "Shifter") else "")
            abilities.append(f"{name} Sphere Mastery\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t"
                             f"ABILITY:Spheres Magic Talent|AUTOMATIC|{free} Sphere{bonus}\t"
                             f"DESC:Free {free} sphere; class-level caster level for this sphere where specified by the source.")
            lines[2] += f"\tABILITY:Special Ability|AUTOMATIC|{name} Sphere Mastery"
        if name == "Symbiat":
            abilities.append("Symbiat Mental Powers\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tABILITY:Spheres Magic Talent|AUTOMATIC|Mind Sphere|Telekinesis Sphere\tDESC:Two bonus spheres from mental powers.")
            lines[2] += "\tABILITY:Special Ability|AUTOMATIC|Symbiat Mental Powers"
    if name == "Mageknight":
        lines[2] += "\tBONUS:VAR|SPHERES_MAGIC_TALENTS|1"
    if name == "Mageknight":
        feature = "Mystic Combat"
        marker = f"{name} {feature} Feature"
        abilities.append(f"{marker}\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature.Spheres{feature.replace(' ', '')}")
        lines[3] += "\tABILITY:Special Ability|AUTOMATIC|" + marker
    if name == "Blacksmith":
        # Equipment Sphere grants an extra sphere talent on acquisition. Do not
        # grant it automatically: the source awards one talent, not two.
        abilities.append("Blacksmith Equipment Specialist\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tDESC:Gain one Equipment sphere talent at 1st level. Record the free talent separately; it does not consume a class combat talent.")
        lines[2] += "\tABILITY:Special Ability|AUTOMATIC|Blacksmith Equipment Specialist"
    if name == "Soul Weaver":
        categories_for_channel = (f"ABILITYCATEGORY:Soul Weaver Channel\tCATEGORY:Soul Weaver Channel\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:min(1,{prefix}_LEVEL)\tPLURAL:Channel Alignment\tDISPLAYLOCATION:Spheres")
    else:
        categories_for_channel = ""
    categories = []
    if name == "Technician":
        lines[2] += "\tDEFINE:SPHERES_TECHNICIAN_INTUITION|0\tDEFINE:SPHERES_TECHNICIAN_LUCK|0"
        lines[2] += "\t" + "\t".join(technician_class_tags())
    if name == "Scholar":
        lines[2] += "\tDEFINE:SPHERES_SCHOLAR_STUDIED_TECHNIQUE|0"
        lines[2] += "\t" + "\t".join(medical_resources())
        medical_category, medical_ability = medical_records()
        categories.append(medical_category)
        abilities.append(medical_ability)
    if name == "Armiger":
        categories.append(armiger_feat_category())
        for feat in ("Deadly Aim", "Piranha Strike", "Power Attack"):
            lines[2] += "\tDEFINE:ArmigerDeadly " + feat + "|0"
            lines[2] += "\tABILITY:FEAT|AUTOMATIC|" + feat + "|PREVARGTEQ:ArmigerDeadly " + feat + ",1"
        for sphere in ("Sniper", "Barrage"):
            lines[2] += "\tDEFINE:ArmigerRanged " + sphere + "|0"
            lines[2] += "\tABILITY:Spheres Combat Talent|AUTOMATIC|" + sphere + " Sphere|PREVARGTEQ:ArmigerRanged " + sphere + ",1"
    if name == "Blacksmith":
        categories.append(blacksmith_feat_category())
    if name == "Armorist":
        categories.extend(armorist_feat_categories())
        abilities.extend(["Armorist Medium Armor Movement\tCATEGORY:Special Ability\tUNENCUMBEREDMOVE:MediumArmor",
                          "Armorist Heavy Armor Movement\tCATEGORY:Special Ability\tUNENCUMBEREDMOVE:HeavyArmor"])
    if name == "Mageknight":
        review_category, review_ability = mageknight_review()
        categories.append(review_category)
        categories.extend(mageknight_feat_categories())
        abilities.append(review_ability)
    option_sections = {
        "armorist": {"arsenal trick": "Arsenal Trick"},
        "eliciter": {"emotion": "List of Emotions"},
        "hedgewitch": {"secret": "Secret"},
        "mageknight": {"mystic combat": "Mystic Combat (Su)"},
        "shifter": {"bestial trait": "Bestial Trait"},
        "soul-weaver": {"nexus powers": "Bound Nexus (Su)"},
        "thaumaturge": {"invocations": "Invocations"},
        "wraith": {"wraith haunt": "Wraith Haunts"},
        "armiger": {"prowess": "Prowess"},
        "blacksmith": {"smithing insight": "Smithing Insight (Ex)"},
        "commander": {"battlefield specialist": "Battlefield Specialist (Ex)",
                      "logistic specialty": "Logistic Specialty (Ex)"},
        "scholar": {"scholar’s knack": "Scholar’s Knack (Ex)",
                    "material imposition": "Material Imposition"},
        "striker": {"striker art": "Striker Art (Ex)"},
        "technician": {"technical insight": "List of Technical Insights"},
    }
    for group, levels in choices.items():
        if name == "Thaumaturge" and group == "invocations":
            from spheres_thaumaturge import INVOCATION_LEVELS, invocation_records, master_records
            master_category, master_choices = master_records()
            categories.append(master_category)
            abilities.extend(master_choices)
            abilities.append('Thaumaturge Occult Knowledge\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t'
                             'BONUS:SKILL|TYPE.Knowledge,Spellcraft,Use Magic Device|min(5,1+floor((SPHERES_THAUMATURGE_LEVEL-2)/4))\t'
                             'DESC:Scaling bonus to Knowledge, Spellcraft and Use Magic Device checks.')
            lines[3] += '\tABILITY:Special Ability|AUTOMATIC|Thaumaturge Occult Knowledge'
            category = "Thaumaturge Invocations"
            categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:NO\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tPLURAL:Invocations\tDISPLAYLOCATION:Spheres")
            abilities.extend(invocation_records(source_options(source, "Invocations")))
            for title, at in INVOCATION_LEVELS.items():
                lines[at + 1] += f"\tABILITY:{category}|AUTOMATIC|Thaumaturge {title}"
            continue
        if name == "Soul Weaver" and group == "nexus powers":
            from spheres_soul_weaver import NEXUS_LEVELS, nexus_records
            category = "Soul Weaver Nexus Powers"
            categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:NO\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tPLURAL:Bound Nexus Powers\tDISPLAYLOCATION:Spheres")
            abilities.extend(nexus_records(source_options(source, "Bound Nexus (Su)")))
            for title, at in NEXUS_LEVELS.items():
                lines[at + 1] += f"\tABILITY:{category}|AUTOMATIC|Soul Weaver {title}"
            continue
        title = group.title().replace("’", "'")
        category = f"{name} {title}"
        pool = "+".join(f"if({prefix}_LEVEL>={level},1,0)" for level in levels)
        categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:{pool}\tPLURAL:{category} Choices\tDISPLAYLOCATION:Spheres")
        section = option_sections.get(slug, {}).get(group)
        if section:
            abilities.extend(option_abilities(name, category, section, source))
        else:
            abilities.append(f"{title} (Manual)\tCATEGORY:{category}\tMULT:YES\tSTACK:YES\tCHOOSE:USERINPUT|1|TITLE={category} choice\tDESC:Record the source-legal {group} option: %1. Prerequisites and effects require adjudication.|%LIST")
    if name == "Hedgewitch":
        for option in option_abilities(name, "Hedgewitch Secret", "Grand Secrets", source):
            abilities.append(option.replace(f"PREVARGTEQ:{prefix}_LEVEL,1", f"PREVARGTEQ:{prefix}_LEVEL,10"))
    if name == "Commander":
        category = "Commander Enhanced Tactic"
        categories.append("ABILITYCATEGORY:Commander Teamwork Feat\tCATEGORY:FEAT\tTYPE:Teamwork\t"
                          "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\t"
                          "PLURAL:Commander Teamwork Feats\tDISPLAYLOCATION:Feats")
        pool = "+".join(f"if({prefix}_LEVEL>={at},1,0)" for at in range(2, 21, 2))
        categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:{pool}\tPLURAL:Enhanced Tactics\tDISPLAYLOCATION:Spheres")
        abilities.extend(option_abilities(name, category, "Enhanced Tactics (Ex)", source))
    if name == "Thaumaturge":
        categories.append(f"ABILITYCATEGORY:Thaumaturge Bonus Feat\tCATEGORY:FEAT\tTYPE:ItemCreation.Metamagic.SpheresCasting\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:floor({prefix}_LEVEL/4)\tPLURAL:Thaumaturge Bonus Feats\tDISPLAYLOCATION:Feats")
        abilities.append(f"Thaumaturge Bonus Feats\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tDESC:Choose an extra magic talent or feat with casting as a prerequisite every four thaumaturge levels; validate eligibility manually.")
        lines[2] += "\tABILITY:Special Ability|AUTOMATIC|Thaumaturge Bonus Feats"
    if categories_for_channel:
        categories.append(categories_for_channel)
        from spheres_soul_weaver import blessing_records
        records, grants = blessing_records(source_options(source, 'List of Blessings'),
                                          source_options(source, 'List of Blights'))
        abilities.extend(records)
        for polarity, sphere in (('Positive', 'Life'), ('Negative', 'Death')):
            abilities.append(f'Soul Weaver {polarity} Channel\tCATEGORY:Soul Weaver Channel\t'
                             f'ABILITY:Spheres Magic Talent|AUTOMATIC|{sphere} Sphere\t'
                             + '\t'.join(grants[polarity])
                             + f'\tDESC:{polarity} channel energy and free {sphere} sphere; '
                             'blessings/blights are granted at their class levels. Resolve effects on targets at the table.')
    if name == "Armiger":
        categories.append(f"ABILITYCATEGORY:Armiger Practitioner Ability\tCATEGORY:Armiger Practitioner Ability\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:min(1,{prefix}_LEVEL)\tPLURAL:Practitioner Ability\tDISPLAYLOCATION:Spheres")
        for stat, label in (("INT", "Intelligence"), ("WIS", "Wisdom"), ("CHA", "Charisma")):
            abilities.append(f"Armiger {label} Practitioner\tCATEGORY:Armiger Practitioner Ability\tBONUS:VAR|SPHERES_PRACTITIONER_MOD|{stat}")
    if name == "Hedgewitch":
        categories.append(f"ABILITYCATEGORY:Hedgewitch Path\tCATEGORY:Hedgewitch Path\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:2*min(1,{prefix}_LEVEL)\tPLURAL:Hedgewitch Paths\tDISPLAYLOCATION:Spheres")
        abilities.extend(option_abilities(name, "Hedgewitch Path", "List of Paths", source))
    if name == "Wraith":
        lines[2] += "\tDEFINE:SPHERES_WRAITH_FORCED_FORM_COUNT|0"
        abilities.append("Wraith Haunts\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature.SpheresWraithHaunt\tDESC:Wraith haunt selections; each haunt retains its own prerequisites.")
        lines.append("3\tABILITY:Special Ability|AUTOMATIC|Wraith Haunts")
        categories.append(f"ABILITYCATEGORY:Wraith Haunt Path\tCATEGORY:Wraith Haunt Path\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:min(1,{prefix}_LEVEL)\tPLURAL:Wraith Haunt Path\tDISPLAYLOCATION:Spheres")
        for title, text in source_options(source, "List of Haunt Paths"):
            if not title.startswith("Path of the "):
                continue
            title = re.sub(r"\s*\[[^]]+\]", "", title)
            body = text.split("Improved Path Possession:", 1)[0][:900]
            body = re.sub(r"\s+", " ", body).replace("|", "/").replace("%", "percent").replace("(", "[").replace(")", "]")
            match = re.search(r"Path Sphere:\s*([\w ]+?)(?=\s+Path Possession:)", text)
            if not match:
                raise ValueError(f"Missing haunt path sphere: {title}")
            skill_match = re.search(r"Path Skill:\s*([^\n]+?)\s*\((?:Str|Dex|Con|Int|Wis|Cha)\)", text)
            if not skill_match:
                raise ValueError(f"Missing haunt path skill: {title}")
            path_skill = skill_match[1].strip().title()
            for sphere in (s.strip() for s in match.group(1).split(" or ")):
                if not (DATA / f"spheres_power_{sphere.lower()}.lst").is_file():
                    raise ValueError(f"Unknown haunt path sphere: {sphere}")
                key = f"Wraith {title}" + (f" - {sphere}" if " or " in match.group(1) else "")
                sphere_bonus = (f"\tABILITY:Spheres Magic Talent|AUTOMATIC|{sphere} Sphere\t"
                                f"BONUS:VAR|SPHERES_CL_{sphere.upper()}|{prefix}_LEVEL-floor({prefix}_LEVEL*3/4)")
                abilities.append(f"{key}\tCATEGORY:Wraith Haunt Path\tPREVARGTEQ:{prefix}_LEVEL,1{sphere_bonus}"
                                 f"\tCSKILL:{path_skill}\tBONUS:SKILL|{path_skill}|floor({prefix}_LEVEL/2)|TYPE=Insight|PREVARGTEQ:{prefix}_LEVEL,4"
                                 f"\tDESC:{body} Consult source for unrepresented possession effects and duplicate-sphere replacement.")
    if name == "Striker":
        training_category, training_options = striker_training(source)
        categories.append(training_category)
        abilities.extend(training_options)
        categories.append(f"ABILITYCATEGORY:Striker Bare Knuckles\tCATEGORY:Striker Bare Knuckles\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:min(1,{prefix}_LEVEL)\tPLURAL:Bare Knuckles Sphere\tDISPLAYLOCATION:Spheres")
        for sphere in ("Boxing", "Brute", "Open Hand"):
            abilities.append(f"Striker {sphere} Knuckles\tCATEGORY:Striker Bare Knuckles\tABILITY:Spheres Combat Talent|AUTOMATIC|{sphere} Sphere\tDESC:Gain {sphere} sphere without spending a combat talent; if already possessed, choose a legal replacement sphere or talent manually.")
    if name == "Sentinel":
        abilities.append('Sentinel Second Wind\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature.Extraordinary\t'
                         'DEFINE:SPHERES_SENTINEL_SECOND_WIND_DICE|floor(SPHERES_SENTINEL_LEVEL/2)\t'
                         'DEFINE:SPHERES_SENTINEL_SECOND_WIND_BONUS|WIS\t'
                         'DESC:Spend a reserve point as a swift action to heal d6 per two Sentinel levels plus Wisdom modifier, '
                         'up to half maximum HP. Halve healing to regain martial focus, declared before rolling. '
                         'Spending, healing, and the level-7 extra-point exception are table-resolved.')
        lines[4] += '\tABILITY:Special Ability|AUTOMATIC|Sentinel Second Wind'
        abilities.append('Sentinel Wise Reflexes\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature.Extraordinary\t'
                         'BONUS:COMBAT|INITIATIVE|max(0,min(WIS,SPHERES_SENTINEL_LEVEL)-DEX)|TYPE=Ability\t'
                         'BONUS:SAVE|Reflex|max(0,min(WIS,SPHERES_SENTINEL_LEVEL)-DEX)|TYPE=Ability\t'
                         'DESC:Use capped Wisdom instead of Dexterity when it improves initiative or Reflex saves.')
        lines[2] += '\tABILITY:Special Ability|AUTOMATIC|Sentinel Wise Reflexes'
        abilities.append('Sentinel Dedicated Defense\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature.Extraordinary\t'
                         'DR:0/-\tBONUS:DR|-|1+floor((SPHERES_SENTINEL_LEVEL-2)/4)\t'
                         'DESC:Damage reduction stacks with other DR/- sources. Challenge-specific doubling remains table-resolved.')
        lines[3] += '\tABILITY:Special Ability|AUTOMATIC|Sentinel Dedicated Defense'
        abilities.append(f"Sentinel Defender's Soul\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tABILITY:Spheres Combat Talent|AUTOMATIC|Guardian Sphere\tDESC:Free Guardian challenge package; if already possessed, choose a legal Guardian talent instead.")
        lines[2] += "\tABILITY:Special Ability|AUTOMATIC|Sentinel Defender's Soul"
    if name == "Scholar":
        abilities.append("Scholar Problem Solver\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tABILITY:Spheres Combat Talent|AUTOMATIC|Alchemy Sphere|Scout Sphere\tDESC:Free Alchemy and Scout spheres; if already possessed, choose legal talents from those spheres instead.")
        lines[2] += "\tABILITY:Special Ability|AUTOMATIC|Scholar Problem Solver"
    for recipient, title, sphere in (("Commander", "Commander Tactics", "Warleader"),
                                     ("Technician", "Technician Trap Specialist", "Trap")):
        if name == recipient:
            abilities.append(f"{title}\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tABILITY:Spheres Combat Talent|AUTOMATIC|{sphere} Sphere\tDESC:Free {sphere} sphere. If already possessed, choose a legal {sphere} talent instead.")
            lines[2] += f"\tABILITY:Special Ability|AUTOMATIC|{title}"
    for class_title, slot_title, slots, description in (
        ("Armiger", "Customized Weapon", ((1, 3), (11, 1), (19, 1)),
         "Record a customized weapon set and its individually assigned combat talents; the per-weapon progression appears in the source table."),
        ("Technician", "Invention", ((1, 1), (3, 1), (7, 1), (11, 1), (15, 1), (19, 1)),
         "Record an invention base form and its legal improvements; item statistics and improvements require source adjudication."),
        ("Blacksmith", "Equipment Specialist Talent", ((1, 1),),
         "Record the one free Equipment sphere talent; if gaining Equipment sphere itself, apply that sphere's bonus talent too."),
    ):
        if name != class_title:
            continue
        category = f"{name} {slot_title}"
        pool = "+".join(f"{count}*if({prefix}_LEVEL>={at},1,0)" for at, count in slots)
        categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:{pool}\tPLURAL:{category} Choices\tDISPLAYLOCATION:Spheres")
        abilities.append(f"{slot_title} (Manual)\tCATEGORY:{category}\tMULT:YES\tSTACK:YES\tCHOOSE:USERINPUT|1|TITLE={slot_title}\tDESC:{description} Selection: %1.|%LIST")
    if name == "Technician":
        # The wiki has both a top-level invention catalog and a distinct
        # independent-invention base-form catalog. Neither is an archetype.
        end = next(i for i, section in enumerate(source["sections"])
                   if section["heading"] == "Technician Alternate Class Features")
        first = next(i for i, section in enumerate(source["sections"])
                     if section["heading"] == "Inventions" and section["level"] == 1)
        forms = [entry for entry in source["sections"][first + 1:end]
                 if entry["level"] == 2 and entry["heading"] not in ("Base Forms", "Improvements")]
        category = "Technician Invention Base Form"
        categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:1*if({prefix}_LEVEL>=1,1,0)+if({prefix}_LEVEL>=3,1,0)+if({prefix}_LEVEL>=7,1,0)+if({prefix}_LEVEL>=11,1,0)+if({prefix}_LEVEL>=15,1,0)+if({prefix}_LEVEL>=19,1,0)\tPLURAL:Invention Base Forms\tDISPLAYLOCATION:Spheres")
        for entry in forms:
            title = re.sub(r"\s*\[[^]]+\]", "", entry["heading"])
            if title in ("Independent Invention",):
                continue
            body = re.sub(r"\s+", " ", entry["text"][:900]).replace("|", "/").replace("%", "percent").replace("(", "[").replace(")", "]")
            abilities.append(f"Technician {title}\tCATEGORY:{category}\tPREVARGTEQ:{prefix}_LEVEL,1\tDESC:{body} Consult the class source for construction requirements and improvements.")
        abilities.append(f"Technician Independent Invention\tCATEGORY:{category}\tPREVARGTEQ:{prefix}_LEVEL,1\tDESC:Build an independent invention using a source-legal mechanical arm, siege engine or vehicle base form and its improvements. Construct statistics manually.")
    return "\n".join(lines) + "\n", "\n".join(abilities) + "\n", "\n".join(categories) + ("\n" if categories else ""), {"name": name, "magic": magic, "bab": bab, "saves": saves,
                                                                                                            "talents": raw_talents, "caster": caster if magic else None, "choices": choices}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for slug in NAMES:
        class_lst, ability_lst, category_lst, _ = generate(slug)
        for suffix, content in (("class", class_lst), ("features", ability_lst), ("categories", category_lst)):
            if not content:
                continue
            path = DATA / f"spheres_{slug}_{suffix}.lst"
            if args.check:
                if not path.is_file() or path.read_text() != content:
                    raise ValueError(f"Generated class data differs: {path}")
            else:
                path.write_text(content)
        print(f"{slug}: 20 levels, source-table progression")


if __name__ == "__main__":
    main()