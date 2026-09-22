package dicepool;

import java.util.random.RandomGenerator;

public interface ResolutionEngine {
    double probability();
    Result resolve(RandomGenerator random);

    /** value is the d20 face or pool success count; margin excludes automatic-face overrides. */
    record Result(boolean success, int value, long margin) { }
}