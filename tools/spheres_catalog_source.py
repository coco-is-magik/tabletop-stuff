"""Bounded source snapshots for the PF1 Power/Might catalog (stdlib only).

No network access occurs while loading characters or generating reviewed LST.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "testdata/spheres/catalog-source"
POWER = "alteration blood conjuration creation dark death destruction divination enhancement fallen-fey fate illusion life light mana mind nature protection telekinesis time war warp weather bear technomancy veilweaving".split()
MIGHT = "alchemy athletics barrage barroom beastmastery berserker boxing brute dual-wielding duelist equipment-sphere fencing gladiator guardian lancer open-hand scoundrel scout shield sniper trap warleader-sphere wrestling leadership tech tinker pilot".split()
FEATS = "admixture-feats anathema-feats aristeia-feats champion-feats chance-feats channeling-feats combat-feats companion-feats counterspell-feats damnation-feats drawback-feats extra-feats general-feats item-creation-feats metamagic-feats necrosis-feats plague-feats practitioner-feats protokinesis-feats proxy-feats purring-feats racial-feats ritual-feats skybourne-feats squadron-feats surreal-feats teamwork-feats theurge-feats wild-magic-feats".split()
CLASSES = "armorist elementalist eliciter fey-adept hedgewitch mageknight shifter soul-weaver symbiat thaumaturge wraith armiger blacksmith commander scholar sentinel striker technician".split()


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active = False
        self.skip = 0
        self.heading = None
        self.parts = []
        self.sections = []
        self.current = {"level": 0, "heading": "Introduction", "anchor": "", "text": ""}

    def flush(self):
        text = " ".join("".join(self.parts).split())
        if self.heading is not None:
            self.current = {"level": self.heading, "heading": text, "anchor": self.anchor, "text": ""}
            self.sections.append(self.current)
        elif text:
            self.current["text"] += ("\n" if self.current["text"] else "") + text
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if attrs.get("id") == "page-content":
                self.active = True
                self.sections.append(self.current)
            if self.active:
                self.depth += 1
        if not self.active:
            return
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.flush()
            self.heading = int(tag[1])
            self.anchor = attrs.get("id", "")
        elif tag in ("p", "li", "tr", "br"):
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.flush()
            self.heading = None
        elif tag in ("p", "li", "tr"):
            self.flush()
        if tag == "div":
            self.depth -= 1
            if self.depth == 0:
                self.flush()
                self.active = False

    def handle_data(self, data):
        if self.active and not self.skip:
            self.parts.append(data)


def fetch(slug):
    if slug not in POWER + MIGHT + FEATS + CLASSES + ["traits", "practitioner-traits", "casting-traditions", "martial-traditions", "legal:start", "using-spheres-of-might", "using-spheres-of-power"]:
        raise ValueError("Not a catalog source")
    url = "https://spheresofpower.wikidot.com/" + slug
    request = urllib.request.Request(url, headers={"User-Agent": "PF1-PCGen-catalog/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(3_000_001)
    if len(raw) > 3_000_000:
        raise ValueError("Oversized source")
    page = Page()
    page.feed(raw.decode("utf-8"))
    if not page.sections or not any(s["text"] for s in page.sections):
        raise ValueError("Missing page content")
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    snapshot = {"url": url, "retrieved": "2026-09-24", "sha256": hashlib.sha256(raw).hexdigest(),
                "sections": page.sections}
    (SNAPSHOTS / (slug.replace(":", "-") + ".json")).write_text(json.dumps(snapshot, indent=2) + "\n")
    print(f"{slug}: {len(page.sections)} sections, {len(raw)} bytes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="+")
    args = parser.parse_args()
    if len(args.slugs) > 5:
        parser.error("At most five pages per fetch batch")
    for slug in args.slugs:
        fetch(slug)


if __name__ == "__main__":
    main()