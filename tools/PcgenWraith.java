package pcgen.gui2.facade;

import java.math.BigDecimal;
import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Extra haunt grants use the existing option pool, not free-form feat targets. */
class PcgenWraith {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var haunts = game.getAbilityCategory("Wraith Wraith Haunt");
        var feats = AbilityCategory.FEAT;
        var extra = ability(feats, "Extra Wraith Haunt");
        var rounds = ability(haunts, "Wraith Extra Incorporeality");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_WRAITH_LEVEL", "").intValue();
        int baseline = Math.max(0, (level - 1) / 2);
        boolean reload = args[4].equals("wraith-reload");
        int baseRounds = level >= 20 ? 0 : level + pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
        int increment = level >= 20 ? 0 : 4;
        try {
            for (String[] gate : new String[][] {
                    {"Wraith Ghost Glide (requires wraith 7)", "7"},
                    {"Wraith Ghost Glide - Improved (requires wraith 11)", "11"},
                    {"Wraith Share Wraith Form", "3"}}) {
                var haunt = ability(haunts, gate[0]);
                require(haunt.qualifies(pc, haunt) == (level >= Integer.parseInt(gate[1])),
                    "Haunt class-level gate: " + gate[0]);
            }
            var paths = game.getAbilityCategory("Wraith Haunt Path");
            var path = ability(paths, "Wraith Path of the Despoiler");
            var heal = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Heal");
            if (reload) {
                require(pc.hasAbilityKeyed(paths, path.getKeyName()), "Path persistence");
                require(pc.isClassSkill(heal), "Saved path class skill");
                require(pc.getTotalBonusTo("SKILL", "Heal") == (level < 4 ? 0 : level / 2), "Saved path bonus");
                controller.removeAbility(paths, path);
            }
            boolean originalClassSkill = pc.isClassSkill(heal);
            double originalBonus = pc.getTotalBonusTo("SKILL", "Heal");
            controller.addAbility(paths, path);
            int otherCasterLevel = pc.getVariableValue("SPHERES_FEY_ADEPT_LEVEL", "").intValue();
            require(pc.getVariableValue("SPHERES_CL_DEATH", "").intValue() == level + otherCasterLevel,
                "Path sphere must preserve caster levels from other classes: death="
                    + pc.getVariableValue("SPHERES_CL_DEATH", "") + " global="
                    + pc.getVariableValue("SPHERES_CASTER_LEVEL", "") + " wraith=" + level
                    + " fey=" + otherCasterLevel + " errors=" + messages.errors);
            require(pc.isClassSkill(heal), "Path class skill");
            require(pc.getTotalBonusTo("SKILL", "Heal") == originalBonus + (level < 4 ? 0 : level / 2), "Path insight bonus");
            controller.removeAbility(paths, path);
            require(pc.isClassSkill(heal) == originalClassSkill, "Path class skill refund");
            require(pc.getTotalBonusTo("SKILL", "Heal") == originalBonus, "Path bonus refund");
            controller.addAbility(paths, path);
            if (level < 3) {
                rejected(controller, messages, feats, extra, "InfoAbility.Messages.NotQualified");
                rejected(controller, messages, haunts, rounds, "InfoAbility.Messages.NotQualified");
            } else {
                if (reload) {
                    require(pc.hasAbilityKeyed(haunts, rounds.getKeyName()), "Repeated rounds persistence");
                    require(pc.getVariableValue("SPHERES_WRAITH_FORM_ROUNDS", "").intValue() == baseRounds + 2 * increment,
                        "Saved form rounds");
                    controller.removeAbility(haunts, rounds);
                    require(pc.getVariableValue("SPHERES_WRAITH_FORM_ROUNDS", "").intValue() == baseRounds + increment,
                        "Partial rounds refund");
                    controller.removeAbility(haunts, rounds);
                    require(pc.hasAbilityKeyed(feats, extra.getKeyName()), "Extra haunt persistence");
                    require(pc.getAvailableAbilityPool(haunts).intValue() == baseline + 2, "Both grants persisted");
                    controller.removeAbility(feats, extra);
                    require(pc.getAvailableAbilityPool(haunts).intValue() == baseline + 1, "Reload partial refund");
                    controller.removeAbility(feats, extra);
                }
                var featPool = pc.getAvailableAbilityPool(feats);
                var expanded = ability(haunts, "Wraith Expanded Path Possession (requires haunt path - path sphere of the selected path)");
                var improvedExpanded = ability(haunts, "Wraith Expanded Path Possession - Improved (requires expanded path possession - wraith 12)");
                require(!improvedExpanded.qualifies(pc, improvedExpanded), "Improved expanded path requires base haunt");
                controller.addAbility(haunts, expanded);
                require(improvedExpanded.qualifies(pc, improvedExpanded) == (level >= 12),
                    "Improved expanded path requires Wraith twelve");
                controller.removeAbility(haunts, expanded);
                require(!improvedExpanded.qualifies(pc, improvedExpanded), "Expanded path prerequisite removal");
                var magic = game.getAbilityCategory("Spheres Magic Talent");
                var enhancement = ability(magic, "Enhancement Sphere");
                var ride = ability(haunts, "Wraith Object Ride");
                var armaments = ability(haunts, "Wraith Possess Armaments (requires Enhancement sphere or object ride or path of the poltergeist)");
                var poltergeist = ability(paths, "Wraith Path of the Poltergeist");
                var reactive = ability(haunts, "Wraith Reactive Possession (requires possess armaments or path of the poltergeist improved path possession)");
                require(!reactive.qualifies(pc, reactive), "Reactive Possession requires an entry route");
                require(!armaments.qualifies(pc, armaments), "Armaments requires both prerequisite groups");
                controller.addAbility(magic, enhancement);
                require(!armaments.qualifies(pc, armaments), "Enhancement alone must not qualify");
                controller.addAbility(haunts, ride);
                require(armaments.qualifies(pc, armaments), "Enhancement and Object Ride qualify");
                if (baseline >= 2) {
                    controller.addAbility(haunts, armaments);
                    require(reactive.qualifies(pc, reactive), "Armaments unlocks Reactive Possession");
                    controller.removeAbility(haunts, armaments);
                    require(!reactive.qualifies(pc, reactive), "Lost Armaments prerequisite");
                }
                controller.removeAbility(magic, enhancement);
                require(!armaments.qualifies(pc, armaments), "Object Ride alone must not qualify");
                controller.removeAbility(haunts, ride);
                controller.removeAbility(paths, path);
                controller.addAbility(paths, poltergeist);
                require(reactive.qualifies(pc, reactive) == (level >= 8), "Improved path possession level gate");
                require(!armaments.qualifies(pc, armaments), "Poltergeist alone must not qualify");
                controller.addAbility(magic, enhancement);
                require(armaments.qualifies(pc, armaments), "Enhancement and Poltergeist qualify");
                controller.removeAbility(paths, poltergeist);
                require(!reactive.qualifies(pc, reactive), "Lost Poltergeist prerequisite");
                require(!armaments.qualifies(pc, armaments), "Lost possession prerequisite");
                controller.removeAbility(magic, enhancement);
                controller.addAbility(paths, path);
                require(pc.getAvailableAbilityPool(haunts).intValue() == baseline, "Base haunt pool");
                for (int count = 1; count <= 2; count++) {
                    controller.addAbility(feats, extra);
                    require(pc.getAvailableAbilityPool(haunts).intValue() == baseline + count, "Repeat haunt grant");
                    require(pc.getAvailableAbilityPool(feats).equals(featPool.subtract(BigDecimal.valueOf(count))), "Feat cost");
                }
                var selection = ability(haunts, "Wraith Amnesiac Possession");
                controller.addAbility(haunts, selection);
                require(pc.hasAbilityKeyed(haunts, selection.getKeyName()), "Haunt selection");
                require(pc.getAvailableAbilityPool(haunts).intValue() == baseline + 1, "Haunt slot spending");
                controller.removeAbility(haunts, selection);
                var share = ability(haunts, "Wraith Share Wraith Form");
                var forced = ability(haunts, "Wraith Forced Wraith Form (requires share wraith form)");
                rejected(controller, messages, haunts, forced, "InfoAbility.Messages.NotQualified");
                controller.addAbility(haunts, share);
                controller.addAbility(haunts, forced);
                controller.addAbility(haunts, forced);
                require(pc.getVariableValue("SPHERES_WRAITH_FORCED_FORM_COUNT", "").intValue() == 2, "Two forced form selections");
                rejected(controller, messages, haunts, forced, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(haunts, forced);
                require(pc.getVariableValue("SPHERES_WRAITH_FORCED_FORM_COUNT", "").intValue() == 1, "Partial forced form refund");
                require(forced.qualifies(pc, forced), "Second forced form slot restored");
                controller.removeAbility(haunts, share);
                require(!forced.qualifies(pc, forced), "Share Wraith Form prerequisite loss");
                controller.removeAbility(haunts, forced);
                require(pc.getVariableValue("SPHERES_WRAITH_FORCED_FORM_COUNT", "").intValue() == 0, "Full forced form refund");
                for (int count = 1; count >= 0; count--) {
                    controller.removeAbility(feats, extra);
                    require(pc.getAvailableAbilityPool(haunts).intValue() == baseline + count, "Haunt refund");
                }
                require(pc.getAvailableAbilityPool(feats).equals(featPool), "Full feat refund");
                controller.addAbility(feats, extra);
                controller.addAbility(feats, extra);
                controller.addAbility(haunts, rounds);
                controller.addAbility(haunts, rounds);
                require(pc.getVariableValue("SPHERES_WRAITH_FORM_ROUNDS", "").intValue() == baseRounds + 2 * increment,
                    "Stacked extra rounds");
                require(pc.getAvailableAbilityPool(haunts).intValue() == baseline, "Repeated rounds spend two slots");
            }
            require(messages.errors.size() == 2, "Unexpected errors: " + messages.errors);
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