package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.core.Equipment;
import pcgen.core.character.EquipSet;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Arsenal Trick prerequisites and repeatable grants through the real controller. */
class PcgenArmorist {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory("Armorist Arsenal Trick");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_ARMORIST_LEVEL", "").intValue();
        boolean reload = args[4].equals("armorist-reload");
        var combat = ability(cat, "Armorist Combat Talent");
        var featOption = ability(cat, "Armorist Combat Feat");
        var feats = game.getAbilityCategory("Armorist Combat Feat Feat");
        var initiative = ability(AbilityCategory.FEAT, "Improved Initiative");
        try {
            if (reload && level >= 6) {
                require(pc.getVariableValue("SPHERES_COMBAT_TALENTS", "").intValue() == 2, "Saved combat talents");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"), "Saved chosen feat");
                controller.removeAbility(feats, initiative);
                controller.removeAbility(cat, featOption);
                controller.removeAbility(cat, combat);
                require(pc.getVariableValue("SPHERES_COMBAT_TALENTS", "").intValue() == 1, "Saved partial refund");
                controller.removeAbility(cat, combat);
            }
            for (String[] test : new String[][] {
                    {"Battle Magician (requires armorist 5)", "5"},
                    {"Combat Implementation (requires armorist 6 - bind implement class feature)", "6"},
                    {"Bonded Boost (requires armorist 10 - boost equipment class feature)", "10"}}) {
                var option = ability(cat, "Armorist " + test[0]);
                require(option.qualifies(pc, option) == (level >= Integer.parseInt(test[1])), "Level gate " + test[0]);
                if (!option.qualifies(pc, option)) rejected(controller, messages, cat, option, "InfoAbility.Messages.NotQualified");
            }
            var binding = ability(cat, "Armorist Additional Binding (requires bound equipment)");
            int bound = pc.getVariableValue("SPHERES_ARMORIST_BOUND_ITEMS", "").intValue();
            controller.addAbility(cat, binding);
            require(pc.getVariableValue("SPHERES_ARMORIST_BOUND_ITEMS", "").intValue() == bound + 1, "Additional binding");
            controller.removeAbility(cat, binding);
            require(pc.getVariableValue("SPHERES_ARMORIST_BOUND_ITEMS", "").intValue() == bound, "Binding refund");
            require(pc.getTotalBonusTo("MISC", "MAXDEX") == 0, "No armor bonus when unequipped");
            var armor = Globals.getContext().getReferenceContext()
                    .silentlyGetConstructedCDOMObject(Equipment.class, "Chainmail").clone();
            pc.addEquipment(armor);
            pc.addEquipSet(new EquipSet("0.9", "Armor regression"));
            var equipped = new EquipSet("0.9.1", "Armor", armor.getName(), armor);
            pc.addEquipSet(equipped);
            pc.setCalcEquipSetId("0.9");
            pc.setCalcEquipmentList();
            pc.calcActiveBonuses();
            int training = Math.max(0, (level + 1) / 4);
            require(pc.getTotalBonusTo("MISC", "MAXDEX") == training, "Equipped armor Dexterity allowance");
            require(pc.getTotalBonusTo("MISC", "ACCHECK") == training, "Equipped armor check reduction");
            var greater = ability(cat, "Armorist Greater Armor Training (requires armorist 3)");
            if (level >= 4) {
                controller.addAbility(cat, greater);
                controller.addAbility(cat, greater);
                require(pc.getTotalBonusTo("MISC", "MAXDEX") == training + 2, "Repeated armor training");
                controller.removeAbility(cat, greater);
                require(pc.getTotalBonusTo("MISC", "ACCHECK") == training + 1, "Partial armor training refund");
                controller.removeAbility(cat, greater);
                require(pc.getTotalBonusTo("MISC", "MAXDEX") == training, "Full armor training refund");
            } else {
                rejected(controller, messages, cat, greater, "InfoAbility.Messages.NotQualified");
            }
            pc.delEquipSet(equipped);
            pc.setCalcEquipmentList();
            pc.removeEquipment(armor);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("MISC", "MAXDEX") == 0, "Unequipping removes armor benefit");
            var companion = ability(cat, "Armorist Bound Companion (requires natural materials or horseman’s materials)");
            rejected(controller, messages, cat, companion, "InfoAbility.Messages.NotQualified");
            for (String name : new String[] {"Natural Materials", "Horseman’s Materials"}) {
                var option = ability(cat, "Armorist " + name);
                controller.addAbility(cat, option);
                require(companion.qualifies(pc, companion), "Alternative prerequisite " + name);
                controller.removeAbility(cat, option);
                require(!companion.qualifies(pc, companion), "Removed prerequisite " + name);
            }
            if (level >= 4) {
                controller.addAbility(cat, combat);
                controller.addAbility(cat, combat);
                require(pc.getVariableValue("SPHERES_COMBAT_TALENTS", "").intValue() == 2, "Repeatable talent grant");
                controller.removeAbility(cat, combat);
                require(pc.getVariableValue("SPHERES_COMBAT_TALENTS", "").intValue() == 1, "Partial talent refund");
                controller.removeAbility(cat, combat);
                require(pc.getVariableValue("SPHERES_COMBAT_TALENTS", "").intValue() == 0, "Full talent refund");
                for (String name : new String[] {"Combat Feat", "Crafter", "Champion"}) {
                    var option = ability(cat, "Armorist " + name);
                    var pool = game.getAbilityCategory("Armorist " + name + " Feat");
                    controller.addAbility(cat, option);
                    controller.addAbility(cat, option);
                    require(pc.getAvailableAbilityPool(pool).intValue() == 2, "Repeatable feat grant " + name);
                    controller.removeAbility(cat, option);
                    require(pc.getAvailableAbilityPool(pool).intValue() == 1, "Partial feat refund");
                    controller.removeAbility(cat, option);
                    require(pc.getAvailableAbilityPool(pool).intValue() == 0, "Full feat refund");
                }
            }
            if (level >= 6) {
                controller.addAbility(cat, combat);
                controller.addAbility(cat, combat);
                controller.addAbility(cat, featOption);
                rejected(controller, messages, feats, ability(AbilityCategory.FEAT, "Whirlwind Attack"),
                        "InfoAbility.Messages.NotQualified");
                controller.addAbility(feats, initiative);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"), "Chosen feat");
                require(pc.getAvailableAbilityPool(feats).intValue() == 0, "Spent feat pool");
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