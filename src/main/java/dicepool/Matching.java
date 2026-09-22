package dicepool;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public final class Matching {
    private Matching() { }
    public record Match(PoolRule rule, double probability, double error) { }

    public static List<Match> search(double target, int maxDice) {
        if (!Double.isFinite(target) || target < 0 || target > 1)
            throw new IllegalArgumentException("probability must be finite and in [0,1]");
        if (maxDice < 1 || maxDice > PoolRule.MAX_DICE)
            throw new IllegalArgumentException("max-dice must be 1..200");
        List<Match> matches = new ArrayList<>();
        for (int dice = 1; dice <= maxDice; dice++) {
            for (int tn = 2; tn <= 10; tn++) {
                PoolEngine engine = new PoolEngine(new PoolRule(dice, tn, 1));
                for (int required = 1; required <= dice; required++) {
                    double p = engine.atLeast(required);
                    matches.add(new Match(new PoolRule(dice, tn, required), p, Math.abs(p - target)));
                }
            }
        }
        matches.sort(Comparator.comparingDouble(Match::error)
                .thenComparingInt(m -> m.rule().dice())
                .thenComparingInt(m -> m.rule().target())
                .thenComparingInt(m -> m.rule().required()));
        return List.copyOf(matches);
    }
}