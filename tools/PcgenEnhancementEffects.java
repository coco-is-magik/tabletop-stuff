package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.PCTemplate;
import pcgen.facade.core.ChooserFacade;
import pcgen.facade.core.TempBonusFacade;
import pcgen.system.CharacterManager;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Received effects use the production temporary-bonus controller, not talent grants. */
class PcgenEnhancementEffects {
    private static class CasterLevelChoice extends Messages {
        int level = 1;
        boolean cancel;
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            if (cancel) return false;
            for (var item : chooser.getAvailableList()) {
                if (item.toString().equals(Integer.toString(level))) {
                    chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing caster level " + level);
        }
    }

    private static TempBonusFacade available(CharacterFacadeImpl facade, String key) {
        for (var effect : facade.getAvailableTempBonuses()) {
            if (effect.getKeyName().equals(key)) return effect;
        }
        throw new IllegalStateException("Missing temporary effect " + key);
    }

    private static TempBonusFacade applied(CharacterFacadeImpl facade, String key) {
        for (var effect : facade.getTempBonuses()) {
            if (effect.getKeyName().equals(key)) return effect;
        }
        throw new IllegalStateException("Effect was not applied: " + key);
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = (CharacterFacadeImpl) CharacterManager.getCharacters().iterator().next();
        var choice = new CasterLevelChoice();
        var oldDelegate = ChooserFactory.getDelegate();
        ChooserFactory.setDelegate(choice);
        String strength = "Enhancement Effect - Physical Enhancement - STR";
        String intelligence = "Enhancement Effect - Mental Enhancement - INT";
        boolean reload = args[4].equals("enhancement-reload");
        try {
            if (reload) {
                double arcanaAttack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                facade.removeTempBonus(applied(facade, "Fate Effect - Swords"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == arcanaAttack - 3, "Persisted Swords CL20 removal");
                double arcanaFortitude = pc.getTotalBonusTo("SAVE", "Fortitude");
                double arcanaWill = pc.getTotalBonusTo("SAVE", "Will");
                facade.removeTempBonus(applied(facade, "Fate Effect - Pentacles - Fortitude"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Fortitude") == arcanaFortitude - 2, "Persisted Pentacles CL10 removal");
                require(pc.getTotalBonusTo("SAVE", "Will") == arcanaWill, "Persisted Pentacles save isolation");
                double foolWill = pc.getTotalBonusTo("SAVE", "Will");
                facade.removeTempBonus(applied(facade, "Fate Effect - The Fool"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == foolWill + 2, "Persisted Fool CL10 removal");
                var cupsSkill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Spellcraft");
                int cupsBefore = pcgen.core.analysis.SkillModifier.modifier(cupsSkill, pc).intValue();
                facade.removeTempBonus(applied(facade, "Fate Effect - Cups"));
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(cupsSkill, pc).intValue() == cupsBefore - 4, "Persisted Cups CL20 removal");
                double wandsBefore = pc.getTotalBonusTo("COMBAT", "INITIATIVE");
                facade.removeTempBonus(applied(facade, "Fate Effect - Wands"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == wandsBefore - 3, "Persisted Wands CL10 removal");
                var hermitSaved = applied(facade, "Fate Effect - The Hermit - Self Aid - Attack");
                double attackBeforeHermit = pc.getTotalBonusTo("COMBAT", "TOHIT");
                facade.setTempBonusActive(hermitSaved, true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attackBeforeHermit + 5, "Persisted inactive Hermit CL10 reactivation");
                facade.removeTempBonus(hermitSaved);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attackBeforeHermit, "Persisted Hermit independent removal");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 3, "Persisted Empress three-point weapon roll");
                facade.removeTempBonus(applied(facade, "Fate Effect - The Empress - Spend - Weapon Damage"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0, "Persisted Empress removal");
                var persistedSkill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Spellcraft");
                int persistedModifier = pcgen.core.analysis.SkillModifier.modifier(persistedSkill, pc).intValue();
                facade.removeTempBonus(applied(facade, "Fate Effect - The World - Conditional Skills"));
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(persistedSkill, pc).intValue() == persistedModifier - 6, "Persisted World CL20 skill bonus removal");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == -7, "Inactive persisted Magician does not modify attacks");
                var persistedMagician = applied(facade, "Fate Effect - The Magician - Attacks of Opportunity");
                facade.setTempBonusActive(persistedMagician, true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == -3, "Persisted Magician CL10 reactivation");
                facade.removeTempBonus(persistedMagician);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == -7, "Persisted Magician removal preserves other penalties");
                var savedClimb = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Climb");
                var savedBluff = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Bluff");
                double savedCmb = pc.getTotalBonusTo("COMBAT", "CMB");
                int savedClimbBonus = pcgen.core.analysis.SkillModifier.modifier(savedClimb, pc).intValue();
                facade.removeTempBonus(applied(facade, "Fate Effect - Strength"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "CMB") == savedCmb - 4, "Persisted CL8 Strength maneuver removal");
                require(pcgen.core.analysis.SkillModifier.modifier(savedClimb, pc).intValue() == savedClimbBonus - 4, "Persisted CL8 Strength skill removal");
                int savedBluffBonus = pcgen.core.analysis.SkillModifier.modifier(savedBluff, pc).intValue();
                facade.removeTempBonus(applied(facade, "Fate Effect - Pain - Mental Skills"));
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(savedBluff, pc).intValue() == savedBluffBonus + 4, "Persisted Pain removal preserves other modifiers");
                double savedWill = pc.getTotalBonusTo("SAVE", "Will");
                double savedFortitude = pc.getTotalBonusTo("SAVE", "Fortitude");
                double savedReflex = pc.getTotalBonusTo("SAVE", "Reflex");
                facade.removeTempBonus(applied(facade, "Fate Effect - The Hanged Man - Penalize Will"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == savedWill + 2, "Persisted Hanged Man penalty removal");
                require(pc.getTotalBonusTo("SAVE", "Fortitude") == savedFortitude - 4 && pc.getTotalBonusTo("SAVE", "Reflex") == savedReflex - 4, "Persisted CL20 Hanged Man insight removal");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == -7, "Saved Borrow Luck attack penalty with Serendipity and Cripple");
                facade.removeTempBonus(applied(facade, "Fate Effect - Borrow Luck - Attack Rolls"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == -3, "Saved Serendipity stacks with Cripple");
                facade.removeTempBonus(applied(facade, "Fate Effect - Serendipity"));
                pc.calcActiveBonuses();
                var savedWalk = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
                double boostedWalk = pc.getDisplay().movementOfType(savedWalk);
                facade.removeTempBonus(applied(facade, "Enhancement Effect - Alter Movement - Walk"));
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(savedWalk) == boostedWalk - 30, "Saved CL10 movement removal");
                require(pc.getVariableValue("FireResistanceBonus", "").intValue() == 22, "Saved energy resistance CL12");
                facade.removeTempBonus(applied(facade, "Protection Effect - Energy Resistance - Fire"));
                pc.calcActiveBonuses();
                require(pc.getVariableValue("FireResistanceBonus", "").intValue() == 0, "Saved energy resistance removal");
                require(pc.getTotalBonusTo("SKILL", "ALL") == -4, "Saved Cripple CL10 penalty");
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == -1, "Saved Cripple combines with Superior Reflexes");
                facade.removeTempBonus(applied(facade, "Enhancement Effect - Cripple"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Saved Cripple removal");
                require(pc.getTotalBonusTo("STAT", "STR") == 6, "Saved external CL14 Strength effect");
                require(pc.getTotalBonusTo("STAT", "INT") == 4, "Saved external CL7 Intelligence effect");
                facade.removeTempBonus(applied(facade, strength));
                facade.removeTempBonus(applied(facade, intelligence));
                require(pc.getTotalBonusTo("SAVE", "Will") == 8, "Saved Staunch Resistance and Resistance aegis");
                require(pc.getTotalBonusTo("SKILL", "Perception") == 8, "Saved Enhance Focus CL12");
                facade.removeTempBonus(applied(facade, "Enhancement Effect - Staunch Resistance - Will"));
                facade.removeTempBonus(applied(facade, "Enhancement Effect - Enhance Focus - Perception"));
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 3, "Saved Superior Reflexes CL9");
                require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_SUPERIOR_REFLEXES_AOO") == 3, "Saved additional attacks");
                facade.removeTempBonus(applied(facade, "Enhancement Effect - Superior Reflexes"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == 18, "Saved complementary aegis armor types");
                require(pc.getTotalBonusTo("SAVE", "Will") == 4, "Saved Ultimate Resistance CL12");
                for (String aegis : new String[] {"Deflection", "Armored Magic - Armor", "Armored Magic - Shield", "Resistance"}) {
                    facade.removeTempBonus(applied(facade, "Protection Effect - " + aegis));
                }
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "Acrobatics") == 4, "Saved Slippery CL10");
                double savedCmd = pc.getTotalBonusTo("COMBAT", "CMD");
                facade.removeTempBonus(applied(facade, "Protection Effect - Slippery"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "Acrobatics") == 0, "Saved Slippery skill removal");
                require(pc.getTotalBonusTo("COMBAT", "CMD") == savedCmd - 4, "Saved Slippery CMD removal");
            }
            require(pc.getTotalLevels() == 2, "Recipient level differs from supplied caster level");
            String[][] fateRolls = {{"Attack Rolls", "COMBAT", "TOHIT"},
                {"Saving Throws", "SAVE", "Will"}, {"Skill Checks", "SKILL", "ALL"},
                {"Ability Checks", "COMBAT", "INITIATIVE"}};
            for (int target = 0; target < fateRolls.length; target++) {
                double[] baseline = new double[fateRolls.length];
                for (int i = 0; i < fateRolls.length; i++) baseline[i] = pc.getTotalBonusTo(fateRolls[i][1], fateRolls[i][2]);
                String key = "Fate Effect - Borrow Luck - " + fateRolls[target][0];
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                for (int i = 0; i < fateRolls.length; i++) {
                    require(pc.getTotalBonusTo(fateRolls[i][1], fateRolls[i][2]) == baseline[i] - (i == target ? 4 : 0), "Borrow Luck isolates " + fateRolls[target][0]);
                }
                require(pc.getTotalBonusTo("STAT", "STR") == 0, "Borrow Luck does not reduce ability scores");
                facade.setTempBonusActive(applied(facade, key), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo(fateRolls[target][1], fateRolls[target][2]) == baseline[target], "Borrow Luck ending toggle");
                facade.removeTempBonus(applied(facade, key));
            }
            for (int penalty : new int[] {1, 3, 5}) {
                String key = "Fate Effect - Greater Serendipity - Enemy";
                choice.level = penalty;
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                for (String[] roll : fateRolls) require(pc.getTotalBonusTo(roll[1], roll[2]) == -penalty, "Enemy Serendipity matches allied bonus");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0, "Enemy Serendipity does not penalize damage");
                facade.removeTempBonus(applied(facade, key));
                pc.calcActiveBonuses();
                for (String[] roll : fateRolls) require(pc.getTotalBonusTo(roll[1], roll[2]) == 0, "Enemy leaves consecration");
            }
            String peace = "Protection Effect - Inner Peace - Situational Skills";
            String priestess = "Fate Effect - The High Priestess - Discharged";
            double priestessBaseAc = pc.getTotalBonusTo("COMBAT", "AC");
            for (int cl : new int[] {5, 6, 9, 10, 19, 20}) {
                choice.level = cl;
                facade.addTempBonus(available(facade, priestess));
                pc.calcActiveBonuses();
                for (String save : new String[] {"Fortitude", "Reflex", "Will"}) {
                    require(pc.getTotalBonusTo("SAVE", save) == cl / 2, "Priestess discharge half CL " + save);
                }
                require(pc.getTotalBonusTo("COMBAT", "AC") == priestessBaseAc && pc.getTotalBonusTo("SKILL", "ALL") == 0, "Priestess discharge only saves");
                var stacking = new PCTemplate();
                stacking.setName("Priestess insight stacking fixture");
                require(Globals.getContext().processToken(stacking, "BONUS", "SAVE|ALL|5|TYPE=Insight"), "Priestess stacking fixture");
                Globals.getContext().commit();
                pc.addTemplate(stacking);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == Math.max(5, cl / 2), "Priestess highest insight");
                pc.removeTemplate(stacking);
                facade.setTempBonusActive(applied(facade, priestess), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Priestess expiration toggle");
                facade.removeTempBonus(applied(facade, priestess));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Priestess removal");
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"},
                    {"Defense", "COMBAT", "AC"}, {"Skill", "SKILL", "ALL"}}) {
                String key = "Fate Effect - The Hermit - Self Aid - " + target[0];
                double baseline = pc.getTotalBonusTo(target[1], target[2]);
                for (int cl : new int[] {1, 4, 5, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline + 3 + cl / 5, "Hermit self aid " + target[0] + " CL" + cl);
                    require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("SAVE", "Will") == 0, "Hermit excludes damage and saves");
                    facade.setTempBonusActive(applied(facade, key), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Hermit inactive outside aid context");
                    facade.setTempBonusActive(applied(facade, key), true);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline + 3 + cl / 5, "Hermit reactivation");
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Hermit removal");
                }
            }
            for (String[] target : new String[][] {{"Attack", "COMBAT", "TOHIT"},
                    {"Weapon Damage", "COMBAT", "DAMAGE"}, {"Save", "SAVE", "Will"},
                    {"Skill", "SKILL", "ALL"}, {"Initiative", "COMBAT", "INITIATIVE"}}) {
                for (boolean discharge : new boolean[] {false, true}) {
                    if (discharge && target[0].equals("Weapon Damage")) continue;
                    String key = "Fate Effect - The Empress - " + (discharge ? "Discharge" : "Spend") + " - " + target[0];
                    double baseline = pc.getTotalBonusTo(target[1], target[2]);
                    for (int points : discharge ? new int[] {0, 1, 3, 4, 7, 8, 21} : new int[] {1, 2, 4}) {
                        choice.level = points;
                        facade.addTempBonus(available(facade, key));
                        pc.calcActiveBonuses();
                        int bonus = discharge ? 5 + points / 4 : points;
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline + bonus, "Empress point formula " + key + " " + points);
                        require(pc.getTotalBonusTo("STAT", "STR") == 0, "Empress does not change ability scores");
                        var empressStacking = new PCTemplate();
                        empressStacking.setName("Empress insight stacking fixture");
                        String bonusStat = target[0].equals("Save") ? "ALL" : target[2];
                        require(Globals.getContext().processToken(empressStacking, "BONUS", target[1] + "|" + bonusStat + "|6|TYPE=Insight"), "Empress stacking fixture");
                        Globals.getContext().commit();
                        pc.addTemplate(empressStacking);
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline + Math.max(6, bonus), "Empress does not stack insight bonuses");
                        pc.removeTemplate(empressStacking);
                        facade.setTempBonusActive(applied(facade, key), false);
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Empress disabled after roll");
                        facade.removeTempBonus(applied(facade, key));
                        pc.calcActiveBonuses();
                        require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Empress removal");
                    }
                }
            }
            for (String[] target : new String[][] {{"Swords", "COMBAT", "TOHIT", "1"},
                    {"Wands", "COMBAT", "INITIATIVE", "2"},
                    {"Pentacles - Fortitude", "SAVE", "Fortitude", "1"},
                    {"Pentacles - Reflex", "SAVE", "Reflex", "1"},
                    {"Pentacles - Will", "SAVE", "Will", "1"}}) {
                String key = "Fate Effect - " + target[0];
                double baseline = pc.getTotalBonusTo(target[1], target[2]);
                for (int cl : new int[] {1, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline + Integer.parseInt(target[3]) + cl / 10, "Arcana scaling " + target[0]);
                    require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0, "Arcana does not grant damage");
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == baseline, "Arcana removal " + target[0]);
                }
            }
            for (int cl : new int[] {1, 9, 10, 19, 20}) {
                String[] skillNames = {"Spellcraft", "Sense Motive", "Bluff", "Climb", "Acrobatics"};
                int[] before = new int[skillNames.length];
                for (int i = 0; i < skillNames.length; i++) {
                    var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, skillNames[i]);
                    before[i] = pcgen.core.analysis.SkillModifier.modifier(skill, pc).intValue();
                }
                choice.level = cl;
                facade.addTempBonus(available(facade, "Fate Effect - Cups"));
                pc.calcActiveBonuses();
                for (int i = 0; i < skillNames.length; i++) {
                    var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, skillNames[i]);
                    require(pcgen.core.analysis.SkillModifier.modifier(skill, pc).intValue() == before[i] + (i < 3 ? 2 + cl / 10 : 0), "Cups mental-skill scope " + skillNames[i]);
                }
                facade.removeTempBonus(applied(facade, "Fate Effect - Cups"));
                pc.calcActiveBonuses();
                for (int i = 0; i < skillNames.length; i++) {
                    var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, skillNames[i]);
                    require(pcgen.core.analysis.SkillModifier.modifier(skill, pc).intValue() == before[i], "Cups removal " + skillNames[i]);
                }
            }
            for (int cl : new int[] {1, 9, 10, 19, 20, 29, 30, 40}) {
                choice.level = cl;
                facade.addTempBonus(available(facade, "Fate Effect - The Fool"));
                pc.calcActiveBonuses();
                for (String save : new String[] {"Fortitude", "Reflex", "Will"}) {
                    require(pc.getTotalBonusTo("SAVE", save) == -Math.max(0, 3 - cl / 10), "Fool save penalty " + save + " CL" + cl);
                }
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0 && pc.getTotalBonusTo("STAT", "DEX") == 0, "Fool affects saves only");
                facade.removeTempBonus(applied(facade, "Fate Effect - The Fool"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Fool free-action ending");
            }
            String world = "Fate Effect - The World - Conditional Skills";
            for (String[] target : new String[][] {{"Attacks of Opportunity", "COMBAT", "TOHIT"}, {"Untrained Skills", "SKILL", "ALL"}}) {
                String key = "Fate Effect - The Magician - " + target[0];
                for (int cl : new int[] {1, 4, 5, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 2 + cl / 5, "Magician scaling " + target[0]);
                    require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == 0 && pc.getTotalBonusTo("SAVE", "Will") == 0, "Magician excludes damage and saves");
                    require(pc.getTotalBonusTo(target[1].equals("COMBAT") ? "SKILL" : "COMBAT", target[1].equals("COMBAT") ? "ALL" : "TOHIT") == 0, "Magician roll-category isolation");
                    var stacking = new PCTemplate();
                    stacking.setName("Magician insight stacking fixture");
                    require(Globals.getContext().processToken(stacking, "BONUS", target[1] + "|" + target[2] + "|5|TYPE=Insight"), "Magician stacking fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(stacking);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == Math.max(5, 2 + cl / 5), "Magician highest insight");
                    pc.removeTemplate(stacking);
                    facade.setTempBonusActive(applied(facade, key), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 0, "Magician disabled outside context");
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(target[1], target[2]) == 0, "Magician removal");
                }
            }
            var worldSkill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Spellcraft");
            int worldBaseline = pcgen.core.analysis.SkillModifier.modifier(worldSkill, pc).intValue();
            for (int cl : new int[] {1, 4, 5, 9, 10, 19, 20}) {
                choice.level = cl;
                facade.addTempBonus(available(facade, world));
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(worldSkill, pc).intValue() == worldBaseline + 2 + cl / 5, "World take-check skill bonus");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0 && pc.getTotalBonusTo("SAVE", "Will") == 0, "World affects skills only");
                var stacking = new PCTemplate();
                stacking.setName("World insight stacking fixture");
                require(Globals.getContext().processToken(stacking, "BONUS", "SKILL|ALL|5|TYPE=Insight"), "World stacking fixture");
                Globals.getContext().commit();
                pc.addTemplate(stacking);
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(worldSkill, pc).intValue() == worldBaseline + Math.max(5, 2 + cl / 5), "World highest insight only");
                pc.removeTemplate(stacking);
                facade.setTempBonusActive(applied(facade, world), false);
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(worldSkill, pc).intValue() == worldBaseline, "World disabled for rolled checks");
                facade.removeTempBonus(applied(facade, world));
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(worldSkill, pc).intValue() == worldBaseline, "World removed");
            }
            for (String motif : new String[] {"Justice", "The Devil - Discharged"}) {
                boolean justice = motif.equals("Justice");
                String key = "Fate Effect - " + motif + " - Conditional";
                String second = justice ? "DAMAGE" : "AC";
                double baseSecond = pc.getTotalBonusTo("COMBAT", second);
                for (int cl : new int[] {1, 3, 4, 5, 9, 10, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    int bonus = 2 + cl / (justice ? 5 : 4);
                    require(pc.getTotalBonusTo("COMBAT", "TOHIT") == bonus, "Conditional motif attack " + motif);
                    require(pc.getTotalBonusTo("COMBAT", second) == baseSecond + bonus, "Conditional motif secondary benefit " + motif);
                    facade.setTempBonusActive(applied(facade, key), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", "TOHIT") == 0 && pc.getTotalBonusTo("COMBAT", second) == baseSecond, "Conditional motif against another target");
                    facade.removeTempBonus(applied(facade, key));
                }
            }
            String[] painSkills = {"Spellcraft", "Sense Motive", "Bluff", "Climb", "Acrobatics"};
            int[] painBaseline = new int[painSkills.length];
            for (int i = 0; i < painSkills.length; i++) {
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, painSkills[i]);
                painBaseline[i] = pcgen.core.analysis.SkillModifier.modifier(skill, pc).intValue();
            }
            facade.addTempBonus(available(facade, "Fate Effect - Pain - Mental Skills"));
            pc.calcActiveBonuses();
            for (int i = 0; i < painSkills.length; i++) {
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, painSkills[i]);
                require(pcgen.core.analysis.SkillModifier.modifier(skill, pc).intValue() == painBaseline[i] - (i < 3 ? 4 : 0), "Pain mental versus physical skill " + painSkills[i]);
            }
            require(pc.getTotalBonusTo("STAT", "INT") == 0 && pc.getTotalBonusTo("SAVE", "Will") == 0, "Pain does not alter score or save");
            facade.removeTempBonus(applied(facade, "Fate Effect - Pain - Mental Skills"));
            pc.calcActiveBonuses();
            for (int i = 0; i < painSkills.length; i++) {
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, painSkills[i]);
                require(pcgen.core.analysis.SkillModifier.modifier(skill, pc).intValue() == painBaseline[i], "Pain removal " + painSkills[i]);
            }
            String[] savingThrows = {"Fortitude", "Reflex", "Will"};
            for (String penalized : savingThrows) {
                String key = "Fate Effect - The Hanged Man - Penalize " + penalized;
                for (int cl : new int[] {1, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    for (String save : savingThrows) require(pc.getTotalBonusTo("SAVE", save) == (save.equals(penalized) ? -2 : 2 + cl / 10), "Hanged Man bonus and penalty " + save);
                    facade.setTempBonusActive(applied(facade, key), false);
                    pc.calcActiveBonuses();
                    for (String save : savingThrows) require(pc.getTotalBonusTo("SAVE", save) == 0, "Hanged Man choose neither");
                    facade.removeTempBonus(applied(facade, key));
                }
            }
            double baseCmb = pc.getTotalBonusTo("COMBAT", "CMB");
            double baseCmd = pc.getTotalBonusTo("COMBAT", "CMD");
            var climb = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Climb");
            var swim = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Swim");
            int baseClimb = pcgen.core.analysis.SkillModifier.modifier(climb, pc).intValue();
            int baseSwim = pcgen.core.analysis.SkillModifier.modifier(swim, pc).intValue();
            for (int cl : new int[] {1, 3, 4, 7, 8, 20}) {
                choice.level = cl;
                facade.addTempBonus(available(facade, "Fate Effect - Strength"));
                pc.calcActiveBonuses();
                int bonus = 2 + cl / 4;
                require(pc.getTotalBonusTo("COMBAT", "CMB") == baseCmb + bonus && pc.getTotalBonusTo("COMBAT", "CMD") == baseCmd + bonus, "Strength motif maneuvers");
                require(pcgen.core.analysis.SkillModifier.modifier(climb, pc).intValue() == baseClimb + bonus, "Strength motif Climb");
                require(pcgen.core.analysis.SkillModifier.modifier(swim, pc).intValue() == baseSwim + bonus, "Strength motif Swim");
                require(pc.getTotalBonusTo("STAT", "STR") == 0 && pc.getTotalBonusTo("COMBAT", "TOHIT") == 0, "Strength motif does not change score or ordinary attack");
                facade.removeTempBonus(applied(facade, "Fate Effect - Strength"));
                pc.calcActiveBonuses();
                require(pcgen.core.analysis.SkillModifier.modifier(climb, pc).intValue() == baseClimb && pc.getTotalBonusTo("COMBAT", "CMD") == baseCmd, "Strength motif removal");
            }
            for (String motif : new String[] {"The Star", "The Chariot", "The Moon", "The Hierophant"}) {
                boolean star = motif.equals("The Star");
                String key = "Fate Effect - " + motif + " - Conditional";
                String type = star ? "COMBAT" : "SAVE";
                String target = star ? "AC" : "Will";
                double base = pc.getTotalBonusTo(type, target);
                var insight = new PCTemplate();
                insight.setName("Existing insight for " + motif);
                require(Globals.getContext().processToken(insight, "BONUS", type + "|" + target + "|3|TYPE=Insight"), "Insight stacking fixture");
                Globals.getContext().commit();
                pc.addTemplate(insight);
                for (int cl : new int[] {1, 4, 5, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(type, target) == base + Math.max(3, 2 + cl / (star || motif.equals("The Hierophant") ? 5 : 10)), "Motif scaling and insight stacking " + motif);
                    facade.setTempBonusActive(applied(facade, key), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(type, target) == base + 3, "Motif outside qualifying context " + motif);
                    facade.removeTempBonus(applied(facade, key));
                }
                pc.removeTemplate(insight);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo(type, target) == base, "Motif cleanup " + motif);
            }
            facade.addTempBonus(available(facade, peace));
            pc.calcActiveBonuses();
            for (String situation : new String[] {"Bluff=Conceal Emotions", "Bluff=Relay Secret Messages", "Diplomacy=Calm Creatures"}) {
                require(pc.getTotalBonusTo("SITUATION", situation) == 4, "Inner Peace situation " + situation);
            }
            require(pc.getTotalBonusTo("SKILL", "Bluff") == 0 && pc.getTotalBonusTo("SKILL", "Diplomacy") == 0, "Inner Peace no general skill bonus");
            facade.removeTempBonus(applied(facade, peace));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SITUATION", "Bluff=Conceal Emotions") == 0, "Inner Peace situational removal");
            var morale = new PCTemplate();
            morale.setName("Existing morale save fixture");
            require(Globals.getContext().processToken(morale, "BONUS", "SAVE|ALL|2|TYPE=Morale"), "Morale fixture");
            Globals.getContext().commit();
            pc.addTemplate(morale);
            for (String aegis : new String[] {"Breathless", "Inner Peace", "Deathless", "Fateless", "Resist Transformation"}) {
                String key = "Protection Effect - " + aegis + " - Conditional Saves";
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                for (String save : new String[] {"Fortitude", "Reflex", "Will"}) {
                    require(pc.getTotalBonusTo("SAVE", save) == 4, "Conditional morale does not stack: " + aegis);
                }
                var effect = applied(facade, key);
                facade.setTempBonusActive(effect, false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 2, "Disabled aegis does not affect ordinary saves");
                facade.setTempBonusActive(effect, true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 4, "Context reactivation");
                facade.removeTempBonus(effect);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 2, "Other morale survives removal");
            }
            for (String aegis : new String[] {"Destructionless", "Eyeless", "Stabilize", "Iron Shield"}) {
                String key = "Protection Effect - " + aegis + " - Conditional Defense";
                double ac = pc.getTotalBonusTo("COMBAT", "AC");
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac + 4, "Conditional aegis AC");
                require(pc.getTotalBonusTo("SAVE", "Will") == (aegis.equals("Iron Shield") ? 6 : 4), "Conditional defense bonus type");
                var effect = applied(facade, key);
                facade.setTempBonusActive(effect, false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac && pc.getTotalBonusTo("SAVE", "Will") == 2, "Disabled conditional defense");
                facade.removeTempBonus(effect);
                pc.calcActiveBonuses();
            }
            pc.removeTemplate(morale);
            pc.calcActiveBonuses();
            for (String stat : new String[] {"STR", "DEX", "CON", "INT", "WIS", "CHA"}) {
                String key = "Enhancement Effect - " +
                        ((stat.equals("STR") || stat.equals("DEX") || stat.equals("CON"))
                                ? "Physical Enhancement" : "Mental Enhancement") + " - " + stat;
                var source = Globals.getContext().getReferenceContext()
                        .silentlyGetConstructedCDOMObject(PCTemplate.class, key);
                require(source != null, "Loaded effect template");
                double base = pc.getTotalBonusTo("STAT", stat);
                for (int cl : new int[] {1, 6, 7, 13, 14, 20, 21, 100}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    int bonus = 2 + 2 * (cl / 7);
                    require(pc.getTotalBonusTo("STAT", stat) == base + bonus, "Temporary ability bonus " + stat + " CL" + cl + " actual=" + pc.getTotalBonusTo("STAT", stat) + " base=" + base + " enabled=" + pc.getUseTempMods() + " effects=" + pc.getTempBonusMap());
                    var effect = applied(facade, key);
                    facade.setTempBonusActive(effect, false);
                    require(pc.getTotalBonusTo("STAT", stat) == base, "Inactive effect does not apply");
                    facade.setTempBonusActive(effect, true);
                    require(pc.getTotalBonusTo("STAT", stat) == base + bonus, "Effect reactivation");
                    facade.removeTempBonus(effect);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("STAT", stat) == base, "Effect removal restores original ability bonus");
                }
            }
            choice.cancel = true;
            facade.addTempBonus(available(facade, strength));
            require(facade.getTempBonuses().getSize() == 0, "Cancelled caster level creates no effect");
            choice.cancel = false;
            String serendipity = "Fate Effect - Serendipity";
            double originalAttack = pc.getTotalBonusTo("COMBAT", "TOHIT");
            double originalAc = pc.getTotalBonusTo("COMBAT", "AC");
            facade.addTempBonus(available(facade, serendipity));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == originalAttack + 1, "Serendipity attack luck");
            require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 1, "Serendipity initiative luck");
            require(pc.getTotalBonusTo("SKILL", "ALL") == 1 && pc.getTotalBonusTo("SAVE", "Will") == 1, "Serendipity skill and save luck");
            require(pc.getTotalBonusTo("COMBAT", "AC") == originalAc, "Serendipity does not grant AC");
            var luck = new PCTemplate();
            luck.setName("Existing luck fixture");
            require(Globals.getContext().processToken(luck, "BONUS", "COMBAT|TOHIT|3|TYPE=Luck"), "Luck fixture");
            Globals.getContext().commit();
            pc.addTemplate(luck);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == originalAttack + 3, "Serendipity takes highest luck bonus");
            pc.removeTemplate(luck);
            facade.removeTempBonus(applied(facade, serendipity));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == originalAttack, "Serendipity removal");
            for (String kind : new String[] {"Sacred", "Profane"}) {
                String key = "Fate Effect - Hallow - " + kind + " - Opposed Alignment Only";
                for (int cl : new int[] {1, 9, 10, 19, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    int bonus = 1 + cl / 10;
                    require(pc.getTotalBonusTo("COMBAT", "TOHIT") == originalAttack + bonus, "Hallow attack progression");
                    require(pc.getTotalBonusTo("COMBAT", "AC") == originalAc + bonus, "Hallow AC progression");
                    require(pc.getTotalBonusTo("SAVE", "Will") == bonus, "Hallow save progression");
                    facade.setTempBonusActive(applied(facade, key), false);
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", "AC") == originalAc && pc.getTotalBonusTo("SAVE", "Will") == 0, "Hallow disabled outside opposed alignment context");
                    facade.removeTempBonus(applied(facade, key));
                }
            }
            var walk = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
            var fly = pcgen.cdom.enumeration.MovementType.getConstant("Fly");
            double baseWalk = pc.getDisplay().movementOfType(walk);
            String levitating = "Enhancement Effect - Lighten - Levitating Attack";
            double baseAttack = pc.getTotalBonusTo("COMBAT", "TOHIT");
            double baseDamage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
            for (int penalty : new int[] {1, 2, 3, 4, 5, 1}) {
                choice.level = penalty;
                facade.addTempBonus(available(facade, levitating));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == baseAttack - penalty, "Levitating attack sequence and stabilization");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == baseDamage, "Levitating does not change damage");
                facade.setTempBonusActive(applied(facade, levitating), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == baseAttack, "Levitating disabled for nonweapon attacks");
                facade.removeTempBonus(applied(facade, levitating));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == baseAttack, "Levitating penalty removal");
            }
            for (String weight : new String[] {"Half Weight", "Weightless or Floating"}) {
                String key = "Enhancement Effect - Lighten - " + weight + " - Conditional CMD";
                double cmd = pc.getTotalBonusTo("COMBAT", "CMD");
                double ac = pc.getTotalBonusTo("COMBAT", "AC");
                double cmb = pc.getTotalBonusTo("COMBAT", "CMB");
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "CMD") == cmd - (weight.equals("Half Weight") ? 2 : 4), "Lighten selected weight penalty");
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac && pc.getTotalBonusTo("COMBAT", "CMB") == cmb, "Lighten does not change AC or CMB");
                facade.setTempBonusActive(applied(facade, key), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "CMD") == cmd, "Lighten disabled for other maneuvers");
                facade.removeTempBonus(applied(facade, key));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "CMD") == cmd, "Lighten penalty removal");
            }
            for (int cl : new int[] {1, 4, 5, 9, 10, 20}) {
                choice.level = cl;
                String key = "Enhancement Effect - Alter Movement - Walk";
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(walk) == baseWalk + 10 + 10 * (cl / 5), "Alter Movement walking speed");
                require(pc.getTotalBonusTo("SKILL", "Acrobatics") == 0, "Movement does not grant unconditional skill bonus");
                facade.removeTempBonus(applied(facade, key));
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(walk) == baseWalk, "Movement speed refund");
            }
            choice.level = 10;
            facade.addTempBonus(available(facade, "Enhancement Effect - Alter Movement - Fly"));
            pc.calcActiveBonuses();
            require(pc.getDisplay().movementOfType(fly) == 0, "Alter Movement cannot create flight");
            facade.removeTempBonus(applied(facade, "Enhancement Effect - Alter Movement - Fly"));
            for (String mode : new String[] {"Climb", "Swim", "Fly", "Burrow"}) {
                var movement = pcgen.cdom.enumeration.MovementType.getConstant(mode);
                var original = new PCTemplate();
                original.setName("Existing " + mode + " speed fixture");
                require(Globals.getContext().processToken(original, "MOVE", mode + ",20"), "Existing movement fixture");
                require(Globals.getContext().processToken(original, "BONUS", "MOVEADD|TYPE." + mode + "|20|TYPE=Enhancement"), "Existing movement enhancement fixture");
                Globals.getContext().commit();
                pc.addTemplate(original);
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(movement) == 40, "Existing enhanced speed");
                String key = "Enhancement Effect - Alter Movement - " + mode;
                for (int cl : new int[] {1, 10}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getDisplay().movementOfType(movement) == 20 + Math.max(20, 10 + 10 * (cl / 5)), "Movement enhancement takes highest source " + mode);
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getDisplay().movementOfType(movement) == 40, "Movement preserves existing enhancement " + mode);
                }
                pc.removeTemplate(original);
                pc.calcActiveBonuses();
                require(pc.getDisplay().movementOfType(movement) == 0, "Movement fixture removal " + mode);
            }
            choice.level = 10;
            String movementSkills = "Enhancement Effect - Alter Movement - Conditional Skills";
            facade.addTempBonus(available(facade, movementSkills));
            pc.calcActiveBonuses();
            for (String skill : new String[] {"Acrobatics", "Climb", "Fly", "Swim"}) require(pc.getTotalBonusTo("SKILL", skill) == 6, "Conditional movement skill bonus");
            facade.setTempBonusActive(applied(facade, movementSkills), false);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SKILL", "Acrobatics") == 0, "Movement skill disabled outside context");
            facade.removeTempBonus(applied(facade, movementSkills));
            for (String energy : new String[] {"Acid", "Cold", "Electricity", "Fire", "Sonic"}) {
                String key = "Protection Effect - Energy Resistance - " + energy;
                String variable = energy + "ResistanceBonus";
                for (int cl : new int[] {1, 5, 12, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getVariableValue(variable, "").intValue() == 10 + cl, "Energy resistance " + energy + " CL" + cl);
                    for (String otherEnergy : new String[] {"Acid", "Cold", "Electricity", "Fire", "Sonic"}) {
                        if (!otherEnergy.equals(energy)) require(pc.getVariableValue(otherEnergy + "ResistanceBonus", "").intValue() == 0, "Resistance stays energy-specific");
                    }
                    var other = new PCTemplate();
                    other.setName("Resistance stacking " + energy);
                    require(Globals.getContext().processToken(other, "BONUS", "VAR|" + variable + "|25|TYPE=Resistance"), "Resistance stacking fixture");
                    Globals.getContext().commit();
                    pc.addTemplate(other);
                    pc.calcActiveBonuses();
                    require(pc.getVariableValue(variable, "").intValue() == Math.max(25, 10 + cl), "Energy resistance takes highest source");
                    pc.removeTemplate(other);
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getVariableValue(variable, "").intValue() == 0, "Energy resistance refund");
                }
            }
            for (int cl : new int[] {1, 5, 10, 20, 100}) {
                choice.level = cl;
                String key = "Protection Effect - Mettle - Critical Confirmation Only";
                double ac = pc.getTotalBonusTo("COMBAT", "AC");
                facade.addTempBonus(available(facade, key));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac + 5 + cl, "Mettle confirmation AC");
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Mettle does not grant save bonuses");
                var effect = applied(facade, key);
                facade.setTempBonusActive(effect, false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Mettle inactive for ordinary attacks");
                facade.setTempBonusActive(effect, true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac + 5 + cl, "Mettle reactivation");
                facade.removeTempBonus(effect);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Mettle removal");
            }
            for (int cl : new int[] {1, 4, 5, 9, 10, 20}) {
                double cmd = pc.getTotalBonusTo("COMBAT", "CMD");
                double cmb = pc.getTotalBonusTo("COMBAT", "CMB");
                double ac = pc.getTotalBonusTo("COMBAT", "AC");
                choice.level = cl;
                facade.addTempBonus(available(facade, "Protection Effect - Slippery"));
                pc.calcActiveBonuses();
                int bonus = 2 + cl / 5;
                require(pc.getTotalBonusTo("COMBAT", "CMD") == cmd + bonus, "Slippery CMD progression");
                for (String skill : new String[] {"Acrobatics", "Escape Artist"}) {
                    require(pc.getTotalBonusTo("SKILL", skill) == bonus, "Slippery skill progression");
                }
                require(pc.getTotalBonusTo("COMBAT", "CMB") == cmb && pc.getTotalBonusTo("COMBAT", "AC") == ac, "Slippery does not grant CMB or AC");
                facade.removeTempBonus(applied(facade, "Protection Effect - Slippery"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "CMD") == cmd, "Slippery CMD removal");
                require(pc.getTotalBonusTo("SKILL", "Escape Artist") == 0, "Slippery skill removal");
            }
            for (String aegis : new String[] {"Deflection", "Armored Magic - Armor", "Armored Magic - Shield", "Resistance"}) {
                for (int cl : new int[] {1, 3, 4, 5, 9, 10, 12, 20}) {
                    choice.level = cl;
                    String key = "Protection Effect - " + aegis;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    int expected = aegis.equals("Resistance") ? 1 + cl / 4 : (aegis.endsWith("Armor") ? 3 : 1) + cl / 5;
                    if (aegis.equals("Resistance")) {
                        for (String save : new String[] {"Fortitude", "Reflex", "Will"}) {
                            require(pc.getTotalBonusTo("SAVE", save) == expected, "Aegis save CL" + cl);
                        }
                    } else {
                        require(pc.getTotalBonusTo("COMBAT", "AC") == 10 + expected, "Aegis AC " + aegis + " CL" + cl);
                    }
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo("COMBAT", "AC") == 10 && pc.getTotalBonusTo("SAVE", "Will") == 0, "Aegis removal");
                }
            }
            for (String[] entry : new String[][] {
                    {"Staunch Resistance", "Fortitude", "SAVE", "Fortitude"},
                    {"Staunch Resistance", "Reflex", "SAVE", "Reflex"},
                    {"Staunch Resistance", "Will", "SAVE", "Will"},
                    {"Enhance Focus", "Perception", "SKILL", "Perception"},
                    {"Enhance Focus", "Craft (Mechanical)", "SKILL", "Craft (Mechanical)"},
                    {"Enhance Focus", "Knowledge (Arcana)", "SKILL", "Knowledge (Arcana)"}}) {
                String key = "Enhancement Effect - " + entry[0] + " - " + entry[1];
                double base = pc.getTotalBonusTo(entry[2], entry[3]);
                for (int cl : new int[] {1, 3, 4, 5, 9, 10, 12, 20}) {
                    choice.level = cl;
                    facade.addTempBonus(available(facade, key));
                    pc.calcActiveBonuses();
                    int bonus = entry[0].equals("Staunch Resistance") ? 2 + cl / 5 : 5 + cl / 4;
                    require(pc.getTotalBonusTo(entry[2], entry[3]) == base + bonus, "Received " + key + " CL" + cl);
                    require(pc.getTotalBonusTo("STAT", "STR") == 0, "Save and skill effects do not change Strength");
                    facade.removeTempBonus(applied(facade, key));
                    pc.calcActiveBonuses();
                    require(pc.getTotalBonusTo(entry[2], entry[3]) == base, "Received effect refund " + key);
                }
            }
            for (int cl : new int[] {1, 4, 5, 8, 9, 12, 13, 20}) {
                choice.level = cl;
                facade.addTempBonus(available(facade, "Enhancement Effect - Superior Reflexes"));
                pc.calcActiveBonuses();
                int bonus = 1 + (cl - 1) / 4;
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == bonus, "Superior Reflexes initiative CL" + cl);
                require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_SUPERIOR_REFLEXES_AOO") == bonus, "Superior Reflexes additional attacks CL" + cl);
                facade.removeTempBonus(applied(facade, "Enhancement Effect - Superior Reflexes"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 0, "Initiative refund");
                require(pc.getTotalBonusTo("VAR", "SPHERES_RECEIVED_SUPERIOR_REFLEXES_AOO") == 0, "Additional attacks refund");
            }
            String cripple = "Enhancement Effect - Cripple";
            for (int cl : new int[] {1, 3, 4, 7, 8, 20}) {
                String helping = "Protection Effect - Helping Hand - Skill Reroll Only";
                choice.level = cl;
                facade.addTempBonus(available(facade, helping));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == Math.max(1, cl / 4), "Helping Hand reroll bonus CL" + cl);
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Helping Hand does not modify saving throws");
                var effect = applied(facade, helping);
                facade.setTempBonusActive(effect, false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Helping Hand disabled after check");
                facade.removeTempBonus(effect);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Helping Hand removed");
            }
            for (int cl : new int[] {1, 5, 10, 20}) {
                String exclusion = "Protection Effect - Exclusion - Attacker Penalty";
                choice.level = cl;
                double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                facade.addTempBonus(available(facade, exclusion));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack - cl, "Exclusion penalty CL" + cl);
                require(pc.getTotalBonusTo("COMBAT", "AC") == 10, "Exclusion does not grant AC");
                var effect = applied(facade, exclusion);
                facade.setTempBonusActive(effect, false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Exclusion disabled outside context");
                facade.setTempBonusActive(effect, true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack - cl, "Exclusion reactivated");
                facade.removeTempBonus(effect);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Exclusion removal");
            }
            for (int cl : new int[] {1, 4, 5, 9, 10, 20}) {
                String guardian = "Protection Effect - Guardian - Attacker Penalty";
                choice.level = cl;
                double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                facade.addTempBonus(available(facade, guardian));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack - 1 - cl / 5, "Guardian attacker penalty CL" + cl);
                require(pc.getTotalBonusTo("COMBAT", "AC") == 10, "Guardian does not grant recipient AC");
                var effect = applied(facade, guardian);
                facade.setTempBonusActive(effect, false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Disabled Guardian attacker penalty");
                facade.setTempBonusActive(effect, true);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack - 1 - cl / 5, "Reactivated Guardian attacker penalty");
                facade.setTempBonusActive(effect, false);
                facade.removeTempBonus(effect);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Removed Guardian attacker penalty");
            }
            for (int cl : new int[] {1, 4, 5, 9, 10, 20}) {
                choice.level = cl;
                double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
                facade.addTempBonus(available(facade, cripple));
                pc.calcActiveBonuses();
                int penalty = -2 - cl / 5;
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack + penalty, "Cripple attack CL" + cl);
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == penalty, "Cripple initiative CL" + cl);
                require(pc.getTotalBonusTo("SAVE", "Will") == penalty, "Cripple save CL" + cl);
                require(pc.getTotalBonusTo("SKILL", "ALL") == penalty, "Cripple all skills CL" + cl);
                require(pc.getTotalBonusTo("STAT", "STR") == 0, "Cripple does not lower Strength");
                facade.removeTempBonus(applied(facade, cripple));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Cripple attack refund");
                require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == 0, "Cripple initiative refund");
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Cripple save refund");
                require(pc.getTotalBonusTo("SKILL", "ALL") == 0, "Cripple skills refund");
            }
            String spectral = "Enhancement Effect - Spectral Enhancement - Conditional Saves";
            for (int cl : new int[] {1, 4, 5, 9, 10, 20}) {
                choice.level = cl;
                facade.addTempBonus(available(facade, spectral));
                pc.calcActiveBonuses();
                for (String save : new String[] {"Fortitude", "Reflex", "Will"}) {
                    require(pc.getTotalBonusTo("SAVE", save) == 2 + cl / 5, "Spectral conditional save " + save + " CL" + cl);
                }
                require(pc.getTotalBonusTo("COMBAT", "AC") == 10, "Spectral save toggle does not grant armor");
                facade.removeTempBonus(applied(facade, spectral));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Spectral conditional save removal");
            }
            choice.level = 14;
            facade.addTempBonus(available(facade, strength));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("STAT", "STR") == 6, "CL14 effect applied before stacking fixture");
            var other = new PCTemplate();
            other.setName("Other enhancement bonus stacking fixture");
            require(Globals.getContext().processToken(other, "BONUS", "STAT|STR|4|TYPE=ENHANCEMENT"), "Stacking fixture");
            Globals.getContext().commit();
            pc.addTemplate(other);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("STAT", "STR") == 6, "Enhancement bonuses do not stack");
            facade.removeTempBonus(applied(facade, strength));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("STAT", "STR") == 4, "Removing stronger effect preserves weaker bonus");
            pc.removeTemplate(other);
            var skillOther = new PCTemplate();
            skillOther.setName("Existing skill enhancement stacking fixture");
            require(Globals.getContext().processToken(skillOther, "BONUS", "SKILL|Perception|6|TYPE=Enhancement"), "Skill stacking fixture");
            var saveOther = new PCTemplate();
            saveOther.setName("Existing resistance saving throw fixture");
            require(Globals.getContext().processToken(saveOther, "BONUS", "SAVE|Will|2|TYPE=Resistance"), "Resistance fixture");
            Globals.getContext().commit();
            pc.addTemplate(skillOther);
            pc.addTemplate(saveOther);
            choice.level = 12;
            facade.addTempBonus(available(facade, "Enhancement Effect - Enhance Focus - Perception"));
            choice.level = 10;
            facade.addTempBonus(available(facade, "Enhancement Effect - Staunch Resistance - Will"));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SKILL", "Perception") == 8, "Focus does not stack with another enhancement bonus");
            require(pc.getTotalBonusTo("SAVE", "Will") == 6, "Untyped Staunch Resistance stacks with resistance bonuses");
            facade.removeTempBonus(applied(facade, "Enhancement Effect - Enhance Focus - Perception"));
            facade.removeTempBonus(applied(facade, "Enhancement Effect - Staunch Resistance - Will"));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SKILL", "Perception") == 6, "Focus removal preserves other skill bonus");
            require(pc.getTotalBonusTo("SAVE", "Will") == 2, "Staunch removal preserves resistance bonus");
            pc.removeTemplate(skillOther);
            pc.removeTemplate(saveOther);
            choice.level = 14;
            facade.addTempBonus(available(facade, strength));
            choice.level = 7;
            facade.addTempBonus(available(facade, intelligence));
            choice.level = 10;
            facade.addTempBonus(available(facade, "Enhancement Effect - Staunch Resistance - Will"));
            choice.level = 12;
            facade.addTempBonus(available(facade, "Enhancement Effect - Enhance Focus - Perception"));
            choice.level = 9;
            facade.addTempBonus(available(facade, "Enhancement Effect - Superior Reflexes"));
            pc.calcActiveBonuses();
            choice.level = 5;
            for (String aegis : new String[] {"Deflection", "Armored Magic - Armor", "Armored Magic - Shield"}) {
                facade.addTempBonus(available(facade, "Protection Effect - " + aegis));
            }
            choice.level = 12;
            facade.addTempBonus(available(facade, "Protection Effect - Resistance"));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "AC") == 18, "Different aegis AC types combine");
            require(pc.getTotalBonusTo("SAVE", "Will") == 8, "Resistance aegis combines with untyped Staunch bonus");
            require(choice.errors.isEmpty(), "Chooser errors " + choice.errors);
            choice.level = 10;
            facade.addTempBonus(available(facade, "Protection Effect - Slippery"));
            pc.calcActiveBonuses();
            if (!reload) {
                facade.addTempBonus(available(facade, "Fate Effect - Serendipity"));
                choice.level = 10;
                facade.addTempBonus(available(facade, "Enhancement Effect - Alter Movement - Walk"));
                choice.level = 12;
                facade.addTempBonus(available(facade, "Protection Effect - Energy Resistance - Fire"));
                choice.level = 10;
                facade.addTempBonus(available(facade, "Enhancement Effect - Cripple"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("SKILL", "ALL") == -3, "Cripple and Serendipity retained before save");
                facade.addTempBonus(available(facade, "Fate Effect - Borrow Luck - Attack Rolls"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == -7, "Borrow Luck retained with other effects");
                choice.level = 8;
                facade.addTempBonus(available(facade, "Fate Effect - Strength"));
                facade.addTempBonus(available(facade, "Fate Effect - Pain - Mental Skills"));
                choice.level = 20;
                facade.addTempBonus(available(facade, "Fate Effect - The Hanged Man - Penalize Will"));
                facade.addTempBonus(available(facade, "Fate Effect - The World - Conditional Skills"));
                choice.level = 10;
                facade.addTempBonus(available(facade, "Fate Effect - The Magician - Attacks of Opportunity"));
                facade.setTempBonusActive(applied(facade, "Fate Effect - The Magician - Attacks of Opportunity"), false);
                choice.level = 10;
                facade.addTempBonus(available(facade, "Fate Effect - The Hermit - Self Aid - Attack"));
                facade.setTempBonusActive(applied(facade, "Fate Effect - The Hermit - Self Aid - Attack"), false);
                choice.level = 3;
                facade.addTempBonus(available(facade, "Fate Effect - The Empress - Spend - Weapon Damage"));
                choice.level = 20;
                facade.addTempBonus(available(facade, "Fate Effect - Cups"));
                choice.level = 10;
                facade.addTempBonus(available(facade, "Fate Effect - Wands"));
                facade.addTempBonus(available(facade, "Fate Effect - Pentacles - Fortitude"));
                facade.addTempBonus(available(facade, "Fate Effect - The Fool"));
                choice.level = 20;
                facade.addTempBonus(available(facade, "Fate Effect - Swords"));
                pc.calcActiveBonuses();
                facade.setFile(Path.of(args[5]).toFile());
                require(CharacterManager.saveCharacter(facade), "Save failed");
            }
        } finally {
            ChooserFactory.setDelegate(oldDelegate);
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}