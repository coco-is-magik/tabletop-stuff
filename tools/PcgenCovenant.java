package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Covenant choice, shared capacities, alignment rejection and persistence. */
class PcgenCovenant {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var paths = game.getAbilityCategory("Hedgewitch Path");
        var secrets = game.getAbilityCategory("Hedgewitch Secret");
        var energy = game.getAbilityCategory("Hedgewitch Covenant Energy");
        var path = ability(paths, "Hedgewitch Covenant");
        var extra = ability(secrets, "Hedgewitch Covenant Extra Healing");
        var positive = ability(energy, "Hedgewitch Covenant Positive");
        var negative = ability(energy, "Hedgewitch Covenant Negative");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int count = Math.min(2, level / 2);
        int base = 3 + level / 2;
        boolean reload = args[4].endsWith("reload");
        var channelSlots = game.getAbilityCategory("Hedgewitch Channel Feat");
        var channelSecret = ability(secrets, "Hedgewitch Covenant Channel Feats");
        var luck = ability(game.getAbilityCategory("FEAT"), "Channel Luck");
        int retainedChannel = level >= 6 ? 1 : 0;
        var smite = ability(secrets, "Hedgewitch Covenant Smite");
        try {
            if (reload) {
                if (level >= 10) {
                    require(pc.hasAbilityKeyed(secrets, smite.getKeyName()), "Saved Smite selection");
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_SMITE_USES", "").intValue() == 1, "Saved Smite capacity");
                    controller.removeAbility(secrets, smite);
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_SMITE_USES", "").intValue() == 0, "Saved Smite refund");
                }
                if (retainedChannel == 1) {
                    require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Channel Luck"), "Saved bonus channel feat");
                    require(pc.getAvailableAbilityPool(channelSlots).intValue() == 0, "Saved channel feat expenditure");
                    controller.removeAbility(channelSlots, luck);
                    controller.removeAbility(secrets, channelSecret);
                }
                require(pc.hasAbilityKeyed(energy, "Hedgewitch Covenant Positive"), "Saved energy choice");
                require(pc.getAvailableAbilityPool(energy).intValue() == 0, "Saved energy slot spent");
                require(pc.getAvailableAbilityPool(secrets).intValue() == level / 2 - count, "Saved secret cost");
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_USES", "").intValue() == base + 4 * count, "Saved shared capacity");
                controller.removeAbility(energy, positive);
                for (int i = count - 1; i >= 0; i--) {
                    controller.removeAbility(secrets, extra);
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_USES", "").intValue() == base + 4 * i, "Partial healing refund");
                }
            }
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_USES", "").intValue() == base, "Base touch capacity");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_DICE", "").intValue() == Math.max(1, level / 2), "Touch/channel dice floor");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_DIE_SIZE", "").intValue() == (level >= 20 ? 8 : 6), "Mastery die size");
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_DC", "").intValue() == 10 + level / 2, "Channel DC");
            for (String alignment : new String[] {"LG", "NG", "CG", "LN", "TN", "CN", "LE", "NE", "CE"}) {
                var value = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.PCAlignment.class, alignment);
                pcgen.output.channel.compat.AlignmentCompat.setCurrentAlignment(pc.getCharID(), value);
                pc.calcActiveBonuses();
                require(positive.qualifies(pc, positive) == !alignment.endsWith("E"), "Positive alignment " + alignment);
                require(negative.qualifies(pc, negative) == !alignment.endsWith("G"), "Negative alignment " + alignment);
            }
            var neutral = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.PCAlignment.class, "TN");
            pcgen.output.channel.compat.AlignmentCompat.setCurrentAlignment(pc.getCharID(), neutral);
            pc.calcActiveBonuses();
            controller.addAbility(energy, positive);
            var pulsing = ability(game.getAbilityCategory("FEAT"), "Pulsing Channel");
            var war = ability(game.getAbilityCategory("Spheres Magic Talent"), "War Sphere");
            var succor = ability(game.getAbilityCategory("FEAT"), "Succor");
            controller.addAbility(game.getAbilityCategory("Spheres Magic Talent"), war);
            require(succor.qualifies(pc, succor), "Positive Covenant qualifies lay on hands feat");
            controller.removeAbility(energy, positive);
            controller.addAbility(energy, negative);
            require(!succor.qualifies(pc, succor), "Negative Covenant is not lay on hands");
            controller.removeAbility(energy, negative);
            controller.addAbility(energy, positive);
            controller.removeAbility(game.getAbilityCategory("Spheres Magic Talent"), war);
            require(!succor.qualifies(pc, succor), "Touch equivalence does not bypass sphere requirement");
            require(smite.qualifies(pc, smite) == (level >= 10), "Grand secret level gate");
            if (level >= 10) {
                var attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                controller.addAbility(secrets, smite);
                controller.addAbility(secrets, smite);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_SMITE_USES", "").intValue() == 2, "Repeated smite capacity");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Smite is not unconditional attack bonus");
                controller.removeAbility(paths, path);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_SMITE_USES", "").intValue() == 0, "Lost smite path");
                controller.addAbility(paths, path);
                controller.removeAbility(secrets, smite);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_SMITE_USES", "").intValue() == 1, "Partial smite refund");
                controller.removeAbility(secrets, smite);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_SMITE_USES", "").intValue() == 0, "Smite refund");
            }
            require(pulsing.qualifies(pc, pulsing) == (level >= 8 && level < 20), "Covenant independent 4d6 prerequisite");
            controller.removeAbility(energy, positive);
            require(!pulsing.qualifies(pc, pulsing), "Channel dice require energy selection");
            controller.addAbility(energy, negative);
            require(pulsing.qualifies(pc, pulsing) == (level >= 8 && level < 20), "Negative Covenant independent 4d6 prerequisite");
            controller.removeAbility(energy, negative);
            controller.addAbility(energy, positive);
            var channelLife = ability(game.getAbilityCategory("FEAT"), "Channel Life");
            var magic = game.getAbilityCategory("Spheres Magic Talent");
            var life = ability(magic, "Life Sphere");
            controller.addAbility(magic, life);
            require(channelLife.qualifies(pc, channelLife), "Covenant satisfies positive channel prerequisite");
            controller.removeAbility(magic, life);
            require(luck.isType("HedgewitchChannelFeat"), "Channel prerequisite family");
            if (level >= 2) {
                controller.addAbility(secrets, channelSecret);
                require(pc.getAvailableAbilityPool(channelSlots).intValue() == 1, "Channel feat slot");
                controller.addAbility(channelSlots, luck);
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Channel Luck"), "Channel feat selection");
                require(pc.getAvailableAbilityPool(channelSlots).intValue() == 0, "Channel feat slot spent");
                controller.removeAbility(channelSlots, luck);
                if (level >= 4) {
                    controller.addAbility(secrets, channelSecret);
                    require(pc.getAvailableAbilityPool(channelSlots).intValue() == 2, "Repeat channel secret");
                    controller.removeAbility(paths, path);
                    require(pc.getAvailableAbilityPool(channelSlots).intValue() == 0, "Path loss suppresses slots");
                    controller.addAbility(paths, path);
                    controller.removeAbility(secrets, channelSecret);
                    require(pc.getAvailableAbilityPool(channelSlots).intValue() == 1, "Partial channel secret refund");
                }
                controller.removeAbility(secrets, channelSecret);
                require(pc.getAvailableAbilityPool(channelSlots).intValue() == 0, "Channel feat refund");
            } else {
                require(!channelSecret.qualifies(pc, channelSecret), "Channel secret level gate");
            }
            for (int i = 1; i <= count; i++) {
                controller.addAbility(secrets, extra);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_USES", "").intValue() == base + i * 4, "Repeated healing");
            }
            if (level == 1) require(!extra.qualifies(pc, extra), "Secret level boundary");
            controller.removeAbility(paths, path);
            require(!pulsing.qualifies(pc, pulsing), "Channel dice require retained Covenant path");
            require(!positive.qualifies(pc, positive), "Energy requires path");
            require(!extra.qualifies(pc, extra), "Secret requires path");
            require(!channelLife.qualifies(pc, channelLife), "Lost covenant cannot qualify channel feat");
            for (String suffix : new String[] {"USES", "DICE", "DIE_SIZE", "DC"}) {
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_" + suffix, "").intValue() == 0, "Lost path suppresses " + suffix);
            }
            controller.addAbility(paths, path);
            require(pc.getVariableValue("SPHERES_HEDGEWITCH_COVENANT_USES", "").intValue() == base + count * 4, "Restored shared capacity");
            if (retainedChannel == 1) {
                controller.addAbility(secrets, channelSecret);
                controller.addAbility(channelSlots, luck);
            }
            if (level >= 10) controller.addAbility(secrets, smite);
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