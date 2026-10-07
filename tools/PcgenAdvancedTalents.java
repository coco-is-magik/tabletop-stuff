package pcgen.gui2.facade;

import java.nio.file.Files;
import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Advanced-talent eligibility, selection, refund and save/reload through PCGen. */
class PcgenAdvancedTalents {
    private static void assertCounter(pcgen.core.PlayerCharacter pc, String[] fields) {
        int actual = pc.getVariableValue(fields[4], "").intValue();
        require(actual == Integer.parseInt(fields[5]),
                fields[2] + " " + fields[4] + ": expected " + fields[5] + " got " + actual);
    }

    public static void main(String[] args) throws Exception {
        require(args.length == 8, "character template output config gate saved cases category required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory(args[7]);
        var facade = CharacterManager.getCharacters().iterator().next();
        var controller = new CharacterAbilities(pc, new Messages(), facade.getDataSet(), new TodoManager());
        var cases = Files.readAllLines(Path.of(args[6]));
        boolean reload = args[4].endsWith("reload");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var first = cases.get(0).split("\t");
        try {
            if (reload) {
                require(pc.hasAbilityKeyed(cat, ability(cat, first[2]).getKeyName()),
                        "Advanced talent lost on reload: " + first[2]);
                assertCounter(pc, first);
                controller.removeAbility(cat, ability(cat, first[2]));
                if (!first[1].equals("-")) {
                    controller.removeAbility(cat, ability(cat, first[1]));
                }
                controller.removeAbility(cat, ability(cat, first[0]));
                require(pc.getAvailableAbilityPool(magic).equals(pc.getTotalAbilityPool(magic)),
                        "Removal did not refund the advanced-talent pool");
            } else {
                for (String line : cases) {
                    var fields = line.split("\t");
                    boolean select = fields[3].equals("select");
                    controller.addAbility(cat, ability(cat, fields[0]));
                    if (!fields[1].equals("-")) {
                        controller.addAbility(cat, ability(cat, fields[1]));
                    }
                    var advanced = ability(cat, fields[2]);
                    require(advanced.qualifies(pc, advanced) == select,
                            fields[2] + ": qualifies expected " + select);
                    if (select) {
                        controller.addAbility(cat, advanced);
                        require(pc.hasAbilityKeyed(cat, advanced.getKeyName()),
                                "Advanced talent not selected: " + fields[2]);
                        assertCounter(pc, fields);
                        controller.removeAbility(cat, advanced);
                        require(!pc.hasAbilityKeyed(cat, advanced.getKeyName()),
                                "Advanced talent not removed: " + fields[2]);
                    } else {
                        require(!pc.hasAbilityKeyed(cat, advanced.getKeyName()),
                                "Blocked advanced talent was selectable: " + fields[2]);
                    }
                    if (!fields[1].equals("-")) {
                        controller.removeAbility(cat, ability(cat, fields[1]));
                    }
                    controller.removeAbility(cat, ability(cat, fields[0]));
                    require(pc.getAvailableAbilityPool(magic).equals(pc.getTotalAbilityPool(magic)),
                            "Removal did not refund the talent pool");
                }
                controller.addAbility(cat, ability(cat, first[0]));
                controller.addAbility(cat, ability(cat, first[1]));
                controller.addAbility(cat, ability(cat, first[2]));
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
