package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Shared Drone/AI caps through the production selection controller. */
class PcgenTechLimits {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Combat Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var sphere = ability(cat, "Tech Sphere");
        var drone = ability(cat, "Tech - Drone");
        var ai = ability(cat, "Tech - Artificial Intelligence");
        var feats = pcgen.core.AbilityCategory.FEAT;
        var mobile = ability(feats, "Mobile Drone");
        boolean reload = args[4].equals("techlimits-reload");
        try {
            if (reload) {
                require(pc.getVariableValue("SPHERES_TECH_DRONE_AI_COUNT", "").intValue() == 4, "Saved combined counter");
                rejected(controller, messages, cat, drone, "InfoAbility.Messages.NotQualified");
                rejected(controller, messages, cat, ai, "InfoAbility.Messages.NotQualified");
                for (int i = 0; i < 2; i++) {
                    controller.removeAbility(cat, drone);
                    controller.removeAbility(cat, ai);
                }
                controller.removeAbility(cat, sphere);
            }
            var pool = pc.getAvailableAbilityPool(cat);
            rejected(controller, messages, cat, ai, "InfoAbility.Messages.NotQualified");
            rejected(controller, messages, cat, drone, "InfoAbility.Messages.NotQualified");
            controller.addAbility(cat, sphere);
            var ammunition = ability(feats, "Technologically Alchemical Ammo");
            var spitter = ability(cat, "Tech - Ammo Spitter");
            var alchemy = ability(cat, "Alchemy Sphere");
            var packages = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Alchemy Package");
            var formulae = ability(packages, "Alchemy Package - Formulae");
            var poison = ability(packages, "Alchemy Package - Poison");
            require(!ammunition.qualifies(pc, ammunition), "Tech alone must not satisfy ammunition prerequisites");
            controller.addAbility(cat, spitter);
            require(pc.hasAbilityKeyed(cat, spitter.getKeyName()), "Ammo Spitter purchase");
            require(!ammunition.qualifies(pc, ammunition), "Ammo Spitter alone lacks Alchemy package");
            controller.addAbility(cat, alchemy);
            require(pc.hasAbilityKeyed(cat, alchemy.getKeyName()), "Alchemy purchase");
            require(!ammunition.qualifies(pc, ammunition), "Alchemy without Formulae must fail");
            controller.addAbility(packages, poison);
            require(pc.hasAbilityKeyed(packages, poison.getKeyName()), "Poison package purchase");
            require(!ammunition.qualifies(pc, ammunition), "Poison cannot substitute for Formulae");
            controller.removeAbility(packages, poison);
            controller.addAbility(packages, formulae);
            require(pc.hasAbilityKeyed(packages, formulae.getKeyName()), "Formulae package purchase");
            require(ammunition.qualifies(pc, ammunition), "Explicit sphere, talent and Formulae qualify");
            controller.removeAbility(cat, spitter);
            require(!ammunition.qualifies(pc, ammunition), "Lost Ammo Spitter prerequisite");
            controller.addAbility(cat, spitter);
            require(ammunition.qualifies(pc, ammunition), "Restoring Ammo Spitter restores qualification");
            controller.removeAbility(packages, formulae);
            require(!ammunition.qualifies(pc, ammunition), "Lost Formulae prerequisite");
            controller.removeAbility(cat, alchemy);
            controller.removeAbility(cat, spitter);
            require(!mobile.qualifies(pc, mobile), "Tech alone must not unlock Drone feats");
            rejected(controller, messages, feats, mobile, "InfoAbility.Messages.NotQualified");
            for (var selection : new pcgen.core.Ability[] {drone, ai}) {
                for (int i = 1; i <= 4; i++) {
                    controller.addAbility(cat, selection);
                    require(pc.getVariableValue("SPHERES_TECH_DRONE_AI_COUNT", "").intValue() == i, "Single-family counter " + i);
                    require(mobile.qualifies(pc, mobile) == (selection == drone), "AI must not substitute for Drone");
                }
                rejected(controller, messages, cat, drone, "InfoAbility.Messages.NotQualified");
                rejected(controller, messages, cat, ai, "InfoAbility.Messages.NotQualified");
                for (int i = 3; i >= 0; i--) {
                    controller.removeAbility(cat, selection);
                    require(pc.getVariableValue("SPHERES_TECH_DRONE_AI_COUNT", "").intValue() == i, "Partial counter refund " + i);
                }
                require(!mobile.qualifies(pc, mobile), "Removing last Drone revokes feat qualification");
            }
            controller.removeAbility(cat, sphere);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Full paid-pool refund");
            controller.addAbility(cat, sphere);
            for (int i = 0; i < 2; i++) {
                controller.addAbility(cat, drone);
                controller.addAbility(cat, ai);
            }
            rejected(controller, messages, cat, drone, "InfoAbility.Messages.NotQualified");
            rejected(controller, messages, cat, ai, "InfoAbility.Messages.NotQualified");
            controller.removeAbility(cat, ai);
            controller.addAbility(cat, drone);
            require(pc.getVariableValue("SPHERES_TECH_DRONE_AI_COUNT", "").intValue() == 4, "Cross-family replacement");
            controller.removeAbility(cat, drone);
            controller.addAbility(cat, ai);
            require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == 5, "Mixed selections cost five paid talents including sphere");
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