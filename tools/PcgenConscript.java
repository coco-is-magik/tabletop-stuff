package pcgen.gui2.facade;

import java.nio.file.Path;
import java.util.List;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Class accounting only; manual talent records deliberately do not evaluate spheres. */
class PcgenConscript {
    public static void main(String[] args) throws Exception {
        require(args.length == 6, "character template output config gate save required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var specs = game.getAbilityCategory("Conscript Specialization");
        var bonus = game.getAbilityCategory("Conscript Bonus Feat");
        var talents = game.getAbilityCategory("Spheres Combat Talent");
        var mental = game.getAbilityCategory("Conscript Practitioner Ability");
        var special = game.getAbilityCategory("Special Ability");
        var internal = game.getAbilityCategory("Internal");
        int level = pc.getTotalLevels();
        int points = pc.getVariableValue("SPHERES_CONSCRIPT_SPECIALIZATION_POINTS", "").intValue();
        int[][] lost = {{}, {1, 10, 20}, {1, 6, 10, 14, 20}, {1, 2, 6, 10, 14, 18, 20},
                {1, 2, 6, 8, 10, 14, 16, 18, 20}, {1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20}};
        int feats = 1 + level / 2;
        for (int threshold : lost[points]) if (level >= threshold) feats--;
        require(pc.getVariableValue("SPHERES_CONSCRIPT_LEVEL", "").intValue() == level, "Class level");
        require(pc.getTotalAbilityPool(bonus).intValue() == feats, "Forfeiture table");
        require(pc.getAvailableAbilityPool(specs).intValue() == 5 - points, "Purchase budget");
        require(pc.getVariableValue("SPHERES_PRACTITIONER_MOD", "").intValue() == 4, "Practitioner choice");
        require(pc.getVariableValue("SPHERES_PRACTITIONER_DC", "").intValue() == 14 + level / 2, "Practitioner DC");
        require(pc.getAvailableAbilityPool(mental).intValue() == 0, "Mental choice spending");
        require(pc.getAvailableAbilityPool(game.getAbilityCategory("Conscript Class Skill")).intValue() == 0, "Three class skills");
        require(pc.getAvailableAbilityPool(game.getAbilityCategory("Conscript Martial Tradition")).intValue() == 0, "Tradition record");
        for (String skillName : List.of("Acrobatics", "Stealth", "Bluff")) {
            var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, skillName);
            require(pc.isClassSkill(skill), "Additional class skill not applied: " + skillName);
        }
        require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == 0, "Conscript gained magic talents");
        require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 0, "Conscript gained spell points");
        boolean gear = pc.hasAbilityKeyed(specs, "Conscript Gear Training");
        require(pc.hasAbilityKeyed(internal, "Weapon Prof ~ Martial") == gear, "Martial proficiency grant");
        require(pc.hasAbilityKeyed(internal, "Armor Prof ~ Heavy") == (gear && level >= 6), "Heavy armor level gate");
        boolean evasion = pc.hasAbilityKeyed(specs, "Conscript Evasion");
        require(pc.hasAbilityKeyed(special, "Evasion") == (evasion && level >= 3), "Evasion gate");
        require(pc.hasAbilityKeyed(special, "Improved Evasion") == (evasion && level >= 10), "Improved evasion gate");
        int speed = pc.hasAbilityKeyed(specs, "Conscript Fast Movement") && level >= 3 ? 10 * (1 + (level - 1) / 5) : 0;
        require(pc.getVariableValue("SPHERES_CONSCRIPT_SPEED", "").intValue() == speed, "Fast movement progression");
        for (String name : List.of("Banner", "Inspiration", "Armor Training", "Resolve", "Sneak Attack", "Studied Target")) {
            if (!pc.hasAbilityKeyed(specs, "Conscript " + name)) continue;
            String variable;
            int value;
            switch (name) {
                case "Banner": variable = "SPHERES_CONSCRIPT_BANNER"; value = level < 2 ? 0 : 1 + (level - 2) / 4; break;
                case "Inspiration": variable = "SPHERES_CONSCRIPT_INSPIRATION"; value = level / 2; break;
                case "Armor Training": variable = "SPHERES_CONSCRIPT_ARMOR"; value = level < 3 ? 0 : 1 + (level - 2) / 4; break;
                case "Resolve": variable = "SPHERES_CONSCRIPT_RESOLVE"; value = (level + 1) / 2; break;
                case "Sneak Attack": variable = "SneakAttackDice"; value = level / 3; break;
                default: variable = "SPHERES_CONSCRIPT_STUDIED"; value = 1 + level / 8;
            }
            require(pc.getVariableValue(variable, "").intValue() == value, name + " resource progression");
        }
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("conscript-reload");
        try {
            var favored = game.getAbilityCategory("Favored Class");
            var rewards = game.getAbilityCategory("Favored Class Bonus");
            var favoredPool = pc.getTotalAbilityPool(rewards);
            var favoredConscript = ability(favored, "Conscript");
            controller.addAbility(favored, favoredConscript);
            require(messages.errors.isEmpty(), "Cannot favor Conscript");
            require(pc.getTotalAbilityPool(rewards).intValue() == favoredPool.intValue() + level, "Favored rewards progression");
            controller.removeAbility(favored, favoredConscript);
            require(pc.getTotalAbilityPool(rewards).equals(favoredPool), "Favored rewards refund");
            var extra = ability(AbilityCategory.FEAT, "Extra Combat Talent");
            int count = Math.min(2, feats);
            var normalFeats = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
            if (!reload) {
                for (int i = 0; i < count; i++) controller.addAbility(bonus, extra);
                require(messages.errors.isEmpty(), "Bonus feat selection failed");
                var otherMental = ability(mental, pc.hasAbilityKeyed(mental, "Wisdom Practitioner") ? "Intelligence Practitioner" : "Wisdom Practitioner");
                rejected(controller, messages, mental, otherMental, "InfoAbility.Messages.NoPoints");
                if (points == 5) rejected(controller, messages, specs, ability(specs, "Conscript Banner"),
                        level == 1 ? "InfoAbility.Messages.NoPoints" : "InfoAbility.Messages.NotQualified");
                if (gear) rejected(controller, messages, specs, ability(specs, "Conscript Gear Training"),
                        "InfoAbility.Messages.Duplicate");
            }
            require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(normalFeats), "Normal feat pool changed");
            require(pc.getTotalAbilityPool(talents).intValue() == level + (level + 1) / 2 + count, "Talent progression/extra feat");
            require(pc.getAvailableAbilityPool(talents).intValue() == level + (level + 1) / 2 + count - 1, "Manual talent not spent/restored");
            require(pc.getAvailableAbilityPool(bonus).intValue() == feats - count, "Bonus feat spending");
            if (reload) {
                for (int i = 0; i < count; i++) controller.removeAbility(bonus, extra);
                for (String name : List.of("Gear Training", "Fast Movement", "Indomitable Will", "Evasion",
                        "Banner", "Inspiration", "Armor Training", "Resolve", "Sneak Attack", "Studied Target")) {
                    if (pc.hasAbilityKeyed(specs, "Conscript " + name)) controller.removeAbility(specs, ability(specs, "Conscript " + name));
                }
                require(pc.getAvailableAbilityPool(specs).intValue() == 5, "Specialization refund");
                require(pc.getAvailableAbilityPool(bonus).intValue() == 1 + level / 2, "Feat refund");
                require(pc.getTotalAbilityPool(talents).intValue() == level + (level + 1) / 2, "Talent refund");
                require(pc.getVariableValue("SPHERES_CONSCRIPT_SPEED", "").intValue() == 0, "Speed removal");
                require(!pc.hasAbilityKeyed(special, "Evasion"), "Evasion removal");
                require(!pc.hasAbilityKeyed(internal, "Weapon Prof ~ Martial"), "Gear removal");
                for (String variable : List.of("SPHERES_CONSCRIPT_BANNER", "SPHERES_CONSCRIPT_INSPIRATION",
                        "SPHERES_CONSCRIPT_ARMOR", "SPHERES_CONSCRIPT_RESOLVE", "SPHERES_CONSCRIPT_STUDIED", "SneakAttackDice")) {
                    require(pc.getVariableValue(variable, "").intValue() == 0, "Removed feature retained " + variable);
                }
            }
        } finally {
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