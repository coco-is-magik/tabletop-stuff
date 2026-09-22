package dicepool;

/** Experimental coefficients, not Pathfinder rules. Negative competence clamps to zero dice. */
public record ConversionModel(int diceOffset, int bonusPerDie, int target,
                              int dcOffset, int dcPerSuccess, int minimumDice) {
    public ConversionModel(int diceOffset, int bonusPerDie, int target, int dcOffset, int dcPerSuccess) {
        this(diceOffset, bonusPerDie, target, dcOffset, dcPerSuccess, 0);
    }

    public static ConversionModel named(String name) {
        return switch (name) {
            case "baseline" -> new ConversionModel(5, 2, 6, 10, 3);
            case "tn8-7-4" -> new ConversionModel(0, 1, 8, 7, 4, 1);
            case "tn8-8-4" -> new ConversionModel(0, 1, 8, 8, 4, 1);
            case "tn8-10-5" -> new ConversionModel(0, 1, 8, 10, 5, 1);
            default -> throw new IllegalArgumentException("unknown model " + name);
        };
    }
    public ConversionModel {
        if (minimumDice < 0 || minimumDice > PoolRule.MAX_DICE)
            throw new IllegalArgumentException("minimum dice must be 0..200");
        if (bonusPerDie < 1 || dcPerSuccess < 1)
            throw new IllegalArgumentException("model divisors must be positive");
        if (target < 2 || target > 10) throw new IllegalArgumentException("model target must be 2..10");
    }

    public PoolRule convert(Check check) {
        long dice = Math.max(minimumDice, diceOffset + Math.floorDiv((long) check.bonus(), bonusPerDie));
        if (dice > PoolRule.MAX_DICE) throw new IllegalArgumentException("model produces more than 200 dice");
        long required = -Math.floorDiv(-((long) check.dc() - dcOffset), dcPerSuccess);
        return new PoolRule((int) dice, target, Math.toIntExact(required));
    }
}