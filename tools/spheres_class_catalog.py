"""Generate PF1 Spheres base-class progressions from pinned class tables.

Only class-table numbers and grants are automated. Descriptions explicitly retain
the source's context-dependent features without pretending to run combat actions.
"""
import argparse
import json
import re

from spheres_catalog_source import ROOT, SNAPSHOTS
from spheres_mageknight import option_tags as mageknight_tags, review_records as mageknight_review

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
        "Eliciter": (("Persuasive", f"2+floor({level}/6)", "bonus to Mind sphere and eliciter DCs, Bluff, Diplomacy and Intimidate"),
                     ("Hypnotism Uses", f"3+floor({level}/2)", "uses per day; DC includes the persuasive bonus")),
        "Armorist": (("Bound Items", f"1+floor({level}/5)", "pieces of bound equipment"),
                     ("Armor Training", f"max(0,floor(({level}+1)/4))", "armor check penalty reduction and increase to maximum Dexterity bonus while wearing armor")),
        "Soul Weaver": (("Channel Dice", f"floor(({level}+1)/2)", "d6 channel energy; positive or negative channel is a permanent choice"),),
        "Blacksmith": (("Thunderous Blows Dice", f"floor(({level}+1)/2)", "d6 conditional damage on qualifying attacks or sunders"),),
        "Technician": (("Trapfinding", f"max(1,floor({level}/2))", "bonus to locating traps and Disable Device checks"),),
        "Sentinel": (("Reserve Points", f"max(1,floor({level}/2)+WIS)", "daily reserve points; temporary HP from a spent point is 2 x BAB + WIS"),),
        "Mageknight": (("Resist Magic", f"1+floor(({level}-1)/4)", "saving throw bonus against spells, spell-like abilities, and magic sphere effects"),),
        "Symbiat": (("Psionics Rounds", f"4+INT+2*({level}-1)", "rounds per day of psionic effects"),),
        "Thaumaturge": (("Invocation Uses", f"SPHERES_CASTING_ABILITY+floor({level}/2)", "uses per day of invocations; only one invocation per roll"),
                        ("Forbidden Lore", f"2+floor(({level}-1)/4)", "caster-level increase on one qualifying effect when invoked, subject to backlash; not a permanent caster-level increase")),
        "Fey Adept": (("Shadowmark Dice", f"floor(({level}+1)/2)", "d6 shadowmark damage when its conditions are met"),
                      ("Truesight Uses", f"floor({level}/4)", "uses per day of truesight from level 4")),
    }
    features = []
    for key, formula, context in mapping.get(name, ()):
        variable = prefix + "_" + re.sub(r"\W+", "_", key.upper())
        features.append(f"{name} {key} (Reference)\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t"
                        f"DEFINE:{variable}|0\tBONUS:VAR|{variable}|{formula}\t"
                        f"DESC:%{variable} {context}; apply to qualifying rolls or uses only.")
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
        if level == 1:
            if name == "Mageknight":
                # Keep the pool definition alive when one repeated Combat Talent
                # selection is removed; PCGen removes that selection's DEFINE.
                grants.append("DEFINE:SPHERES_COMBAT_TALENTS|0")
            grants += proficiencies(source, magic)
            grants.append("ABILITY:Special Ability|AUTOMATIC|" + ("Spheres Casting Core" if magic else f"{name} Combat Training"))
            grants += ["ABILITY:Special Ability|AUTOMATIC|" + entry.split("\t", 1)[0] for entry in numeric]
        feature_key = f"{name} Class Features {level}"
        grants.append("ABILITY:Special Ability|AUTOMATIC|" + feature_key)
        special = row[5].replace("|", "/").replace("\t", " ") or "No new class-table feature"
        abilities.append(f"{feature_key}\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tDESC:Level {level}: {special}. See {source['url']} for effects, timing and prerequisites.")
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
    if name == "Mageknight":
        review_category, review_ability = mageknight_review()
        categories.append(review_category)
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
        pool = "+".join(f"if({prefix}_LEVEL>={at},1,0)" for at in range(2, 21, 2))
        categories.append(f"ABILITYCATEGORY:{category}\tCATEGORY:{category}\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:{pool}\tPLURAL:Enhanced Tactics\tDISPLAYLOCATION:Spheres")
        abilities.extend(option_abilities(name, category, "Enhanced Tactics (Ex)", source))
    if name == "Thaumaturge":
        categories.append(f"ABILITYCATEGORY:Thaumaturge Bonus Feat\tCATEGORY:FEAT\tTYPE:ItemCreation.Metamagic.SpheresCasting\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:floor({prefix}_LEVEL/4)\tPLURAL:Thaumaturge Bonus Feats\tDISPLAYLOCATION:Feats")
        abilities.append(f"Thaumaturge Bonus Feats\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\tDESC:Choose an extra magic talent or feat with casting as a prerequisite every four thaumaturge levels; validate eligibility manually.")
        lines[2] += "\tABILITY:Special Ability|AUTOMATIC|Thaumaturge Bonus Feats"
    if categories_for_channel:
        categories.append(categories_for_channel)
        abilities.extend(("Soul Weaver Positive Channel\tCATEGORY:Soul Weaver Channel\tABILITY:Spheres Magic Talent|AUTOMATIC|Life Sphere\tDESC:Positive channel energy and free Life sphere; consult class rules for channel uses and effects.",
                          "Soul Weaver Negative Channel\tCATEGORY:Soul Weaver Channel\tABILITY:Spheres Magic Talent|AUTOMATIC|Death Sphere\tDESC:Negative channel energy and free Death sphere; consult class rules for channel uses and effects."))
    if name == "Armiger":
        categories.append(f"ABILITYCATEGORY:Armiger Practitioner Ability\tCATEGORY:Armiger Practitioner Ability\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:min(1,{prefix}_LEVEL)\tPLURAL:Practitioner Ability\tDISPLAYLOCATION:Spheres")
        for stat, label in (("INT", "Intelligence"), ("WIS", "Wisdom"), ("CHA", "Charisma")):
            abilities.append(f"Armiger {label} Practitioner\tCATEGORY:Armiger Practitioner Ability\tBONUS:VAR|SPHERES_PRACTITIONER_MOD|{stat}")
    if name == "Hedgewitch":
        categories.append(f"ABILITYCATEGORY:Hedgewitch Path\tCATEGORY:Hedgewitch Path\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:2*min(1,{prefix}_LEVEL)\tPLURAL:Hedgewitch Paths\tDISPLAYLOCATION:Spheres")
        abilities.extend(option_abilities(name, "Hedgewitch Path", "List of Paths", source))
    if name == "Wraith":
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
            for sphere in (s.strip() for s in match.group(1).split(" or ")):
                if not (DATA / f"spheres_power_{sphere.lower()}.lst").is_file():
                    raise ValueError(f"Unknown haunt path sphere: {sphere}")
                key = f"Wraith {title}" + (f" - {sphere}" if " or " in match.group(1) else "")
                sphere_bonus = (f"\tABILITY:Spheres Magic Talent|AUTOMATIC|{sphere} Sphere\t"
                                f"BONUS:VAR|SPHERES_CL_{sphere.upper()}|{prefix}_LEVEL-SPHERES_CASTER_LEVEL")
                abilities.append(f"{key}\tCATEGORY:Wraith Haunt Path\tPREVARGTEQ:{prefix}_LEVEL,1{sphere_bonus}\tDESC:{body} Consult source for any unrepresented path skills and effects.")
    if name == "Striker":
        categories.append(f"ABILITYCATEGORY:Striker Bare Knuckles\tCATEGORY:Striker Bare Knuckles\tEDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:min(1,{prefix}_LEVEL)\tPLURAL:Bare Knuckles Sphere\tDISPLAYLOCATION:Spheres")
        for sphere in ("Boxing", "Brute", "Open Hand"):
            abilities.append(f"Striker {sphere} Knuckles\tCATEGORY:Striker Bare Knuckles\tABILITY:Spheres Combat Talent|AUTOMATIC|{sphere} Sphere\tDESC:Gain {sphere} sphere without spending a combat talent; if already possessed, choose a legal replacement sphere or talent manually.")
    if name == "Sentinel":
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