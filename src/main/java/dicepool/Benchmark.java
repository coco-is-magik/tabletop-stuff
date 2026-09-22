package dicepool;

import java.util.ArrayList;
import java.util.List;

public final class Benchmark {
    private Benchmark() { }
    public record Row(Check check, PoolRule pool, double d20, double probability) {
        public double error() { return Math.abs(d20 - probability); }
    }
    public record Metrics(int count, double mae, double rmse, double maxError,
                          double within1, double within2point5, double within5, double within10,
                          double averageDice, double medianDice, int p95Dice, int maxDice) { }

    public static List<Row> grid(ConversionModel model, Check.Type type) {
        List<Row> rows = new ArrayList<>();
        for (int bonus = -5; bonus <= 50; bonus++) {
            for (int dc = 5; dc <= 60; dc++) {
                Check check = new Check(type, bonus, dc);
                PoolRule rule = model.convert(check);
                rows.add(new Row(check, rule, new D20Engine(check).probability(),
                        new PoolEngine(rule).probability()));
            }
        }
        return List.copyOf(rows);
    }

    public static Metrics summarize(List<Row> rows) {
        if (rows.isEmpty()) throw new IllegalArgumentException("benchmark cannot be empty");
        double sum = 0, square = 0, max = 0, dice = 0;
        int[] within = new int[4];
        double[] limits = {0.01, 0.025, 0.05, 0.1};
        int[] pools = new int[rows.size()];
        for (int i = 0; i < rows.size(); i++) {
            Row row = rows.get(i);
            double error = row.error();
            sum += error;
            square += error * error;
            max = Math.max(max, error);
            pools[i] = row.pool().dice();
            dice += pools[i];
            for (int j = 0; j < limits.length; j++) if (error <= limits[j] + 1e-12) within[j]++;
        }
        java.util.Arrays.sort(pools);
        int n = rows.size();
        return new Metrics(n, sum / n, Math.sqrt(square / n), max,
                within[0] / (double) n, within[1] / (double) n,
                within[2] / (double) n, within[3] / (double) n, dice / n,
                (pools[(n - 1) / 2] + pools[n / 2]) / 2.0,
                pools[(int) Math.ceil(n * 0.95) - 1], pools[n - 1]);
    }
}