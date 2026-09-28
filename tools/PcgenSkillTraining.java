package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.core.Skill;
import pcgen.core.PlayerCharacter;
import pcgen.core.analysis.SkillRankControl;
import pcgen.system.CharacterManager;
import pcgen.facade.core.ChooserFacade;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Persistent skill training through the production ability controller. */
class PcgenSkillTraining {
    private static class CraftChoice extends Messages {
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            if (chooser.getSelectedList().getSize() == 1) {
                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                chooser.commit();
                return true;
            }
            for (var item : chooser.getAvailableList()) {
                require(item.getKeyName().startsWith("Craft ("), "Craftsman must offer only Craft skills");
            }
            for (var item : chooser.getAvailableList()) {
                if (item.getKeyName().equals("Craft (Weapons)")) {
                    chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Expected Craft (Weapons) choice");
        }
    }
    private static void ranks(PlayerCharacter pc, String name, int expected) {
        var skill = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(Skill.class, name);
        require(skill != null, "Missing skill: " + name);
        int actual = SkillRankControl.getTotalRank(pc, skill).intValue();
        require(actual == expected, name + " ranks: expected " + expected + ", got " + actual);
    }

    public static void main(String[] args) throws Exception {
        require(args.length == 6, "character template output config gate saved required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Combat Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new CraftChoice();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("skills-reload");
        int level = pc.getTotalLevels();
        try {
            var warleader = ability(cat, "Warleader Sphere");
            if (reload) {
                require(pc.hasAbilityKeyed(cat, "Warleader Sphere"), "Saved overlap sphere");
                double withOverlap = pc.getTotalBonusTo("SKILL", "Diplomacy");
                controller.removeAbility(cat, warleader);
                require(pc.getTotalBonusTo("SKILL", "Diplomacy") == withOverlap - level / 2,
                        "Saved overlap bonus");
            }
            for (String[] test : new String[][] {
                    {"Fencing Sphere", "Fencing - Read Foe", "Sense Motive", "Bluff"},
                    {"Leadership Sphere", "Leadership - Military Training", "Profession (Soldier)", "Diplomacy"}}) {
                var sphere = ability(cat, test[0]);
                var talent = ability(cat, test[1]);
                if (reload) {
                    ranks(pc, test[2], Math.min(level, 10));
                    controller.removeAbility(cat, talent);
                    ranks(pc, test[2], 0);
                    ranks(pc, test[3], Math.min(level, 5));
                    controller.removeAbility(cat, sphere);
                }
                ranks(pc, test[2], 0);
                rejected(controller, messages, cat, talent, "InfoAbility.Messages.NotQualified");
                var pool = pc.getAvailableAbilityPool(cat);
                controller.addAbility(cat, sphere);
                ranks(pc, test[2], 0);
                ranks(pc, test[3], Math.min(level, 5));
                controller.addAbility(cat, talent);
                ranks(pc, test[2], Math.min(level, 10));
                ranks(pc, test[3], Math.min(level, 10));
                controller.removeAbility(cat, talent);
                ranks(pc, test[2], 0);
                ranks(pc, test[3], Math.min(level, 5));
                controller.removeAbility(cat, sphere);
                require(pc.getAvailableAbilityPool(cat).equals(pool), "Full talent refund");
                controller.addAbility(cat, sphere);
                controller.addAbility(cat, talent);
            }
            double baseline = pc.getTotalBonusTo("SKILL", "Diplomacy");
            controller.addAbility(cat, warleader);
            ranks(pc, "Diplomacy", Math.min(level, 10));
            require(pc.getTotalBonusTo("SKILL", "Diplomacy") == baseline + level / 2,
                    "Diplomacy overlap competence bonus");
            controller.removeAbility(cat, warleader);
            require(pc.getTotalBonusTo("SKILL", "Diplomacy") == baseline, "Overlap bonus removal");
            if (!reload) controller.addAbility(cat, warleader);
            var athletics = ability(cat, "Athletics Sphere");
            var pilot = ability(cat, "Athletics - Ace Pilot");
            var tech = ability(cat, "Tech Sphere");
            var tinker = ability(cat, "Tinker Sphere");
            var gadgets = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Tech Bonus Gadget");
            var battery = ability(cat, "Tech - Battery");
            var shield = ability(cat, "Tech - Compact Shield");
            if (reload) {
                require(pc.getVariableValue("SPHERES_TECH_COMPACTSHIELD_COUNT", "").intValue() == 2,
                        "Saved repeat limit counter");
                rejected(controller, messages, cat, shield, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(cat, shield);
                require(pc.getVariableValue("SPHERES_TECH_COMPACTSHIELD_COUNT", "").intValue() == 1,
                        "Saved counter partial refund");
                controller.removeAbility(cat, shield);
                require(pc.hasAbilityKeyed(cat, "Tech - Battery"), "Free gadget persistence");
                require(pc.getAvailableAbilityPool(gadgets).intValue() == 0, "Saved gadget pool spend");
                controller.removeAbility(gadgets, battery);
                ranks(pc, "Profession (Pilot)", Math.min(level, 10));
                ranks(pc, "Craft (Mechanical)", 5);
                controller.removeAbility(cat, pilot);
                controller.removeAbility(cat, athletics);
                controller.removeAbility(cat, tinker);
                controller.removeAbility(cat, tech);
            }
            ranks(pc, "Profession (Pilot)", 0);
            rejected(controller, messages, cat, pilot, "InfoAbility.Messages.NotQualified");
            controller.addAbility(cat, athletics);
            controller.addAbility(cat, pilot);
            ranks(pc, "Profession (Pilot)", Math.min(level, 10));
            controller.removeAbility(cat, pilot);
            ranks(pc, "Profession (Pilot)", 0);
            controller.addAbility(cat, pilot);
            ranks(pc, "Craft (Mechanical)", 0);
            controller.addAbility(cat, tech);
            ranks(pc, "Craft (Mechanical)", 5);
            require(pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue() == 6, "Tech capacity");
            require(pc.getVariableValue("SPHERES_TECH_RECHARGE", "").intValue() == 3, "Tech recharge");
            require(pc.getVariableValue("SPHERES_DC_TECH", "").intValue() == 16, "Tech rank-based DC");
            double mechanical = pc.getTotalBonusTo("SKILL", "Craft (Mechanical)");
            controller.addAbility(cat, tinker);
            var equipment = ability(cat, "Equipment Sphere");
            var craftsman = ability(cat, "Equipment - Craftsman");
            var equipmentPool = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Equipment Bonus Talent");
            var oldDelegate = ChooserFactory.getDelegate();
            ChooserFactory.setDelegate(messages);
            try {
                if (reload) {
                    ranks(pc, "Craft (Weapons)", level);
                    controller.removeAbility(equipmentPool, craftsman);
                    ranks(pc, "Craft (Weapons)", 0);
                    controller.removeAbility(cat, equipment);
                }
                controller.addAbility(cat, equipment);
                controller.addAbility(equipmentPool, craftsman);
                ranks(pc, "Craft (Weapons)", level);
                require(pc.getAvailableAbilityPool(equipmentPool).intValue() == 0, "Craftsman free talent cost");
                controller.removeAbility(equipmentPool, craftsman);
                ranks(pc, "Craft (Weapons)", 0);
                require(pc.getAvailableAbilityPool(equipmentPool).intValue() == 1, "Craftsman refund");
                controller.addAbility(equipmentPool, craftsman);
            } finally {
                ChooserFactory.setDelegate(oldDelegate);
            }
            var paidPool = pc.getAvailableAbilityPool(cat);
            require(pc.getAvailableAbilityPool(gadgets).intValue() == 1, "Starting gadget grant");
            controller.addAbility(gadgets, battery);
            require(pc.hasAbilityKeyed(cat, "Tech - Battery"), "Free gadget selection");
            require(pc.getAvailableAbilityPool(cat).equals(paidPool), "Free gadget must not spend paid talents");
            require(pc.getAvailableAbilityPool(gadgets).intValue() == 0, "Free gadget cost");
            ranks(pc, "Craft (Mechanical)", Math.min(level, 10));
            require(pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue() == Math.min(level, 10) + 2,
                    "Gadget scales charge capacity");
            controller.removeAbility(gadgets, battery);
            ranks(pc, "Craft (Mechanical)", 5);
            require(pc.getAvailableAbilityPool(gadgets).intValue() == 1, "Free gadget refund");
            controller.addAbility(gadgets, battery);
            ranks(pc, "Craft (Mechanical)", Math.min(level, 10));
            require(pc.getTotalBonusTo("SKILL", "Craft (Mechanical)") == mechanical + level / 2,
                    "Tinker overlap bonus");
            controller.removeAbility(cat, tinker);
            require(pc.getTotalBonusTo("SKILL", "Craft (Mechanical)") == mechanical, "Tinker overlap removal");
            var extra = ability(cat, "Tech - Extra Gadgets");
            for (int i = 1; i <= 2; i++) {
                controller.addAbility(cat, extra);
                int skillRanks = Math.min(level, 5 * (2 + i));
                require(pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue() == skillRanks + 2 + 2 * i,
                        "Extra Gadgets charge capacity " + i);
                require(pc.getVariableValue("SPHERES_TECH_PREPARED_GADGETS", "").intValue() == skillRanks / 2 + 1 + 2 * i,
                        "Extra Gadgets prepared capacity " + i);
            }
            controller.removeAbility(cat, extra);
            require(pc.getVariableValue("SPHERES_TECH_EXTRAGADGETS_COUNT", "").intValue() == 1,
                    "Repeat counter survives partial removal");
            require(pc.getVariableValue("SPHERES_TECH_PREPARED_GADGETS", "").intValue() == Math.min(level, 15) / 2 + 3,
                    "Extra Gadgets partial refund");
            controller.removeAbility(cat, extra);
            require(pc.getVariableValue("SPHERES_TECH_PREPARED_GADGETS", "").intValue() == Math.min(level, 10) / 2 + 1,
                    "Extra Gadgets full refund");
            for (String[] test : new String[][] {{"Alchemy Sphere", "ALCHEMY"}, {"Trap Sphere", "TRAP"}}) {
                var sphere = ability(cat, test[0]);
                controller.addAbility(cat, sphere);
                require(pc.getVariableValue("SPHERES_DC_" + test[1], "").intValue() == 16,
                        "Rank-based DC " + test[0]);
                controller.removeAbility(cat, sphere);
            }
            controller.addAbility(cat, tinker);
            var extendo = ability(cat, "Tech - Extendo Appendage");
            controller.addAbility(cat, extendo);
            if (level < 10) {
                rejected(controller, messages, cat, extendo, "InfoAbility.Messages.NotQualified");
            } else {
                controller.addAbility(cat, extendo);
                rejected(controller, messages, cat, extendo, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(cat, extendo);
            }
            controller.removeAbility(cat, extendo);
            require(pc.getVariableValue("SPHERES_TECH_EXTENDOAPPENDAGE_COUNT", "").intValue() == 0,
                    "Conditional repeat full refund");
            var range = ability(cat, "Tech - Range Amplifier");
            int rangeLimit = 1 + level / 5;
            for (int i = 1; i <= rangeLimit; i++) controller.addAbility(cat, range);
            require(pc.getVariableValue("SPHERES_TECH_RANGEAMPLIFIER_COUNT", "").intValue() == rangeLimit,
                    "Rank-scaled repeat limit");
            rejected(controller, messages, cat, range, "InfoAbility.Messages.NotQualified");
            for (int i = rangeLimit - 1; i >= 0; i--) {
                controller.removeAbility(cat, range);
                require(pc.getVariableValue("SPHERES_TECH_RANGEAMPLIFIER_COUNT", "").intValue() == i,
                        "Rank-scaled repeat refund " + i);
            }
            for (int i = 1; i <= 2; i++) controller.addAbility(cat, shield);
            rejected(controller, messages, cat, shield, "InfoAbility.Messages.NotQualified");
            controller.removeAbility(cat, shield);
            require(pc.getVariableValue("SPHERES_TECH_COMPACTSHIELD_COUNT", "").intValue() == 1,
                    "Capped repeat counter partial refund");
            controller.addAbility(cat, shield);
            require(pc.getVariableValue("SPHERES_TECH_COMPACTSHIELD_COUNT", "").intValue() == 2,
                    "Capped repeat counter restored");
            rejected(controller, messages, cat, shield, "InfoAbility.Messages.NotQualified");
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