package pcgen.gui2.facade;

import java.nio.file.Files;
import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Reference-variable arithmetic through PCGen's production controller. */
class PcgenCatalogVariables {
    private static void assertValue(pcgen.core.PlayerCharacter pc, pcgen.core.AbilityCategory cat, String[] fields) {
        int actual = pc.getVariableValue(fields[2], "").intValue();
        require(actual == Integer.parseInt(fields[3]),
                fields[1] + " " + fields[2] + ": expected " + fields[3] + " got " + actual
                + " (granted=" + pc.hasAbilityKeyed(cat, fields[1]) + ")");
    }

    public static void main(String[] args) throws Exception {
        require(args.length == 8, "character template output config gate saved cases category required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory(args[7]);
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var cases = Files.readAllLines(Path.of(args[6]));
        boolean reload = args[4].endsWith("reload");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var first = cases.get(0).split("\t");
        try {
            if (reload) {
                // Only the first case is retained across save/reload.
                require(pc.hasAbilityKeyed(cat, ability(cat, first[1]).getKeyName()),
                        "Talent lost on reload: " + first[1]);
                assertValue(pc, cat, first);
                controller.removeAbility(cat, ability(cat, first[1]));
                controller.removeAbility(cat, ability(cat, first[0]));
                require(pc.getAvailableAbilityPool(magic).equals(pc.getTotalAbilityPool(magic)),
                        "Removal did not refund the talent pool");
            } else {
                // Assert each reference on its own so the level-20 talent pool is
                // never asked to hold every case at once.
                for (String line : cases) {
                    var fields = line.split("\t");
                    controller.addAbility(cat, ability(cat, fields[0]));
                    controller.addAbility(cat, ability(cat, fields[1]));
                    assertValue(pc, cat, fields);
                    controller.removeAbility(cat, ability(cat, fields[1]));
                    controller.removeAbility(cat, ability(cat, fields[0]));
                }
                require(pc.getAvailableAbilityPool(magic).equals(pc.getTotalAbilityPool(magic)),
                        "Removal did not refund the talent pool");
                // Retain the first case so save/reload proves persistence.
                controller.addAbility(cat, ability(cat, first[0]));
                controller.addAbility(cat, ability(cat, first[1]));
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
