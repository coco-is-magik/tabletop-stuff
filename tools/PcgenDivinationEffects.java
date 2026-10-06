package pcgen.gui2.facade;

import java.nio.file.Path;
import pcgen.core.Globals;
import pcgen.facade.core.TempBonusFacade;
import pcgen.facade.core.ChooserFacade;
import pcgen.system.CharacterManager;
import pcgen.util.chooser.ChooserFactory;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Conditional Divination recipient modifiers through the production facade. */
class PcgenDivinationEffects {
    private static final String KEY = "Divination Effect - Sensory Overload - Mindless Target";

    private static TempBonusFacade effect(CharacterFacadeImpl facade, boolean applied) {
        return effect(facade, applied, KEY);
    }

    private static TempBonusFacade effect(CharacterFacadeImpl facade, boolean applied, String key) {
        var effects = applied ? facade.getTempBonuses() : facade.getAvailableTempBonuses();
        for (var item : effects) if (item.getKeyName().equals(key)) return item;
        throw new IllegalStateException("Missing Divination effect " + key);
    }

    private static class RollChoice extends Messages {
        int result = 1;
        @Override
        public boolean showGeneralChooser(ChooserFacade chooser) {
            for (var item : chooser.getAvailableList()) {
                if (item.toString().equals(Integer.toString(result))) {
                    chooser.addSelected(item);
                    chooser.commit();
                    return true;
                }
            }
            throw new IllegalStateException("Missing Divine Future roll " + result);
        }
    }

