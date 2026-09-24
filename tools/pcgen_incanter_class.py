"""Bounded thin Incanter acceptance: class math, six budgets, selections and reload."""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture


PURCHASES = ((), ("Familiar",), ("Master of Mysteries",),
             ("Familiar", "Master of Mysteries"),
             ("Master of Mysteries", "Channel Energy"),
             ("Familiar", "Master of Mysteries", "Channel Energy"))


def class_fixture(level, casting, points):
    if points not in range(6):
        raise ValueError("Expected specialization points 0-5")
    return fixture(level, casting) + "".join(
        "ABILITY:Incanter Specialization|TYPE:NORMAL|CATEGORY:Incanter Specialization|"
        f"KEY:{name}\n" for name in PURCHASES[points])


def expected_chassis(level, casting):
    # Fixture CON/DEX are 10; WIS is 8 except when selected as casting ability.
    if level not in range(1, 21) or casting not in ("INT", "WIS", "CHA"):
        raise ValueError("Expected level 1-20 and mental casting ability")
    return {"level": level, "bab": level // 2,
            "fortitude": level // 3, "reflex": level // 3,
            "will": 2 + level // 2 + (4 if casting == "WIS" else -1)}


def run(level, casting, points=None):
    work = workspace()
    cp = classpath()
    log = work / "compile.log"
    with log.open("w") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                        "-cp", cp, "-d", str(work), str(ROOT / "tools/PcgenSpheresGates.java")],
                       stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                       timeout=30, check=True)
    template = work / "class-export.txt"
    template.write_text("level=|TOTALLEVELS|\nbab=|VAR.BAB.INTVAL|\n"
                        "fortitude=|CHECK.FORTITUDE.TOTAL|\nreflex=|CHECK.REFLEX.TOTAL|\n"
                        "will=|CHECK.WILL.TOTAL|\n")
    print(f"Incanter class evidence: {work}", flush=True)
    for budget in range(6) if points is None else (points,):
        character = work / f"class-{budget}.pcg"
        character.write_text(class_fixture(level, casting, budget))
        saved = work / f"saved-{budget}.pcg"
        for gate, source in (("class-save", character), ("class-reload", saved)):
            output = work / f"{budget}-{gate}.txt"
            log = work / f"{budget}-{gate}.log"
            command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true",
                       f"-Dpcgen.config={work}", "-cp", cp + ":" + str(work),
                       "pcgen.gui2.facade.PcgenSpheresGates", str(source), str(template),
                       str(output), "config.ini", gate]
            if gate == "class-save":
                command.append(str(saved))
            with log.open("w") as stream:
                subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                               stderr=subprocess.STDOUT, timeout=90, check=True)
            validate_gate(log, gate)
            validate_chassis(output.read_text(), expected_chassis(level, casting))
        print(f"PASS: Incanter {level} {casting}, {budget} points; class math, grants, reload and refunds", flush=True)


def validate_chassis(text, expected):
    # PCGen renders saves with a leading plus; retain strict field/duplicate checks.
    from spheres import compare_export
    compare_export(text.replace("=+", "="), expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", type=int, choices=range(1, 21), required=True)
    parser.add_argument("--casting", choices=("INT", "WIS", "CHA"), default="INT")
    parser.add_argument("--points", type=int, choices=range(6))
    args = parser.parse_args()
    try:
        run(args.level, args.casting, args.points)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"incanter class: {error}\n")


if __name__ == "__main__":
    main()