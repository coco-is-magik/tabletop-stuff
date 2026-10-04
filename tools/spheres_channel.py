"""Channel dice prerequisites for independently modeled Core and Spheres pools."""


def dice_prerequisite(dice):
    if not isinstance(dice, int) or isinstance(dice, bool) or dice < 1:
        raise ValueError("Expected a positive channel dice threshold")
    alternatives = []
    # Each branch owns both its feature and its dice. Independent pools must
    # never combine, and a different die size does not satisfy an Nd6 rule.
    for key, prefix in (("Cleric ~ Channel Positive Energy", "ClericChannelPositiveEnergy"),
                        ("Cleric ~ Channel Negative Energy", "ClericChannelNegativeEnergy"),
                        ("Paladin ~ Channel Positive Energy", "PaladinChannel")):
        alternatives.append("[PREMULT:3,[PREABILITY:1,CATEGORY=Special Ability," + key + "],"
                            f"[PREVARGTEQ:{prefix}Dice,{dice}],[PREVAREQ:{prefix}DieSize,6]]")
    alternatives.append("[PREMULT:2,[PREABILITY:1,CATEGORY=Special Ability,"
                        "Incanter Positive Channel,Incanter Negative Channel],"
                        f"[PREVARGTEQ:SPHERES_CHANNEL_DICE,{dice}]]")
    alternatives.append("[PREMULT:2,[PREABILITY:1,CATEGORY=Soul Weaver Channel,"
                        "Soul Weaver Positive Channel,Soul Weaver Negative Channel],"
                        f"[PREVARGTEQ:SPHERES_SOUL_WEAVER_CHANNEL_DICE,{dice}]]")
    return "PREMULT:1," + ",".join(alternatives)