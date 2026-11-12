"""Explicit Nov9 save, using the previously verified archive/copy primitives.

No work executes on import. No network, push, publication or source Git writes.
The source cutoff precedes receipts; final bookkeeping is captured separately.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import plistlib
import subprocess

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "communication/checkpoints/save-publish-20261109-state.json"


def primitives():
    spec = importlib.util.spec_from_file_location(
        "verified_save_20261105", ROOT / "communication/checkpoints/save-helper-20261105.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args])


def invariant(state):
    assert git(ROOT, "rev-parse", "HEAD").decode().strip() == state["activeHead"]
    assert git(ROOT, "branch", "--show-current").decode().strip() == state["activeBranch"]
    index = Path(os.fsdecode(git(ROOT, "rev-parse", "--git-path", "index")).strip())
    assert sha(index if index.is_absolute() else ROOT / index) == state["indexSHA256"]
    for name, digest in state["sourceRuntimeHashes"].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in state["coreBaseline"].items():
        assert sha(ROOT / name) == digest, name


def write_json(helper, path, value, replace=False):
    helper.atomic_bytes(helper.json_bytes(value), path, replace=replace)


def save():
    helper = primitives()
    state = json.loads(STATE.read_text())
    invariant(state)
    assert state.get("publicLiveVerified") is True
    assert state.get("independentReviewComplete") is True
    clone = Path(state["checkpointClone"]).resolve()
    job = Path(state["job"]).resolve()
    assert clone.is_relative_to(job) and not clone.is_relative_to(ROOT)
    assert (clone / ".git").is_dir() and not (clone / ".git").is_symlink()
    assert Path(git(clone, "rev-parse", "--show-toplevel").decode().strip()).resolve() == clone
    assert git(clone, "branch", "--show-current").decode().strip() == state["checkpointBranch"]
    assert not git(clone, "status", "--porcelain", "-z")
    paths = helper.source_paths(ROOT)
    hashes = {p: sha(helper.relative_path(ROOT, p)) for p in paths}
    recovery = helper.recovery_paths(ROOT)
    recovery_hashes = {p: sha(helper.relative_path(ROOT, p)) for p in recovery}
    findings = helper.secret_findings(ROOT, sorted(set(paths + recovery)))
    assert not findings, "Recognizable secret patterns; paths only: " + json.dumps(findings)
    assert max((ROOT / p).stat().st_size for p in paths) < 90 * 1024 * 1024
    lessons, counts = helper.lesson_inventory(ROOT)
    launcher, launcher_files = helper.launcher_inventory(ROOT, state)
    stem = "Namelecule-" + state["stamp"] + "-final"
    artifacts = [ROOT / "communication/checkpoints" / (stem + suffix)
                 for suffix in (".zip", ".bundle", "-recovery.zip")]
    assert all(not p.exists() for p in artifacts)
    old = {os.fsdecode(p) for p in git(clone, "ls-files", "-z").split(b"\0") if p}
    for name in old - set(paths):
        helper.relative_path(clone, name).unlink(missing_ok=True)
    for name, digest in hashes.items():
        helper.verified_copy(helper.relative_path(ROOT, name), helper.relative_path(clone, name),
                             replace=True, expected=digest)
    subprocess.run(["git", "-C", str(clone), "add", "-A"], check=True)
    subprocess.run(["git", "--literal-pathspecs", "-C", str(clone), "add", "-f",
                    "--pathspec-from-file=-", "--pathspec-file-nul"],
                   input=b"\0".join(os.fsencode(p) for p in paths) + b"\0", check=True)
    helper.verify_staged_bytes(clone, hashes)
    subprocess.run(["git", "-C", str(clone), "commit", "--quiet", "-m",
                    "Save complete Namelecule snapshot — 9 November 2026"], check=True)
    commit = git(clone, "rev-parse", "HEAD").decode().strip()
    assert not git(clone, "status", "--porcelain", "-z")
    invariant(state)
    assert all(sha(ROOT / p) == digest for p, digest in hashes.items())
    cutoff = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest = {"date": "2026-11-09", "files": hashes, "checkpointSnapshotCommit": commit,
                "publicReleaseCommit": state["publicReleaseCommit"], "cutoffUTC": cutoff,
                "activeTheoryLessons": counts, "coreChanged": False,
                "scope": "Tracked+nonignored untracked source, explicit React dist/public; includes React WIP. Git/private ignored files and earlier communication archives excluded. Receipts follow this cutoff."}
    helper.create_zip(ROOT, hashes, artifacts[0], manifest)
    helper.create_bundle(clone, artifacts[1])
    helper.create_zip(ROOT, recovery_hashes, artifacts[2],
                      {"date": "2026-11-09", "files": recovery_hashes}, prefix="")
    assert all(sha(ROOT / p) == digest for p, digest in hashes.items())
    invariant(state)
    copies = []
    for folder in state["externalFolders"]:
        destination = Path(folder)
        assert destination.is_absolute() and not destination.resolve().is_relative_to(ROOT)
        destination.mkdir(parents=True, exist_ok=True)
        copied = {}
        for artifact in artifacts:
            copied[artifact.name] = helper.verified_copy(artifact, destination / artifact.name)
            sidecar = artifact.name + ".sha256"
            copied[sidecar] = helper.atomic_bytes(
                (copied[artifact.name] + "  " + artifact.name + "\n").encode(), destination / sidecar)
        for name in lessons + [helper.PILOT_REL]:
            relative = ("Σενάρια JSON/" if name in lessons else "Χωριστός πιλότος/") + Path(name).name
            copied[relative] = helper.verified_copy(ROOT / name, destination / relative, replace=True)
        for name in ("SESSION-NOTES.md", "YANNIS-CONTRIBUTIONS.md"):
            copied[name] = helper.verified_copy(ROOT / "docs" / name, destination / name, replace=True)
        for path in launcher_files:
            relative = "Namelecule.app/" + path.relative_to(launcher).as_posix()
            copied[relative] = helper.verified_copy(path, destination / relative, replace=True)
        copied["links.txt"] = helper.atomic_bytes((state["finalLink"] + "\n").encode(),
                                                    destination / "links.txt", replace=True)
        copied["Namelecule — Υποδοχή.webloc"] = helper.atomic_bytes(
            plistlib.dumps({"URL": state["finalLink"]}), destination / "Namelecule — Υποδοχή.webloc", replace=True)
        readme = ("Namelecule — Συνολική αποθήκευση 9/11/2026\n" + state["finalLink"] +
                  "\nCheckpoint: " + commit + "\n14 ενεργά μαθήματα / 328 βήματα.\n"
                  "Πλήρες αντίγραφο πηγών με React WIP, όχι ελεγμένο offline πακέτο συνεδρίου.\n"
                  "Τα μεταγενέστερα receipts/bookkeeping έχουν χωριστό χρονικό όριο.\n")
        copied["ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt"] = helper.atomic_bytes(readme.encode(), destination / "ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt", replace=True)
        assert all(sha(destination / p) == digest for p, digest in copied.items())
        copies.append({"directory": str(destination), "files": copied, "allHashesVerified": True})
    current_json = ROOT / "scenarios/alkanes-user-3.scenario.json"
    desktop_json = Path("/Users/yannisskendros/Desktop/αρχεία  json/9Αλκάνια.json")
    if desktop_json.exists() and sha(desktop_json) != sha(current_json):
        recovery_copy = Path(state["externalFolders"][1]) / ("9Αλκάνια-before-fullsave-" + state["stamp"] + ".json")
        helper.verified_copy(desktop_json, recovery_copy)
    helper.verified_copy(current_json, desktop_json, replace=True)
    export = {"source": str(current_json), "destination": str(desktop_json),
              "sha256": sha(current_json), "identicalBytesVerified": sha(current_json) == sha(desktop_json)}
    write_json(helper, ROOT / "communication/checkpoints/alkanes-json-export-20261109-fullsave.json", export)
    state.update(saveComplete=True, checkpointSnapshotCommit=commit, latestLocalCheckpointCommit=commit,
                 sourceFileCount=len(paths), sourceCutoffUTC=cutoff,
                 archives={str(p.relative_to(ROOT)): sha(p) for p in artifacts},
                 sourceZIPAllHashesAndCRCVerified=True, bundleVerified=True,
                 recoveryFiles=len(recovery), externalCopies=copies, launcherFiles=len(launcher_files),
                 activeTheoryLessons=counts, currentAlkaneJSONExport=export,
                 coreChangedSinceSessionStart=False, sourceHeadIndexPreserved=True,
                 fullCheckpointRemoteUploaded=False,
                 secretPatternFindings=[], secretScanLimit="Pattern scan is not a complete secret audit")
    write_json(helper, STATE, state, replace=True)
    receipt = ROOT / "communication/checkpoints" / (stem + "-save-state.json")
    write_json(helper, receipt, state)
    for copy in copies:
        helper.verified_copy(receipt, Path(copy["directory"]) / receipt.name)
    invariant(state)
    print(json.dumps({"snapshotCommit": commit, "sourceFiles": len(paths),
                      "archives": state["archives"], "externalVerified": len(copies),
                      "desktopJSONMatches": export["identicalBytesVerified"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    save()
