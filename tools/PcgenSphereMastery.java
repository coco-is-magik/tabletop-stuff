package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Class-specific full progression must not cancel another class's casting. */
class PcgenSphereMastery {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        int shifter = pc.getVariableValue("SPHERES_SHIFTER_LEVEL", "").intValue();
        int eliciter = pc.getVariableValue("SPHERES_ELICITER_LEVEL", "").intValue();
        int adept = pc.getVariableValue("SPHERES_FEY_ADEPT_LEVEL", "").intValue();
        int elementalist = pc.getVariableValue("SPHERES_ELEMENTALIST_LEVEL", "").intValue();
        int wraith = pc.getVariableValue("SPHERES_WRAITH_LEVEL", "").intValue();
        int hedgewitch = pc.getVariableValue("SPHERES_HEDGEWITCH_LEVEL", "").intValue();
        int mageknight = pc.getVariableValue("SPHERES_MAGEKNIGHT_LEVEL", "").intValue();
        int base = shifter * 3 / 4 + eliciter * 3 / 4 + adept + elementalist * 3 / 4 + wraith * 3 / 4 + hedgewitch * 3 / 4 + mageknight / 2;
        require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == base, "Ordinary caster level unchanged");
        if (shifter > 0) {
            int actual = pc.getVariableValue("SPHERES_CL_ALTERATION", "").intValue();
            require(actual == base + shifter - shifter * 3 / 4, "Alteration multiclass caster level: " + actual);
        }
        if (eliciter > 0) {
            int actual = pc.getVariableValue("SPHERES_CL_MIND", "").intValue();
            require(actual == base + eliciter - eliciter * 3 / 4, "Mind multiclass caster level: " + actual);
        }
        if (elementalist > 0) {
            int actual = pc.getVariableValue("SPHERES_CL_DESTRUCTION", "").intValue();
            require(actual == base + elementalist - elementalist * 3 / 4, "Destruction multiclass caster level: " + actual);
        }
        if (adept > 0) {
            require(pc.getVariableValue("SPHERES_CL_ILLUSION", "").intValue() == base, "Unrelated sphere unchanged");
        }
        var game = pcgen.core.SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("mastery-reload");
        try {
            if (mageknight >= 2) {
                var choices = game.getAbilityCategory("Mageknight Mystic Combat");
                var weirding = ability(choices, "Mageknight Weirding Adept");
                if (!reload) controller.addAbility(choices, weirding);
                require(pc.hasAbilityKeyed(choices, weirding.getKeyName()), "Retained Weirding Adept");
                require(pc.getVariableValue("SPHERES_MAGE_FEINT_CL", "").intValue() == base + mageknight - mageknight / 2, "Mage Feint preserves all other class contributions");
                require(pc.getVariableValue("SPHERES_CL_ILLUSION", "").intValue() == base, "Other Illusion effects unchanged");
                controller.removeAbility(choices, weirding);
                require(pc.getVariableValue("SPHERES_MAGE_FEINT_CL", "").intValue() == 0, "Mage Feint reference removal");
                controller.addAbility(choices, weirding);
            }
            if (wraith > 0) {
                var paths = game.getAbilityCategory("Wraith Haunt Path");
                var path = ability(paths, "Wraith Path of the Despoiler");
                if (reload) {
                    require(pc.hasAbilityKeyed(paths, path.getKeyName()), "Saved Wraith path");
                    require(pc.getVariableValue("SPHERES_CL_DEATH", "").intValue() == base + wraith - wraith * 3 / 4, "Saved Death mastery");
                    controller.removeAbility(paths, path);
                }
                controller.addAbility(paths, path);
                require(pc.getVariableValue("SPHERES_CL_DEATH", "").intValue() == base + wraith - wraith * 3 / 4, "Wraith preserves all caster contributions");
                controller.removeAbility(paths, path);
                controller.addAbility(game.getAbilityCategory("Spheres Magic Talent"), ability(game.getAbilityCategory("Spheres Magic Talent"), "Death Sphere"));
                require(pc.getVariableValue("SPHERES_CL_DEATH", "").intValue() == base, "Path removal removes only mastery");
                controller.removeAbility(game.getAbilityCategory("Spheres Magic Talent"), ability(game.getAbilityCategory("Spheres Magic Talent"), "Death Sphere"));
                controller.addAbility(paths, path);
            }
            if (hedgewitch > 0) {
                var paths = game.getAbilityCategory("Hedgewitch Path");
                var path = ability(paths, "Hedgewitch Transmuter");
                var magic = game.getAbilityCategory("Spheres Magic Talent");
                var creation = ability(magic, "Creation Sphere");
                if (reload) {
                    require(pc.hasAbilityKeyed(paths, path.getKeyName()), "Saved Transmuter path");
                    require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == base + hedgewitch - hedgewitch * 3 / 4, "Saved create-only progression");
                    controller.removeAbility(paths, path);
                    controller.removeAbility(magic, creation);
                }
                controller.addAbility(paths, path);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == 0, "Create requires Creation sphere");
                controller.addAbility(magic, creation);
                pc.calcActiveBonuses();
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == base + hedgewitch - hedgewitch * 3 / 4, "Transmuter preserves other casting contributions: actual=" + pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "") + " base=" + base + " creation=" + pc.getVariableValue("SPHERES_CL_CREATION", "") + " errors=" + messages.errors);
                require(pc.getVariableValue("SPHERES_CL_CREATION", "").intValue() == base, "Destroy and alter do not receive create-only mastery");
                controller.removeAbility(paths, path);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_CREATE_CL", "").intValue() == 0, "Lost Transmuter revokes create reference");
                controller.addAbility(paths, path);
            }
            if (hedgewitch >= 2) {
                var paths = game.getAbilityCategory("Hedgewitch Path");
                var secrets = game.getAbilityCategory("Hedgewitch Secret");
                var magic = game.getAbilityCategory("Spheres Magic Talent");
                var exorcism = ability(paths, "Hedgewitch Exorcism");
                var protection = ability(magic, "Protection Sphere");
                var ward = ability(secrets, "Hedgewitch Exorcism Warding Sanction");
                if (!reload) {
                    controller.addAbility(paths, exorcism);
                    controller.addAbility(magic, protection);
                    controller.addAbility(secrets, ward);
                } else {
                    require(pc.hasAbilityKeyed(secrets, ward.getKeyName()), "Saved Warding Sanction");
                }
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_WARD_CL", "").intValue() == base + hedgewitch - hedgewitch * 3 / 4, "Ward-only multiclass progression");
                require(pc.getVariableValue("SPHERES_CL_PROTECTION", "").intValue() == base, "Aegis keeps ordinary progression");
                controller.removeAbility(paths, exorcism);
                require(pc.getVariableValue("SPHERES_HEDGEWITCH_WARD_CL", "").intValue() == 0, "Lost Exorcism disables ward reference");
                controller.addAbility(paths, exorcism);
            }
            require(messages.errors.isEmpty(), "Path errors: " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        if (args[4].equals("mastery-save")) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}