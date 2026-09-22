/** Batch API bridge: avoid RC10 CLI's conflicting output-file validators. */
class PcgenSpheresExport {
    public static void main(String[] args) {
        if (args.length != 4 && args.length != 5) {
            throw new IllegalArgumentException("character template output config [save] required");
        }
        boolean exported = pcgen.system.Main.loadCharacterAndExport(
                args[0], args[1], args[2], args[3]);
        if (exported) {
            var characters = pcgen.core.Globals.getPCList();
            if (characters.size() != 1) {
                throw new IllegalStateException("Expected exactly one loaded character");
            }
            var character = characters.get(0);
            var category = pcgen.core.SettingsHandler.getGameAsProperty().get()
                    .getAbilityCategory("Spheres Magic Talent");
            if (category == null
                    || !character.hasAbilityKeyed(category, "Destruction Sphere")
                    || !character.hasAbilityKeyed(category, "Searing Blast")) {
                throw new IllegalStateException("Selected Spheres talents were not loaded");
            }
            var spent = character.getTotalAbilityPool(category)
                    .subtract(character.getAvailableAbilityPool(category));
            if (spent.compareTo(java.math.BigDecimal.valueOf(2)) != 0) {
                throw new IllegalStateException("Expected two spent talents, got " + spent);
            }
            System.out.println("SPHERES_SELECTION_OK: Destruction Sphere, Searing Blast; spent=2");
            if (args.length == 5) {
                var facade = pcgen.system.CharacterManager.getCharacters().iterator().next();
                facade.setFile(new java.io.File(args[4]));
                if (!pcgen.system.CharacterManager.saveCharacter(facade)) {
                    throw new IllegalStateException("PCGen character save failed");
                }
            }
        }
        // PCGen may leave executor threads alive after batch work.
        System.exit(exported ? 0 : 1);
    }
}