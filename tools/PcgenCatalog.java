package pcgen.gui2.facade;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.core.Skill;
import pcgen.core.prereq.PrereqHandler;
import pcgen.persistence.lst.prereq.PreParserFactory;
import pcgen.core.analysis.SkillRankControl;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Catalog selections go through PCGen's real controller, not a second evaluator. */
class PcgenCatalog {
    // Base-sphere reference values at the level-20 INT Incanter fixture (CL 20).
    private static final String[][] BASE_REFERENCES = {
        {"War Sphere", "SPHERES_WAR_TOTEM_RADIUS_FEET", "100"},
        {"War Sphere", "SPHERES_WAR_TOTEM_WAR_DAMAGE", "6"},
        {"War Sphere", "SPHERES_WAR_COMMANDING_AID_ATTACK", "24"},
    };

    private static void checkResources(pcgen.core.PlayerCharacter pc, String sphere) {
        String variable = null;
        int expected = 0;
        switch (sphere) {
            case "Berserker Sphere": variable = "SPHERES_BERSERKER_TEMP_HP"; expected = 23; break;
            case "Duelist Sphere": variable = "SPHERES_DUELIST_BLEED"; expected = 7; break;
            case "Shield Sphere": variable = "SPHERES_ACTIVE_DEFENSE"; expected = 7; break;
            case "Boxing Sphere": variable = "SPHERES_COUNTER_PUNCH_BONUS"; expected = 12; break;
            case "Sniper Sphere": variable = "SPHERES_DEADLY_SHOT_DICE"; expected = 6; break;
            case "Barrage Sphere": variable = "SPHERES_BARRAGE_FOCUSED_ATTACKS"; expected = 5; break;
            case "Fencing Sphere": variable = "SPHERES_FATAL_THRUST_DICE"; expected = 5; break;
            default: break;
        }
        if (variable != null) {
            require(pc.getVariableValue(variable, "").intValue() == expected, "Resource: " + variable);
        }
        for (String[] reference : BASE_REFERENCES) {
            if (reference[0].equals(sphere)) {
                require(pc.getVariableValue(reference[1], "").intValue() == Integer.parseInt(reference[2]),
                        "Reference: " + reference[1]);
            }
        }
    }

    private static boolean satisfies(pcgen.core.PlayerCharacter pc, String prerequisite) throws Exception {
        return PrereqHandler.passes(PreParserFactory.getInstance().parse(prerequisite), pc, null);
    }

    private static void checkAssociatedFeats(pcgen.core.PlayerCharacter pc,
            CharacterAbilities controller, pcgen.core.AbilityCategory cat) throws Exception {
        var talent = ability(cat, "Equipment - Dagger Dancer");
        String prerequisite = "PREFEAT:1,Critical Focus";
        require(!satisfies(pc, prerequisite), "Unexpected Critical Focus before talent");
        var pool = pc.getAvailableAbilityPool(cat);
        var feats = SettingsHandler.getGameAsProperty().get().getAbilityCategory("FEAT");
        var featPool = pc.getAvailableAbilityPool(feats);
        controller.addAbility(cat, talent);
        require(satisfies(pc, prerequisite), "Associated feat did not satisfy PREFEAT");
        require(satisfies(pc, "PREABILITY:1,CATEGORY=FEAT,Critical Focus"),
                "Associated feat did not satisfy upstream PREABILITY");
        require(pc.getAvailableAbilityPool(feats).equals(featPool), "Association spent feat pool");
        controller.removeAbility(cat, talent);
        require(!satisfies(pc, prerequisite), "Association survived talent removal");
        require(pc.getAvailableAbilityPool(cat).equals(pool), "Association refund");
        var versatile = ability(cat, "Equipment - Versatile Fighter");
        var stances = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Versatile Fighter Stance");
        var offensive = ability(stances, "Versatile Fighter - Offensive Style");
        var defensive = ability(stances, "Versatile Fighter - Defensive Style");
        require(!offensive.qualifies(pc, offensive), "Stance without talent");
        controller.addAbility(cat, versatile);
        require(pc.getAvailableAbilityPool(stances).intValue() == 1, "Stance slot");
        require(!satisfies(pc, "PREFEAT:1,Power Attack"), "Inactive stance granted feat");
        controller.addAbility(stances, offensive);
        require(pc.getAvailableAbilityPool(stances).intValue() == 0, "Stance cost");
        require(satisfies(pc, "PREFEAT:1,Power Attack"), "Offensive feat missing");
        require(!satisfies(pc, "PREFEAT:1,Combat Expertise"), "Wrong stance feat");
        controller.removeAbility(stances, offensive);
        require(!satisfies(pc, "PREFEAT:1,Power Attack"), "Inactive offensive feat retained");
        controller.addAbility(stances, defensive);
        require(satisfies(pc, "PREFEAT:1,Combat Expertise"), "Defensive feat missing");
        controller.removeAbility(cat, versatile);
        require(!defensive.qualifies(pc, defensive), "Stance survived prerequisite loss");
        require(!satisfies(pc, "PREFEAT:1,Combat Expertise"), "Invalid stance retained feat benefits");
        controller.removeAbility(stances, defensive);
        require(pc.getAvailableAbilityPool(cat).equals(pool), "Stance talent refund");
        require(pc.getAvailableAbilityPool(feats).equals(featPool), "Stance spent feat pool");
    }

