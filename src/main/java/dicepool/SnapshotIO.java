package dicepool;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

/** Versioned properties interchange at the I/O boundary, not a PCG character parser. */
public final class SnapshotIO {
    private SnapshotIO() { }

    public static CharacterSnapshot read(Reader reader) throws IOException {
        Properties p = new Properties();
        p.load(reader);
        Map<String, Integer> abilities = new HashMap<>(), saves = new HashMap<>(), skills = new HashMap<>();
        for (String key : List.of("STR", "DEX", "CON", "INT", "WIS", "CHA"))
            abilities.put(key, number(p, "ability." + key));
        for (String key : List.of("FORT", "REF", "WILL")) saves.put(key, number(p, "save." + key));
        for (String key : p.stringPropertyNames()) if (key.startsWith("skill."))
            skills.put(key.substring(6), number(p, key));
        int count = number(p, "attack.count");
        if (count < 0 || count > 100) throw new IllegalArgumentException("attack.count must be 0..100");
        List<CharacterSnapshot.Attack> attacks = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            String prefix = "attack." + i + ".";
            attacks.add(new CharacterSnapshot.Attack(text(p, prefix + "name"), number(p, prefix + "bonus"),
                    text(p, prefix + "damage"), number(p, prefix + "criticalMinimum"), number(p, prefix + "criticalMultiplier")));
        }
        return new CharacterSnapshot(number(p, "schemaVersion"), text(p, "name"), text(p, "provenance"),
                number(p, "level"), abilities, saves, number(p, "ac.total"), number(p, "ac.touch"),
                number(p, "ac.flatFooted"), attacks, skills);
    }

    public static void write(CharacterSnapshot snapshot, Writer writer) throws IOException {
        Properties p = new Properties();
        put(p, "schemaVersion", snapshot.schemaVersion());
        put(p, "name", snapshot.name());
        put(p, "provenance", snapshot.provenance());
        put(p, "level", snapshot.level());
        snapshot.abilities().forEach((key, value) -> put(p, "ability." + key, value));
        snapshot.saves().forEach((key, value) -> put(p, "save." + key, value));
        snapshot.skills().forEach((key, value) -> put(p, "skill." + key, value));
        put(p, "ac.total", snapshot.armorClass());
        put(p, "ac.touch", snapshot.touchArmorClass());
        put(p, "ac.flatFooted", snapshot.flatFootedArmorClass());
        put(p, "attack.count", snapshot.attacks().size());
        for (int i = 0; i < snapshot.attacks().size(); i++) {
            var attack = snapshot.attacks().get(i);
            String prefix = "attack." + i + ".";
            put(p, prefix + "name", attack.name());
            put(p, prefix + "bonus", attack.bonus());
            put(p, prefix + "damage", attack.damage());
            put(p, prefix + "criticalMinimum", attack.criticalMinimum());
            put(p, prefix + "criticalMultiplier", attack.criticalMultiplier());
        }
        // Stable sorted properties without Properties.store's wall-clock timestamp.
        for (String key : p.stringPropertyNames().stream().sorted().toList())
            writer.write(escape(key) + "=" + escape(p.getProperty(key)) + "\n");
    }

    private static String escape(String text) {
        return text.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
                .replace("\t", "\\t").replace(" ", "\\ ").replace("=", "\\=")
                .replace(":", "\\:").replace("#", "\\#").replace("!", "\\!");
    }
    private static void put(Properties p, String key, Object value) { p.setProperty(key, value.toString()); }
    private static String text(Properties p, String key) {
        String value = p.getProperty(key);
        if (value == null || value.isBlank()) throw new IllegalArgumentException("missing snapshot field " + key);
        return value;
    }
    private static int number(Properties p, String key) { return Integer.parseInt(text(p, key).strip()); }
}