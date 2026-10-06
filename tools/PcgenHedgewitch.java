package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import pcgen.facade.core.ChooserFacade;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** General secret grants, partial refunds and retained selections. */
class PcgenHedgewitch {
    private static void inspiration(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var path = ability(paths, "Hedgewitch Font Of Inspiration");
        var extra = ability(secrets, "Hedgewitch Font Of Inspiration Extra Inspiration");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int repeats = Math.min(2, level / 2);

        boolean reload = args[4].endsWith("reload");
        try {
            if (reload) {
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSPIRATION", "").intValue() == 3 + level / 2 + repeats * 2, "Saved inspiration capacity");
                for (int i = 0; i < repeats; i++) controller.removeAbility(secrets, extra);
            }
            require(pc.hasAbilityKeyed(magic, "Divination Sphere"), "Free Divination sphere");
            var feats = game.getAbilityCategory("FEAT");
            var rigorous = ability(feats, "Rigorous Defense");
            var deduction = ability(feats, "Deduction");
            var life = ability(magic, "Life Sphere");
            var war = ability(magic, "War Sphere");
            require(!rigorous.qualifies(pc, rigorous) && !deduction.qualifies(pc, deduction), "Independent sphere prerequisites");
            controller.addAbility(magic, life);
            require(rigorous.qualifies(pc, rigorous), "Inspiration feature qualifies with Life");
            controller.removeAbility(magic, life);
            controller.addAbility(magic, war);
            require(deduction.qualifies(pc, deduction) == (level >= 5), "Studied combat feature boundary");
            controller.removeAbility(magic, war);
            var combat = game.getAbilityCategory("Spheres Combat Talent");
            var scout = ability(combat, "Scout Sphere");
            var studiedScout = ability(feats, "Studied Scout");
            require(!studiedScout.qualifies(pc, studiedScout), "Studied Scout requires Scout independently");
            var extraCombat = ability(feats, "Extra Combat Talent");
            controller.addAbility(feats, extraCombat);
            controller.addAbility(combat, scout);
            require(studiedScout.qualifies(pc, studiedScout) == (level >= 5), "Studied Scout combat alternative");
            controller.removeAbility(combat, scout);
            controller.removeAbility(feats, extraCombat);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSPIRATION", "").intValue() == 3 + level / 2, "Inspiration base capacity");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_STUDIED_BONUS", "").intValue() == (level >= 5 ? level / 2 : 0), "Studied combat boundary");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_STUDIED_ROUNDS", "").intValue() == (level >= 5 ? Math.max(1, pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue()) : 0), "Studied combat duration");
            for (int i = 1; i <= repeats; i++) {
                controller.addAbility(secrets, extra);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSPIRATION", "").intValue() == 3 + level / 2 + i * 2, "Repeated inspiration grant");
            }
            if (repeats > 0) {
                controller.removeAbility(secrets, extra);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSPIRATION", "").intValue() == 3 + level / 2 + (repeats - 1) * 2, "Partial inspiration refund");
                controller.addAbility(secrets, extra);
            }
            controller.removeAbility(paths, path);
            require(!pc.hasAbilityKeyed(magic, "Divination Sphere"), "Sphere source removal");
            require(!extra.qualifies(pc, extra), "Extra Inspiration prerequisite loss");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSPIRATION", "").intValue() == 0, "Inspiration path loss");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_STUDIED_BONUS", "").intValue() == 0, "Studied combat path loss");
            controller.addAbility(magic, life);
            controller.addAbility(magic, war);
            require(!rigorous.qualifies(pc, rigorous) && !deduction.qualifies(pc, deduction), "Feature-dependent feats reject after path loss");
            controller.removeAbility(magic, life);
            controller.removeAbility(magic, war);
            controller.addAbility(paths, path);
            require(messages.errors.isEmpty(), "Inspiration errors: " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save Inspiration failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }

    private static void charlatan(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var performances = game.getAbilityCategory("Versatile Performance");
        var path = ability(paths, "Hedgewitch Charlatanism");
        var extra = ability(secrets, "Hedgewitch Charlatanism Extra Guile");
        var performance = ability(performances, "Versatile Performance ~ Act");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new MetamagicChoice();
        messages.target = "Bluff";
        var oldDelegate = ChooserFactory.getDelegate();
        ChooserFactory.setDelegate(messages);
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int repeats = Math.min(2, level / 2);
        boolean reload = args[4].endsWith("reload");
        try {
            if (reload) {
                if (level >= 6) {
                    var exceptional = ability(secrets, "Hedgewitch Charlatanism Exceptional Skill");
                    require(pc.getTotalBonusTo("SKILL", "Bluff") == level / 2, "Saved exceptional skill choice");
                    require(pc.getTotalBonusTo("SKILL", "Bluff (Perform (Act))") == level / 2, "Saved substitution bonus");
                    controller.removeAbility(secrets, exceptional);
                }
                require(pc.getAvailableAbilityPool(performances).intValue() == 0, "Saved performance slot spent");
                require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), performance.getKeyName()), "Saved performance choice");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE", "").intValue() == 3 + level / 2 + 2 * repeats, "Saved guile capacity");
                controller.removeAbility(performances, performance);
                for (int i = 0; i < repeats; i++) controller.removeAbility(secrets, extra);
            }
            require(pc.getAvailableAbilityPool(performances).intValue() == 1, "One path performance");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE", "").intValue() == 3 + level / 2, "Base guile capacity");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE_SKILL_BONUS", "").intValue() == (level >= 20 ? 6 : level >= 10 ? 4 : 2), "Guile skill progression");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE_SNEAK_DICE", "").intValue() == (level + 1) / 2, "Guile conditional sneak dice");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE_SNEAK_DIE_SIZE", "").intValue() == (level >= 20 ? 8 : 6), "Mastery die size");
            if (level >= 2) {
                var exceptional = ability(secrets, "Hedgewitch Charlatanism Exceptional Skill");
                double ordinary = pc.getTotalBonusTo("SKILL", "Bluff");
                double substituted = pc.getTotalBonusTo("SKILL", "Bluff (Perform (Act))");
                controller.addAbility(secrets, exceptional);
                require(pc.getTotalBonusTo("SKILL", "Bluff") == ordinary + level / 2, "Exceptional ordinary skill bonus");
                require(pc.getTotalBonusTo("SKILL", "Bluff (Perform (Act))") == substituted + level / 2, "Exceptional substituted skill bonus");
                require(pc.getTotalBonusTo("SKILL", "Disguise (Perform (Act))") == 0, "No bonus to other substitution");
                controller.removeAbility(secrets, exceptional);
                require(pc.getTotalBonusTo("SKILL", "Bluff (Perform (Act))") == substituted, "Exceptional skill refund");
                var evasion = ability(secrets, "Hedgewitch Charlatanism Evasion");
                controller.addAbility(secrets, evasion);
                require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Evasion"), "Evasion grant");
                controller.removeAbility(paths, path);
                require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Evasion"), "Evasion path-loss suppression");
                require(!extra.qualifies(pc, extra), "Secret prerequisite loss");
                controller.addAbility(paths, path);
                controller.removeAbility(secrets, evasion);
                var more = ability(secrets, "Hedgewitch Charlatanism Versatile Performance");
                controller.addAbility(secrets, more);
                require(pc.getAvailableAbilityPool(performances).intValue() == 2, "Extra performance slot");
                controller.removeAbility(secrets, more);
                for (int i = 1; i <= repeats; i++) {
                    controller.addAbility(secrets, extra);
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE", "").intValue() == 3 + level / 2 + 2 * i, "Repeated guile grant");
                }
                controller.removeAbility(secrets, extra);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE", "").intValue() == 3 + level / 2 + 2 * (repeats - 1), "Partial guile refund");
                controller.addAbility(secrets, extra);
            } else require(!extra.qualifies(pc, extra), "Level-one non-Academia secret gate");
            controller.removeAbility(paths, path);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_GUILE", "").intValue() == 0, "Path removal suppresses guile and extras");
            require(pc.getAvailableAbilityPool(performances).intValue() == 0, "Path performance refund");
            controller.addAbility(paths, path);
            controller.addAbility(performances, performance);
            if (level >= 6) controller.addAbility(secrets, ability(secrets, "Hedgewitch Charlatanism Exceptional Skill"));
            require(messages.errors.isEmpty(), "Charlatan errors: " + messages.errors);
        } finally {
            ChooserFactory.setDelegate(oldDelegate);
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save Charlatan failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }

    private static void umbral(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var path = ability(paths, "Hedgewitch Umbral");
        var extra = ability(game.getAbilityCategory("FEAT"), "Extra Shadowstuff");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int fey = pc.getVariableValue("SPHERES_FEY_ADEPT_LEVEL", "").intValue();
        boolean reload = args[4].endsWith("reload");
        var charisma = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "CHA");
        int original = pc.getStat(charisma);
        try {
            require(pc.hasAbilityKeyed(paths, path.getKeyName()), "Saved Umbral path");
            require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOWMARK_DICE", "").intValue() == (Math.max(level, fey) + 1) / 2, "Saved shadowmark uses stronger class, not pooled levels");
            require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOWMARK_DIE_SIZE", "").intValue() == 6, "Umbral shadowmark die size");
            require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOWMARK_PENALTY", "").intValue() == 1 + (Math.max(level, fey) - 1) / 6, "Shadowmark penalty progression");
            var secrets = game.getAbilityCategory("Hedgewitch Secret");
            var eyes = ability(secrets, "Hedgewitch Umbral Eyes of Black");
            var improved = ability(secrets, "Hedgewitch Umbral Improved Shadow Sculptor");
            var shadowSecret = ability(secrets, "Hedgewitch Umbral Shadowstuff");
            var shadowFeats = game.getAbilityCategory("Hedgewitch Shadowstuff Feat");
            if (reload && level >= 10) {
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS", "").intValue() == 2, "Saved repeated Improved Shadow Sculptor");
                controller.removeAbility(secrets, improved);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS", "").intValue() == 1, "Saved partial sculptor refund");
                controller.removeAbility(secrets, improved);
            }
            if (reload && level >= 2) {
                require(pc.hasAbilityKeyed(secrets, eyes.getKeyName()), "Saved Eyes of Black");
                controller.removeAbility(secrets, eyes);
            }
            if (level >= 2) {
                if (reload && level >= 4) {
                    require(pc.hasAbilityKeyed(secrets, shadowSecret.getKeyName()), "Saved Shadowstuff secret");
                    require(pc.getAvailableAbilityPool(shadowFeats).intValue() == 0, "Saved Shadowstuff feat spent slot");
                    controller.removeAbility(shadowFeats, extra);
                    controller.removeAbility(secrets, shadowSecret);
                }
                controller.addAbility(secrets, eyes);
                var vision = pcgen.util.enumeration.VisionType.getVisionType("Darkvision");
                int distance = pc.getDisplay().getVisionList().stream().filter(v -> v.getType().equals(vision))
                    .mapToInt(v -> Integer.parseInt(v.getDistance().toString())).max().orElse(0);
                require(distance == Math.max(level * 5, fey >= 2 ? 30 : 0) + level * 5 + (fey >= 2 ? 30 : 0), "Eyes of Black combines darkvision sources");
            }
            if (level >= 10) {
                var shadowMagic = ability(game.getAbilityCategory("FEAT"), "Shadow Magic");
                controller.addAbility(game.getAbilityCategory("FEAT"), shadowMagic);
                int illusionCL = pc.getVariableValue("SPHERES_CL_ILLUSION", "").intValue();
                require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_EFFECT_CL", "").intValue() == Math.max(1, illusionCL - 2), "Base Shadow Magic CL actual=" + pc.getVariableValue("SPHERES_SHADOW_MAGIC_EFFECT_CL", "") + " illusion=" + illusionCL + " errors=" + messages.errors);
                controller.addAbility(secrets, improved);
                controller.addAbility(secrets, improved);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS", "").intValue() == 2, "Shadow Magic scoped CL");
                require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_EFFECT_CL", "").intValue() == Math.max(1, illusionCL), "Sculptor changes Shadow Magic effects");
                require(pc.getVariableValue("SPHERES_CL_ILLUSION", "").intValue() == illusionCL, "Sculptor does not change ordinary Illusion CL");
                require(!improved.qualifies(pc, improved), "Improved sculptor repeat cap");
                controller.removeAbility(secrets, improved);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS", "").intValue() == 1, "Sculptor partial refund");
                controller.removeAbility(secrets, improved);
                controller.removeAbility(game.getAbilityCategory("FEAT"), shadowMagic);
            } else require(!improved.qualifies(pc, improved), "Grand secret level gate");
            require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOW_POINTS", "").intValue() == 3 + (level + fey) / 2 + (reload ? 2 : 0), "Saved shared shadow capacity");
            if (reload) controller.removeAbility(game.getAbilityCategory("FEAT"), extra);
            for (int score : new int[] {3, 10, 20}) {
                pc.setStat(charisma, score);
                pc.calcActiveBonuses();
                int modifier = pc.getVariableValue("CHA", "").intValue();
                int baseline = (fey > 0 ? Math.max(3, modifier) : 3) + (level + fey) / 2;
                require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOW_POINTS", "").intValue() == baseline, "Combined levels and higher modifier");
                require(extra.qualifies(pc, extra), "Umbral qualifies for Extra Shadowstuff");
                controller.addAbility(game.getAbilityCategory("FEAT"), extra);
                require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOW_POINTS", "").intValue() == baseline + 2, "Extra Shadowstuff added once");
                controller.removeAbility(game.getAbilityCategory("FEAT"), extra);
                controller.removeAbility(paths, path);
                require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOW_POINTS", "").intValue() == (fey > 0 ? Math.max(1, modifier + fey / 2) : 0), "Umbral removal restores Fey-only pool");
                require(extra.qualifies(pc, extra) == (fey > 0), "Shadow prerequisite after path removal");
                require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOWMARK_DICE", "").intValue() == (fey + 1) / 2, "Shadowmark source removal");
                require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOWMARK_DIE_SIZE", "").intValue() == (fey > 0 ? 6 : 0), "Shadowmark die source removal");
                controller.addAbility(paths, path);
            }
            pc.setStat(charisma, original);
            pc.calcActiveBonuses();
            controller.addAbility(game.getAbilityCategory("FEAT"), extra);
            if (level >= 4) {
                controller.addAbility(secrets, shadowSecret);
                controller.addAbility(shadowFeats, extra);
                require(pc.getVariableValue("SPHERES_FEY_ADEPT_SHADOW_POINTS", "").intValue() == 3 + (level + fey) / 2 + 4, "Secret and purchased Extra Shadowstuff stack");
            }
            if (level >= 10) {
                controller.addAbility(secrets, improved);
                controller.addAbility(secrets, improved);
            }
            require(messages.errors.isEmpty(), "Shadow pool errors: " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save Umbral failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
    private static void exorcism(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var path = ability(paths, "Hedgewitch Exorcism");
        var enduring = ability(secrets, "Hedgewitch Exorcism Enduring Exorcism");
        var greater = ability(secrets, "Hedgewitch Exorcism Greater Sanction");
        var moral = ability(secrets, "Hedgewitch Exorcism Moral High-Ground");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int modifier = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
        boolean reload = args[4].endsWith("reload");
        try {
            if (reload) {
                if (level >= 8) {
                    var ward = ability(secrets, "Hedgewitch Exorcism Warding Sanction");
                    var magic = game.getAbilityCategory("Spheres Magic Talent");
                    require(pc.hasAbilityKeyed(secrets, ward.getKeyName()), "Saved Warding Sanction");
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_WARD_CL", "").intValue() == pc.getVariableValue("SPHERES_CL_PROTECTION", "").intValue() + level - level * 3 / 4, "Saved ward caster level");
                    controller.removeAbility(secrets, ward);
                    controller.removeAbility(magic, ability(magic, "Protection Sphere"));
                }
                if (level >= 2) {
                    require(pc.hasAbilityKeyed(secrets, enduring.getKeyName()), "Saved Enduring Exorcism");
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_ROUNDS", "").intValue() == modifier + 10 + 2 * (level - 1), "Saved extra rounds");
                    controller.removeAbility(secrets, enduring);
                }
                if (level >= 10) {
                    require(pc.hasAbilityKeyed(secrets, greater.getKeyName()), "Saved Greater Sanction");
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_DC", "").intValue() == 12 + level / 2 + modifier, "Saved DC secret");
                    controller.removeAbility(secrets, greater);
                    controller.removeAbility(secrets, moral);
                }
            }
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_ROUNDS", "").intValue() == modifier + 4 + 2 * (level - 1), "Base sanction rounds");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_DC", "").intValue() == 10 + level / 2 + modifier, "Base sanction DC");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_RADIUS", "").intValue() == 30 + 5 * ((level - 1) / 4), "Radius progression");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_LIMIT", "").intValue() == 1 + (level - 1) / 4, "Simultaneous sanctions");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_PUSH", "").intValue() == level + modifier, "Sanction push uses class level");
            require(pc.getTotalBonusTo("SITUATION", "Knowledge (Arcana)=Identify Creatures") == level / 2, "Identification-only competence bonus");
            require(pc.getTotalBonusTo("SKILL", "Knowledge (Arcana)") == 0, "No unconditional Knowledge bonus");
            if (level >= 2) {
                var nemesis = ability(secrets, "Hedgewitch Exorcism Nemesis Sanction");
                var ward = ability(secrets, "Hedgewitch Exorcism Warding Sanction");
                var magic = game.getAbilityCategory("Spheres Magic Talent");
                var protection = ability(magic, "Protection Sphere");
                require(!ward.qualifies(pc, ward), "Warding Sanction requires Protection");
                controller.addAbility(magic, protection);
                controller.addAbility(secrets, ward);
                int protectionLevel = pc.getVariableValue("SPHERES_CL_PROTECTION", "").intValue();
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_WARD_CL", "").intValue() == protectionLevel + level - level * 3 / 4, "Wards replace only Hedgewitch progression");
                require(pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "").intValue() == protectionLevel + level - level * 3 / 4, "Shared ward CL includes Warding Sanction");
                controller.removeAbility(magic, protection);
                require(!ward.qualifies(pc, ward), "Protection loss invalidates ward secret");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_WARD_CL", "").intValue() == 0, "Protection loss suppresses ward CL");
                controller.removeAbility(secrets, ward);
                var rattling = ability(secrets, "Hedgewitch Exorcism Rattling Sanction");
                controller.addAbility(secrets, nemesis);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_NEMESIS_RANGE", "").intValue() == 30 + 5 * (level - 1), "Single target sanction range");
                controller.removeAbility(secrets, nemesis);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_NEMESIS_RANGE", "").intValue() == 0, "Nemesis refund");
                controller.addAbility(secrets, rattling);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_RATTLING_DICE", "").intValue() == level / 2, "Rattling dice");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_RATTLING_TARGETS", "").intValue() == Math.max(1, level / 2), "Rattling optional targets");
                controller.removeAbility(secrets, rattling);
            }
            if (level >= 2) controller.addAbility(secrets, enduring);
            else require(!enduring.qualifies(pc, enduring), "No first-level Exorcism secret");
            if (level >= 10) {
                controller.addAbility(secrets, greater);
                controller.addAbility(secrets, moral);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_RADIUS", "").intValue() == 50 + 5 * ((level - 1) / 4), "Greater sanction range");
            } else require(!greater.qualifies(pc, greater), "Grand secret boundary");
            controller.removeAbility(paths, path);
            for (String quantity : new String[] {"ROUNDS", "DC", "RADIUS", "LIMIT", "PUSH"}) {
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_" + quantity, "").intValue() == 0, "Path loss suppresses " + quantity);
            }
            require(!enduring.qualifies(pc, enduring), "Lost path prerequisite");
            controller.addAbility(paths, path);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_SANCTION_ROUNDS", "").intValue() == modifier + 4 + 2 * (level - 1) + (level >= 2 ? 6 : 0), "Restored sanction resources");
            if (level >= 8) {
                var magic = game.getAbilityCategory("Spheres Magic Talent");
                controller.addAbility(magic, ability(magic, "Protection Sphere"));
                controller.addAbility(secrets, ability(secrets, "Hedgewitch Exorcism Warding Sanction"));
            }
            require(messages.errors.isEmpty(), "Exorcism errors: " + messages.errors);
        } finally { controller.closeCharacter(); }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save Exorcism failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }

    private static void combatMastery(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var category = game.getAbilityCategory("Hedgewitch Combat Mastery");
        var path = ability(paths, "Hedgewitch Combat");
        var choice = ability(category, "Hedgewitch Combat Mastery - Constitution");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].endsWith("reload");
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        try {
            require(pc.hasAbilityKeyed(paths, path.getKeyName()), "Combat path persists");
            if (level == 20) {
                if (reload) {
                    require(pc.hasAbilityKeyed(category, choice.getKeyName()), "Combat mastery selection persists");
                    require(pc.getAvailableAbilityPool(category).intValue() == 0, "Saved mastery slot cost");
                    require(pc.getTotalBonusTo("STAT", "CON") == 2, "Saved mastery Constitution");
                    controller.removeAbility(category, choice);
                }
                require(pc.getTotalBonusTo("STAT", "CON") == 0, "No mastery bonus without choice");
                require(pc.getAvailableAbilityPool(category).intValue() == 1, "Combat mastery slot");
                for (String name : new String[] {"Strength", "Dexterity", "Constitution"}) {
                    String stat = name.equals("Strength") ? "STR" : name.equals("Dexterity") ? "DEX" : "CON";
                    var candidate = ability(category, "Hedgewitch Combat Mastery - " + name);
                    controller.addAbility(category, candidate);
                    require(pc.getTotalBonusTo("STAT", stat) == 2, "Physical mastery choice " + name);
                    controller.removeAbility(paths, path);
                    require(pc.getTotalBonusTo("STAT", stat) == 0, "Physical mastery path suppression " + name);
                    controller.addAbility(paths, path);
                    require(pc.getTotalBonusTo("STAT", stat) == 2, "Physical mastery path restoration " + name);
                    controller.removeAbility(category, candidate);
                    require(pc.getTotalBonusTo("STAT", stat) == 0, "Physical mastery refund " + name);
                }
                controller.addAbility(category, choice);
            } else {
                require(!choice.qualifies(pc, choice), "No early mastery");
                require(pc.getAvailableAbilityPool(category).intValue() == 0, "No early mastery slot");
            }
            require(messages.errors.isEmpty(), "Combat mastery errors: " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save mastery failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
    private static void savedResources(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int repeats = Math.min(2, level / 4);
        boolean reload = args[4].endsWith("reload");
        boolean herbs = args[6].equals("herbology");
        int actionSecrets = herbs && level >= 14 ? 3 : 0;
        String[][] entries = herbs
            ? new String[][] {{"Herbology", "Extra Concoctions", "CONCOCTIONS"}, {"Transmuter", "Transformations", "TRANSMUTATIONS"}}
            : new String[][] {{"Black Magic", "Curses", "CURSES"}, {"Spiritualism", "Extra Spirit", "SPIRIT_USES"}};
        try {
            require(pc.getAvailableAbilityPool(paths).intValue() == 0, "Saved resource paths occupy both slots");
            require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 - (reload ? 2 * repeats + actionSecrets : 0), "Saved resource secret costs");
            if (actionSecrets > 0 && reload) {
                var potent = ability(secrets, "Hedgewitch Herbology Potent Concoctions");
                var swift = ability(secrets, "Hedgewitch Herbology Swift Poison");
                var instant = ability(secrets, "Hedgewitch Herbology Instant Poison");
                require(pc.hasAbilityKeyed(secrets, potent.getKeyName()), "Saved Potent Concoctions");
                require(pc.hasAbilityKeyed(secrets, swift.getKeyName()), "Saved Swift Poison");
                require(pc.hasAbilityKeyed(secrets, instant.getKeyName()) && instant.qualifies(pc, instant), "Saved dependent Instant Poison");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == level, "Saved expiration duration");
                var path = ability(paths, "Hedgewitch Herbology");
                controller.removeAbility(paths, path);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == 0, "Retained Potent suppressed without path");
                require(!instant.qualifies(pc, instant), "Retained Instant Poison loses path");
                controller.addAbility(paths, path);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == level, "Retained Potent restored");
                controller.removeAbility(secrets, swift);
                require(!instant.qualifies(pc, instant), "Retained Instant Poison loses Swift Poison");
                controller.removeAbility(secrets, instant);
                controller.removeAbility(secrets, potent);
            }
            for (String[] entry : entries) {
                var path = ability(paths, "Hedgewitch " + entry[0]);
                var secret = ability(secrets, "Hedgewitch " + entry[0] + " " + entry[1]);
                String variable = "SPHERES_HEDGEWITCH_" + entry[2];
                require(pc.hasAbilityKeyed(paths, path.getKeyName()), "Saved path key");
                require(pc.getVariableValue(variable, "").intValue() == 3 + level / 2 + (reload ? 2 * repeats : 0), "Saved capacity: " + variable);
                if (reload) {
                    for (int i = repeats - 1; i >= 0; i--) {
                        controller.removeAbility(secrets, secret);
                        require(pc.getVariableValue(variable, "").intValue() == 3 + level / 2 + 2 * i, "Saved partial refund");
                    }
                }
                controller.removeAbility(paths, path);
                require(!secret.qualifies(pc, secret), "Saved secret loses path qualification");
                require(pc.getVariableValue(variable, "").intValue() == 0, "Saved path refund");
                controller.addAbility(paths, path);
                for (int i = 0; i < repeats; i++) controller.addAbility(secrets, secret);
            }
            if (herbs) {
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Distill Compound"), "Persisted Distill Compound");
                require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Assassin ~ Poison Use"), "Persisted poison use");
                if (actionSecrets > 0) {
                    for (String name : new String[] {"Potent Concoctions", "Swift Poison", "Instant Poison"}) {
                        controller.addAbility(secrets, ability(secrets, "Hedgewitch Herbology " + name));
                    }
                }
            } else {
                int limit = level >= 20 ? 3 + level / 2 + 2 * repeats : 1 + (level >= 5 ? 1 : 0) + (level >= 13 ? 1 : 0);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_SPIRIT_TALENT_LIMIT", "").intValue() == limit, "Saved spirit capacity");
            }
            require(messages.errors.isEmpty(), "Unexpected saved-resource errors: " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save resources failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
    private static void resources(String[] args) throws Exception {
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var traveler = ability(paths, "Hedgewitch Temporal Traveler");
        var transmuter = ability(paths, "Hedgewitch Transmuter");
        var extra = ability(secrets, "Hedgewitch Transmuter Transformations");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].endsWith("reload");
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int repeats = Math.min(2, level / 2);
        var gritSecret = ability(secrets, "Hedgewitch Temporal Traveler Grit Feats");
        var gritPool = game.getAbilityCategory("Hedgewitch Grit Feat");
        if (reload && level >= 6) {
            require(pc.getAvailableAbilityPool(gritPool).intValue() == 1, "Saved grit slot");
            controller.removeAbility(secrets, gritSecret);
        }
        try {
            require(pc.getAvailableAbilityPool(paths).intValue() == 0, "Resource paths persist");
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Spheres Magic Talent"), "Time Sphere"), "Saved Time sphere");
            for (String[] entry : new String[][] {{"Practiced Transmutation", "SIZE_STEPS"},
                    {"Ranged Transmutation", "RANGE"}, {"Greater Transformation", "HD_BONUS"}}) {
                var secret = ability(secrets, "Hedgewitch Transmuter " + entry[0]);
                int minimum = entry[1].equals("HD_BONUS") ? 10 : 2;
                if (level < minimum) {
                    require(!secret.qualifies(pc, secret), "Transmuter secret level gate " + entry[0]);
                    continue;
                }
                controller.addAbility(secrets, secret);
                int expected = entry[1].equals("SIZE_STEPS") ? 1 : entry[1].equals("RANGE") ? 25 + 5 * (level / 2) : 1 + (level - 10) / 3;
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATION_" + entry[1], "").intValue() == expected, "Transmuter scoped value " + entry[0]);
                controller.removeAbility(paths, transmuter);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATION_" + entry[1], "").intValue() == 0, "Transmuter secret suppression " + entry[0]);
                controller.addAbility(paths, transmuter);
                controller.removeAbility(secrets, secret);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATION_" + entry[1], "").intValue() == 0, "Transmuter secret refund " + entry[0]);
            }
            var magic = game.getAbilityCategory("Spheres Magic Talent");
            var creation = ability(magic, "Creation Sphere");
            if (!reload) {
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == 0, "No create effect without sphere");
                controller.addAbility(magic, creation);
            }
            int generalCL = pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue();
            require(pc.getVariableValue("SPHERES_CL_CREATION", "").intValue() == generalCL, "Alter CL unchanged");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == generalCL + level - level * 3 / 4, "Create-only full progression preserves other classes");
            controller.removeAbility(magic, creation);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == 0, "Create reference loses sphere prerequisite");
            controller.addAbility(magic, creation);
            if (reload) {
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 - repeats, "Saved resource secret cost");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATIONS", "").intValue() == 3 + level / 2 + 2 * repeats, "Saved transformation capacity");
                for (int i = repeats; i > 0; i--) {
                    controller.removeAbility(secrets, extra);
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATIONS", "").intValue() == 3 + level / 2 + 2 * (i - 1), "Partial transformation refund");
                }
            }
            if (level >= 2) {
                for (int i = 1; i <= repeats; i++) {
                    controller.addAbility(secrets, gritSecret);
                    require(pc.getAvailableAbilityPool(gritPool).intValue() == i, "Repeated grit feat slots");
                }
                for (int i = repeats - 1; i >= 0; i--) {
                    controller.removeAbility(secrets, gritSecret);
                    require(pc.getAvailableAbilityPool(gritPool).intValue() == i, "Partial grit feat slot refunds");
                }
            } else {
                require(!gritSecret.qualifies(pc, gritSecret), "Grit secret level gate");
            }
            var intelligence = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "INT");
            int original = pc.getStat(intelligence);
            for (int score : new int[] {7, 10, 18}) {
                pc.setStat(intelligence, score);
                pc.calcActiveBonuses();
                int modifier = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSIGHT_CAPACITY", "").intValue() == Math.max(1, modifier), "Insight modifier and floor");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATION_DC", "").intValue() == 10 + level / 2 + modifier, "Transformation DC modifier");
            }
            pc.setStat(intelligence, original);
            pc.calcActiveBonuses();
            controller.removeAbility(paths, traveler);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSIGHT_CAPACITY", "").intValue() == 0, "Insight refund");
            require(!gritSecret.qualifies(pc, gritSecret), "Grit secret requires traveler path");
            controller.removeAbility(paths, transmuter);
            require(!extra.qualifies(pc, extra), "Transformations rejects missing path");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATIONS", "").intValue() == 0, "Transformation path refund");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == 0, "Create reference loses path");
            var herbology = ability(paths, "Hedgewitch Herbology");
            var concoctions = ability(secrets, "Hedgewitch Herbology Extra Concoctions");
            controller.addAbility(paths, herbology);
            require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Distill Compound"), "Herbology bonus feat");
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Assassin ~ Poison Use"), "Herbology poison use");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == 1, "Base concoction expiration");
            var potent = ability(secrets, "Hedgewitch Herbology Potent Concoctions");
            if (level >= 2) {
                controller.addAbility(secrets, potent);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == level, "Potent expiration");
                controller.removeAbility(secrets, potent);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == 1, "Expiration refund");
                for (String[] pair : new String[][] {{"Swift Poison", "Instant Poison"}, {"Surgeon", "Miracle Man"}}) {
                    var base = ability(secrets, "Hedgewitch Herbology " + pair[0]);
                    var grand = ability(secrets, "Hedgewitch Herbology " + pair[1]);
                    require(!grand.qualifies(pc, grand), "Missing Herbology secret prerequisite");
                    controller.addAbility(secrets, base);
                    require(grand.qualifies(pc, grand) == (level >= 10), "Herbology grand-secret level");
                    controller.removeAbility(secrets, base);
                    require(!grand.qualifies(pc, grand), "Herbology lost secret prerequisite");
                }
            }
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTIONS", "").intValue() == 3 + level / 2, "Concoction capacity");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HEALING_DICE", "").intValue() == Math.max(1, level / 2), "Concoction healing dice floor");
            for (int i = 1; i <= repeats; i++) {
                controller.addAbility(secrets, concoctions);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTIONS", "").intValue() == 3 + level / 2 + 2 * i, "Repeated concoctions");
            }
            for (int i = repeats; i > 0; i--) controller.removeAbility(secrets, concoctions);
            controller.removeAbility(paths, herbology);
            require(!pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Distill Compound"), "Herbology feat refund");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTIONS", "").intValue() == 0, "Concoction refund");
            require(!potent.qualifies(pc, potent), "Potent requires Herbology");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_CONCOCTION_HOURS", "").intValue() == 0, "Expiration path refund");
            require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Assassin ~ Poison Use"), "Poison use refund");
            for (String[] entry : new String[][] {{"Black Magic", "Curses", "CURSES"}, {"Spiritualism", "Extra Spirit", "SPIRIT_USES"}}) {
                var path = ability(paths, "Hedgewitch " + entry[0]);
                var secret = ability(secrets, "Hedgewitch " + entry[0] + " " + entry[1]);
                String variable = "SPHERES_HEDGEWITCH_" + entry[2];
                var magicPool = pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Magic Talent"));
                require(!secret.qualifies(pc, secret), "Resource secret requires path");
                controller.addAbility(paths, path);
                require(pc.getVariableValue(variable, "").intValue() == 3 + level / 2, "Path resource capacity");
                for (int i = 1; i <= repeats; i++) {
                    controller.addAbility(secrets, secret);
                    require(pc.getVariableValue(variable, "").intValue() == 3 + level / 2 + 2 * i, "Repeated resource secret");
                }
                if (entry[0].equals("Spiritualism")) {
                    int limit = level >= 20 ? 3 + level / 2 + 2 * repeats : 1 + (level >= 5 ? 1 : 0) + (level >= 13 ? 1 : 0);
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_SPIRIT_TALENT_LIMIT", "").intValue() == limit, "Spirit simultaneous capacity");
                    require(pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Magic Talent")).equals(magicPool), "Spiritualism does not grant permanent talents");
                }
                for (int i = repeats - 1; i >= 0; i--) {
                    controller.removeAbility(secrets, secret);
                    require(pc.getVariableValue(variable, "").intValue() == 3 + level / 2 + 2 * i, "Resource secret partial refund");
                }
                controller.removeAbility(paths, path);
                require(pc.getVariableValue(variable, "").intValue() == 0, "Resource path refund");
            }
            controller.addAbility(paths, traveler);
            controller.addAbility(paths, transmuter);
            for (int i = 0; i < repeats; i++) controller.addAbility(secrets, extra);
            require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 - repeats, "Repeated resource secret cost");
            if (level >= 6) {
                controller.addAbility(secrets, gritSecret);
                controller.removeAbility(paths, traveler);
                require(pc.getAvailableAbilityPool(gritPool).intValue() == 0, "Lost path suppresses grit slot");
                controller.addAbility(paths, traveler);
                require(pc.getAvailableAbilityPool(gritPool).intValue() == 1, "Restored grit slot");
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 - repeats - 1, "Saved grit secret cost");
            }
            require(messages.errors.isEmpty(), "Resource errors: " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Resource save failed");
        }
    }
    private static class MetamagicChoice extends Messages {
        String target = "Extend Spell";
        boolean addingRepeat;
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            if (chooser.getSelectedList().getSize() > 0 && !addingRepeat) {
                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                chooser.commit();
                return true;
            }
            if (target.equals("Extend Spell")) {
                require(chooser.getAvailableList().getSize() == 1, "Only the owned metamagic feat is offered");
            }
            for (var selected : chooser.getAvailableList()) {
                if (selected.getKeyName().equals(target)) {
                    chooser.addSelected(selected);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing choice " + target);
        }
    }
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        if (args.length > 6 && args[6].equals("inspiration")) {
            inspiration(args);
            return;
        }
        if (args.length > 6 && args[6].equals("charlatan")) {
            charlatan(args);
            return;
        }
        if (args.length > 6 && args[6].equals("umbral")) {
            umbral(args);
            return;
        }
        if (args.length > 6 && args[6].equals("exorcism")) {
            exorcism(args);
            return;
        }
        if (args.length > 6 && args[6].equals("combat")) {
            combatMastery(args);
            return;
        }
        if (args.length > 6 && (args[6].equals("herbology") || args[6].equals("spirits"))) {
            savedResources(args);
            return;
        }
        if (args.length > 6 && args[6].equals("resources")) {
            resources(args);
            System.out.println("SPHERES_GATES_OK: " + args[4]);
            System.exit(0);
        }
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var magic = game.getAbilityCategory("Hedgewitch Magical Skill Feat");
        var champion = game.getAbilityCategory("Hedgewitch Champion Feat");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new MetamagicChoice();
        var oldDelegate = ChooserFactory.getDelegate();
        ChooserFactory.setDelegate(messages);
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        boolean reload = args[4].equals("hedgewitch-reload");
        var training = ability(secrets, "Hedgewitch Combat Talent");
        var familiar = ability(secrets, "Hedgewitch Familiar");
        var magical = ability(secrets, "Hedgewitch Magical Skill");
        var feat = ability(magic, "Extend Spell");
        var master = ability(secrets, "Hedgewitch Metamagic Master");
        var builder = ability(secrets, "Hedgewitch Arcane Builder");
        try {
            var auras = game.getAbilityCategory("Hedgewitch Celestial Aura");
            var moon = ability(auras, "Hedgewitch Celestial Aura - Moon");
            var star = ability(auras, "Hedgewitch Celestial Aura - Star");
            if (reload) {
                require(pc.getAvailableAbilityPool(auras).intValue() == 0, "Saved two known auras");
                controller.removeAbility(auras, moon);
                controller.removeAbility(auras, star);
            }
            require(pc.getAvailableAbilityPool(auras).intValue() == 2, "Astrology grants two known auras");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_EFFECTIVE_LEVEL", "").intValue() == level + (level == 20 ? 5 : 0), "Astrology mastery effective level");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_ACTIVE_LIMIT", "").intValue() == 1, "Base active aura limit");
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Spheres Magic Talent"), "Light Sphere"), "Astrology bonus Light sphere");
            controller.addAbility(auras, moon);
            controller.addAbility(auras, star);
            require(pc.getAvailableAbilityPool(auras).intValue() == 0, "Aura selections spend separate pool");
            var metamagicCategory = game.getAbilityCategory("Hedgewitch Metamagic Knowledge Feat");
            var knowledge = ability(secrets, "Hedgewitch Academia Metamagic Knowledge");
            var silent = ability(metamagicCategory, "Silent Spell");
            if (reload && level >= 12) {
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Silent Spell"), "Saved path-secret metamagic feat");
                require(pc.getAvailableAbilityPool(metamagicCategory).intValue() == 0, "Saved path-secret feat slot cost");
                controller.removeAbility(metamagicCategory, silent);
                controller.removeAbility(secrets, knowledge);
                require(pc.getAvailableAbilityPool(metamagicCategory).intValue() == 0, "Saved path-secret refund");
            }
            var masteryCategory = game.getAbilityCategory("Hedgewitch Academia Mastery");
            var wisdomMastery = ability(masteryCategory, "Hedgewitch Academia Mastery - Wisdom");
            if (reload && level == 20) {
                require(pc.getTotalBonusTo("STAT", "WIS") == 2, "Saved Academia mastery bonus");
                require(pc.getAvailableAbilityPool(masteryCategory).intValue() == 0, "Saved mastery slot spend");
                controller.removeAbility(masteryCategory, wisdomMastery);
                require(pc.getTotalBonusTo("STAT", "WIS") == 0, "Saved mastery removal");
            }
            require(pc.getAvailableAbilityPool(masteryCategory).intValue() == (level == 20 ? 1 : 0), "Academia mastery level gate");
            require(wisdomMastery.qualifies(pc, wisdomMastery) == (level == 20), "Mastery qualification level");
            var paths = game.getAbilityCategory("Hedgewitch Path");
            var academia = ability(paths, "Hedgewitch Academia");
            var astrology = ability(paths, "Hedgewitch Astrology");
            var geography = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Knowledge (Geography)");
            var nature = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Knowledge (Nature)");
            require(pc.isClassSkill(geography) && pc.isClassSkill(nature), "Loaded path class skills");
            int loadedPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
            var extraPoints = ability(secrets, "Hedgewitch Academia Extra Spell Points");
            if (reload && level == 1) {
                require(pc.getAvailableAbilityPool(secrets).intValue() == 0, "Saved first-level Academia secret cost");
                require(loadedPoints == 3, "Saved first-level extra spell points");
                controller.removeAbility(secrets, extraPoints);
                loadedPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                require(loadedPoints == 1, "Saved extra spell point refund");
            }
            controller.removeAbility(paths, academia);
            require(!wisdomMastery.qualifies(pc, wisdomMastery), "Mastery requires actual Academia path");
            require(!extraPoints.qualifies(pc, extraPoints), "Path secret requires Academia");
            require(!knowledge.qualifies(pc, knowledge), "Metamagic Knowledge requires Academia");
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == loadedPoints - level / 2, "Academia spell point refund");
            require(training.qualifies(pc, training) == (level >= 2), "Without Academia normal secret level applies");
            require(pc.isClassSkill(geography), "Shared path skill survives one source removal");
            require(!pc.isClassSkill(nature), "Unique path skill refunded");
            controller.removeAbility(paths, astrology);
            require(!moon.qualifies(pc, moon), "Known aura requires Astrology path");
            require(!pc.hasAbilityKeyed(game.getAbilityCategory("Spheres Magic Talent"), "Light Sphere"), "Astrology sphere refund");
            require(!pc.isClassSkill(geography), "Shared skill removed with final source");
            var umbral = ability(paths, "Hedgewitch Umbral");
            var combatPath = ability(paths, "Hedgewitch Combat");
            var combatSecret = ability(secrets, "Hedgewitch Combat Combat Feat");
            var combatFeats = game.getAbilityCategory("Hedgewitch Combat Feat");
            var combatFeat = ability(combatFeats, "Improved Initiative");
            require(!combatSecret.qualifies(pc, combatSecret), "Combat secret rejects wrong path");
            controller.addAbility(paths, combatPath);
            var combatMastery = game.getAbilityCategory("Hedgewitch Combat Mastery");
            var constitutionMastery = ability(combatMastery, "Hedgewitch Combat Mastery - Constitution");
            require(pc.getAvailableAbilityPool(combatMastery).intValue() == (level == 20 ? 1 : 0), "Combat mastery pool level");
            require(constitutionMastery.qualifies(pc, constitutionMastery) == (level == 20), "Combat mastery level prerequisite");
            if (level == 20) {
                double con = pc.getTotalBonusTo("STAT", "CON");
                controller.addAbility(combatMastery, constitutionMastery);
                require(pc.getTotalBonusTo("STAT", "CON") == con + 2, "Combat mastery Constitution");
                controller.removeAbility(paths, combatPath);
                require(pc.getTotalBonusTo("STAT", "CON") == con, "Combat mastery suppressed on path loss");
                require(!constitutionMastery.qualifies(pc, constitutionMastery), "Combat mastery loses prerequisite");
                controller.addAbility(paths, combatPath);
                require(pc.getTotalBonusTo("STAT", "CON") == con + 2, "Combat mastery restored");
                controller.removeAbility(combatMastery, constitutionMastery);
                require(pc.getTotalBonusTo("STAT", "CON") == con, "Combat mastery refund");
            }
            if (level >= 2 && !reload) {
                controller.addAbility(secrets, combatSecret);
                require(pc.getAvailableAbilityPool(combatFeats).intValue() == 1, "Combat secret feat slot");
                controller.addAbility(combatFeats, combatFeat);
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Improved Initiative"), "Combat secret grants chosen feat");
                controller.removeAbility(paths, combatPath);
                require(pc.getAvailableAbilityPool(combatFeats).intValue() == -1, "Path loss exposes spent unsupported combat slot");
                require(!combatSecret.qualifies(pc, combatSecret), "Combat secret loses path qualification");
                controller.addAbility(paths, combatPath);
                require(pc.getAvailableAbilityPool(combatFeats).intValue() == 0, "Path restoration restores spent combat slot");
                controller.removeAbility(combatFeats, combatFeat);
                controller.removeAbility(secrets, combatSecret);
                require(pc.getAvailableAbilityPool(combatFeats).intValue() == 0, "Combat secret refunds pool");
                var tactician = ability(secrets, "Hedgewitch Combat Tactician");
                controller.addAbility(secrets, tactician);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TACTICIAN_USES", "").intValue() == 1, "Tactician use grant");
                controller.removeAbility(paths, combatPath);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TACTICIAN_USES", "").intValue() == 0, "Tactician uses suppressed without path");
                require(pc.getAvailableAbilityPool(game.getAbilityCategory("Hedgewitch Tactician Feat")).intValue() == 0, "Tactician slots suppressed without path");
                controller.addAbility(paths, combatPath);
                controller.removeAbility(secrets, tactician);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TACTICIAN_USES", "").intValue() == 0, "Tactician refund");
                var aid = ability(secrets, "Hedgewitch Combat Greater Aid");
                controller.addAbility(secrets, aid);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AID_BONUS", "").intValue() == 3 + level / 6, "Greater Aid scaling");
                controller.removeAbility(paths, combatPath);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AID_BONUS", "").intValue() == 0, "Greater Aid requires retained path");
                controller.addAbility(paths, combatPath);
                controller.removeAbility(secrets, aid);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AID_BONUS", "").intValue() == 0, "Greater Aid refund");
                var armorTraining = ability(secrets, "Hedgewitch Combat Armor Training");
                require(armorTraining.qualifies(pc, armorTraining) == (level >= 10), "Armor Training grand-secret gate");
                if (level >= 10) {
                    var walk = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
                    var strength = Globals.getContext().getReferenceContext()
                        .silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "STR");
                    int originalStrength = pc.getStat(strength);
                    pc.setStat(strength, 20);
                    pc.calcActiveBonuses();
                    double baseSpeed = pc.getDisplay().movementOfType(walk);
                    for (String armorName : new String[] {"Chainmail", "Full Plate"}) {
                        var armor = Globals.getContext().getReferenceContext()
                            .silentlyGetConstructedCDOMObject(pcgen.core.Equipment.class, armorName).clone();
                        pc.addEquipment(armor);
                        var armorSet = new pcgen.core.character.EquipSet("0.9", "Hedgewitch armor regression");
                        pc.addEquipSet(armorSet);
                        var equipped = new pcgen.core.character.EquipSet("0.9.1", "Armor", armor.getName(), armor);
                        pc.addEquipSet(equipped);
                        pc.setCalcEquipSetId("0.9");
                        pc.setCalcEquipmentList();
                        pc.calcActiveBonuses();
                        require(pc.getDisplay().movementOfType(walk) < baseSpeed, "Armor initially slows movement");
                        controller.addAbility(secrets, armorTraining);
                        pc.adjustMoveRates();
                        require(pc.getDisplay().movementOfType(walk) == baseSpeed, "Armor Training restores movement");
                        controller.removeAbility(secrets, armorTraining);
                        pc.adjustMoveRates();
                        require(pc.getDisplay().movementOfType(walk) < baseSpeed, "Armor Training removal restores penalty");
                        pc.delEquipSet(equipped);
                        pc.delEquipSet(armorSet);
                        pc.setCalcEquipSetId("0.1");
                        pc.setCalcEquipmentList();
                        pc.removeEquipment(armor);
                        pc.calcActiveBonuses();
                    }
                    pc.setStat(strength, originalStrength);
                    pc.calcActiveBonuses();
                }
            }
            controller.removeAbility(paths, combatPath);
            double stealth = pc.getTotalBonusTo("SKILL", "Stealth");
            double disguise = pc.getTotalBonusTo("SKILL", "Disguise");
            controller.addAbility(paths, umbral);
            var sculptor = ability(secrets, "Hedgewitch Umbral Shadow Sculptor");
            if (level >= 2 && !reload) {
                controller.addAbility(secrets, sculptor);
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Shadow Magic"), "Shadow Sculptor automatic feat");
                controller.removeAbility(secrets, sculptor);
                require(!pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Shadow Magic"), "Shadow Sculptor removal");
            }
            require(pc.getTotalBonusTo("SKILL", "Stealth") == stealth + Math.max(1, level / 2), "Umbral Stealth scaling");
            require(pc.getTotalBonusTo("SKILL", "Disguise") == disguise + Math.max(1, level / 2), "Umbral Disguise scaling");
            controller.removeAbility(paths, umbral);
            require(pc.getTotalBonusTo("SKILL", "Stealth") == stealth, "Umbral bonus refund");
            var green = ability(paths, "Hedgewitch Green Magic");
            controller.addAbility(paths, green);
            var bonds = ability(secrets, "Hedgewitch Green Magic Bestial Bonds");
            var venom = ability(secrets, "Hedgewitch Green Magic Venom Immunity");
            var vitality = ability(secrets, "Hedgewitch Green Magic Wild Vitality");
            require(venom.qualifies(pc, venom) == (level >= 10), "Green immunity grand-secret level");
            if (level >= 2 && !reload) {
                var combatPool = pc.getAvailableAbilityPool(combat);
                controller.addAbility(secrets, bonds);
                require(pc.hasAbilityKeyed(combat, "Beastmastery Sphere"), "Bestial Bonds base sphere");
                require(pc.hasAbilityKeyed(combat, "Beastmastery - Focusing Connection"), "Bestial Bonds bonus talent");
                controller.removeAbility(paths, green);
                require(!pc.hasAbilityKeyed(combat, "Beastmastery Sphere"), "Bestial Bonds suppressed with path loss");
                controller.addAbility(paths, green);
                require(pc.hasAbilityKeyed(combat, "Beastmastery Sphere"), "Bestial Bonds restores with path");
                require(pc.getAvailableAbilityPool(combat).equals(combatPool), "Bonus talents do not spend normal pool");
                controller.removeAbility(secrets, bonds);
                require(!pc.hasAbilityKeyed(combat, "Beastmastery Sphere"), "Bestial Bonds refund");
                if (level >= 10) {
                    controller.addAbility(secrets, venom);
                    require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Poison"), "Venom immunity grant");
                    controller.removeAbility(paths, green);
                    require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Poison"), "Venom immunity path suppression");
                    controller.addAbility(paths, green);
                    controller.removeAbility(secrets, venom);
                    require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Poison"), "Venom immunity refund");
                    controller.addAbility(secrets, vitality);
                    require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Disease"), "Disease immunity grant");
                    controller.removeAbility(secrets, vitality);
                }
            }
            require(pc.getVariableValue("WildEmpathyLVL", "").intValue() == level, "Green Magic wild empathy advancement");
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Druid ~ Woodland Stride"), "Green Magic woodland stride");
            controller.removeAbility(paths, green);
            require(!bonds.qualifies(pc, bonds), "Bestial Bonds requires Green Magic path");
            require(pc.getVariableValue("WildEmpathyLVL", "").intValue() == 0, "Wild empathy refund");
            require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Druid ~ Woodland Stride"), "Woodland stride refund");
            var tinker = ability(paths, "Hedgewitch Tinker");
            double perception = pc.getTotalBonusTo("SKILL", "Perception");
            controller.addAbility(paths, tinker);
            require(pc.getTotalBonusTo("SKILL", "Disable Device") == Math.max(1, level / 2), "Tinker Disable Device");
            require(pc.getTotalBonusTo("SITUATION", "Perception=Trapfinding") == Math.max(1, level / 2), "Tinker trap perception");
            require(pc.getTotalBonusTo("SKILL", "Perception") == perception, "No unconditional Perception bonus");
            controller.removeAbility(paths, tinker);
            require(pc.getTotalBonusTo("SKILL", "Disable Device") == 0, "Tinker refund");
            var traveler = ability(paths, "Hedgewitch Temporal Traveler");
            controller.addAbility(paths, traveler);
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Spheres Magic Talent"), "Time Sphere"), "Temporal Traveler bonus sphere");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSIGHT_CAPACITY", "").intValue() == Math.max(1, pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue()), "Insight capacity floor");
            if (level >= 2 && !reload) {
                var traps = ability(secrets, "Hedgewitch Temporal Traveler Trapfinding");
                controller.addAbility(secrets, traps);
                require(pc.getTotalBonusTo("SKILL", "Disable Device") == Math.max(1, level / 2), "Temporal trapfinding scaling");
                controller.removeAbility(secrets, traps);
            }
            controller.removeAbility(paths, traveler);
            require(!pc.hasAbilityKeyed(game.getAbilityCategory("Spheres Magic Talent"), "Time Sphere"), "Temporal sphere refund");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_INSIGHT_CAPACITY", "").intValue() == 0, "Insight capacity refund");
            var transmuter = ability(paths, "Hedgewitch Transmuter");
            controller.addAbility(paths, transmuter);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATIONS", "").intValue() == 3 + level / 2, "Transmuter daily capacity");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATION_DC", "").intValue() == 10 + level / 2 + pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue(), "Transmuter save DC");
            if (level >= 2 && !reload) {
                var transforms = ability(secrets, "Hedgewitch Transmuter Transformations");
                controller.addAbility(secrets, transforms);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATIONS", "").intValue() == 5 + level / 2, "Extra transformations capacity");
                controller.removeAbility(secrets, transforms);
            }
            controller.removeAbility(paths, transmuter);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_TRANSMUTATIONS", "").intValue() == 0, "Transmuter refund");
            controller.addAbility(paths, academia);
            controller.addAbility(paths, astrology);
            require(pc.isClassSkill(nature) && pc.isClassSkill(geography), "Path skills restored");
            require(pc.getAvailableAbilityPool(paths).intValue() == 0, "Two path slots spent");
            if (level == 20) {
                controller.addAbility(masteryCategory, wisdomMastery);
                require(pc.getTotalBonusTo("STAT", "WIS") == 2, "Chosen mental ability bonus");
                controller.removeAbility(paths, academia);
                require(pc.getTotalBonusTo("STAT", "WIS") == 0, "Lost path suppresses mastery effect");
                controller.addAbility(paths, academia);
                require(pc.getTotalBonusTo("STAT", "WIS") == 2, "Restored path restores mastery effect");
            }
            if (reload && level >= 10) {
                require(pc.getConsolidatedAssociationList(builder).equals(java.util.List.of("Potions")), "Saved crafting type");
                require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Craft Potions") == 4, "Saved conditional crafting bonus");
                controller.removeAbility(secrets, builder);
            }
            if (reload && level >= 6) {
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 + 1 - (level >= 10 ? 4 : 3), "Saved secret costs");
                if (level >= 10) {
                    require(pc.getConsolidatedAssociationList(master).equals(java.util.List.of("Extend Spell")), "Saved Metamagic Master target");
                    controller.removeAbility(secrets, master);
                }
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == level, "Saved familiar level");
                require(pc.getAvailableAbilityPool(combat).intValue() == 1, "Saved combat grant");
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Extend Spell"), "Saved bonus feat");
                controller.removeAbility(magic, feat);
                controller.removeAbility(secrets, magical);
                controller.removeAbility(secrets, familiar);
                controller.removeAbility(secrets, training);
            }
            require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 + 1, "Academia bonus secret pool");
            var syzygy = ability(secrets, "Hedgewitch Astrology Syzygy");
            require(syzygy.qualifies(pc, syzygy) == (level >= 10), "Syzygy grand-secret gate");
            if (level >= 10) {
                controller.addAbility(secrets, syzygy);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_ACTIVE_LIMIT", "").intValue() == 2, "Syzygy active aura capacity");
                controller.removeAbility(paths, astrology);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_ACTIVE_LIMIT", "").intValue() == 0, "No active aura capacity without path");
                require(!syzygy.qualifies(pc, syzygy), "Syzygy requires path");
                controller.removeAbility(secrets, syzygy);
                controller.addAbility(paths, astrology);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_ACTIVE_LIMIT", "").intValue() == 1, "Syzygy refund");
            }
            if (level >= 2) {
                var extraAura = ability(secrets, "Hedgewitch Astrology Extra Aura");
                var sun = ability(auras, "Hedgewitch Celestial Aura - Sun");
                controller.addAbility(secrets, extraAura);
                controller.addAbility(auras, sun);
                require(pc.getAvailableAbilityPool(auras).intValue() == 0, "Extra Aura spends new slot");
                controller.removeAbility(auras, sun);
                controller.removeAbility(secrets, extraAura);
                require(pc.getAvailableAbilityPool(auras).intValue() == 0, "Extra Aura refund");
            }
            if (level >= 4) {
                var reach = ability(secrets, "Hedgewitch Astrology Heaven's Reach");
                controller.addAbility(secrets, reach);
                controller.addAbility(secrets, reach);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_RADIUS", "").intValue() == 50, "Repeated aura reach");
                require(!reach.qualifies(pc, reach), "Aura reach limited to twice");
                controller.removeAbility(secrets, reach);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_AURA_RADIUS", "").intValue() == 40, "Partial aura reach refund");
                controller.removeAbility(secrets, reach);
            }
            require(knowledge.qualifies(pc, knowledge) == (level >= 10), "Metamagic Knowledge grand-secret level gate");
            var scholarship = ability(secrets, "Hedgewitch Academia Scholarship");
            double knowledgeBonus = pc.getTotalBonusTo("SKILL", "TYPE.Knowledge");
            controller.addAbility(secrets, scholarship);
            require(pc.getTotalBonusTo("SKILL", "TYPE.Knowledge") == knowledgeBonus + 1 + level / 5, "Scholarship competence progression");
            controller.removeAbility(paths, academia);
            require(pc.getTotalBonusTo("SKILL", "TYPE.Knowledge") == knowledgeBonus, "Scholarship suppressed without path");
            controller.addAbility(paths, academia);
            controller.removeAbility(secrets, scholarship);
            require(pc.getTotalBonusTo("SKILL", "TYPE.Knowledge") == knowledgeBonus, "Scholarship refund");
            controller.addAbility(secrets, extraPoints);
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == loadedPoints + 2, "Academia secret spell points");
            if (level >= 2) {
                controller.addAbility(secrets, extraPoints);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == loadedPoints + 4, "Repeated Academia secret");
                controller.removeAbility(secrets, extraPoints);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == loadedPoints + 2, "Partial spell point refund");
            }
            controller.removeAbility(secrets, extraPoints);
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == loadedPoints, "Spell point secret refund");
            require(training.qualifies(pc, training), "Academia secret available at first level");
            if (level == 1) {
                controller.addAbility(secrets, training);
                require(pc.getAvailableAbilityPool(secrets).intValue() == 0, "First-level secret spend");
                require(pc.getAvailableAbilityPool(combat).intValue() == 1, "First-level secret grant");
                controller.removeAbility(secrets, training);
                controller.addAbility(secrets, extraPoints);
            }
            var feats = game.getAbilityCategory("FEAT");
            var extra = ability(feats, "Extra Secret");
            require(extra.qualifies(pc, extra) == (level >= 2), "Extra Secret feature gate");
            if (level >= 2) {
                controller.addAbility(feats, extra);
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 + 2, "Extra Secret grant");
                controller.addAbility(feats, extra);
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 + 3, "Repeated Extra Secret");
                controller.removeAbility(feats, extra);
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 + 2, "Partial Extra Secret refund");
                controller.removeAbility(feats, extra);
            }
            require(ability(secrets, "Hedgewitch Arcane Builder").qualifies(pc, pc) == (level >= 10), "Grand secret level boundary");
            require(!master.qualifies(pc, master), "Master requires an owned metamagic feat");
            if (level >= 2) {
                controller.addAbility(secrets, training);
                require(pc.getAvailableAbilityPool(combat).intValue() == 1, "Combat grant");
                if (level >= 4) {
                    controller.addAbility(secrets, training);
                    require(pc.getAvailableAbilityPool(combat).intValue() == 2, "Repeated combat grant");
                    controller.removeAbility(secrets, training);
                    require(pc.getAvailableAbilityPool(combat).intValue() == 1, "Partial combat refund");
                }
                controller.removeAbility(secrets, training);
                require(pc.getAvailableAbilityPool(combat).intValue() == 0, "Combat refund");
                controller.addAbility(secrets, magical);
                require(pc.getAvailableAbilityPool(magic).intValue() == 1, "Magical Skill feat slot");
                controller.addAbility(magic, feat);
                require(pc.getAvailableAbilityPool(magic).intValue() == 0, "Magical Skill feat spend");
                require(master.qualifies(pc, master) == (level >= 10), "Master level and metamagic requirements");
                if (level >= 10) {
                    double ordinary = pc.getTotalBonusTo("SKILL", "Spellcraft");
                    messages.target = "Potions";
                    controller.addAbility(secrets, builder);
                    require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Craft Potions") == 4, "Selected crafting bonus");
                    require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Craft Wands") == 0, "Unselected crafting excluded");
                    require(pc.getTotalBonusTo("SKILL", "Spellcraft") == ordinary, "No unconditional Spellcraft bonus");
                    messages.target = "Wands";
                    messages.addingRepeat = true;
                    controller.addAbility(secrets, builder);
                    messages.addingRepeat = false;
                    require(pc.getConsolidatedAssociationList(builder).size() == 2, "Distinct repeated crafting choices");
                    require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Craft Wands") == 4, "Second crafting type");
                    controller.removeAbility(secrets, builder);
                    require(pc.getConsolidatedAssociationList(builder).size() == 1, "Partial crafting choice refund");
                    controller.removeAbility(secrets, builder);
                    require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Craft Potions") == 0, "Crafting refund");
                    messages.target = "Extend Spell";
                    controller.addAbility(secrets, master);
                    require(pc.getConsolidatedAssociationList(master).equals(java.util.List.of("Extend Spell")), "Owned metamagic selected");
                    controller.removeAbility(magic, feat);
                    require(!master.qualifies(pc, master), "Removing metamagic revokes Master qualification");
                    controller.removeAbility(secrets, master);
                    controller.addAbility(magic, feat);
                }
                controller.removeAbility(magic, feat);
                controller.removeAbility(secrets, magical);
                require(pc.getAvailableAbilityPool(magic).intValue() == 0, "Magical Skill refund");
                var championSecret = ability(secrets, "Hedgewitch Champion");
                controller.addAbility(secrets, championSecret);
                require(pc.getAvailableAbilityPool(champion).intValue() == 1, "Champion feat slot");
                controller.removeAbility(secrets, championSecret);
                require(pc.getAvailableAbilityPool(champion).intValue() == 0, "Champion refund");
                controller.addAbility(secrets, familiar);
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == level, "Familiar level");
                controller.removeAbility(secrets, familiar);
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == 0, "Familiar refund");
                if (level >= 6) {
                    controller.addAbility(secrets, familiar);
                    controller.addAbility(secrets, training);
                    controller.addAbility(secrets, magical);
                    controller.addAbility(magic, feat);
                    if (level >= 10) {
                        controller.addAbility(secrets, master);
                        messages.target = "Potions";
                        controller.addAbility(secrets, builder);
                    }
                }
            }
            if (level >= 12) {
                controller.addAbility(secrets, knowledge);
                controller.addAbility(metamagicCategory, silent);
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Silent Spell"), "Metamagic Knowledge feat grant");
            }
            require(messages.errors.isEmpty(), "Unexpected errors: " + messages.errors);
        } finally {
            ChooserFactory.setDelegate(oldDelegate);
            controller.closeCharacter();
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}