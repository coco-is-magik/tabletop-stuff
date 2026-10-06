package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Spell Dabbler uses the normal feat prerequisites and three bounded slots. */
class PcgenSpellDabbler {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var feats = game.getAbilityCategory("FEAT");
        var prowess = game.getAbilityCategory("Armiger Prowess");
        var choices = game.getAbilityCategory("Armiger Spell Dabbler Feat");
        var dabbler = ability(prowess, "Armiger Spell Dabbler");
        var basic = ability(feats, "Basic Magic Training");
        var advanced = ability(feats, "Advanced Magic Training");
        var extra = ability(feats, "Extra Magic Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].endsWith("reload");
        try {
            if (reload) {
                require(pc.hasAbilityKeyed(feats, "Basic Magic Training") && pc.hasAbilityKeyed(feats, "Advanced Magic Training"), "Saved training feats");
                require(pc.getAvailableAbilityPool(choices).intValue() == 0, "Saved feat slot cost");
                controller.removeAbility(choices, extra);
                controller.removeAbility(choices, advanced);
                controller.removeAbility(choices, basic);
                for (int i = 0; i < 3; i++) controller.removeAbility(prowess, dabbler);
            }
            require(!advanced.qualifies(pc, advanced) && !extra.qualifies(pc, extra), "Casting prerequisites not waived");
            for (int i = 1; i <= 3; i++) {
                controller.addAbility(prowess, dabbler);
                require(pc.getAvailableAbilityPool(choices).intValue() == i, "Repeated dabbler slots");
            }
            require(!dabbler.qualifies(pc, dabbler), "Three-selection cap");
            controller.addAbility(choices, basic);
            require(advanced.qualifies(pc, advanced) && extra.qualifies(pc, extra), "Basic Training unlocks legal follow-ups");
            controller.addAbility(choices, advanced);
            var talents = game.getAbilityCategory("Spheres Magic Talent");
            var before = pc.getAvailableAbilityPool(talents);
            controller.addAbility(choices, extra);
            require(pc.getAvailableAbilityPool(talents).intValue() == before.intValue() + 1, "Actual extra talent grant");
            require(pc.getAvailableAbilityPool(choices).intValue() == 0, "Three feats spend three slots");
            controller.removeAbility(prowess, dabbler);
            require(pc.getAvailableAbilityPool(choices).intValue() == -1, "Dependent feat stays visibly overspent");
            controller.addAbility(prowess, dabbler);
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