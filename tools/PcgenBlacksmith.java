package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.facade.core.ChooserFacade;
import pcgen.system.CharacterManager;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Persistent smithing grants through the production controller and chooser. */
class PcgenBlacksmith {
    private static class CraftChoice extends Messages {
        String skill = "Craft (Weapons)";
        boolean removing;

        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            var list = removing ? chooser.getSelectedList() : chooser.getAvailableList();
            for (var item : list) {
                require(item.getKeyName().startsWith("Craft ("), "Only Craft choices");
            }
            for (var item : list) {
                if (item.getKeyName().equals(skill)) {
                    if (removing) chooser.removeSelected(item);
                    else chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing Craft choice " + skill);
        }
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Blacksmith Smithing Insight");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new CraftChoice();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_BLACKSMITH_LEVEL", "").intValue();
        boolean reload = args[4].equals("blacksmith-reload");
        var durable = ability(cat, "Blacksmith Durable");
        var crafting = ability(cat, "Blacksmith Crafting Competence");
        var shield = ability(cat, "Blacksmith Shieldsmith");
        var master = ability(cat, "Blacksmith Master Shieldsmith (Requires Shieldsmith)");
        var previous = ChooserFactory.getDelegate();
        ChooserFactory.setDelegate(messages);
        try {
            require(pc.getTotalBonusTo("SKILL", "Profession (Blacksmith)") == Math.max(1, level / 2), "Skilled Craftsman bonus");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Craft Wondrous Item") == (level >= 3), "Level 3 crafting feat");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Craft Magic Arms and Armor") == (level >= 5), "Level 5 crafting feat");
            if (reload) {
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Toughness"), "Durable persistence");
                controller.removeAbility(cat, durable);
                if (level >= 4) {
                    require(pc.getTotalBonusTo("SKILL", messages.skill) == level, "Craft choice persistence");
                    messages.removing = true;
                    controller.removeAbility(cat, crafting);
                    messages.removing = false;
                }
            }
            var pool = pc.getAvailableAbilityPool(cat);
            controller.addAbility(cat, durable);
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Endurance"), "Endurance grant");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Toughness"), "Toughness grant");
            controller.removeAbility(cat, durable);
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Endurance"), "Endurance removal");
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Toughness"), "Toughness removal");
            rejected(controller, messages, cat, master, "InfoAbility.Messages.NotQualified");
            controller.addAbility(cat, shield);
            require(master.qualifies(pc, master), "Shieldsmith prerequisite");
            controller.removeAbility(cat, shield);
            require(!master.qualifies(pc, master), "Prerequisite removal");
            require(pc.getTotalBonusTo("SKILL", messages.skill) == 0, "No initial skill bonus");
            controller.addAbility(cat, crafting);
            require(pc.getTotalBonusTo("SKILL", messages.skill) == level, "Crafting competence");
            if (level >= 4) {
                messages.skill = "Craft (Armor)";
                controller.addAbility(cat, crafting);
                require(pc.getTotalBonusTo("SKILL", messages.skill) == level, "Second craft bonus");
                messages.removing = true;
                controller.removeAbility(cat, crafting);
                require(pc.getTotalBonusTo("SKILL", messages.skill) == 0, "Second craft refund");
                require(pc.getTotalBonusTo("SKILL", "Craft (Weapons)") == level, "First craft survives partial removal");
            }
            messages.skill = "Craft (Weapons)";
            messages.removing = true;
            controller.removeAbility(cat, crafting);
            messages.removing = false;
            require(pc.getTotalBonusTo("SKILL", messages.skill) == 0, "Full craft refund");
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Full insight refund");
            for (String[] test : new String[][] {{"Armorclad Mastery", "4"}, {"Stunning Strikes", "12"}}) {
                var insight = ability(cat, "Blacksmith " + test[0]);
                require(insight.qualifies(pc, insight) == (level >= Integer.parseInt(test[1])), "Body-text level gate " + test[0]);
                if (!insight.qualifies(pc, insight)) rejected(controller, messages, cat, insight, "InfoAbility.Messages.NotQualified");
            }
            var expanded = ability(cat, "Blacksmith Expanded Crafting");
            var itemFeats = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Blacksmith Item Creation Feat");
            if (reload && level >= 6) {
                require(pc.getAvailableAbilityPool(itemFeats).intValue() == 1, "Saved item creation pool");
                controller.removeAbility(cat, expanded);
            }
            for (int i = 1; i <= Math.min(2, level / 2); i++) {
                controller.addAbility(cat, expanded);
                require(pc.getAvailableAbilityPool(itemFeats).intValue() == i, "Repeated crafting pool");
            }
            rejected(controller, messages, itemFeats, ability(AbilityCategory.FEAT, "Forge Ring"), "InfoAbility.Messages.NotQualified");
            for (int i = Math.min(2, level / 2) - 1; i >= 0; i--) {
                controller.removeAbility(cat, expanded);
                require(pc.getAvailableAbilityPool(itemFeats).intValue() == i, "Crafting pool refund");
            }
            controller.addAbility(cat, durable);
            if (level >= 4) controller.addAbility(cat, crafting);
            if (level >= 6) controller.addAbility(cat, expanded);
        } finally {
            ChooserFactory.setDelegate(previous);
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