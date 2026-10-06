package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import pcgen.facade.core.ChooserFacade;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Persistent bestial traits, prerequisite loss, refunds and saved selections. */
class PcgenShifter {
    private static class WeaponDamage extends pcgen.io.exporttoken.WeaponToken {
        String base(pcgen.core.PlayerCharacter pc, pcgen.core.Equipment weapon) {
            return getWeaponToken(pc, weapon, new java.util.StringTokenizer("BASEDAMAGE", "."), "WEAPON.BASEDAMAGE");
        }
    }
    private static class EnergyChoice extends Messages {
        String choice = "Acid";
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            if (chooser.getSelectedList().getSize() > 0) {
                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                chooser.commit();
                return true;
            }
            for (var item : chooser.getAvailableList()) {
                if (item.getKeyName().equals(choice)) {
                    chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Expected choice: " + choice);
        }
    }
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var traits = game.getAbilityCategory("Shifter Bestial Trait");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var champion = game.getAbilityCategory("Shifter Champion Feat");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new EnergyChoice();
        var oldDelegate = pcgen.util.chooser.ChooserFactory.getDelegate();
        pcgen.util.chooser.ChooserFactory.setDelegate(messages);
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_SHIFTER_LEVEL", "").intValue();
        int baselineAC = pc.getRace().getKeyName().equals("Halfling") ? 12 : 10;
        var hide = ability(traits, "Shifter Animal Hide (Ex)");
        var training = ability(traits, "Shifter Combat Talent");
        var adaptation = ability(traits, "Shifter Adaptation (Ex)");
        var improved = ability(traits, "Shifter Adaptation - Improved (requires adaptation)");
        var greater = ability(traits, "Shifter Adaptation - Greater (requires adaptation - improved adaptation - shifter 10)");
        boolean reload = args[4].equals("shifter-reload");
        try {
            var shiftingStyle = ability(traits, "Shifter Shifting Style");
            require(!shiftingStyle.qualifies(pc, shiftingStyle), "Base Shifter lacks Apex Knowledge of Many Shapes");
            if (reload && level == 6) {
                var savedBite = pc.getDisplay().getEquipmentSet().stream()
                    .filter(e -> e.isNatural() && e.getName().startsWith("Bite")).findFirst();
                require(savedBite.isPresent(), "Saved improved attack target exists");
                require(new WeaponDamage().base(pc, savedBite.get()).equals(pc.getRace().getKeyName().equals("Halfling") ? "1d6" : "1d8"),
                    "Saved Improved Natural Attack damage");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE.Natural") == 2, "Saved Magical Attacks enhancement");
                require(pc.getAvailableAbilityPool(traits).intValue() == 0, "Saved attack choices spend three traits");
                controller.removeAbility(traits, ability(traits, "Shifter Improved Natural Attack (Ex) (requires shifter 6)"));
                controller.removeAbility(traits, ability(traits, "Shifter Magical Attacks (Su)"));
                controller.removeAbility(traits, ability(traits, "Shifter Bite (Ex)"));
                pc.setCalcEquipmentList();
            }
            if (reload && level == 2) {
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == 2, "Saved Animal Advisor level");
                require(pc.getAvailableAbilityPool(traits).intValue() == 0, "Saved Animal Advisor cost");
                controller.removeAbility(traits, ability(traits, "Shifter Animal Advisor (Su)"));
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == 0, "Saved Animal Advisor refund");
            }
            if (reload) {
                var ordinary = pc.getEquipmentNamed("Dagger");
                require(ordinary != null && !ordinary.isNatural(), "Saved ordinary equipment");
                require(pc.getDisplay().getEquipSet().stream().anyMatch(set -> set.getItem() != null
                    && set.getItem().getName().equals("Dagger") && set.getItem() != ordinary),
                    "Ordinary equipped inventory still uses a separate clone");
                pc.removeEquipment(ordinary);
            }
            if (reload && level >= 4 && level < 10 && level != 6) {
                var breathCategory = game.getAbilityCategory("Shifter Breath Weapon Configuration");
                var savedCone = ability(breathCategory, "Shifter Breath Fire Cone");
                require(pc.getAvailableAbilityPool(traits).intValue() == level / 2 - 2, "Saved breath trait costs");
                require(pc.getAvailableAbilityPool(breathCategory).intValue() == 0, "Saved breath choice cost");
                require(pc.hasAbilityKeyed(breathCategory, "Shifter Breath Fire Cone"), "Saved breath configuration");
                require(pc.getVariableValue("SPHERES_SHIFTER_BREATH_RANGE", "").intValue() == 60, "Saved improved breath range");
                controller.removeAbility(breathCategory, savedCone);
                controller.removeAbility(traits, ability(traits, "Shifter Breath Weapon - Improved (requires breath weapon bestial trait - shifter level 4)"));
                controller.removeAbility(traits, ability(traits, "Shifter Breath Weapon (Su)"));
            }
            if (reload && level >= 18) {
                require(pc.getAvailableAbilityPool(traits).intValue() == level / 2 - 9, "Saved weapon and healing costs");
                require(pc.getVariableValue("FastHealingRate", "").intValue() == level / 2, "Saved repeated fast healing");
                require(pc.getDisplay().getEquipmentSet().stream().anyMatch(e -> e.isNatural() && e.getName().startsWith("Bite")), "Saved natural weapon");
                var fast = ability(traits, "Shifter Fast Healing (Ex) (requires quick healing bestial trait - shifter level 10)");
                controller.removeAbility(traits, fast);
                require(pc.getVariableValue("FastHealingRate", "").intValue() == 1, "Saved partial healing refund");
                controller.removeAbility(traits, fast);
                controller.removeAbility(traits, ability(traits, "Shifter Quick Healing (Su)"));
                controller.removeAbility(traits, ability(traits, "Shifter Bite (Ex)"));
                pc.setCalcEquipmentList();
                require(pc.getDisplay().getEquipmentSet().stream().noneMatch(e -> e.isNatural() && e.getName().startsWith("Bite")), "Saved natural weapon refund");
            }
            if (reload && level >= 10) {
                require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Acid"), "Saved chosen immunity");
                require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Fire"), "Saved choice excludes other energies");
                require(pc.getAvailableAbilityPool(traits).intValue() == level / 2 - 5, "Saved adaptation and hide costs");
                controller.removeAbility(traits, greater);
                controller.removeAbility(traits, improved);
                controller.removeAbility(traits, adaptation);
            }
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Endurance") == (level >= 3), "Endurance level grant");
            require(pc.getVariableValue("WildEmpathyLVL", "").intValue() == level, "Wild empathy advancement");
            require(pc.getTotalBonusTo("STAT", "CON") == (level < 7 ? 0 : 2 + 2 * ((level - 7) / 6)), "Inherent Constitution progression");
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Poison") == (level >= 8), "Poison immunity level");
            require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Disease") == (level >= 12), "Disease immunity level");
            if (reload && level >= 10) {
                require(pc.getTotalBonusTo("COMBAT", "AC") == baselineAC + 2, "Saved repeated natural armor");
                require(pc.getAvailableAbilityPool(traits).intValue() == level / 2 - 2, "Saved trait cost");
                controller.removeAbility(traits, hide);
                require(pc.getTotalBonusTo("COMBAT", "AC") == baselineAC + 1, "Partial natural armor refund");
                controller.removeAbility(traits, hide);
            }
            require(pc.getAvailableAbilityPool(traits).intValue() == level / 2, "Base trait pool");
            if (level < 2) {
                require(!hide.qualifies(pc, hide), "First trait level gate");
            } else {
                var breathCategory = game.getAbilityCategory("Shifter Breath Weapon Configuration");
                var breath = ability(traits, "Shifter Breath Weapon (Su)");
                var breathImproved = ability(traits, "Shifter Breath Weapon - Improved (requires breath weapon bestial trait - shifter level 4)");
                var cone = ability(breathCategory, "Shifter Breath Fire Cone");
                var line = ability(breathCategory, "Shifter Breath Cold Line");
                require(!cone.qualifies(pc, cone), "Breath configuration needs trait");
                require(!breathImproved.qualifies(pc, breathImproved), "Improved breath needs base trait");
                controller.addAbility(traits, breath);
                require(pc.getVariableValue("SPHERES_SHIFTER_BREATH_DC", "").intValue() == 10 + level / 2 + pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue(), "Breath DC");
                require(pc.getVariableValue("SPHERES_SHIFTER_BREATH_DICE", "").intValue() == (level + 1) / 2, "Breath dice progression");
                controller.addAbility(breathCategory, cone);
                require(pc.getAvailableAbilityPool(breathCategory).intValue() == 0, "Breath configuration spend");
                require(!line.qualifies(pc, line), "Only one energy/shape combination");
                require(pc.getVariableValue("SPHERES_SHIFTER_BREATH_RANGE", "").intValue() == 30, "Base cone range");
                if (level >= 4) {
                    controller.addAbility(traits, breathImproved);
                    require(pc.getVariableValue("SPHERES_SHIFTER_BREATH_RANGE", "").intValue() == 60, "Improved cone range");
                    controller.removeAbility(traits, breathImproved);
                }
                controller.removeAbility(breathCategory, cone);
                controller.addAbility(breathCategory, line);
                require(pc.getVariableValue("SPHERES_SHIFTER_BREATH_RANGE", "").intValue() == 60, "Base line range");
                controller.removeAbility(traits, breath);
                require(!line.qualifies(pc, line), "Configuration loses prerequisite");
                controller.removeAbility(breathCategory, line);
                require(pc.getAvailableAbilityPool(breathCategory).intValue() == 0, "Breath full refund");
                require(!improved.qualifies(pc, improved), "Adaptation prerequisite");
                controller.addAbility(traits, adaptation);
                require(improved.qualifies(pc, improved), "Adaptation unlocks improved");
                if (level >= 4) {
                    controller.addAbility(traits, improved);
                    for (String energy : new String[] {"Acid", "Cold", "Electricity", "Fire", "Sonic"}) {
                        require(pc.getVariableValue(energy + "ResistanceBonus", "").intValue() == level,
                            "Improved adaptation resistance: " + energy);
                    }
                    require(greater.qualifies(pc, greater) == (level >= 10), "Greater adaptation level gate");
                    if (level >= 10) {
                        controller.addAbility(traits, greater);
                        require(pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Acid"), "Chosen energy immunity");
                        require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Fire"), "No unchosen immunity");
                        controller.removeAbility(traits, greater);
                        require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Immunity to Acid"), "Immunity refund");
                    }
                    controller.removeAbility(traits, adaptation);
                    require(!improved.qualifies(pc, improved), "Lost adaptation prerequisite");
                    controller.removeAbility(traits, improved);
                    require(pc.getVariableValue("AcidResistanceBonus", "").intValue() == 0, "Resistance refund");
                } else {
                    controller.removeAbility(traits, adaptation);
                }
                var pool = pc.getAvailableAbilityPool(combat);
                controller.addAbility(traits, training);
                require(pc.getAvailableAbilityPool(combat).intValue() == pool.intValue() + 1, "Combat talent grant");
                if (level >= 4) {
                    controller.addAbility(traits, training);
                    require(pc.getAvailableAbilityPool(combat).intValue() == pool.intValue() + 2, "Repeated combat grant");
                    controller.removeAbility(traits, training);
                    require(pc.getAvailableAbilityPool(combat).intValue() == pool.intValue() + 1, "Partial combat refund");
                }
                controller.removeAbility(traits, training);
                require(pc.getAvailableAbilityPool(combat).equals(pool), "Combat grant refund");
                var featGrant = ability(traits, "Shifter Champion");
                controller.addAbility(traits, featGrant);
                require(pc.getAvailableAbilityPool(champion).intValue() == 1, "Champion pool grant");
                controller.removeAbility(traits, featGrant);
                require(pc.getAvailableAbilityPool(champion).intValue() == 0, "Champion refund");
                var heal = ability(traits, "Shifter Quick Healing (Su)");
                controller.addAbility(traits, heal);
                require(pc.getVariableValue("SPHERES_SHIFTER_QUICK_HEALING_HP", "").intValue() == 5 * (level / 2), "Healing capacity");
                var fast = ability(traits, "Shifter Fast Healing (Ex) (requires quick healing bestial trait - shifter level 10)");
                require(fast.qualifies(pc, fast) == (level >= 10), "Fast healing level gate");
                if (level >= 10) {
                    controller.addAbility(traits, fast);
                    require(pc.getVariableValue("FastHealingRate", "").intValue() == 1, "First fast healing selection");
                    controller.addAbility(traits, fast);
                    require(pc.getVariableValue("FastHealingRate", "").intValue() == level / 2, "Second fast healing selection");
                    require(!fast.qualifies(pc, fast), "Fast healing repeat cap");
                    controller.removeAbility(traits, fast);
                    require(pc.getVariableValue("FastHealingRate", "").intValue() == 1, "Partial fast healing refund");
                    controller.removeAbility(traits, fast);
                    require(pc.getVariableValue("FastHealingRate", "").intValue() == 0, "Full fast healing refund");
                }
                controller.removeAbility(traits, heal);
                require(!fast.qualifies(pc, fast), "Fast healing requires Quick Healing");
                require(pc.getVariableValue("SPHERES_SHIFTER_QUICK_HEALING_HP", "").intValue() == 0, "Healing refund");
                var trainer = ability(traits, "Shifter Animal Trainer (Ex)");
                double bonus = pc.getTotalBonusTo("SKILL", "Handle Animal");
                controller.addAbility(traits, trainer);
                require(pc.getTotalBonusTo("SKILL", "Handle Animal") == bonus + level / 2, "Animal Trainer bonus");
                controller.removeAbility(traits, trainer);
                require(pc.getTotalBonusTo("SKILL", "Handle Animal") == bonus, "Animal Trainer refund");
                var climb = ability(traits, "Shifter Spider Climb (Ex)");
                var speed = ability(traits, "Shifter Bestial Speed (Ex)");
                var walk = pcgen.cdom.enumeration.MovementType.getConstant("Walk");
                var climbing = pcgen.cdom.enumeration.MovementType.getConstant("Climb");
                double walkBase = pc.getDisplay().movementOfType(walk);
                controller.addAbility(traits, climb);
                require(pc.getDisplay().movementOfType(climbing) == 30, "Climb speed");
                if (level >= 4) {
                    controller.addAbility(traits, speed);
                    pc.adjustMoveRates();
                    require(pc.getDisplay().movementOfType(climbing) == 40, "Bestial Speed increases climb: " + pc.getDisplay().movementOfType(climbing) + " bonus=" + pc.getTotalBonusTo("MOVEADD", "TYPE.ALL") + " errors=" + messages.errors);
                    require(pc.getDisplay().movementOfType(walk) == walkBase + 10, "Bestial Speed increases walk");
                    controller.removeAbility(traits, speed);
                    pc.adjustMoveRates();
                    require(pc.getDisplay().movementOfType(climbing) == 30, "Speed refund");
                }
                controller.removeAbility(traits, climb);
                var flight = ability(traits, "Shifter Flight (Ex) (requires shifter 6)");
                var perfectFlight = ability(traits, "Shifter Flight - Perfect (requires shifter 6)");
                var fly = pcgen.cdom.enumeration.MovementType.getConstant("Fly");
                require(flight.qualifies(pc, flight) == (level >= 6), "Flight level gate");
                if (level >= 6) {
                    controller.addAbility(traits, flight);
                    require(pc.getDisplay().movementOfType(fly) == 30, "Flight speed");
                    require(pc.getVariableValue("Maneuverability", "").intValue() == 1, "Clumsy flight");
                    controller.addAbility(traits, perfectFlight);
                    require(pc.getVariableValue("Maneuverability", "").intValue() == 1 + level / 6, "Improved maneuverability");
                    controller.removeAbility(traits, perfectFlight);
                    require(pc.getVariableValue("Maneuverability", "").intValue() == 1, "Maneuverability refund");
                    controller.removeAbility(traits, flight);
                    pc.adjustMoveRates();
                    require(pc.getDisplay().movementOfType(fly) == 0, "Flight refund");
                }
                var skillfulFlight = ability(traits, "Shifter Flight - Skillful (Ex)");
                messages.choice = "Flyby Attack";
                controller.addAbility(traits, skillfulFlight);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Flyby Attack"), "Chosen flight feat");
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Hover"), "Unchosen flight feat absent");
                controller.removeAbility(traits, skillfulFlight);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Flyby Attack"), "Flight feat refund");
                messages.choice = "Acid";
                var fortification = ability(traits, "Shifter Fortification (Ex) (requires shifter level 6)");
                int fortificationLimit = Math.min(3, level / 6);
                for (int count = 1; count <= fortificationLimit; count++) {
                    controller.addAbility(traits, fortification);
                    require(pc.getVariableValue("SPHERES_SHIFTER_FORTIFICATION_PERCENT", "").intValue() == 25 * count, "Fortification capacity");
                }
                require(!fortification.qualifies(pc, fortification), "Fortification level-dependent cap");
                for (int count = fortificationLimit - 1; count >= 0; count--) {
                    controller.removeAbility(traits, fortification);
                    require(pc.getVariableValue("SPHERES_SHIFTER_FORTIFICATION_PERCENT", "").intValue() == 25 * count, "Fortification partial refund");
                }
                var sprint = ability(traits, "Shifter Sprint (Ex)");
                var magical = ability(traits, "Shifter Magical Attacks (Su)");
                double weaponDamage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
                double weaponHit = pc.getTotalBonusTo("COMBAT", "TOHIT");
                controller.addAbility(traits, magical);
                int magicalBonus = 1 + level / 5;
                require(pc.getTotalBonusTo("COMBAT", "TOHIT.Natural") == magicalBonus, "Natural attack enhancement");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE.Natural") == magicalBonus, "Natural damage enhancement");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == weaponDamage && pc.getTotalBonusTo("COMBAT", "TOHIT") == weaponHit,
                    "Magical Attacks does not affect manufactured weapons");
                var otherEnhancement = new pcgen.core.PCTemplate();
                otherEnhancement.setName("Natural enhancement stacking regression");
                require(Globals.getContext().processToken(otherEnhancement, "BONUS", "COMBAT|TOHIT.Natural,DAMAGE.Natural|6|TYPE=Enhancement"), "Enhancement fixture parse");
                Globals.getContext().commit();
                pc.addTemplate(otherEnhancement);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE.Natural") == 6, "Enhancement bonuses do not stack");
                pc.removeTemplate(otherEnhancement);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE.Natural") == magicalBonus, "Independent enhancement removal");
                controller.removeAbility(traits, magical);
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE.Natural") == 0, "Magical Attacks refund");
                var advisor = ability(traits, "Shifter Animal Advisor (Su)");
                controller.addAbility(traits, advisor);
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == level, "Animal Advisor familiar level");
                var otherFamiliar = new pcgen.core.PCTemplate();
                otherFamiliar.setName("Independent familiar advancement regression");
                require(Globals.getContext().processToken(otherFamiliar, "DEFINE", "FamiliarMasterLVL|0"), "Independent familiar definition");
                require(Globals.getContext().processToken(otherFamiliar, "BONUS", "VAR|FamiliarMasterLVL|3|TYPE=Base.STACK"), "Familiar fixture parse");
                Globals.getContext().commit();
                pc.addTemplate(otherFamiliar);
                pc.calcActiveBonuses();
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == level + 3, "Animal Advisor stacks with independent source");
                controller.removeAbility(traits, advisor);
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == 3, "Animal Advisor refund preserves other source");
                pc.removeTemplate(otherFamiliar);
                pc.calcActiveBonuses();
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == 0, "Animal Advisor refund");
                var snatch = ability(traits, "Shifter Snatch (requires Huge size)");
                require(!snatch.qualifies(pc, snatch), "Snatch requires Huge size");
                var huge = new pcgen.core.PCTemplate();
                huge.setName("Shifter Snatch size regression");
                require(Globals.getContext().processToken(huge, "BONUS", "SIZEMOD|NUMBER|" +
                    (pc.getRace().getKeyName().equals("Halfling") ? 3 : 2)), "Huge fixture parse");
                Globals.getContext().commit();
                pc.addTemplate(huge);
                pc.calcActiveBonuses();
                require(snatch.qualifies(pc, snatch), "Huge unlocks Snatch");
                controller.addAbility(traits, snatch);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Snatch"), "Snatch feat grant");
                pc.removeTemplate(huge);
                pc.calcActiveBonuses();
                require(!snatch.qualifies(pc, snatch), "Snatch size loss");
                controller.removeAbility(traits, snatch);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Snatch"), "Snatch refund");
                for (String[] attack : new String[][] {{"Bite", "Bite", "1d6"}, {"Claws", "Claw", "1d4"}, {"Gore", "Gore", "1d6"}}) {
                    var trait = ability(traits, "Shifter " + attack[0] + " (Ex)");
                    controller.addAbility(traits, trait);
                    var weapon = pc.getDisplay().getEquipmentSet().stream()
                        .filter(e -> e.isNatural() && e.getName().startsWith(attack[1])).findFirst();
                    require(weapon.isPresent(), "Natural weapon grant: " + attack[0]);
                    String damage = pc.getRace().getKeyName().equals("Halfling")
                        ? (attack[0].equals("Claws") ? "1d3" : "1d4") : attack[2];
                    require(weapon.get().getDamage(pc).equals(damage), "Natural weapon damage: " + weapon.get().getDamage(pc));
                    if (level >= 6) {
                        var improvedAttack = ability(traits, "Shifter Improved Natural Attack (Ex) (requires shifter 6)");
                        messages.choice = attack[1];
                        controller.addAbility(traits, improvedAttack);
                        String increased = pc.getRace().getKeyName().equals("Halfling")
                            ? (attack[0].equals("Claws") ? "1d4" : "1d6")
                            : (attack[0].equals("Claws") ? "1d6" : "1d8");
                        String exported = new WeaponDamage().base(pc, weapon.get());
                        require(exported.equals(increased), "Chosen natural damage increase: " + exported);
                        controller.removeAbility(traits, improvedAttack);
                        require(new WeaponDamage().base(pc, weapon.get()).equals(damage), "Natural damage improvement refund");
                        messages.choice = "Acid";
                    }
                    var large = new pcgen.core.PCTemplate();
                    large.setName("Shifter weapon size regression");
                    int sizeSteps = pc.getRace().getKeyName().equals("Halfling") ? 2 : 1;
                    require(Globals.getContext().processToken(large, "BONUS", "SIZEMOD|NUMBER|" + sizeSteps), "Size fixture parse");
                    Globals.getContext().commit();
                    pc.addTemplate(large);
                    pc.calcActiveBonuses();
                    var enlarged = pc.getDisplay().getEquipmentSet().stream()
                        .filter(e -> e.isNatural() && e.getName().startsWith(attack[1])).toList();
                    require(enlarged.size() == 1, "One active size-qualified natural weapon");
                    require(enlarged.get(0).getDamage(pc).equals(attack[0].equals("Claws") ? "1d6" : "1d8"), "Natural weapon tracks size change: " + enlarged.get(0).getDamage(pc) + " size=" + pc.getSizeAdjustment().getKeyName());
                    pc.removeTemplate(large);
                    pc.calcActiveBonuses();
                    controller.removeAbility(traits, trait);
                    require(pc.getDisplay().getEquipmentSet().stream().noneMatch(e -> e.isNatural() && e.getName().startsWith(attack[1])), "Natural weapon refund");
                }
                controller.addAbility(traits, sprint);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Run"), "Sprint feat");
                controller.removeAbility(traits, sprint);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Run"), "Sprint feat removal");
                if (level >= 10) {
                    controller.addAbility(traits, hide);
                    controller.addAbility(traits, hide);
                    require(pc.getTotalBonusTo("COMBAT", "AC") == baselineAC + 2, "Stacked natural armor");
                }
                if (level >= 4 && level < 10 && level != 6) {
                    controller.addAbility(traits, breath);
                    controller.addAbility(traits, breathImproved);
                    controller.addAbility(breathCategory, cone);
                }
                if (level >= 10) {
                    controller.addAbility(traits, adaptation);
                    controller.addAbility(traits, improved);
                    controller.addAbility(traits, greater);
                }
                if (level >= 18) {
                    controller.addAbility(traits, ability(traits, "Shifter Bite (Ex)"));
                    controller.addAbility(traits, heal);
                    controller.addAbility(traits, fast);
                    controller.addAbility(traits, fast);
                }
                if (level == 2) {
                    controller.addAbility(traits, advisor);
                }
                if (level == 6) {
                    controller.addAbility(traits, ability(traits, "Shifter Bite (Ex)"));
                    messages.choice = "Bite";
                    controller.addAbility(traits, ability(traits, "Shifter Improved Natural Attack (Ex) (requires shifter 6)"));
                    messages.choice = "Acid";
                    controller.addAbility(traits, magical);
                }
            }
            require(messages.errors.isEmpty(), "Unexpected errors: " + messages.errors);
        } finally {
            pcgen.util.chooser.ChooserFactory.setDelegate(oldDelegate);
            controller.closeCharacter();
        }
        if (!reload) {
            var dagger = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Equipment.class, "Dagger").clone();
            pc.addEquipment(dagger);
            var rootSet = pc.getEquipSetByIdPath(pcgen.core.character.EquipSet.DEFAULT_SET_PATH);
            require(rootSet != null, "Default equipment set");
            var daggerSet = new pcgen.core.character.EquipSet("0.1.99", "Carried", dagger.getName(), dagger);
            daggerSet.setQty(1.0f);
            pc.addEquipSet(daggerSet);
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}