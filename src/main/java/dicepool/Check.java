package dicepool;

import java.util.Objects;

public record Check(Type type, int bonus, int dc) {
    public enum Type { ATTACK, SAVE, SKILL, ABILITY_CHECK, CMB, OTHER }
    public Check { Objects.requireNonNull(type, "check type"); }
    public boolean automaticFaces() {
        return type == Type.ATTACK || type == Type.SAVE || type == Type.CMB;
    }
}