package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.core.AbilityCategory;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Persistent bonuses and at-will selections, not invocation activation. */
class PcgenThaumaturge {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory("Thaumaturge Master Invoker");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_THAUMATURGE_LEVEL", "").intValue();
        int modifier = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
        var blessing = ability(cat, "Thaumaturge Master Invoker - Lingering Blessing");
        var defense = ability(cat, "Thaumaturge Master Invoker - Empowered Defense");
        boolean reload = args[4].equals("thaumaturge-reload");
        try {
            var magic = game.getAbilityCategory("Spheres Magic Talent");
            var mana = ability(magic, "Mana Sphere");
            var tainted = ability(AbilityCategory.FEAT, "Tainted Manabond");
            require(!tainted.qualifies(pc, tainted), "Forbidden lore alone does not grant Mana qualification");
            var magicPool = pc.getAvailableAbilityPool(magic);
            controller.addAbility(magic, mana);
            require(tainted.qualifies(pc, tainted), "Mana plus forbidden lore must qualify");
            controller.addAbility(AbilityCategory.FEAT, tainted);
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, tainted.getKeyName()), "Tainted Manabond selection");
            controller.removeAbility(magic, mana);
            require(!tainted.qualifies(pc, tainted), "Tainted Manabond sphere prerequisite loss");
            controller.removeAbility(AbilityCategory.FEAT, tainted);
            require(pc.getAvailableAbilityPool(magic).equals(magicPool), "Mana refund");
            int bonus = level < 2 ? 0 : Math.min(5, 1 + (level - 2) / 4);
            for (String skill : new String[] {"Knowledge (Arcana)", "Knowledge (Nature)", "Spellcraft", "Use Magic Device"}) {
                var record = Globals.getContext().getReferenceContext()
                    .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, skill);
                int ability = pcgen.core.analysis.SkillModifier.getStatMod(record, pc);
                require(pcgen.core.analysis.SkillModifier.modifier(record, pc).intValue() == ability + bonus,
                    "Occult Knowledge: " + skill);
            }
            require(pc.getTotalBonusTo("SKILL", "Climb") == 0, "Occult Knowledge must not affect unrelated skills");
            require(pc.getVariableValue("SPHERES_THAUMATURGE_INVOCATION_DC", "").intValue() == 10 + level / 2 + modifier,
                "Invocation saving throw DC");
            var extra = ability(AbilityCategory.FEAT, "Extra Invocations");
            int uses = modifier + level / 2;
            require(pc.getVariableValue("SPHERES_THAUMATURGE_INVOCATION_USES", "").intValue() == uses, "Base uses");
            controller.addAbility(AbilityCategory.FEAT, extra);
            require(pc.getVariableValue("SPHERES_THAUMATURGE_INVOCATION_USES", "").intValue() == uses + 2, "Extra uses");
            controller.removeAbility(AbilityCategory.FEAT, extra);
            require(pc.getVariableValue("SPHERES_THAUMATURGE_INVOCATION_USES", "").intValue() == uses, "Uses refund");
            var bonusFeats = game.getAbilityCategory("Thaumaturge Bonus Feat");
            var talentFeat = ability(AbilityCategory.FEAT, "Extra Magic Talent");
            require(talentFeat.isType("SpheresCasting"), "Bonus feat type must include Extra Magic Talent");
            if (level >= 4) {
                var available = pc.getAvailableAbilityPool(bonusFeats);
                var ordinary = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
                int talents = pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue();
                int repeats = Math.min(2, level / 4);
                for (int i = 1; i <= repeats; i++) {
                    controller.addAbility(bonusFeats, talentFeat);
                    require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == talents + i,
                        "Bonus feat actually grants a magic talent");
                    require(pc.getAvailableAbilityPool(bonusFeats).intValue() == available.intValue() - i,
                        "Bonus feat spends class pool");
                }
                for (int i = repeats - 1; i >= 0; i--) {
                    controller.removeAbility(bonusFeats, talentFeat);
                    require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == talents + i,
                        "Bonus talent partial refund");
                }
                require(pc.getAvailableAbilityPool(bonusFeats).equals(available), "Bonus feat refund");
                require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(ordinary), "Ordinary feat pool isolation");
            }
            if (level < 20) {
                require(pc.getTotalAbilityPool(cat).intValue() == 0, "Early mastery pool");
                rejected(controller, messages, cat, blessing, "InfoAbility.Messages.NotQualified");
            } else {
                if (reload) {
                    require(pc.hasAbilityKeyed(cat, blessing.getKeyName()), "Saved blessing mastery");
                    require(pc.hasAbilityKeyed(cat, defense.getKeyName()), "Saved defense mastery");
                    require(pc.getAvailableAbilityPool(cat).intValue() == 0, "Saved mastery pool");
                    controller.removeAbility(cat, blessing);
                    require(pc.getAvailableAbilityPool(cat).intValue() == 1, "Partial mastery refund");
                    controller.removeAbility(cat, defense);
                }
                require(pc.getAvailableAbilityPool(cat).intValue() == 2, "Mastery full pool");
                controller.addAbility(cat, blessing);
                rejected(controller, messages, cat, blessing, "InfoAbility.Messages.Duplicate");
                controller.addAbility(cat, defense);
                require(pc.getAvailableAbilityPool(cat).intValue() == 0, "Two mastery slots spent");
                require(pc.getVariableValue("SPHERES_THAUMATURGE_INVOCATION_USES", "").intValue() == uses,
                    "Mastery must not change daily uses for other invocations");
            }
            require(messages.errors.size() == 1, "Unexpected controller errors: " + messages.errors);
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