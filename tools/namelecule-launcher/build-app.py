"""Build a standalone macOS launcher bundle, leaving app source untouched."""

import argparse
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile


def make_icon(source, root, resources):
    with tempfile.TemporaryDirectory(prefix="namelecule-icon-") as temporary:
        folder = Path(temporary)
        square = folder / "logo-square.png"
        subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", str(source / "make-icon.js"),
                        str(root / "design/assets/namelecule-methane-v1.png"), str(square)], check=True)
        iconset = folder / "Namelecule.iconset"
        iconset.mkdir()
        for size in (16, 32, 128, 256, 512):
            for multiplier in (1, 2):
                suffix = "@2x" if multiplier == 2 else ""
                name = "icon_%dx%d%s.png" % (size, size, suffix)
                pixels = str(size * multiplier)
                subprocess.run(["/usr/bin/sips", "-z", pixels, pixels, str(square),
                                "--out", str(iconset / name)], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["/usr/bin/iconutil", "-c", "icns", str(iconset),
                        "-o", str(resources / "namelecule.icns")], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    root = source.parent.parent
    destination = args.destination.expanduser().resolve()
    if destination.exists():
        parser.error("Destination already exists; it will not be overwritten.")
    if destination.suffix != ".app":
        parser.error("Destination must end in .app")
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["/usr/bin/osacompile", "-o", str(destination),
                    str(source / "launch.applescript")], check=True)
    resources = destination / "Contents/Resources"
    make_icon(source, root, resources)
    shutil.copy2(source / "launcher.py", resources / "launcher.py")
    (resources / "project.json").write_text(
        json.dumps({"project_root": str(root)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    info_path = destination / "Contents/Info.plist"
    with info_path.open("rb") as handle:
        info = plistlib.load(handle)
    info.update({"CFBundleIdentifier": "local.namelecule.launcher",
                 "CFBundleName": "Namelecule", "CFBundleDisplayName": "Namelecule",
                 "CFBundleIconFile": "namelecule.icns",
                 "CFBundleShortVersionString": "1.0",
                 "NSDesktopFolderUsageDescription": "Το Namelecule διαβάζει τον φάκελο της εφαρμογής στην Επιφάνεια Εργασίας για να την ανοίξει στο Firefox."})
    with info_path.open("wb") as handle:
        plistlib.dump(info, handle)
    # Finder/iCloud can attach directory metadata to a newly built Desktop app.
    attributes = subprocess.check_output(["/usr/bin/xattr", str(destination)], text=True).splitlines()
    if "com.apple.FinderInfo" in attributes:
        subprocess.run(["/usr/bin/xattr", "-d", "com.apple.FinderInfo", str(destination)], check=True)
    # osacompile signs the initial bundle; resource/plist additions require a
    # fresh local signature so macOS can identify the completed launcher.
    subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", str(destination)], check=True)
    print(destination)


if __name__ == "__main__":
    main()
