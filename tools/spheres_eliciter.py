"""Eliciter emotion progression; legacy emotion keys remain the minor powers."""
import re


def emotion_records(options):
    records = []
    for title, text in options:
        name = re.sub(r"\s*\[[^]]+\]", "", title).strip()
        parts = re.split(r"(?m)^(Minor|Lesser|Greater|Master):", text)
        if parts[1::2] != ['Minor', 'Lesser', 'Greater', 'Master']:
            raise ValueError('Unreviewed emotion tier structure: ' + title)
        previous = None
        for index, (tier, level) in enumerate((('Minor', 2), ('Lesser', 5), ('Greater', 8), ('Master', 11))):
            key = 'Eliciter ' + name + ('' if tier == 'Minor' else ' - ' + tier)
            tags = [key, 'CATEGORY:Eliciter Emotion', f'PREVARGTEQ:SPHERES_ELICITER_LEVEL,{level}']
            if previous:
                tags.append('PREABILITY:1,CATEGORY=Eliciter Emotion,' + previous)
            body = re.sub(r'\s+', ' ', parts[2 + index * 2]).strip()
            if not body:
                raise ValueError('Empty emotion tier: ' + key)
            if index == 0 and parts[0].strip():
                body = re.sub(r'\s+', ' ', parts[0]).strip() + ' ' + body
            body = body.replace('|', '/').replace('%', 'percent').replace('(', '[').replace(')', ']')
            tags.append('DESC:' + tier + ': ' + body)
            records.append('\t'.join(tags))
            previous = key
    return records