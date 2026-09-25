/** Load/export/save a base class without the Incanter-only talent assumptions. */
class PcgenClassCatalog {
    public static void main(String[] args) {
        if (args.length < 7 || args.length > 8) {
            throw new IllegalArgumentException("character template output config required-spheres required-choice expected-pools [saved character]");
        }
        boolean exported = pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]);
        if (exported) {
            var characters = pcgen.core.Globals.getPCList();
            if (characters.size() != 1) {
                throw new IllegalStateException("Expected one character");
            }
            var pc = characters.get(0);
            var game = pcgen.core.SettingsHandler.getGameAsProperty().get();
            for (var required : args[4].split(",")) {
                if (required.isEmpty() || required.equals("-")) {
                    continue;
                }
                var category = game.getAbilityCategory(required.startsWith("M:")
                        ? "Spheres Magic Talent" : "Spheres Combat Talent");
                var sphere = required.substring(2) + " Sphere";
                if (!pc.hasAbilityKeyed(category, sphere)) {
                    throw new IllegalStateException("Missing class-granted sphere: " + sphere);
                }
            }
            if (!args[5].equals("-")) {
                var choice = args[5].split(":", 2);
                var category = game.getAbilityCategory(choice[0]);
                if (category == null || !pc.hasAbilityKeyed(category, choice[1])) {
                    throw new IllegalStateException("Missing chosen class feature: " + args[5]);
                }
            }
            if (!args[6].equals("-")) {
                for (var pool : args[6].split("@")) {
                    var parts = pool.split("=", 2);
                    var category = game.getAbilityCategory(parts[0]);
                    if (category == null || pc.getTotalAbilityPool(category)
                            .compareTo(new java.math.BigDecimal(parts[1])) != 0) {
                        throw new IllegalStateException("Incorrect class choice pool " + pool + ": "
                                + (category == null ? "missing" : pc.getTotalAbilityPool(category)));
                    }
                }
            }
            if (args.length == 8) {
                var facade = pcgen.system.CharacterManager.getCharacters().iterator().next();
                facade.setFile(new java.io.File(args[7]));
                if (!pcgen.system.CharacterManager.saveCharacter(facade)) {
                    throw new IllegalStateException("Character save failed");
                }
            }
        }
        System.exit(exported ? 0 : 1);
    }
}