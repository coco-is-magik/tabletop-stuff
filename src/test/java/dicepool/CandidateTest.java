package dicepool;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

public final class CandidateTest {
    private CandidateTest() { }
    public static void main(String[] args) {
        for (String name : new String[]{"tn8-7-4", "tn8-8-4", "tn8-10-5"}) {
            var model = ConversionModel.named(name);
            for (int bonus = -5; bonus <= 50; bonus++) {
                var pool = model.convert(new Check(Check.Type.ATTACK, bonus, 18));
                require(pool.dice() == Math.max(1, bonus) && pool.target() == 8);
            }
            var config = new Scenarios.Config(1, 20, 3, 5, 10, null, null, null);
            var rows = Scenarios.compare(config, model);
            require(rows.size() == 660 && rows.equals(Scenarios.compare(config, model)));
        }
        var model = ConversionModel.named("tn8-7-4");
        require(model.convert(new Check(Check.Type.ATTACK, 11, 15)).required() == 2);
        require(model.convert(new Check(Check.Type.ATTACK, 11, 18)).required() == 3);
        require(model.convert(new Check(Check.Type.ATTACK, 11, 21)).required() == 4);
        for (int dc : new int[]{7, 8, 11, 12, 15, 16, 19, 20}) {
            require(model.convert(new Check(Check.Type.SKILL, 11, dc)).required() == (int) Math.ceil((dc - 7) / 4.0));
        }
        var baseline = ConversionModel.named("baseline");
        require(baseline.equals(new ConversionModel(5, 2, 6, 10, 3)));
        require(baseline.convert(new Check(Check.Type.SKILL, -100, 10)).dice() == 0);
        var out = new ByteArrayOutputStream();
        var err = new ByteArrayOutputStream();
        Main.execute(new String[]{"scenarios", "--model", "tn8-7-4", "--format", "csv"}, new PrintStream(out), new PrintStream(err));
        require(out.toString().lines().count() == 661);
        require(err.toString().contains("desiredDirectionOrParity="));
        reject(() -> ConversionModel.named("unknown"));
        reject(() -> new ConversionModel(0, 1, 8, 7, 4, -1));
        reject(() -> Main.execute(new String[]{"scenarios", "--model", "tn8-7-4", "--target", "9"}, System.out, System.err));
        System.out.println("PASS: candidate models, full-grid replay, boundary and CLI checks");
    }
    private static void require(boolean value) { if (!value) throw new AssertionError("candidate check failed"); }
    private static void reject(Runnable action) {
        try { action.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("expected rejection");
    }
}