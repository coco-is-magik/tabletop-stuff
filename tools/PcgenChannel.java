package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Channel feature identity, energy polarity, removal and retained feat gates. */
class PcgenChannel {
    private static void blessings(pcgen.core.PlayerCharacter pc, String polarity) {
        int level = pc.getVariableValue("SPHERES_SOUL_WEAVER_LEVEL", "").intValue();
        var special = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Special Ability");
        String[][] powers = {{"Blessing", "Heal", "Restore", "Revive", "Renew"},
            {"Blight", "Lesion", "Mind Blight", "Consume", "Detonate"}};
        for (int side = 0; side < powers.length; side++) {
            for (int i = 0; i < powers[side].length; i++) {
                boolean expected = level >= 2 + 4 * i && polarity.equals(side == 0 ? "Positive" : "Negative");
                require(pc.hasAbilityKeyed(special, "Soul Weaver " + powers[side][i]) == expected,
                    "Blessing/blight polarity and level: " + powers[side][i]);
            }
        }
        var mastery = ability(AbilityCategory.FEAT, "Blessing/Blight Mastery");
        require(mastery.qualifies(pc, mastery) == (level >= 2 && !polarity.equals("None")),
            "Blessing/Blight Mastery requires an actual granted power and channel");
    }
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var extraNexus = ability(AbilityCategory.FEAT, "Extra Nexus Powers");
        if (pc.getClassKeyed("Soul Weaver") != null) {
            var nexus = game.getAbilityCategory("Soul Weaver Nexus Powers");
            int soulLevel = pc.getVariableValue("SPHERES_SOUL_WEAVER_LEVEL", "").intValue();
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Soul Weaver Gravewalker")
                == (soulLevel >= 20), "Gravewalker level-20 immunity grant");
            String[][] tiers = {{"Aid the Dead", "Lovelorn Soul", "Siphon Health"},
                {"Curious Spirit", "Summon Spirit I"},
                {"Channel Mastery", "Summon Spirit II", "Divine Soul", "Blessed Soul"},
                {"Summon Spirit III", "Ghostpoint"},
                {"Summon Spirit IV", "Temporary Resurrection", "Trap Soul"}, {"Summon Spirit V"}};
            int[] at = {1, 4, 8, 12, 16, 20};
            for (int tier = 0; tier < tiers.length; tier++) {
                for (String power : tiers[tier]) {
                    require(pc.hasAbilityKeyed(nexus, "Soul Weaver " + power) == (soulLevel >= at[tier]),
                        "Automatic nexus level gate: " + power);
                }
            }
            require(pc.getAvailableAbilityPool(nexus).intValue() == 0, "Nexus powers are not purchased choices");
            if (args[4].equals("channel-reload")) {
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, extraNexus.getKeyName()), "Extra Nexus persistence");
                require(pc.getVariableValue("SPHERES_SOUL_WEAVER_BOUND_SOULS", "").intValue() == 9,
                    "Saved Extra Nexus capacity");
                controller.removeAbility(AbilityCategory.FEAT, extraNexus);
            }
            int charisma = pc.getVariableValue("CHA", "").intValue();
            require(pc.getVariableValue("SPHERES_SOUL_WEAVER_CHANNEL_DC", "").intValue() == 10 + soulLevel / 2 + charisma,
                "Channel DC uses Charisma and class level");
            require(pc.getVariableValue("SPHERES_SOUL_WEAVER_NEXUS_DC", "").intValue() == 14 + soulLevel / 2,
                "Nexus DC uses casting ability and class level");
            require(pc.getVariableValue("SPHERES_SOUL_WEAVER_CHANNEL_USES", "").intValue() == Math.max(1, 3 + charisma),
                "Channel uses must use Charisma and minimum one");
            require(pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue() == 4, "Intelligence casting fixture");
            require(pc.getVariableValue("SPHERES_SOUL_WEAVER_BOUND_SOULS", "").intValue() == 7,
                "Bound souls must use casting ability, not Charisma");
            var pool = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
            int repetitions = Math.min(2, pool.intValue());
            require(repetitions >= 1, "Extra Nexus fixture needs an available feat");
            for (int i = 1; i <= repetitions; i++) {
                controller.addAbility(AbilityCategory.FEAT, extraNexus);
                require(pc.getVariableValue("SPHERES_SOUL_WEAVER_BOUND_SOULS", "").intValue() == 7 + 2 * i,
                    "Repeated Extra Nexus grant");
            }
            for (int i = repetitions - 1; i >= 0; i--) {
                controller.removeAbility(AbilityCategory.FEAT, extraNexus);
                require(pc.getVariableValue("SPHERES_SOUL_WEAVER_BOUND_SOULS", "").intValue() == 7 + 2 * i,
                    "Partial Extra Nexus refund");
            }
            require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(pool), "Extra Nexus pool refund");
            controller.addAbility(AbilityCategory.FEAT, extraNexus);
        } else {
            require(!extraNexus.qualifies(pc, extraNexus), "Channel energy alone is not bound nexus");
        }
        var pulsing = ability(AbilityCategory.FEAT, "Pulsing Channel");
        if (pc.getClassKeyed("Cleric") != null && pc.getClassKeyed("Soul Weaver") != null) {
            var core = game.getAbilityCategory("Channel Energy");
            var soul = game.getAbilityCategory("Soul Weaver Channel");
            var clericChannel = ability(game.getAbilityCategory("Special Ability"), "Cleric ~ Channel Positive Energy");
            var soulChannel = ability(soul, "Soul Weaver Positive Channel");
            boolean reloadMixed = args[4].equals("channel-reload");
            try {
                if (reloadMixed) {
                    require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), clericChannel.getKeyName()),
                        "Mixed Cleric channel persisted");
                    require(pc.hasAbilityKeyed(soul, soulChannel.getKeyName()), "Mixed Soul Weaver channel persisted");
                } else {
                    controller.addAbility(core, clericChannel);
                    controller.addAbility(soul, soulChannel);
                }
                require(pc.getVariableValue("ClericChannelPositiveEnergyDice", "").intValue() == 3, "Independent Cleric dice");
                require(pc.getVariableValue("SPHERES_SOUL_WEAVER_CHANNEL_DICE", "").intValue() == 3, "Independent Soul Weaver dice");
                require(!pulsing.qualifies(pc, pulsing), "Two 3d6 pools must not qualify as 4d6");
                rejected(controller, messages, AbilityCategory.FEAT, pulsing, "InfoAbility.Messages.NotQualified");
                require(messages.errors.size() == 1, "Unexpected mixed channel errors: " + messages.errors);
            } finally {
                controller.closeCharacter();
            }
            if (!reloadMixed) {
                facade.setFile(Path.of(args[5]).toFile());
                require(CharacterManager.saveCharacter(facade), "Save failed");
            }
            System.out.println("SPHERES_GATES_OK: " + args[4]);
            System.exit(0);
        }
        boolean fourDice = pc.getVariableValue("TL", "").intValue() >= 7;
        if (pc.getClassKeyed("Paladin") != null) {
            try {
                var luck = ability(AbilityCategory.FEAT, "Channel Luck");
                var energized = ability(AbilityCategory.FEAT, "Energized Spell");
                require(luck.qualifies(pc, luck), "Paladin generic channel type");
                require(energized.qualifies(pc, energized), "Paladin positive polarity");
                require(pulsing.qualifies(pc, pulsing) == fourDice, "Paladin channel dice threshold");
                if (args[4].equals("channel-reload")) {
                    require(pc.hasAbilityKeyed(AbilityCategory.FEAT, luck.getKeyName()), "Saved Paladin channel feat");
                    controller.removeAbility(AbilityCategory.FEAT, luck);
                }
                controller.addAbility(AbilityCategory.FEAT, luck);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, luck.getKeyName()), "Paladin channel feat selection");
                require(messages.errors.isEmpty(), "Unexpected Paladin errors: " + messages.errors);
            } finally {
                controller.closeCharacter();
            }
            if (!args[4].equals("channel-reload")) {
                facade.setFile(Path.of(args[5]).toFile());
                require(CharacterManager.saveCharacter(facade), "Save failed");
            }
            System.out.println("SPHERES_GATES_OK: " + args[4]);
            System.exit(0);
        }
        boolean cleric = pc.getClassKeyed("Cleric") != null;
        var channels = game.getAbilityCategory(cleric ? "Channel Energy" : "Soul Weaver Channel");
        var lookup = cleric ? game.getAbilityCategory("Special Ability") : channels;
        var positive = ability(lookup, cleric ? "Cleric ~ Channel Positive Energy" : "Soul Weaver Positive Channel");
        var negative = ability(lookup, cleric ? "Cleric ~ Channel Negative Energy" : "Soul Weaver Negative Channel");
        var luck = ability(AbilityCategory.FEAT, "Channel Luck");
        var energized = ability(AbilityCategory.FEAT, "Energized Spell");
        var life = ability(AbilityCategory.FEAT, "Channel Life");
        var detonation = ability(AbilityCategory.FEAT, "Channeled Detonation");
        boolean reload = args[4].equals("channel-reload");
        try {
            if (reload) {
                blessings(pc, cleric ? "None" : "Negative");
                require(pc.hasAbilityKeyed(lookup, negative.getKeyName()), "Saved negative channel");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, luck.getKeyName()), "Saved channel feat");
                require(luck.qualifies(pc, luck), "Saved channel qualification");
                controller.removeAbility(AbilityCategory.FEAT, luck);
                controller.removeAbility(channels, negative);
            }
            require(!luck.qualifies(pc, luck), "Class levels alone must not replace channel selection");
            blessings(pc, "None");
            require(!pulsing.qualifies(pc, pulsing), "Channel dice require selected feature");
            require(!energized.qualifies(pc, energized), "Energized requires a channel polarity");
            require(!detonation.qualifies(pc, detonation), "Negative channel missing");
            rejected(controller, messages, AbilityCategory.FEAT, luck, "InfoAbility.Messages.NotQualified");
            var featPool = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
            var channelPool = pc.getAvailableAbilityPool(channels);
            controller.addAbility(channels, positive);
            blessings(pc, cleric ? "None" : "Positive");
            require(luck.qualifies(pc, luck), "Positive channel generic qualification");
            require(energized.qualifies(pc, energized), "Positive energized qualification");
            require(pulsing.qualifies(pc, pulsing) == fourDice, "Positive channel dice threshold");
            require(life.qualifies(pc, life) == !cleric, "Only Soul Weaver channel grants Life");
            require(!detonation.qualifies(pc, detonation), "Positive is not negative channel");
            controller.addAbility(AbilityCategory.FEAT, luck);
            controller.removeAbility(channels, positive);
            blessings(pc, "None");
            require(!luck.qualifies(pc, luck), "Channel prerequisite loss");
            require(!energized.qualifies(pc, energized), "Energized prerequisite loss");
            require(!pulsing.qualifies(pc, pulsing), "Channel dice prerequisite loss");
            controller.removeAbility(AbilityCategory.FEAT, luck);
            require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(featPool), "Feat refund");
            require(pc.getAvailableAbilityPool(channels).equals(channelPool), "Channel refund");
            controller.addAbility(channels, negative);
            blessings(pc, cleric ? "None" : "Negative");
            require(luck.qualifies(pc, luck), "Negative channel generic qualification");
            require(energized.qualifies(pc, energized), "Negative energized qualification");
            require(pulsing.qualifies(pc, pulsing) == fourDice, "Negative channel dice threshold");
            require(!life.qualifies(pc, life), "Negative channel does not grant Life");
            require(detonation.qualifies(pc, detonation) == (!cleric
                && pc.getVariableValue("SPHERES_CL_DEATH", "").intValue() >= 5),
                "Negative channel still requires Death sphere level");
            controller.addAbility(AbilityCategory.FEAT, luck);
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, luck.getKeyName()), "Channel feat selected");
            require(messages.errors.size() == 1, "Unexpected channel errors: " + messages.errors);
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