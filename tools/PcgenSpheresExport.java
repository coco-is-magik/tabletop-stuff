/** Batch API bridge: avoid RC10 CLI's conflicting output-file validators. */
class PcgenSpheresExport {
    public static void main(String[] args) {
        if (args.length < 4 || args.length > 5) {
            throw new IllegalArgumentException("character template output config [save or gate] required");
        }
        boolean exported = pcgen.system.Main.loadCharacterAndExport(
                args[0], args[1], args[2], args[3]);
        if (exported) {
            var characters = pcgen.core.Globals.getPCList();
            if (characters.size() != 1) {
                throw new IllegalStateException("Expected exactly one loaded character");
            }
            var character = characters.get(0);
            var game = pcgen.core.SettingsHandler.getGameAsProperty().get();
            var category = game.getAbilityCategory("Spheres Magic Talent");
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
            if (args.length == 5 && "sword-save".equals(args[4])) {
                var active = game.getAbilityCategory("Incanter Active Specialization");
                var tricks = game.getAbilityCategory("Incanter Arsenal Trick");
                var combat = game.getAbilityCategory("Incanter Arsenal Combat Feat");
                if (!character.hasAbilityKeyed(active, "Active Sword Birth")
                        || !character.hasAbilityKeyed(tricks, "Combat Feat")
                        || !character.hasAbilityKeyed(pcgen.core.AbilityCategory.FEAT, "Improved Initiative")
                        || character.getTotalAbilityPool(combat).intValue() != 1) {
                    throw new IllegalStateException("Sword Birth selections were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: sword-save");
            } else if (args.length == 5 && "human-favored-save".equals(args[4])) {
                var rewards = game.getAbilityCategory("Favored Class Bonus");
                if (character.getVariableValue("SPHERES_INCANTER_HUMAN_FCB_COUNT", "").intValue() != 6
                        || character.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() != 12
                        || character.getTotalAbilityPool(rewards).intValue() < 6) {
                    throw new IllegalStateException("Human favored class rewards were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: human-favored-save");
            } else if (args.length == 5 && "aasimar-favored-save".equals(args[4])) {
                if (character.getVariableValue("SPHERES_INCANTER_AASIMAR_FCB_COUNT", "").intValue() != 6
                        || character.getTotalBonusTo("SKILL", "Spellcraft") != 3.0) {
                    throw new IllegalStateException("Aasimar favored Spellcraft rewards were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: aasimar-favored-save");
            } else if (args.length == 5 && "tiefling-favored-save".equals(args[4])) {
                if (character.getVariableValue("SPHERES_INCANTER_TIEFLING_FCB_COUNT", "").intValue() != 6
                        || character.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue()
                        != character.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue()
                        + character.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue() + 3) {
                    throw new IllegalStateException("Tiefling concentration rewards were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: tiefling-favored-save");
            } else if (args.length == 5 && "gnome-favored-save".equals(args[4])) {
                if (character.getVariableValue("SPHERES_INCANTER_GNOME_DESTRUCTION_COUNT", "").intValue() != 6
                        || character.getVariableValue("SPHERES_DC_DESTRUCTION", "").intValue() != 18
                        || character.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() != 6) {
                    throw new IllegalStateException("Gnome favored Destruction DC was not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: gnome-favored-save");
            } else if (args.length == 5 && "halfling-favored-save".equals(args[4])) {
                var active = game.getAbilityCategory("Incanter Active Specialization");
                var channel = game.getAbilityCategory("Special Ability");
                if (character.getVariableValue("SPHERES_INCANTER_HALFLING_CHANNEL_COUNT", "").intValue() != 6
                        || !character.hasAbilityKeyed(active, "Active Channel Energy")
                        || !character.hasAbilityKeyed(channel, "Incanter Positive Channel")
                        || character.getVariableValue("SPHERES_CHANNEL_FAVORED_USES", "").intValue() != 3
                        || character.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() != 10) {
                    throw new IllegalStateException("Halfling channel bonus was not restored: count="
                            + character.getVariableValue("SPHERES_INCANTER_HALFLING_CHANNEL_COUNT", "")
                            + " favored=" + character.getVariableValue("SPHERES_CHANNEL_FAVORED_USES", "")
                            + " uses=" + character.getVariableValue("SPHERES_CHANNEL_USES", "")
                            + " active=" + character.hasAbilityKeyed(active, "Active Channel Energy")
                            + " polarity=" + character.hasAbilityKeyed(channel, "Incanter Positive Channel"));
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: halfling-favored-save");
            } else if (args.length == 5 && "healer-save".equals(args[4])) {
                var active = game.getAbilityCategory("Incanter Active Specialization");
                var special = game.getAbilityCategory("Special Ability");
                var channel = game.getAbilityCategory("Incanter Channel Energy");
                var mercy = game.getAbilityCategory("Mercy");
                if (!character.hasAbilityKeyed(active, "Active Channel Energy")
                        || !character.hasAbilityKeyed(active, "Active Merciful Healer")
                        || !character.hasAbilityKeyed(special, "Incanter Positive Channel")
                        || !character.hasAbilityKeyed(special, "Mercy ~ Fatigued")
                        || character.getTotalAbilityPool(channel).intValue() != 1
                        || character.getTotalAbilityPool(mercy).intValue() != 2
                        || character.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() != 7
                        || character.getVariableValue("MercyLVL", "").intValue() != 6) {
                    throw new IllegalStateException("Channel and mercy choices were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: healer-save");
            } else if (args.length == 5 && "domains-save".equals(args[4])) {
                var active = game.getAbilityCategory("Incanter Active Specialization");
                var special = game.getAbilityCategory("Special Ability");
                if (!character.hasAbilityKeyed(active, "Active Cleric Domain (Air)")
                        || !character.hasAbilityKeyed(special, "Domain Power ~ Lightning Arc")
                        || character.getVariableValue("DomainAirLVL", "").intValue() != 6) {
                    throw new IllegalStateException("Air domain powers were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: domains-save");
            } else if (args.length == 5 && "bloodline-save".equals(args[4])) {
                var active = game.getAbilityCategory("Incanter Active Specialization");
                var special = game.getAbilityCategory("Special Ability");
                if (!character.hasAbilityKeyed(active, "Active Sorcerer Bloodline (Aberrant)")
                        || !character.hasAbilityKeyed(special, "Aberrant Bloodline ~ Acidic Ray")
                        || character.getVariableValue("Sorcerer_Aberrant_BloodlinePower1LVL", "").intValue() != 6
                        || character.hasAbilityKeyed(special, "Aberrant Bloodline ~ Bonus Spells")) {
                    throw new IllegalStateException("Aberrant bloodline powers were not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: bloodline-save");
            } else if (args.length == 5 && "half-orc-favored-save".equals(args[4])) {
                var active = game.getAbilityCategory("Incanter Active Specialization");
                if (!character.hasAbilityKeyed(active, "Active Sorcerer Bloodline (Aberrant)")
                        || character.getVariableValue("SPHERES_INCANTER_HALF_ORC_BLOODLINE_COUNT", "").intValue() != 5
                        || character.getVariableValue("BloodlineLVL", "").intValue() != 7
                        || character.getVariableValue("BloodlineProgressionLVL", "").intValue() != 6) {
                    throw new IllegalStateException("Half-Orc bloodline favored class bonus was not restored");
                }
                System.out.println("SPHERES_SPECIALIZATION_OK: half-orc-favored-save");
            } else if (args.length == 5) {
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