    private static double value(pcgen.core.PlayerCharacter pc, String kind, String key) {
        if (kind.equals("SKILL")) {
            var skill = Globals.getContext().getReferenceContext().silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, key);
            return pcgen.core.analysis.SkillModifier.modifier(skill, pc).doubleValue();
        }
        return pc.getTotalBonusTo(kind, key);
    }

    private static void monsterLore(CharacterFacadeImpl facade, pcgen.core.PlayerCharacter pc, boolean reload) {
        String key = "Divination Effect - Discern Individual - Monster Lore";
        if (reload) {
            double before = value(pc, "SKILL", "Knowledge (Arcana)");
            facade.setTempBonusActive(effect(facade, true, key), true);
            pc.calcActiveBonuses();
            require(value(pc, "SKILL", "Knowledge (Arcana)") == before + 5, "Persisted monster lore CL11");
            facade.removeTempBonus(effect(facade, true, key));
            pc.calcActiveBonuses();
        }
        var old = ChooserFactory.getDelegate();
        var choice = new RollChoice();
        ChooserFactory.setDelegate(choice);
        try {
            String[] skills = {"Arcana", "Dungeoneering", "Local", "Nature", "Planes", "Religion"};
            double[] base = new double[skills.length];
            for (int i = 0; i < skills.length; i++) base[i] = value(pc, "SKILL", "Knowledge (" + skills[i] + ")");
            double history = value(pc, "SKILL", "Knowledge (History)");
            double spellcraft = value(pc, "SKILL", "Spellcraft");
            for (int cl : new int[] {1, 2, 3, 4, 11, 20}) {
                choice.result = cl;
                facade.addTempBonus(effect(facade, false, key));
                pc.calcActiveBonuses();
                for (int i = 0; i < skills.length; i++) {
                    require(value(pc, "SKILL", "Knowledge (" + skills[i] + ")") == base[i] + Math.max(1, cl / 2), "Monster lore scaling " + skills[i]);
                }
                require(value(pc, "SKILL", "Knowledge (History)") == history, "Non-monster Knowledge excluded");
                require(value(pc, "SKILL", "Spellcraft") == spellcraft, "Spellcraft excluded");
                facade.setTempBonusActive(effect(facade, true, key), false);
                pc.calcActiveBonuses();
                for (int i = 0; i < skills.length; i++) require(value(pc, "SKILL", "Knowledge (" + skills[i] + ")") == base[i], "Monster lore disabled");
                facade.removeTempBonus(effect(facade, true, key));
                pc.calcActiveBonuses();
            }
            if (!reload) {
                choice.result = 11;
                facade.addTempBonus(effect(facade, false, key));
                facade.setTempBonusActive(effect(facade, true, key), false);
            }
        } finally {
            ChooserFactory.setDelegate(old);
        }
    }

    private static void future(CharacterFacadeImpl facade, pcgen.core.PlayerCharacter pc, boolean reload) {
        String saved = "Divination Effect - Divine Future - Maneuver";
        if (reload) {
            double before = pc.getTotalBonusTo("COMBAT", "CMB");
            facade.removeTempBonus(effect(facade, true, saved));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "CMB") == before - 7, "Saved Divine Future result removal");
        }
        var old = ChooserFactory.getDelegate();
        var choice = new RollChoice();
        ChooserFactory.setDelegate(choice);
        try {
            String[][] targets = {{"Attack", "COMBAT", "TOHIT"}, {"Save", "SAVE", "Will"},
                    {"Skill", "SKILL", "Spellcraft"}, {"Initiative", "COMBAT", "INITIATIVE"},
                    {"Maneuver", "COMBAT", "CMB"}};
            double damage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
            double ac = pc.getTotalBonusTo("COMBAT", "AC");
            for (String[] target : targets) {
                String key = "Divination Effect - Divine Future - " + target[0];
                double[] base = new double[targets.length];
                for (int i = 0; i < targets.length; i++) base[i] = value(pc, targets[i][1], targets[i][2]);
                for (int roll : new int[] {1, 4, 5, 7, 8}) {
                    choice.result = roll;
                    facade.addTempBonus(effect(facade, false, key));
                    pc.calcActiveBonuses();
                    for (int i = 0; i < targets.length; i++) {
                        require(value(pc, targets[i][1], targets[i][2]) == base[i] +
                                (targets[i][0].equals(target[0]) ? roll : 0), "Divine Future category isolation " + target[0]);
                    }
                    require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == damage, "Divine Future excludes damage");
                    require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Divine Future excludes AC");
                    facade.setTempBonusActive(effect(facade, true, key), false);
                    pc.calcActiveBonuses();
                    for (int i = 0; i < targets.length; i++) require(value(pc, targets[i][1], targets[i][2]) == base[i], "Future roll disabled");
                    facade.removeTempBonus(effect(facade, true, key));
                }
            }
            if (!reload) {
                choice.result = 7;
                facade.addTempBonus(effect(facade, false, saved));
            }
        } finally {
            ChooserFactory.setDelegate(old);
        }
    }

    private static void precognition(CharacterFacadeImpl facade, pcgen.core.PlayerCharacter pc,
                                     CharacterAbilities controller) {
        var feats = pcgen.core.AbilityCategory.FEAT;
        String key = "Divination State - Active Senses";
        var protection = ability(feats, "Precogniscent Protection");
        var resistance = ability(feats, "Precogniscent Resistance");
        var smite = ability(feats, "Precogniscent Smite");
        var old = ChooserFactory.getDelegate();
        var choice = new RollChoice();
        ChooserFactory.setDelegate(choice);
        try {
            double ac = pc.getTotalBonusTo("COMBAT", "AC");
            double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
            double damage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
            double save = pc.getTotalBonusTo("SAVE", "Will");
            choice.result = 10;
            facade.addTempBonus(effect(facade, false, key));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Active senses alone grant no feat benefits");
            facade.removeTempBonus(effect(facade, true, key));
            for (var feat : new pcgen.core.Ability[] {protection, resistance, smite}) {
                controller.addAbility(feats, feat);
                require(pc.hasAbilityKeyed(feats, feat.getKeyName()), "Selected " + feat.getKeyName());
            }
            require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Known senses are not active senses");
            int hd = pc.getTotalLevels();
            for (int count : new int[] {0, 1, 2, 3, 4, 10}) {
                choice.result = count;
                facade.addTempBonus(effect(facade, false, key));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac + Math.min(count, 1 + hd / 5), "Protection HD cap");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack + Math.min(count, 1 + hd / 5), "Smite attack HD cap");
                require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == damage + Math.min(count, 1 + hd / 5), "Smite damage HD cap");
                require(pc.getTotalBonusTo("SAVE", "Will") == save + Math.min(count, 1 + hd / 4), "Resistance HD cap");
                facade.setTempBonusActive(effect(facade, true, key), false);
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Sense dismissal removes Protection");
                require(pc.getTotalBonusTo("SAVE", "Will") == save, "Sense dismissal removes Resistance");
                facade.removeTempBonus(effect(facade, true, key));
            }
            choice.result = 10;
            facade.addTempBonus(effect(facade, false, key));
            var competing = new pcgen.core.PCTemplate();
            competing.setName("Competing Precogniscent bonus types");
            require(Globals.getContext().processToken(competing, "BONUS", "COMBAT|AC,TOHIT,DAMAGE|6|TYPE=Insight"), "Competing insight fixture");
            require(Globals.getContext().processToken(competing, "BONUS", "SAVE|ALL|6|TYPE=Resistance"), "Competing resistance fixture");
            Globals.getContext().commit();
            pc.addTemplate(competing);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "AC") == ac + Math.max(6, 1 + hd / 5), "Protection insight does not stack");
            require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack + Math.max(6, 1 + hd / 5), "Smite insight does not stack");
            require(pc.getTotalBonusTo("SAVE", "Will") == save + Math.max(6, 1 + hd / 4), "Resistance does not stack");
            pc.removeTemplate(competing);
            controller.removeAbility(feats, protection);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("COMBAT", "AC") == ac, "Feat removal removes Protection despite active senses");
            require(pc.getTotalBonusTo("SAVE", "Will") == save + 1 + hd / 4, "Other feat survives shared definition removal");
            controller.addAbility(feats, protection);
            facade.removeTempBonus(effect(facade, true, key));
            for (var feat : new pcgen.core.Ability[] {protection, resistance, smite}) controller.removeAbility(feats, feat);
            pc.calcActiveBonuses();
        } finally {
            ChooserFactory.setDelegate(old);
        }
    }

    private static void capability(CharacterFacadeImpl facade, pcgen.core.PlayerCharacter pc, boolean reload) {
        String key = "Divination Effect - Divine Capability - Assessed Target";
        if (reload) {
            double before = value(pc, "SKILL", "Spellcraft");
            facade.setTempBonusActive(effect(facade, true, key), true);
            pc.calcActiveBonuses();
            require(value(pc, "SKILL", "Spellcraft") == before + 5, "Persisted capability CL11");
            facade.removeTempBonus(effect(facade, true, key));
            pc.calcActiveBonuses();
        }
        var old = ChooserFactory.getDelegate();
        var choice = new RollChoice();
        ChooserFactory.setDelegate(choice);
        try {
            double spellcraft = value(pc, "SKILL", "Spellcraft");
            double motive = value(pc, "SKILL", "Sense Motive");
            double attack = pc.getTotalBonusTo("COMBAT", "TOHIT");
            double save = pc.getTotalBonusTo("SAVE", "Will");
            for (int cl : new int[] {1, 2, 3, 10, 11, 20}) {
                choice.result = cl;
                facade.addTempBonus(effect(facade, false, key));
                pc.calcActiveBonuses();
                require(value(pc, "SKILL", "Spellcraft") == spellcraft + cl / 2, "Capability Spellcraft half CL");
                require(value(pc, "SKILL", "Sense Motive") == motive + cl / 2, "Capability Sense Motive half CL");
                require(pc.getTotalBonusTo("COMBAT", "TOHIT") == attack, "Capability does not affect attacks");
                require(pc.getTotalBonusTo("SAVE", "Will") == save, "Capability does not affect saves");
                facade.setTempBonusActive(effect(facade, true, key), false);
                pc.calcActiveBonuses();
                require(value(pc, "SKILL", "Spellcraft") == spellcraft, "Capability disabled outside assessment");
                facade.removeTempBonus(effect(facade, true, key));
                pc.calcActiveBonuses();
                require(value(pc, "SKILL", "Sense Motive") == motive, "Capability removal");
            }
            if (!reload) {
                choice.result = 11;
                facade.addTempBonus(effect(facade, false, key));
                facade.setTempBonusActive(effect(facade, true, key), false);
            }
        } finally {
            ChooserFactory.setDelegate(old);
        }
    }

    private static void conditionalSenses(CharacterFacadeImpl facade, pcgen.core.PlayerCharacter pc, boolean reload) {
        String retained = "Divination Effect - Unhooded Sight - Disbelieve Illusion";
        if (reload) {
            double before = pc.getTotalBonusTo("SAVE", "Will");
            facade.setTempBonusActive(effect(facade, true, retained), true);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SAVE", "Will") == before + 4, "Retained Unhooded Sight CL9");
            facade.removeTempBonus(effect(facade, true, retained));
            pc.calcActiveBonuses();
        }
        var old = ChooserFactory.getDelegate();
        var choice = new RollChoice();
        ChooserFactory.setDelegate(choice);
        try {
            double perception = value(pc, "SKILL", "Perception");
            double will = pc.getTotalBonusTo("SAVE", "Will");
            double fort = pc.getTotalBonusTo("SAVE", "Fortitude");
            double reflex = pc.getTotalBonusTo("SAVE", "Reflex");
            int msb = pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue();
            int clBase = pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue();
            for (String name : new String[] {"Ghost Sight - Invisible or Ethereal Target", "Unhooded Sight - Disbelieve Illusion"}) {
                String key = "Divination Effect - " + name;
                boolean ghost = name.startsWith("Ghost");
                for (int cl : new int[] {1, 2, 3, 4, 9, 10, 20}) {
                    choice.result = cl;
                    facade.addTempBonus(effect(facade, false, key));
                    pc.calcActiveBonuses();
                    int bonus = ghost ? cl : Math.max(1, cl / 2);
                    require(value(pc, "SKILL", "Perception") == perception + bonus, "Conditional sense Perception");
                    require(pc.getTotalBonusTo("SAVE", "Will") == will + (ghost ? 0 : bonus), "Conditional sense Will");
                    require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == msb + (ghost ? 0 : bonus), "Conditional sense MSB");
                    require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == clBase, "Sense does not increase caster level");
                    require(pc.getTotalBonusTo("SAVE", "Fortitude") == fort && pc.getTotalBonusTo("SAVE", "Reflex") == reflex, "Other saves unchanged");
                    facade.setTempBonusActive(effect(facade, true, key), false);
                    pc.calcActiveBonuses();
                    require(value(pc, "SKILL", "Perception") == perception, "Conditional sense disabled");
                    facade.removeTempBonus(effect(facade, true, key));
                    pc.calcActiveBonuses();
                    require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == msb, "Conditional MSB removal");
                }
            }
            if (!reload) {
                choice.result = 9;
                facade.addTempBonus(effect(facade, false, retained));
                facade.setTempBonusActive(effect(facade, true, retained), false);
            }
        } finally {
            ChooserFactory.setDelegate(old);
        }
    }

    private static void sniper(CharacterFacadeImpl facade, pcgen.core.PlayerCharacter pc) {
        var old = ChooserFactory.getDelegate();
        var choice = new RollChoice();
        ChooserFactory.setDelegate(choice);
        try {
            for (String[] target : new String[][] {
                    {"Distance Perception", "SKILL", "Perception"},
                    {"Ranged Attack Penalties", "COMBAT", "TOHIT"}}) {
                String key = "Divination Effect - Sniper's Eye - " + target[0];
                double base = value(pc, target[1], target[2]);
                double damage = pc.getTotalBonusTo("COMBAT", "DAMAGE");
                for (int cl : new int[] {1, 2, 3, 10, 20}) {
                    for (int penalty : new int[] {0, 2, 6, 15}) {
                        var original = new pcgen.core.PCTemplate();
                        original.setName("Sniper penalty " + target[0] + cl + " " + penalty);
                        require(Globals.getContext().processToken(original, "BONUS", target[1] + "|" + target[2] + "|-" + penalty), "Original eligible penalty");
                        Globals.getContext().commit();
                        pc.addTemplate(original);
                        choice.result = Math.min(penalty, target[0].equals("Distance Perception") ? cl : cl / 2);
                        facade.addTempBonus(effect(facade, false, key));
                        pc.calcActiveBonuses();
                        require(value(pc, target[1], target[2]) == base - penalty + choice.result, "Sniper offsets actual eligible penalty");
                        require(value(pc, target[1], target[2]) <= base, "Sniper never exceeds unpenalized roll");
                        require(pc.getTotalBonusTo("COMBAT", "DAMAGE") == damage, "Sniper does not add damage");
                        facade.removeTempBonus(effect(facade, true, key));
                        pc.calcActiveBonuses();
                        require(value(pc, target[1], target[2]) == base - penalty, "Sniper removal restores penalty");
                        pc.removeTemplate(original);
                        pc.calcActiveBonuses();
                    }
                }
            }
        } finally {
            ChooserFactory.setDelegate(old);
        }
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var facade = (CharacterFacadeImpl) CharacterManager.getCharacters().iterator().next();
        boolean reload = args[4].equals("divination-reload");
        var cat = pcgen.core.SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var sphere = ability(cat, "Divination Sphere");
        var futureTalent = ability(cat, "Divination - Divine Future");
        try {
            if (reload) {
                var feats = pcgen.core.AbilityCategory.FEAT;
                require(pc.getVariableValue("SPHERES_ACTIVE_DIVINATION_SENSES", "").intValue() == 10, "Persisted active senses");
                int hd = pc.getTotalLevels();
                double before = pc.getTotalBonusTo("COMBAT", "AC");
                facade.removeTempBonus(effect(facade, true, "Divination State - Active Senses"));
                pc.calcActiveBonuses();
                require(pc.getTotalBonusTo("COMBAT", "AC") == before - (1 + hd / 5), "Persisted Protection removal");
                for (String name : new String[] {"Protection", "Resistance", "Smite"}) {
                    var feat = ability(feats, "Precogniscent " + name);
                    require(pc.hasAbilityKeyed(feats, feat.getKeyName()), "Persisted Precogniscent feat " + name);
                    controller.removeAbility(feats, feat);
                }
                require(pc.getVariableValue("SPHERES_DIVINATION_DIVINEFUTURE_COUNT", "").intValue() == 5, "Five saved Divine Future selections");
                rejected(controller, messages, cat, futureTalent, "InfoAbility.Messages.NotQualified");
                for (int i = 0; i < 5; i++) controller.removeAbility(cat, futureTalent);
                controller.removeAbility(cat, sphere);
            }
            var pool = pc.getAvailableAbilityPool(cat);
            rejected(controller, messages, cat, futureTalent, "InfoAbility.Messages.NotQualified");
            controller.addAbility(cat, sphere);
            for (int i = 1; i <= 5; i++) {
                controller.addAbility(cat, futureTalent);
                require(pc.getVariableValue("SPHERES_DIVINATION_DIVINEFUTURE_COUNT", "").intValue() == i, "Divine Future capacity " + i);
            }
            rejected(controller, messages, cat, futureTalent, "InfoAbility.Messages.NotQualified");
            for (int i = 4; i >= 0; i--) {
                controller.removeAbility(cat, futureTalent);
                require(pc.getVariableValue("SPHERES_DIVINATION_DIVINEFUTURE_COUNT", "").intValue() == i, "Divine Future partial refund " + i);
            }
            controller.removeAbility(cat, sphere);
            require(pc.getAvailableAbilityPool(cat).equals(pool), "Divine Future full pool refund");
            controller.addAbility(cat, sphere);
            precognition(facade, pc, controller);
            var greater = ability(cat, "Divination - Greater Divine");
            var lingering = ability(cat, "Divination - Lingering Divination");
            var shared = ability(cat, "Divination - Shared Perception");
            var viewing = ability(cat, "Divination - Viewing");
            int originalCl = pc.getVariableValue("SPHERES_CL_DIVINATION", "").intValue();
            for (int cl : new int[] {1, 2, 4, 5, 9, 10, 11, 20}) {
                var fixture = new pcgen.core.PCTemplate();
                fixture.setName("Divination sphere CL fixture " + cl);
                require(Globals.getContext().processToken(fixture, "BONUS", "VAR|SPHERES_CL_DIVINATION|" + (cl - originalCl)), "Divination CL fixture");
                Globals.getContext().commit();
                pc.addTemplate(fixture);
                require(pc.getVariableValue("SPHERES_DIVINATION_DIVINE_RANGE", "").intValue() == 100 + 10 * cl, "Medium divine range");
                require(pc.getVariableValue("SPHERES_DIVINATION_SENSE_HOURS", "").intValue() == cl, "Sense duration uses sphere CL");
                controller.addAbility(cat, shared);
                controller.addAbility(cat, viewing);
                require(pc.getVariableValue("SPHERES_DIVINATION_SHARED_TARGETS", "").intValue() == 2 + cl / 5, "Shared Perception target capacity");
                require(pc.getVariableValue("SPHERES_DIVINATION_SHARED_RANGE", "").intValue() == 400 + 40 * cl, "Shared Perception uses long range without Greater Divine");
                require(pc.getVariableValue("SPHERES_DIVINATION_VIEWING_DETECT_DC", "").intValue() == 20 + cl, "Viewing sensor detection DC");
                controller.removeAbility(cat, viewing);
                controller.removeAbility(cat, shared);
                require(pc.getVariableValue("SPHERES_DIVINATION_SHARED_TARGETS", "").intValue() == 0, "Shared Perception refund");
                require(pc.getVariableValue("SPHERES_DIVINATION_VIEWING_DETECT_DC", "").intValue() == 0, "Viewing refund");
                controller.addAbility(cat, greater);
                require(pc.getVariableValue("SPHERES_DIVINATION_DIVINE_RANGE", "").intValue() == 400 + 40 * cl, "Greater Divine long range");
                controller.removeAbility(cat, greater);
                require(pc.getVariableValue("SPHERES_DIVINATION_DIVINE_RANGE", "").intValue() == 100 + 10 * cl, "Greater Divine refund");
                controller.addAbility(cat, lingering);
                require(pc.getVariableValue("SPHERES_DIVINATION_LINGER_ROUNDS", "").intValue() == 2, "Lingering concentration extension");
                controller.removeAbility(cat, lingering);
                require(pc.getVariableValue("SPHERES_DIVINATION_LINGER_ROUNDS", "").intValue() == 0, "Lingering refund");
                pc.removeTemplate(fixture);
            }
            if (!reload) {
                for (int i = 0; i < 5; i++) controller.addAbility(cat, futureTalent);
            }
        } finally {
            controller.closeCharacter();
        }
        if (reload) {
            require(pc.getTotalBonusTo("SAVE", "Will") == 0, "Saved inactive penalty stays inactive");
            facade.setTempBonusActive(effect(facade, true), true);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SAVE", "Will") == -2, "Saved penalty reactivates");
            require(pc.getTotalBonusTo("SAVE", "Fortitude") == -2, "Saved Fortitude penalty");
            facade.removeTempBonus(effect(facade, true));
            pc.calcActiveBonuses();
        }
        double fortitude = pc.getTotalBonusTo("SAVE", "Fortitude");
        double will = pc.getTotalBonusTo("SAVE", "Will");
        double reflex = pc.getTotalBonusTo("SAVE", "Reflex");
        double initiative = pc.getTotalBonusTo("COMBAT", "INITIATIVE");
        double intelligence = pc.getTotalBonusTo("STAT", "INT");
        for (int repeat = 0; repeat < 2; repeat++) {
            facade.addTempBonus(effect(facade, false));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SAVE", "Fortitude") == fortitude - 2, "Fortitude penalty");
            require(pc.getTotalBonusTo("SAVE", "Will") == will - 2, "Will penalty");
            require(pc.getTotalBonusTo("SAVE", "Reflex") == reflex, "Reflex unaffected");
            require(pc.getTotalBonusTo("COMBAT", "INITIATIVE") == initiative, "No incidental initiative penalty");
            require(pc.getTotalBonusTo("STAT", "INT") == intelligence, "Does not change intelligence");
            facade.setTempBonusActive(effect(facade, true), false);
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SAVE", "Will") == will, "Unrelated Will saves unaffected while disabled");
            require(pc.getTotalBonusTo("SAVE", "Fortitude") == fortitude, "Unrelated Fortitude saves unaffected while disabled");
            facade.removeTempBonus(effect(facade, true));
            pc.calcActiveBonuses();
            require(pc.getTotalBonusTo("SAVE", "Will") == will, "Removal restores saves");
        }
        sniper(facade, pc);
        monsterLore(facade, pc, reload);
        conditionalSenses(facade, pc, reload);
        capability(facade, pc, reload);
        future(facade, pc, reload);
        if (!reload) {
            var retainedController = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
            var old = ChooserFactory.getDelegate();
            var choice = new RollChoice();
            choice.result = 10;
            ChooserFactory.setDelegate(choice);
            try {
                for (String name : new String[] {"Protection", "Resistance", "Smite"}) {
                    var feat = ability(pcgen.core.AbilityCategory.FEAT, "Precogniscent " + name);
                    retainedController.addAbility(pcgen.core.AbilityCategory.FEAT, feat);
                    require(pc.hasAbilityKeyed(pcgen.core.AbilityCategory.FEAT, feat.getKeyName()), "Retained Precogniscent feat " + name);
                }
                facade.addTempBonus(effect(facade, false, "Divination State - Active Senses"));
            } finally {
                retainedController.closeCharacter();
                ChooserFactory.setDelegate(old);
            }
            facade.addTempBonus(effect(facade, false));
            facade.setTempBonusActive(effect(facade, true), false);
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Save failed");
        }
        System.out.println("SPHERES_GATES_OK: " + args[4]);
        System.exit(0);
    }
}