package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Emotion tiers consume real choices; higher tiers require earlier powers. */
class PcgenEliciter {
    public static void main(String[] args) throws Exception {
        require(args.length == 6, "character template output config gate saved required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Eliciter Emotion");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_ELICITER_LEVEL", "").intValue();
        boolean reload = args[4].equals("eliciter-reload");
        String[] tiers = {"", " - Lesser", " - Greater", " - Master"};
        int count = level < 2 ? 0 : Math.min(4, 1 + (level - 2) / 3);
        try {
            var feats = pcgen.core.AbilityCategory.FEAT;
            var extra = ability(feats, "Extra Emotion");
            var strike = ability(feats, "Elicit Strike");
            require(extra.qualifies(pc, extra) == (level >= 2), "Emotion feature qualification");
            require(strike.qualifies(pc, strike) == (level >= 2), "Elicit Strike feature qualification");
            if (reload && level >= 2) {
                require(pc.hasAbilityKeyed(feats, extra.getKeyName()), "Extra Emotion persisted");
                controller.removeAbility(feats, extra);
            }
            var featPool = pc.getAvailableAbilityPool(feats);
            var emotionPool = pc.getAvailableAbilityPool(cat);
            if (level >= 2) {
                for (int i = 1; i <= 2; i++) {
                    controller.addAbility(feats, extra);
                    require(pc.getAvailableAbilityPool(cat).subtract(emotionPool).intValue() == i,
                        "Repeated Extra Emotion grant");
                    require(featPool.subtract(pc.getAvailableAbilityPool(feats)).intValue() == i,
                        "Extra Emotion feat cost");
                }
                for (int i = 1; i >= 0; i--) {
                    controller.removeAbility(feats, extra);
                    require(pc.getAvailableAbilityPool(cat).subtract(emotionPool).intValue() == i,
                        "Partial Extra Emotion refund");
                }
                require(pc.getAvailableAbilityPool(feats).equals(featPool), "Extra Emotion full refund");
            } else {
                rejected(controller, messages, feats, extra, "InfoAbility.Messages.NotQualified");
            }
            int persuasive = 2 + level / 6;
            require(pc.getVariableValue("SPHERES_ELICITER_PERSUASIVE", "").intValue() == persuasive, "Persuasive progression");
            require(pc.getVariableValue("SPHERES_ELICITER_CLASS_DC", "").intValue() == 10 + level / 2 + 3 + persuasive,
                    "Emotion DC uses Charisma and persuasive bonus");
            for (String skill : new String[] {"Bluff", "Diplomacy", "Intimidate"}) {
                require(pc.getTotalBonusTo("SKILL", skill) == persuasive, "Persuasive skill bonus: " + skill);
            }
            int cl = pc.getVariableValue("SPHERES_CL_MIND", "").intValue();
            int casting = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
            require(pc.getVariableValue("SPHERES_DC_MIND", "").intValue() == 10 + cl / 2 + casting + persuasive,
                    "Mind sphere DC bonus");
            if (reload) {
                for (int i = count - 1; i >= 0; i--) {
                    String key = "Eliciter Apathy" + tiers[i];
                    require(pc.hasAbilityKeyed(cat, key), "Saved emotion: " + key);
                    controller.removeAbility(cat, ability(cat, key));
                }
                require(pc.getAvailableAbilityPool(cat).equals(pc.getTotalAbilityPool(cat)), "Saved emotion refunds");
            }
            rejected(controller, messages, cat, ability(cat, "Eliciter Apathy - Lesser"), "InfoAbility.Messages.NotQualified");
            var pool = pc.getAvailableAbilityPool(cat);
            for (int i = 0; i < count; i++) {
                var power = ability(cat, "Eliciter Apathy" + tiers[i]);
                require(power.qualifies(pc, power), "Qualifying emotion tier " + i);
                controller.addAbility(cat, power);
                require(pc.hasAbilityKeyed(cat, power.getKeyName()), "Selected emotion tier " + i);
                require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == i + 1, "Each tier spends one choice");
            }
            if (count < 4) {
                rejected(controller, messages, cat, ability(cat, "Eliciter Apathy" + tiers[count]), "InfoAbility.Messages.NotQualified");
            }
            if (count > 1) {
                var minor = ability(cat, "Eliciter Apathy");
                controller.removeAbility(cat, minor);
                var lesser = ability(cat, "Eliciter Apathy - Lesser");
                require(!lesser.qualifies(pc, lesser), "Removing earlier tier revokes qualification");
                controller.addAbility(cat, minor);
                require(lesser.qualifies(pc, lesser), "Restoring earlier tier restores qualification");
            }
            if (level >= 2) controller.addAbility(feats, extra);
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