"""Covenant energy choice and independent touch/channel resource references."""

PATH = "PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Covenant"
CATEGORY = "Hedgewitch Covenant Energy"
PREFIX = "SPHERES_HEDGEWITCH_COVENANT_"


def channel_prerequisite(energy=None):
    if energy not in (None, "Positive", "Negative"):
        raise ValueError("Unknown Covenant energy")
    choices = [energy] if energy else ["Positive", "Negative"]
    return ("PREMULT:2,[" + PATH + "],[PREABILITY:1,CATEGORY=" + CATEGORY + "," +
            ",".join("Hedgewitch Covenant " + choice for choice in choices) + "]")


def records():
    category = (f"ABILITYCATEGORY:{CATEGORY}\tCATEGORY:{CATEGORY}\tEDITABLE:YES\tEDITPOOL:NO\t"
                "FRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Spheres")
    abilities = []
    for energy, alignments in (("Positive", "LG,NG,CG,LN,TN,CN"),
                                ("Negative", "LE,NE,CE,LN,TN,CN")):
        abilities.append(f"Hedgewitch Covenant {energy}\tCATEGORY:{CATEGORY}\t{PATH}\t"
                         f"PREALIGN:{alignments}\tDESC:Covenant {energy.lower()} energy. "
                         "Touch spends one use; channel spends two uses from the same pool. "
                         "This selection does not grant an independent cleric channel pool.")
    abilities.append("Hedgewitch Covenant Extra Healing\tCATEGORY:Hedgewitch Secret\t"
                     "PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,1\t"
                     "PREMULT:1,[PREVARGTEQ:SPHERES_HEDGEWITCH_LEVEL,2],"
                     "[PREABILITY:1,CATEGORY=Hedgewitch Path,Hedgewitch Academia]\t" + PATH +
                     "\tMULT:YES\tSTACK:YES\tCHOOSE:NOCHOICE\t"
                     f"BONUS:VAR|{PREFIX}USES|4|{PATH}\t"
                     "DESC:Four additional daily covenant touch uses; two uses pay for one channel. Repeatable.")
    from spheres_hedgewitch import secret_tags
    abilities.append("Hedgewitch Covenant Channel Feats\tCATEGORY:Hedgewitch Secret\t" +
                     "\t".join(secret_tags("Channel Feats", False) + [PATH, "MULT:YES", "STACK:YES",
                     "CHOOSE:NOCHOICE", "BONUS:ABILITYPOOL|Hedgewitch Channel Feat|1|" + PATH]) +
                     "\tDESC:Choose a feat requiring channel energy; meet its prerequisites. Repeatable.")
    abilities.append("Hedgewitch Covenant Smite\tCATEGORY:Hedgewitch Secret\t" +
                     "\t".join(secret_tags("Smite", True) + [PATH, "MULT:YES", "STACK:YES",
                     "CHOOSE:NOCHOICE", f"BONUS:VAR|{PREFIX}SMITE_USES|1|" + PATH]) +
                     "\tDESC:Once per day per selection, smite the alignment detected by your Covenant "
                     "path benefit, as a paladin's smite evil. Target, activation and expenditure are "
                     "player tracked; this is not a permanent attack, damage or AC bonus.")
    return category, abilities


def feat_category():
    return ("ABILITYCATEGORY:Hedgewitch Channel Feat\tCATEGORY:FEAT\tTYPE:HedgewitchChannelFeat\t"
            "EDITABLE:YES\tEDITPOOL:NO\tFRACTIONALPOOL:NO\tVISIBLE:QUALIFY\tPOOL:0\tDISPLAYLOCATION:Feats")


def path_tags():
    return [f"BONUS:ABILITYPOOL|{CATEGORY}|1",
            f"BONUS:VAR|{PREFIX}USES|3+floor(SPHERES_HEDGEWITCH_LEVEL/2)",
            f"BONUS:VAR|{PREFIX}DICE|max(1,floor(SPHERES_HEDGEWITCH_LEVEL/2))",
            f"BONUS:VAR|{PREFIX}DIE_SIZE|if(SPHERES_HEDGEWITCH_LEVEL>=20,8,6)",
            f"BONUS:VAR|{PREFIX}DC|10+floor(SPHERES_HEDGEWITCH_LEVEL/2)+SPHERES_CASTING_ABILITY"]


def definitions():
    return [f"DEFINE:{PREFIX}{quantity}|0" for quantity in ("USES", "DICE", "DIE_SIZE", "DC", "SMITE_USES")]