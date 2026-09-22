"""Verify the pinned archive, inspect it, or unpack unchanged upstream source."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    dependency = json.loads((ROOT / "vendor/manifest.json").read_text())["dependencies"][0]
    archive = ROOT / "vendor" / dependency["archive"]
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != dependency["sha256"]:
        raise ValueError("archive checksum mismatch")
    print(f"Verified {archive.name}: {digest}")
    action = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if action == "verify":
        return
    if action not in {"inspect", "extract"}:
        raise ValueError("usage: vendor.py [verify|inspect|extract]")
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        size = sum(member.size for member in members)
        if len(members) > 50000 or size > 1_000_000_000:
            raise ValueError("archive exceeds extraction bounds")
        print(f"Archive entries: {len(members)}; unpacked bytes: {size}")
        if action == "inspect":
            return
        destination = ROOT / "vendor" / "upstream"
        if destination.exists():
            raise ValueError("extraction destination already exists; refusing overwrite")
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir() or member.issym()):
                raise ValueError(f"unsafe archive member: {member.name}")
            if member.issym():
                target = (destination / path.parent / member.linkname).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise ValueError(f"escaping symbolic link: {member.name}")
        destination.mkdir()
        source.extractall(destination, members=members, filter="data")
        print(f"Extracted upstream source to {destination}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, tarfile.TarError) as error:
        print(f"vendor: {error}", file=sys.stderr)
        sys.exit(1)