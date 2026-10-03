package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.core.Skill;
import pcgen.core.analysis.SkillRankControl;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Real controller checks for custom tradition purchase, grants and round trips. */
class PcgenTraditions {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("tradition-reload");
        boolean magic = args[6].equals("power");
        try {
            if (args[6].equals("drawback-martial")) {
                var tradition = game.getAbilityCategory("Conscript Martial Tradition");
                var talents = game.getAbilityCategory("Spheres Combat Talent");
                var special = game.getAbilityCategory("Special Ability");
                var sergeant = ability(tradition, "Martial Tradition - Sergeant");
                var spotter = ability(tradition, "Martial Tradition - Expedition Spotter");
                var equipment = game.getAbilityCategory("Sergeant Tradition Choice 1");
                var shield = ability(talents, "Equipment - Shield Training");
                var armor = ability(talents, "Equipment - Armor Training");
                var paid = pc.getAvailableAbilityPool(talents);
                if (!reload) {
                    var hacker = ability(tradition, "Martial Tradition - Hacker");
                    var interfaceTalent = ability(talents, "Tech - Improved User Interface");
                    controller.addAbility(tradition, hacker);
                    require(pc.hasAbilityKeyed(talents, "Tech - Remote Control"), "Hacker first gadget");
                    require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Remote Hacking"), "Hacker feat grant");
                    require(pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Tech Bonus Gadget")).intValue() == 0, "Hacker extra free gadget");
                    require(!interfaceTalent.qualifies(pc, interfaceTalent), "Unsecured accepted incompatible interface");
                    controller.removeAbility(tradition, hacker);
                    require(!pc.hasAbilityKeyed(talents, "Tech - Remote Control"), "Hacker gadget refund");
                    require(!pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "Remote Hacking"), "Hacker feat refund");
                    controller.addAbility(tradition, spotter);
                    require(pc.hasAbilityKeyed(talents, "Trap - Trap Finder"), "Dismantler bonus missing");
                    require(pc.hasAbilityKeyed(special, "Martial Drawback - Dismantler"), "Dismantler missing");
                    require(pc.getAvailableAbilityPool(game.getAbilityCategory("Expedition Spotter Tradition Choice 1")).intValue() == 1, "Spotter sphere choice");
                    require(pc.getAvailableAbilityPool(game.getAbilityCategory("Expedition Spotter Tradition Choice 2")).intValue() == 1, "Spotter theme choice");
                    controller.removeAbility(tradition, spotter);
                    require(!pc.hasAbilityKeyed(talents, "Trap - Trap Finder"), "Dismantler refund");
                    controller.addAbility(tradition, sergeant);
                    require(pc.getAvailableAbilityPool(equipment).intValue() == 2, "Sergeant equipment choices");
                    controller.addAbility(equipment, shield);
                    controller.addAbility(equipment, armor);
                }
                require(pc.hasAbilityKeyed(talents, "Leadership - Squad"), "Squad grant/persistence");
                require(pc.hasAbilityKeyed(game.getAbilityCategory("Spheres Leadership Package"), "Leadership Package - Cohort"), "Cohort grant");
                require(pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Leadership Package")).intValue() == 0, "Extra cohort package slot");
                require(pc.getAvailableAbilityPool(equipment).intValue() == 0, "Equipment spend/persistence");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Tradition spent paid talents");
                if (reload) {
                    controller.removeAbility(equipment, armor);
                    controller.removeAbility(equipment, shield);
                    controller.removeAbility(tradition, sergeant);
                    require(!pc.hasAbilityKeyed(talents, "Leadership - Squad"), "Squad refund");
                    require(!pc.hasAbilityKeyed(special, "Martial Drawback - Squad Leader"), "Drawback refund");
                    require(pc.getAvailableAbilityPool(equipment).intValue() == 0, "Equipment pool refund");
                }
            } else if (magic) {
                var tradition = game.getAbilityCategory("Custom Casting Tradition");
                var drawback = game.getAbilityCategory("Custom Casting Drawback");
                var boon = game.getAbilityCategory("Custom Casting Boon");
                var choice = ability(tradition, "Custom Casting Tradition");
                var verbal = ability(drawback, "Tradition - Verbal Casting");
                var somatic = ability(drawback, "Tradition - Somatic Casting");
                var focus = ability(drawback, "Tradition - Focus Casting");
                var signs = ability(drawback, "Tradition - Magical Signs");
                var prepared = ability(drawback, "Tradition - Prepared Caster");
                var easy = ability(boon, "Tradition - Easy Focus");
                var fortified = ability(boon, "Tradition - Fortified Casting");
                var somaticSecond = ability(drawback, "Tradition - Somatic Casting Second Selection");
                var extended = ability(drawback, "Tradition - Extended Casting");
                var extendedSecond = ability(drawback, "Tradition - Extended Casting Second Selection");
                var charged = ability(drawback, "Tradition - Charged Spells");
                int original = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, choice.getKeyName()), "Casting tradition reload");
                    require(pc.hasAbilityKeyed(drawback, verbal.getKeyName()), "Verbal reload");
                    require(pc.hasAbilityKeyed(drawback, somatic.getKeyName()), "Somatic reload");
                    require(pc.hasAbilityKeyed(boon, easy.getKeyName()), "Boon reload");
                    require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 14, "Spell pool reload");
                    controller.removeAbility(boon, easy);
                    controller.removeAbility(drawback, somatic);
                    controller.removeAbility(drawback, verbal);
                    controller.removeAbility(tradition, choice);
                }
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 14, "Casting cleanup");
                require(!verbal.qualifies(pc, verbal), "Drawback without tradition");
                controller.addAbility(tradition, choice);
                rejected(controller, messages, tradition, choice, "InfoAbility.Messages.Duplicate");
                require(pc.getAvailableAbilityPool(drawback).intValue() == 5, "Drawback capacity");
                require(pc.getAvailableAbilityPool(boon).intValue() == 0, "Boon available without drawbacks");
                rejected(controller, messages, boon, easy, "InfoAbility.Messages.NoPoints");
                require(!fortified.qualifies(pc, fortified), "Fortified without Draining Casting");
                controller.addAbility(drawback, verbal);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 2,
                    "One-point spell pool");
                controller.addAbility(drawback, somatic);
                require(pc.getAvailableAbilityPool(boon).intValue() == 2, "Drawbacks unlock boons");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 4,
                    "Drawback point spell pool: original=" + original + " current=" + pc.getVariableValue("SPHERES_SPELL_POINTS", "")
                    + " drawbacks=" + pc.getVariableValue("SPHERES_TRADITION_DRAWBACKS", ""));
                controller.addAbility(drawback, focus);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 5,
                    "Three-point spell pool");
                controller.addAbility(drawback, signs);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 7,
                    "Four-point spell pool");
                controller.addAbility(drawback, prepared);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 10,
                    "Five-point spell pool");
                rejected(controller, messages, drawback, ability(drawback, "Tradition - Draining Casting"),
                    "InfoAbility.Messages.NoPoints");
                controller.removeAbility(drawback, prepared);
                controller.removeAbility(drawback, signs);
                controller.removeAbility(drawback, focus);
                controller.addAbility(boon, easy);
                require(pc.getAvailableAbilityPool(boon).intValue() == 0, "Boon costs two points");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original, "Boon spent bonus spell points");
                rejected(controller, messages, boon, fortified, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(boon, easy);
                controller.removeAbility(drawback, somatic);
                controller.removeAbility(drawback, verbal);
                require(!somaticSecond.qualifies(pc, somaticSecond), "Second somatic requires first");
                require(!extendedSecond.qualifies(pc, extendedSecond), "Second extended requires first");
                rejected(controller, messages, drawback, extendedSecond, "InfoAbility.Messages.NotQualified");
                controller.addAbility(drawback, extended);
                require(pc.getAvailableAbilityPool(drawback).intValue() == 3, "Extended costs two points");
                require(pc.getAvailableAbilityPool(boon).intValue() == 2, "Extended grants two boon points");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 4,
                    "Extended counts as two spell-point drawbacks");
                controller.addAbility(drawback, extendedSecond);
                require(pc.getAvailableAbilityPool(drawback).intValue() == 1, "Double extended costs four points");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 7,
                    "Double extended counts as four drawbacks");
                controller.removeAbility(drawback, extendedSecond);
                require(pc.getVariableValue("SPHERES_TRADITION_DRAWBACKS", "").intValue() == 2,
                    "Partial extended removal retains first award");
                controller.removeAbility(drawback, extended);
                require(pc.getAvailableAbilityPool(drawback).intValue() == 5, "Weighted refund");
                controller.addAbility(drawback, somatic);
                controller.addAbility(drawback, somaticSecond);
                require(pc.getVariableValue("SPHERES_TRADITION_DRAWBACKS", "").intValue() == 2,
                    "Two somatic selections");
                rejected(controller, messages, drawback, somaticSecond, "InfoAbility.Messages.Duplicate");
                controller.removeAbility(drawback, somaticSecond);
                controller.removeAbility(drawback, somatic);
                controller.addAbility(drawback, charged);
                require(pc.getAvailableAbilityPool(boon).intValue() == 2, "Charged boon-only credit");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 2,
                    "Boon-only credit never grants spell points");
                controller.addAbility(boon, easy);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original,
                    "Charged alone funds one boon");
                controller.addAbility(drawback, verbal);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 2,
                    "Boon-only credit spent before ordinary credits");
                controller.removeAbility(boon, easy);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original + 4,
                    "Refund excludes boon-only credit from spell points");
                controller.removeAbility(drawback, verbal);
                rejected(controller, messages, drawback, prepared, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(drawback, charged);
                controller.addAbility(drawback, prepared);
                rejected(controller, messages, drawback, charged, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(drawback, prepared);
                var witchmarked = ability(drawback, "Tradition - Witchmarked");
                controller.addAbility(drawback, signs);
                rejected(controller, messages, drawback, witchmarked, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(drawback, signs);
                controller.addAbility(drawback, witchmarked);
                rejected(controller, messages, drawback, signs, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(drawback, witchmarked);
                var addictive = ability(drawback, "Tradition - Addictive Casting");
                controller.addAbility(drawback, addictive);
                require(pc.getAvailableAbilityPool(drawback).intValue() == 3, "Addictive weighted cost");
                require(pc.getAvailableAbilityPool(boon).intValue() == 2, "Addictive weighted boon award");
                require(pc.getVariableValue("SPHERES_TRADITION_DRAWBACKS", "").intValue() == 2,
                    "Addictive weighted spell points");
                controller.removeAbility(drawback, addictive);
                var draining = ability(drawback, "Tradition - Draining Casting");
                controller.addAbility(drawback, draining);
                controller.addAbility(drawback, verbal);
                int castingBefore = pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue();
                controller.addAbility(boon, fortified);
                require(pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue()
                    == Math.max(castingBefore, pc.getVariableValue("CON", "").intValue()),
                    "Fortified uses higher Constitution without lowering casting modifier");
                controller.removeAbility(boon, fortified);
                var featBoon = ability(boon, "Tradition - Drawback Feat");
                var drawbackFeats = game.getAbilityCategory("Casting Tradition Drawback Feat");
                var atWill = ability(game.getAbilityCategory("FEAT"), "At-Will Powers");
                controller.addAbility(boon, featBoon);
                require(pc.getAvailableAbilityPool(drawbackFeats).intValue() == 1, "Drawback feat boon pool");
                rejected(controller, messages, drawbackFeats, atWill, "InfoAbility.Messages.NotQualified");
                controller.addAbility(drawback, charged);
                controller.addAbility(drawbackFeats, atWill);
                require(pc.hasAbilityKeyed(game.getAbilityCategory("FEAT"), "At-Will Powers"), "Drawback feat grant");
                controller.removeAbility(drawbackFeats, atWill);
                controller.removeAbility(boon, featBoon);
                require(pc.getAvailableAbilityPool(drawbackFeats).intValue() == 0, "Drawback feat refund");
                controller.removeAbility(drawback, charged);
                controller.removeAbility(drawback, verbal);
                controller.removeAbility(drawback, draining);
                controller.removeAbility(tradition, choice);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == original, "Casting refunds");
                controller.addAbility(tradition, choice);
                controller.addAbility(drawback, verbal);
                controller.addAbility(drawback, somatic);
                controller.addAbility(boon, easy);
            } else if (args[6].equals("liturgist")) {
                var tradition = game.getAbilityCategory("Conscript Martial Tradition");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var magicTalents = game.getAbilityCategory("Spheres Magic Talent");
                var spheres = game.getAbilityCategory("Liturgist Magic Sphere");
                var training = game.getAbilityCategory("Spheres Custom Training Weapon");
                var feat = game.getAbilityCategory("FEAT");
                var selected = ability(tradition, "Martial Tradition - Liturgist");
                var life = ability(magicTalents, "Life Sphere");
                var sword = ability(training, "Custom Training - Longsword");
                var exotic = ability(training, "Custom Training - Sword (Bastard)");
                var swordProf = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.WeaponProf.class, "Longsword");
                var exoticProf = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.WeaponProf.class, "Sword (Bastard)");
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, selected.getKeyName()), "Liturgist persisted");
                    require(pc.hasAbilityKeyed(magicTalents, life.getKeyName()), "Liturgist sphere persisted");
                    require(pc.getAvailableAbilityPool(training).intValue() == 2, "Weapon costs persisted");
                    require(pc.hasWeaponProf(swordProf) && pc.hasWeaponProf(exoticProf), "Weapon proficiencies persisted");
                    controller.removeAbility(spheres, life);
                    controller.removeAbility(training, sword);
                    controller.removeAbility(training, exotic);
                    controller.removeAbility(tradition, selected);
                }
                var paid = pc.getAvailableAbilityPool(combat);
                var feats = pc.getAvailableAbilityPool(feat);
                require(!sword.qualifies(pc, sword), "Weapon requires Custom Training");
                controller.addAbility(tradition, selected);
                require(pc.hasAbilityKeyed(feat, "Basic Magic Training"), "Liturgist feat grant");
                require(pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Basic Magic Sphere")).intValue() == 0, "No unrestricted bonus sphere");
                require(pc.getAvailableAbilityPool(spheres).intValue() == 1, "Restricted sphere allowance");
                require(pc.getAvailableAbilityPool(training).intValue() == 5, "Training budget");
                controller.addAbility(training, sword);
                controller.addAbility(training, exotic);
                require(pc.getAvailableAbilityPool(training).intValue() == 2, "Exotic double cost");
                require(pc.hasWeaponProf(swordProf) && pc.hasWeaponProf(exoticProf), "Actual weapon proficiencies granted");
                rejected(controller, messages, training, sword, "InfoAbility.Messages.Duplicate");
                var custom = ability(combat, "Equipment - Custom Training");
                controller.addAbility(combat, custom);
                require(pc.getAvailableAbilityPool(training).intValue() == 7, "Repeated training adds five points");
                controller.removeAbility(combat, custom);
                require(pc.getAvailableAbilityPool(training).intValue() == 2, "Repeated training refund keeps original");
                controller.addAbility(spheres, life);
                require(pc.getAvailableAbilityPool(spheres).intValue() == 0, "Restricted sphere spent");
                require(pc.getAvailableAbilityPool(combat).equals(paid), "Paid combat pool isolation");
                require(pc.getAvailableAbilityPool(feat).equals(feats), "Paid feat pool isolation");
                controller.removeAbility(spheres, life);
                controller.removeAbility(tradition, selected);
                require(!sword.qualifies(pc, sword), "Training prerequisite loss");
                require(!pc.hasWeaponProf(swordProf) && !pc.hasWeaponProf(exoticProf), "Invalid retained choices grant no proficiency");
                require(!pc.hasAbilityKeyed(feat, "Basic Magic Training"), "Training feat removed");
                controller.removeAbility(training, sword);
                controller.removeAbility(training, exotic);
                require(pc.getAvailableAbilityPool(training).intValue() == 0, "Training refunded");
                controller.addAbility(tradition, selected);
                controller.addAbility(training, sword);
                controller.addAbility(training, exotic);
                controller.addAbility(spheres, life);
            } else if (args[6].equals("brew")) {
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var associated = game.getAbilityCategory("Spheres Alchemy Associated Skill");
                var alchemy = ability(combat, "Alchemy Sphere");
                var profession = ability(associated, "Alternative-Brew - Profession - Soldier");
                var craft = ability(associated, "Alternative-Brew - Craft - Mechanical");
                if (reload) {
                    require(pc.hasAbilityKeyed(associated, profession.getKeyName()), "Alternative skill persisted");
                    require(pc.getVariableValue("SPHERES_ALCHEMY_RANKS", "").intValue() == 1, "Alternative ranks persisted");
                    controller.removeAbility(associated, profession);
                    controller.removeAbility(combat, alchemy);
                }
                controller.addAbility(combat, alchemy);
                var paid = pc.getAvailableAbilityPool(combat);
                controller.addAbility(associated, craft);
                var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Craft (Mechanical)");
                require(SkillRankControl.getTotalRank(pc, skill).intValue() == 1, "Configurable Craft ranks");
                require(pc.getVariableValue("SPHERES_ALCHEMY_RANKS", "").intValue() == 1, "Configurable Craft DC ranks");
                require(pc.getAvailableAbilityPool(associated).intValue() == 0, "Single associated skill");
                controller.removeAbility(associated, craft);
                require(SkillRankControl.getTotalRank(pc, skill).intValue() == 0, "Craft choice refund");
                controller.addAbility(associated, profession);
                require(pc.getAvailableAbilityPool(combat).equals(paid), "Alternative grants no paid talent");
            } else if (args[6].equals("medic")) {
                var tradition = game.getAbilityCategory("Conscript Martial Tradition");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var packages = game.getAbilityCategory("Spheres Alchemy Package");
                var free = game.getAbilityCategory("Spheres Alchemy Bonus Formula");
                var medic = ability(tradition, "Martial Tradition - Field Medic");
                var alchemy = ability(combat, "Alchemy Sphere");
                var formulae = ability(packages, "Alchemy Package - Formulae");
                var salve = ability(combat, "Alchemy - Salve");
                var heal = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Heal");
                var craft = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Craft (Alchemy)");
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, medic.getKeyName()), "Medic persisted");
                    require(pc.hasAbilityKeyed(combat, salve.getKeyName()), "Medic salve persisted");
                    require(SkillRankControl.getTotalRank(pc, heal).intValue() == 1, "Medic skill persisted");
                    controller.removeAbility(tradition, medic);
                }
                var paid = pc.getAvailableAbilityPool(combat);
                controller.addAbility(tradition, medic);
                require(SkillRankControl.getTotalRank(pc, heal).intValue() == 1, "Medic Heal ranks");
                require(SkillRankControl.getTotalRank(pc, craft).intValue() == 0, "Medic must not grant Craft ranks");
                require(pc.getVariableValue("SPHERES_ALCHEMY_RANKS", "").intValue() == 1, "Medic associated ranks");
                require(pc.getVariableValue("SPHERES_ALCHEMY_FORMULAE", "").intValue() == 1, "Medic formula count");
                require(pc.getVariableValue("SPHERES_ALCHEMY_PREPARED_FORMULAE", "").intValue() == 2, "Medic formula capacity");
                require(pc.getVariableValue("SPHERES_ALCHEMY_BATCH", "").intValue() == 1, "Medic formula batch");
                require(!ability(combat, "Alchemy - Witchbane").qualifies(pc, ability(combat, "Alchemy - Witchbane")), "Toxin requires poison package");
                require(pc.getAvailableAbilityPool(free).intValue() == 0, "Salve consumes free formula");
                require(pc.getAvailableAbilityPool(packages).intValue() == 0, "Fixed formulae package cost");
                require(pc.getAvailableAbilityPool(combat).equals(paid), "Medic preserves paid talents");
                controller.removeAbility(tradition, medic);
                require(!pc.hasAbilityKeyed(combat, salve.getKeyName()), "Medic salve refund");
                require(SkillRankControl.getTotalRank(pc, heal).intValue() == 0, "Medic Heal refund");
                controller.addAbility(combat, alchemy);
                require(SkillRankControl.getTotalRank(pc, craft).intValue() == 1, "Ordinary Alchemy restores Craft");
                controller.addAbility(packages, formulae);
                require(pc.getAvailableAbilityPool(free).intValue() == 1, "Ordinary formulae free choice");
                controller.addAbility(free, salve);
                require(pc.hasAbilityKeyed(combat, salve.getKeyName()), "Free formula selection");
                controller.removeAbility(free, salve);
                controller.removeAbility(packages, formulae);
                controller.removeAbility(combat, alchemy);
                require(pc.getAvailableAbilityPool(combat).equals(paid), "Ordinary Alchemy refund");
                var associated = game.getAbilityCategory("Spheres Alchemy Associated Skill");
                var brewing = ability(associated, "Alternative-Brew - Profession - Soldier");
                var soldier = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Profession (Soldier)");
                require(!brewing.qualifies(pc, brewing), "Brew requires Alchemy");
                controller.addAbility(combat, alchemy);
                controller.addAbility(associated, brewing);
                require(SkillRankControl.getTotalRank(pc, soldier).intValue() == 1, "Alternative profession ranks");
                require(SkillRankControl.getTotalRank(pc, craft).intValue() == 0, "Alternative replaces Craft ranks");
                require(pc.getVariableValue("SPHERES_ALCHEMY_RANKS", "").intValue() == 1, "Alternative associated ranks: " + pc.getVariableValue("SPHERES_ALCHEMY_RANKS", ""));
                require(!medic.qualifies(pc, medic), "Medic rejects conflicting associated skill");
                controller.removeAbility(combat, alchemy);
                require(SkillRankControl.getTotalRank(pc, soldier).intValue() == 0, "Retained brew grants no ranks without sphere");
                controller.removeAbility(associated, brewing);
                require(pc.getAvailableAbilityPool(associated).intValue() == 1, "Brew refund");
                controller.addAbility(tradition, medic);
                require(!brewing.qualifies(pc, brewing), "Medic excludes alternate profession");
            } else if (args[6].equals("ace")) {
                var tradition = game.getAbilityCategory("Conscript Martial Tradition");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var packages = game.getAbilityCategory("Spheres Athletics Package");
                var start = game.getAbilityCategory("Ace Starting Package");
                var ace = ability(tradition, "Martial Tradition - Ace");
                var fly = ability(packages, "Athletics Package - Fly");
                var pilot = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Profession (Pilot)");
                var flying = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(Skill.class, "Fly");
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, ace.getKeyName()), "Ace persisted");
                    require(pc.hasAbilityKeyed(packages, fly.getKeyName()), "Ace package persisted");
                    require(SkillRankControl.getTotalRank(pc, flying).intValue() == 0, "Driver ranks persisted incorrectly");
                    controller.removeAbility(start, fly);
                    controller.removeAbility(tradition, ace);
                }
                var paid = pc.getAvailableAbilityPool(combat);
                controller.addAbility(tradition, ace);
                require(pc.hasAbilityKeyed(combat, "Athletics - Ace Pilot"), "Driver bonus talent");
                require(!pc.hasAbilityKeyed(combat, "Equipment Sphere"), "Ace must not grant Equipment");
                require(pc.getAvailableAbilityPool(packages).intValue() == 0, "Ace ordinary package slot");
                require(pc.getAvailableAbilityPool(start).intValue() == 1, "Ace restricted package slot");
                controller.addAbility(start, fly);
                require(pc.hasAbilityKeyed(packages, fly.getKeyName()), "Ace chosen package");
                require(SkillRankControl.getTotalRank(pc, flying).intValue() == 0, "Driver must suppress package ranks");
                require(SkillRankControl.getTotalRank(pc, pilot).intValue() == 1, "Ace Pilot ranks");
                require(pc.getAvailableAbilityPool(combat).equals(paid), "Ace spent paid talents");
                controller.removeAbility(tradition, ace);
                require(!pc.hasAbilityKeyed(combat, "Athletics - Ace Pilot"), "Driver talent refund");
                require(SkillRankControl.getTotalRank(pc, pilot).intValue() == 0, "Pilot rank refund");
                controller.removeAbility(start, fly);
                controller.addAbility(tradition, ace);
                controller.addAbility(start, fly);
            } else if (args[6].equals("halfling") || args[6].equals("half-orc")) {
                boolean halfling = args[6].equals("halfling");
                String race = halfling ? "Halfling" : "Half-Orc";
                String title = halfling ? "Clever Combatant" : "Trained Berserk";
                String sphere = halfling ? "Scoundrel Sphere" : "Berserker Sphere";
                String replaced = halfling ? "Halfling Luck" : "Orc Ferocity";
                var racial = game.getAbilityCategory(race + " Racial Trait");
                var special = game.getAbilityCategory("Special Ability");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var selected = ability(racial, race + " ~ Spheres " + title);
                if (reload) {
                    require(pc.hasAbilityKeyed(special, selected.getKeyName()), "Racial choice reload");
                    require(pc.hasAbilityKeyed(combat, sphere), "Racial sphere reload");
                    controller.removeAbility(racial, selected);
                }
                require(pc.hasAbilityKeyed(special, race + " ~ " + replaced), "Default racial trait present");
                var paid = pc.getAvailableAbilityPool(combat);
                controller.addAbility(racial, selected);
                require(pc.hasAbilityKeyed(combat, sphere), "Alternate racial sphere grant");
                require(!pc.hasAbilityKeyed(special, race + " ~ " + replaced), "Default racial trait replaced");
                require(pc.getAvailableAbilityPool(combat).equals(paid), "Racial grant preserves paid talents");
                controller.removeAbility(racial, selected);
                require(!pc.hasAbilityKeyed(combat, sphere), "Removed racial sphere refunded");
                require(pc.hasAbilityKeyed(special, race + " ~ " + replaced), "Default racial trait restored");
                controller.addAbility(racial, selected);
            } else if (args[6].equals("elf")) {
                var racial = game.getAbilityCategory("Elf Racial Trait");
                var special = game.getAbilityCategory("Special Ability");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var dreamless = ability(racial, "Elf ~ Spheres Dreamless Sleep");
                var sleep = ability(combat, "Scout - Somnambulance");
                if (reload) {
                    require(pc.hasAbilityKeyed(special, dreamless.getKeyName()), "Dreamless reload");
                    controller.removeAbility(racial, dreamless);
                }
                require(!sleep.qualifies(pc, sleep), "Somnambulance normally requires Scout");
                controller.addAbility(racial, dreamless);
                require(pc.hasAbilityKeyed(combat, sleep.getKeyName()), "Dreamless talent grant");
                require(sleep.qualifies(pc, sleep), "Dreamless second purchase without Scout");
                require(pc.getVariableValue("SPHERES_SCOUT_SOMNAMBULANCE_COUNT", "").intValue() == 1,
                    "Dreamless first rank: " + pc.getVariableValue("SPHERES_SCOUT_SOMNAMBULANCE_COUNT", ""));
                require(!pc.hasAbilityKeyed(special, "Elf ~ Elven Immunities"), "Elven immunities replaced");
                controller.removeAbility(racial, dreamless);
                require(!sleep.qualifies(pc, sleep), "Dreamless removal restores sphere requirement");
                require(pc.hasAbilityKeyed(special, "Elf ~ Elven Immunities"), "Elven immunities restored");
                controller.addAbility(racial, dreamless);
            } else if (args[6].equals("racial")) {
                var racial = game.getAbilityCategory("Human Racial Trait");
                var industry = ability(racial, "Human ~ Spheres Titan of Industry");
                var feats = game.getAbilityCategory("FEAT");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                if (reload) {
                    require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), industry.getKeyName()), "Racial selection reload");
                    require(pc.hasAbilityKeyed(combat, "Tinker Sphere"), "Racial sphere reload");
                    controller.removeAbility(racial, industry);
                }
                var featPool = pc.getAvailableAbilityPool(feats);
                var combatPool = pc.getAvailableAbilityPool(combat);
                controller.addAbility(racial, industry);
                require(pc.hasAbilityKeyed(combat, "Tinker Sphere"), "Racial Tinker grant");
                require(pc.getAvailableAbilityPool(feats).intValue() == featPool.intValue() - 1,
                    "Racial grant replaces human bonus feat");
                require(pc.getAvailableAbilityPool(combat).equals(combatPool), "Racial grant is free");
                controller.removeAbility(racial, industry);
                require(!pc.hasAbilityKeyed(combat, "Tinker Sphere"), "Racial sphere refund");
                require(pc.getAvailableAbilityPool(feats).equals(featPool), "Human feat restored");
                controller.addAbility(racial, industry);
            } else {
                var tradition = game.getAbilityCategory("Conscript Martial Tradition");
                var equipment = game.getAbilityCategory("Custom Martial Equipment");
                var theme = game.getAbilityCategory("Custom Martial Theme");
                var base = game.getAbilityCategory("Custom Martial Sphere");
                var bonus = game.getAbilityCategory("Spheres Equipment Bonus Talent");
                var talents = game.getAbilityCategory("Spheres Combat Talent");
                var choice = ability(tradition, "Custom Martial Tradition");
                var shield = ability(talents, "Equipment - Shield Training");
                var armor = ability(talents, "Equipment - Armor Training");
                var fencing = ability(talents, "Fencing Sphere");
                var scout = ability(talents, "Scout Sphere");
                var paid = pc.getAvailableAbilityPool(talents);
                if (!reload) {
                    rejected(controller, messages, equipment, armor, "InfoAbility.Messages.NotQualified");
                }
                if (reload) {
                    require(pc.hasAbilityKeyed(tradition, choice.getKeyName()), "Martial tradition reload");
                    require(pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Equipment reload");
                    require(pc.hasAbilityKeyed(talents, shield.getKeyName()), "Shield reload");
                    require(pc.hasAbilityKeyed(talents, fencing.getKeyName()), "Fencing reload");
                    controller.removeAbility(theme, scout);
                    controller.removeAbility(base, fencing);
                    controller.removeAbility(equipment, armor);
                    controller.removeAbility(bonus, shield);
                    controller.removeAbility(tradition, choice);
                }
                require(!pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Equipment not refunded");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Tradition touched paid pool");
                var warden = ability(tradition, "Martial Tradition - Warden");
                var iron = ability(tradition, "Martial Tradition - Iron Breaker Style");
                controller.addAbility(tradition, iron);
                require(!pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Iron Breaker has no Equipment grant");
                require(pc.hasAbilityKeyed(talents, "Berserker - Greater Sunder"), "Iron Breaker fixed talent");
                require(pc.getAvailableAbilityPool(bonus).intValue() == 0, "Iron Breaker has no Equipment free talent");
                controller.removeAbility(tradition, iron);
                require(!pc.hasAbilityKeyed(talents, "Berserker - Greater Sunder"), "Iron Breaker refund");
                controller.addAbility(tradition, warden);
                for (String grant : new String[]{"Equipment Sphere", "Equipment - Armor Training",
                        "Equipment - Shield Training", "Guardian Sphere", "Shield Sphere"}) {
                    require(pc.hasAbilityKeyed(talents, grant), "Warden missing " + grant);
                }
                require(pc.getAvailableAbilityPool(bonus).intValue() == 0, "Warden extra Equipment talent");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Warden charged paid pool");
                controller.removeAbility(tradition, warden);
                require(!pc.hasAbilityKeyed(talents, "Shield Sphere"), "Warden grant not refunded");
                var gunner = ability(tradition, "Martial Tradition - Combat Gunner");
                var gunnerChoice = game.getAbilityCategory("Combat Gunner Tradition Choice 1");
                controller.addAbility(tradition, gunner);
                require(pc.getAvailableAbilityPool(gunnerChoice).intValue() == 1, "Gunner choice pool");
                var barrage = ability(talents, "Barrage Sphere");
                controller.addAbility(gunnerChoice, barrage);
                require(pc.hasAbilityKeyed(talents, "Barrage Sphere"), "Gunner variable grant");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Gunner charged paid pool");
                controller.removeAbility(gunnerChoice, barrage);
                controller.removeAbility(tradition, gunner);
                require(pc.getAvailableAbilityPool(gunnerChoice).intValue() == 0, "Gunner refund");
                var chemist = ability(tradition, "Martial Tradition - Chemist");
                var alchemyPackage = game.getAbilityCategory("Spheres Alchemy Package");
                controller.addAbility(tradition, chemist);
                require(pc.hasAbilityKeyed(alchemyPackage, "Alchemy Package - Formulae"), "Chemist fixed package");
                require(pc.getAvailableAbilityPool(alchemyPackage).intValue() == 0, "Chemist extra package");
                controller.removeAbility(tradition, chemist);
                require(!pc.hasAbilityKeyed(alchemyPackage, "Alchemy Package - Formulae"), "Chemist package refund");
                var bushido = ability(tradition, "Martial Tradition - Bushido Warrior");
                var bushidoChoice = game.getAbilityCategory("Bushido Warrior Tradition Choice 1");
                var beastmastery = ability(bushidoChoice, "Bushido Warrior Tradition Choice 1 - Beastmastery Sphere");
                var beastPackage = game.getAbilityCategory("Spheres Beastmastery Package");
                controller.addAbility(tradition, bushido);
                require(!pc.hasAbilityKeyed(beastPackage, "Beastmastery Package - Ride"), "Unchosen Ride absent");
                require(pc.getAvailableAbilityPool(beastPackage).intValue() == 0, "No negative unchosen package pool");
                controller.addAbility(bushidoChoice, beastmastery);
                require(pc.hasAbilityKeyed(beastPackage, "Beastmastery Package - Ride"), "Bushido Ride grant");
                require(pc.getAvailableAbilityPool(beastPackage).intValue() == 0, "Bushido extra package");
                controller.removeAbility(bushidoChoice, beastmastery);
                require(!pc.hasAbilityKeyed(beastPackage, "Beastmastery Package - Ride"), "Bushido Ride refund");
                controller.removeAbility(tradition, bushido);
                var runner = ability(tradition, "Martial Tradition - Free Runner");
                var athleticsPackage = game.getAbilityCategory("Spheres Athletics Package");
                controller.addAbility(tradition, runner);
                require(pc.hasAbilityKeyed(athleticsPackage, "Athletics Package - Run"), "Runner Run grant");
                require(pc.hasAbilityKeyed(athleticsPackage, "Athletics Package - Leap"), "Runner Leap grant");
                require(pc.getAvailableAbilityPool(athleticsPackage).intValue() == 1, "Runner third package choice");
                require(!pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Runner unlisted Equipment sphere");
                controller.removeAbility(tradition, runner);
                require(pc.getAvailableAbilityPool(athleticsPackage).intValue() == 0, "Runner package refund");
                var highlander = ability(tradition, "Martial Tradition - Highlander");
                var highlanderChoice = game.getAbilityCategory("Highlander Tradition Choice 1");
                var highlanderScout = ability(highlanderChoice, "Highlander Tradition Choice 1 - Scout Sphere");
                var scoutBonus = game.getAbilityCategory("Highlander Scout Talent");
                var dualBonus = game.getAbilityCategory("Highlander Dual Wielding Talent");
                controller.addAbility(tradition, highlander);
                controller.addAbility(highlanderChoice, highlanderScout);
                require(pc.getAvailableAbilityPool(scoutBonus).intValue() == 1, "Highlander linked talent");
                require(pc.getAvailableAbilityPool(dualBonus).intValue() == 0, "Highlander unselected branch");
                controller.removeAbility(highlanderChoice, highlanderScout);
                require(pc.getAvailableAbilityPool(scoutBonus).intValue() == 0, "Highlander branch refund");
                controller.removeAbility(tradition, highlander);
                var janjaweed = ability(tradition, "Martial Tradition - Janjaweed");
                var janjaweedChoice = game.getAbilityCategory("Janjaweed Tradition Choice 1");
                var mounted = ability(janjaweedChoice, "Janjaweed Tradition Choice 1 - Mounted Training");
                var gunmanship = ability(janjaweedChoice, "Janjaweed Tradition Choice 1 - Gunmanship");
                var mountedPool = game.getAbilityCategory("Janjaweed Beastmastery Talents");
                controller.addAbility(tradition, janjaweed);
                controller.addAbility(janjaweedChoice, mounted);
                require(pc.getAvailableAbilityPool(mountedPool).intValue() == 2, "Janjaweed two mounted talents");
                require(!pc.hasAbilityKeyed(talents, "Barrage Sphere"), "Mounted branch excludes gunmanship");
                controller.removeAbility(janjaweedChoice, mounted);
                require(pc.getAvailableAbilityPool(mountedPool).intValue() == 0, "Mounted branch refund");
                controller.addAbility(janjaweedChoice, gunmanship);
                require(pc.hasAbilityKeyed(talents, "Barrage Sphere"), "Janjaweed Barrage grant");
                require(pc.hasAbilityKeyed(talents, "Sniper Sphere"), "Janjaweed Sniper grant");
                controller.removeAbility(janjaweedChoice, gunmanship);
                require(!pc.hasAbilityKeyed(talents, "Sniper Sphere"), "Janjaweed Sniper refund");
                controller.removeAbility(tradition, janjaweed);
                var artist = ability(tradition, "Martial Tradition - Wandering Martial Artist");
                var artistChoice = game.getAbilityCategory("Wandering Martial Artist Tradition Choice 1");
                var unarmedChoice = ability(artistChoice,
                    "Wandering Martial Artist Tradition Choice 1 - Improved Unarmed Strike");
                var feats = game.getAbilityCategory("FEAT");
                var featPool = pc.getAvailableAbilityPool(feats);
                controller.addAbility(tradition, artist);
                controller.addAbility(artistChoice, unarmedChoice);
                require(pc.hasAbilityKeyed(feats, "Improved Unarmed Strike"), "Artist existing feat grant");
                require(pc.getAvailableAbilityPool(feats).equals(featPool), "Artist free feat");
                controller.removeAbility(artistChoice, unarmedChoice);
                controller.removeAbility(tradition, artist);
                var elven = ability(tradition, "Martial Tradition - Elven Duelist");
                var finesse = ability(talents, "Equipment - Finesse Fighting");
                controller.addAbility(tradition, elven);
                require(pc.getVariableValue("SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT", "").intValue() == 2,
                    "Elven Duelist grants two Finesse Fighting ranks");
                require(!finesse.qualifies(pc, finesse), "Third Finesse Fighting rank must be rejected");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Elven ranks are free");
                controller.removeAbility(tradition, elven);
                require(pc.getVariableValue("SPHERES_EQUIPMENT_FINESSEFIGHTING_COUNT", "").intValue() == 0,
                    "Elven Duelist rank refund");
                var tattooed = ability(tradition, "Martial Tradition - Tattooed Warrior");
                controller.addAbility(tradition, tattooed);
                require(pc.hasAbilityKeyed(feats, "Dragon’s Tattoos"), "Tattooed Dragon feat grant");
                require(pc.hasAbilityKeyed(feats, "Zodiac Tattoos"), "Tattooed Zodiac feat grant");
                require(pc.getAvailableAbilityPool(feats).equals(featPool), "Tattooed feats are free");
                require(pc.getVariableValue("skillinfo(\"TOTALRANK\",\"Craft (Tattoos)\")", "").intValue()
                    == pc.getTotalLevels(), "Tattooed restricted ranks");
                controller.removeAbility(tradition, tattooed);
                require(!pc.hasAbilityKeyed(feats, "Dragon’s Tattoos"), "Tattooed feat refund");
                require(pc.getVariableValue("skillinfo(\"TOTALRANK\",\"Craft (Tattoos)\")", "").intValue()
                    == 0, "Tattooed rank refund");
                controller.addAbility(tradition, choice);
                rejected(controller, messages, tradition, choice, "InfoAbility.Messages.Duplicate");
                require(pc.hasAbilityKeyed(talents, "Equipment Sphere"), "Equipment sphere grant: tradition="
                    + pc.hasAbilityKeyed(tradition, choice.getKeyName()) + " combat="
                    + pc.getVariableValue("SPHERES_COMBAT_TALENTS", "") + " free="
                    + pc.getAvailableAbilityPool(bonus));
                require(pc.getAvailableAbilityPool(bonus).intValue() == 1, "First equipment talent grant");
                require(pc.getAvailableAbilityPool(equipment).intValue() == 1, "Second equipment talent grant");
                controller.addAbility(bonus, shield);
                controller.addAbility(equipment, armor);
                controller.addAbility(base, fencing);
                controller.addAbility(theme, scout);
                require(pc.hasAbilityKeyed(talents, armor.getKeyName()), "Equipment choice missing");
                require(pc.hasAbilityKeyed(talents, fencing.getKeyName()), "Base choice missing");
                require(pc.hasAbilityKeyed(talents, scout.getKeyName()), "Theme choice missing");
                require(pc.getAvailableAbilityPool(talents).equals(paid), "Free tradition charged paid pool");
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