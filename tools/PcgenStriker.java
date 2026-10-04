package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Tension capacities and level-limited repeated arts, not current combat tension. */
class PcgenStriker {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Striker Striker Art");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_STRIKER_LEVEL", "").intValue();
        int cap = level < 5 ? 0 : 1 + (level - 5) / 6;
        boolean reload = args[4].equals("striker-reload");
        int constitution = pc.getVariableValue("CON", "").intValue();
        try {
            var combatTalents = gameCategory("Spheres Combat Talent");
            var armored = ability(cat, "Striker Armored Striker");
            var armoredPool = pc.getAvailableAbilityPool(cat);
            int repeats = Math.min(2, armoredPool.intValue());
            for (int i = 1; i <= repeats; i++) {
                controller.addAbility(cat, armored);
                require(pc.getVariableValue("SPHERES_STRIKER_ARMORED_COUNT", "").intValue() == i,
                    "Armored Striker repeat count");
            }
            if (repeats == 2) {
                rejected(controller, messages, cat, armored, "InfoAbility.Messages.NotQualified");
            }
            for (int i = repeats - 1; i >= 0; i--) {
                controller.removeAbility(cat, armored);
                require(pc.getVariableValue("SPHERES_STRIKER_ARMORED_COUNT", "").intValue() == i,
                    "Armored Striker partial refund");
            }
            require(pc.getAvailableAbilityPool(cat).equals(armoredPool), "Armored Striker full refund");
            var unarmored = ability(cat, "Striker Unarmored Striker");
            if (reload) {
                require(pc.hasAbilityKeyed(cat, unarmored.getKeyName()), "Unarmored Striker persistence");
                require(pc.hasAbilityKeyed(combatTalents, "Equipment - Unarmored Training"),
                    "Granted Unarmored Training persistence");
                controller.removeAbility(cat, unarmored);
            }
            var talentPool = pc.getAvailableAbilityPool(combatTalents);
            var artPool = pc.getAvailableAbilityPool(cat);
            boolean hadEquipment = pc.hasAbilityKeyed(combatTalents, "Equipment Sphere");
            controller.addAbility(cat, unarmored);
            require(pc.hasAbilityKeyed(combatTalents, "Equipment - Unarmored Training"),
                "Unarmored Striker grants its talent");
            require(pc.hasAbilityKeyed(combatTalents, "Equipment Sphere") == hadEquipment,
                "Unarmored Striker does not grant the Equipment sphere");
            require(pc.getAvailableAbilityPool(combatTalents).equals(talentPool),
                "Granted talent does not spend a combat talent");
            controller.removeAbility(cat, unarmored);
            require(!pc.hasAbilityKeyed(combatTalents, "Equipment - Unarmored Training"),
                "Unarmored Striker talent removal");
            require(pc.getAvailableAbilityPool(cat).equals(artPool), "Unarmored Striker art refund");
            var training = gameCategory("Striker Tension Training");
            var critical = ability(training, "Striker Training - Critical Offense");
            if (reload && level >= 5) {
                require(pc.hasAbilityKeyed(training, critical.getKeyName()), "Training persistence");
                controller.removeAbility(training, critical);
            }
            require(pc.getAvailableAbilityPool(training).intValue() == cap, "Training pool progression");
            if (level >= 5) {
                controller.addAbility(training, critical);
                require(pc.hasAbilityKeyed(training, critical.getKeyName()), "Training selection");
                controller.removeAbility(training, critical);
                require(pc.getAvailableAbilityPool(training).intValue() == cap, "Training refund");
            } else {
                rejected(controller, messages, training, critical, "InfoAbility.Messages.NotQualified");
            }
            require(pc.getVariableValue("SPHERES_STRIKER_UNLIMITED_TENSION", "").intValue() == (level >= 20 ? 1 : 0), "Unlimited tension gate");
            require(pc.getVariableValue("SPHERES_STRIKER_RISING_TENSION", "").intValue() == (level < 10 ? 0 : level < 16 ? 1 : 2), "Rising tension");
            var special = gameCategory("Special Ability");
            require(pc.hasAbilityKeyed(special, "Uncanny Dodge") == (level >= 3), "Uncanny Dodge level gate");
            require(pc.hasAbilityKeyed(special, "Improved Uncanny Dodge") == (level >= 12), "Improved Uncanny Dodge level gate");
            if (level >= 12) {
                require(pc.getVariableValue("UncannyDodgeFlankingLevel", "").intValue() == level + 4, "Flanking level");
            }
            for (String[] test : new String[][] {{"High Tension", "MAX_TENSION"}, {"Extra Boost", "TENSION_BOOST"}}) {
                var art = ability(cat, "Striker " + test[0] + " (Requires Striker 5)");
                String variable = "SPHERES_STRIKER_" + test[1];
                int base = test[0].equals("High Tension") ? Math.max(1, constitution) + level / 3 : 1 + (level - 1) / 6;
                if (level >= 20) base = test[0].equals("High Tension") ? 0 : 7;
                int increment = level >= 20 ? 0 : 1;
                if (reload && cap > 0) {
                    require(pc.getVariableValue(variable, "").intValue() == base + increment, "Saved capacity " + variable);
                    controller.removeAbility(cat, art);
                }
                require(pc.getVariableValue(variable, "").intValue() == base, "Base capacity " + variable);
                var pool = pc.getAvailableAbilityPool(cat);
                for (int i = 1; i <= cap; i++) {
                    controller.addAbility(cat, art);
                    require(pc.getVariableValue(variable, "").intValue() == base + i * increment, "Repeated grant " + variable);
                }
                rejected(controller, messages, cat, art, "InfoAbility.Messages.NotQualified");
                for (int i = cap - 1; i >= 0; i--) {
                    controller.removeAbility(cat, art);
                    require(pc.getVariableValue(variable, "").intValue() == base + i * increment, "Partial refund " + variable);
                }
                require(pc.getAvailableAbilityPool(cat).equals(pool), "Repeated art full refund");
            }
            var iron = ability(cat, "Striker Iron Soul");
            var steel = ability(cat, "Striker Steel Heart (Requires Iron Soul)");
            rejected(controller, messages, cat, steel, "InfoAbility.Messages.NotQualified");
            controller.addAbility(cat, iron);
            require(steel.qualifies(pc, steel), "Iron Soul prerequisite");
            controller.removeAbility(cat, iron);
            require(!steel.qualifies(pc, steel), "Lost Iron Soul prerequisite");
            var trueDesperation = ability(cat, "Striker True Desperation (Requires Striker 8)");
            int desperate = level >= 4 ? 1 : 0;
            require(pc.getVariableValue("SPHERES_STRIKER_DESPERATE_TENSION", "").intValue() == desperate, "Base desperate tension");
            if (level >= 8) {
                controller.addAbility(cat, trueDesperation);
                require(pc.getVariableValue("SPHERES_STRIKER_DESPERATE_TENSION", "").intValue() == 2, "True Desperation");
                controller.removeAbility(cat, trueDesperation);
            } else {
                rejected(controller, messages, cat, trueDesperation, "InfoAbility.Messages.NotQualified");
            }
            controller.addAbility(cat, unarmored);
            if (cap > 0) {
                controller.addAbility(training, critical);
                controller.addAbility(cat, ability(cat, "Striker High Tension (Requires Striker 5)"));
                controller.addAbility(cat, ability(cat, "Striker Extra Boost (Requires Striker 5)"));
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

    private static pcgen.core.AbilityCategory gameCategory(String name) {
        return SettingsHandler.getGameAsProperty().get().getAbilityCategory(name);
    }
}