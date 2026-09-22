package dicepool;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.util.List;
import java.util.Map;
import java.util.Random;

/** Dependency-free regression suite: explicit checks do not rely on enabled assertions. */
public final class EngineTest {
    private static int checks;
    private EngineTest() { }
    public static void main(String[] args) {
        d20();
        pool();
        experiments();
        snapshots();
        cli();
        System.out.println("PASS: " + checks + " regression checks");
    }
    static void check(boolean condition) {
        checks++;
        if (!condition) throw new AssertionError("check " + checks + " failed");
    }
    static void near(double actual, double expected) { check(Math.abs(actual - expected) < 1e-11); }
    static void rejects(Runnable action) {
        try { action.run(); }
        catch (IllegalArgumentException | NullPointerException | ArithmeticException expected) { checks++; return; }
        throw new AssertionError("expected invalid-input rejection");
    }
    private static void d20() {
        for (Check.Type type : Check.Type.values()) {
            for (int bonus = -5; bonus <= 50; bonus++) {
                for (int dc = 5; dc <= 60; dc++) {
                    D20Engine engine = new D20Engine(new Check(type, bonus, dc));
                    int count = 0;
                    for (int face = 1; face <= 20; face++) if (engine.face(face).success()) count++;
                    near(engine.probability(), count / 20.0);
                }
            }
        }
        near(new D20Engine(new Check(Check.Type.ATTACK, 100, 1)).probability(), .95);
        near(new D20Engine(new Check(Check.Type.SAVE, -100, 100)).probability(), .05);
        near(new D20Engine(new Check(Check.Type.SKILL, Integer.MAX_VALUE, Integer.MIN_VALUE)).probability(), 1);
        near(new D20Engine(new Check(Check.Type.SKILL, Integer.MIN_VALUE, Integer.MAX_VALUE)).probability(), 0);
        rejects(() -> new D20Engine(new Check(Check.Type.SKILL, 0, 10)).face(0));
    }
    private static void pool() {
        near(new PoolEngine(new PoolRule(7, 6, 4)).probability(), .5);
        for (int dice = 0; dice <= 3; dice++) {
            int outcomes = (int) Math.pow(10, dice);
            for (int target = 1; target <= 11; target++) {
                int[] counts = new int[dice + 1];
                for (int outcome = 0; outcome < outcomes; outcome++) {
                    int value = outcome, successes = 0;
                    for (int i = 0; i < dice; i++) {
                        if (value % 10 + 1 >= target) successes++;
                        value /= 10;
                    }
                    counts[successes]++;
                }
                PoolEngine engine = new PoolEngine(new PoolRule(dice, target, 1));
                for (int k = 0; k <= dice; k++) near(engine.distribution()[k], counts[k] / (double) outcomes);
                near(engine.atLeast(0), 1);
                near(engine.atLeast(dice + 1), 0);
            }
        }
        PoolEngine large = new PoolEngine(new PoolRule(200, 6, 100));
        near(java.util.Arrays.stream(large.distribution()).sum(), 1);
        double[] copy = large.distribution();
        copy[0] = 5;
        check(large.distribution()[0] != 5);
        rejects(() -> new PoolRule(-1, 6, 1));
        rejects(() -> new PoolRule(201, 6, 1));
        rejects(() -> new PoolRule(1, 12, 1));
    }
    private static void experiments() {
        for (ResolutionEngine engine : List.of(new D20Engine(new Check(Check.Type.ATTACK, 12, 24)),
                new PoolEngine(new PoolRule(7, 6, 4)))) {
            var a = Simulation.run(engine, 100000, 12345);
            check(a.equals(Simulation.run(engine, 100000, 12345)));
            check(Math.abs(a.difference()) < .01);
            Random first = new Random(123), second = new Random(123);
            for (int i = 0; i < 100; i++) check(engine.resolve(first).equals(engine.resolve(second)));
            rejects(() -> Simulation.run(engine, 0, 0));
        }
        rejects(() -> Matching.search(Double.NaN, 20));
        rejects(() -> Matching.search(1.1, 20));
        rejects(() -> Matching.search(.5, 0));
        var matches = Matching.search(.55, 20);
        check(matches.size() == 1890);
        for (int i = 1; i < matches.size(); i++) check(matches.get(i - 1).error() <= matches.get(i).error());
        near(Matching.search(.5, 20).get(0).error(), 0);
        ConversionModel model = new ConversionModel(5, 2, 6, 10, 3);
        check(model.convert(new Check(Check.Type.SKILL, -5, 11)).equals(new PoolRule(2, 6, 1)));
        rejects(() -> new ConversionModel(5, 0, 6, 10, 3));
        rejects(() -> model.convert(new Check(Check.Type.SKILL, 1000, 10)));
        var rows = Benchmark.grid(model, Check.Type.ATTACK);
        check(rows.size() == 3136);
        var metrics = Benchmark.summarize(rows);
        check(metrics.count() == 3136 && metrics.maxDice() == 30);
        check(metrics.mae() <= metrics.rmse() && metrics.rmse() <= metrics.maxError());
        check(metrics.within1() <= metrics.within2point5() && metrics.within5() <= metrics.within10());
        rejects(() -> Benchmark.summarize(List.of()));
        var exact = Benchmark.summarize(List.of(new Benchmark.Row(new Check(Check.Type.SKILL, 0, 10),
                new PoolRule(2, 6, 1), .75, .75)));
        near(exact.mae(), 0);
        near(exact.within1(), 1);
        near(exact.medianDice(), 2);
    }
    private static void snapshots() {
        var abilities = new java.util.HashMap<>(Map.of("STR", 18, "DEX", 12, "CON", 14, "INT", 10, "WIS", 10, "CHA", 8));
        var snapshot = new CharacterSnapshot(1, "Synthetic fighter", "synthetic; not PCGen validated", 5,
                abilities, Map.of("FORT", 6, "REF", 2, "WILL", 1), 20, 11, 19,
                List.of(new CharacterSnapshot.Attack("Longsword", 11, "1d8+5", 19, 2)), Map.of("Climb", 7));
        abilities.put("STR", 1);
        check(snapshot.abilities().get("STR") == 18);
        rejects(() -> new CharacterSnapshot.Attack("bad", 0, "1d8", 21, 2));
        try {
            var writer = new java.io.StringWriter();
            SnapshotIO.write(snapshot, writer);
            check(snapshot.equals(SnapshotIO.read(new java.io.StringReader(writer.toString()))));
            var second = new java.io.StringWriter();
            SnapshotIO.write(snapshot, second);
            check(writer.toString().equals(second.toString()));
            try (var reader = java.nio.file.Files.newBufferedReader(java.nio.file.Path.of("testdata/synthetic-fighter.properties"))) {
                check(SnapshotIO.read(reader).attacks().get(0).bonus() == 11);
            }
            String invalid = writer.toString().replace("schemaVersion=1", "schemaVersion=99");
            try {
                SnapshotIO.read(new java.io.StringReader(invalid));
                throw new AssertionError("unsupported schema accepted");
            } catch (IllegalArgumentException expected) { checks++; }
        } catch (java.io.IOException error) { throw new AssertionError(error); }
    }
    private static void cli() {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        PrintStream output = new PrintStream(bytes);
        Main.execute(new String[]{"match", "--probability", ".55", "--limit", "1"}, output, output);
        check(bytes.toString().lines().count() == 2);
        rejects(() -> Main.execute(new String[]{"match", "--probability", "NaN"}, output, output));
        rejects(() -> Main.execute(new String[]{"match", "--typo", "1"}, output, output));
        rejects(() -> Main.execute(new String[]{"match", "--probability", ".5", "--probability", ".6"}, output, output));
        bytes.reset();
        Main.execute(new String[]{"benchmark"}, output, new PrintStream(new ByteArrayOutputStream()));
        check(bytes.toString().lines().count() == 3137);
    }
}