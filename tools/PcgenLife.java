package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Life resource formulas are references, not actual target healing or expenditure. */
class PcgenLife {
    private static void check(pcgen.core.PlayerCharacter pc, int cl, int mod, boolean deeper, boolean greater, boolean restore) {
        require(pc.getVariableValue("SPHERES_LIFE_CURE_DICE", "").intValue() == 1 + (deeper ? 1 + cl / 5 : 0), "Cure dice");
        require(pc.getVariableValue("SPHERES_LIFE_CURE_BONUS", "").intValue() == cl * (restore ? 2 : 1), "Cure bonus");
        require(pc.getVariableValue("SPHERES_LIFE_INVIGORATE_HP", "").intValue() == cl * (deeper ? 2 : 1) + (greater ? mod : 0), "Invigorate HP");
        require(pc.getVariableValue("SPHERES_LIFE_INVIGORATE_HOURS", "").intValue() == (greater ? cl : 1), "Invigorate hours");
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var sphere = ability(cat, "Life Sphere");
        var deeper = ability(cat, "Life - Deeper Healing");
        var greater = ability(cat, "Life - Greater Invigorate");
        var restore = ability(cat, "Life - Restore Health");
        boolean reload = args[4].equals("life-reload");
        int cl = pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue();
        int mod = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
        try {
            if (reload) {
                check(pc, cl, mod, true, true, true);
                controller.removeAbility(cat, deeper);
                controller.removeAbility(cat, greater);
                controller.removeAbility(cat, restore);
                controller.removeAbility(cat, sphere);
            }
            var pool = pc.getAvailableAbilityPool(cat);
            rejected(controller, messages, cat, greater, "InfoAbility.Messages.NotQualified");
            controller.addAbility(cat, sphere);
            check(pc, cl, mod, false, false, false);
            controller.addAbility(cat, greater);
            check(pc, cl, mod, false, true, false);
            controller.addAbility(cat, deeper);
            check(pc, cl, mod, true, true, false);
            controller.addAbility(cat, restore);
            check(pc, cl, mod, true, true, true);
            rejected(controller, messages, cat, greater, "InfoAbility.Messages.Duplicate");
            controller.removeAbility(cat, greater);
            check(pc, cl, mod, true, false, true);
            controller.removeAbility(cat, deeper);
            controller.removeAbility(cat, restore);
            check(pc, cl, mod, false, false, false);
            controller.removeAbility(cat, sphere);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Full talent refund");
            for (var selection : new pcgen.core.Ability[] {sphere, deeper, greater, restore}) controller.addAbility(cat, selection);
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