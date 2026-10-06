"""Build the Power/Might feat catalog from pinned OGC snapshots, without network access.

Only exact prerequisite grammar is compiled. Unsupported clauses require explicit
per-feat adjudication; they are never silently treated as satisfied.
"""
import argparse
import json
import re

from spheres_catalog import clean_name, inventory
from spheres_catalog_lst import category, key, text, token, PACKAGES
from spheres_catalog_source import ROOT, SNAPSHOTS, POWER, MIGHT, FEATS
from spheres_traditions import sections as tradition_sections, DEFERRED as DEFERRED_DRAWBACKS

DATA = ROOT / "data/spheres"
LEGACY = {"Extra Magic Talent", "Extra Spell Points", "Extra Arsenal Trick", "Extra Combat Talent"}
SPHERE_CHOICES = {"Sphere Focus", "Combat Sphere Focus", "Combat Sphere Specialization"}
TYPES = {t.lower(): t for t in (
    "Combat", "Teamwork", "Metamagic", "ItemCreation", "Admixture", "Anathema",
    "Aristeia", "Champion", "Chance", "Channeling", "Companion", "Counterspell",
    "Damnation", "Defiler", "Drawback", "DualSphere", "Necrosis", "Plague", "Protokinesis",
    "Proxy", "Purring", "Racial", "Ritual", "Squadron", "Surreal", "Theurge", "WildMagic")}
# General casting-tradition drawbacks with selectable records; see
# data/spheres/spheres_traditions.lst. Feat prerequisites cite these as
# "X drawback", "X (drawback)" or a bare "X".
DRAWBACKS = tuple(key for key in tradition_sections('General Drawbacks')
                 if key not in DEFERRED_DRAWBACKS)
SKILLS = {"acrobatics", "bluff", "climb", "craft (alchemy)", "craft (calligraphy)",
          "craft (tattoos)", "diplomacy", "fly", "handle animal", "heal", "intimidate",
          "knowledge (arcana)", "knowledge (dungeoneering)", "knowledge (history)",
          "knowledge (planes)", "knowledge (religion)", "perception", "perform (dance)",
          "profession (engineer)", "ride", "sense motive", "sleight of hand",
          "spellcraft", "stealth", "survival", "swim", "use magic device"}


def normalize(value):
    return " ".join(value.replace("’", "'").replace("–", "-").split()).casefold()


DRAWBACK_MAP = {normalize(n): n for n in DRAWBACKS}


def name(heading):
    value = clean_name(heading).rstrip("*").strip()
    # The source alternates between these two spellings in its prerequisites.
    match = re.fullmatch(r"(.+), (Improved|Greater|Superior)", value)
    return match[2] + " " + match[1] if match else value


def rules(value):
    return value.split("\n| Spheres of Power")[0].split("\n| Spheres of Might")[0].strip()


def inventory_feats():
    result = {}
    for slug in FEATS + POWER + MIGHT:
        source = json.loads((SNAPSHOTS / (slug + ".json")).read_text())
        active = slug in FEATS
        boundary = 0
        current = None
        for section in source["sections"]:
            heading, level = section["heading"], section["level"]
            # Current entries have TOC anchors. The wiki's Original tab does not;
            # importing it reintroduces renamed/retired feats as new choices.
            if level and not section["anchor"]:
                current = None
                continue
            if slug not in FEATS and level <= 2:
                active = "feat" in heading.lower() and not re.search(r"old|original", heading, re.I)
                boundary = level
                current = None
            if not active or not level or level == boundary:
                continue
            body = rules(section["text"])
            if not re.search(r"\bBenefits?:", body):
                if current and level > current["level"]:
                    current["text"] += "\n" + heading + ": " + body
                continue
            feat_name = name(heading)
            identity = normalize(feat_name)
            if identity in result:
                result[identity]["sources"].append(source["url"] + "#" + section["anchor"])
                # The reviewed Cataclysm entry supersedes the earlier drawback-only
                # duplicate, including its Defiler type and four-feat benefit.
                if slug == 'drawback-feats' and heading == 'Terrain Defiler (Defiler, Drawback) [Cata. HB]':
                    result[identity].update(heading=heading, text=body, types=['Defiler', 'Drawback'])
                    current = result[identity]
                continue
            types = []
            for group in re.findall(r"[([]([^])]+)[)\]]", heading):
                for part in group.split(","):
                    recognized = TYPES.get(re.sub(r"[ -]", "", part).lower())
                    if recognized:
                        types.append(recognized)
            current = {"name": feat_name, "heading": heading, "level": level,
                       "types": sorted(set(types)) or ["General"], "text": body,
                       "sources": [source["url"] + "#" + section["anchor"]]}
            result[identity] = current
    return sorted(result.values(), key=lambda r: normalize(r["name"]))


def split_clauses(value):
    """Commas inside sphere talent/package lists are not conjunction boundaries."""
    parts, start, depth = [], 0, 0
    for i, char in enumerate(value):
        depth += (char == "(") - (char == ")")
        if char in ",;" and depth == 0:
            parts.append(value[start:i].strip())
            start = i + 1
    parts.append(value[start:].strip())
    return [p for p in parts if p]


def core_feats():
    path = ROOT / "vendor/upstream/pcgen-6.08.00RC10/data/pathfinder/paizo/roleplaying_game/core_rulebook/cr_feats.lst"
    return {normalize(line.split("\t")[0]): line.split("\t")[0]
            for line in path.read_text().splitlines() if line and not line.startswith("#")}


