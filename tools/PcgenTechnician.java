package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Technical insight dependency, capacity and automatic sphere round trips. */
class PcgenTechnician {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory("Technician Technical Insight");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_TECHNICIAN_LEVEL", "").intValue();
        boolean reload = args[4].equals("technician-reload");
        var intuition = ability(cat, "Technician Intuition (Ex)");
        var luck = ability(cat, "Technician Luck");
        var lucky = ability(cat, "Technician Intuition - Lucky");
        try {
            require(pc.getVariableValue("SPHERES_TECHNICIAN_GADGETS", "").intValue() == Math.max(1, level / 2), "Daily gadgets");
            require(pc.getVariableValue("SPHERES_TECHNICIAN_GADGET_DC", "").intValue() == 10 + level / 2, "Gadget DC");
            require(pc.getTotalBonusTo("SKILL", "Disable Device") == Math.max(1, level / 2), "Trapfinding Disable Device");
            require(pc.getTotalBonusTo("SKILL", "Knowledge (Engineering)") == level / 2, "Technically Minded");
            require(pc.getTotalBonusTo("SKILL", "Perception") == 0, "Do not apply trap-only bonus to all Perception");
            if (reload) {
                require(pc.getVariableValue("SPHERES_TECHNICIAN_INTUITION", "").intValue() == 2, "Saved intuition");
                require(pc.getVariableValue("SPHERES_TECHNICIAN_LUCK", "").intValue() == 2, "Saved luck");
                controller.removeAbility(cat, lucky);
                controller.removeAbility(cat, luck);
                controller.removeAbility(cat, intuition);
            }
            var pool = pc.getAvailableAbilityPool(cat);
            for (String key : new String[] {"Intuition - Combat", "Intuition - Meditative", "Intuition - Reactive",
                    "Luck - Combatant’s", "Luck - Showman’s", "Luck - Socialite’s", "Intuition - Lucky"}) {
                var upgrade = ability(cat, "Technician " + key);
                rejected(controller, messages, cat, upgrade, "InfoAbility.Messages.NotQualified");
                var parent = key.startsWith("Intuition") ? intuition : luck;
                controller.addAbility(cat, parent);
                if (key.equals("Intuition - Lucky")) {
                    require(!upgrade.qualifies(pc, upgrade), "Lucky requires both parents");
                    controller.addAbility(cat, luck);
                }
                require(upgrade.qualifies(pc, upgrade), "Insight dependencies satisfied");
                controller.addAbility(cat, upgrade);
                String resource = key.startsWith("Intuition") ? "INTUITION" : "LUCK";
                require(pc.getVariableValue("SPHERES_TECHNICIAN_" + resource, "").intValue() == 2, "Upgrade capacity");
                controller.removeAbility(cat, upgrade);
                require(pc.getVariableValue("SPHERES_TECHNICIAN_" + resource, "").intValue() == 1, "Upgrade refund");
                if (key.equals("Intuition - Lucky")) controller.removeAbility(cat, luck);
                controller.removeAbility(cat, parent);
                require(!upgrade.qualifies(pc, upgrade), "Dependency removal");
                require(pc.getVariableValue("SPHERES_TECHNICIAN_" + resource, "").intValue() == 0, "Parent refund");
            }
            for (String[] test : new String[][] {{"Greater Craftsman", "6"}, {"Expert’s Insight", "10"}}) {
                var insight = ability(cat, "Technician " + test[0]);
                require(insight.qualifies(pc, insight) == (level >= Integer.parseInt(test[1])), "Insight level gate");
            }
            var professional = ability(cat, "Technician Professional Insight (Ex)");
            controller.addAbility(cat, professional);
            require(pc.getTotalBonusTo("SKILL", "TYPE.Craft") == level / 2, "Craft bonus");
            require(pc.getTotalBonusTo("SKILL", "TYPE.Profession") == level / 2, "Profession bonus");
            controller.removeAbility(cat, professional);
            require(pc.getTotalBonusTo("SKILL", "TYPE.Craft") == 0, "Professional refund");
            var gadgeteer = ability(cat, "Technician Gadgeteer");
            var paid = pc.getAvailableAbilityPool(combat);
            controller.addAbility(cat, gadgeteer);
            require(pc.hasAbilityKeyed(combat, "Tinker Sphere"), "Gadgeteer sphere grant");
            require(pc.getAvailableAbilityPool(combat).equals(paid), "Automatic sphere does not spend talents");
            controller.removeAbility(cat, gadgeteer);
            require(!pc.hasAbilityKeyed(combat, "Tinker Sphere"), "Gadgeteer refund");
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Insight pool refunds");
            controller.addAbility(cat, intuition);
            controller.addAbility(cat, luck);
            controller.addAbility(cat, lucky);
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