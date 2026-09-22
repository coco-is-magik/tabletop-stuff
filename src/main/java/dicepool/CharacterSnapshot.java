package dicepool;

import java.util.List;
import java.util.Map;
import java.util.Objects;

/** Final calculated values only; no character-building logic. */
public record CharacterSnapshot(int schemaVersion, String name, String provenance, int level,
        Map<String, Integer> abilities, Map<String, Integer> saves,
        int armorClass, int touchArmorClass, int flatFootedArmorClass,
        List<Attack> attacks, Map<String, Integer> skills) {
    public record Attack(String name, int bonus, String damage, int criticalMinimum, int criticalMultiplier) {
        public Attack {
            if (name == null || name.isBlank() || damage == null || damage.isBlank())
                throw new IllegalArgumentException("attack name and damage required");
            if (criticalMinimum < 2 || criticalMinimum > 20 || criticalMultiplier < 2)
                throw new IllegalArgumentException("invalid critical profile");
        }
    }
    public CharacterSnapshot {
        if (schemaVersion != 1) throw new IllegalArgumentException("unsupported snapshot schema");
        if (name == null || name.isBlank() || provenance == null || provenance.isBlank() || level < 1)
            throw new IllegalArgumentException("name, provenance and positive level required");
        abilities = Map.copyOf(abilities);
        saves = Map.copyOf(saves);
        attacks = List.copyOf(attacks);
        skills = Map.copyOf(skills);
        for (String key : List.of("STR", "DEX", "CON", "INT", "WIS", "CHA")) {
            if (Objects.requireNonNull(abilities.get(key), "missing ability " + key) < 0)
                throw new IllegalArgumentException("negative ability");
        }
        for (String key : List.of("FORT", "REF", "WILL"))
            Objects.requireNonNull(saves.get(key), "missing save " + key);
    }
}