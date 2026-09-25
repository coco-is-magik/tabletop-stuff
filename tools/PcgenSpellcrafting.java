package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Production-controller checks for custom spell ownership and persistence. */
class PcgenSpellcrafting {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var repertoire = game.getAbilityCategory("Spheres Spell Repertoire");
        var acquisition = game.getAbilityCategory("Spheres Spell Acquisition");
        var talents = game.getAbilityCategory("Spheres Magic Talent");
        var spell = ability(repertoire, "Restoring Shield");
        var learned = ability(acquisition, "Learned - Restoring Shield");
        var research = ability(acquisition, "Researched - Restoring Shield");
        var life = ability(talents, "Life Sphere");
        var protection = ability(talents, "Protection Sphere");
        boolean reload = args[4].equals("spell-reload");
        try {
            require(pc.getTotalAbilityPool(repertoire).intValue() == 4, "Repertoire uses casting modifier");
            if (reload) {
                require(pc.hasAbilityKeyed(repertoire, spell.getKeyName()), "Spell reload");
                require(pc.hasAbilityKeyed(acquisition, learned.getKeyName()), "Acquisition reload");
                require(pc.getAvailableAbilityPool(repertoire).intValue() == 3, "Slot reload");
                controller.removeAbility(repertoire, spell);
                controller.removeAbility(acquisition, learned);
                controller.removeAbility(talents, protection);
                controller.removeAbility(talents, life);
            }
            rejected(controller, messages, repertoire, spell, "InfoAbility.Messages.NotQualified");
            rejected(controller, messages, acquisition, learned, "InfoAbility.Messages.NotQualified");
            controller.addAbility(talents, life);
            require(!spell.qualifies(pc, spell), "Missing Protection accepted");
            controller.addAbility(talents, protection);
            require(!spell.qualifies(pc, spell), "Missing acquisition accepted");
            require(learned.qualifies(pc, learned), "Learning incorrectly needs Spellcrafting");
            require(!research.qualifies(pc, research), "Research without Spellcrafting");
            var feat = ability(AbilityCategory.FEAT, "Spellcrafting");
            var mastery = ability(AbilityCategory.FEAT, "Spellbook Mastery");
            require(!mastery.qualifies(pc, mastery), "Mastery without Spellcrafting");
            controller.addAbility(AbilityCategory.FEAT, feat);
            require(research.qualifies(pc, research), "Research with feat rejected");
            require(mastery.qualifies(pc, mastery), "Mastery chain rejected");
            controller.removeAbility(AbilityCategory.FEAT, feat);
            controller.addAbility(acquisition, learned);
            controller.addAbility(repertoire, spell);
            require(pc.hasAbilityKeyed(repertoire, spell.getKeyName()), "Spell not selected");
            require(pc.getAvailableAbilityPool(repertoire).intValue() == 3, "Spell must cost one slot");
            rejected(controller, messages, repertoire, spell, "InfoAbility.Messages.Duplicate");
            controller.removeAbility(repertoire, spell);
            require(pc.getAvailableAbilityPool(repertoire).intValue() == 4, "Slot not refunded");
            controller.removeAbility(talents, life);
            require(!spell.qualifies(pc, spell), "Removed prerequisite still qualifies");
            controller.addAbility(talents, life);
            controller.addAbility(repertoire, spell);
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