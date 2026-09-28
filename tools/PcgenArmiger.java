package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import pcgen.facade.core.ChooserFacade;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Base-class Prowess qualification, grants, refunds and persistence. */
class PcgenArmiger {
    private static class FeatChoice extends Messages {
        String choice = "Piranha Strike";
        boolean removing;

        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            var list = removing ? chooser.getSelectedList() : chooser.getAvailableList();
            for (var item : list) {
                if (item.getKeyName().equals(choice)) {
                    if (removing) chooser.removeSelected(item);
                    else chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing feat choice: " + choice);
        }
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var cat = game.getAbilityCategory("Armiger Prowess");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var packages = game.getAbilityCategory("Spheres Leadership Package");
        var feats = game.getAbilityCategory("Armiger Champion Feat");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new FeatChoice();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        int level = pc.getVariableValue("SPHERES_ARMIGER_LEVEL", "").intValue();
        boolean reload = args[4].equals("armiger-reload");
        var focus = ability(cat, "Armiger Extra Focus (Requires Armiger 6)");
        var champion = ability(cat, "Armiger Champion");
        var deadly = ability(cat, "Armiger Deadly Prowess");
        var ranged = ability(cat, "Armiger Ranged Prowess");
        var oldDelegate = ChooserFactory.getDelegate();
        ChooserFactory.setDelegate(messages);
        try {
            if (reload) {
                if (level >= 8) {
                    require(pc.hasAbilityKeyed(combat, "Sniper Sphere"), "Saved ranged sphere");
                    messages.choice = "Sniper";
                    messages.removing = true;
                    controller.removeAbility(cat, ranged);
                    messages.removing = false;
                    messages.choice = "Piranha Strike";
                }
                require(pc.getTotalAbilityPool(feats).intValue() == 1, "Saved Champion pool");
                controller.removeAbility(cat, champion);
                if (level >= 6) {
                    require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Great Focus"), "Saved Great Focus");
                    controller.removeAbility(cat, focus);
                    require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Piranha Strike"), "Saved Deadly Prowess");
                    messages.removing = true;
                    controller.removeAbility(cat, deadly);
                    messages.removing = false;
                }
            }
            var piranha = ability(AbilityCategory.FEAT, "Piranha Strike");
            var combatPool = pc.getAvailableAbilityPool(combat);
            messages.choice = "Sniper";
            controller.addAbility(cat, ranged);
            require(pc.hasAbilityKeyed(combat, "Sniper Sphere"), "Ranged Prowess grants Sniper");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Precise Shot"), "Sniper base feat grant");
            if (level >= 4) {
                messages.choice = "Barrage";
                controller.addAbility(cat, ranged);
                require(pc.hasAbilityKeyed(combat, "Barrage Sphere"), "Second ranged choice grants Barrage");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Point-Blank Shot"), "Barrage base feat grant");
                messages.removing = true;
                controller.removeAbility(cat, ranged);
                require(!pc.hasAbilityKeyed(combat, "Barrage Sphere"), "Barrage partial refund");
                require(pc.hasAbilityKeyed(combat, "Sniper Sphere"), "Sniper survives partial refund");
            }
            messages.choice = "Sniper";
            messages.removing = true;
            controller.removeAbility(cat, ranged);
            require(!pc.hasAbilityKeyed(combat, "Sniper Sphere"), "Ranged full refund");
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Precise Shot"), "Base feat removed with sphere");
            require(pc.getAvailableAbilityPool(combat).equals(combatPool), "Ranged grants do not spend combat talents");
            messages.choice = "Piranha Strike";
            messages.removing = false;
            require(!piranha.qualifies(pc, piranha), "Fixture must lack ordinary Piranha Strike prerequisites");
            var pool = pc.getAvailableAbilityPool(cat);
            controller.addAbility(cat, deadly);
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Piranha Strike"), "Deadly Prowess bypasses feat prerequisites");
            require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == 1, "Deadly Prowess costs one slot");
            if (level >= 6) {
                messages.choice = "Deadly Aim";
                controller.addAbility(cat, deadly);
                messages.choice = "Power Attack";
                controller.addAbility(cat, deadly);
                require(pool.subtract(pc.getAvailableAbilityPool(cat)).intValue() == 3, "Three distinct feat choices");
                messages.removing = true;
                controller.removeAbility(cat, deadly);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Power Attack"), "Remove one granted feat");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Piranha Strike"), "Keep other granted feat");
                messages.choice = "Deadly Aim";
                controller.removeAbility(cat, deadly);
            }
            messages.choice = "Piranha Strike";
            messages.removing = true;
            controller.removeAbility(cat, deadly);
            messages.removing = false;
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Piranha Strike"), "Deadly Prowess full removal");
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Deadly Prowess full refund");
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Great Focus"), "No orphan Great Focus");
            for (String[] test : new String[][] {
                    {"Faith in Steel (Requires Enhanced Customization)", "5"},
                    {"Linebreaker (Requires Rapid Assault)", "5"},
                    {"Mobile Assault (Requires Rapid Assault)", "5"},
                    {"Penetrating Assault (Requires Rapid Assault)", "5"},
                    {"Shift Training (Requires Armiger 4)", "4"},
                    {"Technical Fluidity (requires Armiger 6)", "6"}}) {
                var option = ability(cat, "Armiger " + test[0]);
                require(option.qualifies(pc, option) == (level >= Integer.parseInt(test[1])), "Gate " + test[0]);
                if (!option.qualifies(pc, option)) {
                    rejected(controller, messages, cat, option, "InfoAbility.Messages.NotQualified");
                }
            }
            if (level >= 4) {
                var leadership = ability(combat, "Leadership Sphere");
                var cohort = ability(packages, "Leadership Package - Cohort");
                var share = ability(cat, "Armiger Share Customized Weapon (Requires Leadership sphere and (cohort) package)");
                rejected(controller, messages, cat, share, "InfoAbility.Messages.NotQualified");
                controller.addAbility(combat, leadership);
                rejected(controller, messages, cat, share, "InfoAbility.Messages.NotQualified");
                controller.addAbility(packages, cohort);
                controller.addAbility(cat, share);
                require(pc.hasAbilityKeyed(cat, share.getKeyName()), "Share selected with both prerequisites");
                controller.removeAbility(packages, cohort);
                require(!share.qualifies(pc, share), "Package removal revokes qualification");
                controller.removeAbility(cat, share);
                controller.removeAbility(combat, leadership);
            }
            controller.addAbility(cat, champion);
            require(pc.getAvailableAbilityPool(feats).intValue() == 1, "Champion grant");
            if (level >= 4) {
                controller.addAbility(cat, champion);
                require(pc.getAvailableAbilityPool(feats).intValue() == 2, "Repeated Champion");
                controller.removeAbility(cat, champion);
                require(pc.getAvailableAbilityPool(feats).intValue() == 1, "Champion partial refund");
            }
            controller.removeAbility(cat, champion);
            require(pc.getAvailableAbilityPool(feats).intValue() == 0, "Champion full refund");
            if (level >= 6) {
                controller.addAbility(cat, focus);
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Great Focus"), "Great Focus grant");
                controller.removeAbility(cat, focus);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Great Focus"), "Great Focus removal");
                controller.addAbility(cat, focus);
            } else {
                rejected(controller, messages, cat, focus, "InfoAbility.Messages.NotQualified");
            }
            controller.addAbility(cat, champion);
            if (level >= 6) controller.addAbility(cat, deadly);
            if (level >= 8) {
                messages.choice = "Sniper";
                controller.addAbility(cat, ranged);
            }
        } finally {
            ChooserFactory.setDelegate(oldDelegate);
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