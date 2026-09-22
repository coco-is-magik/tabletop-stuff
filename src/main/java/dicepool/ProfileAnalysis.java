package dicepool;

import java.util.List;
import java.util.function.ToDoubleFunction;

/** Absolute probability summaries across scenarios, not outcome percentiles of a single roll. */
public final class ProfileAnalysis {
    private ProfileAnalysis() { }
    public record Stats(int count, double mean, double median, double p10, double p90,
                        double minimum, double maximum) { }

    public static Stats summarize(List<Scenarios.Row> rows, ToDoubleFunction<Scenarios.Row> probability) {
        if (rows.isEmpty()) throw new IllegalArgumentException("no scenarios to summarize");
        double[] values = rows.stream().mapToDouble(probability).sorted().toArray();
        double sum = 0;
        for (double value : values) {
            if (!Double.isFinite(value) || value < 0 || value > 1)
                throw new IllegalArgumentException("probabilities must be finite and in [0,1]");
            sum += value;
        }
        int n = values.length;
        return new Stats(n, sum / n, (values[(n - 1) / 2] + values[n / 2]) / 2,
                values[(int) Math.ceil(n * .1) - 1], values[(int) Math.ceil(n * .9) - 1], values[0], values[n - 1]);
    }
}