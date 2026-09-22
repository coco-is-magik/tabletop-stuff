package dicepool;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** PF1e scenario baseline v1; published target guidelines plus explicit synthetic assumptions. */
public final class Scenarios {
    private Scenarios() { }
    // Bestiary, Monster Statistics by CR, CR 1..20. Not empirical monster percentiles.
    private static final int[] AC = {12, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 36};
    private static final int[] SAVE_DC = {12, 13, 14, 15, 15, 16, 17, 18, 18, 19, 20, 21, 21, 22, 23, 24, 24, 25, 26, 27};
    public enum Profile { LOW, TYPICAL, HIGH }
    public enum Difficulty { LOW, AVERAGE, HIGH, VERY_HARD }

    public record Config(int firstLevel, int lastLevel, int acSpread, int dcSpread, int skillBase,
                         Check.Type type, Profile profile, Integer bonus) {
        public Config {
            if (firstLevel < 1 || lastLevel > 20 || firstLevel > lastLevel)
                throw new IllegalArgumentException("level range must be within 1..20 and ordered");
            if (acSpread < 1 || acSpread > 10 || dcSpread < 1 || dcSpread > 10)
                throw new IllegalArgumentException("AC/DC spreads must be 1..10");
            if (skillBase < 0 || skillBase > 100) throw new IllegalArgumentException("skill-base must be 0..100");
            if (type != null && type != Check.Type.ATTACK && type != Check.Type.SAVE && type != Check.Type.SKILL)
                throw new IllegalArgumentException("scenario type must be ATTACK, SAVE or SKILL");
            if (bonus != null && (bonus < -100 || bonus > 100))
                throw new IllegalArgumentException("scenario bonus must be -100..100");
            if (bonus != null && profile != null)
                throw new IllegalArgumentException("choose --bonus or --profile, not both");
        }
    }
    public record Row(int level, String profile, Difficulty difficulty, Benchmark.Row comparison) { }

    public static int bonus(int level, Check.Type type, Profile profile) {
        if (level < 1 || level > 20) throw new IllegalArgumentException("level must be 1..20");
        Objects.requireNonNull(profile, "profile");
        return switch (type) {
            case ATTACK -> switch (profile) {
                case LOW -> level / 2 + 2;
                case TYPICAL -> 3 * level / 4 + 3 + level / 4;
                case HIGH -> level + 4 + level / 4;
            };
            case SAVE -> switch (profile) {
                case LOW -> level / 3 + 1;
                case TYPICAL -> 2 + level / 2 + 2;
                case HIGH -> 2 + level / 2 + 5 + level / 4;
            };
            case SKILL -> switch (profile) {
                case LOW -> level / 2 + 1;
                case TYPICAL -> level + 3 + 2;
                case HIGH -> level + 3 + 4 + level / 4;
            };
            default -> throw new IllegalArgumentException("unsupported scenario type");
        };
    }

    public static List<Row> compare(Config config, ConversionModel model) {
        Objects.requireNonNull(config, "config");
        Objects.requireNonNull(model, "model");
        List<Row> rows = new ArrayList<>();
        for (int level = config.firstLevel(); level <= config.lastLevel(); level++) {
            for (Check.Type type : List.of(Check.Type.ATTACK, Check.Type.SAVE, Check.Type.SKILL)) {
                if (config.type() != null && config.type() != type) continue;
                for (Profile profile : Profile.values()) {
                    if (config.bonus() != null && profile != Profile.TYPICAL) continue;
                    if (config.profile() != null && config.profile() != profile) continue;
                    int bonus = config.bonus() == null ? bonus(level, type, profile) : config.bonus();
                    for (Difficulty difficulty : Difficulty.values()) {
                        if (type == Check.Type.ATTACK && difficulty == Difficulty.VERY_HARD) continue;
                        int center = switch (type) {
                            case ATTACK -> AC[level - 1];
                            case SAVE -> SAVE_DC[level - 1];
                            default -> level + config.skillBase();
                        };
                        int spread = type == Check.Type.ATTACK ? config.acSpread() : config.dcSpread();
                        int dc = center + (difficulty.ordinal() - 1) * spread;
                        Check check = new Check(type, bonus, dc);
                        PoolRule pool = model.convert(check);
                        rows.add(new Row(level, config.bonus() == null ? profile.name() : "CUSTOM", difficulty,
                                new Benchmark.Row(check, pool, new D20Engine(check).probability(),
                                        new PoolEngine(pool).probability())));
                    }
                }
            }
        }
        return List.copyOf(rows);
    }
}