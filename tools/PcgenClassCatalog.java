package pcgen.gui2.facade;

/** Load/export/save a base class without the Incanter-only talent assumptions. */
class PcgenClassCatalog {
    public static void main(String[] args) {
        if (args.length < 7 || args.length > 8) {
            throw new IllegalArgumentException("character template output config required-spheres required-choice expected-pools [saved character]");
        }
        boolean exported = pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]);
        if (exported) {
            var characters = pcgen.core.Globals.getPCList();
            if (characters.size() != 1) {
                throw new IllegalStateException("Expected one character");
            }
            var pc = characters.get(0);
            var game = pcgen.core.SettingsHandler.getGameAsProperty().get();
            if (pc.getClassKeyed("Wraith") != null) {
                int level = pc.getVariableValue("SPHERES_WRAITH_LEVEL", "").intValue();
                int casting = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
                String[] names = {"FORM_ROUNDS", "FORM_UNLIMITED", "HAUNT_DC", "POSSESSION_DC", "POSSESSION_TARGETS"};
                int[] expected = {level >= 20 ? 0 : level + casting, level >= 20 ? 1 : 0,
                    10 + level / 2 + casting, level < 2 ? 0 : 10 + level / 2 + casting,
                    level < 2 ? 0 : level < 10 ? 1 : Math.max(2, casting)};
                for (int i = 0; i < names.length; i++) {
                    if (pc.getVariableValue("SPHERES_WRAITH_" + names[i], "").intValue() != expected[i]) {
                        throw new IllegalStateException("Wraith reference progression: " + names[i]);
                    }
                }
            }
            if (pc.getClassKeyed("Commander") != null) {
                int level = pc.getVariableValue("SPHERES_COMMANDER_LEVEL", "").intValue();
                var extraTerrain = pcgen.core.Globals.getContext().getReferenceContext()
                    .getManufacturerId(pcgen.core.AbilityCategory.FEAT).getActiveObject("Extra Battlefield Specialization");
                var extraArt = pcgen.core.Globals.getContext().getReferenceContext()
                    .getManufacturerId(pcgen.core.AbilityCategory.FEAT).getActiveObject("Extra Striker Art");
                if (extraTerrain.qualifies(pc, extraTerrain) != (level >= 5)
                    || extraArt.qualifies(pc, extraArt)) {
                    throw new IllegalStateException("Practitioner feat requires named class levels, not character level");
                }
                int focusUses = level < 5 ? 0 : 1 + (level - 5) / 6;
                int activeTactics = level < 2 ? 0 : level < 10 ? 1 : level < 20 ? 2 : 3;
                if (pc.getVariableValue("SPHERES_COMMANDER_GROUP_FOCUS_USES", "").intValue() != focusUses
                    || pc.getVariableValue("SPHERES_COMMANDER_ACTIVE_ENHANCED_TACTICS", "").intValue() != activeTactics) {
                    throw new IllegalStateException("Commander resource progression");
                }
                for (String[] option : new String[][] {
                        {"Enhanced Tactic", "Expert Coordinator", "2"},
                        {"Battlefield Specialist", "Cold", "3"},
                        {"Logistic Specialty", "Field Feeding", "7"}}) {
                    var category = game.getAbilityCategory("Commander " + option[0]);
                    var ability = pcgen.core.Globals.getContext().getReferenceContext()
                        .getManufacturerId(category).getActiveObject("Commander " + option[1]);
                    if (ability == null || ability.qualifies(pc, ability) != (level >= Integer.parseInt(option[2]))) {
                        throw new IllegalStateException("Commander option level gate: " + option[0]);
                    }
                }
                if (level >= 6) {
                    var category = game.getAbilityCategory("Commander Enhanced Tactic");
                    var teamwork = game.getAbilityCategory("Commander Teamwork Feat");
                    var expert = pcgen.core.Globals.getContext().getReferenceContext()
                        .getManufacturerId(category).getActiveObject("Commander Expert Coordinator");
                    var character = pcgen.system.CharacterManager.getCharacters().iterator().next();
                    var controller = new pcgen.gui2.facade.CharacterAbilities(pc,
                        new pcgen.system.ConsoleUIDelegate(), character.getDataSet(), new pcgen.gui2.facade.TodoManager());
                    var featPool = pc.getAvailableAbilityPool(pcgen.core.AbilityCategory.FEAT);
                    try {
                        if (args.length == 7) {
                            if (pc.getAvailableAbilityPool(teamwork).intValue() != 2
                                || !pc.hasAbilityKeyed(category, expert.getKeyName())) {
                                throw new IllegalStateException("Expert Coordinator retained grants");
                            }
                            controller.removeAbility(category, expert);
                            controller.removeAbility(category, expert);
                        }
                        var initial = pc.getAvailableAbilityPool(category);
                        if (level >= 7) {
                            var logistics = game.getAbilityCategory("Commander Logistic Specialty");
                            var logisticsPool = pc.getAvailableAbilityPool(logistics);
                            var cavalry = pcgen.core.Globals.getContext().getReferenceContext()
                                .getManufacturerId(logistics).getActiveObject("Commander Call In the Cavalry");
                            if (args.length == 7) {
                                if (!pc.hasAbilityKeyed(logistics, cavalry.getKeyName())
                                    || pc.getVariableValue("SPHERES_COMMANDER_CAVALRY_MOUNTS", "").intValue() != level) {
                                    throw new IllegalStateException("Cavalry retained selection and capacity");
                                }
                                controller.removeAbility(logistics, cavalry);
                                logisticsPool = pc.getAvailableAbilityPool(logistics);
                            }
                            for (String name : new String[] {"Call In A Specialist", "Field Feeding", "Call In the Cavalry"}) {
                                var selection = pcgen.core.Globals.getContext().getReferenceContext()
                                    .getManufacturerId(logistics).getActiveObject("Commander " + name);
                                controller.addAbility(logistics, selection);
                                if (!pc.hasAbilityKeyed(logistics, selection.getKeyName())) {
                                    throw new IllegalStateException("Logistic selection failed: " + name);
                                }
                                String[][] values = name.equals("Field Feeding")
                                    ? new String[][] {{"FIELD_FEEDING_ADDITIONAL_CREATURES", "" + 10 * level},
                                                      {"FIELD_FEEDING_DC", "20"}}
                                    : name.equals("Call In the Cavalry")
                                    ? new String[][] {{"CAVALRY_MOUNTS", "" + level},
                                                      {"CAVALRY_WEEKS", "" + (1 + (level - 7) / 4)},
                                                      {"CAVALRY_MAX_HD", "5"}, {"CAVALRY_SPEED", "60"}}
                                    : new String[][] {{"SPECIALIST_LEVEL", "" + (level - 3)},
                                                      {"SPECIALIST_MAX_DAYS", "" + level / 2},
                                                      {"SPECIALIST_ARRIVAL_HOURS", "" + Math.max(1, 24 - level)}};
                                for (var value : values) {
                                    if (pc.getVariableValue("SPHERES_COMMANDER_" + value[0], "").intValue()
                                        != Integer.parseInt(value[1])) {
                                        throw new IllegalStateException("Logistics reference: " + value[0]);
                                    }
                                }
                                if (name.equals("Call In A Specialist")) {
                                    var friends = pcgen.core.Globals.getContext().getReferenceContext()
                                        .getManufacturerId(pcgen.core.AbilityCategory.FEAT).getActiveObject("Friends In Close Places");
                                    if (friends.qualifies(pc, friends)) {
                                        throw new IllegalStateException("Friends requires Leadership followers");
                                    }
                                    var followers = new pcgen.core.PCTemplate();
                                    followers.setName("Commander followers regression");
                                    var context = pcgen.core.Globals.getContext();
                                    if (!context.processToken(followers, "ABILITY", "Spheres Combat Talent|AUTOMATIC|Leadership Sphere")
                                        || !context.processToken(followers, "ABILITY", "Spheres Leadership Package|AUTOMATIC|Leadership Package - Followers")) {
                                        throw new IllegalStateException("Followers fixture parsing");
                                    }
                                    context.commit();
                                    pc.addTemplate(followers);
                                    try {
                                        if (!friends.qualifies(pc, friends)) {
                                            throw new IllegalStateException("Friends prerequisites satisfied");
                                        }
                                        double diplomacy = pc.getTotalBonusTo("SKILL", "Diplomacy");
                                        controller.addAbility(pcgen.core.AbilityCategory.FEAT, friends);
                                        if (!pc.hasAbilityKeyed(pcgen.core.AbilityCategory.FEAT, friends.getKeyName())
                                            || pc.getVariableValue("SPHERES_COMMANDER_FOLLOWER_SPECIALIST_HOURS", "") != Math.max(1, 24 - level) / 2.0
                                            || pc.getTotalBonusTo("SKILL", "Diplomacy") != diplomacy
                                            || pc.getVariableValue("SPHERES_COMMANDER_FOLLOWER_CHECK_BONUS", "").intValue() != 2) {
                                            throw new IllegalStateException("Friends conditional references must preserve fractional hours and personal skills");
                                        }
                                        controller.removeAbility(logistics, selection);
                                        if (friends.qualifies(pc, friends)) {
                                            throw new IllegalStateException("Friends lost specialist prerequisite");
                                        }
                                        controller.addAbility(logistics, selection);
                                        controller.removeAbility(pcgen.core.AbilityCategory.FEAT, friends);
                                        if (level >= 10) {
                                            var ranks = new pcgen.core.PCTemplate();
                                            ranks.setName("Commander Diplomacy threshold regression");
                                            if (!context.processToken(ranks, "BONUS", "SKILLRANK|Diplomacy|5")) {
                                                throw new IllegalStateException("Diplomacy rank fixture parsing");
                                            }
                                            context.commit();
                                            pc.addTemplate(ranks);
                                            try {
                                                controller.addAbility(pcgen.core.AbilityCategory.FEAT, friends);
                                                if (pc.getVariableValue("SPHERES_COMMANDER_FOLLOWER_CHECK_BONUS", "").intValue() != 4) {
                                                    throw new IllegalStateException("Ten Diplomacy ranks improve follower checks");
                                                }
                                                controller.removeAbility(pcgen.core.AbilityCategory.FEAT, friends);
                                            } finally {
                                                pc.removeTemplate(ranks);
                                            }
                                        }
                                    } finally {
                                        pc.removeTemplate(followers);
                                    }
                                    if (!pc.getAvailableAbilityPool(pcgen.core.AbilityCategory.FEAT).equals(featPool)) {
                                        throw new IllegalStateException("Friends feat refund");
                                    }
                                }
                                controller.removeAbility(logistics, selection);
                                for (var value : values) {
                                    if (pc.hasVariable("SPHERES_COMMANDER_" + value[0])) {
                                        throw new IllegalStateException("Removed logistics must not retain capacity: " + value[0]);
                                    }
                                }
                                if (!pc.getAvailableAbilityPool(logistics).equals(logisticsPool)) {
                                    throw new IllegalStateException("Logistic specialty refund");
                                }
                            }
                            controller.addAbility(logistics, cavalry);
                        }
                        var terrainCategory = game.getAbilityCategory("Commander Battlefield Specialist");
                        var plains = pcgen.core.Globals.getContext().getReferenceContext()
                            .getManufacturerId(terrainCategory).getActiveObject("Commander Plains");
                        var terrainPool = pc.getAvailableAbilityPool(terrainCategory);
                        double survival = pc.getTotalBonusTo("SKILL", "Survival");
                        controller.addAbility(terrainCategory, plains);
                        if (pc.getTotalBonusTo("SITUATION", "Survival=Scavenge food in plains terrain") != 1
                            || pc.getTotalBonusTo("SKILL", "Survival") != survival) {
                            throw new IllegalStateException("Plains bonus must be situational with minimum one");
                        }
                        controller.removeAbility(terrainCategory, plains);
                        if (pc.getTotalBonusTo("SITUATION", "Survival=Scavenge food in plains terrain") != 0
                            || !pc.getAvailableAbilityPool(terrainCategory).equals(terrainPool)) {
                            throw new IllegalStateException("Plains bonus and pool refund");
                        }
                        for (int count = 1; count <= 2; count++) {
                            controller.addAbility(category, expert);
                            if (pc.getAvailableAbilityPool(teamwork).intValue() != count) {
                                throw new IllegalStateException("Expert Coordinator repeated teamwork grant");
                            }
                        }
                        var twilight = pcgen.core.Globals.getContext().getReferenceContext()
                            .getManufacturerId(pcgen.core.AbilityCategory.FEAT).getActiveObject("Twilight Adept");
                        if (twilight.qualifies(pc, twilight)) {
                            throw new IllegalStateException("Teamwork feat must enforce its sphere prerequisite");
                        }
                        var light = new pcgen.core.PCTemplate();
                        light.setName("Commander teamwork prerequisite regression");
                        if (!pcgen.core.Globals.getContext().processToken(light, "ABILITY",
                                "Spheres Magic Talent|AUTOMATIC|Light Sphere")) {
                            throw new IllegalStateException("Teamwork prerequisite fixture failed");
                        }
                        pcgen.core.Globals.getContext().commit();
                        pc.addTemplate(light);
                        pc.calcActiveBonuses();
                        try {
                            if (!twilight.qualifies(pc, twilight)) {
                                throw new IllegalStateException("Teamwork prerequisite fixture did not qualify");
                            }
                            controller.addAbility(teamwork, twilight);
                            if (!pc.hasAbilityKeyed(pcgen.core.AbilityCategory.FEAT, twilight.getKeyName())
                                || pc.getAvailableAbilityPool(teamwork).intValue() != 1
                                || !pc.getAvailableAbilityPool(pcgen.core.AbilityCategory.FEAT).equals(featPool)) {
                                throw new IllegalStateException("Teamwork selection must spend only the dedicated slot");
                            }
                            controller.removeAbility(category, expert);
                            controller.removeAbility(category, expert);
                            if (pc.getAvailableAbilityPool(teamwork).intValue() != -1) {
                                throw new IllegalStateException("Spent teamwork grant removal must expose overspending");
                            }
                            controller.removeAbility(teamwork, twilight);
                            if (pc.getAvailableAbilityPool(teamwork).intValue() != 0) {
                                throw new IllegalStateException("Teamwork cleanup must refund overspending");
                            }
                            controller.addAbility(category, expert);
                            controller.addAbility(category, expert);
                        } finally {
                            pc.removeTemplate(light);
                            pc.calcActiveBonuses();
                        }
                        if (twilight.qualifies(pc, twilight)) {
                            throw new IllegalStateException("Removed sphere must revoke teamwork qualification");
                        }
                        for (int count = 1; count >= 0; count--) {
                            controller.removeAbility(category, expert);
                            if (pc.getAvailableAbilityPool(teamwork).intValue() != count) {
                                throw new IllegalStateException("Expert Coordinator partial refund");
                            }
                        }
                        if (!pc.getAvailableAbilityPool(category).equals(initial)
                            || !pc.getAvailableAbilityPool(pcgen.core.AbilityCategory.FEAT).equals(featPool)) {
                            throw new IllegalStateException("Expert Coordinator must not consume normal feats");
                        }
                        controller.addAbility(category, expert);
                        controller.addAbility(category, expert);
                    } finally {
                        controller.closeCharacter();
                    }
                }
            }
            if (pc.getClassKeyed("Fey Adept") != null) {
                int level = pc.getVariableValue("SPHERES_FEY_ADEPT_LEVEL", "").intValue();
                boolean capstone = level == 20;
                var visionType = pcgen.util.enumeration.VisionType.getVisionType("Darkvision");
                int baseVision = level >= 2 ? 60 : 0;
                for (int external : new int[] {0, 20, 30, 60, 120}) {
                    var template = new pcgen.core.PCTemplate();
                    template.setName("Fey vision regression " + external);
                    if (!pcgen.core.Globals.getContext().processToken(template, "VISION", "Darkvision (" + external + "')")) {
                        throw new IllegalStateException("Vision fixture failed to parse");
                    }
                    pcgen.core.Globals.getContext().commit();
                    pc.addTemplate(template);
                    pc.calcActiveBonuses();
                    int expected = level >= 2 ? Math.max(30, external) + 30 : external;
                    int actual = pc.getDisplay().getVisionList().stream()
                        .filter(v -> v.getType().equals(visionType))
                        .mapToInt(v -> Integer.parseInt(v.getDistance().toString())).max().orElse(0);
                    if (actual != expected) throw new IllegalStateException("Darkvision stacking " + external + ": " + actual);
                    pc.removeTemplate(template);
                    pc.calcActiveBonuses();
                    int restored = pc.getDisplay().getVisionList().stream()
                        .filter(v -> v.getType().equals(visionType))
                        .mapToInt(v -> Integer.parseInt(v.getDistance().toString())).max().orElse(0);
                    if (restored != baseVision) throw new IllegalStateException("Darkvision source removal");
                }
                boolean darkness = pc.getDisplay().getVision(pcgen.util.enumeration.VisionType.getVisionType("See in Darkness")) != null;
                if (darkness != (level >= 14)) {
                    throw new IllegalStateException("See in Darkness level boundary");
                }
                var charisma = pcgen.core.Globals.getContext().getReferenceContext()
                    .silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "CHA");
                int original = pc.getStat(charisma);
                try {
                    for (int score : new int[] {3, 10, 18}) {
                        pc.setStat(charisma, score);
                        pc.setDirty(true);
                        pc.calcActiveBonuses();
                        if (pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOW_POINTS", "").intValue()
                            != Math.max(1, Math.floorDiv(score - 10, 2) + level / 2)) {
                            throw new IllegalStateException("Shadow point capacity must use Charisma: " + score);
                        }
                    }
                } finally {
                    pc.setStat(charisma, original);
                    pc.setDirty(true);
                    pc.calcActiveBonuses();
                }
                if (pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOWMARK_PENALTY", "").intValue() != 1 + (level - 1) / 6
                    || pc.getVariableValue("SPHERES_FEY_ADEPT_MASTER_ILLUSIONIST_ROUNDS", "").intValue() != Math.max(1, level / 2)) {
                    throw new IllegalStateException("Fey Adept duration/penalty progression");
                }
                if (pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Fey Adept Feytouched") != capstone
                    || pc.getTotalBonusTo("SAVE", "Fortitude") != (capstone ? 2 : 0)
                    || pc.getTotalBonusTo("SAVE", "Reflex") != (capstone ? 2 : 0)
                    || pc.getTotalBonusTo("SAVE", "Will") != (capstone ? 2 : 0)
                    || !pc.getDisplay().calcDR().equals(capstone ? "10/cold iron" : "")) {
                    throw new IllegalStateException("Feytouched level boundary: " + level
                        + " DR=" + pc.getDisplay().calcDR() + " saves=" + pc.getTotalBonusTo("SAVE", "Fortitude"));
                }
            }
            if (pc.getClassKeyed("Symbiat") != null) {
                int level = pc.getVariableValue("SPHERES_SYMBIAT_LEVEL", "").intValue();
                int rogue = pc.getVariableValue("RogueLVL", "").intValue();
                if (pc.getTotalBonusTo("SITUATION", "Perception=Avoid being surprised") != level / 3
                    || pc.getTotalBonusTo("SKILL", "Perception") != level / 2
                    || pc.getTotalBonusTo("SKILL", "Sense Motive") != level / 2) {
                    throw new IllegalStateException("Danger Sense Perception: situation="
                        + pc.getTotalBonusTo("SITUATION", "Perception=Avoid being surprised")
                        + " general=" + pc.getTotalBonusTo("SKILL", "Perception") + " level=" + level);
                }
                if (pc.getTotalBonusTo("MOVEADD", "TYPE.Walk") != 10 * Math.min(6, level / 3)) {
                    throw new IllegalStateException("Pushed Movement scaling: "
                        + pc.getTotalBonusTo("MOVEADD", "TYPE.Walk"));
                }
                var category = game.getAbilityCategory("Special Ability");
                String[] defenses = {"Evasion", "Trap Sense", "Uncanny Dodge", "Improved Uncanny Dodge", "Improved Evasion"};
                int[] thresholds = {2, 3, 4, 8, 9};
                for (int i = 0; i < defenses.length; i++) {
                    boolean expected = level >= thresholds[i];
                    if (defenses[i].equals("Improved Uncanny Dodge")) {
                        expected = expected || (level >= 4 && rogue >= 4);
                    }
                    if (pc.hasAbilityKeyed(category, defenses[i]) != expected) {
                        throw new IllegalStateException("Symbiat defense boundary: " + defenses[i]);
                    }
                }
                if (level >= 3 && pc.getVariableValue("TrapSenseBonus", "").intValue() != level / 3 + rogue / 3) {
                    throw new IllegalStateException("Symbiat trap sense scaling");
                }
                if (level >= 4 && pc.getVariableValue("UncannyDodgeFlankingLevel", "").intValue()
                    != level + (rogue >= 4 ? rogue : 0) + (level >= 8 || rogue >= 4 ? 4 : 0)) {
                    throw new IllegalStateException("Symbiat flanking threshold");
                }
            }
            if (pc.getClassKeyed("Sentinel") != null) {
                int level = pc.getVariableValue("SPHERES_SENTINEL_LEVEL", "").intValue();
                var references = pcgen.core.Globals.getContext().getReferenceContext();
                var wisdom = references.silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "WIS");
                var dexterity = references.silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "DEX");
                int originalWisdom = pc.getStat(wisdom);
                int originalDexterity = pc.getStat(dexterity);
                try {
                    for (int[] scores : new int[][] {{18, 10}, {7, 3}, {3, 18}, {18, 18}, {30, 7}}) {
                        pc.setStat(wisdom, scores[0]);
                        pc.setStat(dexterity, scores[1]);
                        pc.setDirty(true);
                        pc.calcActiveBonuses();
                        int wis = Math.floorDiv(scores[0] - 10, 2);
                        int dex = Math.floorDiv(scores[1] - 10, 2);
                        int expected = Math.max(dex, Math.min(wis, level));
                        if (pc.getVariableValue("SPHERES_SENTINEL_RESERVE_POINTS", "").intValue() != Math.max(1, level / 2 + wis)
                            || pc.getVariableValue("SPHERES_SENTINEL_RESERVE_TEMPORARY_HP", "").intValue() != 2 * level + wis) {
                            throw new IllegalStateException("Sentinel reserve formulas");
                        }
                        if (pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Sentinel Second Wind") != (level >= 3)) {
                            throw new IllegalStateException("Second Wind level boundary");
                        }
                        if (level >= 3 && (pc.getVariableValue("SPHERES_SENTINEL_SECOND_WIND_DICE", "").intValue() != level / 2
                            || pc.getVariableValue("SPHERES_SENTINEL_SECOND_WIND_BONUS", "").intValue() != wis)) {
                            throw new IllegalStateException("Second Wind dice and Wisdom modifier");
                        }
                        if (pc.getTotalBonusTo("COMBAT", "INITIATIVE") + dex != expected
                            || pc.getTotalBonusTo("SAVE", "Reflex") != expected) {
                            throw new IllegalStateException("Wise Reflexes replacement WIS=" + scores[0]
                                + " DEX=" + scores[1] + " expected=" + expected
                                + " initiative=" + pc.getTotalBonusTo("COMBAT", "INITIATIVE")
                                + " reflex=" + pc.getTotalBonusTo("SAVE", "Reflex"));
                        }
                    }
                } finally {
                    pc.setStat(wisdom, originalWisdom);
                    pc.setStat(dexterity, originalDexterity);
                    pc.setDirty(true);
                    pc.calcActiveBonuses();
                }
                int reduction = level < 2 ? 0 : 1 + (level - 2) / 4;
                String baseline = pc.getDisplay().calcDR();
                if (reduction > 0 && !baseline.equals(reduction + "/-")) {
                    throw new IllegalStateException("Dedicated Defense: " + baseline);
                }
                var template = new pcgen.core.PCTemplate();
                template.setName("Sentinel DR stacking regression");
                template.addToListFor(pcgen.cdom.enumeration.ListKey.DAMAGE_REDUCTION,
                    new pcgen.cdom.content.DamageReduction(pcgen.cdom.base.FormulaFactory.getFormulaFor("3"), "-"));
                pc.addTemplate(template);
                pc.calcActiveBonuses();
                if (!pc.getDisplay().calcDR().equals((3 + reduction) + "/-")) {
                    throw new IllegalStateException("Dedicated Defense must stack: " + pc.getDisplay().calcDR());
                }
                pc.removeTemplate(template);
                pc.calcActiveBonuses();
                if (!pc.getDisplay().calcDR().equals(baseline)) {
                    throw new IllegalStateException("External DR removal must restore baseline");
                }
            }
            if (pc.getClassKeyed("Thaumaturge") != null) {
                int level = pc.getVariableValue("SPHERES_THAUMATURGE_LEVEL", "").intValue();
                String[][] tiers = {{"Lingering Blessing", "Lingering Pain", "Meditation"},
                    {"Empowered Attack", "Empowered Defense"}, {"Channel Punishment", "Defensive Invocation"},
                    {"Item Lore", "Soulfire"}, {"Empowered Resistance", "Flexible Caster"}, {"Rebuke Death"}};
                int[] thresholds = {1, 3, 7, 11, 15, 19};
                var category = game.getAbilityCategory("Thaumaturge Invocations");
                for (int tier = 0; tier < tiers.length; tier++) {
                    for (String invocation : tiers[tier]) {
                        if (pc.hasAbilityKeyed(category, "Thaumaturge " + invocation) != (level >= thresholds[tier])) {
                            throw new IllegalStateException("Invocation availability: " + invocation);
                        }
                    }
                }
            }
            for (var required : args[4].split(",")) {
                if (required.isEmpty() || required.equals("-")) {
                    continue;
                }
                var category = game.getAbilityCategory(required.startsWith("M:")
                        ? "Spheres Magic Talent" : "Spheres Combat Talent");
                var sphere = required.substring(2) + " Sphere";
                if (!pc.hasAbilityKeyed(category, sphere)) {
                    throw new IllegalStateException("Missing class-granted sphere: " + sphere);
                }
            }
            if (!args[5].equals("-")) {
                var choice = args[5].split(":", 2);
                var category = game.getAbilityCategory(choice[0]);
                if (category == null || !pc.hasAbilityKeyed(category, choice[1])) {
                    throw new IllegalStateException("Missing chosen class feature: " + args[5]);
                }
            }
            if (!args[6].equals("-")) {
                for (var pool : args[6].split("@")) {
                    var parts = pool.split("=", 2);
                    var category = game.getAbilityCategory(parts[0]);
                    if (category == null || pc.getTotalAbilityPool(category)
                            .compareTo(new java.math.BigDecimal(parts[1])) != 0) {
                        throw new IllegalStateException("Incorrect class choice pool " + pool + ": "
                                + (category == null ? "missing" : pc.getTotalAbilityPool(category)));
                    }
                }
            }
            if (args.length == 8) {
                var facade = pcgen.system.CharacterManager.getCharacters().iterator().next();
                facade.setFile(new java.io.File(args[7]));
                if (!pcgen.system.CharacterManager.saveCharacter(facade)) {
                    throw new IllegalStateException("Character save failed");
                }
            }
        }
        System.exit(exported ? 0 : 1);
    }
}