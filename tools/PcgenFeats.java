package pcgen.gui2.facade;

import java.nio.file.Path;
import java.math.BigDecimal;
import pcgen.core.AbilityCategory;
import pcgen.core.Globals;
import pcgen.core.SettingsHandler;
import pcgen.system.CharacterManager;
import static pcgen.gui2.facade.PcgenSpheresGates.*;

/** Production-controller gates for feat prerequisites, effects and persistence. */
class PcgenFeats {
    private static Messages pathologyChoice(boolean remove) {
        return new Messages() {
            @Override
            public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
                if (remove) {
                    require(chooser.getSelectedList().getSize() == 2, "Saved Pathology choice count");
                    var names = new java.util.HashSet<String>();
                    for (var item : chooser.getSelectedList()) names.add(item.getKeyName());
                    require(names.equals(java.util.Set.of("Blinding sickness", "Mindfire")),
                        "Pathology disease choices must survive reload");
                    while (chooser.getSelectedList().getSize() > 0)
                        chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                } else {
                    var choices = new java.util.ArrayList<pcgen.facade.core.InfoFacade>();
                    for (var item : chooser.getAvailableList())
                        if (item.getKeyName().equals("Blinding sickness") || item.getKeyName().equals("Mindfire"))
                            choices.add(item);
                    require(choices.size() == 2, "Published Pathology targets available");
                    for (var item : choices) chooser.addSelected(item);
                }
                chooser.commit();
                return true;
            }
        };
    }
    private static Messages cautiousChoice(boolean remove) {
        return new Messages() {
            @Override
            public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
                if (remove) {
                    require(chooser.getSelectedList().getSize() == 1, "One saved Cautious target");
                    require(chooser.getSelectedList().getElementAt(0).getKeyName().equals("Climb"),
                        "Cautious skill choice must survive persistence");
                    chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                } else {
                    require(chooser.getAvailableList().getSize() == 1, "One eligible Cautious skill");
                    var selected = chooser.getAvailableList().getElementAt(0);
                    require(selected.getKeyName().equals("Climb"), "Expected Climb skill choice");
                    chooser.addSelected(selected);
                }
                chooser.commit();
                return true;
            }
        };
    }

    public static void main(String[] args) throws Exception {
        require(pcgen.system.Main.loadCharacterAndExport(args[0], args[1], args[2], args[3]), "Load failed");
        var pc = Globals.getPCList().get(0);
        var game = SettingsHandler.getGameAsProperty().get();
        var facade = CharacterManager.getCharacters().iterator().next();
        var messages = new Messages();
        var controller = new CharacterAbilities(pc, messages, facade.getDataSet(), new TodoManager());
        var feats = AbilityCategory.FEAT;
        if (args[6].equals("power")) {
            var expedited = ability(feats, "Expedited Incantation");
            var solitary = ability(feats, "Solitary Incantation");
            var perseverance = ability(feats, "Ritualistic Perseverance");
            var incanter = pc.getClassKeyed("Incanter (Spheres Prototype)");
            var climb = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Climb");
            var swim = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Swim");
            if (args[4].equals("feats-reload")) {
                var magicSaved = game.getAbilityCategory("Spheres Magic Talent");
                require(pc.hasAbilityKeyed(feats, "Pathology"), "Pathology retained in save");
                require(pc.hasAbilityKeyed(feats, "Virulent Ailment"), "Virulent retained in save");
                require(pc.hasAbilityKeyed(magicSaved, "Blood Sphere"), "Blood retained in save");
                var diseaseChooser = pcgen.util.chooser.ChooserFactory.getDelegate();
                pcgen.util.chooser.ChooserFactory.setDelegate(pathologyChoice(true));
                try {
                    controller.removeAbility(feats, ability(feats, "Pathology"));
                } finally {
                    pcgen.util.chooser.ChooserFactory.setDelegate(diseaseChooser);
                }
                controller.removeAbility(feats, ability(feats, "Virulent Ailment"));
                controller.removeAbility(magicSaved, ability(magicSaved, "Blood Sphere"));
                var cautious = ability(feats, "Cautious Incantation");
                require(pc.hasAbilityKeyed(feats, cautious.getKeyName()), "Cautious feat persistence");
                require(pcgen.core.analysis.SkillRankControl.getTotalRank(pc, climb).intValue() == 3,
                    "Cautious prerequisite ranks persistence");
                var previous = pcgen.util.chooser.ChooserFactory.getDelegate();
                pcgen.util.chooser.ChooserFactory.setDelegate(cautiousChoice(true));
                try {
                    controller.removeAbility(feats, cautious);
                } finally {
                    pcgen.util.chooser.ChooserFactory.setDelegate(previous);
                }
            }
            var incantationPool = pc.getAvailableAbilityPool(feats);
            for (int ranks : new int[] {0, 2, 3, 4, 5, 0}) {
                for (var skill : new pcgen.core.Skill[] {climb, swim}) {
                    double previous = pcgen.core.analysis.SkillRankControl.getTotalRank(pc, skill).doubleValue();
                    require(pcgen.core.analysis.SkillRankControl.modRanks(ranks - previous, incanter, true, pc, skill).isEmpty(),
                        "Set incantation prerequisite ranks");
                }
                pc.calcActiveBonuses();
                require(expedited.qualifies(pc, expedited) == (ranks >= 3), "Incantation requires three ranks in one skill");
                require(solitary.qualifies(pc, solitary) == (ranks >= 5), "Solitary requires five ranks in one skill");
                require(perseverance.qualifies(pc, perseverance) == (ranks >= 3), "Perseverance requires two qualifying skills");
                if (ranks == 3) {
                    var cautious = ability(feats, "Cautious Incantation");
                    boolean[] removingCautious = {false};
                    var previousChooser = pcgen.util.chooser.ChooserFactory.getDelegate();
                    pcgen.util.chooser.ChooserFactory.setDelegate(new Messages() {
                        @Override
                        public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
                            if (removingCautious[0]) {
                                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                            } else {
                                require(chooser.getAvailableList().getSize() + chooser.getSelectedList().getSize() == 2,
                                    "Only distinct trained incantation skills offered");
                                for (var item : chooser.getAvailableList()) {
                                    require(item.getKeyName().equals("Climb") || item.getKeyName().equals("Swim"),
                                        "Untrained incantation skill offered");
                                }
                                chooser.addSelected(chooser.getAvailableList().getElementAt(0));
                            }
                            chooser.commit();
                            return true;
                        }
                    });
                    try {
                        controller.addAbility(feats, cautious);
                        require(pc.hasAbilityKeyed(feats, cautious.getKeyName()), "Cautious skill selection");
                        require(pc.getAvailableAbilityPool(feats).equals(incantationPool.subtract(BigDecimal.ONE)),
                            "Cautious selection spends one feat");
                        controller.addAbility(feats, cautious);
                        require(pc.getAvailableAbilityPool(feats).equals(incantationPool.subtract(BigDecimal.valueOf(2))),
                            "Second distinct Cautious skill spends one additional feat");
                        removingCautious[0] = true;
                        controller.removeAbility(feats, cautious);
                        require(pc.hasAbilityKeyed(feats, cautious.getKeyName()), "Partial Cautious refund retains other skill");
                        require(pc.getAvailableAbilityPool(feats).equals(incantationPool.subtract(BigDecimal.ONE)),
                            "Partial Cautious removal refunds one feat");
                        controller.removeAbility(feats, cautious);
                        require(!pc.hasAbilityKeyed(feats, cautious.getKeyName()), "Cautious selection removed");
                    } finally {
                        pcgen.util.chooser.ChooserFactory.setDelegate(previousChooser);
                    }
                    controller.addAbility(feats, expedited);
                    require(pc.hasAbilityKeyed(feats, expedited.getKeyName()), "Incantation feat selection");
                    controller.removeAbility(feats, expedited);
                    pcgen.util.chooser.ChooserFactory.setDelegate(new Messages() {
                        @Override
                        public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
                            if (chooser.getSelectedList().getSize() == 2) {
                                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                                chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                            } else {
                                require(chooser.getAvailableList().getSize() == 2, "Perseverance eligible pair");
                                var first = chooser.getAvailableList().getElementAt(0);
                                var second = chooser.getAvailableList().getElementAt(1);
                                require(!first.getKeyName().equals(second.getKeyName()), "Perseverance distinct skills");
                                chooser.addSelected(first);
                                chooser.addSelected(second);
                            }
                            chooser.commit();
                            return true;
                        }
                    });
                    try {
                        controller.addAbility(feats, perseverance);
                        require(pc.hasAbilityKeyed(feats, perseverance.getKeyName()), "Perseverance pair selected");
                        require(pc.getAvailableAbilityPool(feats).equals(incantationPool.subtract(BigDecimal.ONE)),
                            "Two Perseverance choices cost one feat, not two");
                        controller.removeAbility(feats, perseverance);
                        require(!pc.hasAbilityKeyed(feats, perseverance.getKeyName()), "Perseverance pair removed");
                        require(pc.getAvailableAbilityPool(feats).equals(incantationPool), "Perseverance pair refund");
                    } finally {
                        pcgen.util.chooser.ChooserFactory.setDelegate(previousChooser);
                    }
                }
            }
            require(pcgen.core.analysis.SkillRankControl.modRanks(6, incanter, true, pc, climb).isEmpty(),
                "Set one six-rank skill");
            pc.calcActiveBonuses();
            require(expedited.qualifies(pc, expedited), "One six-rank skill satisfies single-skill prerequisite");
            require(!perseverance.qualifies(pc, perseverance), "Six ranks in one skill cannot replace two three-rank skills");
            require(pcgen.core.analysis.SkillRankControl.modRanks(-6, incanter, true, pc, climb).isEmpty(),
                "Restore incantation ranks");
            pc.calcActiveBonuses();
            require(pc.getAvailableAbilityPool(feats).equals(incantationPool), "Incantation feat refund");
            var vigilant = ability(feats, "Vigilant Skeptic");
            var alertness = ability(feats, "Alertness");
            var perception = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Perception");
            var senseMotive = Globals.getContext().getReferenceContext()
                .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Sense Motive");
            require(!vigilant.qualifies(pc, vigilant), "Vigilant requires skills or Alertness");
            require(pcgen.core.analysis.SkillRankControl.modRanks(5, incanter, true, pc, perception).isEmpty(),
                "Set Perception branch ranks");
            pc.calcActiveBonuses();
            require(!vigilant.qualifies(pc, vigilant), "One skill cannot satisfy conjunction");
            require(pcgen.core.analysis.SkillRankControl.modRanks(5, incanter, true, pc, senseMotive).isEmpty(),
                "Set Sense Motive branch ranks");
            pc.calcActiveBonuses();
            require(vigilant.qualifies(pc, vigilant), "Both skills satisfy Vigilant");
            for (var skill : new pcgen.core.Skill[] {perception, senseMotive}) {
                require(pcgen.core.analysis.SkillRankControl.modRanks(-5, incanter, true, pc, skill).isEmpty(),
                    "Remove Vigilant branch ranks");
            }
            pc.calcActiveBonuses();
            require(!vigilant.qualifies(pc, vigilant), "Vigilant loses skill route");
            controller.addAbility(feats, alertness);
            require(vigilant.qualifies(pc, vigilant), "Alertness alone satisfies Vigilant");
            controller.addAbility(feats, vigilant);
            require(pc.hasAbilityKeyed(feats, vigilant.getKeyName()), "Vigilant selection");
            controller.removeAbility(feats, alertness);
            require(!vigilant.qualifies(pc, vigilant), "Vigilant loses feat route");
            controller.removeAbility(feats, vigilant);
            require(pc.getAvailableAbilityPool(feats).equals(incantationPool), "Vigilant refunds");
            var magic = game.getAbilityCategory("Spheres Magic Talent");
            var virulent = ability(feats, "Virulent Ailment");
            var encompassing = ability(feats, "Encompassing Illness");
            var plaguePool = pc.getAvailableAbilityPool(feats);
            var plagueTalents = pc.getAvailableAbilityPool(magic);
            require(!virulent.qualifies(pc, virulent), "Plague requires a qualifying sphere");
            for (String sphereName : new String[] {"Blood Sphere", "Death Sphere"}) {
                var plagueSphere = ability(magic, sphereName);
                controller.addAbility(magic, plagueSphere);
                require(virulent.qualifies(pc, virulent), "Plague magic entry route " + sphereName);
                require(!encompassing.qualifies(pc, encompassing), "Every Plague route requires Virulent Ailment");
                controller.addAbility(feats, virulent);
                require(encompassing.qualifies(pc, encompassing), "Shared Plague feat and level satisfied");
                if (sphereName.equals("Blood Sphere")) {
                    var pathology = ability(feats, "Pathology");
                    var chooserBefore = pcgen.util.chooser.ChooserFactory.getDelegate();
                    pcgen.util.chooser.ChooserFactory.setDelegate(new Messages() {
                        private int calls = 0;
                        @Override
                        public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
                            int existing = chooser.getSelectedList().getSize();
                            if (calls++ >= 2) {
                                require(existing == (calls == 3 ? 4 : 2), "Pathology partial selection count");
                                for (int i = 0; i < 2; i++) {
                                    chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                                }
                            } else {
                                require(existing == (calls == 1 ? 0 : 2), "Pathology repeat retains choices");
                                require(chooser.getAvailableList().getSize() == 12 - existing,
                                    "Pathology excludes previously chosen diseases");
                                chooser.addSelected(chooser.getAvailableList().getElementAt(0));
                                chooser.addSelected(chooser.getAvailableList().getElementAt(0));
                            }
                            chooser.commit();
                            return true;
                        }
                    });
                    try {
                        var beforePathology = pc.getAvailableAbilityPool(feats);
                        controller.addAbility(feats, pathology);
                        require(pc.hasAbilityKeyed(feats, pathology.getKeyName()), "Pathology selection");
                        require(pc.getAvailableAbilityPool(feats).equals(beforePathology.subtract(BigDecimal.ONE)),
                            "Two diseases cost one feat");
                        controller.addAbility(feats, pathology);
                        require(pc.getAvailableAbilityPool(feats).equals(beforePathology.subtract(BigDecimal.valueOf(2))),
                            "Four diseases cost two feats");
                        controller.removeAbility(feats, pathology);
                        require(pc.getAvailableAbilityPool(feats).equals(beforePathology.subtract(BigDecimal.ONE)),
                            "Pathology partial refund");
                        controller.removeAbility(feats, pathology);
                        require(pc.getAvailableAbilityPool(feats).equals(beforePathology), "Pathology refund");
                    } finally {
                        pcgen.util.chooser.ChooserFactory.setDelegate(chooserBefore);
                    }
                }
                if (sphereName.equals("Death Sphere")) {
                    var rotten = ability(feats, "Rotten Hordes");
                    var shroud = ability(magic, "Death - Shroud");
                    require(!rotten.qualifies(pc, rotten), "Rotten Hordes requires Shroud on every route");
                    controller.addAbility(magic, shroud);
                    int points = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                    controller.addAbility(feats, rotten);
                    require(pc.hasAbilityKeyed(feats, rotten.getKeyName()), "Rotten Hordes selected");
                    require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == points + 1,
                        "Rotten Hordes spell point grant");
                    controller.removeAbility(magic, shroud);
                    require(!rotten.qualifies(pc, rotten), "Rotten Hordes prerequisite loss");
                    controller.removeAbility(feats, rotten);
                    require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == points,
                        "Rotten Hordes spell point refund");
                }
                controller.addAbility(feats, encompassing);
                require(pc.hasAbilityKeyed(feats, encompassing.getKeyName()), "Encompassing selection");
                controller.removeAbility(feats, virulent);
                require(!encompassing.qualifies(pc, encompassing), "Shared Plague prerequisite loss");
                controller.removeAbility(feats, encompassing);
                controller.removeAbility(magic, plagueSphere);
                require(!virulent.qualifies(pc, virulent), "Plague sphere prerequisite loss");
            }
            require(pc.getAvailableAbilityPool(feats).equals(plaguePool), "Plague feat refunds");
            require(pc.getAvailableAbilityPool(magic).equals(plagueTalents), "Plague sphere refunds");
            var warp = ability(magic, "Warp Sphere");
            var archer = ability(feats, "Dimensional Archer");
            var beforeWarp = pc.getAvailableAbilityPool(magic);
            var beforeArcher = pc.getAvailableAbilityPool(feats);
            require(!archer.qualifies(pc, archer), "Dimensional Archer requires Warp");
            controller.addAbility(magic, warp);
            require(archer.qualifies(pc, archer), "Reversed BAB prerequisite accepts sufficient BAB");
            controller.addAbility(feats, archer);
            require(pc.hasAbilityKeyed(feats, archer.getKeyName()), "Dimensional Archer selection");
            controller.removeAbility(magic, warp);
            require(!archer.qualifies(pc, archer), "Dimensional Archer loses Warp prerequisite");
            controller.removeAbility(feats, archer);
            require(pc.getAvailableAbilityPool(magic).equals(beforeWarp), "Warp refund");
            require(pc.getAvailableAbilityPool(feats).equals(beforeArcher), "Dimensional Archer refund");
            var light = ability(magic, "Light Sphere");
            var glow = ability(feats, "Seraphic Glow");
            var dark = ability(magic, "Dark Sphere");
            var damning = ability(feats, "Damning Darkness");
            var drawbacks = game.getAbilityCategory("Custom Casting Drawback");
            var terrain = ability(drawbacks, "Tradition - Terrain Casting");
            var defiler = ability(feats, "Terrain Defiler");
            var traditions = game.getAbilityCategory("Custom Casting Tradition");
            var tradition = ability(traditions, "Custom Casting Tradition");
            var original = pcgen.output.channel.compat.AlignmentCompat.getCurrentAlignment(pc.getCharID());
            var originalPool = pc.getAvailableAbilityPool(feats);
            var hubris = ability(feats, "Hubris Style");
            var defiance = ability(feats, "Hubris Defiance");
            var triumph = ability(feats, "Hubris Triumph");
            controller.addAbility(magic, light);
            controller.addAbility(magic, dark);
            require(pc.hasAbilityKeyed(magic, light.getKeyName()), "Light prerequisite setup");
            require(pc.hasAbilityKeyed(magic, dark.getKeyName()), "Dark prerequisite setup");
            require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 10,
                "Sphere selections must preserve caster level after reload");
            controller.addAbility(traditions, tradition);
            controller.addAbility(drawbacks, terrain);
            require(pc.hasAbilityKeyed(drawbacks, terrain.getKeyName()), "Terrain prerequisite setup");
            try {
                for (String key : new String[] {"LG", "NG", "CG", "LN", "TN", "CN", "LE", "NE", "CE"}) {
                    var alignment = Globals.getContext().getReferenceContext()
                        .silentlyGetConstructedCDOMObject(pcgen.core.PCAlignment.class, key);
                    require(alignment != null, "Missing alignment " + key);
                    facade.setAlignment(alignment);
                    boolean good = key.endsWith("G");
                    require(glow.qualifies(pc, glow) == good, "Good alignment qualification " + key);
                    require(damning.qualifies(pc, damning) == key.endsWith("E"), "Evil alignment qualification " + key);
                    require(defiler.qualifies(pc, defiler) == !good, "Non-good alignment qualification " + key);
                    boolean nonlawful = !key.startsWith("L");
                    require(hubris.qualifies(pc, hubris) == nonlawful, "Hubris alignment " + key);
                    require(!defiance.qualifies(pc, defiance), "Hubris Defiance requires Style");
                    if (nonlawful) {
                        controller.addAbility(feats, hubris);
                        require(defiance.qualifies(pc, defiance), "BAB five meets Defiance threshold");
                        controller.addAbility(feats, defiance);
                        require(!triumph.qualifies(pc, triumph), "Character level ten is not BAB nine or Monk nine");
                        controller.removeAbility(feats, hubris);
                        require(!defiance.qualifies(pc, defiance), "Defiance prerequisite loss");
                        controller.removeAbility(feats, defiance);
                    }
                    if (good) {
                        controller.addAbility(feats, glow);
                        require(pc.hasAbilityKeyed(feats, glow.getKeyName()), "Alignment feat grant");
                        controller.removeAbility(feats, glow);
                    } else {
                        rejected(controller, messages, feats, glow, "InfoAbility.Messages.NotQualified");
                    }
                    require(pc.getAvailableAbilityPool(feats).equals(originalPool), "Alignment feat refund");
                }
                var nature = ability(magic, "Nature Sphere");
                var terrainFocus = ability(feats, "Terrain Focus");
                controller.addAbility(magic, nature);
                require(terrainFocus.qualifies(pc, terrainFocus), "Terrain Focus setup");
                controller.addAbility(feats, defiler);
                require(pc.hasAbilityKeyed(feats, defiler.getKeyName()), "Terrain Defiler setup");
                rejected(controller, messages, feats, terrainFocus, "InfoAbility.Messages.NotQualified");
                controller.removeAbility(feats, defiler);
                require(terrainFocus.qualifies(pc, terrainFocus), "Terrain Focus qualification restoration");
                var oldChooser = pcgen.util.chooser.ChooserFactory.getDelegate();
                pcgen.util.chooser.ChooserFactory.setDelegate(new Messages() {
                    @Override
                    public boolean showGeneralChooser(pcgen.facade.core.ChooserFacade chooser) {
                        if (chooser.getSelectedList().getSize() > 0) {
                            chooser.removeSelected(chooser.getSelectedList().getElementAt(0));
                        } else {
                            require(chooser.isUserInput(), "Expected terrain target chooser");
                            chooser.addSelected(new pcgen.core.chooser.InfoWrapper("Forest"));
                        }
                        chooser.commit();
                        return true;
                    }
                });
                try {
                    controller.addAbility(feats, terrainFocus);
                    require(pc.hasAbilityKeyed(feats, terrainFocus.getKeyName()), "Terrain Focus selection");
                    rejected(controller, messages, feats, defiler, "InfoAbility.Messages.NotQualified");
                    controller.removeAbility(feats, terrainFocus);
                } finally {
                    pcgen.util.chooser.ChooserFactory.setDelegate(oldChooser);
                }
                require(defiler.qualifies(pc, defiler), "Terrain Defiler qualification restoration");
                controller.removeAbility(magic, nature);
                require(pc.getAvailableAbilityPool(feats).equals(originalPool), "Terrain exclusion refunds");
            } finally {
                facade.setAlignment(original);
                controller.removeAbility(magic, light);
                controller.removeAbility(magic, dark);
                controller.removeAbility(drawbacks, terrain);
                controller.removeAbility(traditions, tradition);
            }
        }
        boolean reload = args[4].equals("feats-reload");
        if (args[6].equals("mixed")) {
            try {
                var advanced = ability(feats, "Advanced Magic Training");
                var basic = ability(feats, "Basic Magic Training");
                require(!basic.qualifies(pc, basic), "Spherecasting class accepted Basic Magic Training");
                require(pc.getVariableValue("SPHERES_SPELL_POOL_LEVELS", "").intValue() == 4,
                    "Mixed fixture spherecasting levels");
                if (reload) {
                    require(pc.hasAbilityKeyed(feats, advanced.getKeyName()), "Mixed training persistence");
                    require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 5,
                        "Mixed training caster level persistence");
                    controller.removeAbility(feats, advanced);
                }
                int cl = pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue();
                int msb = pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue();
                int sp = pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue();
                var pool = pc.getAvailableAbilityPool(feats);
                var casting = game.getAbilityCategory("Spheres Casting Ability");
                var traditions = game.getAbilityCategory("Custom Casting Tradition");
                require(pc.getAvailableAbilityPool(casting).intValue() == 1, "Class casting allowance");
                require(pc.getAvailableAbilityPool(traditions).intValue() == 1, "Class tradition allowance");
                controller.addAbility(feats, advanced);
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == cl + 3,
                    "Only six noncasting levels should advance CL");
                require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == msb + 6,
                    "Only six noncasting levels should advance MSB");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == sp,
                    "Noncasting levels inflated spell pool");
                controller.removeAbility(feats, advanced);
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == cl, "Mixed CL refund");
                require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == msb, "Mixed MSB refund");
                require(pc.getAvailableAbilityPool(feats).equals(pool), "Mixed feat refund");
                controller.addAbility(feats, advanced);
            } finally {
                controller.closeCharacter();
            }
            if (!reload) {
                facade.setFile(Path.of(args[5]).toFile());
                require(CharacterManager.saveCharacter(facade), "Mixed save failed");
            }
            System.out.println("SPHERES_GATES_OK: " + args[4]);
            System.exit(0);
        }
        boolean might = args[6].equals("might");
        var talents = game.getAbilityCategory(might ? "Spheres Combat Talent" : "Spheres Magic Talent");
        String sphere = might ? "Fencing Sphere" : "Life Sphere";
        String focus = might ? "Combat Sphere Focus - Fencing" : "Sphere Focus - Life";
        String dc = might ? "SPHERES_DC_FENCING" : "SPHERES_DC_LIFE";
        try {
            var martialFocus = ability(AbilityCategory.FEAT, "Instinctive Stance");
            if (might) {
                var virulent = ability(feats, "Virulent Ailment");
                var encompassing = ability(feats, "Encompassing Illness");
                var originalFeats = pc.getAvailableAbilityPool(feats);
                var originalTalents = pc.getAvailableAbilityPool(talents);
                require(!virulent.qualifies(pc, virulent), "BAB alone cannot qualify for Plague");
                for (String entry : new String[] {"Duelist Sphere", "Alchemy Sphere"}) {
                    var entrySphere = ability(talents, entry);
                    controller.addAbility(talents, entrySphere);
                    require(virulent.qualifies(pc, virulent), "Martial Plague route " + entry);
                    require(!encompassing.qualifies(pc, encompassing), "Martial route still requires Virulent");
                    controller.addAbility(feats, virulent);
                    require(encompassing.qualifies(pc, encompassing), "Martial shared prerequisites");
                    controller.removeAbility(feats, virulent);
                    controller.removeAbility(talents, entrySphere);
                    require(!virulent.qualifies(pc, virulent), "Martial sphere removal");
                }
                require(pc.getAvailableAbilityPool(feats).equals(originalFeats), "Martial Plague feat refund");
                require(pc.getAvailableAbilityPool(talents).equals(originalTalents), "Martial Plague talent refund");
            }
            require(martialFocus.qualifies(pc, martialFocus) == might, "Initial martial focus eligibility");
            if (!might) {
                var extraCombat = ability(feats, "Extra Combat Talent");
                controller.addAbility(feats, extraCombat);
                require(martialFocus.qualifies(pc, martialFocus), "Extra Combat Talent must grant focus eligibility");
                require(pc.getVariableValue("SPHERES_MARTIAL_FOCUS_CAPACITY", "").intValue() == 1, "Baseline focus capacity");
                controller.removeAbility(feats, extraCombat);
                require(!martialFocus.qualifies(pc, martialFocus), "Focus eligibility must disappear with last source");
            } else {
                require(pc.getVariableValue("SPHERES_MARTIAL_FOCUS_CAPACITY", "").intValue() == 1, "Practitioner focus capacity");
            }
            if (reload) {
                require(pc.hasAbilityKeyed(feats, focus), "Focus not persisted");
                controller.removeAbility(feats, ability(feats, focus));
                if (might) {
                    require(pc.hasAbilityKeyed(feats, "Basic Magic Training"), "Basic Magic reload");
                    require(pc.hasAbilityKeyed(feats, "Advanced Magic Training"), "Advanced Magic reload");
                    require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 5, "Training caster level reload");
                    var castingChoices = game.getAbilityCategory("Spheres Casting Ability");
                    var traditionChoices = game.getAbilityCategory("Custom Casting Tradition");
                    require(pc.hasAbilityKeyed(castingChoices, "Wisdom Casting"), "Feat casting ability not persisted");
                    require(pc.hasAbilityKeyed(traditionChoices, "Custom Casting Tradition"), "Feat tradition not persisted");
                    require(pc.getAvailableAbilityPool(castingChoices).intValue() == 0, "Reload casting choice cost");
                    require(pc.getAvailableAbilityPool(traditionChoices).intValue() == 0, "Reload tradition choice cost");
                    controller.removeAbility(castingChoices, ability(castingChoices, "Wisdom Casting"));
                    controller.removeAbility(traditionChoices, ability(traditionChoices, "Custom Casting Tradition"));
                    controller.removeAbility(game.getAbilityCategory("Spheres Basic Magic Sphere"),
                        ability(game.getAbilityCategory("Spheres Magic Talent"), "Life Sphere"));
                    controller.removeAbility(feats, ability(feats, "Advanced Magic Training"));
                    controller.removeAbility(feats, ability(feats, "Basic Magic Training"));
                }
            } else {
                controller.addAbility(talents, ability(talents, sphere));
            }
            int baseline = pc.getVariableValue(dc, "").intValue();
            var pool = pc.getAvailableAbilityPool(feats);
            controller.addAbility(feats, ability(feats, focus));
            require(pc.getVariableValue(dc, "").intValue() == baseline + 1, "Sphere focus DC");
            require(pc.getAvailableAbilityPool(feats).equals(pool.subtract(BigDecimal.ONE)), "Feat pool spending");
            rejected(controller, messages, feats, ability(feats, focus), "InfoAbility.Messages.Duplicate");
            controller.removeAbility(feats, ability(feats, focus));
            require(pc.getVariableValue(dc, "").intValue() == baseline, "Focus removal");
            require(pc.getAvailableAbilityPool(feats).equals(pool), "Feat refund");
            controller.addAbility(feats, ability(feats, focus));
            if (!might) {
                var counter = ability(feats, "Counterspell");
                var improved = ability(feats, "Improved Counterspell (Spheres)");
                if (reload) {
                    require(pc.hasAbilityKeyed(feats, improved.getKeyName()), "Counterspell chain reload");
                    controller.removeAbility(feats, improved);
                    controller.removeAbility(feats, counter);
                }
                rejected(controller, messages, feats, improved, "InfoAbility.Messages.NotQualified");
                controller.addAbility(feats, counter);
                var destruction = ability(talents, "Destruction Sphere");
                var admixture = ability(talents, "Admixture");
                var selective = ability(talents, "Destruction - Selective Blast");
                var curative = ability(feats, "Curative Admixture");
                var selectiveAdmixture = ability(feats, "Selective Admixture");
                var magicPool = pc.getAvailableAbilityPool(talents);
                var familyPool = pc.getAvailableAbilityPool(feats);
                controller.addAbility(talents, destruction);
                controller.addAbility(talents, admixture);
                controller.addAbility(talents, selective);
                require(!selectiveAdmixture.qualifies(pc, selectiveAdmixture),
                    "An unrelated feat must not satisfy the Admixture family requirement");
                controller.addAbility(feats, curative);
                require(selectiveAdmixture.qualifies(pc, selectiveAdmixture), "Admixture family unlock");
                controller.addAbility(feats, selectiveAdmixture);
                require(pc.hasAbilityKeyed(feats, selectiveAdmixture.getKeyName()), "Selective Admixture selection");
                controller.removeAbility(feats, curative);
                require(!selectiveAdmixture.qualifies(pc, selectiveAdmixture), "Admixture family prerequisite loss");
                controller.removeAbility(feats, selectiveAdmixture);
                controller.removeAbility(talents, selective);
                controller.removeAbility(talents, admixture);
                controller.removeAbility(talents, destruction);
                require(pc.getAvailableAbilityPool(talents).equals(magicPool), "Admixture talent refunds");
                require(pc.getAvailableAbilityPool(feats).equals(familyPool), "Admixture feat refunds");
                var enhancement = ability(talents, "Enhancement Sphere");
                var circle = ability(feats, "Circle Casting");
                var proxy = ability(feats, "Spell Proxy");
                var maintain = ability(feats, "Maintain Proxy");
                controller.addAbility(talents, enhancement);
                controller.addAbility(feats, circle);
                require(!maintain.qualifies(pc, maintain), "Circle Casting is not a Proxy feat");
                require(!proxy.qualifies(pc, proxy), "Personal Magics exclusion must be reviewed");
                var proxyReviews = game.getAbilityCategory("Spheres Feat Adjudication");
                var proxyReview = ability(proxyReviews, "Reviewed - Spell Proxy");
                controller.addAbility(proxyReviews, proxyReview);
                controller.addAbility(feats, proxy);
                var choreography = ability(feats, "Mystic Choreography");
                require(!choreography.qualifies(pc, choreography), "Choreography requires a listed drawback");
                var traditionCategory = game.getAbilityCategory("Custom Casting Tradition");
                var drawbackCategory = game.getAbilityCategory("Custom Casting Drawback");
                var customTradition = ability(traditionCategory, "Custom Casting Tradition");
                var verbal = ability(drawbackCategory, "Tradition - Verbal Casting");
                controller.addAbility(traditionCategory, customTradition);
                controller.addAbility(drawbackCategory, verbal);
                require(choreography.qualifies(pc, choreography), "One listed drawback unlocks Choreography");
                controller.removeAbility(drawbackCategory, verbal);
                require(!choreography.qualifies(pc, choreography), "Choreography drawback loss");
                controller.removeAbility(traditionCategory, customTradition);
                require(maintain.qualifies(pc, maintain), "Proxy family unlock");
                controller.addAbility(feats, maintain);
                require(pc.hasAbilityKeyed(feats, maintain.getKeyName()), "Maintain Proxy selection");
                controller.removeAbility(feats, proxy);
                controller.removeAbility(proxyReviews, proxyReview);
                require(!proxy.qualifies(pc, proxy), "Personal Magics review removal");
                require(!maintain.qualifies(pc, maintain), "Proxy family prerequisite loss");
                controller.removeAbility(feats, maintain);
                controller.removeAbility(feats, circle);
                controller.removeAbility(talents, enhancement);
                require(pc.getAvailableAbilityPool(talents).equals(magicPool), "Proxy talent refund");
                require(pc.getAvailableAbilityPool(feats).equals(familyPool), "Proxy feat refunds");
                var mastery = ability(feats, "Counterspell Mastery");
                int msb = pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue();
                require(pc.getVariableValue("SPHERES_COUNTERSPELL_CHECK", "").intValue() == msb,
                    "Counterspell baseline check");
                controller.addAbility(feats, mastery);
                require(pc.getVariableValue("SPHERES_COUNTERSPELL_CHECK", "").intValue() == msb + 2,
                    "Counterspell Mastery check bonus");
                require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == msb,
                    "Counterspell Mastery must not raise all magical skill checks");
                controller.removeAbility(feats, mastery);
                require(pc.getVariableValue("SPHERES_COUNTERSPELL_CHECK", "").intValue() == msb,
                    "Counterspell Mastery refund");
                require(improved.qualifies(pc, improved), "Counterspell chain not unlocked");
                controller.addAbility(feats, improved);
                require(pc.getVariableValue("SPHERES_COUNTERSPELL_ADDITIONAL_EFFECTS", "").intValue() == 2, "Counterspell scaling");
                var unresolved = ability(feats, "Extra Bestial Trait");
                rejected(controller, messages, feats, unresolved, "InfoAbility.Messages.NotQualified");
                var review = game.getAbilityCategory("Spheres Feat Adjudication");
                var approval = ability(review, "Reviewed - Extra Bestial Trait");
                controller.addAbility(review, approval);
                require(pc.getAvailableAbilityPool(review).intValue() == 0, "Approval has cost");
                require(unresolved.qualifies(pc, unresolved), "Approval failed");
                controller.removeAbility(review, approval);
                require(!unresolved.qualifies(pc, unresolved), "Approval removal failed");
                var empower = ability(feats, "Empower Spell (Spheres)");
                controller.addAbility(feats, empower);
                require(pc.getVariableValue("SPHERES_METAMAGIC_EMPOWERSPELL_COST", "").intValue() == 2, "Metamagic spell-point cost");
                controller.removeAbility(feats, empower);
                require(pc.getVariableValue("SPHERES_METAMAGIC_EMPOWERSPELL_COST", "").intValue() == 0, "Metamagic cost removal");
                var combat = game.getAbilityCategory("Spheres Combat Talent");
                var extraCombat = ability(feats, "Extra Combat Talent");
                controller.addAbility(feats, extraCombat);
                controller.addAbility(combat, ability(combat, "Fencing Sphere"));
                require(pc.hasAbilityKeyed(combat, "Fencing Sphere"), "Cross-class combat sphere: " + messages.errors);
                var spec = ability(feats, "Combat Sphere Specialization - Fencing");
                controller.addAbility(feats, spec);
                require(pc.hasAbilityKeyed(feats, spec.getKeyName()), "Cross-class specialization: " + messages.errors);
                require(pc.getVariableValue("SPHERES_BAB_FENCING", "").intValue() == 8, "Low BAB specialization scaling: " + pc.getVariableValue("SPHERES_BAB_FENCING", ""));
                require(pc.getVariableValue("SPHERES_DC_FENCING", "").intValue() == 14, "Specialization DC scaling");
                require(pc.baseAttackBonus() == 5, "Specialization changed attack bonus");
                controller.removeAbility(feats, spec);
                controller.removeAbility(combat, ability(combat, "Fencing Sphere"));
                controller.removeAbility(feats, extraCombat);
            } else {
                var specialization = ability(feats, "Combat Sphere Specialization - Fencing");
                controller.addAbility(feats, specialization);
                require(pc.getVariableValue("SPHERES_BAB_FENCING", "").intValue() == 10, "Effective BAB exceeded level cap");
                require(pc.baseAttackBonus() == 10, "Specialization changed attack BAB");
                controller.removeAbility(feats, specialization);
                var extra = ability(feats, "Extra Combat Talent");
                var talentPool = pc.getAvailableAbilityPool(talents);
                controller.addAbility(feats, extra);
                controller.addAbility(feats, extra);
                require(pc.getAvailableAbilityPool(talents).equals(talentPool.add(BigDecimal.valueOf(2))), "Repeated feat talents");
                controller.removeAbility(feats, extra);
                controller.removeAbility(feats, extra);
                require(pc.getAvailableAbilityPool(talents).equals(talentPool), "Repeated feat refunds");
                var great = ability(feats, "Great Focus");
                rejected(controller, messages, feats, great, "InfoAbility.Messages.NotQualified");
                controller.addAbility(talents, ability(talents, "Shield Sphere"));
                require(great.qualifies(pc, great), "Two sphere prerequisite");
                controller.addAbility(feats, great);
                require(pc.getVariableValue("SPHERES_MARTIAL_FOCUS_CAPACITY", "").intValue() == 2, "Great Focus capacity");
                controller.removeAbility(feats, great);
                require(pc.getVariableValue("SPHERES_MARTIAL_FOCUS_CAPACITY", "").intValue() == 1, "Great Focus capacity refund");
                controller.removeAbility(talents, ability(talents, "Shield Sphere"));
                var basic = ability(feats, "Basic Magic Training");
                var castingChoices = game.getAbilityCategory("Spheres Casting Ability");
                var traditionChoices = game.getAbilityCategory("Custom Casting Tradition");
                var wisdom = ability(castingChoices, "Wisdom Casting");
                var tradition = ability(traditionChoices, "Custom Casting Tradition");
                require(!wisdom.qualifies(pc, wisdom), "Noncaster ability choice unlocked");
                require(!tradition.qualifies(pc, tradition), "Noncaster tradition unlocked");
                controller.addAbility(feats, basic);
                require(pc.getAvailableAbilityPool(castingChoices).intValue() == 1, "Feat casting ability allowance");
                require(pc.getAvailableAbilityPool(traditionChoices).intValue() == 1, "Feat tradition allowance");
                controller.addAbility(castingChoices, wisdom);
                controller.addAbility(traditionChoices, tradition);
                require(pc.hasAbilityKeyed(castingChoices, wisdom.getKeyName()), "Feat Wisdom casting rejected");
                require(pc.hasAbilityKeyed(traditionChoices, tradition.getKeyName()), "Feat casting tradition rejected");
                require(pc.getAvailableAbilityPool(castingChoices).intValue() == 0, "Casting choice cost");
                require(pc.getAvailableAbilityPool(traditionChoices).intValue() == 0, "Tradition choice cost");
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 1, "Basic Magic caster level");
                require(pc.getVariableValue("SPHERES_MAGIC_TALENTS", "").intValue() == 0, "Basic Magic bonus talents leaked");
                require(pc.getVariableValue("SPHERES_SPELL_POINTS", "").intValue() == 1, "Basic Magic spell pool");
                var basicPool = game.getAbilityCategory("Spheres Basic Magic Sphere");
                require(pc.getAvailableAbilityPool(basicPool).intValue() == 1, "Basic Magic sphere grant");
                var advanced = ability(feats, "Advanced Magic Training");
                require(advanced.qualifies(pc, advanced), "Advanced Magic qualification");
                controller.addAbility(feats, advanced);
                require(pc.hasAbilityKeyed(feats, advanced.getKeyName()), "Advanced Magic not selected: " + messages.errors);
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 5, "Advanced Magic low casting: " + pc.getVariableValue("SPHERES_CASTER_LEVEL", ""));
                require(pc.getVariableValue("SPHERES_MAGIC_SKILL_BONUS", "").intValue() == 10, "Advanced Magic skill bonus");
                controller.removeAbility(feats, advanced);
                controller.removeAbility(feats, basic);
                require(!wisdom.qualifies(pc, wisdom), "Casting ability survived last casting source");
                require(!tradition.qualifies(pc, tradition), "Tradition survived last casting source");
                controller.removeAbility(castingChoices, wisdom);
                controller.removeAbility(traditionChoices, tradition);
                require(pc.getAvailableAbilityPool(castingChoices).intValue() == 0, "Casting allowance survived refund");
                require(pc.getAvailableAbilityPool(traditionChoices).intValue() == 0, "Tradition allowance survived refund");
                require(pc.getVariableValue("SPHERES_CASTER_LEVEL", "").intValue() == 0, "Magic training refund");
                controller.addAbility(feats, basic);
                controller.addAbility(feats, advanced);
                controller.addAbility(basicPool, ability(game.getAbilityCategory("Spheres Magic Talent"), "Life Sphere"));
                controller.addAbility(castingChoices, wisdom);
                controller.addAbility(traditionChoices, tradition);
                require(pc.getAvailableAbilityPool(basicPool).intValue() == 0, "Basic sphere cost");
                require(pc.getAvailableAbilityPool(game.getAbilityCategory("Spheres Magic Talent")).intValue() == 0, "Basic sphere spent paid talents");
            }
            require(messages.errors.stream().noneMatch(e -> e == null), "Invalid error state");
            if (args[6].equals("power")) {
                var climb = Globals.getContext().getReferenceContext()
                    .silentlyGetConstructedCDOMObject(pcgen.core.Skill.class, "Climb");
                require(pcgen.core.analysis.SkillRankControl.modRanks(3,
                    pc.getClassKeyed("Incanter (Spheres Prototype)"), true, pc, climb).isEmpty(),
                    "Set persistent Cautious prerequisite");
                pc.calcActiveBonuses();
                var previous = pcgen.util.chooser.ChooserFactory.getDelegate();
                pcgen.util.chooser.ChooserFactory.setDelegate(cautiousChoice(false));
                try {
                    controller.addAbility(feats, ability(feats, "Cautious Incantation"));
                    require(pc.hasAbilityKeyed(feats, "Cautious Incantation"), "Retain Cautious for save");
                } finally {
                    pcgen.util.chooser.ChooserFactory.setDelegate(previous);
                }
                controller.addAbility(talents, ability(talents, "Blood Sphere"));
                controller.addAbility(feats, ability(feats, "Virulent Ailment"));
                pcgen.util.chooser.ChooserFactory.setDelegate(pathologyChoice(false));
                try {
                    controller.addAbility(feats, ability(feats, "Pathology"));
                    require(pc.hasAbilityKeyed(feats, "Pathology"), "Retain Pathology for save");
                } finally {
                    pcgen.util.chooser.ChooserFactory.setDelegate(previous);
                }
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