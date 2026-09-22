"""ThinkPad-only PCGen prerequisite, duplicate and core-isolation acceptance gates."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from spheres_progression_fixtures import fixture as progression_fixture


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
    if gate not in ("selection", "core-only", "core-with-spheres", "incanter1", "incanter20", "specializations3", "specializations20", "domains1", "domains20", "bloodline1", "bloodline20", "destruction1", "destruction3", "destruction8", "destruction20", "sword1", "sword5", "sword20"):
        raise ValueError(f"Unknown gate: {gate}")
    cp = classpath()
    work = workspace()
    fixture = ROOT / "testdata/spheres/incanter1-int18.pcg"
    template = ROOT / "data/spheres/spheres_export.txt"
    if gate.startswith("sword"):
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
    print(f"PCGen {gate} evidence: {work}", flush=True)
    with log.open("a", encoding="utf-8") as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL,
                       stdout=stream, stderr=subprocess.STDOUT, timeout=90, check=True)
    validate_gate(log, gate)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("selection", "isolation", "all", "incanter1", "incanter20", "specializations3", "specializations20", "domains1", "domains20", "bloodline1", "bloodline20", "destruction1", "destruction3", "destruction8", "destruction20", "sword1", "sword5", "sword20"))
    args = parser.parse_args()
    try:
        if args.gate.startswith("sword"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} arena progression, trick prerequisites and refunds")
        if args.gate.startswith("destruction"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} specialization grants, costs, level gates and removal")
        if args.gate.startswith("bloodline"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} powers, scaling, exclusions and removal")
        if args.gate.startswith("domains"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} powers, casting modifier, paired activation and refunds")
        if args.gate.startswith("specializations"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} activation, scaling and choice restrictions")
        if args.gate.startswith("incanter"):
            run_gate(args.gate)
            print(f"PASS: {args.gate} bonus feats and resource grants")
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