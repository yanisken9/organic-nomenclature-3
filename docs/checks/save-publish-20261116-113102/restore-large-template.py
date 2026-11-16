"""Restore losslessly encoded checkpoint files; importing this module is read-only."""

from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import re
import tempfile


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def safe_path(root, name):
    relative = Path(name)
    require(not relative.is_absolute() and bool(relative.parts)
            and ".." not in relative.parts and ".git" not in relative.parts,
            "Unsafe restoration path: " + str(name))
    path = root
    for part in relative.parts:
        path = path / part
        require(not path.is_symlink(), "Symlink in restoration path: " + str(name))
    require(path.parent.resolve().is_relative_to(root), "Restoration path escapes root")
    return path


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def restore(root):
    root = Path(root).resolve(strict=True)
    manifest = json.loads(safe_path(root, "_namelecule_checkpoint_restore/manifest.json")
                          .read_text(encoding="utf-8"))
    require(manifest.get("format") == 1, "Unsupported restoration manifest")
    restored, present, seen = [], [], set()
    for entry in manifest["encodedLargeFiles"]:
        name = entry["path"]
        require(name not in seen, "Duplicate restoration path: " + name)
        seen.add(name)
        require(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is not None
                and re.fullmatch(r"[0-9a-f]{64}", entry["gzipSHA256"]) is not None,
                "Invalid restoration digest")
        require(type(entry["bytes"]) is int and entry["bytes"] >= 0
                and type(entry["mode"]) is int and 0 <= entry["mode"] <= 0o777,
                "Invalid restoration size or mode")
        require(manifest["originalFiles"].get(name) == entry["sha256"],
                "Restoration digest does not match original manifest")
        require(entry["gzip"].startswith("_namelecule_checkpoint_restore/large/"),
                "Unexpected compressed-file location")
        destination = safe_path(root, name)
        compressed = safe_path(root, entry["gzip"])
        require(compressed.is_file() and digest(compressed) == entry["gzipSHA256"],
                "Compressed bytes differ: " + name)
        if destination.exists():
            require(destination.is_file() and destination.stat().st_size == entry["bytes"]
                    and digest(destination) == entry["sha256"]
                    and destination.stat().st_mode & 0o777 == entry["mode"],
                    "Refusing to replace an existing different file: " + name)
            present.append(name)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        safe_path(root, name)
        descriptor, temporary = tempfile.mkstemp(prefix=".namelecule-restore-",
                                                dir=destination.parent)
        temporary = Path(temporary)
        try:
            count = 0
            checksum = hashlib.sha256()
            with os.fdopen(descriptor, "wb") as output, gzip.open(compressed, "rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    count += len(chunk)
                    require(count <= entry["bytes"], "Expanded file exceeds recorded size")
                    checksum.update(chunk)
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            require(count == entry["bytes"] and checksum.hexdigest() == entry["sha256"],
                    "Expanded bytes differ: " + name)
            os.chmod(temporary, entry["mode"])
            safe_path(root, name)
            os.link(temporary, destination)  # Exclusive publication; never replaces a file.
            require(digest(destination) == entry["sha256"], "Published restoration differs")
            restored.append(name)
        finally:
            temporary.unlink(missing_ok=True)
    return {"restored": restored, "alreadyPresent": present,
            "encodedLargeFilesVerified": len(seen), "allVerified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(restore(args.root), ensure_ascii=False))


if __name__ == "__main__":
    main()
