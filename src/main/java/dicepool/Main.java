package dicepool;

import java.io.PrintStream;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public final class Main {
    private Main() { }
    public static void main(String[] args) {
        try { execute(args, System.out, System.err); }
        catch (IllegalArgumentException | ArithmeticException error) {
            System.err.println("error: " + error.getMessage());
            System.exit(2);
        }
    }

    static void execute(String[] args, PrintStream out, PrintStream err) {
        if (args.length == 0 || args[0].equals("help")) {
            out.println("Commands: scenarios, match, table, probability, simulate, benchmark");
            out.println("scenarios [--level 5 | --min-level 1 --max-level 20] [--type ATTACK|SAVE|SKILL]");
            out.println("          [--profile LOW|TYPICAL|HIGH | --bonus 11] [--format table|csv]");
            out.println("          [--ac-spread 3 --dc-spread 5 --skill-base 10]");
            out.println("          [--report rows|profiles] (profiles: absolute probability distribution across scenarios)");
            out.println("          [--model baseline|tn8-7-4|tn8-8-4|tn8-10-5] (cannot combine with coefficients)");
            out.println("          Direct rolled checks only; take-10/take-20 situations excluded.");
            out.println("          accepts the same conversion coefficients as benchmark; defaults are experimental.");
            out.println("match --probability 0.55 [--max-dice 20 --limit 10]");
            out.println("probability|simulate --system d20 --type ATTACK --bonus 12 --dc 24");
            out.println("probability|simulate --system pool --dice 7 --target 6 --successes 4");
            out.println("simulate additionally accepts --iterations 100000 --seed 12345");
            out.println("benchmark [--type ATTACK --dice-offset 5 --bonus-per-die 2");
            out.println("           --target 6 --dc-offset 10 --dc-per-success 3]");
            out.println("benchmark writes CSV to stdout and metrics to stderr; table matches 5%..95%.");
            return;
        }
        Map<String, String> options = new HashMap<>();
        for (int i = 1; i < args.length; i += 2) {
            if (!args[i].startsWith("--") || i + 1 >= args.length)
                throw new IllegalArgumentException("expected --option value");
            if (options.put(args[i].substring(2), args[i + 1]) != null)
                throw new IllegalArgumentException("duplicate option " + args[i]);
        }
        Set<String> allowed = switch (args[0]) {
            case "match" -> Set.of("probability", "max-dice", "limit");
            case "table" -> Set.of("max-dice");
            case "probability", "simulate" -> Set.of("system", "type", "bonus", "dc", "dice", "target",
                    "successes", "iterations", "seed");
            case "benchmark" -> Set.of("type", "dice-offset", "bonus-per-die", "target", "dc-offset", "dc-per-success");
            case "scenarios" -> Set.of("level", "min-level", "max-level", "type", "profile", "bonus", "format",
                    "ac-spread", "dc-spread", "skill-base", "dice-offset", "bonus-per-die", "target", "dc-offset", "dc-per-success", "model", "report");
            default -> throw new IllegalArgumentException("unknown command " + args[0]);
        };
        for (String key : options.keySet()) if (!allowed.contains(key))
            throw new IllegalArgumentException("unknown option --" + key);
        switch (args[0]) {
            case "scenarios" -> {
                if (options.containsKey("level") && (options.containsKey("min-level") || options.containsKey("max-level")))
                    throw new IllegalArgumentException("choose --level or a level range, not both");
                String format = options.getOrDefault("format", "table");
                String report = options.getOrDefault("report", "rows");
                if (!report.equals("rows") && !report.equals("profiles"))
                    throw new IllegalArgumentException("report must be rows or profiles");
                if (!format.equals("table") && !format.equals("csv"))
                    throw new IllegalArgumentException("format must be table or csv");
                int first = integer(options, "level", integer(options, "min-level", 1));
                int last = integer(options, "level", integer(options, "max-level", 20));
                var config = new Scenarios.Config(first, last, integer(options, "ac-spread", 3),
                        integer(options, "dc-spread", 5), integer(options, "skill-base", 10),
                        options.containsKey("type") ? type(options) : null,
                        options.containsKey("profile") ? Scenarios.Profile.valueOf(options.get("profile").toUpperCase(Locale.ROOT)) : null,
                        options.containsKey("bonus") ? Integer.valueOf(options.get("bonus")) : null);
                if (options.containsKey("model") && Set.of("dice-offset", "bonus-per-die", "target", "dc-offset", "dc-per-success")
                        .stream().anyMatch(options::containsKey))
                    throw new IllegalArgumentException("choose a named model or explicit coefficients, not both");
                var model = options.containsKey("model") ? ConversionModel.named(options.get("model"))
                        : new ConversionModel(integer(options, "dice-offset", 5), integer(options, "bonus-per-die", 2),
                        integer(options, "target", 6), integer(options, "dc-offset", 10), integer(options, "dc-per-success", 3));
                err.println("Scenario settings: " + config);
                var rows = Scenarios.compare(config, model);
                if (report.equals("profiles")) {
                    err.println("Model: " + model);
                    err.println("Direct rolls only. Synthetic bonus profiles are NOT validated investment tiers.");
                    err.println("All values are percentages; p10/p90 use nearest rank across scenario probabilities, not roll outcomes.");
                    ProfileReport.write(rows, format.equals("csv"), out);
                } else ScenarioReport.write(rows, model, format.equals("csv"), out, err);
            }
            case "match" -> {
                int limit = integer(options, "limit", 10);
                if (limit < 1 || limit > 100) throw new IllegalArgumentException("limit must be 1..100");
                out.println("dice,target,required,probability,error");
                Matching.search(Double.parseDouble(required(options, "probability")), integer(options, "max-dice", 20))
                        .stream().limit(limit).forEach(m -> printMatch(out, m));
            }
            case "table" -> {
                out.println("d20_probability,dice,target,required,pool_probability,error");
                for (int i = 1; i < 20; i++) {
                    out.printf(Locale.ROOT, "%.2f,", i / 20.0);
                    printMatch(out, Matching.search(i / 20.0, integer(options, "max-dice", 20)).get(0));
                }
            }
            case "probability", "simulate" -> {
                String system = required(options, "system");
                ResolutionEngine engine = switch (system) {
                    case "d20" -> new D20Engine(new Check(type(options),
                            Integer.parseInt(required(options, "bonus")), Integer.parseInt(required(options, "dc"))));
                    case "pool" -> new PoolEngine(new PoolRule(Integer.parseInt(required(options, "dice")),
                            integer(options, "target", 6), Integer.parseInt(required(options, "successes"))));
                    default -> throw new IllegalArgumentException("system must be d20 or pool");
                };
                out.printf(Locale.ROOT, "Expected probability: %.9f%n", engine.probability());
                if (args[0].equals("simulate")) {
                    Simulation.Report report = Simulation.run(engine, integer(options, "iterations", 100000),
                            Long.parseLong(options.getOrDefault("seed", "12345")));
                    out.printf(Locale.ROOT, "Seed: %d%nIterations: %d%nSuccesses: %d%nObserved probability: %.9f%nDifference: %.9f%n",
                            report.seed(), report.iterations(), report.successes(), report.observed(), report.difference());
                }
            }
            case "benchmark" -> {
                ConversionModel model = new ConversionModel(integer(options, "dice-offset", 5),
                        integer(options, "bonus-per-die", 2), integer(options, "target", 6),
                        integer(options, "dc-offset", 10), integer(options, "dc-per-success", 3));
                var rows = Benchmark.grid(model, type(options));
                out.println("type,bonus,dc,d20_probability,dice,target,required,pool_probability,error");
                for (var row : rows) out.printf(Locale.ROOT, "%s,%d,%d,%.12f,%d,%d,%d,%.12f,%.12f%n",
                        row.check().type(), row.check().bonus(), row.check().dc(), row.d20(), row.pool().dice(),
                        row.pool().target(), row.pool().required(), row.probability(), row.error());
                err.println("Experimental model: " + model);
                err.println(Benchmark.summarize(rows));
            }
            default -> throw new IllegalArgumentException("unknown command");
        }
    }

    private static Check.Type type(Map<String, String> options) {
        return Check.Type.valueOf(options.getOrDefault("type", "SKILL").toUpperCase(Locale.ROOT));
    }
    private static String required(Map<String, String> options, String name) {
        String value = options.get(name);
        if (value == null) throw new IllegalArgumentException("missing --" + name);
        return value;
    }
    private static int integer(Map<String, String> options, String name, int fallback) {
        return Integer.parseInt(options.getOrDefault(name, Integer.toString(fallback)));
    }
    private static void printMatch(PrintStream out, Matching.Match match) {
        out.printf(Locale.ROOT, "%d,%d,%d,%.12f,%.12f%n", match.rule().dice(), match.rule().target(),
                match.rule().required(), match.probability(), match.error());
    }
}