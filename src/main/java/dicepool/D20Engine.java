package dicepool;

import java.util.Objects;
import java.util.random.RandomGenerator;

public record D20Engine(Check check) implements ResolutionEngine {
    public D20Engine { Objects.requireNonNull(check, "check"); }

    public Result face(int face) {
        if (face < 1 || face > 20) throw new IllegalArgumentException("d20 face must be 1..20");
        long margin = (long) face + check.bonus() - check.dc();
        boolean success = margin >= 0;
        if (check.automaticFaces() && (face == 1 || face == 20)) success = face == 20;
        return new Result(success, face, margin);
    }

    @Override public double probability() {
        long successfulFaces = 21L + check.bonus() - check.dc();
        return Math.max(check.automaticFaces() ? 1 : 0,
                Math.min(check.automaticFaces() ? 19 : 20, successfulFaces)) / 20.0;
    }

    @Override public Result resolve(RandomGenerator random) {
        return face(random.nextInt(20) + 1);
    }
}