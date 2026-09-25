package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Real controller checks for custom tradition purchase, grants and round trips. */
class PcgenTraditions {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("tradition-reload");
        boolean magic = args[6].equals("power");
        try {
            if (magic) {
                var tradition = game.getAbilityCategory("Custom Casting Tradition");
                var drawback = game.getAbilityCategory("Custom Casting Drawback");
                var boon = game.getAbilityCategory("Custom Casting Boon");
                var choice = ability(tradition, "Custom Casting Tradition");
                var verbal = ability(drawback, "Tradition - Verbal Casting");
                var somatic = ability(drawback, "Tradition - Somatic Casting");
                var focus = ability(drawback, "Tradition - Focus Casting");
                var signs = ability(drawback, "Tradition - Magical Signs");
                var prepared = ability(drawback, "Tradition - Prepared Caster");
                var easy = ability(boon, "Tradition - Easy Focus");
                var fortified = ability(boon, "Tradition - Fortified Casting");
                int original = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, choice.getKeyName()), "Casting tradition reload");
                    require(pc.hasAbilityKeyed(drawback, verbal.getKeyName()), "Verbal reload");
                    require(pc.hasAbilityKeyed(drawback, somatic.getKeyName()), "Somatic reload");
                    require(pc.hasAbilityKeyed(boon, easy.getKeyName()), "Boon reload");
                    require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 14, "Spell pool reload");
                    controller.removeAbility(boon, easy);
                    controller.removeAbility(drawback, somatic);
                    controller.removeAbility(drawback, verbal);
                    controller.removeAbility(tradition, choice);
                }
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 14, "Casting cleanup");
                require(!verbal.qualifies(pc, verbal), "Drawback without tradition");
                controller.addAbility(tradition, choice);
                rejected(controller, messages, tradition, choice, "InfoAbility.Messages.Duplicate");
                require(pc.getAvailableAbilityPool(drawback).intValue() == 5, "Drawback capacity");
                require(pc.getAvailableAbilityPool(boon).intValue() == 0, "Boon available without drawbacks");
                rejected(controller, messages, boon, easy, "InfoAbility.Messages.NoPoints");
                require(!fortified.qualifies(pc, fortified), "Fortified without Draining Casting");
                controller.addAbility(drawback, verbal);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 2,
                    "One-point spell pool");
                controller.addAbility(drawback, somatic);
                require(pc.getAvailableAbilityPool(boon).intValue() == 2, "Drawbacks unlock boons");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 4,
                    "Drawback point spell pool: original=" + original + " current=" + pc.getVariableValue("SPHERES_SPELL_POINTS", "")
                    + " drawbacks=" + pc.getVariableValue("SPHERES_TRADITION_DRAWBACKS", ""));
                controller.addAbility(drawback, focus);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 5,
                    "Three-point spell pool");
                controller.addAbility(drawback, signs);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 7,
                    "Four-point spell pool");
                controller.addAbility(drawback, prepared);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 10,
                    "Five-point spell pool");
                rejected(controller, messages, drawback, ability(drawback, "Tradition - Draining Casting"),
                    "InfoAbility.Messages.NoPoints");
                controller.removeAbility(drawback, prepared);
                controller.removeAbility(drawback, signs);
                controller.removeAbility(drawback, focus);
                controller.addAbility(boon, easy);
                require(pc.getAvailableAbilityPool(boon).intValue() == 0, "Boon costs two points");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original, "Boon spent bonus spell points");
                rejected(controller, messages, boon, fortified, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(boon, easy);
                controller.removeAbility(drawback, somatic);
                controller.removeAbility(drawback, verbal);
                controller.removeAbility(tradition, choice);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original, "Casting refunds");
                controller.addAbility(tradition, choice);
                controller.addAbility(drawback, verbal);
                controller.addAbility(drawback, somatic);
                controller.addAbility(boon, easy);
            } else {
                var tradition = game.getAbilityCategory("Conscript Martial Tradition");
                var equipment = game.getAbilityCategory("Custom Martial Equipment");
                var theme = game.getAbilityCategory("Custom Martial Theme");
                var base = game.getAbilityCategory("Custom Martial Sphere");
                var bonus = game.getAbilityCategory("Spheres Equipment Bonus Talent");
                var talents = game.getAbilityCategory("Spheres Combat Talent");
                var choice = ability(tradition, "Custom Martial Tradition");
                var shield = ability(talents, "Equipment - Shield Training");
                var armor = ability(talents, "Equipment - Armor Training");
                var fencing = ability(talents, "Fencing Sphere");
                var scout = ability(talents, "Scout Sphere");
                var paid = pc.getAvailableAbilityPool(talents);
                if (!reload) {
                    rejected(controller, messages, equipment, armor, "InfoAbility.Messages.NotQualified");
                }
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, choice.getKeyName()), "Martial tradition reload");
                    require(pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Equipment reload");
                    require(pc.hasAbilityKeyed(talents, shield.getKeyName()), "Shield reload");
                    require(pc.hasAbilityKeyed(talents, fencing.getKeyName()), "Fencing reload");
                    controller.removeAbility(theme, scout);
                    controller.removeAbility(base, fencing);
                    controller.removeAbility(equipment, armor);
                    controller.removeAbility(bonus, shield);
                    controller.removeAbility(tradition, choice);
                }
                require(!pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Equipment not refunded");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Tradition touched paid pool");
                controller.addAbility(tradition, choice);
                rejected(controller, messages, tradition, choice, "InfoAbility.Messages.Duplicate");
                require(pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Equipment sphere grant: tradition="
                    + pc.hasAbilityKeyed(tradition, choice.getKeyName()) + " combat="
                    + pc.getVariableValue("SPHERES_COMBAT_TALENTS", "") + " free="
                    + pc.getAvailableAbilityPool(bonus));
                require(pc.getAvailableAbilityPool(bonus).intValue() == 1, "First equipment talent grant");
                require(pc.getAvailableAbilityPool(equipment).intValue() == 1, "Second equipment talent grant");
                controller.addAbility(bonus, shield);
                controller.addAbility(equipment, armor);
                controller.addAbility(base, fencing);
                controller.addAbility(theme, scout);
                require(pc.hasAbilityKeyed(talents, armor.getKeyName()), "Equipment choice missing");
                require(pc.hasAbilityKeyed(talents, fencing.getKeyName()), "Base choice missing");
                require(pc.hasAbilityKeyed(talents, scout.getKeyName()), "Theme choice missing");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Free tradition charged paid pool");
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