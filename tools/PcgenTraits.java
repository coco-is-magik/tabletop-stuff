package pcgen.gui2.facade;

import java.math.BigDecimal;
import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Shared Pathfinder trait pool and Spheres trait selection/reload gate. */
class PcgenTraits {
    private static class DaysenseChooser extends Messages {
        @Override
        public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
            if (chooser.getSelectedList().getSize() == 1) {
                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
            } else {
                require(chooser.getAvailableList().getSize() == 2, "Daysense choice count");
                pcgen.facade.core.InfoFacade survival = null;
                for (var item : chooser.getAvailableList()) {
                    require(item.getKeyName().equals("Survival") || item.getKeyName().equals("Knowledge (Geography)"),
                        "Daysense offered an unrelated skill");
                    if (item.getKeyName().equals("Survival")) survival = item;
                }
                require(survival != null, "Daysense Survival choice");
                chooser.addSelected(survival);
            }
            chooser.commit();
            return true;
        }
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var traits = game.getAbilityCategory("Traits");
        require(traits != null, "Core trait category missing");
        var combat = ability(traits, "Spheres Trait ~ Maneuver Trained");
        var second = ability(traits, "Spheres Trait ~ Steel Body");
        var magic = ability(traits, "Spheres Trait ~ Chronosense");
        var drawback = ability(traits, "Spheres Trait ~ Abrasive");
        var otherDrawback = ability(traits, "Spheres Trait ~ Snobby");
        var aura = ability(traits, "Spheres Trait ~ Aura");
        var technophile = ability(traits, "Spheres Trait ~ Technophile");
        var engineering = Globals.getContext().getReferenceContext()
            .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Knowledge (Engineering)");
        var religionSkill = Globals.getContext().getReferenceContext()
            .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Knowledge (Religion)");
        boolean reload = args[4].equals("traits-reload");
        boolean persistDaysense = args.length > 6 && args[6].equals("daysense");
        boolean persistSteel = args.length > 6 && args[6].equals("steel");
        boolean persistDestructive = args.length > 6 && args[6].equals("destructive");
        var daysense = ability(traits, "Spheres Trait ~ Daysense");
        var survival = Globals.getContext().getReferenceContext()
            .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Survival");
        try {
            if (reload) {
                require(controller.getAbilities(traits).getSize() == 2, "Traits not saved");
                require(pc.hasAbilityKeyed(traits.getParentCategory(), aura.getKeyName()), "Aura persistence");
                var savedTrait = persistDaysense ? daysense : persistSteel ? second : persistDestructive
                    ? ability(traits, "Spheres Trait ~ Destructive Talent") : technophile;
                require(pc.hasAbilityKeyed(traits.getParentCategory(), savedTrait.getKeyName()), "Second trait persistence");
                require(pc.getTotalBonusTo("SKILL", "Knowledge (Religion)") == 1, "Saved Aura bonus");
                if (persistDaysense) {
                    require(pc.isClassSkill(survival), "Saved Daysense chosen class skill");
                    require(pc.getTotalBonusTo("SKILL", "Survival") == 1, "Saved Daysense Survival bonus");
                    require(pc.getTotalBonusTo("SKILL", "Knowledge (Geography)") == 1, "Saved Daysense Geography bonus");
                } else if (persistDestructive) {
                    require(pc.getVariableValue("SPHERES_DESTRUCTION_TRAIT_DAMAGE", "").intValue()
                        == 1 + pc.getVariableValue("TL", "").intValue() / 10, "Saved destructive damage");
                } else if (!persistSteel) {
                    require(pc.getTotalBonusTo("SKILL", "Craft (Mechanical)") == 2, "Saved Technophile bonus");
                }
                int savedHP = pc.hitPoints();
                controller.removeAbility(traits, aura);
                var oldChooser = pcgen.util.chooser.ChooserFactory.getDelegate();
                try {
                    if (persistDaysense) pcgen.util.chooser.ChooserFactory.setDelegate(new DaysenseChooser());
                    controller.removeAbility(traits, savedTrait);
                } finally {
                    pcgen.util.chooser.ChooserFactory.setDelegate(oldChooser);
                }
                if (persistDaysense) {
                    require(!pc.isClassSkill(survival), "Saved Daysense class skill removal");
                    require(pc.getTotalBonusTo("SKILL", "Survival") == 0, "Saved Daysense bonus removal");
                }
                if (persistSteel) {
                    int expectedHP = 1 + (pc.getVariableValue("TL", "").intValue() - 1) / 2;
                    require(savedHP - pc.hitPoints() == expectedHP, "Saved Steel Body HP and refund");
                }
                if (persistDestructive) {
                    require(pc.getVariableValue("SPHERES_DESTRUCTION_TRAIT_DAMAGE", "").intValue() == 0,
                        "Saved destructive damage removal");
                }
            }
            var pool = pc.getAvailableAbilityPool(traits);
            var destructive = ability(traits, "Spheres Trait ~ Destructive Talent");
            var magicTalents = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
            var destruction = ability(magicTalents, "Destruction Sphere");
            require(pc.hasAbilityKeyed(magicTalents, destruction.getKeyName()), "Destructive Talent fixture sphere");
            double damage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
            controller.addAbility(traits, destructive);
            int blastBonus = 1 + pc.getVariableValue("TL", "").intValue() / 10;
            require(pc.getVariableValue("SPHERES_DESTRUCTION_TRAIT_DAMAGE", "").intValue() == blastBonus,
                "Destructive Talent level-scaled bonus");
            require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == damage, "Destructive Talent is not weapon damage");
            controller.removeAbility(magicTalents, destruction);
            require(!destructive.qualifies(pc, destructive), "Destructive Talent sphere prerequisite loss");
            require(pc.getVariableValue("SPHERES_DESTRUCTION_TRAIT_DAMAGE", "").intValue() == 0,
                "Destructive Talent inactive without sphere");
            controller.addAbility(magicTalents, destruction);
            require(pc.getVariableValue("SPHERES_DESTRUCTION_TRAIT_DAMAGE", "").intValue() == blastBonus,
                "Destructive Talent sphere prerequisite restoration");
            controller.removeAbility(traits, destructive);
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Destructive Talent pool refund");
            int originalHP = pc.hitPoints();
            int steelHP = 1 + (pc.getVariableValue("TL", "").intValue() - 1) / 2;
            controller.addAbility(traits, second);
            require(pc.hitPoints() == originalHP + steelHP, "Steel Body hit-dice scaling");
            controller.removeAbility(traits, second);
            require(pc.hitPoints() == originalHP, "Steel Body HP refund");
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Steel Body pool refund");
            var scarred = ability(traits, "Spheres Trait ~ Scarred by War");
            var reduction = pcgen.cdom.facet.FacetLibrary.getFacet(pcgen.cdom.facet.DamageReductionFacet.class);
            var originalReduction = reduction.getDRString(pc.getCharID());
            controller.addAbility(traits, scarred);
            require(Integer.valueOf(1).equals(reduction.getDR(pc.getCharID(), "piercing")),
                "Scarred by War piercing bypass");
            controller.removeAbility(traits, scarred);
            require(reduction.getDRString(pc.getCharID()).equals(originalReduction), "Scarred by War DR refund");
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Scarred by War pool refund");
            for (String[] entry : new String[][] {
                    {"Learned Readiness", "Perception"},
                    {"Industrial Worker", "Knowledge (Engineering)"},
                    {"Higher Calling", "Diplomacy"}}) {
                var selected = ability(traits, "Spheres Trait ~ " + entry[0]);
                var skill = Globals.getContext().getReferenceContext()
                    .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, entry[1]);
                boolean originalClass = pc.isClassSkill(skill);
                double originalBonus = pc.getTotalBonusTo("SKILL", entry[1]);
                controller.addAbility(traits, selected);
                require(pc.hasAbilityKeyed(traits.getParentCategory(), selected.getKeyName()), entry[0] + " selection");
                require(pc.isClassSkill(skill), entry[0] + " class skill grant");
                require(pc.getTotalBonusTo("SKILL", entry[1]) == originalBonus,
                    entry[0] + " must not grant an unconditional skill bonus");
                controller.removeAbility(traits, selected);
                require(pc.isClassSkill(skill) == originalClass, entry[0] + " class skill refund");
                require(pc.getAvailableAbilityPool(traits).equals(pool), entry[0] + " pool refund");
            }
            boolean survivalClass = pc.isClassSkill(survival);
            double survivalBonus = pc.getTotalBonusTo("SKILL", "Survival");
            double geographyBonus = pc.getTotalBonusTo("SKILL", "Knowledge (Geography)");
            var previousChooser = pcgen.util.chooser.ChooserFactory.getDelegate();
            pcgen.util.chooser.ChooserFactory.setDelegate(new DaysenseChooser());
            try {
                controller.addAbility(traits, daysense);
                require(pc.isClassSkill(survival), "Daysense selected class skill");
                require(pc.getTotalBonusTo("SKILL", "Survival") == survivalBonus + 1, "Daysense Survival bonus");
                require(pc.getTotalBonusTo("SKILL", "Knowledge (Geography)") == geographyBonus + 1,
                    "Daysense unselected skill still receives bonus");
                require(!daysense.qualifies(pc, daysense), "Daysense cannot be taken twice");
                controller.removeAbility(traits, daysense);
                require(pc.isClassSkill(survival) == survivalClass, "Daysense class skill refund");
                require(pc.getTotalBonusTo("SKILL", "Survival") == survivalBonus, "Daysense skill refund");
                require(pc.getTotalBonusTo("SKILL", "Knowledge (Geography)") == geographyBonus,
                    "Daysense Geography refund");
                require(pc.getAvailableAbilityPool(traits).equals(pool), "Daysense pool refund");
            } finally {
                pcgen.util.chooser.ChooserFactory.setDelegate(previousChooser);
            }
            String[][] skillTraits = {
                {"Bountiful Charm", "Diplomacy", "Recruit cohorts", "2"},
                {"Abrasive", "Diplomacy", "Improve a creature's attitude", "-5"},
                {"Abrasive", "Diplomacy", "Entertain", "-5"},
                {"Abrasive", "Diplomacy", "Impressive display of skill", "-5"},
                {"Impersonator", "Bluff", "Impersonate another creature", "2"},
                {"Guardian Of The Real", "Knowledge (Planes)", "Identify monsters", "2"},
                {"Weird Virtuoso", "Perform (Dance)", "Subtly provide somatic components", "1"},
                {"Weird Virtuoso", "Perform (Oratory)", "Whisper verbal components", "1"},
                {"Weird Virtuoso", "Perform (Sing)", "Whisper verbal components", "1"},
                {"Corpse Watcher", "Heal", "Learn information (not treatment)", "3"},
                {"Colloquial Terms", "Linguistics", "Communicate without a shared language", "4"},
                {"Skeptical", "Sense Motive", "", "1"}
            };
            for (var entry : skillTraits) {
                var selected = ability(traits, "Spheres Trait ~ " + entry[0]);
                String type = entry[2].isEmpty() ? "SKILL" : "SITUATION";
                String key = entry[1] + (entry[2].isEmpty() ? "" : "=" + entry[2]);
                double before = pc.getTotalBonusTo(type, key);
                double general = pc.getTotalBonusTo("SKILL", entry[1]);
                controller.addAbility(traits, selected);
                require(pc.getTotalBonusTo(type, key) == before + Integer.parseInt(entry[3]),
                    entry[0] + " skill bonus");
                if (!entry[2].isEmpty()) {
                    require(pc.getTotalBonusTo("SKILL", entry[1]) == general,
                        entry[0] + " leaked to general skill checks");
                }
                controller.removeAbility(traits, selected);
                require(pc.getTotalBonusTo(type, key) == before, entry[0] + " bonus refund");
                require(pc.getAvailableAbilityPool(traits).equals(pool), entry[0] + " pool refund");
            }
            var spatial = ability(traits, "Spheres Trait ~ Spatial Awareness");
            boolean originalEngineering = pc.isClassSkill(engineering);
            controller.addAbility(traits, spatial);
            require(pc.isClassSkill(engineering), "Spatial Awareness engineering class skill");
            controller.removeAbility(traits, spatial);
            require(pc.isClassSkill(engineering) == originalEngineering, "Spatial Awareness class skill refund");
            double religion = pc.getTotalBonusTo("SKILL", "Knowledge (Religion)");
            double mechanical = pc.getTotalBonusTo("SKILL", "Craft (Mechanical)");
            controller.addAbility(traits, aura);
            require(pc.isClassSkill(religionSkill), "Aura religion class skill");
            require(pc.getTotalBonusTo("SKILL", "Knowledge (Religion)") == religion + 1,
                "Aura religion bonus");
            controller.addAbility(traits, technophile);
            require(pc.getTotalBonusTo("SKILL", "Craft (Mechanical)") == mechanical + 2,
                "Technophile mechanical bonus");
            require(pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue() == 0,
                "Technophile must not create a charge pool");
            var talents = game.getAbilityCategory("Spheres Combat Talent");
            var tech = ability(talents, "Tech Sphere");
            var extra = ability(pcgen.core.AbilityCategory.FEAT, "Extra Combat Talent");
            controller.addAbility(pcgen.core.AbilityCategory.FEAT, extra);
            controller.addAbility(talents, tech);
            require(pc.hasAbilityKeyed(talents, tech.getKeyName()), "Tech setup");
            int charges = pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue();
            controller.removeAbility(traits, technophile);
            require(pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue() == charges - 2,
                "Technophile capacity refund");
            controller.addAbility(traits, technophile);
            controller.removeAbility(talents, tech);
            require(pc.getVariableValue("SPHERES_TECH_CHARGE_CAPACITY", "").intValue() == 0,
                "Retained Technophile recreated lost charge pool");
            controller.removeAbility(pcgen.core.AbilityCategory.FEAT, extra);
            controller.removeAbility(traits, technophile);
            controller.removeAbility(traits, aura);
            require(pc.getTotalBonusTo("SKILL", "Knowledge (Religion)") == religion, "Aura refund");
            require(pc.getTotalBonusTo("SKILL", "Craft (Mechanical)") == mechanical, "Technophile refund");
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Skill traits pool refund");
            controller.addAbility(traits, drawback);
            require(pc.getAvailableAbilityPool(traits).equals(pool.add(BigDecimal.ONE)), "Drawback net trait pool");
            require(!otherDrawback.qualifies(pc, otherDrawback), "Second drawback qualified");
            rejected(controller, messages, traits, otherDrawback, "InfoAbility.Messages.NotQualified");
            controller.removeAbility(traits, drawback);
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Drawback removal/refund");
            require(combat.qualifies(pc, combat), "Combat trait not qualified");
            controller.addAbility(traits, combat);
            require(controller.getAbilities(traits).getSize() == 1, "Combat trait not selected: " + messages.errors);
            require(pc.getAvailableAbilityPool(traits).equals(pool.subtract(BigDecimal.ONE)), "Shared trait pool not spent");
            require(!second.qualifies(pc, second), "Duplicate combat category qualified");
            rejected(controller, messages, traits, second, "InfoAbility.Messages.NotQualified");
            controller.addAbility(traits, magic);
            require(controller.getAbilities(traits).getSize() == 2, "Magic trait not selected: " + messages.errors);
            controller.removeAbility(traits, magic);
            controller.removeAbility(traits, combat);
            require(pc.getAvailableAbilityPool(traits).equals(pool), "Trait pool refund");
            controller.addAbility(traits, aura);
            require(messages.errors.size() == 2, "Unexpected errors: " + messages.errors);
            var oldChooser = pcgen.util.chooser.ChooserFactory.getDelegate();
            try {
                if (persistDaysense) pcgen.util.chooser.ChooserFactory.setDelegate(new DaysenseChooser());
                controller.addAbility(traits, persistDaysense ? daysense : persistSteel ? second
                    : persistDestructive ? destructive : technophile);
                require(controller.getAbilities(traits).getSize() == 2, "Final persisted trait count");
                require(messages.errors.size() == 2, "Unexpected final trait errors: " + messages.errors);
            } finally {
                pcgen.util.chooser.ChooserFactory.setDelegate(oldChooser);
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