package dicepool;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.util.List;

public final class ScenarioTest {
    private static int checks;
    private static final ConversionModel MODEL = new ConversionModel(5, 2, 6, 10, 3);
    private ScenarioTest() { }
    public static void main(String[] args) {
        var config = new Scenarios.Config(1, 20, 3, 5, 10, null, null, null);
        var rows = Scenarios.compare(config, MODEL);
        check(rows.size() == 660);
        check(rows.equals(Scenarios.compare(config, MODEL)));
        int[] ac = {12,14,15,17,18,19,20,21,23,24,25,27,28,29,30,31,32,33,34,36};
        int[] dc = {12,13,14,15,15,16,17,18,18,19,20,21,21,22,23,24,24,25,26,27};
        for (int level = 1; level <= 20; level++) {
            var single = Scenarios.compare(new Scenarios.Config(level, level, 3, 5, 10, null,
                    Scenarios.Profile.TYPICAL, null), MODEL);
            check(single.size() == 11);
            check(single.get(1).comparison().check().dc() == ac[level - 1]);
            check(single.get(4).comparison().check().dc() == dc[level - 1]);
            check(single.get(8).comparison().check().dc() == level + 10);
            for (int i = 0; i < single.size(); i++) {
                var row = single.get(i);
                var c = row.comparison();
                check(c.d20() >= 0 && c.d20() <= 1 && c.probability() >= 0 && c.probability() <= 1);
                if (row.difficulty() != Scenarios.Difficulty.LOW) {
                    var previous = single.get(i - 1).comparison();
                    check(c.d20() <= previous.d20());
                    check(c.probability() <= previous.probability() + 1e-12);
                }
            }
        }
        var fighter = Scenarios.compare(new Scenarios.Config(5, 5, 3, 5, 10, Check.Type.ATTACK, null, 11), MODEL);
        check(fighter.size() == 3 && fighter.get(1).profile().equals("CUSTOM"));
        near(fighter.get(0).comparison().d20(), .85);
        near(fighter.get(1).comparison().d20(), .70);
        near(fighter.get(2).comparison().d20(), .55);
        near(fighter.get(1).comparison().probability(), 968.0 / 1024);
        check(fighter.get(1).comparison().pool().equals(new PoolRule(10, 6, 3)));
        var skill = Scenarios.compare(new Scenarios.Config(20, 20, 3, 5, 10, Check.Type.SKILL, null, -100), MODEL);
        near(skill.get(0).comparison().d20(), 0);
        var save = Scenarios.compare(new Scenarios.Config(20, 20, 3, 5, 10, Check.Type.SAVE, null, -100), MODEL);
        near(save.get(0).comparison().d20(), .05);
        check(Scenarios.bonus(1, Check.Type.ATTACK, Scenarios.Profile.TYPICAL) == 3);
        check(Scenarios.bonus(20, Check.Type.ATTACK, Scenarios.Profile.TYPICAL) == 23);
        check(Scenarios.bonus(20, Check.Type.SAVE, Scenarios.Profile.HIGH) == 22);
        check(Scenarios.bonus(20, Check.Type.SKILL, Scenarios.Profile.HIGH) == 32);
        check(Scenarios.compare(new Scenarios.Config(5, 5, 2, 3, 12, Check.Type.SKILL, null, 10), MODEL)
                .get(3).comparison().check().dc() == 23);
        rejects(() -> new Scenarios.Config(0, 20, 3, 5, 10, null, null, null));
        rejects(() -> new Scenarios.Config(5, 4, 3, 5, 10, null, null, null));
        rejects(() -> new Scenarios.Config(1, 21, 3, 5, 10, null, null, null));
        rejects(() -> new Scenarios.Config(1, 20, 0, 5, 10, null, null, null));
        rejects(() -> new Scenarios.Config(1, 20, 3, 5, 10, Check.Type.CMB, null, null));
        rejects(() -> new Scenarios.Config(1, 20, 3, 5, 10, null, Scenarios.Profile.HIGH, 10));
        rejects(() -> new Scenarios.Config(1, 20, 3, 5, 10, null, null, 101));
        String csv = cli("scenarios", "--format", "csv");
        check(csv.equals(cli("scenarios", "--format", "csv")));
        check(csv.lines().count() == 661);
        check(csv.lines().allMatch(line -> line.split(",").length == 13));
        check(cli("scenarios", "--level", "5", "--type", "attack", "--bonus", "11", "--format", "csv")
                .contains("5,ATTACK,CUSTOM,AVERAGE,11,18,10,6,3,0.700000000000,0.945312500000"));
        check(cli("scenarios", "--level", "5", "--profile", "typical").lines().count() == 12);
        rejects(() -> cli("scenarios", "--level", "5", "--min-level", "1"));
        rejects(() -> cli("scenarios", "--format", "bad"));
        rejects(() -> cli("scenarios", "--profile", "bad"));
        rejects(() -> cli("scenarios", "--level", "oops"));
        rejects(() -> cli("scenarios", "--unknown", "1"));
        var out = new ByteArrayOutputStream();
        ScenarioReport.write(fighter, MODEL, true, new PrintStream(new ByteArrayOutputStream()), new PrintStream(out));
        check(out.toString().contains("ALL n=3") && out.toString().contains("ATTACK n=3"));
        check(out.toString().contains("AVERAGE n=1") && out.toString().contains("max="));
        rejects(() -> ScenarioReport.write(List.of(), MODEL, true, System.out, System.err));
        System.out.println("PASS: " + checks + " scenario baseline checks");
    }
    private static String cli(String... args) {
        var out = new ByteArrayOutputStream();
        Main.execute(args, new PrintStream(out), new PrintStream(new ByteArrayOutputStream()));
        return out.toString();
    }
    private static void check(boolean condition) {
        checks++;
        if (!condition) throw new AssertionError("scenario check " + checks + " failed");
    }
    private static void near(double actual, double expected) { check(Math.abs(actual - expected) < 1e-11); }
    private static void rejects(Runnable action) {
        try { action.run(); }
        catch (IllegalArgumentException expected) { checks++; return; }
        throw new AssertionError("expected rejection");
    }
}