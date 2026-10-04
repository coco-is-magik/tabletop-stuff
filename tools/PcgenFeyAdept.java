package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Shadow feat stacking, refunds, prerequisite rejection and retained selections. */
class PcgenFeyAdept {
    private static int value(pcgen.core.PlayerCharacter pc, String suffix) {
        return pc.getVariableValue("SPHERES_FEY_ADEPT_" + suffix, "").intValue();
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var feats = AbilityCategory.FEAT;
        var extra = ability(feats, "Extra Shadowstuff");
        var greater = ability(feats, "Greater Shadowmark");
        boolean reload = args[4].equals("fey-reload");
        boolean fey = pc.getClassKeyed("Fey Adept") != null;
        int baseline = Math.max(1, pc.getVariableValue("CHA", "").intValue() + value(pc, "LEVEL") / 2);
        try {
            if (!fey) {
                rejected(controller, messages, feats, extra, "InfoAbility.Messages.NotQualified");
                rejected(controller, messages, feats, greater, "InfoAbility.Messages.NotQualified");
            } else {
                if (reload) {
                    require(pc.hasAbilityKeyed(feats, extra.getKeyName()), "Extra Shadowstuff persistence");
                    require(pc.hasAbilityKeyed(feats, greater.getKeyName()), "Greater Shadowmark persistence");
                    require(value(pc, "SHADOW_POINTS") == baseline + 4, "Both repeat grants persisted");
                    require(value(pc, "SHADOWMARK_DIE_SIZE") == 8, "d8 persisted");
                    controller.removeAbility(feats, extra);
                    require(value(pc, "SHADOW_POINTS") == baseline + 2, "Partial repeat refund on reload");
                    controller.removeAbility(feats, extra);
                    controller.removeAbility(feats, greater);
                }
                var pool = pc.getAvailableAbilityPool(feats);
                int spellPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                int dice = value(pc, "SHADOWMARK_DICE");
                require(value(pc, "SHADOW_POINTS") == baseline, "Baseline shadow points");
                require(value(pc, "SHADOWMARK_DIE_SIZE") == 6, "Baseline d6");
                for (int count = 1; count <= 2; count++) {
                    controller.addAbility(feats, extra);
                    require(value(pc, "SHADOW_POINTS") == baseline + 2 * count, "Stacked shadow points");
                }
                controller.addAbility(feats, greater);
                require(value(pc, "SHADOWMARK_DIE_SIZE") == 8, "Greater Shadowmark d8");
                require(value(pc, "SHADOWMARK_DICE") == dice, "Greater Shadowmark must not change dice count");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == spellPoints,
                    "Shadow points are not spell points");
                rejected(controller, messages, feats, greater, "InfoAbility.Messages.Duplicate");
                controller.removeAbility(feats, greater);
                require(value(pc, "SHADOWMARK_DIE_SIZE") == 6, "Die size refund");
                controller.removeAbility(feats, extra);
                require(value(pc, "SHADOW_POINTS") == baseline + 2, "Partial shadow refund");
                controller.removeAbility(feats, extra);
                require(value(pc, "SHADOW_POINTS") == baseline, "Full shadow refund");
                require(pc.getAvailableAbilityPool(feats).equals(pool), "Feat pool refund");
                controller.addAbility(feats, extra);
                controller.addAbility(feats, extra);
                controller.addAbility(feats, greater);
            }
            require(messages.errors.size() == (fey ? 1 : 2), "Unexpected errors: " + messages.errors);
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