"""Commander option eligibility and self-only conditional skill modifiers."""


def option_tags(category, title):
    levels = {"Commander Enhanced Tactic": 2, "Commander Battlefield Specialist": 3,
              "Commander Logistic Specialty": 7}
    tags = [f"PREVARGTEQ:SPHERES_COMMANDER_LEVEL,{levels[category]}"]
    if category == "Commander Logistic Specialty":
        references = {
            "Call In A Specialist": {
                "SPECIALIST_ARRIVAL_HOURS": "max(1,24-SPHERES_COMMANDER_LEVEL)",
                "SPECIALIST_MAX_DAYS": "floor(SPHERES_COMMANDER_LEVEL/2)",
                "SPECIALIST_LEVEL": "SPHERES_COMMANDER_LEVEL-3",
            },
            "Field Feeding": {"FIELD_FEEDING_ADDITIONAL_CREATURES": "10*SPHERES_COMMANDER_LEVEL",
                              "FIELD_FEEDING_DC": "20"},
            "Call In the Cavalry": {"CAVALRY_MOUNTS": "SPHERES_COMMANDER_LEVEL",
                                    "CAVALRY_WEEKS": "1+floor((SPHERES_COMMANDER_LEVEL-7)/4)",
                                    "CAVALRY_MAX_HD": "5", "CAVALRY_SPEED": "60"},
        }
        for name, formula in references.get(title, {}).items():
            tags.append(f"DEFINE:SPHERES_COMMANDER_{name}|{formula}")
    if category == "Commander Enhanced Tactic" and title == "Expert Coordinator":
        tags.extend(["MULT:YES", "STACK:YES", "CHOOSE:NOCHOICE",
                     "BONUS:ABILITYPOOL|Commander Teamwork Feat|1"])
    if category == "Commander Battlefield Specialist":
        half = "floor(SPHERES_COMMANDER_LEVEL/2)"
        mental = "max(1,max(CHA,INT))"
        situations = {
            "Desert": [("Perception", "Notice natural hazards in desert terrain", mental, "")],
            "Jungle": [("Acrobatics", "In jungle terrain", half, "")],
            "Mountain (including hills)": [(skill, "In mountain terrain including hills", half, "")
                                           for skill in ("Climb", "Survival")],
            "Plains": [("Survival", "Scavenge food in plains terrain", mental, "Competence")],
            "Urban": [("Acrobatics", "Cross rooftops or traverse sewers in urban terrain", half, "Competence"),
                      ("Diplomacy", "Direct a crowd in urban terrain", half, "Competence")],
            "Underground": [("Survival", "In underground terrain", half, "Competence"),
                            ("Perception", "Notice natural hazards underground", half, "Competence")],
            "Water (above and below the surface)": [("Swim", "Fighting in aquatic terrain", half, "")],
        }
        for skill, situation, amount, bonus_type in situations.get(title, []):
            tags.append(f"BONUS:SITUATION|{skill}={situation}|{amount}"
                        + (f"|TYPE={bonus_type}" if bonus_type else ""))
    return tags