"""Fixed-level bound nexus grants; these are not selectable class options."""
import re

NEXUS_LEVELS = {
    "Aid the Dead": 1, "Lovelorn Soul": 1, "Siphon Health": 1,
    "Curious Spirit": 4, "Summon Spirit I": 4,
    "Channel Mastery": 8, "Summon Spirit II": 8, "Divine Soul": 8, "Blessed Soul": 8,
    "Summon Spirit III": 12, "Ghostpoint": 12,
    "Summon Spirit IV": 16, "Temporary Resurrection": 16, "Trap Soul": 16,
    "Summon Spirit V": 20,
}


def nexus_records(options):
    if len(options) != len(NEXUS_LEVELS) or {title for title, _ in options} != set(NEXUS_LEVELS):
        raise ValueError("Bound nexus inventory changed; review automatic grants")
    records = []
    for title, body in options:
        level = NEXUS_LEVELS[title]
        stated = re.match(r"At (\d+)(?:st|nd|rd|th) level,", body)
        if (level > 1 and (not stated or int(stated[1]) != level)) or (level == 1 and stated):
            raise ValueError("Bound nexus level changed: " + title)
        description = " ".join(body.split()).replace("|", "/")
        records.append(f"Soul Weaver {title}\tCATEGORY:Soul Weaver Nexus Powers\t"
                       f"PREVARGTEQ:SPHERES_SOUL_WEAVER_LEVEL,{level}\tDESC:{description}")
    return records


def blessing_records(positive, negative):
    """Grant the appropriate fixed blessing/blight progression from channel choice."""
    records = []
    grants = {}
    for polarity, options, expected in (
            ('Positive', positive, ('Blessing', 'Heal', 'Restore', 'Revive', 'Renew')),
            ('Negative', negative, ('Blight', 'Lesion', 'Mind Blight', 'Consume', 'Detonate'))):
        if tuple(title for title, _ in options) != expected:
            raise ValueError('Blessing/blight inventory changed: ' + polarity)
        grants[polarity] = []
        for (title, body), level in zip(options, (2, 6, 10, 14, 18)):
            if not re.match(r'At ' + str(level) + r'(?:nd|th) level,', body):
                raise ValueError('Blessing/blight level changed: ' + title)
            key = 'Soul Weaver ' + title
            description = ' '.join(body.split()).replace('|', '/')
            records.append(f'{key}\tCATEGORY:Special Ability\tTYPE:SpheresClassFeature\t'
                           f'PREVARGTEQ:SPHERES_SOUL_WEAVER_LEVEL,{level}\tDESC:{description}')
            grants[polarity].append(f'ABILITY:Special Ability|AUTOMATIC|{key}|'
                                    f'PREVARGTEQ:SPHERES_SOUL_WEAVER_LEVEL,{level}')
    return records, grants