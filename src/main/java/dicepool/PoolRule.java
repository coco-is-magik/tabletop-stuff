package dicepool;

public record PoolRule(int dice, int target, int required) {
    public static final int MAX_DICE = 200;
    public PoolRule {
        if (dice < 0 || dice > MAX_DICE) throw new IllegalArgumentException("dice must be 0..200");
        if (target < 1 || target > 11) throw new IllegalArgumentException("d10 target must be 1..11");
        // Nonpositive requirements always succeed; requirements above the pool always fail.
    }
}