    public static void main(String[] args) throws Exception {
        require(args.length == 8, "character template output config gate saved cases category required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory(args[7]);
        var other = game.getAbilityCategory(args[7].equals("Spheres Magic Talent") ? "Spheres Combat Talent" : "Spheres Magic Talent");
        var otherPool = pc.getAvailableAbilityPool(other);
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var cases = Files.readAllLines(Path.of(args[6]));
        boolean reload = args[4].equals("catalog-reload");
        try {
            for (String line : cases) {
                var fields = line.split("\t");
                var sphere = ability(cat, fields[0]);
                var talent = ability(cat, fields[1]);
                if (fields[0].equals("Athletics Sphere")) {
                    var packages = game.getAbilityCategory("Spheres Athletics Package");
                    var climb = ability(packages, "Athletics Package - Climb");
                    if (reload) {
                        require(pc.hasAbilityKeyed(packages, climb.getKeyName()), "Package reload");
                        controller.removeAbility(packages, climb);
                    }
                }
                if (fields[0].equals("Equipment Sphere") && reload) {
                    var stances = game.getAbilityCategory("Spheres Versatile Fighter Stance");
                    var offensive = ability(stances, "Versatile Fighter - Offensive Style");
                    require(pc.hasAbilityKeyed(stances, offensive.getKeyName()), "Active stance lost on reload");
                    require(satisfies(pc, "PREFEAT:1,Power Attack"), "Active stance feat lost on reload");
                    require(satisfies(pc, "PREFEAT:1,Critical Focus"), "Association lost on reload");
                    controller.removeAbility(stances, offensive);
                    controller.removeAbility(cat, ability(cat, "Equipment - Versatile Fighter"));
                    controller.removeAbility(cat, ability(cat, "Equipment - Dagger Dancer"));
                    require(!satisfies(pc, "PREFEAT:1,Power Attack"), "Stance feat survived reload refund");
                    require(!satisfies(pc, "PREFEAT:1,Critical Focus"), "Association survived reload refund");
                    checkAssociatedFeats(pc, controller, cat);
                    var bonus = game.getAbilityCategory("Spheres Equipment Bonus Talent");
                    require(pc.hasAbilityKeyed(cat, "Equipment - Shield Training"), "Equipment grant reload");
                    controller.removeAbility(bonus, ability(cat, "Equipment - Shield Training"));
                    require(pc.getVariableValue("SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT", "").intValue() == 2, "Repeat reload");
                    controller.removeAbility(cat, ability(cat, "Equipment - Finesse Fighting"));
                    controller.removeAbility(cat, ability(cat, "Equipment - Finesse Fighting"));
                }
                if (reload) {
                    require(pc.hasAbilityKeyed(cat, sphere.getKeyName()), "Base lost on reload");
                    require(pc.hasAbilityKeyed(cat, talent.getKeyName()), "Talent lost on reload");
                    checkResources(pc, fields[0]);
                    continue;
                }
                require(!talent.qualifies(pc, talent), "Talent without sphere: " + fields[1]);
                var pool = pc.getAvailableAbilityPool(cat);
                controller.addAbility(cat, sphere);
                require(pc.hasAbilityKeyed(cat, sphere.getKeyName()), "Base not granted: " + fields[0]);
                checkResources(pc, fields[0]);
                if (fields[0].equals("Fencing Sphere")) {
                    var bluff = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Bluff");
                    require(SkillRankControl.getTotalRank(pc, bluff).intValue() == 5, "Sphere skill ranks");
                }
                require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == 1, "Base cost");
                if (fields[0].equals("Equipment Sphere")) {
                    var bonus = game.getAbilityCategory("Spheres Equipment Bonus Talent");
                    require(pc.getAvailableAbilityPool(bonus).intValue() == 1, "Equipment bonus pool");
                    controller.addAbility(bonus, ability(cat, "Equipment - Shield Training"));
                    require(pc.hasAbilityKeyed(cat, "Equipment - Shield Training"), "Equipment free selection");
                    require(pc.getAvailableAbilityPool(bonus).intValue() == 0, "Equipment free cost");
                    require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == 1, "Free equipment charged combat pool");
                    controller.removeAbility(bonus, ability(cat, "Equipment - Shield Training"));
                    var repeat = ability(cat, "Equipment - Finesse Fighting");
                    controller.addAbility(cat, repeat);
                    controller.addAbility(cat, repeat);
                    require(pc.getVariableValue("SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT", "").intValue() == 2, "Repeat count");
                    require(!repeat.qualifies(pc, repeat), "Repeat cap not enforced");
                    controller.removeAbility(cat, repeat);
                    controller.removeAbility(cat, repeat);
                    require(pc.getVariableValue("SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT", "").intValue() == 0, "Repeat refund");
                }
                if (fields[0].equals("Athletics Sphere")) {
                    var packages = game.getAbilityCategory("Spheres Athletics Package");
                    var climb = ability(packages, "Athletics Package - Climb");
                    require(pc.getAvailableAbilityPool(packages).intValue() == 1, "Package grant");
                    controller.addAbility(packages, climb);
                    require(pc.hasAbilityKeyed(packages, climb.getKeyName()), "Package selection");
                    require(pc.getAvailableAbilityPool(packages).intValue() == 0, "Package cost");
                    require(pc.getAvailableAbilityPool(cat).equals(pool.subtract(java.math.BigDecimal.ONE)), "Package charged combat pool");
                    controller.removeAbility(packages, climb);
                }
                rejected(controller, messages, cat, sphere, "InfoAbility.Messages.Duplicate");
                require(talent.qualifies(pc, talent), "Talent rejected: " + fields[1]);
                controller.addAbility(cat, talent);
                require(pc.hasAbilityKeyed(cat, talent.getKeyName()), "Talent not granted: " + fields[1]);
                rejected(controller, messages, cat, talent, "InfoAbility.Messages.Duplicate");
                require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == 2, "Talent cost");
                if (fields[0].equals("Fencing Sphere")) {
                    var bluff = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Bluff");
                    require(SkillRankControl.getTotalRank(pc, bluff).intValue() == 10, "Talent skill rank scaling");
                }
                controller.removeAbility(cat, talent);
                controller.removeAbility(cat, sphere);
                require(pc.getAvailableAbilityPool(cat).equals(pool), "Refund mismatch");
                require(!talent.qualifies(pc, talent), "Prerequisite survived removal");
                controller.addAbility(cat, sphere);
                controller.addAbility(cat, talent);
                if (fields[0].equals("Athletics Sphere")) {
                    var packages = game.getAbilityCategory("Spheres Athletics Package");
                    controller.addAbility(packages, ability(packages, "Athletics Package - Climb"));
                }
                if (fields[0].equals("Equipment Sphere")) {
                    controller.addAbility(game.getAbilityCategory("Spheres Equipment Bonus Talent"),
                        ability(cat, "Equipment - Shield Training"));
                    controller.addAbility(cat, ability(cat, "Equipment - Finesse Fighting"));
                    controller.addAbility(cat, ability(cat, "Equipment - Finesse Fighting"));
                    controller.addAbility(cat, ability(cat, "Equipment - Dagger Dancer"));
                    controller.addAbility(cat, ability(cat, "Equipment - Versatile Fighter"));
                    var stances = game.getAbilityCategory("Spheres Versatile Fighter Stance");
                    controller.addAbility(stances, ability(stances, "Versatile Fighter - Offensive Style"));
                }
            }
            require(pc.getAvailableAbilityPool(other).equals(otherPool), "Pool isolation");
            if (reload) {
                for (String line : cases) {
                    var fields = line.split("\t");
                    controller.removeAbility(cat, ability(cat, fields[1]));
                    controller.removeAbility(cat, ability(cat, fields[0]));
                }
                require(pc.getTotalAbilityPool(cat).equals(pc.getAvailableAbilityPool(cat)), "Reload refund");
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