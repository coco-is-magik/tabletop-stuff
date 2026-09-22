package dicepool;

import java.io.PrintStream;
import java.util.List;
import java.util.Locale;

/** Presentation only: engines and scenario generation remain free of I/O. */
public final class ScenarioReport {
    private ScenarioReport() { }
    public static void write(List<Scenarios.Row> rows, ConversionModel model, boolean csv,
                             PrintStream out, PrintStream err) {
        if (rows.isEmpty()) throw new IllegalArgumentException("no scenarios");
        err.println("PF1e scenarios v1: CR=level; synthetic bonuses and difficulty offsets, not validated characters.");
        err.println("Model: " + model);
        err.println("Direct rolls only; take-10/take-20 situations excluded. Average parity diagnostic: within 5pp.");
        out.println(csv ? "level,type,profile,difficulty,bonus,ac_or_dc,dice,target,required,d20_probability,pool_probability,delta_pp,error_pp"
                : "Level Type   Profile Difficulty Bonus AC/DC Pool       D20%    Pool% Delta(pp)");
        for (var row : rows) {
            var c = row.comparison();
            double delta = 100 * (c.probability() - c.d20());
            if (csv) out.printf(Locale.ROOT, "%d,%s,%s,%s,%d,%d,%d,%d,%d,%.12f,%.12f,%.9f,%.9f%n",
                    row.level(), c.check().type(), row.profile(), row.difficulty(), c.check().bonus(), c.check().dc(),
                    c.pool().dice(), c.pool().target(), c.pool().required(), c.d20(), c.probability(), delta, c.error() * 100);
            else out.printf(Locale.ROOT, "%5d %-6s %-7s %-9s %+4d %5d %2dd10/%d/%-3d %6.2f %8.2f %+9.2f%n",
                    row.level(), c.check().type(), row.profile(), row.difficulty(), c.check().bonus(), c.check().dc(),
                    c.pool().dice(), c.pool().target(), c.pool().required(), c.d20() * 100, c.probability() * 100, delta);
        }
        summarize("ALL", rows, err);
        for (Check.Type type : List.of(Check.Type.ATTACK, Check.Type.SAVE, Check.Type.SKILL)) {
            var group = rows.stream().filter(r -> r.comparison().check().type() == type).toList();
            if (!group.isEmpty()) summarize(type.name(), group, err);
        }
        for (var difficulty : Scenarios.Difficulty.values()) {
            var group = rows.stream().filter(r -> r.difficulty() == difficulty).toList();
            if (!group.isEmpty()) summarize(difficulty.name(), group, err);
        }
    }

    private static void summarize(String label, List<Scenarios.Row> rows, PrintStream out) {
        var metrics = Benchmark.summarize(rows.stream().map(Scenarios.Row::comparison).toList());
        long shaped = rows.stream().filter(row -> {
            double delta = row.comparison().probability() - row.comparison().d20();
            return switch (row.difficulty()) {
                case LOW -> delta > 1e-12;
                case AVERAGE -> Math.abs(delta) <= .05 + 1e-12;
                case HIGH, VERY_HARD -> delta < -1e-12;
            };
        }).count();
        double signed = rows.stream().mapToDouble(r -> r.comparison().probability() - r.comparison().d20()).average().orElseThrow();
        out.printf(Locale.ROOT, "%s n=%d MAE=%.3fpp RMSE=%.3fpp max=%.3fpp within5pp=%.2f%% dice(avg/p95/max)=%.2f/%d/%d%n",
                label, metrics.count(), metrics.mae() * 100, metrics.rmse() * 100, metrics.maxError() * 100,
                metrics.within5() * 100, metrics.averageDice(), metrics.p95Dice(), metrics.maxDice());
        out.printf(Locale.ROOT, "  meanDelta=%+.3fpp desiredDirectionOrParity=%d/%d%n", signed * 100, shaped, rows.size());
    }
}