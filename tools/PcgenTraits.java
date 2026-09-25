package pcgen.gui2.facade;

import java.math.BigDecimal;
import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Shared Pathfinder trait pool and Spheres trait selection/reload gate. */
class PcgenTraits {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var traits = game.getAbilityCategory("Traits");
        require(traits != null, "Core trait category missing");
        var combat = ability(traits, "Spheres Trait ~ Maneuver Trained");
        var second = ability(traits, "Spheres Trait ~ Steel Body");
        var magic = ability(traits, "Spheres Trait ~ Chronosense");
        var drawback = ability(traits, "Spheres Trait ~ Abrasive");
        var otherDrawback = ability(traits, "Spheres Trait ~ Snobby");
        boolean reload = args[4].equals("traits-reload");
        try {
            if (reload) {
                require(controller.getAbilities(traits).getSize() == 2, "Traits not saved");
                controller.removeAbility(traits, combat);
                controller.removeAbility(traits, magic);
            }
            var pool = pc.getAvailableAbilityPool(traits);
            controller.addAbility(traits, drawback);
            require(pc.getAvailableAbilityPool(traits).equals(pool.add(BigDecimal.ONE)), "Drawback net trait pool");
            require(!otherDrawback.qualifies(pc, otherDrawback), "Second drawback qualified");
            rejected(controller, messages, traits, otherDrawback, "InfoAbility.Messages.NotQualified");
            controller.removeAbility(traits, drawback);
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Drawback removal/refund");
            require(combat.qualifies(pc, combat), "Combat trait not qualified");
            controller.addAbility(traits, combat);
            require(controller.getAbilities(traits).getSize() == 1, "Combat trait not selected: " + messages.errors);
            require(pc.getAvailableAbilityPool(traits).equals(pool.subtract(BigDecimal.ONE)), "Shared trait pool not spent");
            require(!second.qualifies(pc, second), "Duplicate combat category qualified");
            rejected(controller, messages, traits, second, "InfoAbility.Messages.NotQualified");
            controller.addAbility(traits, magic);
            require(controller.getAbilities(traits).getSize() == 2, "Magic trait not selected: " + messages.errors);
            controller.removeAbility(traits, magic);
            controller.removeAbility(traits, combat);
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Trait pool refund");
            controller.addAbility(traits, combat);
            controller.addAbility(traits, magic);
            require(messages.errors.size() == 2, "Unexpected errors: " + messages.errors);
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