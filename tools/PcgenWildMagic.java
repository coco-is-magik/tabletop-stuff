package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Wild-magic count thresholds without applying optional effects globally. */
class PcgenWildMagic {
    private static final String[] PICKS = {"Careful Caster", "Blood Dampening", "Inspired Surge",
        "Manipulate Result", "Risk Management", "Overpower Resistance"};

    private static void check(pcgen.core.PlayerCharacter pc, int count) {
        require(pc.getVariableValue("SPHERES_WILD_MAGIC_FEAT_COUNT", "").intValue() == count, "Wild feat count");
        if (count >= 1) require(pc.getVariableValue("SPHERES_CAREFUL_CASTER_REDUCTION", "").intValue()
            == Math.min(50, 25 + 5 * (count - 1)), "Careful Caster threshold");
        if (count >= 2) {
            require(pc.getVariableValue("SPHERES_BLOOD_DAMPENING_BURN", "").intValue() == (count >= 6 ? 1 : 2), "Burn cost");
            require(pc.getVariableValue("SPHERES_BLOOD_DAMPENING_MAJOR_BURN", "").intValue()
                == (count < 4 ? 0 : count >= 6 ? 3 : 4), "Major burn threshold");
        }
        if (count >= 3) require(pc.getVariableValue("SPHERES_INSPIRED_SURGE_TALENTS", "").intValue()
            == 1 + count / 5, "Temporary talent capacity");
        if (count >= 4) require(pc.getVariableValue("SPHERES_MANIPULATE_RESULT_USES", "").intValue() == count, "Manipulate uses");
        if (count >= 5) {
            require(pc.getVariableValue("SPHERES_RISK_MANAGEMENT_ROLLS", "").intValue() == 1, "Normal reroll count");
            require(pc.getVariableValue("SPHERES_RISK_MANAGEMENT_MAJOR_ROLLS", "").intValue() == (count >= 6 ? 4 : 0), "Major reroll threshold");
        }
        if (count >= 6) require(pc.getVariableValue("SPHERES_OVERPOWER_RESISTANCE_BONUS", "").intValue() == 2 + count / 2, "Conditional resistance check bonus");
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var feats = AbilityCategory.FEAT;
        boolean reload = args[4].equals("wild-reload");
        try {
            // The fixture deliberately supplies test-only feat slots.
            int msb = pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue();
            if (reload) {
                check(pc, PICKS.length);
                for (int i = PICKS.length - 1; i >= 0; i--) {
                    controller.removeAbility(feats, ability(feats, PICKS[i]));
                    check(pc, i);
                }
            }
            var pool = pc.getAvailableAbilityPool(feats);
            for (int i = 0; i < PICKS.length; i++) {
                controller.addAbility(feats, ability(feats, PICKS[i]));
                check(pc, i + 1);
                require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == msb, "No unconditional casting bonus");
            }
            var counter = ability(feats, "Counterspell");
            var chaotic = ability(feats, "Chaotic Counter");
            require(!chaotic.qualifies(pc, chaotic), "Counterspell prerequisite");
            controller.addAbility(feats, counter);
            // The alternative non-sphere dispel-magic route is not compiled yet.
            var reviews = game.getAbilityCategory("Spheres Feat Adjudication");
            var approval = ability(reviews, "Reviewed - Chaotic Counter");
            controller.addAbility(reviews, approval);
            int baseline = pc.getVariableValue("SPHERES_COUNTERSPELL_CHECK", "").intValue();
            controller.addAbility(feats, chaotic);
            require(pc.getVariableValue("SPHERES_COUNTERSPELL_CHECK", "").intValue() == baseline + 1, "Counterspell-only bonus");
            require(pc.getVariableValue("SPHERES_CHAOTIC_COUNTER_INCREASE", "").intValue() == 100, "Chance cap");
            controller.removeAbility(feats, chaotic);
            controller.removeAbility(reviews, approval);
            require(pc.getVariableValue("SPHERES_COUNTERSPELL_CHECK", "").intValue() == baseline, "Counterspell refund");
            controller.removeAbility(feats, counter);
            var shift = ability(feats, "Shift Cost");
            controller.addAbility(feats, shift);
            int level = pc.getTotalLevels();
            require(pc.getVariableValue("SPHERES_SHIFT_COST_REDUCTION", "").intValue() == (level >= 10 ? 2 : 1), "Shift Cost level boundary");
            controller.removeAbility(feats, shift);
            check(pc, 6);
            require(pc.getAvailableAbilityPool(feats).intValue() == pool.intValue() - 6, "Feat slot refunds");
            require(messages.errors.isEmpty(), "Unexpected errors: " + messages.errors);
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