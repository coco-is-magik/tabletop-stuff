package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Feat equivalence qualifies prerequisites without granting the imitated effects. */
class PcgenFeatEquivalence {
    private static boolean qualifies(pcgen.core.PlayerCharacter pc, String feat) {
        var requirement = new pcgen.core.PCTemplate();
        requirement.setName("Equivalence prerequisite " + feat);
        require(Globals.getContext().processToken(requirement, "PREFEAT", "1," + feat), "Prerequisite fixture");
        Globals.getContext().commit();
        return requirement.qualifies(pc, requirement);
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("equivalence-reload");
        var feats = AbilityCategory.FEAT;
        var triumph = ability(feats, "Liberating Triumph");
        var skeptic = ability(feats, "Vigilant Skeptic");
        var alertness = ability(feats, "Alertness");
        var perception = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Perception");
        var casterClass = pc.getClassKeyed("Fey Adept");
        var magic = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
        var analyze = ability(feats, "Analyze Caster");
        var mana = ability(magic, "Mana Sphere");
        var divination = ability(magic, "Divination Sphere");
        var detect = ability(magic, "Divination - Detect Spellcaster");
        require(casterClass != null, "Skill ranks need a persistent class owner");
        try {
            if (reload) {
                if (pc.getTotalLevels() >= 9) {
                    require(pc.hasAbilityKeyed(feats, "Analyze Caster"), "Saved Analyze Caster selection");
                    require(analyze.qualifies(pc, analyze), "Saved Analyze Caster prerequisites");
                    require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Determine casting tradition with Detect Spellcaster") == 5, "Saved Analyze Caster bonus");
                    controller.removeAbility(feats, analyze);
                    controller.removeAbility(magic, detect);
                    controller.removeAbility(magic, divination);
                    controller.removeAbility(magic, mana);
                }
                require(pc.hasAbilityKeyed(feats, "Vigilant Skeptic"), "Saved Skeptic selection");
                require(pcgen.core.analysis.SkillRankControl.getTotalRank(pc, perception).intValue() == 3, "Saved Perception ranks");
                require(pc.getVariableValue("SPHERES_SKEPTIC_FIGMENT_RANGE", "").intValue() == 10, "Saved interaction range");
                require(pc.getTotalBonusTo("SITUATION", "Perception=Target benefiting from a glamer") == pc.getTotalLevels() / 2, "Saved situational bonus");
                controller.removeAbility(feats, skeptic);
                controller.removeAbility(feats, alertness);
                require(pc.hasAbilityKeyed(feats, "Liberating Triumph"), "Saved equivalence feat");
                for (String feat : new String[] {"Great Fortitude", "Lightning Reflexes", "Iron Will"})
                    require(qualifies(pc, feat), "Saved equivalence " + feat);
                controller.removeAbility(feats, triumph);
            }
            double fort = pc.getTotalBonusTo("CHECKS", "FORTITUDE");
            double reflex = pc.getTotalBonusTo("CHECKS", "REFLEX");
            double will = pc.getTotalBonusTo("CHECKS", "WILL");
            for (String feat : new String[] {"Great Fortitude", "Lightning Reflexes", "Iron Will"})
                require(!qualifies(pc, feat), "Absent equivalence " + feat);
            controller.addAbility(feats, triumph);
            for (String feat : new String[] {"Great Fortitude", "Lightning Reflexes", "Iron Will"})
                require(qualifies(pc, feat), "Triumph equivalence " + feat);
            require(pc.getTotalBonusTo("CHECKS", "FORTITUDE") == fort && pc.getTotalBonusTo("CHECKS", "REFLEX") == reflex
                && pc.getTotalBonusTo("CHECKS", "WILL") == will, "No imitated saving throw bonuses");
            var source = new pcgen.core.PCTemplate();
            source.setName("Galvanized prerequisite fixture");
            require(Globals.getContext().processToken(source, "ABILITY", "Custom Casting Drawback|AUTOMATIC|Tradition - Galvanized"), "Drawback fixture");
            Globals.getContext().commit();
            var caster = ability(feats, "Combatant Caster");
            require(!caster.qualifies(pc, caster), "Combatant Caster requires drawback");
            pc.addTemplate(source);
            controller.addAbility(feats, caster);
            require(qualifies(pc, "Combat Casting"), "Combatant Caster equivalence");
            controller.removeAbility(feats, caster);
            require(!qualifies(pc, "Combat Casting"), "Combat Casting equivalence refund");
            pc.removeTemplate(source);
            require(!skeptic.qualifies(pc, skeptic), "Skeptic needs Alertness or both skill ranks");
            controller.addAbility(feats, alertness);
            require(skeptic.qualifies(pc, skeptic), "Alertness route");
            double perceptionBonus = pc.getTotalBonusTo("SKILL", "Perception");
            double motiveBonus = pc.getTotalBonusTo("SKILL", "Sense Motive");
            controller.addAbility(feats, skeptic);
            require(!analyze.qualifies(pc, analyze), "Analyze Caster requires its spheres and talent");
            controller.addAbility(magic, mana);
            require(!analyze.qualifies(pc, analyze), "Mana alone is insufficient");
            controller.addAbility(magic, divination);
            require(!analyze.qualifies(pc, analyze), "Detect Spellcaster is independently required");
            controller.addAbility(magic, detect);
            require(analyze.qualifies(pc, analyze) == (pc.getTotalLevels() >= 9), "Analyze Caster level boundary");
            if (pc.getTotalLevels() >= 9) {
                double spellcraft = pc.getTotalBonusTo("SKILL", "Spellcraft");
                controller.addAbility(feats, analyze);
                require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Determine casting tradition with Detect Spellcaster") == 5, "Analyze Caster scoped bonus");
                require(pc.getTotalBonusTo("SKILL", "Spellcraft") == spellcraft, "No ordinary Spellcraft bonus");
                controller.removeAbility(feats, analyze);
                require(pc.getTotalBonusTo("SITUATION", "Spellcraft=Determine casting tradition with Detect Spellcaster") == 0, "Analyze Caster refund");
                controller.removeAbility(magic, detect);
                require(!analyze.qualifies(pc, analyze), "Loss of Detect Spellcaster revokes qualification");
                controller.addAbility(magic, detect);
                controller.addAbility(feats, analyze);
            } else {
                controller.removeAbility(magic, detect);
                controller.removeAbility(magic, divination);
                controller.removeAbility(magic, mana);
            }
            require(pc.getTotalBonusTo("SKILL", "Perception") == perceptionBonus && pc.getTotalBonusTo("SKILL", "Sense Motive") == motiveBonus, "No general skill increase on selection");
            for (int ranks : new int[] {0, 1, 2, 3}) {
                double current = pcgen.core.analysis.SkillRankControl.getTotalRank(pc, perception).doubleValue();
                require(pcgen.core.analysis.SkillRankControl.modRanks(ranks - current, casterClass, true, pc, perception).isEmpty(), "Perception fixture ranks");
                require(pc.getVariableValue("SPHERES_SKEPTIC_FIGMENT_RANGE", "").intValue() == 5 + 5 * (ranks / 2), "Interaction range rank rounding");
            }
            for (String skill : new String[] {"Perception", "Sense Motive"})
                require(pc.getTotalBonusTo("SITUATION", skill + "=Target benefiting from a glamer") == pc.getTotalLevels() / 2, "Glamer-only level bonus");
            perceptionBonus = pc.getTotalBonusTo("SKILL", "Perception");
            motiveBonus = pc.getTotalBonusTo("SKILL", "Sense Motive");
            controller.removeAbility(feats, skeptic);
            require(pc.getTotalBonusTo("SKILL", "Perception") == perceptionBonus && pc.getTotalBonusTo("SKILL", "Sense Motive") == motiveBonus, "No general skill change on refund");
            require(pc.getTotalBonusTo("SITUATION", "Perception=Target benefiting from a glamer") == 0, "Skeptic refund");
            controller.addAbility(feats, skeptic);
            require(messages.errors.isEmpty(), "Unexpected errors " + messages.errors);
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