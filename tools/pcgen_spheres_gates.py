"""PCGen prerequisite, duplicate and core-isolation acceptance gates."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from spheres_progression_fixtures import fixture as progression_fixture

FEATURE_GATES = (
    "incanter1", "incanter20", "specializations3", "specializations20",
    "domains1", "domains20", "domains-save", "bloodline1", "bloodline20", "bloodline-save", "healer-save",
    "destruction1", "destruction3", "destruction8", "destruction20",
    "sword1", "sword5", "sword20", "sword-save", "human-favored", "half-elf-favored", "human-favored-save", "elf-favored", "dwarf-favored", "aasimar-favored", "aasimar-favored-save", "tiefling-favored", "tiefling-favored-save", "gnome-favored", "gnome-favored-save", "halfling-favored", "halfling-favored-save", "half-orc-favored", "half-orc-favored-save",
)


def validate_gate(log, gate):
    lines = log.read_text(encoding="utf-8").splitlines()
    marker = "prerequisites and duplicates" if gate == "selection" else gate
    if any("SEVERE:" in line or "LSTERROR:" in line for line in lines):
        raise ValueError(f"PCGen error; inspect {log}")
    if f"SPHERES_GATES_OK: {marker}" not in lines:
        raise ValueError(f"Missing gate evidence; inspect {log}")


def compare_core(baseline, augmented):
    for suffix in ("", ".snapshot"):
        left = baseline.with_name(baseline.name + suffix).read_text(encoding="utf-8")
        right = augmented.with_name(augmented.name + suffix).read_text(encoding="utf-8")
        if not left.strip() or left != right or "|" in left:
            raise ValueError(f"Core isolation mismatch or invalid output: {suffix or 'export'}")
    expected = "level=1\nbab=1\nhp=12\nfortitude=+4\nreflex=+1\nwill=+0\nac=11"
    if baseline.read_text(encoding="utf-8").strip() != expected:
        raise ValueError("Core Fighter baseline differs from expected values")


def run_gate(gate):
    if gate not in ("selection", "core-only", "core-with-spheres", *FEATURE_GATES):
        raise ValueError(f"Unknown gate: {gate}")
    cp = classpath()
    work = workspace()
    fixture = ROOT / "testdata/spheres/incanter1-int18.pcg"
    template = ROOT / "data/spheres/spheres_export.txt"
    if gate in ("human-favored", "half-elf-favored", "human-favored-save", "elf-favored", "dwarf-favored", "aasimar-favored", "aasimar-favored-save", "tiefling-favored", "tiefling-favored-save", "gnome-favored", "gnome-favored-save", "halfling-favored", "halfling-favored-save", "half-orc-favored", "half-orc-favored-save"):
        fixture = work / f"{gate}.pcg"
        text = progression_fixture(6)
        if gate == "half-elf-favored":
            text = text.replace("RACE:Human\n", "RACE:Half-Elf\n")
        if gate in ("half-orc-favored", "half-orc-favored-save"):
            text = text.replace("RACE:Human\n", "RACE:Half-Orc\n")
            text += "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Sorcerer Bloodline (Aberrant)\n"
        if gate == "elf-favored":
            text = text.replace("RACE:Human\n", "RACE:Elf\n")
        if gate in ("halfling-favored", "halfling-favored-save"):
            text = text.replace("RACE:Human\n", "RACE:Halfling\n")
            text += "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Channel Energy\n"
        if gate == "dwarf-favored":
            text = text.replace("RACE:Human\n", "RACE:Dwarf\n")
        if gate in ("gnome-favored", "gnome-favored-save"):
            text = text.replace("RACE:Human\n", "RACE:Gnome\n")
        if gate in ("aasimar-favored", "aasimar-favored-save"):
            text = text.replace("RACE:Human\n", "RACE:Aasimar\n")
            text = text.replace("CAMPAIGN:Core Rulebook|", "CAMPAIGN:support ~ aasimar race|CAMPAIGN:Core Rulebook|")
        if gate in ("tiefling-favored", "tiefling-favored-save"):
            text = text.replace("RACE:Human\n", "RACE:Tiefling\n")
            text = text.replace("CAMPAIGN:Core Rulebook|", "CAMPAIGN:support ~ tiefling race|CAMPAIGN:Core Rulebook|")
        fixture.write_text(text, encoding="utf-8")
    elif gate in ("domains-save", "bloodline-save", "healer-save"):
        fixture = work / f"{gate}.pcg"
        purchases = ("Channel Energy", "Merciful Healer") if gate == "healer-save" else (
            "Cleric Domain (Air)" if gate == "domains-save" else "Sorcerer Bloodline (Aberrant)",)
        fixture.write_text(progression_fixture(6) + "".join(
            f"ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:{purchase}\n"
            for purchase in purchases), encoding="utf-8")
    elif gate == "sword-save":
        fixture = work / "sword.pcg"
        fixture.write_text(progression_fixture(5) +
            "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Sword Birth\n", encoding="utf-8")
    elif gate.startswith("sword"):
        fixture = work / "sword.pcg"
        fixture.write_text(progression_fixture(int(gate.removeprefix("sword"))) +
            "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Sword Birth\n", encoding="utf-8")
    elif gate.startswith("destruction"):
        fixture = work / "destruction.pcg"
        text = progression_fixture(int(gate.removeprefix("destruction")))
        text = "\n".join(line for line in text.splitlines()
                         if not line.startswith("ABILITY:Spheres Magic Talent|")) + "\n"
        text += "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Sphere Specialization (Destruction)\n"
        fixture.write_text(text, encoding="utf-8")
    elif gate.startswith("bloodline"):
        fixture = work / "bloodline.pcg"
        fixture.write_text(progression_fixture(int(gate.removeprefix("bloodline"))) +
            "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Sorcerer Bloodline (Aberrant)\n"
            "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Admixture Adept\n", encoding="utf-8")
    elif gate.startswith("domains"):
        level = int(gate.removeprefix("domains"))
        fixture = work / "domains.pcg"
        text = progression_fixture(level)
        for name in ("Air", "Fire"):
            text += f"ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:Cleric Domain ({name})\n"
        fixture.write_text(text, encoding="utf-8")
    elif gate.startswith("specializations"):
        level = int(gate.removeprefix("specializations"))
        fixture = work / "specializations.pcg"
        text = progression_fixture(level)
        for name in ("Channel Energy", "Merciful Healer", "Familiar"):
            text += f"ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|KEY:{name}\n"
        fixture.write_text(text, encoding="utf-8")
    elif gate.startswith("incanter"):
        fixture = work / "incanter.pcg"
        fixture.write_text(progression_fixture(int(gate.removeprefix("incanter"))), encoding="utf-8")
    elif gate != "selection":
        fixture = ROOT / "testdata/spheres/core-fighter1.pcg"
        template = ROOT / "testdata/spheres/core_export.txt"
        if gate == "core-with-spheres":
            text = fixture.read_text(encoding="utf-8")
            fixture = work / "core-with-spheres.pcg"
            fixture.write_text(text.replace("CAMPAIGN:Core Rulebook\n",
                "CAMPAIGN:Core Rulebook|CAMPAIGN:Spheres PF1e - Architecture Prototype\n"),
                encoding="utf-8")
    output = work / "export.txt"
    log = work / "pcgen.log"
    # Compile into this isolated classpath so package-private PCGen controller
    # access uses the same classloader (source-file launch uses a separate loader).
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                        "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java")],
                       stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                       timeout=30, check=True)
    command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
               f"-Dpcgen.config={work}", "-cp", cp + ":" + str(work),
               "pcgen.gui2.facade.PcgenSpheresGates", str(fixture),
               str(template), str(output), "config.ini", gate]
    if gate in ("sword-save", "human-favored-save", "aasimar-favored-save", "tiefling-favored-save", "gnome-favored-save", "halfling-favored-save", "domains-save", "bloodline-save", "healer-save", "half-orc-favored-save"):
        command.append(str(work / "saved.pcg"))
    print(f"PCGen {gate} evidence: {work}", flush=True)
    with log.open("a", encoding="utf-8") as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL,
                       stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
    validate_gate(log, gate)
    if gate in ("sword-save", "human-favored-save", "aasimar-favored-save", "tiefling-favored-save", "gnome-favored-save", "halfling-favored-save", "domains-save", "bloodline-save", "healer-save", "half-orc-favored-save"):
        saved = work / "saved.pcg"
        if not saved.is_file():
            raise ValueError(f"PCGen did not save specialized {gate} character")
        reload_log = work / "reload.log"
        reloaded = work / "reloaded.txt"
        reload_command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
                          f"-Dpcgen.config={work}", "-cp", cp, "--source", "16",
                          str(ROOT / "tools/PcgenSpheresExport.java"), str(saved),
                          str(template), str(reloaded), "config.ini", gate]
        with reload_log.open("w", encoding="utf-8") as stream:
            subprocess.run(reload_command, cwd=work, stdin=subprocess.DEVNULL,
                           stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
        from pcgen_spheres_smoke import validate_result, validate_selection
        from spheres_progression_fixtures import expected
        expected_values = expected(5 if gate == "sword-save" else 6)
        if gate == "human-favored-save":
            expected_values["magic_talents"] += 1
        if gate == "tiefling-favored-save":
            # PCGen's default Tiefling grants +2 Intelligence; this is racial,
            # not a benefit of the favored-class concentration selections.
            expected_values["casting_modifier"] += 1
            expected_values["destruction_dc"] += 1
            expected_values["spell_points"] += 1
        if gate == "gnome-favored-save":
            expected_values["destruction_dc"] += 1
        validate_result(reloaded, reload_log, expected_values)
        validate_selection(reload_log)
        if f"SPHERES_SPECIALIZATION_OK: {gate}" not in reload_log.read_text(encoding="utf-8"):
            raise ValueError("Missing specialized save/reload evidence")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("selection", "isolation", "all", *FEATURE_GATES))
    args = parser.parse_args()
    try:
        if args.gate in ("half-orc-favored", "half-orc-favored-save"):
            run_gate(args.gate)
            print("PASS: Half-Orc bloodline strength without early power unlock")
        if args.gate in ("human-favored", "half-elf-favored"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} six picks, race restriction and removal")
        if args.gate == "elf-favored":
            run_gate(args.gate)
            print("PASS: Elf favored metamagic feat six picks and removal")
        if args.gate == "dwarf-favored":
            run_gate(args.gate)
            print("PASS: Dwarf favored crafting feat pool six picks and removal")
        if args.gate == "halfling-favored":
            run_gate(args.gate)
            print("PASS: Halfling favored channel energy uses, prerequisites and refund")
        if args.gate in ("domains-save", "bloodline-save", "healer-save"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} granted powers survive save/reload")
        if args.gate == "halfling-favored-save":
            run_gate(args.gate)
            print("PASS: Halfling channel energy favored uses survive save/reload")
        if args.gate == "aasimar-favored":
            run_gate(args.gate)
            print("PASS: Aasimar favored Spellcraft bonus, race restriction and removal")
        if args.gate == "aasimar-favored-save":
            run_gate(args.gate)
            print("PASS: Aasimar favored Spellcraft bonus survives save/reload")
        if args.gate in ("tiefling-favored", "tiefling-favored-save"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} concentration bonus and qualification")
        if args.gate in ("gnome-favored", "gnome-favored-save"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} Destruction sphere DC six picks and round trip or removal")
        if args.gate == "human-favored-save":
            run_gate(args.gate)
            print("PASS: six Human favored class picks and talent survive save/reload")
        if args.gate == "sword-save":
            run_gate(args.gate)
            print("PASS: Sword Birth trick, feat and specialization survive save/reload")
        elif args.gate.startswith("sword"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} arena progression, trick prerequisites and refunds")
        if args.gate.startswith("destruction"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} specialization grants, costs, level gates and removal")
        if args.gate in ("bloodline1", "bloodline20"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} powers, scaling, exclusions and removal")
        if args.gate in ("domains1", "domains20"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} powers, casting modifier, paired activation and refunds")
        if args.gate.startswith("specializations"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} activation, scaling and choice restrictions")
        if args.gate.startswith("incanter"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} bonus feats and resource grants")
        if args.gate == "all":
            for gate in FEATURE_GATES:
                run_gate(gate)
                print(f"PASS: {gate}", flush=True)
        if args.gate in ("selection", "all"):
            run_gate("selection")
            print("PASS: prerequisite enforcement and duplicate rejection")
        if args.gate in ("isolation", "all"):
            baseline = run_gate("core-only")
            augmented = run_gate("core-with-spheres")
            compare_core(baseline, augmented)
            print("PASS: core Fighter exports/state unchanged with Spheres loaded; no casting grants")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"gates: {error}\n")


if __name__ == "__main__":
    main()