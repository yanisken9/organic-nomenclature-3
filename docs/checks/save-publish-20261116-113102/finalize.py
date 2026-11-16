"""Explicit final metadata capture/delivery; import performs no saves or Git writes.

The full source/recovery ZIPs plus this metadata delta restore original paths.
The Git checkpoint uses reversible encoding for blobs above the hosting limit.
Closing receipts deliberately follow the archive cutoff.
"""

from pathlib import Path
import concurrent.futures
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


def finish():
    s = o.load()
    o.invariant(s)
    assert s.get("saveComplete") and s.get("publicRuntimeLiveVerified")
    assert s.get("reportLiveVerified") and s.get("independentReviewComplete")
    assert not s.get("finalMetadataCaptured")
    clone = o.ownclone(s, "checkpointClone")
    assert h.git(clone, "rev-parse", "HEAD").decode().strip() == s["checkpointSnapshotCommit"]
    assert not h.git(clone, "status", "--porcelain", "-z")
    source = h.source_paths(R)
    recovery = h.recovery_paths(R)
    paths = sorted(set(source) | set(recovery))
    frozen = Path(s["job"]) / "frozen-final-metadata"
    assert not frozen.exists()
    frozen.mkdir()

    def freeze_one(name):
        return name, o.copydata(h.relative_path(R, name), h.relative_path(frozen, name))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        original = dict(pool.map(freeze_one, paths))
    assert not h.secret_findings(frozen, paths)
    modes = {name: (frozen / name).stat().st_mode & 0o777 for name in paths}
    stored, representation = o.checkpoint_projection(s, frozen, original, record=False)
    stored_modes = {name: (frozen / name).stat().st_mode & 0o777 for name in stored}
    old = {os.fsdecode(name) for name in h.git(clone, "ls-files", "-z").split(b"\0") if name}
    for name in sorted(old - set(stored)):
        h.relative_path(clone, name).unlink(missing_ok=True)
    for name, checksum in stored.items():
        path = h.relative_path(clone, name)
        if (not path.is_file() or o.sha(path) != checksum
                or path.stat().st_mode & 0o777 != stored_modes[name]):
            h.verified_copy(h.relative_path(frozen, name), path, replace=True, expected=checksum)
        assert path.stat().st_mode & 0o777 == stored_modes[name], name
    subprocess.run(["git", "-C", str(clone), "add", "-A"], check=True)
    subprocess.run(["git", "--literal-pathspecs", "-C", str(clone), "add", "-f",
                    "--pathspec-from-file=-", "--pathspec-file-nul"],
                   input=b"\0".join(os.fsencode(name) for name in stored) + b"\0", check=True)
    h.verify_staged_bytes(clone, stored)
    for row in h.git(clone, "ls-files", "-s", "-z").split(b"\0"):
        if row:
            metadata, name = row.split(b"\t", 1)
            mode = metadata.split()[0]
            assert (mode == b"100755") == bool(stored_modes[os.fsdecode(name)] & 0o111)
    subprocess.run(["git", "-C", str(clone), "commit", "--quiet", "-m",
                    "Save final professor report and verified delivery receipts — 16 November 2026"],
                   check=True)
    assert not h.git(clone, "status", "--porcelain", "-z")
    commit = h.git(clone, "rev-parse", "HEAD").decode().strip()
    cutoff = datetime.datetime.now(datetime.timezone.utc).isoformat()
    baseline = {**s["sourceHashes"], **s["recoveryHashes"]}
    previous_frozen = Path(s["frozenSource"])
    delta = {name: value for name, value in original.items()
             if baseline.get(name) != value or not (previous_frozen / name).is_file()
             or (previous_frozen / name).stat().st_mode & 0o777 != modes[name]}
    prefix = R / "communication/checkpoints" / ("Namelecule-" + s["stamp"] + "-final-metadata")
    archive, bundle = Path(str(prefix) + ".zip"), Path(str(prefix) + ".bundle")
    h.create_zip(frozen, delta, archive, {
        "cutoffUTC": cutoff, "baseSnapshot": s["checkpointSnapshotCommit"],
        "metadataCommit": commit, "files": delta, "fullFinalTree": original,
        "fullFinalStoredTree": stored, "fullFinalModes": modes,
        "checkpointRepresentation": representation,
        "deletions": sorted(set(baseline) - set(original)),
        "note": "Original-path delta after full source/recovery ZIPs. Closing receipts follow this cutoff."
    })
    assert not bundle.exists()
    temporary = bundle.with_name("." + bundle.name + ".partial")
    assert not temporary.exists()
    try:
        subprocess.run(["git", "-C", str(clone), "bundle", "create", str(temporary),
                        s["checkpointBranch"], "^" + s["checkpointSnapshotCommit"]], check=True)
        subprocess.run(["git", "-C", str(clone), "bundle", "verify", str(temporary)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        h.publish_temporary(temporary, bundle)
    finally:
        temporary.unlink(missing_ok=True)
    assert set(h.source_paths(R)) | set(h.recovery_paths(R)) == set(original)
    assert all(o.sha(R / name) == value and (R / name).stat().st_mode & 0o777 == modes[name]
               for name, value in original.items())
    o.invariant(s)
    updated = o.package(s, [archive, bundle], frozen)
    before = {record["directory"]: record for record in s["externalCopies"]}
    for record in updated:
        record["files"] = {**before[record["directory"]]["files"], **record["files"]}
        assert all(o.sha(Path(record["directory"]) / name) == value
                   for name, value in record["files"].items())
    s.update(finalMetadataCaptured=True, latestLocalCheckpointCommit=commit,
             finalMetadataCutoffUTC=cutoff, finalMetadataFileCount=len(delta),
             finalCheckpointTreeFiles=len(original), finalCheckpointStoredFiles=len(stored),
             finalOriginalHashes=original, finalStoredHashes=stored,
             finalOriginalModes=modes, finalStoredModes=stored_modes,
             finalSourcePaths=source, finalRecoveryPaths=recovery,
             finalCheckpointRepresentation=representation, frozenFinalMetadata=str(frozen),
             finalMetadataArchives={str(path.relative_to(R)): o.sha(path)
                                    for path in [archive, bundle]},
             incrementalBundlePrerequisite=s["checkpointSnapshotCommit"],
             externalCopies=updated, closingReceiptOutsideArchiveCutoffs=True)
    o.write(o.STATE, s)
    receipt = Path(str(prefix) + "-receipt.json")
    o.write(receipt, s)
    for directory in s["externalFolders"]:
        h.verified_copy(receipt, Path(directory) / receipt.name)
    o.invariant(s)
    print(json.dumps({"metadataCommit": commit, "finalTreeFiles": len(original),
                      "storedTreeFiles": len(stored), "deltaFiles": len(delta),
                      "verifiedFolders": len(updated)}, ensure_ascii=False), flush=True)


def push():
    s = o.load()
    o.invariant(s)
    assert s.get("finalMetadataCaptured") and s.get("independentReviewComplete")
    clone = o.ownclone(s, "checkpointClone")
    head = h.git(clone, "rev-parse", "HEAD").decode().strip()
    assert head == s["latestLocalCheckpointCommit"]
    recovery = json.loads(o.exact(H / "combined-bundle-recovery.json"))
    assert recovery.get("fullBundlePlusIncrementalRecoveryVerified")
    assert recovery["finalCommit"] == head and recovery.get("allOriginalFilesSHA256Verified")
    assert recovery["storedTreeFiles"] == len(s["finalStoredHashes"])
    branch = s["checkpointBranch"]
    remote = h.git(clone, "ls-remote", "origin", "refs/heads/" + branch).decode().split()[0]
    assert remote in [s["checkpointSnapshotCommit"], head], "Checkpoint remote unexpectedly advanced"
    subprocess.run(["git", "-C", str(clone), "push", "origin", "HEAD:refs/heads/" + branch],
                   check=True)
    assert h.git(clone, "ls-remote", "origin", "refs/heads/" + branch).decode().split()[0] == head
    s.update(finalCheckpointRemoteVerified=True, latestRemoteCheckpointCommit=head)
    o.write(o.STATE, s)
    receipt = R / "communication/checkpoints" / ("Namelecule-" + s["stamp"] + "-closing-delivery.json")
    o.write(receipt, {
        "recordedUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "publicRuntimeCommit": s["publicRuntimeCommit"], "publicReportCommit": s["publicReportCommit"],
        "checkpointCommit": head, "report": s["reportLink"], "welcome": s["finalLink"],
        "sourceCutoffUTC": s["sourceCutoffUTC"], "finalMetadataCutoffUTC": s["finalMetadataCutoffUTC"],
        "archives": {**s["archives"], **s["finalMetadataArchives"]},
        "coreChanged": False, "receiptOutsideArchiveCutoffs": True,
        "bundleRecoveryEvidence": str((H / "combined-bundle-recovery.json").relative_to(R))
    })
    for directory in s["externalFolders"]:
        h.verified_copy(receipt, Path(directory) / receipt.name)
    o.invariant(s)
    print(json.dumps({"remoteCheckpoint": head, "closingReceipt": str(receipt)}), flush=True)


if __name__ == "__main__":
    {"finish": finish, "push": push}[sys.argv[1]]()
