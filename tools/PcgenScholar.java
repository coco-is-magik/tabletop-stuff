package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.core.Skill;
import pcgen.core.analysis.SkillModifier;
import pcgen.core.analysis.SkillRankControl;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Knack gates and repeated talent grants through the production controller. */
class PcgenScholar {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory("Scholar Scholar'S Knack");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_SCHOLAR_LEVEL", "").intValue();
        int intMod = pc.getVariableValue("INT", "").intValue();
        int wisMod = pc.getVariableValue("WIS", "").intValue();
        boolean reload = args[4].equals("scholar-reload");
        var studied = ability(cat, "Scholar Studied Technique");
        try {
            var medical = game.getAbilityCategory("Scholar Medical Ability");
            var intelligence = ability(medical, "Scholar Intelligence for Heal");
            if (reload) {
                require(pc.hasAbilityKeyed(medical, intelligence.getKeyName()), "Saved medical ability choice");
                controller.removeAbility(medical, intelligence);
            }
            double originalHeal = pc.getTotalBonusTo("SKILL", "Heal");
            controller.addAbility(medical, intelligence);
            require(pc.getTotalBonusTo("SKILL", "Heal") == originalHeal + intMod - wisMod, "Optional Intelligence substitution");
            controller.removeAbility(medical, intelligence);
            require(pc.getTotalBonusTo("SKILL", "Heal") == originalHeal, "Restore Wisdom for Heal");
            require(pc.getVariableValue("SPHERES_SCHOLAR_MEDICAL_ATTEMPTS_PER_PATIENT", "").intValue() == Math.max(1, intMod),
                    "Medical attempts per patient");
            require(pc.getVariableValue("SPHERES_SCHOLAR_MEDICAL_HP_MULTIPLIER", "").intValue()
                    == (level < 5 ? 1 : level < 9 ? 2 : 3), "Medical healing progression");
            var heal = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Heal");
            var scholar = pc.getClassKeyed("Scholar");
            for (int ranks : new int[] {0, 4, 5, 7, 8, 10, 11}) {
                if (ranks > level) continue;
                double previous = SkillRankControl.getTotalRank(pc, heal).doubleValue();
                require(SkillRankControl.modRanks(ranks - previous, scholar, true, pc, heal).isEmpty(), "Set medical test ranks");
                pc.calcActiveBonuses();
                require(pc.getVariableValue("SPHERES_SCHOLAR_MEDICAL_ABILITY_DAMAGE", "").intValue()
                        == (ranks >= 5 ? 1 : 0), "Ability damage rank gate");
                require(pc.getVariableValue("SPHERES_SCHOLAR_MEDICAL_ABILITY_DRAIN", "").intValue()
                        == (level >= 5 && ranks >= 8 ? 1 : 0), "Ability drain gates");
                require(pc.getVariableValue("SPHERES_SCHOLAR_MEDICAL_REVIVE", "").intValue()
                        == (level >= 9 && ranks >= 11 ? 1 : 0), "Revival gates");
            }
            require(SkillRankControl.modRanks(-SkillRankControl.getTotalRank(pc, heal).doubleValue(),
                    scholar, true, pc, heal).isEmpty(), "Remove medical test ranks");
            pc.calcActiveBonuses();
            if (reload) {
                require(pc.getVariableValue("SPHERES_SCHOLAR_STUDIED_TECHNIQUE", "").intValue() == 1, "Saved repeat count");
                var before = pc.getTotalAbilityPool(combat);
                controller.removeAbility(cat, studied);
                require(before.subtract(pc.getTotalAbilityPool(combat)).intValue() == 3, "Saved talent grant refund");
            }
            for (String[] test : new String[][] {
                    {"Animal Training - Large", "Animal Training - Small"},
                    {"Genetic Modification", "Animal Training - Small"},
                    {"Arcane Studies", "Amateur Arcanist"},
                    {"Breakthrough Historian", "Amateur Arcanist"},
                    {"Crafting Genius", "Amateur Arcanist"},
                    {"Chronomancy", "Chronomancy - Amateur"},
                    {"Lightning Rod - Improved", "Lightning Rod"},
                    {"Ritual Crafter", "Ritual Student"}}) {
                var dependent = ability(cat, "Scholar " + test[0]);
                var parent = ability(cat, "Scholar " + test[1]);
                rejected(controller, messages, cat, dependent, "InfoAbility.Messages.NotQualified");
                controller.addAbility(cat, parent);
                require(dependent.qualifies(pc, dependent), "Knack prerequisite " + test[0]);
                controller.removeAbility(cat, parent);
                require(!dependent.qualifies(pc, dependent), "Removed prerequisite " + test[0]);
            }
            var injections = ability(cat, "Scholar Liquefying Injections");
            var academic = ability(cat, "Scholar Academic Knowledge");
            var healing = ability(cat, "Scholar Expert Healing");
            double healBefore = pc.getTotalBonusTo("SKILL", "Heal");
            controller.addAbility(cat, healing);
            require(pc.getTotalBonusTo("SKILL", "Heal") == healBefore + Math.max(1, level / 2), "Expert Healing bonus");
            controller.removeAbility(cat, healing);
            require(pc.getTotalBonusTo("SKILL", "Heal") == healBefore, "Expert Healing refund");
            controller.addAbility(cat, academic);
            for (String skill : new String[] {"Knowledge (Arcana)", "Knowledge (Nature)", "Knowledge (Religion)"}) {
                var entry = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, skill);
                require(SkillModifier.modifier(entry, pc) == intMod + Math.max(1, level / 2), "Academic Knowledge " + skill);
            }
            controller.removeAbility(cat, academic);
            require(pc.getTotalBonusTo("SKILL", "TYPE.Knowledge") == 0, "Knowledge bonus removal");
            var astrology = ability(cat, "Scholar Astrology");
            controller.addAbility(cat, astrology);
            require(pc.getVariableValue("SPHERES_SCHOLAR_INSIGHT_CAPACITY", "").intValue() == Math.max(0, intMod) + Math.max(1, level / 2), "Insight capacity");
            controller.removeAbility(cat, astrology);
            require(injections.qualifies(pc, injections) == (level >= 6), "Injection level gate");
            if (level < 6) rejected(controller, messages, cat, injections, "InfoAbility.Messages.NotQualified");
            var base = pc.getTotalAbilityPool(combat);
            var pool = pc.getAvailableAbilityPool(cat);
            int count = Math.min(3, level / 2);
            for (int i = 1; i <= count; i++) {
                controller.addAbility(cat, studied);
                require(pc.getTotalAbilityPool(combat).subtract(base).intValue() == 3 * i, "Three talents per knack");
            }
            if (count == 3) rejected(controller, messages, cat, studied, "InfoAbility.Messages.NotQualified");
            for (int i = count - 1; i >= 0; i--) {
                controller.removeAbility(cat, studied);
                require(pc.getTotalAbilityPool(combat).subtract(base).intValue() == 3 * i, "Partial/full talent refund");
            }
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Knack pool refund");
            controller.addAbility(cat, studied);
            controller.addAbility(medical, intelligence);
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