package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.facade.core.ChooserFacade;
import pcgen.facade.core.TempBonusFacade;
import pcgen.system.CharacterManager;
import pcgen.core.SettingsHandler;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Time range/capacity and received-effect lifecycle, without casting simulation. */
class PcgenTime {
    private static class Choice extends Messages {
        int level = 1;
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            for (var item : chooser.getAvailableList()) {
                if (item.toString().equals(Integer.toString(level))) {
                    chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing Time caster level " + level);
        }
    }

    private static TempBonusFacade effect(CharacterFacadeImpl facade, String key, boolean applied) {
        for (var item : applied ? facade.getTempBonuses() : facade.getAvailableTempBonuses()) {
            if (item.getKeyName().equals(key)) return item;
        }
        throw new IllegalStateException("Missing Time effect " + key);
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = (CharacterFacadeImpl) CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var cat = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
        var sphere = ability(cat, "Time Sphere");
        var ranged = ability(cat, "Time - Ranged Time");
        var trap = ability(cat, "Time - Temporal Trap");
        boolean reload = args[4].equals("time-reload");
        String retained = "Time Effect - Haste - Attack";
        if (reload) {
            String age = "Time Effect - Age - Young Adult to Venerable";
            for (String stat : new String[] {"STR", "DEX", "CON"}) {
                require(pc.getTotalBonusTo("STAT", stat) == 0, "Persisted Age remains inactive");
            }
            facade.setTempBonusActive(effect(facade, age, true), true);
            pc.calcActiveBonuses();
            for (String stat : new String[] {"STR", "DEX", "CON"}) {
                require(pc.getTotalBonusTo("STAT", stat) == -6, "Persisted Age cumulative penalty");
            }
            facade.removeTempBonus(effect(facade, age, true));
            pc.calcActiveBonuses();
            String timeline = "Time Effect - Timeline Bridge - Knowledge";
            double knowledge = pc.getTotalBonusTo("SKILL", "TYPE.Knowledge");
            facade.removeTempBonus(effect(facade, timeline, true));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SKILL", "TYPE.Knowledge") == knowledge - 5, "Persisted Timeline Bridge CL11");
            String rapid = "Time Effect - Rapid Response - Initiative";
            double initiative = pc.getTotalBonusTo("COMBAT", "INITIATIVE");
            facade.removeTempBonus(effect(facade, rapid, true));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == initiative - 5, "Persisted Rapid Response CL11");
            String broken = "Time Effect - Broken Time";
            double brokenAttack = pc.getTotalBonusTo("COMBAT", "TOHIT");
            double brokenSkill = pc.getTotalBonusTo("SKILL", "ALL");
            facade.setTempBonusActive(effect(facade, broken, true), true);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == brokenAttack - 5, "Persisted inactive Broken Time CL11 attack");
            require(pc.getTotalBonusTo("SKILL", "ALL") == brokenSkill - 5, "Persisted Broken Time skills");
            facade.removeTempBonus(effect(facade, broken, true));
            pc.calcActiveBonuses();
            String savedAoo = "Time Effect - Improved Haste - Attacks of Opportunity";
            require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_IMPROVED_HASTE_AOO") == 5, "Persisted opportunity capacity CL20");
            facade.removeTempBonus(effect(facade, savedAoo, true));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_IMPROVED_HASTE_AOO") == 0, "Persisted opportunity capacity removal");
            String savedAttack = "Time Effect - Improved Haste - Full Attack";
            double savedAttacks = pc.getTotalBonusTo("COMBAT", "ATTACKS");
            facade.setTempBonusActive(effect(facade, savedAttack, true), true);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "ATTACKS") == savedAttacks + 1, "Persisted inactive full-attack choice");
            facade.removeTempBonus(effect(facade, savedAttack, true));
            pc.calcActiveBonuses();
            require(pc.getVariableValue("SPHERES_TIME_TRAP_CAPACITY", "").intValue() == 3, "Persisted trap capacity");
            require(pc.getVariableValue("SPHERES_TIME_RANGEDTIME_COUNT", "").intValue() == 3, "Persisted ranged selections");
            for (int i = 0; i < 3; i++) {
                controller.removeAbility(cat, ranged);
                controller.removeAbility(cat, trap);
            }
            controller.removeAbility(cat, sphere);
            double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
            facade.setTempBonusActive(effect(facade, retained, true), true);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack + 3, "Persisted inactive Haste CL20");
            facade.removeTempBonus(effect(facade, retained, true));
            pc.calcActiveBonuses();
        }
        try {
            var pool = pc.getAvailableAbilityPool(cat);
            rejected(controller, messages, cat, ranged, "InfoAbility.Messages.NotQualified");
            rejected(controller, messages, cat, trap, "InfoAbility.Messages.NotQualified");
            messages.errors.clear();
            controller.addAbility(cat, sphere);
            int originalCl = pc.getVariableValue("SPHERES_CL_TIME", "").intValue();
            for (String name : new String[] {"Age", "Time Zone", "Causality", "Lingering Time", "After Image", "Retroactive Preparation", "Fast Time", "Stretch Time", "Time Bubble", "Time Freeze"}) {
                var talent = ability(cat, "Time - " + name);
                controller.addAbility(cat, talent);
                for (int cl : new int[] {1, 2, 3, 4, 5, 9, 10, 17, 18, 20, 30}) {
                    var levelFixture = new pcgen.core.PCTemplate();
                    levelFixture.setName("Time limits CL" + cl);
                    require(Globals.getContext().processToken(levelFixture, "BONUS", "VAR|SPHERES_CL_TIME|" + (cl - originalCl)), "Time limits fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(levelFixture);
                    String variable;
                    int expected;
                    switch (name) {
                        case "Age": variable = "AGE_CATEGORY_LIMIT"; expected = 1 + cl / 5; break;
                        case "Time Zone": variable = "ZONE_GLOBE_RADIUS_MAX"; expected = 10 + 5 * (cl / 2); break;
                        case "Causality": variable = "CAUSALITY_DAMAGE_D8"; expected = cl / 2; break;
                        case "Lingering Time": variable = "LINGER_ROUNDS"; expected = 2; break;
                        case "After Image": variable = "AFTER_IMAGE_MISS_CHANCE"; expected = Math.min(50, 20 + 5 * (cl / 3)); break;
                        case "Retroactive Preparation": variable = "RETROACTIVE_VALUE_EXCLUSIVE"; expected = 100 * cl; break;
                        case "Fast Time": variable = "FAST_RADIUS"; expected = 10 + 5 * (cl / 5); break;
                        case "Stretch Time": variable = "STRETCH_RADIUS"; expected = 10 + 5 * (cl / 5); break;
                        case "Time Bubble": variable = "BUBBLE_RADIUS_MAX"; expected = 15 + 5 * (cl / 5); break;
                        default: variable = "FREEZE_RADIUS"; expected = 10 + 5 * (cl / 5); break;
                    }
                    require(pc.getVariableValue("SPHERES_TIME_" + variable, "").intValue() == expected, "Time limit " + name + " CL" + cl);
                    if (name.equals("Time Bubble")) require(pc.getVariableValue("SPHERES_TIME_BUBBLE_DAMAGE_D8", "").intValue() == cl / 2, "Bubble damage dice");
                    if (name.equals("Age")) require(pc.getVariableValue("SPHERES_TIME_AGE_RELEASED_MINUTES", "").intValue() == cl, "Age released duration");
                    if (name.equals("Time Zone")) require(pc.getVariableValue("SPHERES_TIME_ZONE_WALL_CUBES_MAX", "").intValue() == 3 + cl, "Time Zone cube allowance");
                    pc.removeTemplate(levelFixture);
                }
                controller.removeAbility(cat, talent);
                if (name.equals("Age")) require(pc.getVariableValue("SPHERES_TIME_AGE_CATEGORY_LIMIT", "").intValue() == 0, "Age limit removal");
                if (name.equals("Time Zone")) require(pc.getVariableValue("SPHERES_TIME_ZONE_WALL_CUBES_MAX", "").intValue() == 0, "Time Zone removal");
                if (name.equals("Causality")) require(pc.getVariableValue("SPHERES_TIME_CAUSALITY_DAMAGE_D8", "").intValue() == 0, "Causality removal");
                if (name.equals("Lingering Time")) require(pc.getVariableValue("SPHERES_TIME_LINGER_ROUNDS", "").intValue() == 0, "Lingering Time removal");
            }
            for (int cl : new int[] {1, 2, 5, 9, 10, 20}) {
                var fixture = new pcgen.core.PCTemplate();
                fixture.setName("Time CL fixture " + cl);
                require(Globals.getContext().processToken(fixture, "BONUS", "VAR|SPHERES_CL_TIME|" + (cl - originalCl)), "Time CL fixture");
                Globals.getContext().commit();
                pc.addTemplate(fixture);
                require(pc.getVariableValue("SPHERES_TIME_CAST_RANGE", "").intValue() == 0, "Base casting is touch, not close");
                require(pc.getVariableValue("SPHERES_TIME_CONCENTRATION_RANGE", "").intValue() == 25 + 5 * (cl / 2), "Base concentration close range");
                require(pc.getVariableValue("SPHERES_TIME_RELEASED_ROUNDS", "").intValue() == cl, "Released duration");
                int[] ranges = {0, 25 + 5 * (cl / 2), 100 + 10 * cl, 400 + 40 * cl};
                for (int i = 1; i <= 3; i++) {
                    controller.addAbility(cat, ranged);
                    require(pc.getVariableValue("SPHERES_TIME_CAST_RANGE", "").intValue() == ranges[i], "Ranged Time progression");
                }
                for (int i = 2; i >= 0; i--) {
                    controller.removeAbility(cat, ranged);
                    require(pc.getVariableValue("SPHERES_TIME_CAST_RANGE", "").intValue() == ranges[i], "Ranged Time partial refund");
                }
                pc.removeTemplate(fixture);
            }
            for (int i = 1; i <= 3; i++) {
                controller.addAbility(cat, trap);
                require(pc.getVariableValue("SPHERES_TIME_TRAP_CAPACITY", "").intValue() == i, "Trap capacity per purchase");
            }
            for (int i = 2; i >= 0; i--) {
                controller.removeAbility(cat, trap);
                require(pc.getVariableValue("SPHERES_TIME_TRAP_CAPACITY", "").intValue() == i, "Trap partial refund");
            }
            controller.removeAbility(cat, sphere);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Time full refund");
            controller.addAbility(cat, sphere);
            for (int i = 0; i < 3; i++) {
                controller.addAbility(cat, ranged);
                controller.addAbility(cat, trap);
            }
            require(messages.errors.isEmpty(), "Unexpected Time selection errors " + messages.errors);
        } finally {
            controller.closeCharacter();
        }
        var old = ChooserFactory.getDelegate();
        var choice = new Choice();
        ChooserFactory.setDelegate(choice);
        try {
            String fullAttack = "Time Effect - Improved Haste - Full Attack";
            String[] ages = {"Young Adult", "Middle Age", "Old Age", "Venerable"};
            int[] penalties = {0, -1, -3, -6};
            for (int from = 0; from < ages.length; from++) {
                var naturalAge = new pcgen.core.PCTemplate();
                naturalAge.setName("Natural physical aging fixture " + ages[from]);
                require(Globals.getContext().processToken(naturalAge, "BONUS", "STAT|STR,DEX,CON|" + penalties[from]), "Age fixture");
                Globals.getContext().commit();
                pc.addTemplate(naturalAge);
                for (int to = 0; to < ages.length; to++) {
                    if (from == to) continue;
                    String key = "Time Effect - Age - " + ages[from] + " to " + ages[to];
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    for (String stat : new String[] {"STR", "DEX", "CON"}) {
                        require(pc.getTotalBonusTo("STAT", stat) == penalties[to], "Age transition " + key + " " + stat);
                    }
                    for (String stat : new String[] {"INT", "WIS", "CHA"}) {
                        require(pc.getTotalBonusTo("STAT", stat) == 0, "Age never changes mental scores");
                    }
                    facade.setTempBonusActive(effect(facade, key, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("STAT", "STR") == penalties[from], "Age disabling restores original penalty");
                    facade.removeTempBonus(effect(facade, key, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("STAT", "CON") == penalties[from], "Age expiration");
                }
                pc.removeTemplate(naturalAge);
            }
            var arcana = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Knowledge (Arcana)");
            var spellcraft = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Spellcraft");
            for (String[] target : new String[][] {{"Knowledge", "SKILL", "TYPE.Knowledge"},
                    {"Single Attack Defense", "COMBAT", "AC"}, {"Single Save", "SAVE", "Will"}}) {
                String timeline = "Time Effect - Timeline Bridge - " + target[0];
                double baseline = pc.getTotalBonusTo(target[1], target[2]);
                int arcanaBase = pcgen.core.analysis.SkillModifier.modifier(arcana, pc).intValue();
                int spellcraftBase = pcgen.core.analysis.SkillModifier.modifier(spellcraft, pc).intValue();
                for (int cl : new int[] {1, 2, 3, 10, 11, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(effect(facade, timeline, false));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline + cl / 2, "Timeline Bridge " + target[0] + " CL" + cl);
                    require(pcgen.core.analysis.SkillModifier.modifier(arcana, pc).intValue() == arcanaBase + (target[0].equals("Knowledge") ? cl / 2 : 0), "Timeline Bridge actual Knowledge");
                    require(pcgen.core.analysis.SkillModifier.modifier(spellcraft, pc).intValue() == spellcraftBase, "Timeline Bridge excludes Spellcraft");
                    facade.setTempBonusActive(effect(facade, timeline, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Timeline Bridge disabled");
                    facade.removeTempBonus(effect(facade, timeline, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Timeline Bridge removed");
                }
            }
            for (String suffix : new String[] {"Initiative", "Two Selections", "Three Selections"}) {
                String rapid = "Time Effect - Rapid Response - " + suffix;
                boolean initiative = suffix.equals("Initiative");
                String kind = initiative ? "COMBAT" : "SAVE";
                String stat = initiative ? "INITIATIVE" : "Reflex";
                double baseline = pc.getTotalBonusTo(kind, stat);
                for (int cl : new int[] {1, 2, 3, 10, 11, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(effect(facade, rapid, false));
                    pc.calcActiveBonuses();
                    int bonus = initiative ? Math.max(1, cl / 2) : suffix.equals("Two Selections") ? 2 : 4;
                    require(pc.getTotalBonusTo(kind, stat) == baseline + bonus, "Rapid Response " + suffix + " CL" + cl);
                    var competitor = new pcgen.core.PCTemplate();
                    competitor.setName("Rapid Response competing competence");
                    require(Globals.getContext().processToken(competitor, "BONUS", kind + "|" + stat + "|3|TYPE=Competence"), "Competence fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(competitor);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(kind, stat) == baseline + Math.max(3, bonus), "Rapid Response highest competence");
                    pc.removeTemplate(competitor);
                    facade.setTempBonusActive(effect(facade, rapid, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(kind, stat) == baseline, "Rapid Response disabling");
                    facade.removeTempBonus(effect(facade, rapid, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(kind, stat) == baseline, "Rapid Response removal");
                }
            }
            String broken = "Time Effect - Broken Time";
            for (int cl : new int[] {1, 2, 3, 9, 10, 11, 20}) {
                double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                double skill = pc.getTotalBonusTo("SKILL", "ALL");
                double will = pc.getTotalBonusTo("SAVE", "Will");
                double damage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
                choice.level = cl;
                facade.addTempBonus(effect(facade, broken, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack - cl / 2, "Broken Time attack CL" + cl);
                require(pc.getTotalBonusTo("SKILL", "ALL") == skill - cl / 2, "Broken Time skill CL" + cl);
                require(pc.getTotalBonusTo("SAVE", "Will") == will && pc.getTotalBonusTo("COMBAT", "DAMAGE") == damage, "Broken Time isolation");
                facade.setTempBonusActive(effect(facade, broken, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Broken Time disabled");
                facade.removeTempBonus(effect(facade, broken, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == skill, "Broken Time refund");
            }
            double attacks = pc.getTotalBonusTo("COMBAT", "ATTACKS");
            facade.addTempBonus(effect(facade, fullAttack, false));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "ATTACKS") == attacks + 1, "Improved Haste extra full attack");
            var competing = new pcgen.core.PCTemplate();
            competing.setName("Haste spell extra attack fixture");
            require(Globals.getContext().processToken(competing, "BONUS", "COMBAT|ATTACKS|1|TYPE=Enhancement"), "Extra attack stacking fixture");
            Globals.getContext().commit();
            pc.addTemplate(competing);
            require(pc.getTotalBonusTo("COMBAT", "ATTACKS") == attacks + 1, "Improved Haste cannot stack with haste extra attack");
            pc.removeTemplate(competing);
            facade.removeTempBonus(effect(facade, fullAttack, true));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "ATTACKS") == attacks, "Full attack refund");
            String aoo = "Time Effect - Improved Haste - Attacks of Opportunity";
            for (int cl : new int[] {1, 4, 5, 9, 10, 20}) {
                choice.level = cl;
                facade.addTempBonus(effect(facade, aoo, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_IMPROVED_HASTE_AOO") == 1 + cl / 5, "Improved Haste opportunity capacity");
                require(pc.getTotalBonusTo("COMBAT", "ATTACKS") == attacks, "Opportunity option grants no full attack");
                facade.removeTempBonus(effect(facade, aoo, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_IMPROVED_HASTE_AOO") == 0, "Opportunity capacity removal");
            }
            String[] names = {"Haste - Attack", "Haste - Dodge", "Slow - Penalties", "Haste - Walk"};
            for (String name : names) {
                String key = "Time Effect - " + name;
                double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                double ac = pc.getTotalBonusTo("COMBAT", "AC");
                double reflex = pc.getTotalBonusTo("SAVE", "Reflex");
                double will = pc.getTotalBonusTo("SAVE", "Will");
                var walkType = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
                double walk = pc.getDisplay().movementOfType(walkType);
                for (int cl : new int[] {1, 4, 5, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    int bonus = 1 + cl / 10;
                    require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack + (name.equals("Haste - Attack") ? bonus : name.equals("Slow - Penalties") ? -bonus : 0), "Time attack isolation");
                    int defense = name.equals("Haste - Dodge") ? bonus : name.equals("Slow - Penalties") ? -bonus : 0;
                    require(pc.getTotalBonusTo("COMBAT", "AC") == ac + defense, "Time AC");
                    require(pc.getTotalBonusTo("SAVE", "Reflex") == reflex + defense, "Time Reflex");
                    require(pc.getTotalBonusTo("SAVE", "Will") == will, "Time does not modify Will");
                    require(pc.getDisplay().movementOfType(walkType) == walk + (name.equals("Haste - Walk") ? 10 + 10 * (cl / 5) : 0), "Haste movement");
                    facade.setTempBonusActive(effect(facade, key, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack && pc.getTotalBonusTo("COMBAT", "AC") == ac, "Disabled Time modifiers");
                    facade.removeTempBonus(effect(facade, key, true));
                    pc.calcActiveBonuses();
                    require(pc.getDisplay().movementOfType(walkType) == walk, "Movement refund");
                }
            }
            choice.level = 20;
            String savedAge = "Time Effect - Age - Young Adult to Venerable";
            facade.addTempBonus(effect(facade, savedAge, false));
            facade.setTempBonusActive(effect(facade, savedAge, true), false);
            facade.addTempBonus(effect(facade, aoo, false));
            facade.addTempBonus(effect(facade, fullAttack, false));
            facade.setTempBonusActive(effect(facade, fullAttack, true), false);
            facade.addTempBonus(effect(facade, retained, false));
            facade.setTempBonusActive(effect(facade, retained, true), false);
            choice.level = 11;
            facade.addTempBonus(effect(facade, "Time Effect - Timeline Bridge - Knowledge", false));
            facade.addTempBonus(effect(facade, "Time Effect - Rapid Response - Initiative", false));
            facade.addTempBonus(effect(facade, broken, false));
            facade.setTempBonusActive(effect(facade, broken, true), false);
        } finally {
            ChooserFactory.setDelegate(old);
        }
        if (!reload) {
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}