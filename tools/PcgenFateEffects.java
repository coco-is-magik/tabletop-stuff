package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.PCTemplate;
import pcgen.facade.core.ChooserFacade;
import pcgen.facade.core.TempBonusFacade;
import pcgen.system.CharacterManager;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Received bonuses do not grant their source talents or execute combat actions. */
class PcgenFateEffects {
    private static class Choice extends Messages {
        int value;
        boolean cancel;
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            if (cancel) return false;
            for (var item : chooser.getAvailableList()) {
                if (item.toString().equals(Integer.toString(value))) {
                    chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing modifier choice " + value);
        }
    }

    private static TempBonusFacade effect(CharacterFacadeImpl facade, String key, boolean applied) {
        var effects = applied ? facade.getTempBonuses() : facade.getAvailableTempBonuses();
        for (var effect : effects) if (effect.getKeyName().equals(key)) return effect;
        throw new IllegalStateException("Missing " + (applied ? "applied " : "available ") + key);
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = (CharacterFacadeImpl) CharacterManager.getCharacters().iterator().next();
        var choice = new Choice();
        var delegate = ChooserFactory.getDelegate();
        ChooserFactory.setDelegate(choice);
        String villainy = "Fate Effect - Villainy - Paid Ally Bonus";
        String sun = "Fate Effect - The Sun - Discharged";
        boolean reload = args[4].equals("fate-reload");
        try {
            var game = pcgen.core.SettingsHandler.getGameAsProperty().get();
            var magic = game.getAbilityCategory("Spheres Magic Talent");
            var feats = game.getAbilityCategory("FEAT");
            var controller = new CharacterAbilities(pc, choice, facade.getDataSet(), new TodoManager());
            try {
                if (reload) {
                    var retainedFate = ability(magic, "Fate Sphere");
                    var retainedRange = ability(magic, "Fate - Resounding Word");
                    int retainedCl = pc.getVariableValue("SPHERES_CL_FATE", "").intValue();
                    require(pc.getVariableValue("SPHERES_FATE_EMPRESS_INITIAL_POINTS", "").intValue() == 1 + retainedCl, "Saved Empress starting pool");
                    require(pc.getVariableValue("SPHERES_FATE_WHEEL_D4_COUNT", "").intValue() == 1 + retainedCl / 10, "Saved Wheel dice count");
                    for (String name : new String[] {"The Empress", "The Wheel", "Cups", "Pentacles", "Swords", "Wands"})
                        controller.removeAbility(magic, ability(magic, "Fate - " + name));
                    require(pc.getVariableValue("SPHERES_FATE_EMPRESS_INITIAL_POINTS", "").intValue() == 0, "Saved Empress removal");
                    require(pc.getVariableValue("SPHERES_FATE_WHEEL_D4_COUNT", "").intValue() == 0, "Saved Wheel removal");
                    require(pc.getVariableValue("SPHERES_FATE_RESOUNDINGWORD_COUNT", "").intValue() == 2, "Saved repeated Resounding Word count");
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 400 + 40 * retainedCl, "Saved long word range");
                    controller.removeAbility(magic, retainedRange);
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 100 + 10 * retainedCl, "Saved partial range refund");
                    controller.removeAbility(magic, retainedRange);
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 25 + 5 * (retainedCl / 2), "Saved full range refund");
                    controller.removeAbility(magic, retainedFate);
                }
                var spite = ability(feats, "Spiteful End");
                require(!spite.qualifies(pc, spite), "Spiteful End rejects neither sphere");
                for (String sphere : new String[] {"Death Sphere", "Fate Sphere"}) {
                    var selected = ability(magic, sphere);
                    controller.addAbility(magic, selected);
                    require(spite.qualifies(pc, spite), "Either sphere qualifies independently " + sphere);
                    controller.removeAbility(magic, selected);
                    require(!spite.qualifies(pc, spite), "Sphere loss revokes Spiteful End");
                }
                var fate = ability(magic, "Fate Sphere");
                var mana = ability(magic, "Mana Sphere");
                var divination = ability(magic, "Divination Sphere");
                var precognition = ability(feats, "Precogniscent Protection");
                require(!precognition.qualifies(pc, precognition), "Precognition requires a sense source");
                controller.addAbility(magic, divination);
                require(precognition.qualifies(pc, precognition), "Read Magic satisfies base sense ability");
                controller.removeAbility(magic, divination);
                require(!precognition.qualifies(pc, precognition), "Base sense removal revokes qualification");
                var favoriteBoost = ability(feats, "Favorite Boost");
                require(!favoriteBoost.qualifies(pc, favoriteBoost), "Favorite Boost requires Mana and an amp");
                controller.addAbility(magic, mana);
                require(!favoriteBoost.qualifies(pc, favoriteBoost), "Mana base sphere is not an amp talent");
                var bulwark = ability(magic, "Mana - Bulwark");
                controller.addAbility(magic, bulwark);
                require(!favoriteBoost.qualifies(pc, favoriteBoost), "Manipulation alone is not amp");
                controller.removeAbility(magic, bulwark);
                for (String name : new String[] {"Arcanodynamics", "Heightened Magic"}) {
                    var amp = ability(magic, "Mana - " + name);
                    controller.addAbility(magic, amp);
                    require(favoriteBoost.qualifies(pc, favoriteBoost), "Reviewed amp member " + name);
                    controller.removeAbility(magic, amp);
                    require(!favoriteBoost.qualifies(pc, favoriteBoost), "Amp removal revokes qualification");
                }
                controller.removeAbility(magic, mana);
                var firewall = ability(feats, "Sacrosanct Firewall");
                var technomancy = ability(magic, "Technomancy Sphere");
                require(!firewall.qualifies(pc, firewall), "Firewall rejects no spheres");
                controller.addAbility(magic, technomancy);
                require(!firewall.qualifies(pc, firewall), "Firewall requires Fate base word");
                controller.addAbility(magic, fate);
                require(firewall.qualifies(pc, firewall), "Firewall accepts base Hallow and Technomancy");
                controller.removeAbility(magic, technomancy);
                require(!firewall.qualifies(pc, firewall), "Firewall independently requires Technomancy");
                controller.removeAbility(magic, fate);
                var war = ability(magic, "War Sphere");
                var rally = ability(magic, "War - Absorb");
                var vigilance = ability(feats, "Sanctified Vigilance");
                controller.addAbility(magic, fate);
                controller.addAbility(magic, war);
                require(!vigilance.qualifies(pc, vigilance), "Base spheres do not replace a purchased rally talent");
                controller.addAbility(magic, rally);
                require(vigilance.qualifies(pc, vigilance), "Purchased rally qualifies");
                controller.removeAbility(magic, rally);
                require(!vigilance.qualifies(pc, vigilance), "Rally removal revokes qualification");
                controller.removeAbility(magic, war);
                controller.removeAbility(magic, fate);
                require(choice.errors.isEmpty(), "Qualification controller errors " + choice.errors);
                controller.addAbility(magic, fate);
                var resounding = ability(magic, "Fate - Resounding Word");
                double baselineCl = pc.getVariableValue("SPHERES_CL_FATE", "").doubleValue();
                for (int cl : new int[] {1, 2, 4, 5, 6, 7, 9, 10, 13, 14, 20, 21}) {
                    var level = new PCTemplate();
                    level.setName("Fate caster level boundary " + cl);
                    require(Globals.getContext().processToken(level, "BONUS", "VAR|SPHERES_CL_FATE|" + (cl - baselineCl)), "Fate level fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(level);
                    require(pc.getVariableValue("SPHERES_FATE_CONSECRATION_RADIUS", "").intValue() == 20 + 5 * (cl / 5), "Fate radius boundary");
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 25 + 5 * (cl / 2), "Fate close range");
                    controller.addAbility(magic, resounding);
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 100 + 10 * cl, "Fate medium range");
                    controller.addAbility(magic, resounding);
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 400 + 40 * cl, "Fate long range");
                    require(!resounding.qualifies(pc, resounding), "Resounding third selection disallowed");
                    controller.removeAbility(magic, resounding);
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 100 + 10 * cl, "Fate partial range refund");
                    controller.removeAbility(magic, resounding);
                    require(pc.getVariableValue("SPHERES_FATE_WORD_RANGE", "").intValue() == 25 + 5 * (cl / 2), "Fate full range refund");
                    for (String[] pair : new String[][] {{"Echoing Word", "ECHOING_ADDITIONAL_TARGETS"},
                            {"Bargain", "BARGAIN_ROUNDS"}, {"Harm", "HARM_DAMAGE"}, {"Consequences", "CONSEQUENCES_DAMAGE"}}) {
                        var talent = ability(magic, "Fate - " + pair[0]);
                        controller.addAbility(magic, talent);
                        require(pc.getVariableValue("SPHERES_FATE_" + pair[1], "").intValue() ==
                                (pair[0].equals("Consequences") ? cl : Math.max(1, cl / 2)), "Fate reference " + pair[0]);
                        if (pair[0].equals("Consequences"))
                            require(pc.getVariableValue("SPHERES_FATE_CONSEQUENCES_PER_ROUND", "").intValue() == 1 + cl / 5, "Consequences limit");
                        controller.removeAbility(magic, talent);
                        require(pc.getVariableValue("SPHERES_FATE_" + pair[1], "").intValue() == 0, "Fate reference removal");
                    }
                    pc.removeTemplate(level);
                    var undo = ability(magic, "Fate - Undo Harm");
                    pc.addTemplate(level);
                    String[][] motifValues = {{"The Tower", "TOWER_BYPASS", "TOWER_DISCHARGE_D4"},
                            {"The Queen", "QUEEN_FEAR_ROUND_REDUCTION", "QUEEN_DISCHARGE_DAMAGE_REDUCTION"},
                            {"The Page", "PAGE_MORALE_EXTRA_ROUNDS"}, {"The Lovers", "LOVERS_MAX_SAVE_BONUS"},
                            {"Cups", "CUPS_RETAINED_D20", "CUPS_DISCHARGE_MINUTES"},
                            {"Pentacles", "PENTACLES_REROLLS", "PENTACLES_DISCHARGE_MINUTES"},
                            {"Swords", "SWORDS_CONFIRM_BONUS", "SWORDS_DISCHARGE_MINUTES"},
                            {"Wands", "WANDS_DISCHARGE_MINUTES"},
                            {"The Empress", "EMPRESS_INITIAL_POINTS", "EMPRESS_SPEND_LIMIT"},
                            {"The Wheel", "WHEEL_D4_COUNT", "WHEEL_BONUS_PER_RESULT"}};
                    int[][] expectedMotifs = {{5 + cl / 4, cl}, {2 + cl / 5, Math.max(1, cl / 2)},
                            {1 + cl / 10}, {2 + cl / 5}, {2 + cl / 7, cl},
                            {1 + cl / 10, cl}, {Math.max(1, cl / 2), 1}, {cl},
                            {1 + cl, Math.max(1, cl / 5)}, {1 + cl / 10, 1 + cl / 10}};
                    for (int i = 0; i < motifValues.length; i++) {
                        var motif = ability(magic, "Fate - " + motifValues[i][0]);
                        controller.addAbility(magic, motif);
                        for (int j = 1; j < motifValues[i].length; j++)
                            require(pc.getVariableValue("SPHERES_FATE_" + motifValues[i][j], "").intValue() == expectedMotifs[i][j - 1], "Motif caster reference " + motifValues[i][j]);
                        controller.removeAbility(magic, motif);
                        for (int j = 1; j < motifValues[i].length; j++)
                            require(pc.getVariableValue("SPHERES_FATE_" + motifValues[i][j], "").intValue() == 0, "Motif reference removal " + motifValues[i][j]);
                    }
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_MAX_HEALING", "").intValue() == 0, "Undo Harm absent");
                    controller.addAbility(magic, undo);
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_MAX_HEALING", "").intValue() == 5 + cl, "Undo Harm healing cap");
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_CONDITIONS", "").intValue() == 0, "First Undo Harm has no condition removal");
                    controller.addAbility(magic, undo);
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_CONDITIONS", "").intValue() == 1 + cl / 10, "Second Undo Harm condition limit");
                    controller.removeAbility(magic, undo);
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_MAX_HEALING", "").intValue() == 5 + cl, "Undo Harm partial refund preserves healing");
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_CONDITIONS", "").intValue() == 0, "Undo Harm partial refund removes condition benefit");
                    controller.removeAbility(magic, undo);
                    require(pc.getVariableValue("SPHERES_FATE_UNDO_HARM_MAX_HEALING", "").intValue() == 0, "Undo Harm full refund");
                    pc.removeTemplate(level);
                }
                controller.removeAbility(magic, fate);
            } finally {
                controller.closeCharacter();
            }
            if (reload) {
                String emperorReduction = "Fate Effect - The Emperor - Penalty Reduction - Initiative";
                String savedConfirmation = "Fate Effect - Swords - Discharged Confirmation Only";
                double beforeConfirmation = pc.getTotalBonusTo("COMBAT", "TOHIT");
                facade.setTempBonusActive(effect(facade, savedConfirmation, true), true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == beforeConfirmation + 5, "Saved inactive Swords CL10 confirmation");
                facade.removeTempBonus(effect(facade, savedConfirmation, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == beforeConfirmation, "Saved confirmation removal");
                String savedKnight = "Fate Effect - The Knight - Condition Initiative Penalties";
                double beforeKnight = pc.getTotalBonusTo("COMBAT", "INITIATIVE");
                facade.setTempBonusActive(effect(facade, savedKnight, true), true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == beforeKnight + 4, "Saved inactive Knight input four");
                facade.removeTempBonus(effect(facade, savedKnight, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == beforeKnight, "Saved Knight independent removal");
                String savedLovers = "Fate Effect - The Lovers - Adjacent Allies";
                double beforeLovers = pc.getTotalBonusTo("SAVE", "Will");
                facade.removeTempBonus(effect(facade, savedLovers, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == beforeLovers - 1, "Saved Lovers eight replaces Emperor seven");
                String savedPage = "Fate Effect - The Page - Discharged Morale - Skill";
                double beforePage = pc.getTotalBonusTo("SKILL", "ALL");
                facade.setTempBonusActive(effect(facade, savedPage, true), true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == beforePage + 6, "Saved inactive Page retains morale input three");
                facade.removeTempBonus(effect(facade, savedPage, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == beforePage, "Saved Page independent removal");
                String emperorDischarge = "Fate Effect - The Emperor - Discharged Insight - Save";
                double savedInitiative = pc.getTotalBonusTo("COMBAT", "INITIATIVE");
                facade.setTempBonusActive(effect(facade, emperorReduction, true), true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == savedInitiative + 2, "Saved inactive Emperor reduction retains chosen magnitude");
                facade.removeTempBonus(effect(facade, emperorReduction, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == savedInitiative, "Saved Emperor reduction removal");
                double savedEmperorWill = pc.getTotalBonusTo("SAVE", "Will");
                facade.removeTempBonus(effect(facade, emperorDischarge, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == savedEmperorWill - 4, "Saved Emperor insight competes with Sun insight instead of stacking");
                double savedWheelAttack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                double savedWheelDamage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
                facade.removeTempBonus(effect(facade, "Fate Effect - The Wheel - Ongoing - 1 - Attack and Damage", true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == savedWheelAttack - 6, "Saved repeated Wheel category attack");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == savedWheelDamage - 6, "Saved repeated Wheel category damage");
                double savedWheelSkill = pc.getTotalBonusTo("SKILL", "ALL");
                facade.removeTempBonus(effect(facade, "Fate Effect - The Wheel - Discharged - Skill", true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == savedWheelSkill - 16, "Saved Wheel discharge sum eight");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 7, "Saved Malice plus Villainy");
                require(pc.getTotalBonusTo("CONCENTRATION", "ALLSPELLS") == 3, "Saved King CL20 spell concentration");
                int savedConcentration = pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue();
                facade.removeTempBonus(effect(facade, "Fate Effect - The King", true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("CONCENTRATION", "ALLSPELLS") == 0, "Saved King spell refund");
                require(pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue() == savedConcentration - 3, "Saved King sphere refund");
                require(pc.getTotalBonusTo("SAVE", "Will") == 6, "Saved Malice plus Sun");
                facade.removeTempBonus(effect(facade, "Fate Effect - Malice - Accumulated Bonus", true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "STAT.INT") == -4, "Saved Pain mental skill penalty");
                facade.removeTempBonus(effect(facade, "Fate Effect - Pain", true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "STAT.INT") == 0, "Saved Pain removal");
                String discharged = "Fate Effect - The Hanged Man - Discharged - Combat Maneuver";
                require(pc.getTotalBonusTo("COMBAT", "CMB") == 3, "Saved Hanged Man seven damage bonus");
                facade.removeTempBonus(effect(facade, discharged, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "CMB") == 0, "Saved Hanged Man refund");
                require(pc.getTotalBonusTo("SKILL", "ALL") == 4, "Saved Borrow Trouble skill bonus");
                facade.removeTempBonus(effect(facade, "Fate Effect - Borrow Trouble - Skill Checks", true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Saved Borrow Trouble removal");
                var savedWalk = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
                double speed = pc.getDisplay().movementOfType(savedWalk);
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 1, "Saved Perfect DEX initiative");
                facade.removeTempBonus(effect(facade, "Fate Effect - Perfect - DEX", true));
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(savedWalk) == speed - 20, "Saved Perfect CL10 movement removal");
                String trained = "Fate Effect - Perfect - INT - Trained Check Only";
                require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Saved trained modifier stays inactive");
                facade.setTempBonusActive(effect(facade, trained, true), true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == 4, "Saved trained CL10 reactivation");
                facade.removeTempBonus(effect(facade, trained, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 4, "Saved Villainy CL9");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 4, "Saved weapon damage");
                require(pc.getTotalBonusTo("SAVE", "Will") == 3, "Saved Sun modifier");
                facade.removeTempBonus(effect(facade, villainy, true));
                facade.removeTempBonus(effect(facade, sun, true));
                pc.calcActiveBonuses();
            }
            double baseAc = pc.getTotalBonusTo("COMBAT", "AC");
            for (int cl : new int[] {1, 4, 5, 9, 10, 19, 20}) {
                choice.value = cl;
                String nature = "Divination Effect - Nature Sense";
                facade.addTempBonus(effect(facade, nature, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "Knowledge (Nature)") == 1 + cl / 5, "Nature Sense scaling");
                require(pc.getTotalBonusTo("SKILL", "Survival") == 1 + cl / 5, "Nature Sense Survival");
                require(pc.getTotalBonusTo("SKILL", "Perception") == 0, "Nature Sense skill isolation");
                facade.removeTempBonus(effect(facade, nature, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "Survival") == 0, "Nature Sense removal");
                for (String[] entry : new String[][] {{"Prescience", "TOHIT"},
                        {"Prescience - Dismissed Attack", "TOHIT"}, {"Prescience - Dismissed Maneuver", "CMB"}}) {
                    String key = "Divination Effect - " + entry[0];
                    int bonus = entry[0].equals("Prescience") ? 1 + cl / 10 : 10 + cl / 2;
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", entry[1]) == bonus, "Prescience current formula " + key);
                    require(pc.getTotalBonusTo("COMBAT", "CMD") == 0 && pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0, "Prescience excludes damage and defense");
                    var insight = new PCTemplate();
                    insight.setName("Prescience competing insight");
                    require(Globals.getContext().processToken(insight, "BONUS", "COMBAT|" + entry[1] + "|5|TYPE=Insight"), "Prescience stacking fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(insight);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", entry[1]) == Math.max(5, bonus), "Prescience highest insight");
                    pc.removeTemplate(insight);
                    facade.setTempBonusActive(effect(facade, key, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", entry[1]) == 0, "Prescience disabled");
                    facade.removeTempBonus(effect(facade, key, true));
                }
                String foreshadow = "Divination Effect - Foreshadow";
                String dodge = foreshadow + " - Dodge AC";
                facade.addTempBonus(effect(facade, foreshadow, false));
                facade.addTempBonus(effect(facade, dodge, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Reflex") == 2 + cl / 10, "Foreshadow Reflex scaling");
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 2 + cl / 10, "Foreshadow initiative scaling");
                require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc + 1 + cl / 10, "Foreshadow dodge scaling");
                facade.setTempBonusActive(effect(facade, dodge, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Foreshadow denied dodge");
                require(pc.getTotalBonusTo("SAVE", "Reflex") == 2 + cl / 10, "Dodge loss preserves Reflex");
                facade.removeTempBonus(effect(facade, dodge, true));
                facade.removeTempBonus(effect(facade, foreshadow, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Reflex") == 0 && pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 0, "Foreshadow refund");
            }
            String swordsConfirmation = "Fate Effect - Swords - Discharged Confirmation Only";
            for (int cl : new int[] {1, 2, 3, 4, 9, 10, 19, 20}) {
                choice.value = cl;
                facade.addTempBonus(effect(facade, swordsConfirmation, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == Math.max(1, cl / 2), "Swords confirmation minimum and scaling");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Swords confirmation excludes damage and defense");
                facade.setTempBonusActive(effect(facade, swordsConfirmation, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Ordinary attacks outside confirmation context");
                facade.removeTempBonus(effect(facade, swordsConfirmation, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Swords confirmation removal");
            }
            String knight = "Fate Effect - The Knight - Condition Initiative Penalties";
            for (int penalty : new int[] {0, 2, 3, 4, 6}) {
                var conditions = new PCTemplate();
                conditions.setName("Knight condition and unrelated penalty fixture");
                require(Globals.getContext().processToken(conditions, "BONUS", "COMBAT|INITIATIVE|-" + (penalty + 1)), "Knight initiative fixture");
                require(Globals.getContext().processToken(conditions, "BONUS", "COMBAT|TOHIT|-2"), "Knight unrelated condition effect");
                Globals.getContext().commit();
                pc.addTemplate(conditions);
                choice.value = penalty;
                facade.addTempBonus(effect(facade, knight, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == -1, "Knight preserves noncondition initiative penalty");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == -2, "Knight preserves other condition effects");
                facade.removeTempBonus(effect(facade, knight, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == -penalty - 1, "Knight expiration restores full penalty");
                pc.removeTemplate(conditions);
                pc.calcActiveBonuses();
            }
            String lovers = "Fate Effect - The Lovers - Adjacent Allies";
            for (int allies : new int[] {0, 1, 2, 6, 1, 0}) {
                choice.value = allies;
                facade.addTempBonus(effect(facade, lovers, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == allies, "Lovers current capped adjacency");
                require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc && pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Lovers affects saves only");
                var insight = new PCTemplate();
                insight.setName("Lovers competing insight fixture");
                require(Globals.getContext().processToken(insight, "BONUS", "SAVE|ALL|3|TYPE=Insight"), "Lovers fixture");
                Globals.getContext().commit();
                pc.addTemplate(insight);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == Math.max(3, allies), "Lovers highest insight");
                pc.removeTemplate(insight);
                facade.removeTempBonus(effect(facade, lovers, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Lovers adjacency reset");
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"}, {"Damage", "COMBAT", "DAMAGE"},
                    {"Save", "SAVE", "Will"}, {"Skill", "SKILL", "ALL"}, {"Initiative", "COMBAT", "INITIATIVE"}}) {
                String page = "Fate Effect - The Page - Discharged Morale - " + target[0];
                for (int magnitude : new int[] {1, 2, 5}) {
                    var morale = new PCTemplate();
                    morale.setName("Page original morale fixture");
                    require(Globals.getContext().processToken(morale, "BONUS", target[1] + "|" + target[2] + "|" + magnitude + "|TYPE=Morale"), "Page morale fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(morale);
                    choice.value = magnitude;
                    facade.addTempBonus(effect(facade, page, false));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 2 * magnitude, "Page doubles rather than triples morale");
                    require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Page does not alter AC");
                    facade.setTempBonusActive(effect(facade, page, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == magnitude, "Page disabling preserves original bonus");
                    facade.removeTempBonus(effect(facade, page, true));
                    pc.removeTemplate(morale);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 0, "Page cleanup");
                }
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"}, {"Damage", "COMBAT", "DAMAGE"},
                    {"Save", "SAVE", "Will"}, {"Skill", "SKILL", "ALL"}, {"Initiative", "COMBAT", "INITIATIVE"}}) {
                String emperor = "Fate Effect - The Emperor - Penalty Reduction - " + target[0];
                String emperorDischarge = "Fate Effect - The Emperor - Discharged Insight - " + target[0];
                for (int magnitude : new int[] {1, 3, 6}) {
                    choice.value = magnitude;
                    facade.addTempBonus(effect(facade, emperorDischarge, false));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == magnitude, "Emperor external penalty insight");
                    var insight = new PCTemplate();
                    insight.setName("Emperor discharge competing insight");
                    require(Globals.getContext().processToken(insight, "BONUS", target[1] + "|" + target[2] + "|4|TYPE=Insight"), "Emperor insight fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(insight);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == Math.max(4, magnitude), "Emperor highest insight");
                    pc.removeTemplate(insight);
                    facade.removeTempBonus(effect(facade, emperorDischarge, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 0, "Emperor discharge expiration");
                }
                for (int cl : new int[] {1, 9, 10, 20}) {
                    for (int magnitude : new int[] {2, 3, 6}) {
                        var penalty = new PCTemplate();
                        penalty.setName("Emperor original penalty fixture");
                        require(Globals.getContext().processToken(penalty, "BONUS", target[1] + "|" + target[2] + "|-" + magnitude), "Emperor penalty fixture");
                        Globals.getContext().commit();
                        pc.addTemplate(penalty);
                        choice.value = Math.min(1 + cl / 10, magnitude - 1);
                        facade.addTempBonus(effect(facade, emperor, false));
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == -magnitude + choice.value, "Emperor partial penalty offset");
                        require(pc.getTotalBonusTo(target[1], target[2]) <= -1, "Emperor leaves minimum penalty");
                        require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Emperor does not alter AC");
                        facade.removeTempBonus(effect(facade, emperor, true));
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == -magnitude, "Emperor removal restores penalty");
                        pc.removeTemplate(penalty);
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == 0, "Emperor fixture cleanup");
                    }
                }
            }
            String[] wheelCategories = {"1 - Attack and Damage", "2 - Saves", "3 - Initiative and Skills", "4 - Concentration and Maneuvers"};
            String[][] wheelStats = {{"COMBAT", "TOHIT"}, {"COMBAT", "DAMAGE"}, {"SAVE", "Will"},
                    {"COMBAT", "INITIATIVE"}, {"SKILL", "ALL"}, {"CONCENTRATION", "ALLSPELLS"},
                    {"COMBAT", "CMB"}, {"COMBAT", "CMD"}};
            int[] wheelGroups = {0, 0, 1, 2, 2, 3, 3, 3};
            for (int category = 0; category < wheelCategories.length; category++) {
                String key = "Fate Effect - The Wheel - Ongoing - " + wheelCategories[category];
                for (int total : new int[] {1, 2, 4, 6, 9}) {
                    choice.value = total;
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    for (int i = 0; i < wheelStats.length; i++)
                        require(pc.getTotalBonusTo(wheelStats[i][0], wheelStats[i][1]) == (wheelGroups[i] == category ? total : 0), "Wheel ongoing category isolation " + category);
                    require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Wheel does not increase AC");
                    var insight = new PCTemplate();
                    insight.setName("Wheel insight fixture");
                    for (int i = 0; i < wheelStats.length; i++)
                        if (wheelGroups[i] == category)
                            require(Globals.getContext().processToken(insight, "BONUS", wheelStats[i][0] + "|" + wheelStats[i][1] + "|3|TYPE=Insight"), "Wheel competing insight");
                    Globals.getContext().commit();
                    pc.addTemplate(insight);
                    pc.calcActiveBonuses();
                    for (int i = 0; i < wheelStats.length; i++)
                        if (wheelGroups[i] == category)
                            require(pc.getTotalBonusTo(wheelStats[i][0], wheelStats[i][1]) == Math.max(3, total), "Wheel highest insight, repeated results already summed");
                    pc.removeTemplate(insight);
                    facade.removeTempBonus(effect(facade, key, true));
                    pc.calcActiveBonuses();
                    for (String[] stat : wheelStats) require(pc.getTotalBonusTo(stat[0], stat[1]) == 0, "Wheel ongoing removal");
                }
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"},
                    {"Save", "SAVE", "Will"}, {"Skill", "SKILL", "ALL"},
                    {"Initiative", "COMBAT", "INITIATIVE"}, {"Concentration", "CONCENTRATION", "ALLSPELLS"}}) {
                String wheel = "Fate Effect - The Wheel - Discharged - " + target[0];
                double base = pc.getTotalBonusTo(target[1], target[2]);
                for (int sum : new int[] {1, 4, 5, 8, 12}) {
                    choice.value = sum;
                    facade.addTempBonus(effect(facade, wheel, false));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == base + 2 * sum, "Wheel double dice sum " + target[0]);
                    require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("COMBAT", "CMD") == 0, "Wheel discharge excludes damage and CMD");
                    facade.setTempBonusActive(effect(facade, wheel, true), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == base, "Wheel single roll ending");
                    facade.removeTempBonus(effect(facade, wheel, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == base, "Wheel refund");
                }
            }
            String king = "Fate Effect - The King";
            int concentrationBase = pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue();
            int casterBase = pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue();
            for (int cl : new int[] {1, 9, 10, 19, 20}) {
                choice.value = cl;
                facade.addTempBonus(effect(facade, king, false));
                pc.calcActiveBonuses();
                int bonus = 1 + cl / 10;
                require(pc.getTotalBonusTo("CONCENTRATION", "ALLSPELLS") == bonus, "King spell concentration");
                require(pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue() == concentrationBase + bonus, "King sphere concentration");
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == casterBase, "King does not increase CL");
                var competing = new PCTemplate();
                competing.setName("King competing insight fixture");
                require(Globals.getContext().processToken(competing, "BONUS", "CONCENTRATION|ALLSPELLS|2|TYPE=Insight"), "King spell stacking fixture");
                require(Globals.getContext().processToken(competing, "BONUS", "VAR|SPHERES_CONCENTRATION_CHECK|2|TYPE=Insight"), "King sphere stacking fixture");
                Globals.getContext().commit();
                pc.addTemplate(competing);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("CONCENTRATION", "ALLSPELLS") == Math.max(2, bonus), "King spell highest insight");
                require(pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue() == concentrationBase + Math.max(2, bonus), "King sphere highest insight");
                pc.removeTemplate(competing);
                facade.setTempBonusActive(effect(facade, king, true), false);
                pc.calcActiveBonuses();
                require(pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue() == concentrationBase, "King discharge");
                facade.removeTempBonus(effect(facade, king, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("CONCENTRATION", "ALLSPELLS") == 0, "King removal");
            }
            String acceleratedDiplomacy = "Fate Effect - Perfect - CHA - One Round Diplomacy";
            var diplomacy = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Diplomacy");
            var bluff = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Bluff");
            double diplomacyBase = pcgen.core.analysis.SkillModifier.modifier(diplomacy, pc);
            double bluffBase = pcgen.core.analysis.SkillModifier.modifier(bluff, pc);
            choice.value = 5;
            facade.addTempBonus(effect(facade, "Fate Effect - Perfect - CHA", false));
            facade.addTempBonus(effect(facade, acceleratedDiplomacy, false));
            pc.calcActiveBonuses();
            require(pcgen.core.analysis.SkillModifier.modifier(diplomacy, pc) == diplomacyBase - 9, "Accelerated Diplomacy combines penalty and Perfect CHA");
            require(pcgen.core.analysis.SkillModifier.modifier(bluff, pc) == bluffBase + 1, "Accelerated Diplomacy leaves other CHA skills alone");
            facade.setTempBonusActive(effect(facade, acceleratedDiplomacy, true), false);
            pc.calcActiveBonuses();
            require(pcgen.core.analysis.SkillModifier.modifier(diplomacy, pc) == diplomacyBase + 1, "Ordinary Diplomacy retains only Perfect bonus");
            facade.removeTempBonus(effect(facade, acceleratedDiplomacy, true));
            facade.removeTempBonus(effect(facade, "Fate Effect - Perfect - CHA", true));
            pc.calcActiveBonuses();
            require(pcgen.core.analysis.SkillModifier.modifier(diplomacy, pc) == diplomacyBase, "Perfect Diplomacy removal");
            String malice = "Fate Effect - Malice - Accumulated Bonus";
            for (int total : new int[] {1, 2, 4, 3, 1}) {
                choice.value = total;
                facade.addTempBonus(effect(facade, malice, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == total && pc.getTotalBonusTo("COMBAT", "DAMAGE") == total,
                        "Malice replacement total " + total);
                for (String save : new String[] {"Fortitude", "Reflex", "Will"})
                    require(pc.getTotalBonusTo("SAVE", save) == total, "Malice save " + save);
                require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc && pc.getTotalBonusTo("SKILL", "ALL") == 0,
                        "Malice excludes AC and skills");
                facade.setTempBonusActive(effect(facade, malice, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Malice inactive");
                facade.removeTempBonus(effect(facade, malice, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("SAVE", "Will") == 0,
                        "Malice reset and expiration");
            }
            for (String strength : new String[] {"Strong", "Overwhelming"}) {
                String key = "Fate Effect - Enmity - " + strength + " Opposing Aura";
                int penalty = strength.equals("Strong") ? 1 : 2;
                facade.addTempBonus(effect(facade, key, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == -penalty, "Enmity opposing aura " + strength);
                require(pc.getTotalBonusTo("SAVE", "Fortitude") == 0 && pc.getTotalBonusTo("SAVE", "Reflex") == 0,
                        "Enmity save isolation");
                facade.setTempBonusActive(effect(facade, key, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Enmity disabled outside save");
                facade.removeTempBonus(effect(facade, key, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Enmity removal");
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"},
                    {"Save", "SAVE", "Will"}, {"Skill", "SKILL", "ALL"},
                    {"Initiative", "COMBAT", "INITIATIVE"}}) {
                for (boolean positive : new boolean[] {true, false}) {
                    String key = "Fate Effect - Tug Fate - " + (positive ? "Bonus" : "Penalty") + " - " + target[0];
                    double baseline = pc.getTotalBonusTo(target[1], target[2]);
                    for (int cl : new int[] {1, 2, 3, 10, 19, 20}) {
                        choice.value = cl;
                        facade.addTempBonus(effect(facade, key, false));
                        pc.calcActiveBonuses();
                        int amount = (positive ? 1 : -1) * (10 + cl / 2);
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline + amount, "Tug Fate scaling " + key + cl);
                        require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc && pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0,
                                "Tug Fate excludes AC and damage");
                        var luck = new PCTemplate();
                        luck.setName("Tug Fate competing luck");
                        String kind = target[0].equals("Attack") ? "COMBAT|TOHIT" : target[0].equals("Save") ? "SAVE|ALL"
                                : target[0].equals("Skill") ? "SKILL|ALL" : "COMBAT|INITIATIVE";
                        require(Globals.getContext().processToken(luck, "BONUS", kind + "|15|TYPE=Luck"), "Tug Fate luck fixture");
                        Globals.getContext().commit();
                        pc.addTemplate(luck);
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline + (positive ? Math.max(15, amount) : 15 + amount),
                                "Tug Fate typed bonus and untyped penalty");
                        pc.removeTemplate(luck);
                        facade.setTempBonusActive(effect(facade, key, true), false);
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Tug Fate outside trigger");
                        facade.removeTempBonus(effect(facade, key, true));
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Tug Fate removal");
                    }
                }
            }
            String[] painSkills = {"Spellcraft", "Survival", "Bluff", "Climb", "Acrobatics"};
            double[] skillBonuses = new double[painSkills.length];
            for (int i = 0; i < painSkills.length; i++) {
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, painSkills[i]);
                skillBonuses[i] = pcgen.core.analysis.SkillModifier.modifier(skill, pc).doubleValue();
            }
            facade.addTempBonus(effect(facade, "Fate Effect - Pain", false));
            pc.calcActiveBonuses();
            for (int i = 0; i < painSkills.length; i++) {
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, painSkills[i]);
                require(pcgen.core.analysis.SkillModifier.modifier(skill, pc).doubleValue() == skillBonuses[i] - (i < 3 ? 4 : 0),
                        "Pain actual skill scope " + painSkills[i]);
            }
            require(pc.getTotalBonusTo("STAT", "INT") == 0 && pc.getTotalBonusTo("SAVE", "Will") == 0,
                    "Pain preserves ability scores and saves");
            facade.removeTempBonus(effect(facade, "Fate Effect - Pain", true));
            pc.calcActiveBonuses();
            for (int i = 0; i < painSkills.length; i++) {
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, painSkills[i]);
                require(pcgen.core.analysis.SkillModifier.modifier(skill, pc).doubleValue() == skillBonuses[i], "Pain skill refund");
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"},
                    {"Save", "SAVE", "Will"}, {"Combat Maneuver", "COMBAT", "CMB"},
                    {"Skill", "SKILL", "ALL"}, {"Initiative", "COMBAT", "INITIATIVE"}}) {
                String key = "Fate Effect - The Hanged Man - Discharged - " + target[0];
                for (int damage : new int[] {1, 2, 3, 4, 7, 20}) {
                    choice.value = damage;
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    int bonus = Math.max(1, damage / 2);
                    require(pc.getTotalBonusTo(target[1], target[2]) == bonus, "Hanged Man damage " + damage + " " + target[0]);
                    require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("COMBAT", "CMD") == 0,
                            "Hanged Man excludes damage and CMD");
                    var stronger = new PCTemplate();
                    stronger.setName("Hanged Man insight stacking fixture");
                    String tokenCategory = target[1].equals("SAVE") ? "SAVE" : target[1];
                    require(Globals.getContext().processToken(stronger, "BONUS",
                            tokenCategory + "|" + target[2] + "|6|TYPE=Insight"), "Hanged Man stacking fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(stronger);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == Math.max(6, bonus), "Hanged Man highest insight");
                    pc.removeTemplate(stronger);
                    facade.removeTempBonus(effect(facade, key, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 0, "Hanged Man single roll removal");
                }
            }
            String[][] borrowedCategories = {{"Attack Rolls", "COMBAT", "TOHIT"},
                    {"Saving Throws", "SAVE", "Will"}, {"Skill Checks", "SKILL", "ALL"},
                    {"Ability Checks", "COMBAT", "INITIATIVE"}};
            for (String[] category : borrowedCategories) {
                String key = "Fate Effect - Borrow Trouble - " + category[0];
                facade.addTempBonus(effect(facade, key, false));
                pc.calcActiveBonuses();
                for (String[] checked : borrowedCategories) {
                    require(pc.getTotalBonusTo(checked[1], checked[2]) == (checked == category ? 4 : 0),
                            "Borrow Trouble category isolation " + category[0] + " / " + checked[0]);
                }
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("COMBAT", "AC") == baseAc,
                        "Borrow Trouble excludes damage and AC");
                require(pc.getTotalBonusTo("STAT", "DEX") == 0, "Borrow Trouble preserves ability scores");
                facade.setTempBonusActive(effect(facade, key, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo(category[1], category[2]) == 0, "Borrow Trouble ended toggle");
                facade.setTempBonusActive(effect(facade, key, true), true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo(category[1], category[2]) == 4, "Borrow Trouble reactivation");
                facade.removeTempBonus(effect(facade, key, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo(category[1], category[2]) == 0, "Borrow Trouble removal");
            }
            var walk = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
            var fly = pcgen.cdom.enumeration.MovementType.getConstant("Fly");
            double baseWalk = pc.getDisplay().movementOfType(walk);
            for (String maneuver : new String[] {"BullRush", "Overrun", "Trip"}) {
                String key = "Fate Effect - Perfect - STR - " + maneuver + " Already Safe";
                double base = pc.getVariableValue("CMB_" + maneuver, "").doubleValue();
                double defense = pc.getVariableValue("CMD_" + maneuver, "").doubleValue();
                for (int cl : new int[] {1, 3, 4, 8, 20}) {
                    choice.value = cl;
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    require(pc.getVariableValue("CMB_" + maneuver, "").doubleValue() == base + 2 + cl / 4, "Perfect maneuver " + maneuver);
                    require(pc.getVariableValue("CMD_" + maneuver, "").doubleValue() == defense, "Perfect excludes CMD");
                    require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Perfect excludes ordinary attack");
                    facade.removeTempBonus(effect(facade, key, true));
                    pc.calcActiveBonuses();
                    require(pc.getVariableValue("CMB_" + maneuver, "").doubleValue() == base, "Perfect maneuver refund");
                }
            }
            for (String stat : new String[] {"STR", "DEX", "CON", "INT", "WIS", "CHA"}) {
                String key = "Fate Effect - Perfect - " + stat;
                for (int cl : new int[] {1, 4, 5, 10, 20}) {
                    choice.value = cl;
                    facade.addTempBonus(effect(facade, key, false));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("SKILL", "STAT." + stat) == 1, "Perfect skill stat " + stat);
                    require(pc.getTotalBonusTo("STAT", stat) == 0, "Perfect preserves ability score");
                    int initiative = stat.equals("DEX") ? 1 : stat.equals("WIS") ? 1 + cl / 5 : 0;
                    require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == initiative, "Perfect initiative " + stat);
                    require(pc.getDisplay().movementOfType(walk) == baseWalk + (stat.equals("DEX") ? 10 + 5 * (cl / 5) : 0), "Perfect walking speed");
                    require(pc.getDisplay().movementOfType(fly) == 0, "Perfect cannot create flight");
                    if (stat.equals("INT")) {
                        String trained = "Fate Effect - Perfect - INT - Trained Check Only";
                        facade.addTempBonus(effect(facade, trained, false));
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo("SKILL", "ALL") == 2 + cl / 5, "Perfect trained bonus");
                        facade.setTempBonusActive(effect(facade, trained, true), false);
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Untrained checks excluded");
                        facade.removeTempBonus(effect(facade, trained, true));
                    }
                    facade.removeTempBonus(effect(facade, key, true));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("SKILL", "STAT." + stat) == 0, "Perfect removal");
                }
            }
            for (String mode : new String[] {"Climb", "Swim", "Fly", "Burrow"}) {
                var movement = pcgen.cdom.enumeration.MovementType.getConstant(mode);
                var original = new PCTemplate();
                original.setName("Perfect existing " + mode + " fixture");
                require(Globals.getContext().processToken(original, "MOVE", mode + ",20"), "Movement fixture");
                Globals.getContext().commit();
                pc.addTemplate(original);
                choice.value = 10;
                facade.addTempBonus(effect(facade, "Fate Effect - Perfect - DEX", false));
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(movement) == 40, "Perfect existing mode " + mode);
                facade.removeTempBonus(effect(facade, "Fate Effect - Perfect - DEX", true));
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(movement) == 20, "Perfect movement refund");
                pc.removeTemplate(original);
            }
            for (int cl : new int[] {1, 2, 3, 5, 6, 9, 20}) {
                choice.value = cl;
                facade.addTempBonus(effect(facade, villainy, false));
                pc.calcActiveBonuses();
                for (String stat : new String[] {"TOHIT", "DAMAGE"}) {
                    require(pc.getTotalBonusTo("COMBAT", stat) == 1 + cl / 3, "Villainy " + stat + " CL" + cl);
                }
                require(pc.getTotalBonusTo("SAVE", "Will") == 0 && pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Villainy stat isolation");
                facade.setTempBonusActive(effect(facade, villainy, true), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Other targets excluded by disabling");
                facade.removeTempBonus(effect(facade, villainy, true));
            }
            for (int mod : new int[] {-4, 0, 1, 3, 6}) {
                choice.value = mod;
                facade.addTempBonus(effect(facade, sun, false));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc + mod, "Sun signed AC modifier " + mod);
                for (String save : new String[] {"Fortitude", "Reflex", "Will"}) {
                    require(pc.getTotalBonusTo("SAVE", save) == mod, "Sun signed save " + save);
                }
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Sun excludes attacks");
                facade.removeTempBonus(effect(facade, sun, true));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == baseAc, "Sun removal");
            }
            choice.value = 3;
            facade.addTempBonus(effect(facade, sun, false));
            var stacking = new PCTemplate();
            stacking.setName("Fate insight stacking test");
            require(Globals.getContext().processToken(stacking, "BONUS", "SAVE|ALL|5|TYPE=Insight"), "Stacking save fixture");
            require(Globals.getContext().processToken(stacking, "BONUS", "COMBAT|AC|5|TYPE=Insight"), "Stacking AC fixture");
            Globals.getContext().commit();
            pc.addTemplate(stacking);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SAVE", "Will") == 5 && pc.getTotalBonusTo("COMBAT", "AC") == baseAc + 5, "Highest insight only");
            pc.removeTemplate(stacking);
            choice.cancel = true;
            facade.addTempBonus(effect(facade, villainy, false));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Cancelled application");
            choice.cancel = false;
            choice.value = 9;
            facade.addTempBonus(effect(facade, villainy, false));
            pc.calcActiveBonuses();
            choice.value = 10;
            facade.addTempBonus(effect(facade, "Fate Effect - Perfect - DEX", false));
            facade.addTempBonus(effect(facade, "Fate Effect - Perfect - INT - Trained Check Only", false));
            facade.setTempBonusActive(effect(facade, "Fate Effect - Perfect - INT - Trained Check Only", true), false);
            pc.calcActiveBonuses();
            require(choice.errors.isEmpty(), "Unexpected errors " + choice.errors);
            facade.addTempBonus(effect(facade, "Fate Effect - Borrow Trouble - Skill Checks", false));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SKILL", "ALL") == 4, "Borrow Trouble retained for save");
            facade.addTempBonus(effect(facade, "Fate Effect - Pain", false));
            choice.value = 7;
            facade.addTempBonus(effect(facade, "Fate Effect - The Hanged Man - Discharged - Combat Maneuver", false));
            pc.calcActiveBonuses();
            if (!reload) {
                var retainedController = new CharacterAbilities(pc, choice, facade.getDataSet(), new TodoManager());
                try {
                    retainedController.addAbility(magic, ability(magic, "Fate Sphere"));
                    for (String name : new String[] {"The Empress", "The Wheel", "Cups", "Pentacles", "Swords", "Wands"})
                        retainedController.addAbility(magic, ability(magic, "Fate - " + name));
                    retainedController.addAbility(magic, ability(magic, "Fate - Resounding Word"));
                    retainedController.addAbility(magic, ability(magic, "Fate - Resounding Word"));
                    require(pc.getVariableValue("SPHERES_FATE_RESOUNDINGWORD_COUNT", "").intValue() == 2, "Retain two range selections");
                    require(choice.errors.isEmpty(), "Retained talent selection errors " + choice.errors);
                } finally {
                    retainedController.closeCharacter();
                }
                choice.value = 3;
                facade.addTempBonus(effect(facade, malice, false));
                choice.value = 20;
                facade.addTempBonus(effect(facade, king, false));
                // Separate castings: one ongoing motif and a discharged skill roll.
                choice.value = 6;
                facade.addTempBonus(effect(facade, "Fate Effect - The Wheel - Ongoing - 1 - Attack and Damage", false));
                choice.value = 8;
                facade.addTempBonus(effect(facade, "Fate Effect - The Wheel - Discharged - Skill", false));
                choice.value = 2;
                facade.addTempBonus(effect(facade, "Fate Effect - The Emperor - Penalty Reduction - Initiative", false));
                facade.setTempBonusActive(effect(facade, "Fate Effect - The Emperor - Penalty Reduction - Initiative", true), false);
                choice.value = 7;
                facade.addTempBonus(effect(facade, "Fate Effect - The Emperor - Discharged Insight - Save", false));
                choice.value = 3;
                facade.addTempBonus(effect(facade, "Fate Effect - The Page - Discharged Morale - Skill", false));
                facade.setTempBonusActive(effect(facade, "Fate Effect - The Page - Discharged Morale - Skill", true), false);
                choice.value = 8;
                facade.addTempBonus(effect(facade, lovers, false));
                choice.value = 10;
                facade.addTempBonus(effect(facade, swordsConfirmation, false));
                facade.setTempBonusActive(effect(facade, swordsConfirmation, true), false);
                choice.value = 4;
                facade.addTempBonus(effect(facade, knight, false));
                facade.setTempBonusActive(effect(facade, knight, true), false);
                pc.calcActiveBonuses();
                facade.setFile(Path.of(args[5]).toFile());
                require(CharacterManager.saveCharacter(facade), "Save failed");
            }
        } finally {
            ChooserFactory.setDelegate(delegate);
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}