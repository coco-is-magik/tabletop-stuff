package pcgen.gui2.facade;

import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import pcgen.core.Ability;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.PlayerCharacter;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import pcgen.system.ConsoleUIDelegate;

/** Exercises PCGen's production ability-selection controller, without a GUI. */
class PcgenSpheresGates {
    static class Messages extends ConsoleUIDelegate {
        final List<String> errors = new ArrayList<>();

        @Override
        public void showErrorMessage(String title, String message) {
            errors.add(message);
        }
    }

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    static Ability ability(AbilityCategory category, String key) {
        Ability result = Globals.getContext().getReferenceContext()
                .getManufacturerId(category).getActiveObject(key);
        require(result != null, "Missing ability: " + key);
        return result;
    }

    static void state(PlayerCharacter pc, AbilityCategory category, int count, int spent,
                      CharacterAbilities controller) {
        require(controller.getAbilities(category).getSize() == count, "Wrong selection count");
        require(pc.getTotalAbilityPool(category).subtract(pc.getAvailableAbilityPool(category))
                .compareTo(BigDecimal.valueOf(spent)) == 0, "Wrong spent talent pool");
    }

    static void rejected(CharacterAbilities controller, Messages messages, AbilityCategory category,
                         Ability ability, String messageKey) {
        int before = messages.errors.size();
        controller.addAbility(category, ability);
        require(messages.errors.size() == before + 1, "Expected one rejected-selection message");
        require(messages.errors.get(before).equals(pcgen.system.LanguageBundle.getString(messageKey)),
                "Wrong rejection reason: " + messages.errors.get(before));
        System.out.println("REJECTED: " + ability.getKeyName() + " / " + messageKey);
    }

