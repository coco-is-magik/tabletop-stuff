package pcgen.gui2.facade;

import java.math.BigDecimal;
import java.nio.file.Path;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Each paid blended feat funds one allocation, never two talent pools. */
class PcgenBlendedTraining {
    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var feats = AbilityCategory.FEAT;
        var allocations = game.getAbilityCategory("Spheres Blended Talent Allocation");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var combat = game.getAbilityCategory("Spheres Combat Talent");
        var feat = ability(feats, "Extra Blended Training Talent");
        var focus = ability(feats, "Extra Combat Talent");
        var magicChoice = ability(allocations, "Blended Training - Magic");
        var combatChoice = ability(allocations, "Blended Training - Combat");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        boolean reload = args[4].equals("blended-reload");
        try {
            if (reload) {
                require(pc.hasAbilityKeyed(feats, feat.getKeyName()), "Saved blended feat");
                require(pc.hasAbilityKeyed(allocations, magicChoice.getKeyName()), "Saved magic allocation");
                require(pc.hasAbilityKeyed(allocations, combatChoice.getKeyName()), "Saved combat allocation");
                require(pc.getAvailableAbilityPool(allocations).intValue() == 0, "Saved allocation costs");
                var savedMagic = pc.getAvailableAbilityPool(magic);
                var savedCombat = pc.getAvailableAbilityPool(combat);
                controller.removeAbility(allocations, magicChoice);
                controller.removeAbility(allocations, combatChoice);
                require(pc.getAvailableAbilityPool(magic).equals(savedMagic.subtract(BigDecimal.ONE)), "Saved magic refund");
                require(pc.getAvailableAbilityPool(combat).equals(savedCombat.subtract(BigDecimal.ONE)), "Saved combat refund");
                controller.removeAbility(feats, feat);
                controller.removeAbility(feats, feat);
                controller.removeAbility(feats, focus);
            }
            var featPool = pc.getAvailableAbilityPool(feats);
            var magicPool = pc.getAvailableAbilityPool(magic);
            var combatPool = pc.getAvailableAbilityPool(combat);
            require(!feat.qualifies(pc, feat), "Caster without focus must not qualify");
            rejected(controller, messages, feats, feat, "InfoAbility.Messages.NotQualified");
            require(!magicChoice.qualifies(pc, magicChoice), "Allocation requires feat");
            controller.addAbility(feats, focus);
            controller.addAbility(feats, feat);
            controller.addAbility(feats, feat);
            require(pc.getAvailableAbilityPool(feats).equals(featPool.subtract(BigDecimal.valueOf(3))), "Repeated paid feats");
            require(pc.getAvailableAbilityPool(allocations).intValue() == 2, "One allocation per feat");
            require(pc.getAvailableAbilityPool(magic).equals(magicPool), "Unallocated feat cannot grant magic");
            require(pc.getAvailableAbilityPool(combat).equals(combatPool.add(BigDecimal.ONE)), "Only focus feat grants combat initially");
            controller.addAbility(allocations, magicChoice);
            controller.addAbility(allocations, combatChoice);
            require(pc.getAvailableAbilityPool(allocations).intValue() == 0, "Shared allocation budget");
            rejected(controller, messages, allocations, magicChoice, "InfoAbility.Messages.NoPoints");
            require(pc.getAvailableAbilityPool(magic).equals(magicPool.add(BigDecimal.ONE)), "Magic allocation grant");
            require(pc.getAvailableAbilityPool(combat).equals(combatPool.add(BigDecimal.valueOf(2))), "Combat allocation grant");
            controller.removeAbility(feats, focus);
            require(!feat.qualifies(pc, feat), "Lost focus revokes feat qualification");
            require(!magicChoice.qualifies(pc, magicChoice), "Lost focus revokes allocation qualification");
            require(pc.getAvailableAbilityPool(magic).equals(magicPool), "Lost focus disables magic allocation");
            require(pc.getAvailableAbilityPool(combat).equals(combatPool), "Lost focus disables combat allocation");
            controller.addAbility(feats, focus);
            require(pc.getAvailableAbilityPool(magic).equals(magicPool.add(BigDecimal.ONE)), "Restored focus restores magic");
            require(pc.getAvailableAbilityPool(combat).equals(combatPool.add(BigDecimal.valueOf(2))), "Restored focus restores combat");
            controller.removeAbility(allocations, combatChoice);
            controller.addAbility(allocations, magicChoice);
            require(pc.getAvailableAbilityPool(magic).equals(magicPool.add(BigDecimal.valueOf(2))), "Repeated magic allocation");
            controller.removeAbility(allocations, magicChoice);
            require(pc.getAvailableAbilityPool(magic).equals(magicPool.add(BigDecimal.ONE)), "Partial repeated allocation refund");
            controller.removeAbility(allocations, magicChoice);
            controller.removeAbility(feats, feat);
            require(pc.getAvailableAbilityPool(allocations).intValue() == 1, "Partial feat refund");
            controller.removeAbility(feats, feat);
            require(pc.getAvailableAbilityPool(allocations).intValue() == 0, "Full feat refund");
            controller.removeAbility(feats, focus);
            require(pc.getAvailableAbilityPool(feats).equals(featPool), "All feat costs refunded");
            require(pc.getAvailableAbilityPool(magic).equals(magicPool), "All magic refunded");
            require(pc.getAvailableAbilityPool(combat).equals(combatPool), "All combat refunded");
            controller.addAbility(feats, focus);
            controller.addAbility(feats, feat);
            controller.addAbility(feats, feat);
            controller.addAbility(allocations, magicChoice);
            controller.addAbility(allocations, combatChoice);
            require(messages.errors.size() == 2, "Unexpected errors " + messages.errors);
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