package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Both feature sources are required; either class can pay for the bonus feat. */
class PcgenCustomizedBond {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var feats = game.getAbilityCategory("FEAT");
        var bond = ability(feats, "Customized Bond");
        var arsenal = game.getAbilityCategory("Armorist Arsenal Trick");
        var prowess = game.getAbilityCategory("Armiger Prowess");
        var armorist = ability(arsenal, "Armorist Customized Bond");
        var armiger = ability(prowess, "Armiger Customized Bond");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].endsWith("reload");
        boolean mixed = pc.getClassKeyed("Armorist") != null && pc.getClassKeyed("Armiger") != null;
        try {
            require(bond.qualifies(pc, bond) == mixed, "Both equipment feature sources required");
            if (mixed) {
                if (reload) {
                    require(pc.hasAbilityKeyed(feats, "Customized Bond"), "Saved automatic bond feat");
                    require(pc.hasAbilityKeyed(prowess, armiger.getKeyName()), "Saved prowess selection");
                    controller.removeAbility(prowess, armiger);
                    require(!pc.hasAbilityKeyed(feats, "Customized Bond"), "Saved source refund");
                }
                var before = pc.getAvailableAbilityPool(arsenal);
                controller.addAbility(arsenal, armorist);
                require(pc.hasAbilityKeyed(feats, "Customized Bond"), "Arsenal grants feat");
                controller.removeAbility(arsenal, armorist);
                require(!pc.hasAbilityKeyed(feats, "Customized Bond"), "Arsenal refund");
                require(pc.getAvailableAbilityPool(arsenal).equals(before), "Arsenal slot restored");
                controller.addAbility(prowess, armiger);
                require(pc.hasAbilityKeyed(feats, "Customized Bond"), "Prowess grants feat");
            } else {
                require(!armorist.qualifies(pc, armorist) && !armiger.qualifies(pc, armiger), "Single-class options blocked");
            }
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