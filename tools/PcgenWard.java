package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Ward-only rank bonuses never modify general Protection caster level. */
class PcgenWard {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var feats = AbilityCategory.FEAT;
        var protection = ability(magic, "Protection Sphere");
        var warleader = ability(combat, "Warleader Sphere");
        var graph = ability(feats, "Graphomancy");
        var wardlord = ability(feats, "Wardlord");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("ward-reload");
        try {
            if (reload) {
                require(pc.getVariableValue("SPHERES_PROTECTION_DISTANTPROTECTION_COUNT", "").intValue() == 3, "Saved three Distant Protection selections");
                require(pc.getVariableValue("SPHERES_PROTECTION_WARD_RANGE_FEET", "").intValue() == 400 + 40 * pc.getTotalLevels(), "Saved long ward range");
                require(pc.getVariableValue("SPHERES_PROTECTION_WARD_DURATION_ROUNDS", "").intValue() == 10 * pc.getTotalLevels(), "Saved Enduring duration");
                for (int i = 0; i < 3; i++) controller.removeAbility(magic, ability(magic, "Protection - Distant Protection"));
                controller.removeAbility(magic, ability(magic, "Protection - Enduring Protection"));
                for (String name : new String[] {"Greater Barrier", "Shaped Ward", "Buttressing", "Durable Barrier"}) {
                    require(pc.hasAbilityKeyed(magic, "Protection - " + name), "Saved barrier talent " + name);
                }
                require(pc.getVariableValue("SPHERES_PROTECTION_SHAPED_CUBE_HP", "").intValue() == 4 + pc.getTotalLevels(), "Saved greater cube HP");
                controller.removeAbility(magic, ability(magic, "Protection - Greater Barrier"));
                require(pc.getVariableValue("SPHERES_PROTECTION_SHAPED_CUBE_HP", "").intValue() == 5, "Saved greater cube refund");
                controller.removeAbility(magic, ability(magic, "Protection - Shaped Ward"));
                controller.removeAbility(magic, ability(magic, "Protection - Buttressing"));
                require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_DAMAGE_REDUCTION", "").intValue() == Math.max(1, pc.getTotalLevels() / 2), "Saved barrier reduction");
                controller.removeAbility(magic, ability(magic, "Protection - Durable Barrier"));
                require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_DAMAGE_REDUCTION", "").intValue() == 0, "Saved barrier reduction removal");
                require(pc.hasAbilityKeyed(feats, "Graphomancy") && pc.hasAbilityKeyed(feats, "Wardlord"), "Saved ward feats");
                var savedCraft = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Craft (Calligraphy)");
                require(pcgen.core.analysis.SkillRankControl.getTotalRank(pc, savedCraft).intValue() == 5, "Saved Graphomancy Craft ranks");
                require(graph.qualifies(pc, graph), "Saved Graphomancy remains qualified");
                require(pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "").intValue() == pc.getTotalLevels(), "Saved ward CL cap");
                controller.removeAbility(feats, graph);
                controller.removeAbility(feats, wardlord);
                controller.removeAbility(combat, warleader);
                controller.removeAbility(magic, protection);
            }
            var fixture = new pcgen.core.PCTemplate();
            fixture.setName("Ward slot fixture");
            require(Globals.getContext().processToken(fixture, "DEFINE", "SPHERES_COMBAT_TALENTS|0"), "Combat definition fixture");
            require(Globals.getContext().processToken(fixture, "BONUS", "VAR|SPHERES_COMBAT_TALENTS|1"), "Combat slot fixture");
            require(Globals.getContext().processToken(fixture, "BONUS", "ABILITYPOOL|FEAT|2"), "Feat slot fixture");
            Globals.getContext().commit();
            pc.addTemplate(fixture);
            require(!graph.qualifies(pc, graph), "Graphomancy requires Protection");
            controller.addAbility(magic, protection);
            var greater = ability(magic, "Protection - Greater Barrier");
            var shaped = ability(magic, "Protection - Shaped Ward");
            var buttressing = ability(magic, "Protection - Buttressing");
            var durable = ability(magic, "Protection - Durable Barrier");
            controller.addAbility(magic, durable);
            var distant = ability(magic, "Protection - Distant Protection");
            var enduring = ability(magic, "Protection - Enduring Protection");
            int naturalCl = pc.getVariableValue("SPHERES_CL_PROTECTION", "").intValue();
            String[] aegisNames = {"Ablating", "Ray Deflection", "Painful Aegis", "Mass Aegis"};
            String[] aegisVariables = {"INITIAL_ABLATION_PERCENT", "RAY_DEFLECTION_PERCENT", "PAINFUL_NONLETHAL_DAMAGE", "MASS_ADDITIONAL_TARGETS"};
            for (String name : aegisNames) controller.addAbility(magic, ability(magic, "Protection - " + name));
            for (int value : new int[] {1, 2, 3, 4, 5, 17, 18, 20, 29, 30, 40}) {
                var levelFixture = new pcgen.core.PCTemplate();
                levelFixture.setName("Aegis caster level boundary " + value);
                require(Globals.getContext().processToken(levelFixture, "BONUS", "VAR|SPHERES_CL_PROTECTION|" + (value - naturalCl)), "Aegis CL fixture");
                Globals.getContext().commit();
                pc.addTemplate(levelFixture);
                int[] expected = {Math.min(50, 20 + 5 * (value / 3)), Math.min(50, 20 + 5 * (value / 5)), Math.max(1, value / 2), Math.max(1, value / 2)};
                require(pc.getVariableValue("SPHERES_PROTECTION_MASS_DURATION_MINUTES", "").intValue() == 10 * value, "Mass duration reduced to minutes");
                for (int i = 0; i < aegisVariables.length; i++) {
                    require(pc.getVariableValue("SPHERES_PROTECTION_" + aegisVariables[i], "").intValue() == expected[i], "Aegis boundary " + aegisNames[i] + " CL" + value);
                }
                pc.removeTemplate(levelFixture);
            }
            for (int i = 0; i < aegisNames.length; i++) {
                controller.removeAbility(magic, ability(magic, "Protection - " + aegisNames[i]));
                require(pc.getVariableValue("SPHERES_PROTECTION_" + aegisVariables[i], "").intValue() == 0, "Aegis reference removal " + aegisNames[i]);
            }
            require(pc.getVariableValue("SPHERES_PROTECTION_WARD_DURATION_ROUNDS", "").intValue() == naturalCl, "Default paid ward duration");
            require(pc.getVariableValue("SPHERES_PROTECTION_MASS_DURATION_MINUTES", "").intValue() == 0, "Mass duration removal");
            controller.addAbility(magic, enduring);
            require(pc.getVariableValue("SPHERES_PROTECTION_WARD_DURATION_ROUNDS", "").intValue() == 10 * naturalCl, "Enduring converts rounds to minutes");
            require(pc.getVariableValue("SPHERES_PROTECTION_AEGIS_DURATION_HOURS", "").intValue() == naturalCl, "Enduring does not extend aegises");
            for (int count = 0; count <= 3; count++) {
                if (count > 0) controller.addAbility(magic, distant);
                int range = count == 0 ? 0 : count == 1 ? 25 + 5 * (naturalCl / 2) : count == 2 ? 100 + 10 * naturalCl : 400 + 40 * naturalCl;
                require(pc.getVariableValue("SPHERES_PROTECTION_AEGIS_RANGE_FEET", "").intValue() == range, "Distant aegis range step " + count);
                require(pc.getVariableValue("SPHERES_PROTECTION_WARD_RANGE_FEET", "").intValue() == range, "Distant ward range step " + count);
            }
            for (int count = 2; count >= 0; count--) {
                controller.removeAbility(magic, distant);
                int range = count == 0 ? 0 : count == 1 ? 25 + 5 * (naturalCl / 2) : 100 + 10 * naturalCl;
                require(pc.getVariableValue("SPHERES_PROTECTION_WARD_RANGE_FEET", "").intValue() == range, "Distant range partial refund");
            }
            controller.removeAbility(magic, enduring);
            require(pc.getVariableValue("SPHERES_PROTECTION_WARD_DURATION_ROUNDS", "").intValue() == naturalCl, "Enduring duration refund");
            controller.addAbility(magic, shaped);
            require(pc.getVariableValue("SPHERES_PROTECTION_SHAPED_CUBE_HP", "").intValue() == 5, "Normal shaped cube HP");
            controller.addAbility(magic, greater);
            controller.addAbility(magic, buttressing);
            require(!wardlord.qualifies(pc, wardlord), "Wardlord independently requires Warleader");
            controller.addAbility(combat, warleader);
            var craft = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Craft (Calligraphy)");
            var incanter = pc.getClassKeyed("Incanter (Spheres Prototype)");
            require(incanter != null, "Craft ranks must belong to the loaded class for persistence");
            float old = pcgen.core.analysis.SkillRankControl.getTotalRank(pc, craft).floatValue();
            require(pcgen.core.analysis.SkillRankControl.modRanks(-old, incanter, true, pc, craft).isEmpty(), "Clear Craft ranks");
            require(!graph.qualifies(pc, graph), "Graphomancy requires Craft rank");
            require(pcgen.core.analysis.SkillRankControl.modRanks(1, incanter, true, pc, craft).isEmpty(), "Craft rank");
            controller.addAbility(feats, graph);
            int cl = pc.getTotalLevels();
            int previous = 1;
            for (int ranks : new int[] {1, 2, 3, 5}) {
                require(pcgen.core.analysis.SkillRankControl.modRanks(ranks - previous, incanter, true, pc, craft).isEmpty(), "Craft ranks");
                previous = ranks;
                for (int delta : new int[] {-4, -1, 0, 2}) {
                    var adjustment = new pcgen.core.PCTemplate();
                    adjustment.setName("Ward CL fixture " + delta);
                    require(Globals.getContext().processToken(adjustment, "BONUS", "VAR|SPHERES_CL_PROTECTION|" + delta), "CL fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(adjustment);
                    int base = cl + delta;
                    int expected = base + Math.max(0, Math.min(cl - base, (ranks + 1) / 2));
                    require(pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "").intValue() == expected, "Graphomancy rounding and cap actual=" + pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "") + " base=" + pc.getVariableValue("SPHERES_PROTECTION_WARD_BASE_CL", "") + " expected=" + expected + " flag=" + pc.getVariableValue("SPHERES_GRAPHOMANCY", ""));
                    controller.addAbility(feats, wardlord);
                    int diplomacy = pcgen.core.analysis.SkillRankControl.getTotalRank(pc,
                        Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Diplomacy")).intValue();
                    expected = base + Math.max(0, Math.min(cl - base, (ranks + 1) / 2 + (diplomacy + 1) / 2));
                    require(pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "").intValue() == expected, "Combined ward bonuses share HD cap actual=" + pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "") + " expected=" + expected + " diplomacy=" + diplomacy + " base=" + base);
                    require(pc.getVariableValue("SPHERES_CL_PROTECTION", "").intValue() == base, "Aegis/general Protection unchanged");
                    require(pc.getVariableValue("SPHERES_PROTECTION_WARD_RADIUS_FEET", "").intValue() == 10 + 5 * expected, "Ward radius uses ward-specific CL");
                    require(pc.getVariableValue("SPHERES_PROTECTION_WARD_DURATION_ROUNDS", "").intValue() == expected, "Default ward duration uses ward-specific CL");
                    controller.addAbility(magic, distant);
                    controller.addAbility(magic, enduring);
                    require(pc.getVariableValue("SPHERES_PROTECTION_WARD_RANGE_FEET", "").intValue() == 25 + 5 * (expected / 2), "Ward close range includes scoped bonuses");
                    require(pc.getVariableValue("SPHERES_PROTECTION_AEGIS_RANGE_FEET", "").intValue() == 25 + 5 * (base / 2), "Aegis close range excludes ward bonuses");
                    require(pc.getVariableValue("SPHERES_PROTECTION_WARD_DURATION_ROUNDS", "").intValue() == 10 * expected, "Enduring uses ward-specific CL");
                    controller.removeAbility(magic, distant);
                    controller.removeAbility(magic, enduring);
                    require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_HP", "").intValue() == 2 * expected, "Barrier uses ward CL");
                    require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_DAMAGE_REDUCTION", "").intValue() == Math.max(1, expected / 2), "Barrier reduction uses ward CL with minimum one");
                    require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_BREAK_DC", "").intValue() == 15 + expected / 2, "Barrier break DC rounding");
                    require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_WEIGHT_LB", "").intValue() == 2400 + 250 * expected, "Barrier weight capacity");
                    require(pc.getVariableValue("SPHERES_PROTECTION_GREATER_BARRIER_HP", "").intValue() == 10 * expected, "Paid greater barrier HP");
                    require(pc.getVariableValue("SPHERES_PROTECTION_GREATER_BARRIER_BREAK_DC", "").intValue() == 25 + expected / 2, "Paid greater barrier break DC");
                    require(pc.getVariableValue("SPHERES_PROTECTION_GREATER_BARRIER_WEIGHT_LB", "").intValue() == 2 * (2400 + 250 * expected), "Paid greater barrier weight");
                    require(pc.getVariableValue("SPHERES_PROTECTION_SHAPED_CUBE_HP", "").intValue() == 4 + expected, "Greater shaped cube HP");
                    require(pc.getVariableValue("SPHERES_PROTECTION_SHAPED_CUBES", "").intValue() == 2 * expected, "Shaped cube count");
                    require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_REPAIR_HP", "").intValue() == 2 * expected, "Buttressing repair");
                    require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_REGEN_HP", "").intValue() == 1 + expected / 2, "Buttressing regeneration");
                    controller.removeAbility(feats, wardlord);
                    pc.removeTemplate(adjustment);
                }
            }
            controller.removeAbility(feats, graph);
            controller.removeAbility(magic, greater);
            require(pc.getVariableValue("SPHERES_PROTECTION_SHAPED_CUBE_HP", "").intValue() == 5, "Greater Barrier removal restores cube HP");
            controller.removeAbility(magic, shaped);
            controller.removeAbility(magic, buttressing);
            controller.removeAbility(magic, durable);
            require(pc.getVariableValue("SPHERES_PROTECTION_BARRIER_DAMAGE_REDUCTION", "").intValue() == 0, "Barrier reduction refund");
            require(pc.getVariableValue("SPHERES_PROTECTION_WARD_CL", "").intValue() == cl, "Ward bonus refund");
            controller.addAbility(feats, graph);
            controller.addAbility(feats, wardlord);
            require(messages.errors.isEmpty(), "Unexpected errors " + messages.errors);
            controller.addAbility(magic, greater);
            controller.addAbility(magic, shaped);
            controller.addAbility(magic, buttressing);
            controller.addAbility(magic, durable);
            pc.removeTemplate(fixture);
            controller.addAbility(magic, enduring);
            for (int i = 0; i < 3; i++) controller.addAbility(magic, distant);
            require(pc.getVariableValue("SPHERES_PROTECTION_DISTANTPROTECTION_COUNT", "").intValue() == 3, "Retained Distant Protection selections");
            require(messages.errors.isEmpty(), "Retained choice errors " + messages.errors);
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