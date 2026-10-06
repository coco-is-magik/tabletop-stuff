package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Level-dependent feat caps and real option-slot persistence. */
class PcgenExtraOptions {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var feats = game.getAbilityCategory("FEAT");
        var option = game.getAbilityCategory(args[7]);
        var feat = ability(feats, args[6]);
        int cap = Integer.parseInt(args[8]);
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].endsWith("reload");
        try {
            if (reload) {
                require(pc.getVariableValue(args[9], "").intValue() == cap, "Saved extra-option count");
                var pool = pc.getAvailableAbilityPool(option);
                for (int i = 1; i <= cap; i++) {
                    controller.removeAbility(feats, feat);
                    require(pc.getAvailableAbilityPool(option).intValue() == pool.intValue() - i, "Saved partial slot refund");
                }
            }
            var before = pc.getAvailableAbilityPool(option);
            for (int i = 1; i <= cap; i++) {
                controller.addAbility(feats, feat);
                require(pc.getVariableValue(args[9], "").intValue() == i, "Repeated extra feat");
                require(pc.getAvailableAbilityPool(option).intValue() == before.intValue() + i, "One real option slot per feat");
            }
            rejected(controller, messages, feats, feat, "InfoAbility.Messages.NotQualified");
            messages.errors.clear();
            for (int i = cap - 1; i >= 0; i--) {
                controller.removeAbility(feats, feat);
                require(pc.getAvailableAbilityPool(option).intValue() == before.intValue() + i, "Partial slot refund");
            }
            for (int i = 0; i < cap; i++) controller.addAbility(feats, feat);
            require(messages.errors.isEmpty(), "Unexpected errors: " + messages.errors);
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