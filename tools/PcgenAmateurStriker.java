package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Amateur tension choice, capacity, prerequisite-loss and persistence checks. */
class PcgenAmateurStriker {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var feats = game.getAbilityCategory("FEAT");
        var methods = game.getAbilityCategory("Amateur Striker Method");
        var techniques = game.getAbilityCategory("Amateur Striker Technique");
        var amateur = ability(feats, "Amateur Striker");
        var expanded = ability(feats, "Expanded Tension Technique");
        var expandedSlots = game.getAbilityCategory("Expanded Tension Technique");
        var expandedChoice = ability(expandedSlots, "Expanded Tension - Expert Guard");
        var expandedDuplicate = ability(expandedSlots, "Expanded Tension - Swift Focus");
        var method = ability(methods, "Amateur Striker - Offensive Pressure");
        var technique = ability(techniques, "Amateur Striker - Swift Focus");
        var extraArt = ability(feats, "Extra Striker Art");
        var artSlots = game.getAbilityCategory("Striker Striker Art");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].endsWith("reload");
        try {
            if (reload) {
                require(pc.hasAbilityKeyed(expandedSlots, expandedChoice.getKeyName()), "Saved expanded technique");
                require(pc.getAvailableAbilityPool(expandedSlots).intValue() == 0, "Saved expanded slot cost");
                controller.removeAbility(expandedSlots, expandedChoice);
                controller.removeAbility(feats, expanded);
                require(pc.hasAbilityKeyed(feats, "Amateur Striker"), "Saved feat");
                require(pc.hasAbilityKeyed(methods, method.getKeyName()), "Saved method");
                require(pc.hasAbilityKeyed(techniques, technique.getKeyName()), "Saved technique");
                require(pc.getAvailableAbilityPool(methods).intValue() == 0, "Saved method cost");
                require(pc.getAvailableAbilityPool(techniques).intValue() == 0, "Saved technique cost");
                controller.removeAbility(methods, method);
                controller.removeAbility(techniques, technique);
                controller.removeAbility(feats, amateur);
            }
            require(!expanded.qualifies(pc, expanded), "Non-Striker without feat lacks tension");
            require(!method.qualifies(pc, method), "Method requires feat");
            var constitution = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.PCStat.class, "CON");
            pc.setStat(constitution, 12);
            pc.calcActiveBonuses();
            require(!amateur.qualifies(pc, amateur), "Constitution prerequisite");
            pc.setStat(constitution, 16);
            pc.calcActiveBonuses();
            require(amateur.qualifies(pc, amateur), "Eligible non-Striker");
            controller.addAbility(feats, amateur);
            require(expanded.qualifies(pc, expanded), "Amateur supplies tension pool");
            require(pc.baseAttackBonus() == 5 && extraArt.qualifies(pc, extraArt), "Amateur BAB qualifies Extra Striker Art");
            controller.addAbility(feats, extraArt);
            require(pc.getAvailableAbilityPool(artSlots).intValue() == 1, "Amateur extra-art slot");
            require(!extraArt.qualifies(pc, extraArt), "BAB five permits only one extra art");
            controller.removeAbility(feats, extraArt);
            require(pc.getAvailableAbilityPool(artSlots).intValue() == 0, "Amateur extra-art refund");
            require(pc.getAvailableAbilityPool(methods).intValue() == 1, "One method slot");
            require(pc.getAvailableAbilityPool(techniques).intValue() == 1, "One technique slot");
            require(pc.getVariableValue("SPHERES_AMATEUR_STRIKER_CAPACITY", "").intValue() == 3, "Constitution capacity");
            controller.addAbility(methods, method);
            controller.addAbility(techniques, technique);
            controller.addAbility(feats, expanded);
            require(!expandedDuplicate.qualifies(pc, expandedDuplicate), "Cannot learn known amateur technique");
            controller.addAbility(expandedSlots, expandedChoice);
            require(pc.getAvailableAbilityPool(expandedSlots).intValue() == 0, "Expanded slot spent");
            require(!ability(techniques, "Amateur Striker - Expert Guard").qualifies(pc, amateur), "Reverse duplicate blocked");
            controller.addAbility(feats, expanded);
            require(pc.getAvailableAbilityPool(expandedSlots).intValue() == 1, "Repeat feat adds another slot");
            controller.removeAbility(feats, expanded);
            require(pc.getAvailableAbilityPool(expandedSlots).intValue() == 0, "Partial expanded refund");
            controller.removeAbility(feats, expanded);
            require(!expandedChoice.qualifies(pc, expandedChoice), "Lost expanded feat invalidates choice");
            require(pc.getAvailableAbilityPool(expandedSlots).intValue() == -1, "Lost expanded slot remains overspent");
            controller.addAbility(feats, expanded);
            controller.removeAbility(feats, amateur);
            require(!expandedChoice.qualifies(pc, expandedChoice), "Lost tension source invalidates expanded choice");
            require(!expanded.qualifies(pc, expanded), "Lost feat revokes tension prerequisite");
            require(!technique.qualifies(pc, technique), "Lost feat invalidates chosen technique");
            require(pc.getAvailableAbilityPool(methods).intValue() == -1, "Unsupported method remains visibly overspent");
            require(pc.getVariableValue("SPHERES_AMATEUR_STRIKER_CAPACITY", "").intValue() == 0, "Capacity refund");
            controller.addAbility(feats, amateur);
            require(pc.getAvailableAbilityPool(methods).intValue() == 0, "Restored method capacity");
            require(pc.getAvailableAbilityPool(techniques).intValue() == 0, "Restored technique capacity");
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