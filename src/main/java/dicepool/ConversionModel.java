package dicepool;

/** Experimental coefficients, not Pathfinder rules. Negative competence clamps to zero dice. */
public record ConversionModel(int diceOffset, int bonusPerDie, int target,
                              int dcOffset, int dcPerSuccess) {
    public ConversionModel {
        if (bonusPerDie < 1 || dcPerSuccess < 1)
            throw new IllegalArgumentException("model divisors must be positive");
        if (target < 2 || target > 10) throw new IllegalArgumentException("model target must be 2..10");
    }

    public PoolRule convert(Check check) {
        long dice = Math.max(0, diceOffset + Math.floorDiv((long) check.bonus(), bonusPerDie));
        if (dice > PoolRule.MAX_DICE) throw new IllegalArgumentException("model produces more than 200 dice");
        long required = -Math.floorDiv(-((long) check.dc() - dcOffset), dcPerSuccess);
        return new PoolRule((int) dice, target, Math.toIntExact(required));
    }
}