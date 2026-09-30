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
        var books = game.getAbilityCategory("Spheres Book Casting");
        var deciphering = game.getAbilityCategory("Spheres Spell Deciphered");
        var access = game.getAbilityCategory("Spheres Spellbook Access");
        var book = ability(books, "Book Casting - Restoring Shield");
        var deciphered = ability(deciphering, "Deciphered - Restoring Shield");
        var accessible = ability(access, "Accessible Book - Restoring Shield");
        var feat = ability(AbilityCategory.FEAT, "Spellcrafting");
        var mastery = ability(AbilityCategory.FEAT, "Spellbook Mastery");
        String mishap = "SPHERES_BOOK_87891E825E78E78E_MISHAP";
        boolean reload = args[4].equals("spell-reload");
        try {
            require(pc.getTotalAbilityPool(repertoire).intValue() == 4, "Repertoire uses casting modifier");
            if (reload) {
                require(pc.hasAbilityKeyed(books, book.getKeyName()), "Book casting reload");
                require(pc.hasAbilityKeyed(deciphering, deciphered.getKeyName()), "Deciphering reload");
                require(pc.hasAbilityKeyed(access, accessible.getKeyName()), "Book access reload");
                require(pc.getVariableValue(mishap, "").intValue() == 0, "Saved book mishap");
                controller.removeAbility(books, book);
                controller.removeAbility(access, accessible);
                controller.removeAbility(deciphering, deciphered);
                controller.removeAbility(AbilityCategory.FEAT, mastery);
                controller.removeAbility(AbilityCategory.FEAT, feat);
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
            require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 10,
                "Life selection must preserve Incanter caster level; class level="
                    + pc.getVariableValue("SPHERES_INCANTER_LEVEL", "")
                    + " caster bonus=" + pc.getTotalBonusTo("VAR", "SPHERES_CASTER_LEVEL"));
            require(pc.hasAbilityKeyed(talents, life.getKeyName()), "Life purchase failed: " + messages.errors
                + " pool=" + pc.getAvailableAbilityPool(talents));
            require(!spell.qualifies(pc, spell), "Missing Protection accepted");
            controller.addAbility(talents, protection);
            require(pc.hasAbilityKeyed(talents, protection.getKeyName()), "Protection purchase failed: " + messages.errors
                + " CL=" + pc.getVariableValue("SPHERES_CASTER_LEVEL", "")
                + " prerequisites=" + protection.getPrerequisiteList());
            require(!spell.qualifies(pc, spell), "Missing acquisition accepted");
            require(learned.qualifies(pc, learned), "Learning incorrectly needs Spellcrafting");
            require(!research.qualifies(pc, research), "Research without Spellcrafting");
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
            controller.removeAbility(repertoire, spell);
            controller.removeAbility(acquisition, learned);
            var slots = pc.getAvailableAbilityPool(repertoire);
            rejected(controller, messages, books, book, "InfoAbility.Messages.NotQualified");
            rejected(controller, messages, access, accessible, "InfoAbility.Messages.NotQualified");
            controller.addAbility(deciphering, deciphered);
            controller.addAbility(access, accessible);
            require(!book.qualifies(pc, book), "Book casting requires Mastery");
            controller.addAbility(AbilityCategory.FEAT, feat);
            controller.addAbility(AbilityCategory.FEAT, mastery);
            controller.removeAbility(talents, life);
            controller.removeAbility(talents, protection);
            require(book.qualifies(pc, book), "Mastery bypasses missing basic spheres");
            controller.addAbility(books, book);
            require(pc.hasAbilityKeyed(books, book.getKeyName()), "Book casting selection");
            require(pc.getVariableValue(mishap, "").intValue() == 20, "Two missing spheres: 20 percent");
            controller.addAbility(talents, life);
            require(pc.getVariableValue(mishap, "").intValue() == 10, "One missing sphere: 10 percent");
            controller.addAbility(talents, protection);
            require(pc.getVariableValue(mishap, "").intValue() == 0, "No missing spheres: zero mishap");
            controller.removeAbility(access, accessible);
            require(!book.qualifies(pc, book), "Lost book revokes qualification");
            require(pc.hasAbilityKeyed(deciphering, deciphered.getKeyName()), "Losing book preserves deciphering");
            controller.addAbility(access, accessible);
            controller.removeAbility(AbilityCategory.FEAT, mastery);
            require(!book.qualifies(pc, book), "Mastery removal revokes book casting");
            controller.addAbility(AbilityCategory.FEAT, mastery);
            require(pc.getAvailableAbilityPool(repertoire).equals(slots), "Book casting never spends repertoire slots");
            require(!pc.hasAbilityKeyed(acquisition, learned.getKeyName()), "Book casting does not learn spell");
            require(!pc.hasAbilityKeyed(repertoire, spell.getKeyName()), "Book casting does not add to repertoire");
            controller.addAbility(acquisition, learned);
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