def split_alternatives(value):
    """Split OR only outside balanced talent/package parentheses."""
    parts, start, depth = [], 0, 0
    for i, char in enumerate(value):
        depth += (char == "(") - (char == ")")
        if depth < 0:
            return None
        if depth == 0 and value[i:i + 4].lower() == " or ":
            parts.append(value[start:i].strip())
            start = i + 4
    if depth:
        return None
    parts.append(value[start:].strip())
    return parts if all(parts) else None


class Prerequisites:
    def __init__(self, feats):
        self.spheres = {normalize(r["sphere"]): r for r in inventory()}
        self.feats = core_feats()
        self.feats.update({normalize(r["name"]): r["key"] for r in feats})
        self.feats.update({normalize(n): "TYPE=SpheresFeat" + token(n) for n in SPHERE_CHOICES})

    def clause(self, value, caster_variable="SPHERES_CASTER_LEVEL"):
        value = value.strip().rstrip(".")
        # "(drawback)" punctuation is equivalent to the bare "drawback" suffix.
        value = re.sub(r"\s*\(drawback\)", " drawback", value, flags=re.I)
        value = re.sub(r"^(.+? sphere)\s+\(([a-z ]+)\) package$",
                       r"\1 (\2 package)", value, flags=re.I)
        simple = normalize(value)
        alignment = {
            "good alignment": "PREALIGN:LG,NG,CG",
            "evil alignment": "PREALIGN:LE,NE,CE",
            "non-good alignment": "!PREALIGN:LG,NG,CG",
            "nonlawful": "!PREALIGN:LG,LN,LE",
            "non-neutral alignment": "!PREALIGN:TN",
        }
        if simple in alignment:
            return [alignment[simple]]
        if simple.startswith("and "):
            return self.clause(value[4:], caster_variable)
        drawback_choices = re.fullmatch(r"at least one of the (.+) drawbacks", value, re.I)
        if drawback_choices:
            choices = re.split(r",\s*(?:or\s+)?|\s+or\s+", drawback_choices[1])
            names = [DRAWBACK_MAP.get(normalize(choice)) for choice in choices]
            if len(names) < 2 or not all(names) or len(set(names)) != len(names):
                return None
            return ["PREABILITY:1,CATEGORY=Custom Casting Drawback," +
                    ",".join("Tradition - " + name for name in names)]
        # "One of A, B, or C" enumerates single-clause alternatives.
        if simple.startswith("one of "):
            parts = [p for p in re.split(r",\s*(?:or\s+)?|\s+or\s+", value[7:].strip()) if p.strip()]
            alternatives = [self.clause(p, caster_variable) for p in parts]
            if len(alternatives) >= 2 and all(p and len(p) == 1 for p in alternatives):
                return ["PREMULT:1," + ",".join("[" + p[0] + "]" for p in alternatives)]
            return None
        # OR is valid only when every complete alternative can be represented.
        if simple == "1 or more metamagic feats":
            return ["PREFEAT:1,TYPE=Metamagic"]
        if simple == "ability to channel positive or negative energy":
            alternatives = [self.clause("ability to channel " + energy + " energy", caster_variable)
                            for energy in ("positive", "negative")]
            return ["PREMULT:1," + ",".join("[" + tags[0] + "]" for tags in alternatives)]
        skill_family = re.fullmatch(r"any craft or profession ([1-9]\d*) ranks?", simple)
        if skill_family:
            return ["PRESKILL:1,TYPE.Craft=" + skill_family[1] + ",TYPE.Profession=" + skill_family[1]]
        if simple == "studied target or studied combat class feature":
            studied = self.clause("studied combat class feature", caster_variable)[0]
            return ["PREMULT:1,[PREVARGTEQ:SlayerStudiedTargetBonus,1],[" + studied + "]"]
        if simple == "bardic performance or raging song class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=BardicPerformance,TYPE=SkaldRagingSong"]
        # This is one racial predicate, not two independently named OR clauses.
        racial_family = re.fullmatch(r"(construct|fey|plant) type or subtype", simple)
        if racial_family:
            name = racial_family[1].title()
            return [f"PRERACE:1,RACETYPE={name},RACESUBTYPE={name}"]
        racial_subtype = re.fullmatch(r"(construct|plant) subtype", simple)
        if racial_subtype:
            return [f"PRERACE:1,RACESUBTYPE={racial_subtype[1].title()}"]
        if simple == "outsider with the native subtype":
            return ["PRERACE:2,RACETYPE=Outsider,RACESUBTYPE=Native"]
        sphere_alternatives = re.fullmatch(r"([a-z ]+) or ([a-z ]+) sphere", simple)
        if sphere_alternatives:
            names = sphere_alternatives.groups()
            if all(name in self.spheres for name in names):
                alternatives = [self.clause(name + ' sphere', caster_variable) for name in names]
                return ['PREMULT:1,' + ','.join('[' + tags[0] + ']' for tags in alternatives)]
        branches = split_alternatives(value)
        if branches is None:
            return None
        if len(branches) > 1:
            alternatives = [self.clause(p, caster_variable) for p in branches]
            if all(p for p in alternatives):
                return ["PREMULT:1," + ",".join("[" + p[0] + "]" if len(p) == 1 else
                        "[PREMULT:" + str(len(p)) + "," + ",".join("[" + t + "]" for t in p) + "]"
                        for p in alternatives)]
            return None
        if simple in ("casting class feature", "spherecasting class feature"):
            return ["PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core"]
        if simple == "ability to acquire a familiar":
            return ["PREVARGTEQ:FamiliarMasterLVL,1"]
        if simple in ("bardic performance", "bardic performance class feature", "bardic performance class ability"):
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=BardicPerformance"]
        if simple in ("raging song", "raging song class feature"):
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=SkaldRagingSong"]
        if simple == "rage class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=Rage"]
        if simple == "ki pool class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=Ki Pool"]
        if simple == "favored enemy class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,Ranger ~ Favored Enemy,TYPE=FavoredEnemy"]
        if simple == "favored terrain class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=FavoredTerrain"]
        if simple == "improved evasion class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,Improved Evasion"]
        if simple == "psionics":
            return self.clause("psionics class feature", caster_variable)
        if simple == "tension pool":
            # Capacity is zero for the unlimited level-20 pool. Feature ownership,
            # not the current/capped resource quantity, determines eligibility.
            return ["PREMULT:1,[PRECLASS:1,Striker=1],[PREFEAT:1,Amateur Striker]"]
        if simple == "tension class feature":
            return ["PRECLASS:1,Striker=1"]
        if simple in ("inspiration class feature", "studied combat class feature"):
            path = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Font Of Inspiration"
            if simple == "studied combat class feature":
                return ["PREMULT:1,[PREVARGTEQ:InvestigatorStudiedCombatBonus,1],"
                        "[PREMULT:2,[" + path + "],[PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,5]]"]
            return ["PREMULT:1,[PREVARGTEQ:InvestigatorInspirationDice,1],[" + path + "]"]
        if simple == "no levels in a class that has the tension class feature":
            return ["!PRECLASS:1,Striker=1"]
        if simple in ("lay on hands", "lay on hands class feature", "touch of corruption", "touch of corruption class feature"):
            from spheres_covenant import channel_prerequisite
            positive = simple.startswith("lay on hands")
            # Upstream uses the same LayOnHands type for both polarities; exact
            # keys prevent an antipaladin from satisfying positive healing.
            feature_key = "Paladin ~ Lay on Hands" if positive else "Antipaladin ~ Touch of Corruption"
            return ["PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability," + feature_key + "],[" +
                    channel_prerequisite("Positive" if positive else "Negative") + "]"]
        channel_dice = re.fullmatch(r"channel energy ([1-9]\d*)d6", simple)
        if channel_dice:
            from spheres_channel import dice_prerequisite
            return [dice_prerequisite(int(channel_dice[1]))]
        if simple in ("channel energy", "channel energy class feature"):
            from spheres_covenant import channel_prerequisite
            return ["PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability,TYPE=ChannelEnergy,TYPE=Channel Energy],"
                    "[PREABILITY:1,CATEGORY=Soul Weaver Channel,Soul Weaver Positive Channel,Soul Weaver Negative Channel],[" +
                    channel_prerequisite() + "]"]
        channel = re.fullmatch(r"(?:ability to channel|channel) (positive|negative) energy(?: class feature)?", simple)
        if channel:
            from spheres_covenant import channel_prerequisite
            energy = channel[1].title()
            return ["PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability,TYPE=Channel " + energy + " Energy],"
                    "[PREABILITY:1,CATEGORY=Soul Weaver Channel,Soul Weaver " + energy + " Channel],[" +
                    channel_prerequisite(energy) + "]"]
        if simple == "combat training class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=SpheresCombatTraining"]
        if simple == "blessing/blight class feature":
            return ["PREABILITY:1,CATEGORY=Special Ability,Soul Weaver Blessing,Soul Weaver Blight"]
        class_features = {"wraith haunt class feature": "SpheresWraithHaunt",
                          "create reality class feature": "SpheresCreateReality",
                          "bestial trait class feature": "SpheresBestialTrait",
                          "secrets class feature": "SpheresHedgewitchSecrets",
                          "mystic combat class feature": "SpheresMysticCombat",
                          "emotion class feature": "SpheresEmotion"}
        if simple in class_features:
            return ["PREABILITY:1,CATEGORY=Special Ability,TYPE=" + class_features[simple]]
        resource_features = {"psionics class feature": "Symbiat Psionics Rounds (Reference)",
                             "bound equipment class feature": "Armorist Bound Items (Reference)",
                             "customized weapons class feature": "Armiger Talents Per Customized Weapon (Reference)",
                             "sentinel’s reserve class feature": "Sentinel Reserve Points (Reference)",
                             "sentinel's reserve class feature": "Sentinel Reserve Points (Reference)",
                             "shadowstuff class feature": "Fey Adept Shadow Points (Reference)",
                             "shadowmark class feature": "Fey Adept Shadowmark Dice (Reference)",
                             "forbidden lore class feature": "Thaumaturge Forbidden Lore (Reference)",
                             "bound nexus class feature": "Soul Weaver Bound Souls (Reference)",
                             "invocations class feature": "Thaumaturge Invocation Uses (Reference)"}
        if simple in resource_features:
            return ["PREABILITY:1,CATEGORY=Special Ability," + resource_features[simple]]
        shadowmark = re.fullmatch(r"shadowmark ([1-9]\d*)d6", simple)
        if shadowmark:
            return ["PREABILITY:1,CATEGORY=Special Ability,Fey Adept Shadowmark Dice (Reference)",
                    "PREVARGTEQ:SPHERES_FEY_ADEPT_SHADOWMARK_DICE," + shadowmark[1]]
        if simple in ("martial focus", "ability to gain martial focus", "ability to maintain martial focus"):
            return ["PREABILITY:1,CATEGORY=Special Ability,Spheres Martial Focus"]
        if simple in ("no casting class feature", "no spherecasting class feature"):
            return ["!PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core"]
        if simple in ("spell pool", "spell point pool"):
            return ["PREVARGTEQ:SPHERES_SPELL_POINTS,1"]
        if simple == "shadow pool":
            return ["PREMULT:1,[PREABILITY:1,CATEGORY=Special Ability,Fey Adept Shadow Points (Reference)],"
                    "[PREFEAT:1,TYPE=Surreal]"]
        if simple in ("any metamagic feat", "any item creation feat"):
            return ["PREFEAT:1,TYPE=" + ("Metamagic" if "metamagic" in simple else "ItemCreation")]
        feat_families = {"any one admixture feat": "Admixture",
                         "any admixture feat": "Admixture",
                         "at least one proxy feat": "Proxy",
                         "any one teamwork feat": "Teamwork",
                         "at least one metamagic feat": "Metamagic"}
        if simple in feat_families:
            return ["PREFEAT:1,TYPE=" + feat_families[simple]]
        descriptor_requirements = {
            "any talent with the strike descriptor": ("power", r"\[strike\]"),
            "one talent from any sphere that has the strike descriptor": ("power", r"\[strike\]"),
            "any (stance) talent": ("might", r"\(stance\)"),
        }
        if simple in descriptor_requirements:
            system, pattern = descriptor_requirements[simple]
            members = [key(row, talent) for row in self.spheres.values()
                       if row['system'] == system for talent in row['talents']
                       if re.search(pattern, talent['heading'], re.I)]
            if not members:
                return None
            ability_category = 'Spheres Magic Talent' if system == 'power' else 'Spheres Combat Talent'
            return ['PREABILITY:1,CATEGORY=' + ability_category + ',' + ','.join(members)]
        sphere_level = re.fullmatch(r"(.+?) sphere caster level ([1-9]\d*)(?:st|nd|rd|th)?", simple)
        if sphere_level:
            row = self.spheres.get(normalize(sphere_level[1]))
            if row is None or row["system"] != "power":
                return None
            return ["PREABILITY:1,CATEGORY=" + category(row) + "," + row["sphere"] + " Sphere",
                    "PREVARGTEQ:SPHERES_CL_" + token(row["sphere"]).upper() + "," + sphere_level[2]]
        match = re.fullmatch(r"monk (?:level )?([1-9]\d*)(?:st|nd|rd|th)?", simple)
        if match:
            return ["PRECLASS:1,Monk=" + match[1]]
        match = re.fullmatch(r"(commander|armiger|scholar|blacksmith|striker|technician) ([1-9]\d*)", simple)
        if match:
            return ["PRECLASS:1," + match[1].title() + "=" + match[2]]
        match = re.fullmatch(r"\+([1-9]\d*) base attack bonus", simple)
        if match:
            return ["PREATT:" + match[1]]
        match = re.fullmatch(r"([1-9]\d*)(?:st|nd|rd|th) level", simple)
        if match:
            return ["PRELEVEL:MIN=" + match[1]]
        for pattern, prefix in ((r"base attack bonus\s*\+?(\d+)", "PREATT:"),
                (r"(?:character )?level (\d+)(?:st|nd|rd|th)?", "PRELEVEL:MIN="),
                (r"caster level (\d+)(?:st|nd|rd|th)?", "PREVARGTEQ:" + caster_variable + ","),
                (r"(?:magic skill bonus|msb)\s*\+?(\d+)", "PREVARGTEQ:SPHERES_MAGIC_SKILL_BONUS,")):
            match = re.fullmatch(pattern, simple)
            if match:
                return [prefix + match[1]]
        match = re.fullmatch(r"(str|dex|con|int|wis|cha) (\d+)", simple)
        if match:
            return ["PRESTAT:1," + match[1].upper() + "=" + match[2]]
        match = re.fullmatch(r"([1-9]\d*) ranks? in any 1 skill", simple)
        if match:
            # Loaded Core/Spheres skills use Base. A name wildcard stops at the
            # first matching skill in this PCGen version, even if ranks fail.
            return ["PRESKILL:1,TYPE.Base=" + match[1]]
        match = re.fullmatch(r"([1-9]\d*) ranks? in any 2 skills", simple)
        if match:
            return ["PRESKILL:2,TYPE.Base=" + match[1] + ",CHECKMULT"]
        match = re.fullmatch(r"(.+? [1-9]\d* ranks?) and (.+? [1-9]\d* ranks?)", value, re.I)
        if match:
            parts = [self.clause(part, caster_variable) for part in match.groups()]
            if all(part and len(part) == 1 and part[0].startswith("PRESKILL:") for part in parts):
                return parts[0] + parts[1]
            return None
        match = re.fullmatch(r"(.*?) (\d+) ranks?", value, re.I)
        if match and match[1].lower() in SKILLS:
            return ["PRESKILL:1," + match[1].title() + "=" + match[2]]
        match = re.fullmatch(r"(.+?) ranks? ([1-9]\d*)", value, re.I)
        if match and match[1].lower() in SKILLS:
            return ["PRESKILL:1," + match[1].title() + "=" + match[2]]
        match = re.fullmatch(r"(\d+) ranks? in (?:the )?(.+?)(?: skill)?", value, re.I)
        if match and match[2].lower() in SKILLS:
            return ["PRESKILL:1," + match[2].title() + "=" + match[1]]
        match = re.fullmatch(r"(.+?) sphere(?:\s*\((.*)\))?", value, re.I)
        if match and normalize(match[1]) in self.spheres:
            if match[2] is not None and not match[2].strip():
                return None
            row = self.spheres[normalize(match[1])]
            tags = ["PREABILITY:1,CATEGORY=" + category(row) + "," + row["sphere"] + " Sphere"]
            talents = {normalize(t["name"]): key(row, t) for t in row["talents"]}
            if match[2]:
                # This reviewed phrase describes base Read Magic, not OR branches.
                if row['slug'] == 'divination' and match[2].lower() == 'one or more (sense) talents or abilities':
                    return tags
                items = split_clauses(match[2])
                alternatives = split_alternatives(match[2])
                enumeration = (len(items) > 1 and items[-1].lower().startswith("or ")
                               and all(split_alternatives(item) == [item] for item in items[:-1]))
                if enumeration:
                    alternatives = items[:-1] + [items[-1][3:].strip()]
                if alternatives and len(alternatives) > 1 and (len(items) == 1 or enumeration):
                    choices = []
                    for item in alternatives:
                        clean = normalize(clean_name(item))
                        if clean not in talents:
                            return None
                        choices.append("[PREABILITY:1,CATEGORY=" + category(row) + "," + talents[clean] + "]")
                    return tags + ["PREMULT:1," + ",".join(choices)]
                for item in items:
                    # Hallow is a base Fate word, not a separately purchased talent.
                    if row['slug'] == 'fate' and item.lower() == 'hallow (word)':
                        continue
                    # Enhance Equipment is granted by the base sphere; an ability
                    # requirement is distinct from buying an (enhance) talent.
                    if row['slug'] == 'enhancement' and item.lower() == 'any (enhance) ability':
                        continue
                    if row['slug'] == 'illusion' and item.lower() == 'illusionary touch (sensory, touch) x2':
                        tags.append('PREVARGTEQ:SPHERES_ILLUSION_ILLUSIONARYTOUCH_COUNT,2')
                        continue
                    if row['slug'] == 'enhancement' and item.lower() == 'at least one (enhance) talent':
                        members = [key(row, talent) for talent in row['talents']
                                   if '(enhance)' in talent['heading'].lower()]
                        if not members:
                            return None
                        tags.append('PREABILITY:1,CATEGORY=' + category(row) + ',' + ','.join(members))
                        continue
                    family = re.fullmatch(r"(?:any|at least one) \(?([a-z]+(?: [a-z]+)?)\)? talent", item, re.I)
                    reviewed_families = {('creation', 'material'), ('war', 'momentum'), ('war', 'rally'),
                                         ('berserker', 'adrenaline'), ('destruction', 'blast type'),
                                          ('nature', 'spirit'), ('mana', 'amp'), ('divination', 'sense')}
                    if family and (row['slug'], family[1].lower()) in reviewed_families:
                        descriptor = family[1].lower()
                        members = [key(row, talent) for talent in row['talents']
                                   if any(descriptor in [part.strip().lower() for part in group.split(',')]
                                          for group in re.findall(r'\(([^)]+)\)', talent['heading']))]
                        if not members:
                            return None
                        tags.append('PREABILITY:1,CATEGORY=' + category(row) + ',' + ','.join(members))
                        continue
                    package = re.fullmatch(r"\(?([a-z ]+)\)? package", item, re.I)
                    if package and package[1].lower() == 'any' and row['slug'] in PACKAGES:
                        tags.append('PREABILITY:1,CATEGORY=Spheres ' + row['sphere'] + ' Package,' +
                                    ','.join(row['sphere'] + ' Package - ' + choice for choice in PACKAGES[row['slug']]))
                        continue
                    if package and package[1].title() in PACKAGES.get(row["slug"], ()):
                        tags.append("PREABILITY:1,CATEGORY=Spheres " + row["sphere"] + " Package," + row["sphere"] + " Package - " + package[1].title())
                        continue
                    clean = normalize(clean_name(item))
                    if clean not in talents:
                        return None
                    tags.append("PREABILITY:1,CATEGORY=" + category(row) + "," + talents[clean])
            return tags
        if simple == "skill focus (heal)":
            # SERVESAS also activates upstream skill bonuses guarded by PREABILITY.
            # Expand selection prerequisites only; do not imitate the feat globally.
            return ["PREMULT:1,[PREFEAT:1,Skill Focus (Heal)],[PREFEAT:1,Surgeon’s Trade Secrets]"]
        if simple in self.feats:
            return ["PREFEAT:1," + self.feats[simple]]
        drawback = re.sub(r"\s*drawback$", "", simple)
        if drawback in DRAWBACK_MAP:
            return ["PREABILITY:1,CATEGORY=Custom Casting Drawback,Tradition - " + DRAWBACK_MAP[drawback]]
        return None

    # Requirements that are not sphere/feat-specific; when they follow the last
    # branch of an OR expression they are hoisted to apply to every branch (the
    # stricter reading; the adjudication record remains available otherwise).
    GLOBAL = re.compile(r"^(?:base attack bonus|(?:character |caster )?level\b|magic skill bonus|msb\b|"
                        r"\+\d+ base attack bonus|\d+(?:st|nd|rd|th) level\b|.* ranks? \d+$|"
                        r"(?:str|dex|con|int|wis|cha) \d|\d+ ranks?\b|.* \d+ ranks?$|"
                        r"(?:sphere)?casting class feature|combat training class feature|spell pool)", re.I)

    def compile(self, body):
        match = re.search(r"Prerequisites?:\s*(.*?)(?=\n|Benefits?:|$)", body, re.I)
        if not match:
            return [], []
        requirement = match[1].rstrip(".")
        # Shield commas inside "one of A, B, or C" enumerations from clause splitting.
        shielded = re.sub(r"one of ([^,;]+(?:, [^,;]+)*, or [^,;]+)",
                          lambda m: "one of " + m[1].replace(",", "\x00"), requirement, flags=re.I)
        clauses = [c.replace("\x00", ",") for c in split_clauses(shielded)]
        # Published CL prerequisites refer to the greatest prerequisite sphere CL.
        spheres = [r for n, r in self.spheres.items()
                   if re.search(r"\b" + re.escape(n) + r" sphere\b", normalize(requirement)) and r["system"] == "power"]
        variables = ["SPHERES_CL_" + token(r["sphere"]).upper() for r in spheres]
        caster = variables[0] if len(variables) == 1 else "max(" + ",".join(variables) + ")" if variables else "SPHERES_CASTER_LEVEL"
        if any(re.match(r"or\b", c, re.I) for c in clauses):
            # A bare Oxford-comma list is ambiguous with AND-branch syntax.
            # Require explicit "one of" or a semicolon separating branches.
            if ';' not in requirement and len(clauses) >= 3 and re.match(r'or\b', clauses[-1], re.I):
                return [], [requirement]
            return self.branches(clauses, requirement, caster)
        tags, unresolved = [], []
        for clause in clauses:
            parsed = self.clause(clause, caster)
            # Resolve only reviewed bare names with an explicit sphere clause.
            contextual_talents = {"drone": "Tech", "ammo spitter": "Tech",
                                  "plant mastery": "Nature"}
            sphere = contextual_talents.get(normalize(clause))
            if parsed is None and sphere and any(
                    re.fullmatch(re.escape(sphere) + r" sphere(?:\s*\(.*\))?", item, re.I)
                    and self.clause(item, caster) for item in clauses):
                parsed = self.clause(sphere + " sphere (" + clause + ")", caster)
            if parsed:
                tags.extend(parsed)
            else:
                unresolved.append(clause)
        return list(dict.fromkeys(tags)), unresolved

    def branches(self, clauses, original, caster):
        """OR of AND branches; fail closed unless every clause in every branch resolves."""
        branches = [[]]
        for clause in clauses:
            part = re.match(r"or\s+(.*)$", clause.strip(), re.I | re.S)
            if part:
                branches.append([part[1].strip()])
            else:
                branches[-1].append(clause)
        if not branches[0]:
            return [], [original]
        hoisted = []
        for branch in branches[1:]:
            while branch and self.GLOBAL.match(branch[-1].strip()):
                hoisted.append(branch.pop())
        if any(not branch for branch in branches):
            return [], [original]
        alternatives = []
        for branch in branches:
            tags = []
            for clause in branch:
                parsed = self.clause(clause, caster)
                if not parsed:
                    return [], [original]
                tags.extend(parsed)
            alternatives.append(tags)
        tags = ["PREMULT:1," + ",".join("[" + a[0] + "]" if len(a) == 1 else
                "[PREMULT:" + str(len(a)) + "," + ",".join("[" + t + "]" for t in a) + "]"
                for a in alternatives)]
        for clause in hoisted:
            parsed = self.clause(clause, caster)
            if not parsed:
                return [], [original]
            tags.extend(parsed)
        return list(dict.fromkeys(tags)), []


