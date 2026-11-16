"""Explicit local bundle recovery test; imports do not create files or run Git."""

from pathlib import Path
import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("release_ops", H / "release-ops.py")
o = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o)
R, h = o.R, o.h
RAW_ATTRIBUTES = b"* -text -eol -filter -ident\n"


def verify(kind):
    assert kind in ("full", "final")
    s = o.load()
    o.invariant(s)
    assert s.get("saveComplete")
    final = kind == "final"
    if final:
        assert s.get("finalMetadataCaptured")
    branch = s["checkpointBranch"]
    stem = "Namelecule-" + s["stamp"]
    bundle = R / "communication/checkpoints" / (stem + "-full.bundle")
    assert o.sha(bundle) == s["archives"][str(bundle.relative_to(R))]
    destination = Path(s["job"]) / ("independent-final-bundle-recovery" if final
                                      else "independent-full-bundle-recovery")
    assert not destination.exists()
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")

    def git(*args):
        return subprocess.check_output(["git", "-c", "core.hooksPath=" + os.devnull,
                                        "-C", str(destination), *args], env=env,
                                       stderr=subprocess.PIPE)

    subprocess.run(["git", "init", "--quiet", str(destination)], env=env, check=True)
    info = destination / ".git/info/attributes"
    info.write_bytes(RAW_ATTRIBUTES)  # Must precede all checkouts.
    git("fetch", "--quiet", "--no-tags", "--no-write-fetch-head", str(bundle),
        "refs/heads/" + branch + ":refs/heads/" + branch)
    assert git("rev-parse", branch).decode().strip() == s["checkpointSnapshotCommit"]
    expected_commit = s["checkpointSnapshotCommit"]
    stored = s["checkpointStoredHashes"]
    original = {**s["sourceHashes"], **s["recoveryHashes"]}
    original_modes = {name: (Path(s["frozenSource"]) / name).stat().st_mode & 0o777
                      for name in original}
    stored_modes = None
    if final:
        incremental = R / "communication/checkpoints" / (stem + "-final-metadata.bundle")
        assert o.sha(incremental) == s["finalMetadataArchives"][str(incremental.relative_to(R))]
        git("bundle", "verify", str(incremental))
        git("fetch", "--quiet", "--no-tags", "--no-write-fetch-head", str(incremental),
            "refs/heads/" + branch + ":refs/heads/" + branch)
        expected_commit = s["latestLocalCheckpointCommit"]
        stored = s["finalStoredHashes"]
        original = s["finalOriginalHashes"]
        original_modes = s["finalOriginalModes"]
        stored_modes = s["finalStoredModes"]
    assert git("rev-parse", branch).decode().strip() == expected_commit
    assert not (destination / ".git/objects/info/alternates").exists()
    assert not git("remote").strip()
    git("checkout", "--quiet", branch)
    assert info.read_bytes() == RAW_ATTRIBUTES
    h.verify_staged_bytes(destination, stored)
    for name, checksum in stored.items():
        path = h.relative_path(destination, name)
        assert o.sha(path) == checksum, name
        if stored_modes is not None:
            assert bool(path.stat().st_mode & 0o111) == bool(stored_modes[name] & 0o111), name
    manifest = json.loads(o.exact(destination / "_namelecule_checkpoint_restore/manifest.json"))
    assert manifest["originalFiles"] == original
    restoration = json.loads(subprocess.check_output(
        [sys.executable, "-B", str(destination / "_namelecule_checkpoint_restore/restore.py")],
        cwd=destination, env=env))
    assert restoration.get("allVerified")
    encoded_names = {entry["path"] for entry in manifest["encodedLargeFiles"]}
    for name, checksum in original.items():
        path = h.relative_path(destination, name)
        assert path.is_file() and o.sha(path) == checksum, name
        assert bool(path.stat().st_mode & 0o111) == bool(original_modes[name] & 0o111), name
        if name in encoded_names:
            assert path.stat().st_mode & 0o777 == original_modes[name], name
    actual = set()
    for directory, directories, files in os.walk(destination):
        if Path(directory) == destination:
            directories.remove(".git")
        for name in files:
            path = Path(directory) / name
            assert not path.is_symlink()
            actual.add(path.relative_to(destination).as_posix())
    assert actual == set(stored) | set(original)
    assert not (destination / ".git/objects/info/alternates").exists()
    o.invariant(s)
    result = {
        "recordedUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repository": str(destination), "fullBundle": str(bundle.relative_to(R)),
        "baseCommit": s["checkpointSnapshotCommit"], "finalCommit": expected_commit,
        "sourceFiles": len(original), "storedTreeFiles": len(stored),
        "allCommittedBlobSHA256MatchManifest": True,
        "allStoredWorktreeFilesSHA256Verified": True,
        "allOriginalFilesSHA256Verified": True, "allGitExecutableBitsVerified": True,
        "restoredEncodedFileModesVerified": True,
        "permissionScope": "Git retains executable bits; full ordinary permission bits are retained in ZIPs/final metadata, not represented by Git tree modes.",
        "restoration": restoration, "networkUsed": False, "alternatesPresent": False,
        "rawAttributesBeforeCheckout": True, "exactRecoveredFileMembership": True,
        "scope": "Developer local object/worktree recovery, including encoded oversized diagnostics; no application/browser execution."
    }
    if final:
        result.update(incrementalBundle=str(incremental.relative_to(R)),
                      deltaFiles=s["finalMetadataFileCount"],
                      fullBundlePlusIncrementalRecoveryVerified=True)
    else:
        result.update(standaloneFullBundleRecoveryVerified=True)
    evidence = H / ("combined-bundle-recovery.json" if final else "standalone-bundle-recovery.json")
    o.write(evidence, result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("full", "final"))
    verify(parser.parse_args().kind)
