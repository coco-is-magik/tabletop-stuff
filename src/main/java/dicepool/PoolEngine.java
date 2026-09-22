package dicepool;

import java.util.Objects;
import java.util.random.RandomGenerator;

public final class PoolEngine implements ResolutionEngine {
    private final PoolRule rule;
    private final double[] distribution;

    public PoolEngine(PoolRule rule) {
        this.rule = Objects.requireNonNull(rule, "rule");
        distribution = new double[rule.dice() + 1];
        distribution[0] = 1;
        double p = (11 - rule.target()) / 10.0;
        // Convolution avoids factorial overflow and is stable at p=0 and p=1.
        for (int n = 1; n <= rule.dice(); n++) {
            for (int k = n; k >= 0; k--) {
                distribution[k] = distribution[k] * (1 - p)
                        + (k == 0 ? 0 : distribution[k - 1] * p);
            }
        }
    }

    public PoolRule rule() { return rule; }
    public double[] distribution() { return distribution.clone(); }

    public double atLeast(int successes) {
        if (successes <= 0) return 1;
        double sum = 0;
        for (int k = successes; k < distribution.length; k++) sum += distribution[k];
        return Math.min(1, sum);
    }

    @Override public double probability() { return atLeast(rule.required()); }

    @Override public Result resolve(RandomGenerator random) {
        int successes = 0;
        for (int i = 0; i < rule.dice(); i++) {
            if (random.nextInt(10) + 1 >= rule.target()) successes++;
        }
        return new Result(successes >= rule.required(), successes, (long) successes - rule.required());
    }
}