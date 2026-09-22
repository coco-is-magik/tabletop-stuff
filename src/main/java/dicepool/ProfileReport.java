package dicepool;

import java.io.PrintStream;
import java.util.List;
import java.util.Locale;

public final class ProfileReport {
    private ProfileReport() { }
    public static void write(List<Scenarios.Row> rows, boolean csv, PrintStream out) {
        if (rows.isEmpty()) throw new IllegalArgumentException("no scenarios");
        out.println(csv
                ? "profile,difficulty,n,pool_mean_pct,pool_median_pct,pool_p10_pct,pool_p90_pct,pool_min_pct,pool_max_pct,d20_mean_pct,d20_median_pct,d20_p10_pct,d20_p90_pct"
                : "Profile Difficulty  N   Pool mean/median   Pool p10-p90       Pool min-max       D20 mean");
        for (String profile : rows.stream().map(Scenarios.Row::profile).distinct().toList()) {
            for (var difficulty : Scenarios.Difficulty.values()) {
                var group = rows.stream().filter(r -> r.profile().equals(profile) && r.difficulty() == difficulty).toList();
                if (group.isEmpty()) continue;
                var p = ProfileAnalysis.summarize(group, r -> r.comparison().probability());
                var d = ProfileAnalysis.summarize(group, r -> r.comparison().d20());
                if (csv) out.printf(Locale.ROOT, "%s,%s,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f%n",
                        profile, difficulty, p.count(), p.mean()*100, p.median()*100, p.p10()*100, p.p90()*100,
                        p.minimum()*100, p.maximum()*100, d.mean()*100, d.median()*100, d.p10()*100, d.p90()*100);
                else out.printf(Locale.ROOT, "%-7s %-9s %3d   %6.2f / %6.2f   %6.2f - %6.2f   %6.2f - %6.2f   %6.2f%n",
                        profile, difficulty, p.count(), p.mean()*100, p.median()*100, p.p10()*100, p.p90()*100,
                        p.minimum()*100, p.maximum()*100, d.mean()*100);
            }
        }
    }
}