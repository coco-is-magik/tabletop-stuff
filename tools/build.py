"""Small offline Java 17 build driver; no third-party Python packages."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ROOT / "build" / "classes"


def run(args):
    subprocess.run(args, cwd=ROOT, check=True, timeout=90)


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "test"
    if action not in {"build", "test", "run"}:
        raise ValueError("usage: python3 tools/build.py [build|test|run CLI-ARGS...]")
    sources = sorted((ROOT / "src" / "main" / "java").rglob("*.java"))
    if action == "test":
        sources += sorted((ROOT / "src" / "test" / "java").rglob("*.java"))
    if not 1 <= len(sources) <= 40:
        raise ValueError("unexpected source count")
    CLASSES.mkdir(parents=True, exist_ok=True)
    run(["javac", "--release", "17", "-Xlint:all", "-Werror", "-d", str(CLASSES),
         *map(str, sources)])
    if action == "test":
        run(["java", "-ea", "-cp", str(CLASSES), "dicepool.ProfileTest"])
        run(["java", "-ea", "-cp", str(CLASSES), "dicepool.CandidateTest"])
        run(["java", "-ea", "-cp", str(CLASSES), "dicepool.ScenarioTest"])
        run(["java", "-ea", "-cp", str(CLASSES), "dicepool.EngineTest"])
    elif action == "run":
        run(["java", "-cp", str(CLASSES), "dicepool.Main", *sys.argv[2:]])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"build: {error}", file=sys.stderr)
        sys.exit(1)