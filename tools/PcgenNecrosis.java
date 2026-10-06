package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Persistent Necrosis counts and defenses, without activating optional effects. */
class PcgenNecrosis {
    private static final String[] PICKS = {"Cold Heart", "Deadened Flesh", "Numb Mind", "Necrotic Heart"};

    private static void check(pcgen.core.PlayerCharacter pc, int count) {
        require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == count, "Necrosis count");
        require(pc.getVariableValue("ColdResistanceBonus", "").intValue() == (count >= 4 ? 10 : 0), "Cold resistance threshold");
        require(pc.getVariableValue("ElectricityResistanceBonus", "").intValue() == (count >= 4 ? 10 : 0), "Electricity resistance threshold");
        require(pc.getTotalBonusTo("COMBAT", "AC") == 10 + (count >= 4 ? count / 2 : 0), "Deadened Flesh permanent armor threshold");
        String dr = pc.getDisplay().calcDR();
        require(count >= 4 ? dr.contains((count / 2) + "/-") : !dr.contains("/-"), "Deadened Flesh damage reduction: " + dr);
        if (count > 0) {
            require(pc.getVariableValue("SPHERES_COLD_HEART_ACTIVE_ROUNDS", "").intValue() == count, "Optional duration");
            require(pc.getVariableValue("SPHERES_COLD_HEART_ACTIVE_RESISTANCE", "").intValue() == 5 * count, "Optional resistance capacity");
        }
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var feats = AbilityCategory.FEAT;
        boolean reload = args[4].equals("necrosis-reload");
        try {
            if (reload) {
                require(pc.hasAbilityKeyed(feats, "Inhuman Defiler"), "Saved Inhuman Defiler");
                require(pc.hasAbilityKeyed(feats, "Distant Defiling"), "Saved Defiler feat");
                require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == 6, "Saved union Necrosis count");
                require(pc.getVariableValue("SPHERES_DEFILER_FEAT_COUNT", "").intValue() == 6, "Saved union Defiler count");
                int unionPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                controller.removeAbility(feats, ability(feats, "Inhuman Defiler"));
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == unionPoints - 3, "Saved union spell-point refund");
                controller.removeAbility(feats, ability(feats, "Distant Defiling"));
                check(pc, 4);
                for (int n = PICKS.length - 1; n >= 0; n--) {
                    controller.removeAbility(feats, ability(feats, PICKS[n]));
                    check(pc, n);
                }
            } else {
                var talents = game.getAbilityCategory("Spheres Magic Talent");
                require(!ability(feats, "Cold Heart").qualifies(pc, ability(feats, "Cold Heart")), "Death prerequisite");
                controller.addAbility(talents, ability(talents, "Death Sphere"));
            }
            int points = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
            var slots = pc.getAvailableAbilityPool(feats);
            for (int n = 0; n < PICKS.length; n++) {
                controller.addAbility(feats, ability(feats, PICKS[n]));
                check(pc, n + 1);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == points + Math.min(3, n + 1), "Explicit spell-point grants");
                require(pc.getAvailableAbilityPool(feats).intValue() == slots.intValue() - n - 1, "Feat slot spending");
            }
            for (int resistance : new int[] {5, 15}) {
                var template = new pcgen.core.PCTemplate();
                template.setName("Independent cold resistance " + resistance);
                require(Globals.getContext().processToken(template, "BONUS", "VAR|ColdResistanceBonus|" + resistance + "|TYPE=Resistance"), "Resistance fixture");
                Globals.getContext().commit();
                pc.addTemplate(template);
                require(pc.getVariableValue("ColdResistanceBonus", "").intValue() == Math.max(10, resistance), "Resistance uses highest source");
                pc.removeTemplate(template);
                pc.calcActiveBonuses();
                check(pc, 4);
            }
            for (String name : new String[] {"Banshee’s Sotto Voce", "Between Two Worlds", "Deathknight’s Purchase", "Hemomancy", "Wandering Spirit"}) {
                int before = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                var feat = ability(feats, name);
                controller.addAbility(feats, feat);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == before + 1, "Spell point: " + name);
                require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == 5, "Fifth necrosis feat");
                if (name.equals("Hemomancy")) require(pc.getVariableValue("SPHERES_HEMOMANCY_BLEEDING_BLINDSENSE", "").intValue() == 75, "Bleeding-only sense range");
                if (name.equals("Wandering Spirit")) require(pc.getVariableValue("SPHERES_PHYLACTERY_HARDNESS", "").intValue() == 15, "Phylactery hardness");
                controller.removeAbility(feats, feat);
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == before, "Spell point refund: " + name);
                check(pc, 4);
            }
            require(messages.errors.isEmpty(), "Unexpected errors: " + messages.errors);
            var distant = ability(feats, "Distant Defiling");
            var inhuman = ability(feats, "Inhuman Defiler");
            controller.addAbility(feats, distant);
            check(pc, 4);
            require(pc.getVariableValue("SPHERES_DEFILER_FEAT_COUNT", "").intValue() == 1, "Independent Defiler count");
            int beforeDefiler = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
            controller.addAbility(feats, inhuman);
            require(pc.hasAbilityKeyed(feats, "Inhuman Defiler"), "Inhuman selected");
            require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == 6, "Cross-family union counts overlap once");
            require(pc.getVariableValue("SPHERES_DEFILER_FEAT_COUNT", "").intValue() == 6, "Reciprocal cross-family count");
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == beforeDefiler + 3, "Inhuman union spell points");
            controller.removeAbility(feats, inhuman);
            check(pc, 4);
            require(pc.getVariableValue("SPHERES_DEFILER_FEAT_COUNT", "").intValue() == 1, "Cross-family revocation");
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == beforeDefiler, "Inhuman refund");
            controller.removeAbility(feats, distant);
            controller.addAbility(feats, distant);
            controller.addAbility(feats, inhuman);
            var terrainDefiler = ability(feats, "Terrain Defiler");
            controller.addAbility(feats, terrainDefiler);
            require(pc.getVariableValue("SPHERES_DEFILER_FEAT_COUNT", "").intValue() == 7, "Revised Terrain Defiler contributes to union");
            require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == 7, "Terrain Defiler cross-family contribution");
            controller.removeAbility(feats, terrainDefiler);
            // Remove ordinary Necrosis feats while retaining the cross-family bridge.
            // The spell-point benefit starts at four distinct feats, not four per type.
            int sixPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
            for (int n = PICKS.length - 1; n >= 1; n--) {
                controller.removeAbility(feats, ability(feats, PICKS[n]));
                int count = n + 2;
                require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == count, "Union threshold count");
                require(pc.getVariableValue("SPHERES_DEFILER_FEAT_COUNT", "").intValue() == count, "Reciprocal threshold count");
                int explicitLost = PICKS.length - 1 - n;
                int unionBonus = count >= 4 ? count / 2 : 0;
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == sixPoints - explicitLost - 3 + unionBonus,
                    "Four-feat union threshold and explicit refunds");
            }
            for (int n = 1; n < PICKS.length; n++) controller.addAbility(feats, ability(feats, PICKS[n]));
            require(pc.getVariableValue("SPHERES_NECROSIS_FEAT_COUNT", "").intValue() == 6, "Restore saved union");
            require(messages.errors.isEmpty(), "Defiler errors: " + messages.errors);
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