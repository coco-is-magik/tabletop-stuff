"""Wild-magic feat scaling, without activating optional casting effects."""

COUNT = "SPHERES_WILD_MAGIC_FEAT_COUNT"


def feat_tags(name):
    """Every wild-magic feat counts once; values describe available options."""
    values = {
        "Blood Dampening": {
            "BLOOD_DAMPENING_BURN": f"2-if({COUNT}>=6,1,0)",
            "BLOOD_DAMPENING_MAJOR_BURN": f"if({COUNT}>=4,4-if({COUNT}>=6,1,0),0)",
        },
        "Careful Caster": {"CAREFUL_CASTER_REDUCTION": f"min(50,25+5*({COUNT}-1))"},
        "Chaotic Counter": {"CHAOTIC_COUNTER_INCREASE": f"min(100,50+10*{COUNT})"},
        "Energy Shift": {"ENERGY_SHIFT_INCREASE": "50", "ENERGY_SHIFT_FORCE_INCREASE": "100"},
        "Heedless Metamagic": {"HEEDLESS_METAMAGIC_INCREASE_PER_FEAT": "50"},
        "Inspired Surge": {"INSPIRED_SURGE_TALENTS": f"1+floor({COUNT}/5)"},
        "Manipulate Result": {"MANIPULATE_RESULT_USES": COUNT},
        "Overpower Resistance": {"OVERPOWER_RESISTANCE_BONUS": f"2+floor({COUNT}/2)"},
        "Rhythmic Chaos": {"RHYTHMIC_CHAOS_INCREASE": f"min(60,20+10*{COUNT})"},
        "Risk Management": {
            "RISK_MANAGEMENT_ROLLS": f"if({COUNT}>=4,1,2)",
            "RISK_MANAGEMENT_MAJOR_ROLLS": f"if({COUNT}>=6,4,0)",
        },
        "Shift Cost": {"SHIFT_COST_REDUCTION": "if(TL>=10,2,1)",
                       "SHIFT_COST_INCREASE": "if(TL>=10,100,50)"},
        "Shift Effect": {"SHIFT_EFFECT_MAJOR_ALLOWED": f"if({COUNT}>=6,1,0)"},
        "Spectacular Surge": {"SPECTACULAR_SURGE_EVENTS": f"if({COUNT}>=4,2,1)"},
        "War on Reality": {"WAR_ON_REALITY_STRAIN_REDUCTION": "1"},
    }
    tags = [f"DEFINE:{COUNT}|0", f"BONUS:VAR|{COUNT}|1"]
    for suffix, formula in values.get(name, {}).items():
        # These derived values must not feed back into the bonus evaluator.
        tags.append(f"DEFINE:SPHERES_{suffix}|{formula}")
    if name == "Chaotic Counter":
        tags.append("BONUS:VAR|SPHERES_COUNTERSPELL_CHECK_BONUS|1")
    return tags