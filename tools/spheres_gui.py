"""Launch the PCGen GUI with the Spheres campaign dataset available.

A convenience wrapper around the vendored PCGen build. It reuses the same
Java/JavaFX toolchain and the same campaign data path as the headless gates, but
starts PCGen's JavaFX GUI and points it at this repository's `data/` so the
Spheres campaign and its Core dependency appear in the Sources list.

On first launch PCGen shows its Source Selection dialog: pick "Core Rulebook"
(or "Pathfinder RPG for Players") and "Spheres PF1e - Architecture Prototype",
then Load. PCGen remembers the choice in the settings directory below, so later
launches start faster.

Examples:
    python3 tools/spheres_gui.py                     # GUI, opens the sample character
    python3 tools/spheres_gui.py --no-character      # GUI with no character open
    python3 tools/spheres_gui.py --tab Abilities     # start on a tab
    python3 tools/spheres_gui.py --dry-run           # print the launch command only
    python3 tools/spheres_gui.py --party myparty.pcp # open a party file

Extra arguments after `--` are forwarded to PCGen unchanged.
"""
import argparse
import os
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import CACHE, JAVA, PCGEN, ROOT

JAR = PCGEN / "build/libs/pcgen-6.09.06.jar"
JAVAFX_MODULES = ("base", "graphics", "controls", "media", "fxml", "swing", "web")
SETTINGS = ROOT / "build/pcgen-gui"
DEFAULT_CHARACTER = ROOT / "testdata/spheres/incanter1-int18.pcg"


def javafx_jars():
    jars = []
    for module in JAVAFX_MODULES:
        matches = list((CACHE / f"javafx-{module}" / "16").glob(f"*/javafx-{module}-16-linux.jar"))
        if len(matches) != 1:
            raise SystemExit(f"Expected one cached JavaFX 16 Linux {module} JAR under {CACHE}")
        jars.append(matches[0])
    return jars


def settings_dir():
    """Persistent settings so the GUI remembers characters and preferences."""
    SETTINGS.mkdir(parents=True, exist_ok=True)
    config = SETTINGS / "config.ini"
    if not config.is_file():
        config.write_text(
            f"settingsPath={SETTINGS}\nsystemsPath={PCGEN / 'system'}\n"
            f"pluginsPath={PCGEN / 'plugins'}\npccFilesPath={PCGEN / 'data'}\n"
            f"osPath={PCGEN / 'outputsheets'}\npreviewPath={PCGEN / 'preview'}\n",
            encoding="utf-8")
    options = SETTINGS / "options.ini"
    if not options.is_file():
        options.write_text(
            f"pcgen.files.homebrewdataPath={ROOT / 'data'}\n"
            f"pcgen.files.characters={SETTINGS / 'characters'}\n"
            f"pcgen.files.customPath={SETTINGS / 'custom'}\n"
            f"pcgen.files.vendordataPath={SETTINGS / 'vendor'}\n",
            encoding="utf-8")
    return SETTINGS


def launch_command(character, tab, party, extra):
    if not JAVA.is_file():
        raise SystemExit(f"Java runtime not found: {JAVA}")
    if not JAR.is_file():
        raise SystemExit(f"Vendored PCGen JAR not found: {JAR}")
    work = settings_dir()
    args = [str(JAVA), "--enable-preview",
            "--module-path", os.pathsep.join(map(str, javafx_jars())),
            "--add-modules", "javafx.controls,javafx.web,javafx.swing,javafx.fxml",
            "--add-exports", "javafx.graphics/com.sun.javafx.application=ALL-UNNAMED",
            "--add-opens", "javafx.graphics/com.sun.glass.ui=ALL-UNNAMED",
            "-Xms512m", "-Xmx2g",
            f"-Dpcgen.config={work}",
            "-Djava.awt.headless=false",
            "-cp", str(JAR),
            "pcgen.system.Main",
            "--settingsdir", str(work)]
    if tab:
        args += ["--tab", tab]
    if party:
        args += ["--party", str(party)]
    if character:
        args += ["--character", str(character)]
    return args + list(extra)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--character", type=Path,
                        help="character file to open (default: the sample Incanter fixture)")
    parser.add_argument("--no-character", action="store_true",
                        help="start with no character open")
    parser.add_argument("--party", type=Path, help="party file to open")
    parser.add_argument("--tab", help="tab to open, e.g. Summary, Abilities, Inventory")
    parser.add_argument("--dry-run", action="store_true", help="print the command and exit")
    parser.add_argument("--force", action="store_true",
                        help="launch even without a detected display")
    parser.add_argument("extra", nargs="*", help="arguments forwarded to PCGen")
    args = parser.parse_args()

    character = None if args.no_character else (args.character or DEFAULT_CHARACTER)
    if character and not Path(character).is_file():
        parser.error(f"character file not found: {character}")
    if args.party and not args.party.is_file():
        parser.error(f"party file not found: {args.party}")

    command = launch_command(character, args.tab, args.party, args.extra)
    if args.dry_run:
        print(" ".join(command))
        return

    if not args.force and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise SystemExit("No DISPLAY or WAYLAND_DISPLAY detected. Run this on a desktop "
                         "session (or reuse --force if the display is provided some other way).\n"
                         "Command was:\n  " + " ".join(command))

    print(f"PCGen settings directory: {SETTINGS}", flush=True)
    print(f"Campaign data directory:  {ROOT / 'data'}", flush=True)
    if character:
        print(f"Opening character:        {character}", flush=True)
    subprocess.run(command, cwd=SETTINGS)


if __name__ == "__main__":
    main()
