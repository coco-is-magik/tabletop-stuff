package dicepool;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.util.List;

public final class ProfileTest {
    private ProfileTest() { }
    public static void main(String[] args) {
        var rows = Scenarios.compare(new Scenarios.Config(1,20,3,5,10,null,null,null), ConversionModel.named("tn8-8-4"));
        var small = rows.subList(0, 4);
        double[] values = {.1, .4, .9, .6};
        var stats = ProfileAnalysis.summarize(small, r -> values[small.indexOf(r)]);
        require(Math.abs(stats.mean() - .5) < 1e-12 && stats.median() == .5);
        require(stats.p10() == .1 && stats.p90() == .9 && stats.count() == 4);
        var one = ProfileAnalysis.summarize(rows.subList(0,1), r -> .3);
        require(one.mean() == .3 && one.median() == .3 && one.p10() == .3 && one.p90() == .3);
        reject(() -> ProfileAnalysis.summarize(List.of(), r -> .5));
        reject(() -> ProfileAnalysis.summarize(rows, r -> Double.NaN));
        reject(() -> ProfileAnalysis.summarize(rows, r -> 1.1));
        String csv = cli("scenarios", "--model", "tn8-8-4", "--report", "profiles", "--format", "csv");
        require(csv.equals(cli("scenarios", "--model", "tn8-8-4", "--report", "profiles", "--format", "csv")));
        require(csv.lines().count() == 13 && csv.lines().allMatch(l -> l.split(",").length == 13));
        require(cli("scenarios", "--report", "profiles", "--type", "ATTACK", "--bonus", "2", "--level", "1")
                .lines().count() == 4);
        reject(() -> cli("scenarios", "--report", "bad"));
        System.out.println("PASS: profile statistics, percentiles, replay, filters, CSV and rejection tests");
    }
    private static String cli(String... args) {
        var out = new ByteArrayOutputStream();
        Main.execute(args, new PrintStream(out), new PrintStream(new ByteArrayOutputStream()));
        return out.toString();
    }
    private static void require(boolean ok) { if (!ok) throw new AssertionError("profile test failed"); }
    private static void reject(Runnable action) {
        try { action.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("expected rejection");
    }
}