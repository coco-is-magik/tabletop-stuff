package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Life resource formulas are references, not actual target healing or expenditure. */
class PcgenLife {
    private static void check(pcgen.core.PlayerCharacter pc, int cl, int mod, boolean deeper, boolean greater, boolean restore) {
        pc.calcActiveBonuses();
        require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == cl,
            "Life must preserve caster level after recalculation");
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
        int cl = pc.getVariableValue("SPHERES_INCANTER_LEVEL", "").intValue();
        int mod = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
        try {
            if (reload) {
                for (var selected : new pcgen.core.Ability[] {sphere, deeper, greater, restore}) {
                    require(pc.hasAbilityKeyed(cat, selected.getKeyName()), "Missing saved Life selection " + selected);
                }
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
            var observer = ability(pcgen.core.AbilityCategory.FEAT, "Catty Observer");
            var diagnose = ability(cat, "Life - Diagnose");
            var protection = ability(cat, "Protection Sphere");
            var status = ability(cat, "Protection - Status");
            require(!observer.qualifies(pc, observer), "Catty Observer requires a complete alternative");
            controller.addAbility(cat, sphere);
            require(!observer.qualifies(pc, observer), "Life alone does not satisfy Diagnose alternative");
            controller.addAbility(cat, diagnose);
            require(observer.qualifies(pc, observer) == (cl >= 3), "Life and Diagnose still require MSB three");
            controller.removeAbility(cat, diagnose);
            require(!observer.qualifies(pc, observer), "Lost Diagnose revokes qualification");
            controller.removeAbility(cat, sphere);
            controller.addAbility(cat, protection);
            require(!observer.qualifies(pc, observer), "Protection alone does not satisfy Status alternative");
            controller.addAbility(cat, status);
            require(observer.qualifies(pc, observer) == (cl >= 3), "Protection and Status still require MSB three");
            controller.removeAbility(cat, status);
            require(!observer.qualifies(pc, observer), "Lost Status revokes qualification");
            controller.removeAbility(cat, protection);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Alternative prerequisite selection refunds");
            var destruction = ability(cat, "Destruction Sphere");
            var wall = ability(cat, "Destruction - Energy Wall");
            var orb = ability(cat, "Destruction - Explosive Orb");
            var shape = ability(pcgen.core.AbilityCategory.FEAT, "Shape Expert");
            require(!shape.qualifies(pc, shape), "Shape Expert requires Destruction");
            controller.addAbility(cat, destruction);
            require(!shape.qualifies(pc, shape), "Destruction alone cannot satisfy talent alternatives");
            for (var alternative : new pcgen.core.Ability[] {wall, orb}) {
                controller.addAbility(cat, alternative);
                require(shape.qualifies(pc, shape), "Each Shape Expert alternative independently qualifies");
                controller.removeAbility(cat, alternative);
                require(!shape.qualifies(pc, shape), "Removing sole Shape Expert alternative revokes qualification");
            }
            controller.removeAbility(cat, destruction);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Shape Expert prerequisite selection refunds");
            var telekinesis = ability(cat, "Telekinesis Sphere");
            var force = ability(pcgen.core.AbilityCategory.FEAT, "Skillful Force");
            controller.addAbility(cat, telekinesis);
            require(!force.qualifies(pc, force), "Telekinesis alone cannot satisfy Skillful Force");
            for (String name : new String[] {"Finesse", "Steal", "Telekinetic Tools"}) {
                var alternative = ability(cat, "Telekinesis - " + name);
                controller.addAbility(cat, alternative);
                require(force.qualifies(pc, force), "Each Skillful Force alternative independently qualifies: " + name);
                controller.removeAbility(cat, alternative);
                require(!force.qualifies(pc, force), "Lost Skillful Force alternative: " + name);
            }
            controller.removeAbility(cat, telekinesis);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Skillful Force prerequisite refunds");
            for (var selection : new pcgen.core.Ability[] {sphere, deeper, greater, restore}) controller.addAbility(cat, selection);
            check(pc, cl, mod, true, true, true);
            require(messages.errors.size() == 2, "Unexpected Life errors: " + messages.errors);
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