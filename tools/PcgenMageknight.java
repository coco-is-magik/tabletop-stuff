package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Production-controller regression for Mystic Combat prerequisites and grants. */
class PcgenMageknight {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var choices = game.getAbilityCategory("Mageknight Mystic Combat");
        var talents = game.getAbilityCategory("Spheres Magic Talent");
        int level = pc.getVariableValue("SPHERES_MAGEKNIGHT_LEVEL", "").intValue();
        boolean reload = args[4].equals("mageknight-reload");
        var shield = ability(choices, "Mageknight Spell Shield");
        var mirror = ability(choices, "Mageknight Spell Mirror (requires mageknight 10 - spell shield)");
        try {
            if (level >= 16 && reload) {
                var feats = game.getAbilityCategory("Mageknight Greater Combatant Feat");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"), "Chosen combat feat persistence");
                require(pc.getAvailableAbilityPool(feats).intValue() == 0, "Saved feat pool spend");
                controller.removeAbility(feats, ability(AbilityCategory.FEAT, "Improved Initiative"));
                controller.removeAbility(choices, ability(choices, "Mageknight Greater Combatant"));
            }
            if (reload) {
                require(pc.hasAbilityKeyed(choices, shield.getKeyName()), "Shield persistence");
                require(pc.hasAbilityKeyed(choices, mirror.getKeyName()) == (level >= 10), "Mirror persistence");
                if (level >= 10) controller.removeAbility(choices, mirror);
                controller.removeAbility(choices, shield);
                if (level >= 12) {
                    require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == 3 + level / 2 + 2, "Magic Power persistence");
                    require(pc.getVariableValue("SPHERES_COMBAT_TALENTS", "").intValue() == 2, "Combat Talent persistence");
                    for (String name : new String[] {"Magic Power", "Combat Talent"}) {
                        controller.removeAbility(choices, ability(choices, "Mageknight " + name));
                        controller.removeAbility(choices, ability(choices, "Mageknight " + name));
                    }
                }
            }
            for (String[] test : new String[][] {
                    {"Mageknight Elemental Defense (requires mystic defense)", "11"},
                    {"Mageknight Mark of Pain (requires marked)", "7"},
                    {"Mageknight Whirl of Blows (requires mageknight 6)", "6"}}) {
                var option = ability(choices, test[0]);
                boolean qualified = level >= Integer.parseInt(test[1]);
                require(option.qualifies(pc, option) == qualified, "Level prerequisite: " + test[0]);
                if (!qualified) rejected(controller, messages, choices, option, "InfoAbility.Messages.NotQualified");
            }
            if (level >= 4) {
                for (String name : new String[] {"Champion", "Greater Combatant"}) {
                    var option = ability(choices, "Mageknight " + name);
                    var feats = game.getAbilityCategory("Mageknight " + name + " Feat");
                    require(pc.getAvailableAbilityPool(feats).intValue() == 0, "No unearned feat pool");
                    controller.addAbility(choices, option);
                    controller.addAbility(choices, option);
                    require(pc.getAvailableAbilityPool(feats).intValue() == 2, "Repeated feat pool grant");
                    controller.removeAbility(choices, option);
                    require(pc.getAvailableAbilityPool(feats).intValue() == 1, "Partial feat pool refund");
                    if (name.equals("Greater Combatant")) {
                        rejected(controller, messages, feats, ability(AbilityCategory.FEAT, "Whirlwind Attack"),
                                "InfoAbility.Messages.NotQualified");
                        controller.addAbility(feats, ability(AbilityCategory.FEAT, "Improved Initiative"));
                        require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"), "Chosen combat feat grant");
                        require(pc.getAvailableAbilityPool(feats).intValue() == 0, "Chosen feat cost");
                        controller.removeAbility(feats, ability(AbilityCategory.FEAT, "Improved Initiative"));
                    }
                    controller.removeAbility(choices, option);
                    require(pc.getAvailableAbilityPool(feats).intValue() == 0, "Full feat pool refund");
                }
            }
            var strategic = ability(choices, "Mageknight Strategic Planning (requires War sphere)");
            rejected(controller, messages, choices, strategic, "InfoAbility.Messages.NotQualified");
            var war = ability(talents, "War Sphere");
            controller.addAbility(talents, war);
            require(strategic.qualifies(pc, strategic), "War requirement");
            controller.removeAbility(talents, war);
            require(!strategic.qualifies(pc, strategic), "War removal");
            var review = game.getAbilityCategory("Mageknight Mystic Combat Review");
            var approval = ability(review, "Reviewed - Black Dog Companion Curse Talent");
            var companion = ability(choices, "Mageknight Black Dog Companion (requires mageknight 4 - 1 talent with the curse descriptor)");
            rejected(controller, messages, choices, companion, "InfoAbility.Messages.NotQualified");
            if (level >= 4) {
                controller.addAbility(review, approval);
                require(companion.qualifies(pc, companion), "Curse review");
                controller.removeAbility(review, approval);
                require(!companion.qualifies(pc, companion), "Curse review removal");
            }
            if (level >= 4) {
                for (String[] test : new String[][] {{"Magic Power", "SPHERES_MAGIC_TALENTS"},
                                                    {"Combat Talent", "SPHERES_COMBAT_TALENTS"}}) {
                    var option = ability(choices, "Mageknight " + test[0]);
                    int base = pc.getVariableValue(test[1], "").intValue();
                    var pool = pc.getAvailableAbilityPool(choices);
                    controller.addAbility(choices, option);
                    controller.addAbility(choices, option);
                    require(pc.getVariableValue(test[1], "").intValue() == base + 2, "Repeated grant " + test[0]);
                    require(pc.getAvailableAbilityPool(choices).intValue() == pool.intValue() - 2, "Choice cost");
                    controller.removeAbility(choices, option);
                    require(pc.getVariableValue(test[1], "").intValue() == base + 1, "Partial refund " + test[0] + " base=" + base + " actual=" + pc.getVariableValue(test[1], "") + " errors=" + messages.errors);
                    controller.removeAbility(choices, option);
                    require(pc.getVariableValue(test[1], "").intValue() == base, "Full refund");
                    require(pc.getAvailableAbilityPool(choices).equals(pool), "Choice refund");
                }
            }
            for (String[] test : new String[][] {{"Sunder The Veil", "Pierce The Veil"},
                    {"Weirding Initiate", "Weird Defense"},
                    {"Whirl of Blows (requires mageknight 6)", "Whirlwind Attack"}}) {
                var option = ability(choices, "Mageknight " + test[0]);
                if (!option.qualifies(pc, option)) continue;
                controller.addAbility(choices, option);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, test[1]), "Bonus feat " + test[1]);
                controller.removeAbility(choices, option);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, test[1]), "Bonus feat removal " + test[1]);
            }
            rejected(controller, messages, choices, mirror, "InfoAbility.Messages.NotQualified");
            var adept = ability(choices, "Mageknight Weirding Adept");
            var initiate = ability(choices, "Mageknight Weirding Initiate");
            var master = ability(choices, "Mageknight Weirding Master");
            var illusion = ability(talents, "Illusion Sphere");
            var magicPool = pc.getAvailableAbilityPool(talents);
            controller.addAbility(choices, adept);
            require(!pc.hasAbilityKeyed(talents, "Illusion - Mage Feint"), "Adept without talent prerequisite or waiver");
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Weird Motion"), "Adept without feat prerequisite or waiver");
            controller.addAbility(talents, illusion);
            require(pc.hasAbilityKeyed(talents, "Illusion - Mage Feint"), "Adept grants qualified talent");
            require(pc.getVariableValue("SPHERES_MAGE_FEINT_CL", "").intValue() == level, "Mage Feint high caster progression");
            require(pc.getVariableValue("SPHERES_CL_ILLUSION", "").intValue() == level / 2, "Other Illusion effects retain low caster progression");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Weird Motion") == (level >= 3), "Normal Weird Motion BAB gate");
            controller.removeAbility(talents, illusion);
            require(!pc.hasAbilityKeyed(talents, "Illusion - Mage Feint"), "Talent prerequisite removal");
            if (level >= 4) {
                controller.addAbility(choices, initiate);
                require(pc.hasAbilityKeyed(talents, "Illusion - Mage Feint"), "Initiate waives talent prerequisite");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Weird Motion"), "Initiate waives feat prerequisites");
                controller.removeAbility(choices, initiate);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Weird Motion"), "Waiver removal revokes grant");
                controller.addAbility(choices, master);
                require(pc.hasAbilityKeyed(talents, "Illusion - Decoy"), "Adept waives Master talent prerequisite");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Weird Assault"), "Adept waives Master feat prerequisites");
                controller.removeAbility(choices, adept);
                require(!pc.hasAbilityKeyed(talents, "Illusion - Decoy"), "Master waiver removal");
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Weird Assault"), "Master feat waiver removal");
                controller.removeAbility(choices, master);
            } else {
                controller.removeAbility(choices, adept);
            }
            require(pc.getAvailableAbilityPool(talents).equals(magicPool), "Weirding grants do not spend talent slots");
            require(pc.getVariableValue("SPHERES_MAGE_FEINT_CL", "").intValue() == 0, "Removing Adept removes its caster-level value");
            controller.addAbility(choices, shield);
            require(mirror.qualifies(pc, mirror) == (level >= 10), "Mirror level and shield requirements");
            if (level >= 10) {
                controller.addAbility(choices, mirror);
                rejected(controller, messages, choices, mirror, "InfoAbility.Messages.Duplicate");
                controller.removeAbility(choices, shield);
                require(!mirror.qualifies(pc, mirror), "Shield removal revokes mirror qualification");
                controller.addAbility(choices, shield);
            }
            if (level >= 12) {
                for (String name : new String[] {"Magic Power", "Combat Talent"}) {
                    controller.addAbility(choices, ability(choices, "Mageknight " + name));
                    controller.addAbility(choices, ability(choices, "Mageknight " + name));
                }
                require(pc.getAvailableAbilityPool(choices).intValue() == level / 2 - 6, "Persisted selection costs");
            }
            if (level >= 16) {
                controller.addAbility(choices, ability(choices, "Mageknight Greater Combatant"));
                controller.addAbility(game.getAbilityCategory("Mageknight Greater Combatant Feat"),
                        ability(AbilityCategory.FEAT, "Improved Initiative"));
            }
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