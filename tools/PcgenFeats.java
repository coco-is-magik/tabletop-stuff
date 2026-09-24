package pcgen.gui2.facade;

import java.nio.file.Path;
import java.math.BigDecimal;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Production-controller gates for feat prerequisites, effects and persistence. */
class PcgenFeats {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var feats = AbilityCategory.FEAT;
        boolean reload = args[4].equals("feats-reload");
        boolean might = args[6].equals("might");
        var talents = game.getAbilityCategory(might ? "Spheres Combat Talent" : "Spheres Magic Talent");
        String sphere = might ? "Fencing Sphere" : "Life Sphere";
        String focus = might ? "Combat Sphere Focus - Fencing" : "Sphere Focus - Life";
        String dc = might ? "SPHERES_DC_FENCING" : "SPHERES_DC_LIFE";
        try {
            if (reload) {
                require(pc.hasAbilityKeyed(feats, focus), "Focus not persisted");
                controller.removeAbility(feats, ability(feats, focus));
                if (might) {
                    require(pc.hasAbilityKeyed(feats, "Basic Magic Training"), "Basic Magic reload");
                    require(pc.hasAbilityKeyed(feats, "Advanced Magic Training"), "Advanced Magic reload");
                    require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 5, "Training caster level reload");
                    controller.removeAbility(game.getAbilityCategory("Spheres Basic Magic Sphere"),
                        ability(game.getAbilityCategory("Spheres Magic Talent"), "Life Sphere"));
                    controller.removeAbility(feats, ability(feats, "Advanced Magic Training"));
                    controller.removeAbility(feats, ability(feats, "Basic Magic Training"));
                }
            } else {
                controller.addAbility(talents, ability(talents, sphere));
            }
            int baseline = pc.getVariableValue(dc, "").intValue();
            var pool = pc.getAvailableAbilityPool(feats);
            controller.addAbility(feats, ability(feats, focus));
            require(pc.getVariableValue(dc, "").intValue() == baseline + 1, "Sphere focus DC");
            require(pc.getAvailableAbilityPool(feats).equals(pool.subtract(BigDecimal.ONE)), "Feat pool spending");
            rejected(controller, messages, feats, ability(feats, focus), "InfoAbility.Messages.Duplicate");
            controller.removeAbility(feats, ability(feats, focus));
            require(pc.getVariableValue(dc, "").intValue() == baseline, "Focus removal");
            require(pc.getAvailableAbilityPool(feats).equals(pool), "Feat refund");
            controller.addAbility(feats, ability(feats, focus));
            if (!might) {
                var counter = ability(feats, "Counterspell");
                var improved = ability(feats, "Improved Counterspell (Spheres)");
                if (reload) {
                    require(pc.hasAbilityKeyed(feats, improved.getKeyName()), "Counterspell chain reload");
                    controller.removeAbility(feats, improved);
                    controller.removeAbility(feats, counter);
                }
                rejected(controller, messages, feats, improved, "InfoAbility.Messages.NotQualified");
                controller.addAbility(feats, counter);
                require(improved.qualifies(pc, improved), "Counterspell chain not unlocked");
                controller.addAbility(feats, improved);
                require(pc.getVariableValue("SPHERES_COUNTERSPELL_ADDITIONAL_EFFECTS", "").intValue() == 2, "Counterspell scaling");
                var unresolved = ability(feats, "Extra Bestial Trait");
                rejected(controller, messages, feats, unresolved, "InfoAbility.Messages.NotQualified");
                var review = game.getAbilityCategory("Spheres Feat Adjudication");
                var approval = ability(review, "Reviewed - Extra Bestial Trait");
                controller.addAbility(review, approval);
                require(pc.getAvailableAbilityPool(review).intValue() == 0, "Approval has cost");
                require(unresolved.qualifies(pc, unresolved), "Approval failed");
                controller.removeAbility(review, approval);
                require(!unresolved.qualifies(pc, unresolved), "Approval removal failed");
                var empower = ability(feats, "Empower Spell (Spheres)");
                controller.addAbility(feats, empower);
                require(pc.getVariableValue("SPHERES_METAMAGIC_EMPOWERSPELL_COST", "").intValue() == 2, "Metamagic spell-point cost");
                controller.removeAbility(feats, empower);
                require(pc.getVariableValue("SPHERES_METAMAGIC_EMPOWERSPELL_COST", "").intValue() == 0, "Metamagic cost removal");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var extraCombat = ability(feats, "Extra Combat Talent");
                controller.addAbility(feats, extraCombat);
                controller.addAbility(combat, ability(combat, "Fencing Sphere"));
                require(pc.hasAbilityKeyed(combat, "Fencing Sphere"), "Cross-class combat sphere: " + messages.errors);
                var spec = ability(feats, "Combat Sphere Specialization - Fencing");
                controller.addAbility(feats, spec);
                require(pc.hasAbilityKeyed(feats, spec.getKeyName()), "Cross-class specialization: " + messages.errors);
                require(pc.getVariableValue("SPHERES_BAB_FENCING", "").intValue() == 8, "Low BAB specialization scaling: " + pc.getVariableValue("SPHERES_BAB_FENCING", ""));
                require(pc.getVariableValue("SPHERES_DC_FENCING", "").intValue() == 14, "Specialization DC scaling");
                require(pc.baseAttackBonus() == 5, "Specialization changed attack bonus");
                controller.removeAbility(feats, spec);
                controller.removeAbility(combat, ability(combat, "Fencing Sphere"));
                controller.removeAbility(feats, extraCombat);
            } else {
                var specialization = ability(feats, "Combat Sphere Specialization - Fencing");
                controller.addAbility(feats, specialization);
                require(pc.getVariableValue("SPHERES_BAB_FENCING", "").intValue() == 10, "Effective BAB exceeded level cap");
                require(pc.baseAttackBonus() == 10, "Specialization changed attack BAB");
                controller.removeAbility(feats, specialization);
                var extra = ability(feats, "Extra Combat Talent");
                var talentPool = pc.getAvailableAbilityPool(talents);
                controller.addAbility(feats, extra);
                controller.addAbility(feats, extra);
                require(pc.getAvailableAbilityPool(talents).equals(talentPool.add(BigDecimal.valueOf(2))), "Repeated feat talents");
                controller.removeAbility(feats, extra);
                controller.removeAbility(feats, extra);
                require(pc.getAvailableAbilityPool(talents).equals(talentPool), "Repeated feat refunds");
                var great = ability(feats, "Great Focus");
                rejected(controller, messages, feats, great, "InfoAbility.Messages.NotQualified");
                controller.addAbility(talents, ability(talents, "Shield Sphere"));
                require(great.qualifies(pc, great), "Two sphere prerequisite");
                controller.addAbility(feats, great);
                require(pc.getVariableValue("SPHERES_MARTIAL_FOCUS_CAPACITY", "").intValue() == 2, "Great Focus capacity");
                controller.removeAbility(feats, great);
                controller.removeAbility(talents, ability(talents, "Shield Sphere"));
                var basic = ability(feats, "Basic Magic Training");
                controller.addAbility(feats, basic);
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 1, "Basic Magic caster level");
                require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == 0, "Basic Magic bonus talents leaked");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 1, "Basic Magic spell pool");
                var basicPool = game.getAbilityCategory("Spheres Basic Magic Sphere");
                require(pc.getAvailableAbilityPool(basicPool).intValue() == 1, "Basic Magic sphere grant");
                var advanced = ability(feats, "Advanced Magic Training");
                require(advanced.qualifies(pc, advanced), "Advanced Magic qualification");
                controller.addAbility(feats, advanced);
                require(pc.hasAbilityKeyed(feats, advanced.getKeyName()), "Advanced Magic not selected: " + messages.errors);
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 5, "Advanced Magic low casting: " + pc.getVariableValue("SPHERES_CASTER_LEVEL", ""));
                require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == 10, "Advanced Magic skill bonus");
                controller.removeAbility(feats, advanced);
                controller.removeAbility(feats, basic);
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 0, "Magic training refund");
                controller.addAbility(feats, basic);
                controller.addAbility(feats, advanced);
                controller.addAbility(basicPool, ability(game.getAbilityCategory("Spheres Magic Talent"), "Life Sphere"));
                require(pc.getAvailableAbilityPool(basicPool).intValue() == 0, "Basic sphere cost");
                require(pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Magic Talent")).intValue() == 0, "Basic sphere spent paid talents");
            }
            require(messages.errors.stream().noneMatch(e -> e == null), "Invalid error state");
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