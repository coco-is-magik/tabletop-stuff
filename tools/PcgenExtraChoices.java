package pcgen.gui2.facade;

import java.math.BigDecimal;
import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Repeated class-choice feats use existing pools, not bypassed option prerequisites. */
class PcgenExtraChoices {
    private static void resources(pcgen.core.PlayerCharacter pc, CharacterAbilities controller,
                                  Messages messages, String owner, boolean reload) {
        boolean symbiat = owner.equals("symbiat");
        var extra = ability(AbilityCategory.FEAT, symbiat ? "Extra Psionics" : "Extra Invocations");
        var wrong = ability(AbilityCategory.FEAT, symbiat ? "Extra Invocations" : "Extra Psionics");
        String variable = symbiat ? "SPHERES_SYMBIAT_PSIONICS_ROUNDS" : "SPHERES_THAUMATURGE_INVOCATION_USES";
        int increment = symbiat ? 6 : 2;
        int level = pc.getVariableValue("SPHERES_" + owner.toUpperCase() + "_LEVEL", "").intValue();
        int base = symbiat ? 4 + pc.getVariableValue("INT", "").intValue() + 2 * (level - 1)
                          : pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue() + level / 2;
        rejected(controller, messages, AbilityCategory.FEAT, wrong, "InfoAbility.Messages.NotQualified");
        if (reload) {
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, extra.getKeyName()), "Resource feat persistence");
            require(pc.getVariableValue(variable, "").intValue() == base + 2 * increment, "Repeated resource persistence");
            controller.removeAbility(AbilityCategory.FEAT, extra);
            controller.removeAbility(AbilityCategory.FEAT, extra);
        }
        var budget = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
        require(pc.getVariableValue(variable, "").intValue() == base, "Base class resource");
        for (int i = 1; i <= 2; i++) {
            controller.addAbility(AbilityCategory.FEAT, extra);
            require(pc.getVariableValue(variable, "").intValue() == base + i * increment, "Repeated resource grant");
            require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(budget.subtract(BigDecimal.valueOf(i))), "Resource feat cost");
        }
        for (int i = 1; i >= 0; i--) {
            controller.removeAbility(AbilityCategory.FEAT, extra);
            require(pc.getVariableValue(variable, "").intValue() == base + i * increment, "Partial resource refund");
        }
        require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(budget), "Resource feat refund");
        controller.addAbility(AbilityCategory.FEAT, extra);
        controller.addAbility(AbilityCategory.FEAT, extra);
        require(messages.errors.size() == 1, "Unexpected resource feat errors: " + messages.errors);
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        String owner = "Mageknight";
        String feature = "Mystic Combat";
        int level = pc.getVariableValue("SPHERES_" + owner.toUpperCase() + "_LEVEL", "").intValue();
        var pool = game.getAbilityCategory(owner + " " + feature);
        var extra = ability(AbilityCategory.FEAT, "Extra " + feature);
        var wrong = ability(AbilityCategory.FEAT, "Extra Arsenal Trick");
        var option = ability(pool, owner + " Combat Talent");
        boolean reload = args[4].equals("extrachoices-reload");
        try {
            if (!args[6].equals("mageknight")) {
                resources(pc, controller, messages, args[6], reload);
            } else {
            require(!wrong.qualifies(pc, wrong), "Wrong class must not qualify");
            rejected(controller, messages, AbilityCategory.FEAT, wrong, "InfoAbility.Messages.NotQualified");
            require(extra.qualifies(pc, extra) == (level >= 2), "Class feature level boundary");
            if (level < 2) {
                rejected(controller, messages, AbilityCategory.FEAT, extra, "InfoAbility.Messages.NotQualified");
            } else {
                if (reload) {
                    require(pc.hasAbilityKeyed(AbilityCategory.FEAT, extra.getKeyName()), "Extra feat persistence");
                    require(pc.getAvailableAbilityPool(pool).intValue() == level / 2 + 2, "Repeated pool grant persistence");
                    controller.removeAbility(AbilityCategory.FEAT, extra);
                    controller.removeAbility(AbilityCategory.FEAT, extra);
                }
                var before = pc.getAvailableAbilityPool(pool);
                var featsBefore = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
                for (int i = 1; i <= 2; i++) {
                    controller.addAbility(AbilityCategory.FEAT, extra);
                    require(pc.getAvailableAbilityPool(pool).equals(before.add(BigDecimal.valueOf(i))), "Repeated choice grant");
                    require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(featsBefore.subtract(BigDecimal.valueOf(i))), "Feat cost");
                }
                controller.addAbility(pool, option);
                require(pc.hasAbilityKeyed(pool, option.getKeyName()), "Granted pool permits normal option purchase");
                require(pc.getAvailableAbilityPool(pool).equals(before.add(BigDecimal.ONE)), "Option spends granted pool");
                controller.removeAbility(pool, option);
                for (int i = 1; i >= 0; i--) {
                    controller.removeAbility(AbilityCategory.FEAT, extra);
                    require(pc.getAvailableAbilityPool(pool).equals(before.add(BigDecimal.valueOf(i))), "Partial choice refund");
                }
                require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(featsBefore), "Feat refund");
                controller.addAbility(AbilityCategory.FEAT, extra);
                controller.addAbility(AbilityCategory.FEAT, extra);
            }
            require(messages.errors.size() == (level < 2 ? 2 : 1), "Unexpected errors: " + messages.errors);
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