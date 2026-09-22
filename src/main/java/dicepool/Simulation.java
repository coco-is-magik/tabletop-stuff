package dicepool;

import java.util.Random;

public final class Simulation {
    private Simulation() { }
    public record Report(long seed, int iterations, int successes, double expected) {
        public double observed() { return successes / (double) iterations; }
        public double difference() { return observed() - expected; }
    }

    public static Report run(ResolutionEngine engine, int iterations, long seed) {
        if (iterations < 1 || iterations > 10_000_000)
            throw new IllegalArgumentException("iterations must be 1..10000000");
        if (engine instanceof PoolEngine pool && (long) iterations * pool.rule().dice() > 100_000_000)
            throw new IllegalArgumentException("simulation exceeds 100 million die rolls");
        Random random = new Random(seed);
        int successes = 0;
        for (int i = 0; i < iterations; i++) if (engine.resolve(random).success()) successes++;
        return new Report(seed, iterations, successes, engine.probability());
    }
}