    static void selection(PlayerCharacter pc) {
        var category = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Spheres Magic Talent");
        require(category != null, "Missing talent category");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var sphere = ability(category, "Destruction Sphere");
            var talents = List.of(ability(category, "Searing Blast"),
                    ability(category, "Epicenter"), ability(category, "Gather Energy"));
            controller.removeAbility(category, talents.get(0));
            controller.removeAbility(category, sphere);
            state(pc, category, 0, 0, controller);
            require(sphere.qualifies(pc, sphere), "Caster must qualify for base sphere");
            for (var talent : talents) {
                require(!talent.qualifies(pc, talent), "Talent qualified without Destruction");
                rejected(controller, messages, category, talent, "InfoAbility.Messages.NotQualified");
                require(!pc.hasAbilityKeyed(category, talent.getKeyName()), "Rejected talent was granted");
                state(pc, category, 0, 0, controller);
            }
            controller.addAbility(category, sphere);
            require(pc.hasAbilityKeyed(category, sphere.getKeyName()), "Base sphere not granted");
            state(pc, category, 1, 1, controller);
            rejected(controller, messages, category, sphere, "InfoAbility.Messages.Duplicate");
            state(pc, category, 1, 1, controller);
            for (var talent : talents) {
                require(talent.qualifies(pc, talent), "Talent not qualified with Destruction");
                int before = messages.errors.size();
                controller.addAbility(category, talent);
                require(messages.errors.size() == before, "Valid talent selection rejected");
                require(pc.hasAbilityKeyed(category, talent.getKeyName()), "Valid talent not granted");
                state(pc, category, 2, 2, controller);
                rejected(controller, messages, category, talent, "InfoAbility.Messages.Duplicate");
                state(pc, category, 2, 2, controller);
                controller.removeAbility(category, talent);
                state(pc, category, 1, 1, controller);
            }
            controller.removeAbility(category, sphere);
            state(pc, category, 0, 0, controller);
            require(!talents.get(0).qualifies(pc, talents.get(0)), "Removal did not revoke prerequisite");
            System.out.println("SPHERES_GATES_OK: prerequisites and duplicates");
        } finally {
            controller.closeCharacter();
        }
    }

    static void core(PlayerCharacter pc, Path output, boolean withSpheres) throws Exception {
        var lines = new ArrayList<String>();
        lines.add("level=" + pc.getTotalLevels());
        lines.add("bab=" + pc.baseAttackBonus());
        for (var stat : pc.getStatSet()) {
            lines.add("stat_" + stat.getKeyName() + "=" + pc.getStat(stat));
            lines.add("mod_" + stat.getKeyName() + "=" + pc.getStatModFor(stat));
        }
        for (var save : List.of("Fortitude", "Reflex", "Will")) {
            lines.add("save_" + save + "=" + pc.getTotalBonusTo("SAVE", save));
        }
        lines.add("ac=" + pc.getTotalBonusTo("COMBAT", "AC"));
        lines.add("feat_pool=" + pc.getTotalAbilityPool(AbilityCategory.FEAT));
        lines.add("feat_available=" + pc.getAvailableAbilityPool(AbilityCategory.FEAT));
        var category = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(AbilityCategory.class, "Spheres Magic Talent");
        if (withSpheres) {
            require(category != null, "Spheres source was not loaded for comparison");
            var favored = SettingsHandler.getGameAsProperty().get().getAbilityCategory("Favored Class");
            var incanterFavored = ability(favored, "Incanter (Spheres Prototype)");
            require(!incanterFavored.qualifies(pc, incanterFavored),
                    "Core Fighter qualified for Incanter favored class");
            require(pc.getTotalAbilityPool(category).signum() == 0, "Core character gained talents");
            require(!pc.hasAbilityKeyed(category, "Destruction Sphere"), "Core character gained sphere");
            var sphere = ability(category, "Destruction Sphere");
            require(!sphere.qualifies(pc, sphere), "Noncaster qualified for Destruction");
            var messages = new Messages();
            var facade = CharacterManager.getCharacters().iterator().next();
            var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
            try {
                rejected(controller, messages, category, sphere, "InfoAbility.Messages.NotQualified");
                state(pc, category, 0, 0, controller);
            } finally {
                controller.closeCharacter();
            }
        } else {
            require(category == null, "Core-only run unexpectedly loaded Spheres category");
        }
        for (var name : List.of("SPHERES_CASTER_LEVEL", "SPHERES_MAGIC_TALENTS", "SPHERES_SPELL_POINTS",
                "SPHERES_COMBAT_TALENTS", "SPHERES_CONSCRIPT_LEVEL", "SPHERES_CONSCRIPT_BONUS_FEATS")) {
            require(pc.getVariableValue(name, "").intValue() == 0, "Core character gained " + name);
        }
        require(!pc.hasAbilityKeyed(SettingsHandler.getGameAsProperty().get().getAbilityCategory("Special Ability"),
                "Spheres Casting Core"), "Core character gained Spheres casting ability");
        lines.sort(String::compareTo);
        Files.write(output, lines);
        System.out.println("SPHERES_GATES_OK: " + (withSpheres ? "core-with-spheres" : "core-only"));
    }

    static void incanter(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var bonus = game.getAbilityCategory("Incanter Bonus Feat");
        var specs = game.getAbilityCategory("Incanter Specialization");
        var feats = AbilityCategory.FEAT;
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            require(pc.getTotalAbilityPool(bonus).intValue() == 1 + level / 2, "Wrong bonus feat progression");
            var originalFeats = pc.getAvailableAbilityPool(feats);
            var originalTalents = pc.getTotalAbilityPool(magic);
            var originalSpellPoints = pc.getVariableValue("SPHERES_SPELL_POINTS", "");
            var extra = ability(feats, "Extra Magic Talent");
            controller.addAbility(bonus, extra);
            require(messages.errors.isEmpty(), "Bonus feat rejected");
            require(pc.getTotalAbilityPool(magic).intValue() == originalTalents.intValue() + 1,
                    "Extra Magic Talent did not grant one talent");
            require(pc.getAvailableAbilityPool(feats).compareTo(originalFeats) == 0,
                    "Class bonus consumed general feat pool");
            if (level == 1) {
                rejected(controller, messages, bonus, ability(feats, "Extra Spell Points"),
                        "InfoAbility.Messages.NoPoints");
            } else {
                controller.addAbility(bonus, extra);
                require(pc.getTotalAbilityPool(magic).intValue() == originalTalents.intValue() + 2,
                        "Repeated Extra Magic Talent did not stack");
                controller.removeAbility(bonus, extra);
            }
            controller.removeAbility(bonus, extra);
            require(pc.getTotalAbilityPool(magic).compareTo(originalTalents) == 0,
                    "Talent grant was not removed");
            var points = ability(feats, "Extra Spell Points");
            controller.addAbility(bonus, points);
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == originalSpellPoints.intValue() + 2,
                    "Spell-point feat did not grant two points");
            controller.removeAbility(bonus, points);
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").equals(originalSpellPoints),
                    "Spell points did not restore");
            if (level == 1) {
                var mysteries = ability(specs, "Master of Mysteries");
                controller.addAbility(specs, mysteries);
                require(pc.hasAbilityKeyed(specs, "Master of Mysteries"), "Specialization not granted");
                require(pc.getAvailableAbilityPool(specs).intValue() == 3, "Wrong specialization cost");
                require(pc.getTotalAbilityPool(bonus).signum() == 0, "Specialization did not forfeit bonus feat");
                var active = game.getAbilityCategory("Incanter Active Specialization");
                var activeMysteries = ability(active, "Active Master of Mysteries");
                controller.addAbility(active, activeMysteries);
                require(pc.getVariableValue("SPHERES_MYSTERIES_ROUNDS", "").intValue() == 5,
                        "Wrong mysteries rounds");
                controller.removeAbility(active, activeMysteries);
                controller.removeAbility(specs, mysteries);
                require(pc.getTotalAbilityPool(bonus).intValue() == 1, "Bonus feat not restored");
                for (String name : List.of("Channel Energy", "Lay on Hands", "Merciful Healer", "Familiar")) {
                    var purchase = ability(specs, name);
                    var activation = ability(active, "Active " + name);
                    rejected(controller, messages, active, activation, "InfoAbility.Messages.NotQualified");
                    controller.addAbility(specs, purchase);
                    controller.addAbility(active, activation);
                    require(pc.hasAbilityKeyed(active, "Active " + name), "Activation failed: " + name);
                    if (name.equals("Channel Energy")) {
                        var channel = game.getAbilityCategory("Incanter Channel Energy");
                        for (String polarity : List.of("Positive", "Negative")) {
                            var choice = ability(game.getAbilityCategory("Special Ability"), "Incanter " + polarity + " Channel");
                            controller.addAbility(channel, choice);
                            require(pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() == 7, "Wrong channel uses");
                            require(pc.getVariableValue("SPHERES_CHANNEL_DICE", "").intValue() == 1, "Wrong channel dice");
                            require(pc.getVariableValue("SPHERES_CHANNEL_DC", "").intValue() == 14, "Wrong channel DC");
                            controller.removeAbility(channel, choice);
                        }
                        controller.addAbility(specs, mysteries);
                        rejected(controller, messages, active, activeMysteries, "InfoAbility.Messages.NoPoints");
                        controller.removeAbility(specs, mysteries);
                    } else if (name.equals("Familiar")) {
                        require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == 1, "Wrong familiar master level");
                    } else if (name.equals("Lay on Hands")) {
                        require(!pc.hasAbilityKeyed(game.getAbilityCategory("Special Ability"), "Incanter Lay on Hands"),
                                "Lay on hands activated before level 2");
                    } else {
                        require(pc.getTotalAbilityPool(game.getAbilityCategory("Mercy")).signum() == 0, "Mercy granted before level 3");
                    }
                    controller.removeAbility(active, activation);
                    controller.removeAbility(specs, purchase);
                    require(pc.getAvailableAbilityPool(specs).intValue() == 5, "Specialization not refunded");
                }
            }
            System.out.println("SPHERES_GATES_OK: incanter" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    static void specializations(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var specs = game.getAbilityCategory("Incanter Specialization");
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var channel = game.getAbilityCategory("Incanter Channel Energy");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            require(pc.getAvailableAbilityPool(specs).signum() == 0, "Five-point purchase budget not consumed");
            require(pc.getTotalAbilityPool(game.getAbilityCategory("Incanter Bonus Feat")).signum() == 0,
                    "Five specialization points must forfeit every bonus feat");
            var healing = ability(active, "Active Merciful Healer");
            var channeling = ability(active, "Active Channel Energy");
            var familiar = ability(active, "Active Familiar");
            controller.addAbility(active, channeling);
            controller.addAbility(active, healing);
            require(messages.errors.isEmpty(), "Two specializations not active by level 3");
            if (level == 3) {
                rejected(controller, messages, active, familiar, "InfoAbility.Messages.NoPoints");
            } else {
                controller.addAbility(active, familiar);
                require(pc.getVariableValue("FamiliarMasterLVL", "").intValue() == level, "Familiar scaling failed");
            }
            var positive = ability(special, "Incanter Positive Channel");
            controller.addAbility(channel, positive);
            require(pc.getVariableValue("SPHERES_CHANNEL_DICE", "").intValue() == (level + 1) / 2, "Channel dice scaling");
            require(pc.getVariableValue("SPHERES_CHANNEL_DC", "").intValue() == 14 + level / 2, "Channel DC scaling");
            rejected(controller, messages, channel, ability(special, "Incanter Negative Channel"), "InfoAbility.Messages.NoPoints");
            var mercy = game.getAbilityCategory("Mercy");
            require(pc.getTotalAbilityPool(mercy).intValue() == level / 3, "Mercy budget scaling");
            var fatigued = ability(special, "Mercy ~ Fatigued");
            controller.addAbility(mercy, fatigued);
            require(pc.hasAbilityKeyed(special, "Mercy ~ Fatigued"), "Existing mercy was not selectable");
            var exhausted = ability(special, "Mercy ~ Exhausted");
            require(exhausted.qualifies(pc, exhausted) == (level >= 9), "Mercy level/prerequisite enforcement");
            controller.removeAbility(mercy, fatigued);
            controller.removeAbility(channel, positive);
            controller.removeAbility(active, healing);
            require(pc.getTotalAbilityPool(mercy).signum() == 0, "Mercy pool removal failed");
            controller.removeAbility(active, channeling);
            require(pc.getTotalAbilityPool(channel).signum() == 0, "Channel choice pool removal failed");
            System.out.println("SPHERES_GATES_OK: specializations" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    static void sphereSpecOwned(PlayerCharacter pc) {
        var game = SettingsHandler.getGameAsProperty().get();
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var pool = game.getAbilityCategory("Incanter Protection Specialization Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            // The character already possessed Protection before taking the specialization.
            require(pc.hasAbilityKeyed(magic, "Protection Sphere"), "Fixture must know Protection");
            require(pc.getAvailableAbilityPool(pool).intValue() == 1,
                    "Already possessing the sphere must grant one talent of it instead");
            require(pc.getVariableValue("SPHERES_CL_PROTECTION", "").intValue() == 2,
                    "The specialization must still add one caster level with the sphere");
            require(ability(magic, "Protection - Buttressing").qualifies(pc,
                    ability(magic, "Protection - Buttressing")),
                    "The replacement talent must come from that sphere");
            require(!ability(magic, "Nature - Deep Nature").qualifies(pc,
                    ability(magic, "Nature - Deep Nature")),
                    "The replacement talent pool must be restricted to that sphere");
            System.out.println("SPHERES_GATES_OK: spherespec-owned");
        } finally {
            controller.closeCharacter();
        }
    }

    static void sphereSpec(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var specs = game.getAbilityCategory("Incanter Specialization");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var natureTalent = ability(magic, "Nature - Deep Nature");
            // Taking the specialization grants the sphere and its caster level, so the
            // sphere's talents satisfy their prerequisites immediately.
            require(pc.hasAbilityKeyed(magic, "Nature Sphere"),
                    "Taking the specialization must grant its sphere as a magic talent");
            require(natureTalent.qualifies(pc, natureTalent),
                    "Granted sphere must satisfy its talents' sphere prerequisite");
            require(pc.getVariableValue("SPHERES_CL_NATURE", "").intValue() == level + 1,
                    "Taking the specialization must add one caster level with its sphere");
            require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == level,
                    "Sphere caster level bonus leaked to general caster level");
            require(pc.getAvailableAbilityPool(specs).intValue() == 2,
                    "Three-point specialization must consume three of the five points");
            require(pc.getAvailableAbilityPool(
                    game.getAbilityCategory("Incanter Nature Specialization Talent")).signum() == 0,
                    "Gaining the sphere must not also grant a free talent");
            var budget = pc.getAvailableAbilityPool(magic);
            // Activating it only brings its specialization abilities into effect.
            var choice = ability(active, "Active Sphere Specialization (Nature)");
            controller.addAbility(active, choice);
            require(messages.errors.isEmpty(), "Generated Nature specialization failed to activate");
            require(pc.getAvailableAbilityPool(magic).equals(budget),
                    "Bonus specialization sphere must not spend a normal talent");
            require(pc.hasAbilityKeyed(special, "Incanter Nature Animal Companion") == (level >= 3),
                    "Nature level 3 ability gate");
            require(pc.hasAbilityKeyed(special, "Incanter Nature Empower Companion") == (level >= 8),
                    "Nature level 8 ability gate");
            require(pc.hasAbilityKeyed(special, "Incanter Nature Life Connection") == (level >= 20),
                    "Nature level 20 ability gate");
            controller.removeAbility(active, choice);
            require(!pc.hasAbilityKeyed(special, "Incanter Nature Animal Companion"),
                    "Nature ability removal failed");
            require(pc.hasAbilityKeyed(magic, "Nature Sphere")
                    && pc.getVariableValue("SPHERES_CL_NATURE", "").intValue() == level + 1,
                    "Sphere and its caster level belong to the taken specialization");
            // Switching away must remove the sphere and its caster level. Specializations
            // are a 1st-level choice (PREVAREQ:SPHERES_INCANTER_LEVEL,1), so the switch
            // can only be exercised at level 1.
            controller.removeAbility(specs, ability(specs, "Sphere Specialization (Nature)"));
            require(!pc.hasAbilityKeyed(magic, "Nature Sphere"),
                    "Switching away must remove the sphere");
            require(!natureTalent.qualifies(pc, natureTalent),
                    "Removed sphere must not satisfy talent prerequisites");
            require(pc.getVariableValue("SPHERES_CL_NATURE", "").intValue() == 0,
                    "Switching away must remove the sphere caster level");
            require(pc.getAvailableAbilityPool(specs).intValue() == 5, "Specialization refund failed");
            if (level == 1) {
                // Switching to another sphere grants that one instead.
                var alterationTalent = ability(magic, "Alteration - Agile");
                controller.addAbility(specs, ability(specs, "Sphere Specialization (Alteration)"));
                require(messages.errors.isEmpty(), "Switching specializations failed: " + messages.errors);
                require(pc.hasAbilityKeyed(magic, "Alteration Sphere"),
                        "Switching must grant the new specialization's sphere");
                require(alterationTalent.qualifies(pc, alterationTalent),
                        "Switched sphere must satisfy its talents' prerequisite");
                require(pc.getVariableValue("SPHERES_CL_ALTERATION", "").intValue() == level + 1,
                        "Switched sphere must gain its caster level");
            }
            System.out.println("SPHERES_GATES_OK: spherespec" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    static void bloodline(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var choice = ability(active, "Active Sorcerer Bloodline (Aberrant)");
            controller.addAbility(active, choice);
            require(messages.errors.isEmpty(), "Bloodline activation rejected");
            require(pc.hasAbilityKeyed(special, "Aberrant Bloodline ~ Acidic Ray"), "Bloodline starting power missing");
            require(pc.hasAbilityKeyed(special, "Aberrant Bloodline ~ Long Limbs") == (level >= 3), "Bloodline level gating");
            require(pc.getVariableValue("Sorcerer_Aberrant_BloodlinePower1LVL", "").intValue() == level, "Bloodline level scaling");
            require(pc.getVariableValue("Sorcerer_Aberrant_BloodlinePower1Times", "").intValue() == 7, "Bloodline casting ability scaling");
            require(!pc.hasAbilityKeyed(special, "Aberrant Bloodline ~ Bloodline Arcana"), "Forbidden arcana granted");
            require(!pc.hasAbilityKeyed(special, "Aberrant Bloodline ~ Bonus Spells"), "Forbidden spells granted");
            require(pc.getTotalAbilityPool(game.getAbilityCategory("Sorcerer Bloodline Feat")).signum() == 0, "Forbidden feat pool granted");
            var specs = game.getAbilityCategory("Incanter Specialization");
            require(!ability(specs, "Sorcerer Bloodline (Fey)").qualifies(pc, ability(specs, "Sorcerer Bloodline (Fey)")),
                    "Second bloodline must not qualify");
            controller.removeAbility(active, choice);
            require(!pc.hasAbilityKeyed(special, "Aberrant Bloodline ~ Acidic Ray"), "Bloodline removal failed");
            var magic = game.getAbilityCategory("Spheres Magic Talent");
            var budget = pc.getTotalAbilityPool(magic);
            var admixture = ability(active, "Active Admixture Adept");
            controller.addAbility(active, admixture);
            require(pc.hasAbilityKeyed(magic, "Admixture"), "Admixture bonus talent missing");
            require(pc.getVariableValue("SPHERES_ADMIXTURE_POINTS", "").intValue() == Math.max(1, level / 2),
                    "Admixture pool scaling");
            require(pc.getTotalAbilityPool(magic).equals(budget), "Bonus talent changed ordinary budget");
            controller.removeAbility(active, admixture);
            require(!pc.hasAbilityKeyed(magic, "Admixture"), "Admixture bonus removal failed");
            System.out.println("SPHERES_GATES_OK: bloodline" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    static void specializationSave(PlayerCharacter pc, String gate) {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            if (gate.equals("healer-save")) {
                var channel = game.getAbilityCategory("Incanter Channel Energy");
                var mercy = game.getAbilityCategory("Mercy");
                controller.addAbility(active, ability(active, "Active Channel Energy"));
                controller.addAbility(active, ability(active, "Active Merciful Healer"));
                require(pc.getTotalAbilityPool(channel).intValue() == 1, "Channel polarity choice missing");
                controller.addAbility(channel, ability(special, "Incanter Positive Channel"));
                require(pc.getTotalAbilityPool(mercy).intValue() == 2, "Mercy progression missing");
                controller.addAbility(mercy, ability(special, "Mercy ~ Fatigued"));
                require(pc.hasAbilityKeyed(special, "Mercy ~ Fatigued"), "Mercy missing before save");
                require(pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() == 7,
                        "Channel uses missing before save");
            } else if (gate.equals("domains-save")) {
                controller.addAbility(active, ability(active, "Active Cleric Domain (Air)"));
                require(pc.hasAbilityKeyed(special, "Domain Power ~ Lightning Arc"), "Air domain power missing before save");
                require(pc.getVariableValue("DomainAirLVL", "").intValue() == 6, "Air domain level missing before save");
            } else {
                controller.addAbility(active, ability(active, "Active Sorcerer Bloodline (Aberrant)"));
                require(pc.hasAbilityKeyed(special, "Aberrant Bloodline ~ Acidic Ray"), "Aberrant power missing before save");
                require(pc.getVariableValue("Sorcerer_Aberrant_BloodlinePower1LVL", "").intValue() == 6,
                        "Aberrant power level missing before save");
            }
            require(messages.errors.isEmpty(), "Specialization selection failed before save");
            System.out.println("SPHERES_GATES_OK: " + gate);
        } finally {
            controller.closeCharacter();
        }
    }

    static void sword(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var tricks = game.getAbilityCategory("Incanter Arsenal Trick");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var choice = ability(active, "Active Sword Birth");
            controller.addAbility(active, choice);
            require(messages.errors.isEmpty(), "Sword Birth activation failed");
            state(pc, active, 1, 2, controller);
            require(pc.getVariableValue("SPHERES_ARENA_RADIUS", "").intValue() == 15 + 5 * (level / 2), "Arena radius");
            require(pc.getVariableValue("SPHERES_ARENA_DC", "").intValue() == 14 + level / 2, "Arena DC");
            require(pc.hasAbilityKeyed(special, "Incanter Enhanced Armory") == (level >= 3), "Armory level gate");
            if (level >= 3) require(pc.getVariableValue("SPHERES_ARENA_ENHANCEMENT", "").intValue() == Math.min(6, level / 3), "Armory enhancement");
            require(pc.getTotalAbilityPool(tricks).intValue() == level / 5, "Arsenal trick progression");
            var feat = ability(AbilityCategory.FEAT, "Extra Arsenal Trick");
            require(feat.qualifies(pc, feat) == (level >= 5), "Extra trick class-feature level gate");
            var featPool = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
            if (level >= 5) {
                require(featPool.signum() > 0, "Fixture needs an available general feat");
                controller.addAbility(AbilityCategory.FEAT, feat);
                require(messages.errors.isEmpty(), "Extra Arsenal Trick rejected");
                require(pc.getTotalAbilityPool(tricks).intValue() == level / 5 + 1,
                        "Extra Arsenal Trick did not increase trick pool");
                require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).intValue() == featPool.intValue() - 1,
                        "Extra Arsenal Trick did not spend a general feat");
                controller.removeAbility(AbilityCategory.FEAT, feat);
                require(pc.getTotalAbilityPool(tricks).intValue() == level / 5,
                        "Extra Arsenal Trick removal did not refund pool");
                require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(featPool),
                        "Extra Arsenal Trick removal did not refund general feat");
                var combat = ability(tricks, "Combat Feat");
                var combatFeats = game.getAbilityCategory("Incanter Arsenal Combat Feat");
                var poolBefore = pc.getTotalAbilityPool(combatFeats);
                var classFeats = game.getAbilityCategory("Incanter Bonus Feat");
                var classPoolBefore = pc.getTotalAbilityPool(classFeats);
                controller.addAbility(tricks, combat);
                require(messages.errors.isEmpty(), "Arsenal Combat Feat rejected");
                if (level >= 20) {
                    controller.addAbility(tricks, combat);
                    require(messages.errors.isEmpty(), "Second Combat Feat trick rejected");
                    require(pc.getTotalAbilityPool(combatFeats).intValue() == poolBefore.intValue() + 2,
                            "Second Combat Feat trick did not grant another feat choice");
                    controller.removeAbility(tricks, combat);
                }
                require(pc.getTotalAbilityPool(combatFeats).intValue() == poolBefore.intValue() + 1,
                        "Arsenal Combat Feat did not grant combat feat choice");
                require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(featPool),
                        "Arsenal Combat Feat spent ordinary feat pool");
                require(pc.getTotalAbilityPool(classFeats).equals(classPoolBefore),
                        "Arsenal Combat Feat changed Incanter bonus feat pool");
                var powerAttack = ability(AbilityCategory.FEAT, "Power Attack");
                require(!powerAttack.qualifies(pc, powerAttack),
                        "Strength 10 fixture must not qualify for Power Attack");
                rejected(controller, messages, combatFeats, powerAttack, "InfoAbility.Messages.NotQualified");
                require(pc.getAvailableAbilityPool(combatFeats).intValue() == poolBefore.intValue() + 1,
                        "Invalid arsenal feat selection spent a combat feat choice");
                var initiative = ability(AbilityCategory.FEAT, "Improved Initiative");
                int errorsBeforeChoice = messages.errors.size();
                controller.addAbility(combatFeats, initiative);
                require(messages.errors.size() == errorsBeforeChoice,
                        "Arsenal combat feat choice rejected");
                require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"),
                        "Arsenal combat feat did not grant the chosen feat");
                require(pc.getAvailableAbilityPool(combatFeats).intValue() == poolBefore.intValue(),
                        "Arsenal feat choice did not spend its own pool");
                rejected(controller, messages, combatFeats, initiative, "InfoAbility.Messages.NoPoints");
                controller.removeAbility(combatFeats, initiative);
                require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"),
                        "Arsenal combat feat choice removal failed");
                controller.removeAbility(tricks, combat);
                require(pc.getTotalAbilityPool(combatFeats).equals(poolBefore),
                        "Arsenal Combat Feat removal did not refund combat feat pool");
            }
            var ultimate = ability(tricks, "Ultimate Arena");
            require(!ultimate.qualifies(pc, ultimate), "Ultimate Arena missing prerequisites must fail");
            if (level >= 5) {
                var burst = ability(tricks, "Arena Burst");
                controller.addAbility(tricks, burst);
                require(pc.getVariableValue("SPHERES_ARENA_BURST_DICE", "").intValue() == level, "Burst scaling");
                if (level == 5) {
                    rejected(controller, messages, tricks, ability(tricks, "Friendly Arena"), "InfoAbility.Messages.NoPoints");
                } else {
                    var bound = ability(tricks, "Bound Armory");
                    controller.addAbility(tricks, bound);
                    require(ultimate.qualifies(pc, ultimate), "Ultimate Arena valid prerequisites rejected");
                    controller.addAbility(tricks, ultimate);
                    require(pc.getVariableValue("SPHERES_BOUND_ARMORY_BUDGET", "").intValue() == 10, "Bound budget");
                    controller.removeAbility(tricks, ultimate);
                    controller.removeAbility(tricks, bound);
                }
                controller.removeAbility(tricks, burst);
            }
            controller.removeAbility(active, choice);
            require(pc.getTotalAbilityPool(tricks).signum() == 0, "Trick pool removal");
            require(pc.getTotalAbilityPool(game.getAbilityCategory("Incanter Arsenal Combat Feat")).signum() == 0,
                    "Arsenal combat feat pool survived Sword Birth removal");
            require(!feat.qualifies(pc, feat), "Extra Arsenal Trick qualified without active Sword Birth");
            require(!pc.hasAbilityKeyed(special, "Incanter Armory Arena"), "Arena removal");
            System.out.println("SPHERES_GATES_OK: sword" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    static void swordSave(PlayerCharacter pc) throws Exception {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var tricks = game.getAbilityCategory("Incanter Arsenal Trick");
        var combatFeats = game.getAbilityCategory("Incanter Arsenal Combat Feat");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            controller.addAbility(active, ability(active, "Active Sword Birth"));
            controller.addAbility(tricks, ability(tricks, "Combat Feat"));
            controller.addAbility(combatFeats, ability(AbilityCategory.FEAT, "Improved Initiative"));
            require(messages.errors.isEmpty(), "Sword Birth save fixture selections rejected");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Improved Initiative"),
                    "Sword Birth save fixture missing bonus feat");
            require(pc.getTotalAbilityPool(combatFeats).intValue() == 1,
                    "Sword Birth save fixture missing feat pool");
            System.out.println("SPHERES_GATES_OK: sword-save");
        } finally {
            controller.closeCharacter();
        }
    }

    static void talentFavored(PlayerCharacter pc, boolean halfElf, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var baseline = pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue();
            var human = ability(rewards, halfElf ? "Incanter Half-Elf Magic Talent" : "Incanter Human Magic Talent");
            require(!human.qualifies(pc, human), "Favored bonus qualified before choosing Incanter");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Cannot favor Incanter");
            require(pc.getTotalAbilityPool(rewards).intValue() == 6, "Expected exactly six favored class rewards");
            var wrongRace = ability(rewards, halfElf ? "Incanter Human Magic Talent" : "Incanter Half-Elf Magic Talent");
            require(!wrongRace.qualifies(pc, wrongRace), "Wrong-race favored class reward qualified");
            var tiefling = ability(rewards, "Incanter Tiefling Concentration");
            require(!tiefling.qualifies(pc, tiefling), "Tiefling reward qualified for non-Tiefling");
            for (int i = 1; i <= 6; i++) {
                int priorErrors = messages.errors.size();
                controller.addAbility(rewards, human);
                require(messages.errors.size() == priorErrors, "Human favored class reward rejected");
                require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == baseline + i / 6,
                        "Human favored class talent before/after sixth pick");
            }
            if (save) {
                System.out.println("SPHERES_GATES_OK: human-favored-save");
                return;
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, human);
                require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == baseline + i / 6,
                        "Human favored class removal did not refund talent");
            }
            controller.removeAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(pc.getTotalAbilityPool(rewards).signum() == 0, "Favored class reward pool not removed");
            System.out.println("SPHERES_GATES_OK: " + (halfElf ? "half-elf-favored" : "human-favored"));
        } finally {
            controller.closeCharacter();
        }
    }

    static void halfOrcFavored(PlayerCharacter pc, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var reward = ability(rewards, "Incanter Half-Orc Bloodline Power");
            require(!reward.qualifies(pc, reward), "Half-Orc bloodline reward qualified before choosing Incanter");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Half-Orc could not favor Incanter");
            require(!reward.qualifies(pc, reward), "Half-Orc reward qualified without active bloodline");
            controller.addAbility(active, ability(active, "Active Sorcerer Bloodline (Aberrant)"));
            require(messages.errors.isEmpty(), "Half-Orc bloodline activation rejected");
            require(reward.qualifies(pc, reward), "Half-Orc reward not qualified with bloodline");
            int strength = pc.getVariableValue("BloodlineLVL", "").intValue();
            int progression = pc.getVariableValue("BloodlineProgressionLVL", "").intValue();
            for (int i = 1; i <= 5; i++) {
                controller.addAbility(rewards, reward);
                require(messages.errors.isEmpty(), "Half-Orc reward rejected");
                require(pc.getVariableValue("BloodlineLVL", "").intValue() == strength + i / 5,
                        "Bloodline strength did not advance once per five selections");
                require(pc.getVariableValue("BloodlineProgressionLVL", "").intValue() == progression,
                        "Half-Orc bonus unlocked bloodline powers early");
            }
            if (save) {
                System.out.println("SPHERES_GATES_OK: half-orc-favored-save");
                return;
            }
            for (int i = 4; i >= 0; i--) {
                controller.removeAbility(rewards, reward);
                require(pc.getVariableValue("BloodlineLVL", "").intValue() == strength + i / 5,
                        "Half-Orc bonus did not refund on removal");
            }
            System.out.println("SPHERES_GATES_OK: half-orc-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void elfFavored(PlayerCharacter pc) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var metamagic = game.getAbilityCategory("Incanter Elf Favored Metamagic");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var elf = ability(rewards, "Incanter Elf Metamagic Feat");
            require(!elf.qualifies(pc, elf), "Elf favored bonus qualified before choosing Incanter");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Cannot favor Incanter as Elf");
            require(elf.qualifies(pc, elf), "Elf favored bonus did not qualify");
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, elf);
                require(messages.errors.isEmpty(), "Elf favored bonus rejected");
                require(pc.getTotalAbilityPool(metamagic).intValue() == i / 6,
                        "Elf metamagic feat granted before/after sixth reward");
            }
            var extend = ability(AbilityCategory.FEAT, "Extend Spell");
            var generalPool = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
            controller.addAbility(metamagic, extend);
            require(messages.errors.isEmpty(), "Elf favored metamagic feat choice rejected");
            require(pc.hasAbilityKeyed(AbilityCategory.FEAT, "Extend Spell"),
                    "Elf favored metamagic feat not granted");
            require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(generalPool),
                    "Elf favored metamagic feat spent general feat pool");
            controller.removeAbility(metamagic, extend);
            require(!pc.hasAbilityKeyed(AbilityCategory.FEAT, "Extend Spell"),
                    "Elf favored metamagic feat removal failed");
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, elf);
                require(pc.getTotalAbilityPool(metamagic).intValue() == i / 6,
                        "Elf metamagic feat not refunded");
            }
            System.out.println("SPHERES_GATES_OK: elf-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void dwarfFavored(PlayerCharacter pc) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var crafting = game.getAbilityCategory("Incanter Dwarf Favored Crafting");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var dwarf = ability(rewards, "Incanter Dwarf Item Creation Feat");
            require(!dwarf.qualifies(pc, dwarf), "Dwarf reward qualified without favored class");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Cannot favor Incanter as Dwarf");
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, dwarf);
                require(messages.errors.isEmpty(), "Dwarf reward rejected");
                require(pc.getTotalAbilityPool(crafting).intValue() == i / 6,
                        "Dwarf crafting feat before/after sixth selection");
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, dwarf);
                require(pc.getTotalAbilityPool(crafting).intValue() == i / 6,
                        "Dwarf crafting feat refund failed");
            }
            System.out.println("SPHERES_GATES_OK: dwarf-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void aasimarFavored(PlayerCharacter pc, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var aasimar = ability(rewards, "Incanter Aasimar Spellcraft");
            var human = ability(rewards, "Incanter Human Magic Talent");
            require(!aasimar.qualifies(pc, aasimar), "Aasimar reward qualified without favored class");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Cannot favor Incanter as Aasimar");
            require(!human.qualifies(pc, human), "Human reward qualified as Aasimar");
            double baseline = pc.getTotalBonusTo("SKILL", "Spellcraft");
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, aasimar);
                require(messages.errors.isEmpty(), "Aasimar reward rejected");
                require(pc.getTotalBonusTo("SKILL", "Spellcraft") == baseline + i / 2,
                        "Aasimar Spellcraft bonus before/after second selection");
            }
            if (save) {
                require(pc.getVariableValue("SPHERES_INCANTER_AASIMAR_FCB_COUNT", "").intValue() == 6,
                        "Aasimar reward count before saving");
                System.out.println("SPHERES_GATES_OK: aasimar-favored-save");
                return;
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, aasimar);
                require(pc.getTotalBonusTo("SKILL", "Spellcraft") == baseline + i / 2,
                        "Aasimar Spellcraft bonus removal failed");
            }
            System.out.println("SPHERES_GATES_OK: aasimar-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void tieflingFavored(PlayerCharacter pc, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var tiefling = ability(rewards, "Incanter Tiefling Concentration");
            require(!tiefling.qualifies(pc, tiefling), "Tiefling bonus qualified before favoring Incanter");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Cannot favor Incanter as Tiefling");
            require(!ability(rewards, "Incanter Human Magic Talent").qualifies(pc,
                    ability(rewards, "Incanter Human Magic Talent")), "Human bonus qualified for Tiefling");
            int baseline = pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue();
            require(baseline == pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue()
                    + pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue(),
                    "Concentration must start at caster level plus casting ability; got " + baseline);
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, tiefling);
                require(messages.errors.isEmpty(), "Tiefling favored class bonus rejected");
                require(pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue() == baseline + i / 2,
                        "Tiefling concentration bonus must accumulate every two picks");
            }
            if (save) {
                System.out.println("SPHERES_GATES_OK: tiefling-favored-save");
                return;
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, tiefling);
                require(pc.getVariableValue("SPHERES_CONCENTRATION_CHECK", "").intValue() == baseline + i / 2,
                        "Tiefling concentration bonus did not refund on removal");
            }
            System.out.println("SPHERES_GATES_OK: tiefling-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void halflingFavored(PlayerCharacter pc, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var channel = game.getAbilityCategory("Incanter Channel Energy");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var reward = ability(rewards, "Incanter Halfling Channel Uses");
            require(!reward.qualifies(pc, reward), "Halfling channel bonus available without channel");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Halfling could not favor Incanter");
            require(!reward.qualifies(pc, reward), "Halfling channel bonus available before channel choice");
            var activation = ability(active, "Active Channel Energy");
            controller.addAbility(active, activation);
            var positive = ability(channel, "Incanter Positive Channel");
            controller.addAbility(channel, positive);
            require(messages.errors.isEmpty(), "Halfling channel choice rejected");
            require(reward.qualifies(pc, reward), "Halfling channel bonus not available after channel choice");
            int uses = pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue();
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, reward);
                require(messages.errors.isEmpty(), "Halfling reward rejected");
                require(pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() == uses + i / 2,
                        "Halfling channel uses incorrect after selection");
            }
            if (save) {
                System.out.println("SPHERES_GATES_OK: halfling-favored-save");
                return;
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, reward);
                require(pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() == uses + i / 2,
                        "Halfling channel uses incorrect after removal");
            }
            controller.removeAbility(channel, positive);
            require(!reward.qualifies(pc, reward), "Halfling channel bonus available after removing channel");
            controller.removeAbility(active, activation);
            System.out.println("SPHERES_GATES_OK: halfling-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void favoredBurst(PlayerCharacter pc, boolean save, boolean orc) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var reward = ability(rewards, orc ? "Incanter Orc Movement Burst Uses" : "Incanter Halfling Movement Burst Uses");
            require(!reward.qualifies(pc, reward), "Burst reward available before favored class");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Could not favor Incanter");
            var wrongRace = ability(rewards, orc ? "Incanter Halfling Movement Burst Uses" : "Incanter Orc Movement Burst Uses");
            require(!wrongRace.qualifies(pc, wrongRace), "Other race's Burst reward qualified");
            require(!reward.qualifies(pc, reward), "Burst reward available without Destruction specialization");
            var activation = ability(active, "Active Sphere Specialization (Destruction)");
            controller.addAbility(active, activation);
            require(messages.errors.isEmpty(), "Destruction activation rejected");
            require(reward.qualifies(pc, reward), "Burst reward unavailable after activation");
            int baseline = pc.getVariableValue("SPHERES_MOVEMENT_BURST_USES", "").intValue();
            int channel = pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue();
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, reward);
                require(messages.errors.isEmpty(), "Burst reward rejected");
                require(pc.getVariableValue("SPHERES_MOVEMENT_BURST_USES", "").intValue() == baseline + i / 2,
                        "Burst daily uses incorrect after selection");
                require(pc.getVariableValue("SPHERES_CHANNEL_USES", "").intValue() == channel,
                        "Burst reward changed channel daily uses");
            }
            if (save) {
                System.out.println("SPHERES_GATES_OK: " + (orc ? "orc" : "halfling") + "-burst-save");
                return;
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, reward);
                require(pc.getVariableValue("SPHERES_MOVEMENT_BURST_USES", "").intValue() == baseline + i / 2,
                        "Burst daily uses incorrect after removal");
            }
            controller.removeAbility(active, activation);
            require(!reward.qualifies(pc, reward), "Burst reward available after removing activation");
            System.out.println("SPHERES_GATES_OK: " + (orc ? "orc" : "halfling") + "-burst");
        } finally {
            controller.closeCharacter();
        }
    }

    static void orcAirFavored(PlayerCharacter pc, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var reward = ability(rewards, "Incanter Orc Lightning Arc Uses");
            require(!reward.qualifies(pc, reward), "Air reward available before favored class");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(!reward.qualifies(pc, reward), "Air reward available before domain activation");
            controller.addAbility(active, ability(active, "Active Cleric Domain (Air)"));
            require(messages.errors.isEmpty(), "Could not activate Air domain");
            require(pc.hasAbilityKeyed(special, "Domain Power ~ Lightning Arc"), "Air power not granted");
            require(reward.qualifies(pc, reward), "Air reward unavailable after activation");
            int baseline = pc.getVariableValue("LightningArcTimes", "").intValue();
            int burst = pc.getVariableValue("SPHERES_MOVEMENT_BURST_FAVORED_USES", "").intValue();
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, reward);
                require(messages.errors.isEmpty(), "Air reward rejected");
                require(pc.getVariableValue("LightningArcTimes", "").intValue() == baseline + i / 2,
                        "Lightning Arc uses did not accumulate fractionally");
                require(pc.getVariableValue("SPHERES_MOVEMENT_BURST_FAVORED_USES", "").intValue() == burst,
                        "Air reward changed Movement Burst");
            }
            if (!save) {
                for (int i = 5; i >= 0; i--) {
                    controller.removeAbility(rewards, reward);
                    require(pc.getVariableValue("LightningArcTimes", "").intValue() == baseline + i / 2,
                            "Lightning Arc uses did not refund");
                }
                controller.removeAbility(active, ability(active, "Active Cleric Domain (Air)"));
                require(!reward.qualifies(pc, reward), "Air reward qualified after removing domain");
            }
            System.out.println("SPHERES_GATES_OK: orc-air-favored" + (save ? "-save" : ""));
        } finally {
            controller.closeCharacter();
        }
    }

    static void gnomeFavored(PlayerCharacter pc, boolean save) {
        var game = SettingsHandler.getGameAsProperty().get();
        var favored = game.getAbilityCategory("Favored Class");
        var rewards = game.getAbilityCategory("Favored Class Bonus");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var gnome = ability(rewards, "Incanter Gnome Destruction DC");
            require(!gnome.qualifies(pc, gnome), "Gnome bonus qualified before favoring Incanter");
            controller.addAbility(favored, ability(favored, "Incanter (Spheres Prototype)"));
            require(messages.errors.isEmpty(), "Cannot favor Incanter as Gnome");
            var sphere = ability(magic, "Destruction Sphere");
            controller.removeAbility(magic, sphere);
            require(!gnome.qualifies(pc, gnome), "Gnome bonus qualified without Destruction sphere");
            controller.addAbility(magic, sphere);
            require(messages.errors.isEmpty(), "Gnome could not restore Destruction sphere");
            require(gnome.qualifies(pc, gnome), "Gnome Destruction bonus did not qualify");
            int dc = pc.getVariableValue("SPHERES_DC_DESTRUCTION", "").intValue();
            int casterLevel = pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue();
            for (int i = 1; i <= 6; i++) {
                controller.addAbility(rewards, gnome);
                require(messages.errors.isEmpty(), "Gnome favored class reward rejected");
                require(pc.getVariableValue("SPHERES_DC_DESTRUCTION", "").intValue() == dc + i / 6,
                        "Gnome bonus applied before/after six selections");
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == casterLevel,
                        "Gnome bonus changed general caster level");
            }
            if (save) {
                System.out.println("SPHERES_GATES_OK: gnome-favored-save");
                return;
            }
            for (int i = 5; i >= 0; i--) {
                controller.removeAbility(rewards, gnome);
                require(pc.getVariableValue("SPHERES_DC_DESTRUCTION", "").intValue() == dc + i / 6,
                        "Gnome favored class reward not refunded");
            }
            System.out.println("SPHERES_GATES_OK: gnome-favored");
        } finally {
            controller.closeCharacter();
        }
    }

    static void destruction(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            require(pc.hasAbilityKeyed(magic, "Destruction Sphere"),
                    "Taking the specialization must grant its sphere");
            require(pc.getVariableValue("SPHERES_CL_DESTRUCTION", "").intValue() == level + 1,
                    "Taking the specialization must add one caster level with its sphere");
            var budget = pc.getAvailableAbilityPool(magic);
            var choice = ability(active, "Active Sphere Specialization (Destruction)");
            controller.addAbility(active, choice);
            require(messages.errors.isEmpty(), "Three-point specialization must activate at level one");
            state(pc, active, 1, 2, controller);
            require(pc.hasAbilityKeyed(magic, "Destruction Sphere"), "Bonus sphere missing");
            require(pc.getAvailableAbilityPool(magic).equals(budget), "Bonus sphere spent normal talent");
            require(pc.getVariableValue("SPHERES_CL_DESTRUCTION", "").intValue() == level + 1, "Sphere CL bonus missing");
            require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == level, "Sphere bonus leaked to general CL");
            require(pc.hasAbilityKeyed(special, "Incanter Intense Magic"), "Intense Magic starting grant");
            require(pc.getVariableValue("SPHERES_INTENSE_MAGIC_DAMAGE", "").intValue() == Math.max(1, level / 2), "Damage scaling");
            require(pc.hasAbilityKeyed(special, "Incanter Movement Burst"), "Movement Burst starting grant");
            require(pc.getVariableValue("SPHERES_MOVEMENT_BURST_FEET", "").intValue() == 20 + 5 * (level / 2), "Movement Burst distance");
            require(pc.getVariableValue("SPHERES_MOVEMENT_BURST_USES", "").intValue() == 7, "Movement Burst uses");
            require(pc.hasAbilityKeyed(special, "Incanter Elemental Wall") == (level >= 8), "Elemental Wall level gate");
            if (level >= 8) {
                require(pc.getVariableValue("SPHERES_ELEMENTAL_WALL_ROUNDS", "").intValue() == level, "Elemental Wall rounds");
                require(pc.getVariableValue("SPHERES_ELEMENTAL_WALL_LENGTH", "").intValue() == 20 * level, "Elemental Wall length");
                require(pc.getVariableValue("SPHERES_ELEMENTAL_WALL_RADIUS", "").intValue() == 5 * (level / 2), "Elemental Wall radius");
                require(pc.getVariableValue("SPHERES_ELEMENTAL_WALL_PASS_DAMAGE", "").intValue() == Math.min(20, level), "Elemental Wall damage");
            }
            require(!pc.hasAbilityKeyed(special, "Incanter Penetrating Blast"), "Original-only Penetrating Blast granted");
            require(!pc.hasAbilityKeyed(special, "Incanter Indestructible"), "Original-only Indestructible granted");
            rejected(controller, messages, active, choice, "InfoAbility.Messages.Duplicate");
            controller.removeAbility(active, choice);
            require(pc.hasAbilityKeyed(magic, "Destruction Sphere"),
                    "Sphere must persist with the taken specialization");
            require(pc.getVariableValue("SPHERES_CL_DESTRUCTION", "").intValue() == level + 1,
                    "Caster level must persist with the taken specialization");
            var specs = game.getAbilityCategory("Incanter Specialization");
            controller.removeAbility(specs, ability(specs, "Sphere Specialization (Destruction)"));
            require(!pc.hasAbilityKeyed(magic, "Destruction Sphere"),
                    "Sphere must leave with its specialization");
            require(pc.getVariableValue("SPHERES_CL_DESTRUCTION", "").intValue() == level, "CL removal failed");
            require(!pc.hasAbilityKeyed(special, "Incanter Intense Magic"), "Intense Magic removal failed");
            require(!pc.hasAbilityKeyed(special, "Incanter Movement Burst"), "Movement Burst removal failed");
            require(!pc.hasAbilityKeyed(special, "Incanter Elemental Wall"), "Elemental Wall removal failed");
            System.out.println("SPHERES_GATES_OK: destruction" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    static void domains(PlayerCharacter pc, int level) {
        var game = SettingsHandler.getGameAsProperty().get();
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var special = game.getAbilityCategory("Special Ability");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var air = ability(active, "Active Cleric Domain (Air)");
            var fire = ability(active, "Active Cleric Domain (Fire)");
            controller.addAbility(active, air);
            controller.addAbility(active, fire);
            require(messages.errors.isEmpty(), "Paired one-point domains must activate together");
            require(pc.hasAbilityKeyed(special, "Domain Power ~ Lightning Arc"), "Air power missing");
            require(pc.hasAbilityKeyed(special, "Domain Power ~ Fire Bolt"), "Fire power missing");
            for (String name : List.of("Air", "Fire")) {
                require(pc.getVariableValue("Domain" + name + "LVL", "").intValue() == level,
                        "Domain levels stacked across distinct domains");
                require(pc.getVariableValue("Domain" + name + "DC", "").intValue() == 14 + level / 2,
                        "Domain DC must use casting modifier");
                require(pc.getVariableValue("Domain" + name + "Times", "").intValue() == 7,
                        "Domain uses must use casting modifier");
            }
            require(pc.hasAbilityKeyed(special, "Immunity to Electricity") == (level == 20),
                    "Air capstone activation");
            require(pc.hasAbilityKeyed(special, "Immunity to Fire") == (level == 20),
                    "Fire capstone activation");
            rejected(controller, messages, active, air, "InfoAbility.Messages.Duplicate");
            controller.removeAbility(active, air);
            require(!pc.hasAbilityKeyed(special, "Domain Power ~ Lightning Arc"), "Removed domain still grants power");
            require(pc.hasAbilityKeyed(special, "Domain Power ~ Fire Bolt"), "Removing Air removed Fire");
            require(pc.getVariableValue("DomainFireLVL", "").intValue() == level, "Remaining domain level changed");
            controller.removeAbility(active, fire);
            require(!pc.hasAbilityKeyed(special, "Domain Power ~ Fire Bolt"), "Fire removal failed");
            System.out.println("SPHERES_GATES_OK: domains" + level);
        } finally {
            controller.closeCharacter();
        }
    }

    // Thin class acceptance: no sphere, domain, bloodline or companion catalog required.
    static void classContract(PlayerCharacter pc, boolean reload) {
        var game = SettingsHandler.getGameAsProperty().get();
        var bonus = game.getAbilityCategory("Incanter Bonus Feat");
        var specs = game.getAbilityCategory("Incanter Specialization");
        var active = game.getAbilityCategory("Incanter Active Specialization");
        var magic = game.getAbilityCategory("Spheres Magic Talent");
        int level = pc.getTotalLevels();
        int points = pc.getVariableValue("SPHERES_INCANTER_SPECIALIZATION_POINTS", "").intValue();
        int[][] lost = {{}, {1, 10, 20}, {1, 6, 10, 14, 20},
                {1, 2, 6, 10, 14, 18, 20}, {1, 2, 6, 8, 10, 14, 16, 18, 20},
                {1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20}};
        int feats = 1 + level / 2;
        for (int threshold : lost[points]) {
            if (level >= threshold) feats--;
        }
        require(pc.getTotalAbilityPool(bonus).intValue() == feats, "Class forfeiture table mismatch");
        require(pc.getAvailableAbilityPool(specs).intValue() == 5 - points, "Class purchase budget mismatch");
        require(pc.getTotalAbilityPool(active).intValue() == 2 * ((level + 1) / 2), "Activation progression mismatch");
        for (String variable : List.of("SPHERES_INCANTER_LEVEL", "SPHERES_CASTER_LEVEL", "SPHERES_MAGIC_SKILL_BONUS")) {
            require(pc.getVariableValue(variable, "").intValue() == level, variable);
        }
        require(pc.getVariableValue("SPHERES_CASTING_ABILITY", "").intValue() == 4, "Casting choice not restored");
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        try {
            var talent = ability(AbilityCategory.FEAT, "Extra Magic Talent");
            var spellPoints = ability(AbilityCategory.FEAT, "Extra Spell Points");
            var mysteries = ability(active, "Active Master of Mysteries");
            boolean ownsMysteries = pc.hasAbilityKeyed(specs, "Master of Mysteries");
            var generalFeats = pc.getAvailableAbilityPool(AbilityCategory.FEAT);
            if (!reload) {
                require(pc.getAvailableAbilityPool(bonus).intValue() == feats, "Fresh bonus pool already spent");
                if (feats > 0) controller.addAbility(bonus, talent);
                if (feats > 1) controller.addAbility(bonus, spellPoints);
                if (ownsMysteries) controller.addAbility(active, mysteries);
            }
            require(messages.errors.isEmpty(), "Class selections rejected");
            require(pc.getTotalAbilityPool(magic).intValue() == 2 + level + (level + 1) / 2 + (feats > 0 ? 1 : 0),
                    "Class talent progression or saved bonus feat mismatch");
            require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == level + 4 + (feats > 1 ? 2 : 0),
                    "Class spell pool or saved bonus feat mismatch");
            require(pc.getAvailableAbilityPool(bonus).intValue() == Math.max(0, feats - 2), "Saved bonus feat spending mismatch");
            require(pc.getAvailableAbilityPool(AbilityCategory.FEAT).equals(generalFeats), "Class feat leaked into general pool");
            require(pc.hasAbilityKeyed(active, "Active Master of Mysteries") == ownsMysteries, "Class grant not restored");
            if (ownsMysteries) {
                require(pc.getVariableValue("SPHERES_MYSTERIES_ROUNDS", "").intValue() == level + 4, "Class feature resource mismatch");
            }
            if (reload) {
                if (ownsMysteries) controller.removeAbility(active, mysteries);
                if (feats > 0) controller.removeAbility(bonus, talent);
                if (feats > 1) controller.removeAbility(bonus, spellPoints);
                for (String name : List.of("Familiar", "Master of Mysteries", "Channel Energy", "Sphere Specialization (Destruction)")) {
                    if (pc.hasAbilityKeyed(specs, name)) controller.removeAbility(specs, ability(specs, name));
                }
                require(pc.getAvailableAbilityPool(specs).intValue() == 5, "Purchase refund failed after reload");
                require(pc.getAvailableAbilityPool(bonus).intValue() == 1 + level / 2, "Forfeiture refund failed after reload");
                require(pc.getTotalAbilityPool(magic).intValue() == 2 + level + (level + 1) / 2, "Talent refund failed after reload");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == level + 4, "Spell pool refund failed after reload");
                require(pc.getVariableValue("SPHERES_MYSTERIES_ROUNDS", "").intValue() == 0, "Removed feature retained resources");
            }
            System.out.println("SPHERES_GATES_OK: class-" + (reload ? "reload" : "save"));
        } finally {
            controller.closeCharacter();
        }
    }

    public static void main(String[] args) throws Exception {
        require(args.length == 5 || (args.length == 6 && (args[4].equals("class-save") || args[4].equals("sword-save")
                || args[4].equals("human-favored-save") || args[4].equals("aasimar-favored-save")
                || args[4].equals("tiefling-favored-save") || args[4].equals("gnome-favored-save")
                || args[4].equals("halfling-favored-save") || args[4].equals("halfling-burst-save")
                || args[4].equals("orc-burst-save") || args[4].equals("orc-air-favored-save")
                || args[4].equals("domains-save")
                || args[4].equals("bloodline-save") || args[4].equals("healer-save")
                || args[4].equals("half-orc-favored-save"))),
                "character template output config gate [save] required");
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]),
                "Initial PCGen load/export failed");
        require(Globals.getPCList().size() == 1, "Expected one character");
        var pc = Globals.getPCList().get(0);
        switch (args[4]) {
            case "class-save": classContract(pc, false); break;
            case "class-reload": classContract(pc, true); break;
            case "selection": selection(pc); break;
            case "incanter1": incanter(pc, 1); break;
            case "incanter20": incanter(pc, 20); break;
            case "specializations3": specializations(pc, 3); break;
            case "specializations20": specializations(pc, 20); break;
            case "spherespec-owned": sphereSpecOwned(pc); break;
            case "spherespec1": sphereSpec(pc, 1); break;
            case "spherespec3": sphereSpec(pc, 3); break;
            case "spherespec20": sphereSpec(pc, 20); break;
            case "domains1": domains(pc, 1); break;
            case "domains20": domains(pc, 20); break;
            case "bloodline1": bloodline(pc, 1); break;
            case "bloodline20": bloodline(pc, 20); break;
            case "bloodline-save": specializationSave(pc, args[4]); break;
            case "domains-save": specializationSave(pc, args[4]); break;
            case "healer-save": specializationSave(pc, args[4]); break;
            case "destruction1": destruction(pc, 1); break;
            case "destruction3": destruction(pc, 3); break;
            case "destruction8": destruction(pc, 8); break;
            case "destruction20": destruction(pc, 20); break;
            case "sword1": sword(pc, 1); break;
            case "sword5": sword(pc, 5); break;
            case "sword20": sword(pc, 20); break;
            case "sword-save": swordSave(pc); break;
            case "human-favored": talentFavored(pc, false, false); break;
            case "half-elf-favored": talentFavored(pc, true, false); break;
            case "half-orc-favored": halfOrcFavored(pc, false); break;
            case "half-orc-favored-save": halfOrcFavored(pc, true); break;
            case "elf-favored": elfFavored(pc); break;
            case "dwarf-favored": dwarfFavored(pc); break;
            case "aasimar-favored": aasimarFavored(pc, false); break;
            case "aasimar-favored-save": aasimarFavored(pc, true); break;
            case "tiefling-favored": tieflingFavored(pc, false); break;
            case "tiefling-favored-save": tieflingFavored(pc, true); break;
            case "gnome-favored": gnomeFavored(pc, false); break;
            case "gnome-favored-save": gnomeFavored(pc, true); break;
            case "halfling-favored": halflingFavored(pc, false); break;
            case "halfling-favored-save": halflingFavored(pc, true); break;
            case "halfling-burst": favoredBurst(pc, false, false); break;
            case "halfling-burst-save": favoredBurst(pc, true, false); break;
            case "orc-burst": favoredBurst(pc, false, true); break;
            case "orc-burst-save": favoredBurst(pc, true, true); break;
            case "orc-air-favored": orcAirFavored(pc, false); break;
            case "orc-air-favored-save": orcAirFavored(pc, true); break;
            case "human-favored-save": talentFavored(pc, false, true); break;
            case "core-only": core(pc, Path.of(args[2] + ".snapshot"), false); break;
            case "core-with-spheres": core(pc, Path.of(args[2] + ".snapshot"), true); break;
            default: throw new IllegalArgumentException("Unknown gate: " + args[4]);
        }
        if (args[4].equals("class-save") || args[4].equals("sword-save") || args[4].equals("human-favored-save")
                || args[4].equals("aasimar-favored-save") || args[4].equals("tiefling-favored-save")
                || args[4].equals("gnome-favored-save") || args[4].equals("halfling-favored-save")
                || args[4].equals("halfling-burst-save") || args[4].equals("orc-burst-save")
                || args[4].equals("orc-air-favored-save")
                || args[4].equals("domains-save") || args[4].equals("bloodline-save")
                || args[4].equals("healer-save") || args[4].equals("half-orc-favored-save")) {
            require(args.length == 6, "Specialized character save path required");
            var facade = CharacterManager.getCharacters().iterator().next();
            facade.setFile(Path.of(args[5]).toFile());
            require(CharacterManager.saveCharacter(facade), "Sword Birth character save failed");
        }
        System.exit(0);
    }
}