def build():
    from spheres_plague import prerequisites as plague_prerequisites
    feats = inventory_feats()
    core = core_feats()
    for row in feats:
        row["key"] = row["name"].replace(",", "") + (" (Spheres)" if normalize(row["name"]) in core and row["name"] not in LEGACY else "")
    parser = Prerequisites(feats)
    channel_requirements = {parser.clause(clause)[0] for clause in
                            ("channel energy", "channel positive energy", "channel negative energy")}
    from spheres_channel import dice_prerequisite
    channel_requirements.update(dice_prerequisite(int(dice)) for row in feats
                                for dice in re.findall(r"channel energy ([1-9]\d*)d6", row["text"], re.I))
    overrides = json.loads((DATA / "feat-mechanics.json").read_text())
    legacy_overrides = LEGACY.intersection(overrides)
    if legacy_overrides:
        raise ValueError("Legacy feat overrides are not emitted; update the owning LST instead: "
                         + ", ".join(sorted(legacy_overrides)))
    lines = ["# Generated by tools/spheres_feats.py; OGC: catalog-OGL.txt"]
    approvals = ["# Explicit adjudication for prerequisite clauses unsupported by this dataset."]
    for row in feats:
        prereqs, unresolved = parser.compile(row["text"])
        plague = plague_prerequisites(row["name"], row["text"])
        if plague is not None:
            prereqs, unresolved = plague, []
        override = overrides.get(row["name"], {})
        if "prerequisites" in override:
            prereqs, unresolved = override["prerequisites"], []
        from spheres_extra_options import rules as extra_option_rules
        extra_options = extra_option_rules(row['name'])
        if extra_options is not None:
            prereqs, unresolved = extra_options[0], []
        prereqs.extend(override.get("additional_prerequisites", []))
        unresolved.extend(override.get("additional_unresolved_prerequisites", []))
        if row['name'] == 'Greater Created':
            # Level 1 is not equivalent to character creation. Keep the timing
            # restriction explicitly reviewed until acquisition history exists.
            unresolved.append('Only selectable at character creation')
        # A feat cannot supply its own required pre-existing feat family.
        for family in ("Proxy", "Admixture"):
            predicate = "PREFEAT:1,TYPE=" + family
            if family in row["types"] and predicate in prereqs:
                candidates = [other["key"] for other in feats
                              if family in other["types"] and other["key"] != row["key"]]
                if not candidates:
                    raise ValueError("No other feats in required family: " + family)
                prereqs = ["PREFEAT:1," + ",".join(candidates) if tag == predicate else tag
                           for tag in prereqs]
        # Alternative-Brew substitutes only for feats requiring Alchemy,
        # never for unrelated crafting prerequisites or an optional OR branch.
        if 'PREABILITY:1,CATEGORY=Spheres Combat Talent,Alchemy Sphere' in prereqs:
            prereqs = [re.sub(r'PRESKILL:1,Craft \(Alchemy\)=(\d+)',
                             r'PREVARGTEQ:SPHERES_ALCHEMY_RANKS,\1', tag)
                       for tag in prereqs]
        row["prerequisites"] = prereqs
        if 'Surreal' in row['types']:
            others = [other['key'] for other in feats
                      if 'Surreal' in other['types'] and other['key'] != row['key']]
            prereqs = [tag.replace('PREFEAT:1,TYPE=Surreal', 'PREFEAT:1,' + ','.join(others))
                       for tag in prereqs]
            row['prerequisites'] = prereqs
        row["unresolved_prerequisites"] = unresolved
        row["mechanics"] = list(override.get("tags", []))
        if 'Necrosis' in row['types']:
            row['mechanics'].extend(['DEFINE:SPHERES_NECROSIS_FEAT_COUNT|0',
                                     'BONUS:VAR|SPHERES_NECROSIS_FEAT_COUNT|1'])
            if 'Defiler' not in row['types']:
                row['mechanics'].extend(['DEFINE:SPHERES_DEFILER_FEAT_COUNT|0',
                    'BONUS:VAR|SPHERES_DEFILER_FEAT_COUNT|1|PREFEAT:1,Inhuman Defiler'])
        if 'Defiler' in row['types']:
            row['mechanics'].extend(['DEFINE:SPHERES_DEFILER_FEAT_COUNT|0',
                                     'BONUS:VAR|SPHERES_DEFILER_FEAT_COUNT|1'])
            if 'Necrosis' not in row['types']:
                row['mechanics'].extend(['DEFINE:SPHERES_NECROSIS_FEAT_COUNT|0',
                    'BONUS:VAR|SPHERES_NECROSIS_FEAT_COUNT|1|PREFEAT:1,Inhuman Defiler'])
        if 'WildMagic' in row['types']:
            from spheres_wild_magic import feat_tags as wild_magic_tags
            row['mechanics'].extend(wild_magic_tags(row['name']))
        if 'Surreal' in row['types']:
            row['mechanics'].extend(['DEFINE:SPHERES_FEY_ADEPT_SHADOW_POINTS|0',
                                     'BONUS:VAR|SPHERES_FEY_ADEPT_SHADOW_POINTS|1',
                                     'DEFINE:SPHERES_SURREAL_FEAT_COUNT|0',
                                     'BONUS:VAR|SPHERES_SURREAL_FEAT_COUNT|1'])
        if extra_options is not None:
            row['mechanics'].extend(extra_options[1])
        if row['name'] == 'Amateur Striker':
            from spheres_amateur_striker import feat_tags
            row['mechanics'].extend(feat_tags())
        if row['name'] == 'Expanded Tension Technique':
            from spheres_amateur_striker import expanded_tags
            row['mechanics'].extend(expanded_tags())
        cost = re.search(r"\bCost: \+(\d+) spell points?\s*$", row["text"], re.M)
        if "Metamagic" in row["types"] and cost:
            row["mechanics"].append("DEFINE:SPHERES_METAMAGIC_" + token(row["name"]).upper() + "_COST|" + cost[1])
        if row["name"] in LEGACY:
            row["status"] = "existing"
            continue
        types = row["types"] + ["SpheresFeat"]
        if any(tag in channel_requirements for tag in prereqs):
            types.append("HedgewitchChannelFeat")
        # Only a mandatory top-level casting prerequisite certifies this family.
        # An OR branch mentioning casting does not require every applicant to cast.
        if "PREABILITY:1,CATEGORY=Special Ability,Spheres Casting Core" in prereqs:
            types.append("SpheresCasting")
        magic_spheres = {r["sphere"] + " Sphere" for r in parser.spheres.values() if r["system"] == "power"}
        if "SpheresCasting" in types or any(
                tag.startswith("PREABILITY:1,CATEGORY=Spheres Magic Talent,")
                and set(tag.split(",")[2:]) <= magic_spheres for tag in prereqs):
            types.append("HedgewitchMagicalSkill")
        # Incanter grants only feats explicitly referring to spheres/spell points,
        # plus metamagic, crafting, and drawback feats (not all magic-adjacent feats).
        requirement = re.search(r"Prerequisites?:\s*(.*?)(?=\n|Benefits?:|$)", row["text"], re.I)
        requirement = normalize(requirement[1]) if requirement else ""
        if ("casting class feature" in requirement or "spell pool" in requirement or
                any(normalize(r["sphere"]) + " sphere" in requirement for r in parser.spheres.values() if r["system"] == "power")):
            types.append("IncanterBonus")
        if any(t in types for t in ("Drawback", "Proxy", "Theurge")):
            types.append("IncanterBonus")
        tags = [row["key"], "CATEGORY:FEAT", "TYPE:" + ".".join(dict.fromkeys(types))] + prereqs
        if row["name"] in SPHERE_CHOICES:
            tags[2] += ".SpheresFeat" + token(row["name"])
            # Explicit per-sphere records avoid fragile string substitution in BONUS.
            # They share one source feat identity and cannot stack on the same sphere.
            for sphere in parser.spheres.values():
                if (sphere["system"] == "power") != (row["name"] == "Sphere Focus"):
                    continue
                ident = token(sphere["sphere"]).upper()
                variant = tags.copy()
                variant[0] += " - " + sphere["sphere"]
                variant = [t for t in variant if not t.startswith("PREABILITY:") or "Spheres Casting Core" in t]
                if row["name"] == "Combat Sphere Specialization":
                    variant.append("PREABILITY:1,CATEGORY=Spheres Combat Talent," + sphere["sphere"] + " Sphere")
                    variant.append("BONUS:VAR|SPHERES_BAB_" + ident + "|min(max(0,TL-BAB),1+floor((TL-1)/4))")
                else:
                    variant.append("BONUS:VAR|SPHERES_DC_" + ident + "|1")
                variant += ["DESC:" + text(row["text"]) + " Selected sphere: " + sphere["sphere"] + ".",
                            "SOURCEPAGE:" + row["sources"][0]]
                lines.append("\t".join(variant))
            row["status"] = "sphere-specific-records"
            continue
        if unresolved:
            approval = "Reviewed - " + row["key"]
            tags.append("PREABILITY:1,CATEGORY=Spheres Feat Adjudication," + approval)
            approvals.append("\t".join([approval, "CATEGORY:Spheres Feat Adjudication", "COST:0",
                "DESC:Manual prerequisite approval only; does not grant the feat or its effects. Verify: " + text("; ".join(unresolved))]))
        if not any(t.startswith("MULT:") for t in row["mechanics"]):
            if re.search(r"(?:take|select|gain|taken|selected) (?:this feat )?multiple times", row["text"], re.I):
                tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE"] if "effects stack" in row["text"].lower() and "do not stack" not in row["text"].lower() else ["MULT:YES", "STACK:NO", "CHOOSE:USERINPUT|1|TITLE=Distinct feat target (verify source restrictions)"]
            elif re.search(r"(?:take|select|gain) this feat (?:a second time|twice)", row["text"], re.I):
                counter = "SPHERES_FEAT_" + token(row["key"]).upper() + "_COUNT"
                tags += ["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE", "DEFINE:" + counter + "|0",
                         "BONUS:VAR|" + counter + "|1", "PREVARLT:" + counter + ",2"]
        tags += row["mechanics"]
        tags += ["DESC:" + text(row["text"]) + " Automated tags and remaining manual effects: docs/spheres-feats.md. Apply unautomated effects manually.", "SOURCEPAGE:" + row["sources"][0]]
        lines.append("\t".join(tags))
        row["status"] = "partial" if unresolved or not row["mechanics"] else "mechanics-added"
    for kind in ("Magic", "Combat"):
        lines.append("\t".join([
            "Blended Training - " + kind, "CATEGORY:Spheres Blended Talent Allocation",
            "PREFEAT:1,Extra Blended Training Talent", "MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
            "PREABILITY:2,CATEGORY=Special Ability,Spheres Casting Core,Spheres Martial Focus",
            "BONUS:ABILITYPOOL|Spheres " + kind + " Talent|1|PREFEAT:1,Extra Blended Training Talent"
            "|PREABILITY:2,CATEGORY=Special Ability,Spheres Casting Core,Spheres Martial Focus",
            "DESC:Allocate one Extra Blended Training Talent selection to the existing "
            + kind.lower() + " talent pool. Remove the purchased talent before refunding its allocation."]))
    from spheres_amateur_striker import records as amateur_records
    amateur_abilities, amateur_categories = amateur_records()
    from spheres_amateur_striker import expanded_records
    expanded_abilities, expanded_categories = expanded_records()
    amateur_abilities.extend(expanded_abilities)
    amateur_categories.extend(expanded_categories)
    lines.extend(amateur_abilities)
    return {"spheres_feat_catalog.lst": "\n".join(lines) + "\n",
            "spheres_feat_adjudication.lst": "\n".join(approvals) + "\n",
            "spheres_categories_feats.lst": "ABILITYCATEGORY:Spheres Feat Adjudication\tCATEGORY:Spheres Feat Adjudication\tEDITABLE:YES\tEDITPOOL:NO\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:YES\tPLURAL:Manual Feat Prerequisite Approvals\tDISPLAYLOCATION:Spheres\n"
                "ABILITYCATEGORY:Spheres Basic Magic Sphere\tCATEGORY:Spheres Magic Talent\tTYPE:SpheresBaseSphere\tEDITABLE:YES\tEDITPOOL:NO\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPLURAL:Basic Magic Training Sphere\tDISPLAYLOCATION:Spheres\n"
                "ABILITYCATEGORY:Spheres Blended Talent Allocation\tCATEGORY:Spheres Blended Talent Allocation\tEDITABLE:YES\tEDITPOOL:NO\tPOOL:0\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPLURAL:Blended Training Talent Allocations\tDISPLAYLOCATION:Spheres\n" + '\n'.join(amateur_categories) + '\n',
            "feat-catalog.json": json.dumps(feats, indent=2, ensure_ascii=False) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    outputs = build()
    for filename, content in outputs.items():
        path = DATA / filename
        if args.write:
            path.write_text(content, encoding="utf-8")
        elif not path.exists() or path.read_text() != content:
            raise SystemExit("Stale feat catalog: " + str(path))
    rows = json.loads(outputs["feat-catalog.json"])
    print(f'{len(rows)} source feats; {sum(bool(r["unresolved_prerequisites"]) for r in rows)} require prerequisite adjudication')


if __name__ == "__main__":
    main()