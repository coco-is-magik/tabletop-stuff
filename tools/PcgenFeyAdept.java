package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Shadow feat stacking, refunds, prerequisite rejection and retained selections. */
class PcgenFeyAdept {
    private static int value(pcgen.core.PlayerCharacter pc, String suffix) {
        return pc.getVariableValue("SPHERES_FEY_ADEPT_" + suffix, "").intValue();
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var feats = AbilityCategory.FEAT;
        var extra = ability(feats, "Extra Shadowstuff");
        var greater = ability(feats, "Greater Shadowmark");
        boolean reload = args[4].equals("fey-reload");
        boolean fey = pc.getClassKeyed("Fey Adept") != null;
        int baseline = Math.max(1, pc.getVariableValue("CHA", "").intValue() + value(pc, "LEVEL") / 2);
        try {
            var shadowMagic = ability(feats, "Shadow Magic");
            if (reload && !fey && pc.getTotalLevels() >= 3) {
                require(pc.hasAbilityKeyed(feats, shadowMagic.getKeyName()), "Saved Shadow Magic");
                require(pc.getVariableValue("SPHERES_SURREAL_FEAT_COUNT", "").intValue() == 3, "Saved surreal feat count");
                require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_TALENT_CAPACITY", "").intValue() == 1, "Saved temporary talent capacity");
                require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_EFFECT_CL", "").intValue() == Math.max(1, pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() - 2), "Saved Shadow Magic CL without Illusion selection");
                controller.removeAbility(feats, shadowMagic);
            }
            if (fey) {
                var talents = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
                var aura = ability(talents, "Illusion - Manipulate Aura");
                var emulation = ability(feats, "Emulation Expert");
                require(!emulation.qualifies(pc, emulation), "Emulation requires Manipulate Aura independently");
                controller.addAbility(talents, aura);
                require(emulation.qualifies(pc, emulation) == (value(pc, "LEVEL") >= 6), "Create reality level-six boundary");
                controller.addAbility(feats, shadowMagic);
                require(emulation.qualifies(pc, emulation), "Shadow Magic alternative to create reality");
                controller.removeAbility(feats, shadowMagic);
                require(emulation.qualifies(pc, emulation) == (value(pc, "LEVEL") >= 6), "Shadow Magic route removal");
                controller.removeAbility(talents, aura);
                require(!emulation.qualifies(pc, emulation), "Aura removal revokes Emulation Expert");
            }
            var strike = ability(feats, "Surreal Strike");
            if (reload && !fey) {
                require(pc.hasAbilityKeyed(feats, strike.getKeyName()), "Surreal Strike persistence");
                int savedLevel = Math.max(1, pc.getTotalLevels() - 4);
                require(value(pc, "SHADOWMARK_DICE") == (savedLevel + 1) / 2, "Saved Surreal Strike dice");
                require(value(pc, "SHADOWMARK_PENALTY") == 1 + (savedLevel - 1) / 6, "Saved Surreal Strike penalty");
                controller.removeAbility(feats, strike);
                require(value(pc, "SHADOWMARK_DICE") == 0, "Saved Surreal Strike removal");
            }
            int originalDice = value(pc, "SHADOWMARK_DICE");
            int originalPoints = value(pc, "SHADOW_POINTS");
            controller.addAbility(feats, strike);
            int effective = Math.max(value(pc, "LEVEL"), Math.max(1, pc.getTotalLevels() - 4));
            require(value(pc, "SHADOWMARK_DICE") == (effective + 1) / 2, "Surreal Strike strongest source damage");
            require(value(pc, "SHADOWMARK_PENALTY") == 1 + (effective - 1) / 6, "Surreal Strike penalty");
            require(value(pc, "SHADOW_POINTS") == originalPoints + 1, "Surreal Strike does not grant class pool");
            require(greater.qualifies(pc, greater), "Surreal Strike unlocks shadowmark feats");
            controller.removeAbility(feats, strike);
            require(value(pc, "SHADOWMARK_DICE") == originalDice, "Surreal Strike source removal");
            require(value(pc, "SHADOW_POINTS") == originalPoints, "Surreal Strike point refund");
            if (reload && !fey) {
                var shield = ability(feats, "Shadow Shield");
                require(pc.hasAbilityKeyed(feats, shield.getKeyName()), "Standalone surreal feat persistence");
                require(value(pc, "SHADOW_POINTS") == 1, "Standalone pool persistence");
                controller.removeAbility(feats, shield);
                require(value(pc, "SHADOW_POINTS") == 0, "Persisted standalone pool removal");
            }
            require(shadowMagic.qualifies(pc, shadowMagic) == fey, "Shadow pool class route");
            if (!fey) {
                var talents = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
                var illusion = ability(talents, "Illusion Sphere");
                var infusion = ability(talents, "Illusion - Shadow Infusion");
                controller.addAbility(talents, illusion);
                require(!shadowMagic.qualifies(pc, shadowMagic), "Illusion alone is not a shadow pool");
                controller.addAbility(talents, infusion);
                require(shadowMagic.qualifies(pc, shadowMagic), "Shadow Infusion alternative");
                controller.addAbility(feats, shadowMagic);
                require(value(pc, "SHADOW_POINTS") == 1, "First surreal feat grants standalone pool");
                require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_EFFECT_CL", "").intValue()
                    == Math.max(1, pc.getVariableValue("SPHERES_CL_ILLUSION", "").intValue() - 2), "Shadow Magic scoped CL and floor: actual=" + pc.getVariableValue("SPHERES_SHADOW_MAGIC_EFFECT_CL", "") + " illusion=" + pc.getVariableValue("SPHERES_CL_ILLUSION", "") + " sculptor=" + pc.getVariableValue("SPHERES_HEDGEWITCH_SHADOW_MAGIC_CL_BONUS", ""));
                require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_TALENT_CAPACITY", "").intValue() == 1, "Initial temporary talent capacity");
                String[] capacityFeats = pc.getTotalLevels() >= 8
                    ? new String[] {"Shadow Shield", "Shadowstuff Armament", "Shadowy Slay", "Surreal Strike"}
                    : new String[] {};
                for (int i = 0; i < capacityFeats.length; i++) {
                    controller.addAbility(feats, ability(feats, capacityFeats[i]));
                    require(pc.getVariableValue("SPHERES_SURREAL_FEAT_COUNT", "").intValue() == i + 2, "Distinct surreal feat count");
                    require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_TALENT_CAPACITY", "").intValue() == 1 + (i + 2) / 5, "Five-feat capacity boundary");
                }
                for (int i = capacityFeats.length - 1; i >= 0; i--) {
                    controller.removeAbility(feats, ability(feats, capacityFeats[i]));
                    require(pc.getVariableValue("SPHERES_SHADOW_MAGIC_TALENT_CAPACITY", "").intValue() == 1 + (i + 1) / 5, "Capacity partial refund");
                }
                controller.removeAbility(talents, infusion);
                require(!shadowMagic.qualifies(pc, shadowMagic), "Shadow Magic cannot supply its own prerequisite pool");
                controller.removeAbility(feats, shadowMagic);
                require(value(pc, "SHADOW_POINTS") == 0, "Standalone shadow pool refund");
                require(!shadowMagic.qualifies(pc, shadowMagic), "Infusion removal revokes qualification");
                controller.removeAbility(talents, illusion);
                var shield = ability(feats, "Shadow Shield");
                controller.addAbility(feats, shield);
                int level = pc.getTotalLevels();
                require(pc.getVariableValue("SPHERES_SHADOW_SHIELD_DICE", "").intValue() == level, "Shield temporary HP dice");
                require(pc.getVariableValue("SPHERES_SHADOW_SHIELD_RANGE", "").intValue() == 25 + 5 * (level / 2), "Shield range");
                require(pc.getVariableValue("SPHERES_SHADOW_SHIELD_REDUCTION", "").intValue() == 1 + level / 5, "Shield reduction scaling");
                var improvedShield = ability(feats, "Improved Shadow Shield");
                controller.addAbility(feats, improvedShield);
                require(pc.getVariableValue("SPHERES_SHADOW_SHIELD_HP_BONUS", "").intValue() == level, "Improved shield flat HP");
                require(pc.getVariableValue("SPHERES_SHADOW_SHIELD_ALL_DAMAGE", "").intValue() == 1, "Improved shield replaces DR with all-damage reduction");
                controller.removeAbility(feats, improvedShield);
                require(pc.getVariableValue("SPHERES_SHADOW_SHIELD_HP_BONUS", "").intValue() == 0, "Improved shield refund");
                require(shadowMagic.qualifies(pc, shadowMagic), "Independent surreal feat supplies pool");
                controller.addAbility(feats, shadowMagic);
                require(value(pc, "SHADOW_POINTS") == 2, "Distinct surreal feats stack capacity");
                controller.removeAbility(feats, shield);
                require(!shadowMagic.qualifies(pc, shadowMagic), "Independent pool source removed");
                controller.removeAbility(feats, shadowMagic);
            }
            for (String name : new String[] {"Gather Shadowstuff", "Shadowblast"}) {
                var shadowFeat = ability(feats, name);
                require(shadowFeat.qualifies(pc, shadowFeat) == fey, "Shadowmark feature requirement: " + name);
            }
            if (!fey) {
                rejected(controller, messages, feats, extra, "InfoAbility.Messages.NotQualified");
                rejected(controller, messages, feats, greater, "InfoAbility.Messages.NotQualified");
            } else {
                if (reload) {
                    require(pc.hasAbilityKeyed(feats, extra.getKeyName()), "Extra Shadowstuff persistence");
                    require(pc.hasAbilityKeyed(feats, greater.getKeyName()), "Greater Shadowmark persistence");
                    require(value(pc, "SHADOW_POINTS") == baseline + 5, "Repeat grants and surreal point persisted");
                    require(value(pc, "SHADOWMARK_DIE_SIZE") == 8, "d8 persisted");
                    controller.removeAbility(feats, extra);
                    require(value(pc, "SHADOW_POINTS") == baseline + 3, "Partial repeat refund on reload");
                    controller.removeAbility(feats, extra);
                    controller.removeAbility(feats, greater);
                }
                var pool = pc.getAvailableAbilityPool(feats);
                int spellPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                int dice = value(pc, "SHADOWMARK_DICE");
                require(value(pc, "SHADOW_POINTS") == baseline, "Baseline shadow points");
                require(value(pc, "SHADOWMARK_DIE_SIZE") == 6, "Baseline d6");
                for (int count = 1; count <= 2; count++) {
                    controller.addAbility(feats, extra);
                    require(value(pc, "SHADOW_POINTS") == baseline + 2 * count, "Stacked shadow points");
                    require(pc.getVariableValue("SPHERES_SURREAL_FEAT_COUNT", "").intValue() == 0, "Extra shadow points are not surreal feats");
                }
                controller.addAbility(feats, greater);
                require(value(pc, "SHADOW_POINTS") == baseline + 5, "Surreal feat stacks with class pool and Extra Shadowstuff");
                require(value(pc, "SHADOWMARK_DIE_SIZE") == 8, "Greater Shadowmark d8");
                require(value(pc, "SHADOWMARK_DICE") == dice, "Greater Shadowmark must not change dice count");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == spellPoints,
                    "Shadow points are not spell points");
                rejected(controller, messages, feats, greater, "InfoAbility.Messages.Duplicate");
                controller.removeAbility(feats, greater);
                require(value(pc, "SHADOWMARK_DIE_SIZE") == 6, "Die size refund");
                controller.removeAbility(feats, extra);
                require(value(pc, "SHADOW_POINTS") == baseline + 2, "Partial shadow refund");
                controller.removeAbility(feats, extra);
                require(value(pc, "SHADOW_POINTS") == baseline, "Full shadow refund");
                require(pc.getAvailableAbilityPool(feats).equals(pool), "Feat pool refund");
                controller.addAbility(feats, extra);
                controller.addAbility(feats, extra);
                controller.addAbility(feats, greater);
            }
            require(messages.errors.size() == (fey ? 1 : 2), "Unexpected errors: " + messages.errors);
            if (!fey) {
                controller.addAbility(feats, ability(feats, "Shadow Shield"));
                controller.addAbility(feats, strike);
                if (pc.getTotalLevels() >= 3) controller.addAbility(feats, shadowMagic);
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