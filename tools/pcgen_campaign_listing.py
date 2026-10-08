"""Prove the PCGen GUI source selection can offer the Spheres campaign.

Headless gates load campaigns by name, so they cannot detect a campaign missing
from the GUI's lists. This runs the same facades the Source Selection dialog uses
(FacadeFactory) against this repository's data path and asserts the Spheres
campaign is offered by the Advanced tab (game-mode matched) and by the Basic
quick-source list (SHOWINMENU:YES).
"""
import argparse
import subprocess

from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from spheres import DATA


def run():
    work = workspace()
    character = ROOT / "testdata/spheres/incanter1-int18.pcg"
    output = work / "export.txt"
    source = ROOT / "tools/PcgenGuiSources.java"
    cp = classpath()
    with (work / "compile.log").open("w") as stream:
        subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16",
                        "-cp", cp, "-d", str(work), str(source)],
                       stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                       timeout=60, check=True)
    command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
               "-cp", cp + ":" + str(work), "pcgen.system.PcgenGuiSources",
               str(character), str(DATA / "spheres_export.txt"), str(output), "config.ini"]
    log = work / "gui_sources.log"
    print("GUI source listing evidence:", work, flush=True)
    with log.open("w") as stream:
        subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                       stderr=subprocess.STDOUT, timeout=300, check=True)
    text = log.read_text(encoding="utf-8")
    if "SEVERE:" in text or "LSTERROR:" in text:
        raise ValueError(f"PCGen reported load errors; inspect {log}")
    for line in text.splitlines():
        if line.startswith(("loaded campaigns", "ADVANCED_TAB", "BASIC_TAB", "basic tab entries")):
            print(line)
    if "SPHERES_GUI_SOURCES_OK" not in text:
        raise ValueError(f"Missing GUI source listing evidence; inspect {log}")
    print("PASS: the GUI source selection offers the Spheres campaign")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()
