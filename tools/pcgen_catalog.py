"""Bounded production-controller catalog round trips, up to five spheres per run."""
import argparse
import subprocess
from pathlib import Path
from pcgen_spheres_smoke import JAVA, ROOT, classpath, workspace
from pcgen_spheres_gates import validate_gate
from spheres_progression_fixtures import fixture as magic_fixture
from pcgen_conscript_class import fixture as combat_fixture
from spheres_catalog import inventory
from spheres_catalog_lst import key, repeat_limit, PACKAGES


def run(system, offset, count, phase='all', work=None):
    rows = [r for r in inventory() if r["system"] == system][offset:offset+count]
    if not rows:
        raise ValueError("Empty batch")
    if phase == 'reload' and (work is None or not (work / 'saved.pcg').is_file()):
        raise ValueError('Reload requires --work with a saved.pcg')
    work = work or workspace()
    cp = classpath()
    print("Catalog evidence:", work, flush=True)
    char = work / "catalog.pcg"
    # Equipment-only checks need six paid talents, not level-20 class grants.
    # Keep the resource-scaling batches at level 20 and reduce this isolated
    # prerequisite/choice round trip's load on the production controller.
    combat_level = 10 if len(rows) == 1 and rows[0]['sphere'] == 'Equipment' else 20
    raw = magic_fixture(20, "INT") if system == "power" else combat_fixture(combat_level)
    cat = "Spheres Magic Talent" if system == "power" else "Spheres Combat Talent"
    char.write_text("\n".join(s for s in raw.splitlines() if not s.startswith("ABILITY:" + cat + "|")) + "\n")
    cases = []
    for row in rows:
        # Package/repeatability behaviors have separate tests; this covers every sphere.
        talent = next(t for t in row["talents"] if repeat_limit(t) == 1
                      and "Prerequisite" not in t["text"]
                      and not any(p.lower() in t["heading"].lower() for p in PACKAGES.get(row["slug"], ())))
        cases.append(row["sphere"] + " Sphere\t" + key(row, talent))
    case_file = work / "cases.tsv"
    case_file.write_text("\n".join(cases) + "\n")
    template = work / "export.txt"
    template.write_text("level=|TOTALLEVELS|\n")
    sources = [ROOT / 'tools/PcgenSpheresGates.java', ROOT / 'tools/PcgenCatalog.java']
    compiled = [work / 'pcgen/gui2/facade' / (source.stem + '.class') for source in sources]
    if not all(target.is_file() and target.stat().st_mtime >= source.stat().st_mtime
               for source, target in zip(sources, compiled)):
        with (work / "compile.log").open("w") as stream:
            subprocess.run([str(JAVA.with_name("javac")), "--enable-preview", "--release", "16", "-cp", cp,
                            "-d", str(work), *map(str, sources)],
                           stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=30, check=True)
    saved = work / "saved.pcg"
    for gate, source in (("catalog-save", char), ("catalog-reload", saved)):
        if phase != 'all' and gate != 'catalog-' + phase:
            continue
        log = work / (gate + ".log")
        command = [str(JAVA), "--enable-preview", "-Djava.awt.headless=true", f"-Dpcgen.config={work}",
                   "-cp", cp + ":" + str(work), "pcgen.gui2.facade.PcgenCatalog", str(source),
                   str(template), str(work / (gate + ".txt")), "config.ini", gate, str(saved), str(case_file), cat]
        with log.open("w") as stream:
            subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, stdout=stream,
                           stderr=subprocess.STDOUT, timeout=95 if phase != 'all' else 50, check=True)
        validate_gate(log, gate)
    print("PASS:", ", ".join(r["sphere"] for r in rows), "selection, pools, refund; phase", phase)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system", choices=("power", "might"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, choices=range(1,6), default=5)
    parser.add_argument('--phase', choices=('all', 'save', 'reload'), default='all')
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    run(args.system, args.offset, args.count, args.phase, args.work)