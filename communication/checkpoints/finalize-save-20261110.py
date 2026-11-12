"""Capture final report/notes/receipts after the full snapshot's declared cutoff.

No network or source Git writes. The incremental bundle explicitly requires the
earlier full bundle. A closing receipt is outside both archive cutoffs.
"""
from pathlib import Path
import datetime
import importlib.util
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("save_ops", ROOT / "communication/checkpoints/save-helper-20261110.py")
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


def finish():
    h = ops.helpers()
    s = json.loads(ops.STATE.read_text())
    ops.invariant(s)
    assert s["saveComplete"] and s["publicRuntimeLiveVerified"] and s["reportLiveVerified"]
    assert not s.get("finalMetadataCaptured")
    c = ops.clone(s)
    assert h.git(c, "rev-parse", "HEAD").decode().strip() == s["checkpointSnapshotCommit"]
    assert not h.git(c, "status", "--porcelain", "-z")
    # A recovery snapshot preserves source bytes, including CRLF calendar files.
    # Override clean filters in this disposable clone only; the project's tracked
    # attributes and the active checkout must remain unchanged.
    attributes = c / ".git/info/attributes"
    raw_attributes = b"* -text -eol -filter -ident\n"
    assert not attributes.is_symlink()
    if attributes.exists():
        assert attributes.read_bytes() == raw_attributes
    else:
        h.atomic_bytes(raw_attributes, attributes)
    # Include intentionally ignored nonarchive operational records in the final
    # checkpoint, unlike a plain git-ls-files inventory which would omit them.
    paths = sorted(set(h.source_paths(ROOT)) | set(h.recovery_paths(ROOT)))
    assert not h.secret_findings(ROOT, paths)
    hashes = {p: h.sha(ROOT / p) for p in paths}
    assert max((ROOT / p).stat().st_size for p in paths) < 90 * 1024 * 1024
    old = {p.decode() for p in h.git(c, "ls-files", "-z").split(b"\0") if p}
    for p in old - set(paths):
        h.relative_path(c, p).unlink(missing_ok=True)
    for p, digest in hashes.items():
        destination = h.relative_path(c, p)
        if not destination.is_file() or h.sha(destination) != digest:
            h.verified_copy(h.relative_path(ROOT, p), destination, replace=True, expected=digest)
    subprocess.run(["git", "-C", str(c), "add", "-A"], check=True)
    subprocess.run(["git", "--literal-pathspecs", "-C", str(c), "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul"],
                   input=("\0".join(paths) + "\0").encode(), check=True)
    h.verify_staged_bytes(c, hashes)
    subprocess.run(["git", "-C", str(c), "commit", "-q", "-m", "Save final professor report and publication receipts — 10 November 2026"], check=True)
    commit = h.git(c, "rev-parse", "HEAD").decode().strip()
    cutoff = datetime.datetime.now(datetime.timezone.utc).isoformat()
    delta = {p: digest for p, digest in hashes.items() if s["sourceHashes"].get(p) != digest}
    stem = "Namelecule-" + s["stamp"] + "-final-metadata"
    archive = ROOT / "communication/checkpoints" / (stem + ".zip")
    bundle = ROOT / "communication/checkpoints" / (stem + ".bundle")
    manifest = {"cutoffUTC": cutoff, "baseSnapshot": s["checkpointSnapshotCommit"],
                "metadataCommit": commit, "files": delta, "fullFinalTree": hashes,
                "deletionsFromSnapshot": sorted(set(s["sourceHashes"]) - set(hashes)),
                "note": "Apply after full snapshot/recovery. Closing receipt follows this cutoff; archives cannot include their own final hash."}
    h.create_zip(ROOT, delta, archive, manifest)
    assert not bundle.exists()
    temporary = bundle.with_name("." + bundle.name + ".partial")
    assert not temporary.exists()
    subprocess.run(["git", "-C", str(c), "bundle", "create", str(temporary),
                    s["checkpointBranch"], "^" + s["checkpointSnapshotCommit"]], check=True)
    subprocess.run(["git", "-C", str(c), "bundle", "verify", str(temporary)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    h.publish_temporary(temporary, bundle)
    assert all(h.sha(ROOT / p) == digest for p, digest in hashes.items())
    ops.invariant(s)
    updated = ops.copy_package(s, [archive, bundle])
    before = {record["directory"]: record for record in s["externalCopies"]}
    for record in updated:
        record["files"] = {**before[record["directory"]]["files"], **record["files"]}
        assert all(h.sha(Path(record["directory"]) / p) == digest for p, digest in record["files"].items())
    s.update(finalMetadataCaptured=True, latestLocalCheckpointCommit=commit,
             finalMetadataCutoffUTC=cutoff, finalMetadataFileCount=len(delta), finalCheckpointTreeFiles=len(hashes),
             finalMetadataArchives={str(p.relative_to(ROOT)): h.sha(p) for p in [archive, bundle]},
             incrementalBundlePrerequisite=s["checkpointSnapshotCommit"], externalCopies=updated,
             closingReceiptOutsideArchiveCutoffs=True)
    ops.write(ops.STATE, s)
    receipt = ROOT / "communication/checkpoints" / (stem + "-receipt.json")
    ops.write(receipt, s)
    for record in updated:
        h.verified_copy(receipt, Path(record["directory"]) / receipt.name)
    print(json.dumps({"metadataCommit": commit, "finalTreeFiles": len(hashes), "deltaFiles": len(delta),
                      "archives": s["finalMetadataArchives"], "externalVerified": len(updated)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    finish()
