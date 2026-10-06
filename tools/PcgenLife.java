package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Life resource formulas are references, not actual target healing or expenditure. */
class PcgenLife {
    private static boolean focus(pcgen.core.PlayerCharacter pc, String skill) {
        var requirement = new pcgen.core.PCTemplate();
        requirement.setName("Surgeon prerequisite " + skill);
        String token = skill.equals("Heal") ? "PREMULT" : "PREFEAT";
        String value = skill.equals("Heal")
            ? "1,[PREFEAT:1,Skill Focus (Heal)],[PREFEAT:1,Surgeon’s Trade Secrets]"
            : "1,Skill Focus (" + skill + ")";
        require(Globals.getContext().processToken(requirement, token, value), "Skill Focus prerequisite fixture");
        Globals.getContext().commit();
        return requirement.qualifies(pc, requirement);
    }
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
            var feats = pcgen.core.AbilityCategory.FEAT;
            var studied = ability(feats, "Studied Healing");
            var enhancement = ability(cat, "Enhancement Sphere");
            var deepEnhance = ability(cat, "Enhancement - Deep Enhancement");
            var greaterEquipment = ability(cat, "Enhancement - Greater Enhance Equipment");
            // Other sphere selections remain saved while this boundary matrix runs.
            var enhancementBudget = new pcgen.core.PCTemplate();
            enhancementBudget.setName("Enhancement boundary test budget");
            require(Globals.getContext().processToken(enhancementBudget, "BONUS", "ABILITYPOOL|Spheres Magic Talent|24"), "Enhancement test budget");
            Globals.getContext().commit();
            pc.addTemplate(enhancementBudget);
            if (reload) {
                require(pc.hasAbilityKeyed(cat, enhancement.getKeyName()), "Saved Enhancement sphere");
                require(pc.hasAbilityKeyed(cat, deepEnhance.getKeyName()), "Saved Deep Enhancement");
                require(pc.hasAbilityKeyed(cat, greaterEquipment.getKeyName()), "Saved Greater Enhance Equipment");
                var savedRange = ability(cat, "Enhancement - Ranged Enhancement");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGEDENHANCEMENT_COUNT", "").intValue() == 2, "Saved Enhancement range count");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGE_FEET", "").intValue() == 400 + 40 * cl, "Saved Enhancement long range");
                controller.removeAbility(cat, savedRange);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGE_FEET", "").intValue() == 100 + 10 * cl, "Saved Enhancement partial range refund");
                controller.removeAbility(cat, savedRange);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EQUIPMENT_MINUTES", "").intValue() == 60 * cl, "Saved equipment duration");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_DURATION_MINUTES", "").intValue() == 10 * cl, "Saved ordinary enhancement duration");
                require(pc.hasAbilityKeyed(cat, "Enhancement - Lighten"), "Saved Lighten selection");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_LIGHTEN_VERTICAL_SPEED", "").intValue() == 20, "Saved Lighten vertical speed");
                controller.removeAbility(cat, ability(cat, "Enhancement - Lighten"));
                require(pc.hasAbilityKeyed(cat, "Enhancement - Animate Object"), "Saved Animate Object selection");
                require(pc.hasAbilityKeyed(feats, "Complex Animations"), "Saved Complex Animations");
                require(pc.hasAbilityKeyed(feats, "Durable Objects"), "Saved Durable Objects");
                int savedPoints = pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_CONSTRUCTION_POINTS", "").intValue();
                int savedHp = pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", "").intValue();
                controller.removeAbility(feats, ability(feats, "Complex Animations"));
                controller.removeAbility(feats, ability(feats, "Durable Objects"));
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_CONSTRUCTION_POINTS", "").intValue() == savedPoints - 1, "Saved construction bonus removal");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", "").intValue() == savedHp - (cl < 11 ? 10 : cl < 20 ? 20 : 30), "Saved durability removal");
                controller.removeAbility(cat, ability(cat, "Enhancement - Animate Object"));
                controller.removeAbility(cat, greaterEquipment);
                controller.removeAbility(cat, deepEnhance);
                controller.removeAbility(cat, enhancement);
            }
            controller.addAbility(cat, enhancement);
            var mutagenic = ability(feats, "Mutagenic Enhancements");
            var alteration = ability(cat, "Alteration Sphere");
            require(!mutagenic.qualifies(pc, mutagenic), "Mutagenic Enhancements independently requires Alteration");
            controller.addAbility(cat, alteration);
            require(mutagenic.qualifies(pc, mutagenic), "Base Enhance Equipment satisfies enhance ability requirement");
            controller.removeAbility(cat, alteration);
            require(!mutagenic.qualifies(pc, mutagenic), "Mutagenic Enhancements loses Alteration prerequisite");
            var game = SettingsHandler.getGameAsProperty().get();
            var traditions = game.getAbilityCategory("Custom Casting Tradition");
            var drawbacks = game.getAbilityCategory("Custom Casting Drawback");
            var tradition = ability(traditions, "Custom Casting Tradition");
            var extendedCasting = ability(drawbacks, "Tradition - Extended Casting");
            var careful = ability(feats, "Careful Magic");
            require(!careful.qualifies(pc, careful), "Careful Magic requires Extended Casting");
            controller.addAbility(traditions, tradition);
            controller.addAbility(drawbacks, extendedCasting);
            require(careful.qualifies(pc, careful), "Careful Magic prerequisites satisfied");
            controller.addAbility(feats, careful);
            require(pc.hasAbilityKeyed(feats, careful.getKeyName()), "Careful Magic selected");
            for (int castingMod : new int[] {-4, 0, 1, 5}) {
                var adjustment = new pcgen.core.PCTemplate();
                adjustment.setName("Careful Magic casting modifier " + castingMod);
                require(Globals.getContext().processToken(adjustment, "BONUS", "VAR|SPHERES_CASTING_ABILITY|" + (castingMod - mod)), "Careful Magic modifier fixture");
                Globals.getContext().commit();
                pc.addTemplate(adjustment);
                require(pc.getVariableValue("SPHERES_CAREFUL_MAGIC_DISPEL_MSD_BONUS", "").intValue() == Math.max(1, castingMod), "Careful Magic minimum and scaling");
                pc.removeTemplate(adjustment);
            }
            controller.removeAbility(drawbacks, extendedCasting);
            require(!careful.qualifies(pc, careful), "Careful Magic drawback prerequisite removal");
            controller.removeAbility(feats, careful);
            require(pc.getVariableValue("SPHERES_CAREFUL_MAGIC_DISPEL_MSD_BONUS", "").intValue() == 0, "Careful Magic bonus removal");
            controller.removeAbility(traditions, tradition);
            var allyRequirement = ability(feats, "Exceptional Ally");
            var allyConjuration = ability(cat, "Conjuration Sphere");
            controller.addAbility(cat, allyConjuration);
            require(!allyRequirement.qualifies(pc, allyRequirement), "Base spheres alone do not satisfy an enhance talent");
            controller.addAbility(cat, deepEnhance);
            require(!allyRequirement.qualifies(pc, allyRequirement), "Utility Enhancement talent does not satisfy enhance family");
            controller.removeAbility(cat, deepEnhance);
            for (String name : new String[] {"Lighten", "Animate Object"}) {
                var member = ability(cat, "Enhancement - " + name);
                controller.addAbility(cat, member);
                require(allyRequirement.qualifies(pc, allyRequirement), "Each enhance family member qualifies: " + name);
                controller.removeAbility(cat, member);
                require(!allyRequirement.qualifies(pc, allyRequirement), "Last enhance family member removal revokes qualification");
            }
            controller.removeAbility(cat, allyConjuration);
            var illusion = ability(cat, "Illusion Sphere");
            var touch = ability(cat, "Illusion - Illusionary Touch");
            var solid = ability(feats, "Solid Illusions");
            controller.addAbility(cat, illusion);
            require(!solid.qualifies(pc, solid), "Solid Illusions rejects base sphere alone");
            controller.addAbility(cat, touch);
            require(!solid.qualifies(pc, solid), "Solid Illusions rejects one Touch selection");
            controller.addAbility(cat, touch);
            require(solid.qualifies(pc, solid), "Solid Illusions accepts two Touch selections");
            controller.removeAbility(cat, touch);
            require(!solid.qualifies(pc, solid), "Solid Illusions partial refund revokes qualification");
            controller.removeAbility(cat, touch);
            controller.removeAbility(cat, illusion);
            String[] enhancementTalents = {"Mass Enhancement", "Enhance Focus", "Staunch Resistance", "Superior Reflexes",
                "Alter Movement", "Bestow Intelligence", "Cripple", "Deadly Weapon", "Emphasize Belief",
                "Mental Enhancement", "Physical Enhancement", "Ragged Edges", "Energize Body",
                "Energy Enhancement", "Harden/Weaken", "Supply Vigor", "Traveling Weapon",
                "Ravenous Weapon", "Spectral Enhancement", "Enhance Potency"};
            String[] enhancementVariables = {"EXTRA_TARGETS", "FOCUS_BONUS", "SAVE_BONUS", "INITIATIVE_BONUS",
                "MOVEMENT_BONUS", "BESTOW_MENTAL_SCORE", "CRIPPLE_PENALTY", "CRITICAL_CONFIRMATION",
                "ALIGNMENT_DR", "MENTAL_BONUS", "PHYSICAL_BONUS", "BLEED", "CARRY_MULTIPLIER",
                "ENERGY_WEAPON_BONUS", "HARDNESS_CHANGE", "ABILITY_DAMAGE_IGNORED", "COVER_IGNORED",
                "RAVENOUS_D6", "SPECTRAL_RESISTANCE", "POTENCY_DC_REDUCTION"};
            for (String name : enhancementTalents) controller.addAbility(cat, ability(cat, "Enhancement - " + name));
            for (int state = 0; state < 4; state++) {
                if (state == 1) controller.addAbility(cat, deepEnhance);
                if (state == 2) controller.addAbility(cat, greaterEquipment);
                if (state == 3) controller.removeAbility(cat, deepEnhance);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EQUIPMENT_BONUS", "").intValue() == Math.min(5, 1 + cl / 4) + (state >= 2 ? 1 : 0), "Equipment enhancement cap");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EQUIPMENT_MINUTES", "").intValue() == cl * (state == 2 ? 60 : state == 0 ? 1 : 10), "Equipment duration interaction");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_DURATION_MINUTES", "").intValue() == cl * (state == 1 || state == 2 ? 10 : 1), "General duration remains separate");
            }
            controller.removeAbility(cat, greaterEquipment);
            require(pc.getVariableValue("SPHERES_ENHANCEMENT_EQUIPMENT_MINUTES", "").intValue() == cl, "Equipment duration refund");
            var animate = ability(cat, "Enhancement - Animate Object");
            var exceptional = ability(feats, "Exceptional Ally");
            var conjuration = ability(cat, "Conjuration Sphere");
            require(!exceptional.qualifies(pc, exceptional), "Exceptional Ally still requires Conjuration");
            controller.addAbility(cat, conjuration);
            require(exceptional.qualifies(pc, exceptional), "Reviewed enhance talents qualify Exceptional Ally");
            controller.removeAbility(cat, conjuration);
            var complexAnimations = ability(feats, "Complex Animations");
            var durableObjects = ability(feats, "Durable Objects");
            require(!complexAnimations.qualifies(pc, complexAnimations), "Complex Animations needs Animate Object");
            require(!durableObjects.qualifies(pc, durableObjects), "Durable Objects needs Animate Object");
            controller.addAbility(cat, animate);
            var objectFamiliar = ability(feats, "Object Familiar");
            require(!objectFamiliar.qualifies(pc, objectFamiliar), "Object Familiar requires familiar advancement");
            var familiarFixture = new pcgen.core.PCTemplate();
            familiarFixture.setName("Existing familiar advancement prerequisite fixture");
            require(Globals.getContext().processToken(familiarFixture, "DEFINE", "FamiliarMasterLVL|0"), "Familiar advancement definition");
            require(Globals.getContext().processToken(familiarFixture, "BONUS", "VAR|FamiliarMasterLVL|1"), "Familiar advancement fixture");
            Globals.getContext().commit();
            pc.addTemplate(familiarFixture);
            require(objectFamiliar.qualifies(pc, objectFamiliar), "Object Familiar accepts familiar advancement");
            controller.removeAbility(cat, animate);
            require(!objectFamiliar.qualifies(pc, objectFamiliar), "Familiar advancement alone does not satisfy Animate Object");
            controller.addAbility(cat, animate);
            pc.removeTemplate(familiarFixture);
            require(!objectFamiliar.qualifies(pc, objectFamiliar), "Lost familiar advancement revokes qualification");
            int[] animateLevels = {1, 3, 5, 8, 11, 15, 20, 30, 36, 42};
            int[] animateHd = {1, 2, 3, 4, 7, 10, 13, 16, 19, 22};
            int[] animatePoints = {1, 1, 2, 3, 4, 5, 6, 7, 8, 9};
            int[] animateBonusHp = {0, 10, 20, 30, 40, 60, 80, 100, 120, 150};
            int[] durableBonusHp = {10, 20, 30, 40, 60, 80, 110, 130, 150, 180};
            for (int i = 0; i < animateLevels.length; i++) {
                for (int casterLevel : new int[] {Math.max(1, animateLevels[i] - 1), animateLevels[i]}) {
                    int row = casterLevel < animateLevels[i] ? Math.max(0, i - 1) : i;
                    var adjustment = new pcgen.core.PCTemplate();
                    adjustment.setName("Animated object boundary " + casterLevel);
                    require(Globals.getContext().processToken(adjustment, "BONUS", "VAR|SPHERES_CL_ENHANCEMENT|" + (casterLevel - cl)), "Animate boundary fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(adjustment);
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_TOTAL_HD", "").intValue() == 2 * casterLevel, "Animated total HD budget");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_SIZE_INDEX", "").intValue() == row + 2, "Animated object size row");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_SPECTRAL_SIZE_INDEX", "").intValue() == row + 2, "Spectral object size row");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_HD", "").intValue() == animateHd[row], "Animated object HD row");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_CONSTRUCTION_POINTS", "").intValue() == animatePoints[row], "Animated construction-point row");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", "").intValue() == animateBonusHp[row], "Animated size bonus HP: row=" + row + " actual=" + pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", ""));
                    controller.addAbility(feats, complexAnimations);
                    controller.addAbility(feats, durableObjects);
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_CONSTRUCTION_POINTS", "").intValue() == animatePoints[row] + 1, "Complex Animations extra construction point");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", "").intValue() == durableBonusHp[row], "Durable Objects size bonus HP: row=" + row + " actual=" + pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", "") + " expected=" + durableBonusHp[row]);
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_HD", "").intValue() == animateHd[row], "Durable Objects does not increase HD");
                    controller.removeAbility(feats, complexAnimations);
                    controller.removeAbility(feats, durableObjects);
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_CONSTRUCTION_POINTS", "").intValue() == animatePoints[row], "Complex Animations refund");
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_MAX_SIZE_BONUS_HP", "").intValue() == animateBonusHp[row], "Durable Objects refund");
                    pc.removeTemplate(adjustment);
                }
            }
            controller.removeAbility(cat, animate);
            require(pc.getVariableValue("SPHERES_ENHANCEMENT_ANIMATE_TOTAL_HD", "").intValue() == 0, "Animated capacity refund");
            var lighten = ability(cat, "Enhancement - Lighten");
            var flexibility = ability(cat, "Enhancement - Improved Flexibility");
            controller.addAbility(cat, lighten);
            controller.addAbility(cat, flexibility);
            int[] lightenLevels = {1, 3, 5, 8, 11, 15, 20, 25};
            int[] halfSizes = {3, 4, 5, 6, 7, 8, 8, 8};
            int[] weightlessSizes = {2, 3, 4, 5, 6, 7, 8, 8};
            int[] floatSizes = {1, 2, 3, 4, 5, 6, 7, 8};
            for (int casterLevel = 1; casterLevel <= 43; casterLevel++) {
                var adjustment = new pcgen.core.PCTemplate();
                adjustment.setName("Lighten and flexibility boundary " + casterLevel);
                require(Globals.getContext().processToken(adjustment, "BONUS", "VAR|SPHERES_CL_ENHANCEMENT|" + (casterLevel - cl)), "Lighten boundary fixture");
                Globals.getContext().commit();
                pc.addTemplate(adjustment);
                int row = 0;
                while (row + 1 < lightenLevels.length && casterLevel >= lightenLevels[row + 1]) row++;
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_LIGHTEN_HALF_SIZE_INDEX", "").intValue() == halfSizes[row], "Half-weight table row");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_LIGHTEN_WEIGHTLESS_SIZE_INDEX", "").intValue() == weightlessSizes[row], "Weightless table row");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_LIGHTEN_FLOAT_SIZE_INDEX", "").intValue() == floatSizes[row], "Floating table row");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_FLEXIBILITY_NARROW", "").intValue() == (casterLevel >= 6 ? 1 : 0), "Narrow squeezing threshold");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_FLEXIBILITY_TIGHT", "").intValue() == (casterLevel >= 12 ? 1 : 0), "Tight squeezing threshold");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_FLEXIBILITY_FIST", "").intValue() == (casterLevel >= 18 ? 1 : 0), "Fist-sized squeezing threshold");
                pc.removeTemplate(adjustment);
            }
            controller.removeAbility(cat, lighten);
            controller.removeAbility(cat, flexibility);
            require(pc.getVariableValue("SPHERES_ENHANCEMENT_LIGHTEN_VERTICAL_SPEED", "").intValue() == 0, "Lighten reference removal");
            require(pc.getVariableValue("SPHERES_ENHANCEMENT_FLEXIBILITY_NARROW", "").intValue() == 0, "Flexibility reference removal");
            for (int casterLevel : new int[] {1, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 20, 21, 25}) {
                var adjustment = new pcgen.core.PCTemplate();
                adjustment.setName("Enhance equipment boundary " + casterLevel);
                require(Globals.getContext().processToken(adjustment, "BONUS", "VAR|SPHERES_CL_ENHANCEMENT|" + (casterLevel - cl)), "Enhancement boundary fixture");
                Globals.getContext().commit();
                pc.addTemplate(adjustment);
                int[] expectedEnhancements = {Math.max(1, casterLevel / 2), 5 + casterLevel / 4,
                    2 + casterLevel / 5, 1 + Math.max(0, (casterLevel - 1) / 4),
                    10 + 10 * (casterLevel / 5), 6 + casterLevel / 2, -2 - casterLevel / 5,
                    casterLevel / 3, Math.max(1, casterLevel / 3), 2 + 2 * (casterLevel / 7),
                    2 + 2 * (casterLevel / 7), Math.max(1, casterLevel / 2), 2 + casterLevel / 5,
                    casterLevel / 2, casterLevel, 2 + 2 * (casterLevel / 7), 2 + 2 * (casterLevel / 7),
                    1 + casterLevel / 4, casterLevel / 2, 1 + casterLevel / 8};
                for (int i = 0; i < enhancementVariables.length; i++) {
                    require(pc.getVariableValue("SPHERES_ENHANCEMENT_" + enhancementVariables[i], "").intValue() == expectedEnhancements[i], "Enhance reference boundary: " + enhancementVariables[i]);
                }
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EXTRA_AOO", "").intValue() == expectedEnhancements[3], "Superior Reflexes extra attacks");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_SPECTRAL_SAVE_BONUS", "").intValue() == 2 + casterLevel / 5, "Spectral possession and negative-energy save bonus");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_POTENCY_SAVE_DC", "").intValue() == 10 + casterLevel / 2 + mod, "Potency optional replacement DC");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_POTENCY_DISABLE_DC", "").intValue() == 10 + casterLevel + mod, "Potency Disable Device DC");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_MOVEMENT_SKILL_BONUS", "").intValue() == 2 + 2 * (casterLevel / 5), "Movement skill bonus");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EMPOWERED_BLEED", "").intValue() == casterLevel, "Empowered bleed");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_ENDURANCE_CON_BONUS", "").intValue() == casterLevel, "Endurance-only Constitution reference");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_ENERGY_ITEM_DAMAGE", "").intValue() == casterLevel, "Energy item damage");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_DR_CHANGE", "").intValue() == Math.max(1, casterLevel / 2), "Damage reduction change");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_ABILITY_DAMAGE_REDUCTION", "").intValue() == 1 + casterLevel / 7, "Vigor incoming damage reduction");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EQUIPMENT_BONUS", "").intValue() == Math.min(5, 1 + casterLevel / 4), "Base equipment cap boundary");
                controller.addAbility(cat, greaterEquipment);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_EQUIPMENT_BONUS", "").intValue() == Math.min(6, 2 + casterLevel / 4), "Greater equipment cap boundary");
                controller.removeAbility(cat, greaterEquipment);
                var rangedEnhancement = ability(cat, "Enhancement - Ranged Enhancement");
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGE_FEET", "").intValue() == 25 + 5 * (casterLevel / 2), "Enhancement close range");
                controller.addAbility(cat, rangedEnhancement);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGE_FEET", "").intValue() == 100 + 10 * casterLevel, "Enhancement medium range");
                controller.addAbility(cat, rangedEnhancement);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGE_FEET", "").intValue() == 400 + 40 * casterLevel, "Enhancement long range");
                controller.removeAbility(cat, rangedEnhancement);
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_RANGE_FEET", "").intValue() == 100 + 10 * casterLevel, "Enhancement partial range refund");
                controller.removeAbility(cat, rangedEnhancement);
                pc.removeTemplate(adjustment);
            }
            for (int i = 0; i < enhancementTalents.length; i++) {
                controller.removeAbility(cat, ability(cat, "Enhancement - " + enhancementTalents[i]));
                require(pc.getVariableValue("SPHERES_ENHANCEMENT_" + enhancementVariables[i], "").intValue() == 0, "Enhance reference refund");
            }
            controller.removeAbility(cat, enhancement);
            pc.removeTemplate(enhancementBudget);
            pc.calcActiveBonuses();
            if (reload) {
                require(pc.getVariableValue("SPHERES_TELEKINESIS_KINETICFIELD_COUNT", "").intValue() == 2, "Saved Kinetic Field selections");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_CUBES", "").intValue() == 5 + cl / 2, "Saved field shape");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_CATCH_FIELD_ROUNDS", "").intValue() == Math.max(1, cl / 3), "Saved catch field duration");
                controller.removeAbility(cat, ability(cat, "Telekinesis - Kinetic Field"));
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_CUBES", "").intValue() == 0, "Saved field partial refund");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_RADIUS", "").intValue() == 10 + 5 * (cl / 5), "Saved field first selection survives");
                controller.removeAbility(cat, ability(cat, "Telekinesis - Kinetic Field"));
                controller.removeAbility(cat, ability(cat, "Telekinesis - Quick Reactions"));
                require(pc.hasAbilityKeyed(feats, "Skillful Force"), "Saved Skillful Force selection");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FINESSE_PENALTY", "").intValue() == 0, "Saved Finesse penalty removal");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_SPEED", "").intValue() == 30 + 5 * (cl / 2), "Saved Greater Speed");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_INCREASEDRANGE_COUNT", "").intValue() == 2, "Saved repeated range selections");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_RANGE_FEET", "").intValue() == 400 + 40 * cl, "Saved long range");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_POWERFUL", "").intValue() == 1, "Saved Powerful Telekinesis");
                controller.removeAbility(cat, ability(cat, "Telekinesis - Increased Range"));
                require(pc.getVariableValue("SPHERES_TELEKINESIS_RANGE_FEET", "").intValue() == 100 + 10 * cl, "Reload partial range refund");
                controller.removeAbility(cat, ability(cat, "Telekinesis - Increased Range"));
                controller.removeAbility(cat, ability(cat, "Telekinesis - Powerful Telekinesis"));
                controller.removeAbility(feats, ability(feats, "Skillful Force"));
                controller.removeAbility(cat, ability(cat, "Telekinesis - Finesse"));
                controller.removeAbility(cat, ability(cat, "Telekinesis - Greater Speed"));
                controller.removeAbility(cat, ability(cat, "Telekinesis Sphere"));
                require(pc.hasAbilityKeyed(feats, "Studied Healing"), "Studied Healing saved selection");
                var savedHeal = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Heal");
                require(pcgen.core.analysis.SkillRankControl.getTotalRank(pc, savedHeal).intValue() == 11, "Saved Heal ranks");
                require(pc.hasAbilityKeyed(feats, "Surgeon’s Trade Secrets"), "Saved Surgeon selection");
                require(focus(pc, "Heal"), "Saved Skill Focus equivalence");
                require(!focus(pc, "Perception"), "Saved equivalence is skill-specific");
                require(pc.getTotalBonusTo("SITUATION", "Heal=Target under your blood control") == 6, "Saved Surgeon bonus");
                controller.removeAbility(feats, ability(feats, "Surgeon’s Trade Secrets"));
                controller.removeAbility(cat, ability(cat, "Blood Sphere"));
                controller.removeAbility(feats, studied);
            }
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
                String variable = name.equals("Telekinetic Tools") ? "SPHERES_TELEKINESIS_TOOL_BONUS"
                    : "SPHERES_TELEKINESIS_" + name.toUpperCase() + "_PENALTY";
                int baseline = name.equals("Telekinetic Tools") ? 0 : -5;
                require(pc.getVariableValue(variable, "").intValue() == baseline, "Telekinetic skill baseline");
                double ordinary = pc.getTotalBonusTo("SKILL", "Sleight of Hand");
                controller.addAbility(feats, force);
                require(pc.getVariableValue(variable, "").intValue() == (name.equals("Telekinetic Tools") ? 2 : 0), "Skillful Force scoped effect");
                require(pc.getTotalBonusTo("SKILL", "Sleight of Hand") == ordinary, "Skillful Force does not modify ordinary skills");
                controller.removeAbility(feats, force);
                require(pc.getVariableValue(variable, "").intValue() == baseline, "Skillful Force refund");
                controller.removeAbility(cat, alternative);
                require(!force.qualifies(pc, force), "Lost Skillful Force alternative: " + name);
            }
            var speed = ability(cat, "Telekinesis - Greater Speed");
            var field = ability(cat, "Telekinesis - Kinetic Field");
            var reactions = ability(cat, "Telekinesis - Quick Reactions");
            controller.addAbility(cat, reactions);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_CATCH_FIELD_ROUNDS", "").intValue() == 0, "Catch field needs Kinetic Field");
            for (int count = 1; count <= 2; count++) {
                controller.addAbility(cat, field);
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_RADIUS", "").intValue() == 10 + 5 * (cl / 5), "Field radius does not double");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_FIRE_DAMAGE", "").intValue() == Math.max(1, cl / 2), "Field friction damage");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_CUBES", "").intValue() == (count == 2 ? 5 + cl / 2 : 0), "Second-selection field shape");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_WALL_WIDTH", "").intValue() == (count == 2 ? 20 * cl : 0), "Field wall width");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_CATCH_FIELD_ROUNDS", "").intValue() == Math.max(1, cl / 3), "Catch field duration");
            }
            require(!field.qualifies(pc, field), "Kinetic Field repeat cap");
            controller.removeAbility(cat, field);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_RADIUS", "").intValue() == 10 + 5 * (cl / 5), "Partial field refund preserves first selection");
            require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_CUBES", "").intValue() == 0, "Partial field refund removes alternate shapes");
            controller.removeAbility(cat, field);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_FIELD_RADIUS", "").intValue() == 0, "Final field refund");
            require(pc.getVariableValue("SPHERES_TELEKINESIS_CATCH_FIELD_ROUNDS", "").intValue() == 0, "Catch field disabled on talent loss");
            controller.removeAbility(cat, reactions);
            var powerful = ability(cat, "Telekinesis - Powerful Telekinesis");
            var range = ability(cat, "Telekinesis - Increased Range");
            for (int casterLevel : new int[] {1, 2, 3, 4, 5, 7, 8, 10, 11, 14, 15, 19, 20, 24, 25, 29, 30, 39, 40, 49, 50, 59, 60}) {
                var adjustment = new pcgen.core.PCTemplate();
                adjustment.setName("Telekinesis caster level boundary " + casterLevel);
                require(Globals.getContext().processToken(adjustment, "BONUS", "VAR|SPHERES_CL_TELEKINESIS|" + (casterLevel - cl)), "Telekinesis CL fixture");
                Globals.getContext().commit();
                pc.addTemplate(adjustment);
                pc.calcActiveBonuses();
                int size = 1;
                for (int threshold : new int[] {3, 5, 8, 11, 15, 20, 25, 30, 40, 50, 60}) if (casterLevel >= threshold) size++;
                require(pc.getVariableValue("SPHERES_TELEKINESIS_SIZE_INDEX", "").intValue() == size, "Lift size boundary " + casterLevel);
                controller.addAbility(cat, powerful);
                require(pc.getVariableValue("SPHERES_TELEKINESIS_SIZE_INDEX", "").intValue() == size + 1, "Powerful lift size");
                controller.removeAbility(cat, powerful);
                require(pc.getVariableValue("SPHERES_TELEKINESIS_SIZE_INDEX", "").intValue() == size, "Powerful lift refund");
                require(pc.getVariableValue("SPHERES_TELEKINESIS_RANGE_FEET", "").intValue() == 25 + 5 * (casterLevel / 2), "Close range");
                for (int count = 1; count <= 3; count++) {
                    controller.addAbility(cat, range);
                    require(pc.getVariableValue("SPHERES_TELEKINESIS_RANGE_FEET", "").intValue() == (count == 1 ? 100 + 10 * casterLevel : 400 + 40 * casterLevel), "Range steps stop at long");
                }
                for (int count = 2; count >= 0; count--) {
                    controller.removeAbility(cat, range);
                    int feet = count >= 2 ? 400 + 40 * casterLevel : count == 1 ? 100 + 10 * casterLevel : 25 + 5 * (casterLevel / 2);
                    require(pc.getVariableValue("SPHERES_TELEKINESIS_RANGE_FEET", "").intValue() == feet, "Partial range refund");
                }
                pc.removeTemplate(adjustment);
            }
            String[] conditional = {"Divided Mind", "Dampening Field", "Dancing Weapon", "Gravity Ward/Well", "Telekinetic Push", "Flight", "Kinetic Sense", "Tether", "Whirlwind Assembly", "Gravity Shift", "Homing", "Pantomime Cage"};
            String[][] values = {
                {"LIFT_TARGETS", "MANEUVER_EXTRA_TARGETS"},
                {"OBJECT_DEFENSE", "DAMPENING_DR"},
                {"BLUDGEON_DAMAGE_BONUS"},
                {"GRAVITY_RADIUS", "GRAVITY_CMB", "GRAVITY_ESCAPE_CMD"},
                {"PUSH_SPEED_BONUS", "PUSH_SIZE_INCREASE", "PUSH_FALLING_D6"},
                {"FLIGHT_SPEED"}, {"BLINDSENSE_FEET", "BLINDSENSE_MINUTES"},
                {"TETHER_FEET", "TETHER_LINGER_ROUNDS", "TETHER_BREAK_DC"},
                {"ASSEMBLY_RETRIEVAL_FEET"}, {"GRAVITY_SHIFT_RADIUS"}, {"HOMING_ROUNDS"},
                {"CAGE_ROUNDS", "CAGE_ESCAPE_DC"}
            };
            double[][] expected = {
                {1 + cl, Math.max(1, cl / 2)}, {1 + cl / 5, cl / 2}, {mod},
                {10 + 5 * (cl / 5), cl + mod, 10 + cl + mod},
                {(20 + 5 * (cl / 5)) / 2.0, 1 + cl / 5, 1 + cl / 5},
                {20 + 5 * (cl / 5)}, {30, cl}, {30, cl, 10 + cl / 2 + mod},
                {20 + 5 * (cl / 5)}, {10 + 5 * (cl / 5)}, {cl}, {cl, 10 + cl / 2 + mod}
            };
            double armor = pc.getTotalBonusTo("COMBAT", "AC");
            double damage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
            for (int i = 0; i < conditional.length; i++) {
                var talent = ability(cat, "Telekinesis - " + conditional[i]);
                controller.addAbility(cat, talent);
                for (int j = 0; j < values[i].length; j++) {
                    require(pc.getVariableValue("SPHERES_TELEKINESIS_" + values[i][j], "").doubleValue() == expected[i][j], "Telekinetic reference " + values[i][j]);
                }
                require(pc.getTotalBonusTo("COMBAT", "AC") == armor, "Target defense does not change caster armor");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == damage, "Bludgeon bonus is not general damage");
                if (conditional[i].equals("Telekinetic Push")) {
                    controller.addAbility(cat, speed);
                    require(pc.getVariableValue("SPHERES_TELEKINESIS_PUSH_SPEED_BONUS", "").doubleValue() == (30 + 5 * (cl / 2)) / 2.0, "Push follows Greater Speed");
                    controller.removeAbility(cat, speed);
                }
                if (conditional[i].equals("Flight") || conditional[i].equals("Whirlwind Assembly")) {
                    controller.addAbility(cat, speed);
                    int distance = conditional[i].equals("Flight") ? 30 + 5 * (cl / 2) : 20 + 5 * (cl / 5);
                    require(pc.getVariableValue("SPHERES_TELEKINESIS_" + values[i][0], "").intValue() == distance, "Greater Speed only modifies applicable effects");
                    controller.removeAbility(cat, speed);
                }
                controller.removeAbility(cat, talent);
                require(pc.getVariableValue("SPHERES_TELEKINESIS_" + values[i][0], "").intValue() == 0, "Removed telekinetic reference");
            }
            require(pc.getVariableValue("SPHERES_TELEKINESIS_SPEED", "").intValue() == 20 + 5 * (cl / 5), "Telekinetic base speed");
            controller.addAbility(cat, speed);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_SPEED", "").intValue() == 30 + 5 * (cl / 2), "Greater telekinetic speed");
            controller.removeAbility(cat, speed);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_SPEED", "").intValue() == 20 + 5 * (cl / 5), "Telekinetic speed refund");
            var maneuver = ability(cat, "Telekinesis - Telekinetic Maneuver");
            var crush = ability(cat, "Telekinesis - Telekinetic Crush");
            controller.addAbility(cat, maneuver);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_MANEUVER_CMB", "").intValue() == cl + mod, "Telekinetic maneuver CMB");
            require(pc.getVariableValue("SPHERES_TELEKINESIS_GRAPPLE_CMD", "").intValue() == cl + mod + 10, "Telekinetic grapple CMD");
            var forceful = ability(cat, "Telekinesis - Forceful Telekinesis");
            double generalCmb = pc.getTotalBonusTo("COMBAT", "CMB");
            controller.addAbility(cat, forceful);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_MANEUVER_CMB", "").intValue() == cl + mod + 2, "Forceful maneuver bonus");
            require(pc.getVariableValue("SPHERES_TELEKINESIS_GRAPPLE_CMD", "").intValue() == cl + mod + 12, "Forceful grapple defense");
            require(pc.getTotalBonusTo("COMBAT", "CMB") == generalCmb, "Forceful is not general CMB");
            controller.removeAbility(cat, forceful);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_MANEUVER_CMB", "").intValue() == cl + mod, "Forceful refund");
            controller.removeAbility(cat, maneuver);
            controller.addAbility(cat, crush);
            require(pc.getVariableValue("SPHERES_TELEKINESIS_CRUSH_D6", "").intValue() == 1 + cl / 5, "Telekinetic crush dice");
            controller.removeAbility(cat, crush);
            controller.removeAbility(cat, telekinesis);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Skillful Force prerequisite refunds");
            for (var selection : new pcgen.core.Ability[] {sphere, deeper, greater, restore}) controller.addAbility(cat, selection);
            check(pc, cl, mod, true, true, true);
            require(messages.errors.size() == 2, "Unexpected Life errors: " + messages.errors);
            var heal = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Heal");
            var incanter = pc.getClassKeyed("Incanter (Spheres Prototype)");
            require(incanter != null, "Heal ranks must belong to the loaded class for persistence");
            float oldRank = pcgen.core.analysis.SkillRankControl.getTotalRank(pc, heal).floatValue();
            require(pcgen.core.analysis.SkillRankControl.modRanks(-oldRank, incanter, true, pc, heal).isEmpty(), "Clear Heal fixture ranks");
            require(!studied.qualifies(pc, studied), "Studied Healing requires a Heal rank");
            require(pcgen.core.analysis.SkillRankControl.modRanks(1, incanter, true, pc, heal).isEmpty(), "Heal prerequisite rank");
            controller.addAbility(feats, studied);
            int priorRank = 1;
            for (int rank : new int[] {1, 2, 3, 5}) {
                require(pcgen.core.analysis.SkillRankControl.modRanks(rank - priorRank, incanter, true, pc, heal).isEmpty(), "Heal rank change");
                priorRank = rank;
                for (int adjustment : new int[] {-3, -1, 0, 2}) {
                    var source = new pcgen.core.PCTemplate();
                    source.setName("Life caster-level regression " + adjustment);
                    require(Globals.getContext().processToken(source, "BONUS", "VAR|SPHERES_CL_LIFE|" + adjustment), "Life CL fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(source);
                    pc.calcActiveBonuses();
                    int life = cl + adjustment;
                    int cure = life + Math.max(0, Math.min((rank + 1) / 2, pc.getTotalLevels() - life));
                    require(pc.getVariableValue("SPHERES_LIFE_CURE_CL", "").intValue() == cure, "Studied cure CL rounding and HD cap: actual=" + pc.getVariableValue("SPHERES_LIFE_CURE_CL", "") + " expected=" + cure + " rank=" + rank + " life=" + pc.getVariableValue("SPHERES_CL_LIFE", ""));
                    require(pc.getVariableValue("SPHERES_CL_LIFE", "").intValue() == life, "Studied does not change Life CL");
                    require(pc.getVariableValue("SPHERES_LIFE_CURE_BONUS", "").intValue() == 2 * cure, "Restore Health uses cure CL");
                    require(pc.getVariableValue("SPHERES_LIFE_CURE_DICE", "").intValue() == 2 + (int)Math.floor(cure / 5.0), "Deeper Healing uses cure CL");
                    require(pc.getVariableValue("SPHERES_LIFE_INVIGORATE_HP", "").intValue() == Math.max(1, life) + life + mod, "Invigorate unaffected by Studied Healing");
                    pc.removeTemplate(source);
                }
            }
            controller.removeAbility(feats, studied);
            check(pc, cl, mod, true, true, true);
            controller.addAbility(feats, studied);
            var blood = ability(cat, "Blood Sphere");
            var surgeon = ability(feats, "Surgeon’s Trade Secrets");
            require(!surgeon.qualifies(pc, surgeon), "Surgeon requires Blood sphere");
            controller.addAbility(cat, blood);
            double generalHeal = pc.getTotalBonusTo("SKILL", "Heal");
            require(!focus(pc, "Heal"), "No Skill Focus equivalence before Surgeon");
            controller.addAbility(feats, surgeon);
            require(focus(pc, "Heal"), "Surgeon qualifies as Skill Focus Heal");
            require(!focus(pc, "Perception"), "Surgeon does not qualify for other skills");
            for (int ranks : new int[] {9, 10, 11}) {
                float current = pcgen.core.analysis.SkillRankControl.getTotalRank(pc, heal).floatValue();
                require(pcgen.core.analysis.SkillRankControl.modRanks(ranks - current, incanter, true, pc, heal).isEmpty(), "Surgeon Heal ranks");
                require(pc.getTotalBonusTo("SITUATION", "Heal=Target under your blood control") == (ranks >= 10 ? 6 : 3), "Surgeon threshold");
                require(pc.getTotalBonusTo("SKILL", "Heal") == generalHeal, "Surgeon does not improve general Heal: baseline=" + generalHeal + " actual=" + pc.getTotalBonusTo("SKILL", "Heal") + " ranks=" + ranks);
            }
            controller.removeAbility(feats, surgeon);
            require(!focus(pc, "Heal"), "Skill Focus equivalence revoked on removal");
            require(pc.getTotalBonusTo("SITUATION", "Heal=Target under your blood control") == 0, "Surgeon refund");
            controller.removeAbility(cat, blood);
            controller.addAbility(cat, blood);
            controller.addAbility(feats, surgeon);
            controller.addAbility(cat, telekinesis);
            controller.addAbility(cat, ability(cat, "Telekinesis - Finesse"));
            controller.addAbility(cat, speed);
            controller.addAbility(feats, force);
            controller.addAbility(cat, powerful);
            controller.addAbility(cat, range);
            controller.addAbility(cat, range);
            controller.addAbility(cat, field);
            controller.addAbility(cat, field);
            controller.addAbility(cat, reactions);
            controller.addAbility(cat, enhancement);
            controller.addAbility(cat, deepEnhance);
            controller.addAbility(cat, greaterEquipment);
            // The fixture retains two paid range picks in addition to the other spheres.
            var retainedRangeBudget = new pcgen.core.PCTemplate();
            retainedRangeBudget.setName("Retained Enhancement range test budget");
            require(Globals.getContext().processToken(retainedRangeBudget, "BONUS", "ABILITYPOOL|Spheres Magic Talent|4"), "Retained range budget");
            Globals.getContext().commit();
            pc.addTemplate(retainedRangeBudget);
            controller.addAbility(cat, ability(cat, "Enhancement - Ranged Enhancement"));
            controller.addAbility(cat, ability(cat, "Enhancement - Ranged Enhancement"));
            controller.addAbility(cat, lighten);
            controller.addAbility(cat, animate);
            controller.addAbility(feats, complexAnimations);
            controller.addAbility(feats, durableObjects);
            pc.removeTemplate(retainedRangeBudget);
            pc.calcActiveBonuses();
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
