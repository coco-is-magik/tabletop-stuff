"""Launch the PCGen GUI with the Spheres campaign dataset available.

A convenience wrapper around the vendored PCGen build. It reuses the same
Java/JavaFX toolchain and the same campaign data path as the headless gates, but
starts PCGen's JavaFX GUI and points it at this repository's `data/` so the
Spheres campaign and its Core dependency appear in the Sources list.

On launch PCGen shows its Source Selection dialog on the "Advanced" tab, with the
"Pathfinder" game mode and "Spheres PF1e - Architecture Prototype" + "Core Rulebook"
already selected — click Load. PCGen remembers the choice in the settings directory
below, so later launches start faster.

Notes on PCGen's own options, which this wrapper works around:
- `--settingsdir` and `--character` are declared with argparse4j `nargs(1)`, so
  `args.getString(...)`/`args.get(...)` return the list form (`[value]`); PCGen
  then uses a bogus bracketed settings directory and never reads `options.ini`.
  The wrapper therefore configures the settings directory through `config.ini`
  (`settingsPath`, via `-Dpcgen.config`) instead of `--settingsdir`.
- Auto-load and `-m` match campaigns by name, and three pcc files are named
  "Core Rulebook", so they load Core Rulebook twice, which aborts the load. The
  wrapper therefore does not auto-load; pick the sources in the dialog.

Requirement: the campaign declares SHOWINMENU:YES so PCGen lists it at all;
tools/pcgen_campaign_listing.py guards that.

Examples:
    python3 tools/spheres_gui.py               # GUI with the campaign pre-selected
    python3 tools/spheres_gui.py --dry-run     # print the launch command only
    python3 tools/spheres_gui.py -- <pcgen args>   # forward extra args to PCGen
"""
import argparse
import os
from pathlib import Path
import subprocess

from pcgen_spheres_smoke import CACHE, JAVA, PCGEN, ROOT

JAR = PCGEN / "build/libs/pcgen-6.09.06.jar"
JAVAFX_MODULES = ("base", "graphics", "controls", "media", "fxml", "swing", "web")
# Keep settings out of the repository. PCGen writes options.ini/config.ini here.
SETTINGS = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / \
    "tabletop-stuff/pcgen-gui"


def javafx_jars():
    jars = []
    for module in JAVAFX_MODULES:
        matches = list((CACHE / f"javafx-{module}" / "16").glob(f"*/javafx-{module}-16-linux.jar"))
        if len(matches) != 1:
            raise SystemExit(f"Expected one cached JavaFX 16 Linux {module} JAR under {CACHE}")
        jars.append(matches[0])
    return jars


def upsert(path, wanted):
    """Set keys in a Java properties file, replacing any existing values."""
    lines = []
    if path.is_file():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines()
                 if line.split("=", 1)[0] not in wanted]
    lines += [f"{key}={value}" for key, value in wanted.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def seed_settings(settings):
    """Prepare the GUI source dialog for the Spheres campaign.

    - Open on the Advanced tab (homebrew campaigns are only listed there).
    - Default the game mode to Pathfinder.
    - Pre-select Core Rulebook + Spheres so the dialog is ready to Load.
    - Avoid auto-load and `-m`: they match campaigns by name and three pcc files
      are named "Core Rulebook", so they load Core Rulebook twice, aborting the
      load. Pre-selection matches with a break, so it adds Core only once.
    """
    upsert(settings / "UIConfig.v2.ini", {
        "SourceSelectionDialog.useBasic": "false",
        "advancedSourceSelectionPanel.selectedGame": "Pathfinder_RPG",
        "advancedSourceSelectionPanel.selectedSources.Pathfinder_RPG":
            "Core Rulebook|Spheres PF1e - Architecture Prototype",
    })



def settings_dir(override=None):
    """Persistent settings so the GUI remembers characters and preferences."""
    settings = Path(override) if override else SETTINGS
    settings.mkdir(parents=True, exist_ok=True)
    config = settings / "config.ini"
    if not config.is_file():
        config.write_text(
            f"settingsPath={settings}\nsystemsPath={PCGEN / 'system'}\n"
            f"pluginsPath={PCGEN / 'plugins'}\npccFilesPath={PCGEN / 'data'}\n"
            f"osPath={PCGEN / 'outputsheets'}\npreviewPath={PCGEN / 'preview'}\n",
            encoding="utf-8")
    options = settings / "options.ini"
    if not options.is_file():
        options.write_text(
            f"pcgen.files.homebrewdataPath={ROOT / 'data'}\n"
            f"pcgen.files.characters={settings / 'characters'}\n"
            f"pcgen.files.customPath={settings / 'custom'}\n"
            f"pcgen.files.vendordataPath={settings / 'vendor'}\n",
            encoding="utf-8")
    seed_settings(settings)
    return settings


def launch_command(extra, settings=None):
    if not JAVA.is_file():
        raise SystemExit(f"Java runtime not found: {JAVA}")
    if not JAR.is_file():
        raise SystemExit(f"Vendored PCGen JAR not found: {JAR}")
    work = settings_dir(settings)
    args = [str(JAVA), "--enable-preview",
            "--module-path", os.pathsep.join(map(str, javafx_jars())),
            "--add-modules", "javafx.controls,javafx.web,javafx.swing,javafx.fxml",
            "--add-exports", "javafx.graphics/com.sun.javafx.application=ALL-UNNAMED",
            "--add-opens", "javafx.graphics/com.sun.glass.ui=ALL-UNNAMED",
            "-Xms512m", "-Xmx2g",
            f"-Dpcgen.config={work}",
            "-Djava.awt.headless=false",
            "-cp", str(JAR),
            "pcgen.system.Main"]
    return args + list(extra)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--settings-dir", type=Path,
                        help="settings directory (default: a directory under the user data "
                             "directory). PCGen writes and reloads options.ini here.")
    parser.add_argument("--dry-run", action="store_true", help="print the command and exit")
    parser.add_argument("--force", action="store_true",
                        help="launch even without a detected display")
    parser.add_argument("extra", nargs="*", help="arguments forwarded to PCGen")
    args = parser.parse_args()

    command = launch_command(args.extra, args.settings_dir)
    if args.dry_run:
        print(" ".join(command))
        return

    if not args.force and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise SystemExit("No DISPLAY or WAYLAND_DISPLAY detected. Run this on a desktop "
                         "session (or reuse --force if the display is provided some other way).\n"
                         "Command was:\n  " + " ".join(command))

    settings = args.settings_dir or SETTINGS
    print(f"PCGen settings directory: {settings}", flush=True)
    print(f"Campaign data directory:  {ROOT / 'data'}", flush=True)
    subprocess.run(command, cwd=settings)


if __name__ == "__main__":
    main()
