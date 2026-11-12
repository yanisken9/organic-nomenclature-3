"""Explicit Nov10 save operations; no action on import, network or source Git writes.

Uses the existing verified copy/ZIP/bundle primitives. Runtime is frozen; later
receipts are captured by a separate delta rather than pretending self-inclusion.
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
STATE = ROOT / "communication/checkpoints/save-publish-20261110-state.json"


def helpers():
    spec = importlib.util.spec_from_file_location("saved_primitives", ROOT / "communication/checkpoints/save-helper-20261105.py")
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    h.REPORT_REL = "docs/professor-20261110"
    return h


def write(path, value):
    helpers().atomic_bytes(helpers().json_bytes(value), path, replace=True)


def invariant(s):
    h = helpers()
    assert h.git(ROOT, "rev-parse", "HEAD").decode().strip() == s["activeHead"]
    assert h.git(ROOT, "branch", "--show-current").decode().strip() == s["activeBranch"]
    index = Path(os.fsdecode(h.git(ROOT, "rev-parse", "--git-path", "index")).strip())
    assert h.sha(index if index.is_absolute() else ROOT / index) == s["indexSHA256"]
    for p, digest in {**s["baselineRuntime"], **s["coreBaseline"], **s["runtimeOverlay"]}.items():
        assert h.sha(ROOT / p) == digest, p


def clone(s):
    c = Path(s["checkpointClone"]).resolve()
    assert c.is_relative_to(Path(s["job"]).resolve()) and not c.is_relative_to(ROOT)
    assert (c / ".git").is_dir() and not (c / ".git").is_symlink()
    assert helpers().git(c, "rev-parse", "--show-toplevel").decode().strip() == str(c)
    return c


def commit_snapshot(s, paths, hashes):
    h = helpers()
    c = clone(s)
    assert not h.git(c, "status", "--porcelain", "-z")
    branch = h.git(c, "branch", "--show-current").decode().strip()
    if branch != s["checkpointBranch"]:
        assert branch == s["previousCheckpointBranch"]
        subprocess.run(["git", "-C", str(c), "checkout", "-q", "-b", s["checkpointBranch"]], check=True)
    old = {os.fsdecode(p) for p in h.git(c, "ls-files", "-z").split(b"\0") if p}
    for p in old - set(paths):
        h.relative_path(c, p).unlink(missing_ok=True)
    for p, digest in hashes.items():
        h.verified_copy(h.relative_path(ROOT, p), h.relative_path(c, p), replace=True, expected=digest)
    subprocess.run(["git", "-C", str(c), "add", "-A"], check=True)
    subprocess.run(["git", "--literal-pathspecs", "-C", str(c), "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul"],
                   input=("\0".join(paths) + "\0").encode(), check=True)
    h.verify_staged_bytes(c, hashes)
    subprocess.run(["git", "-C", str(c), "commit", "-q", "-m", "Save full Namelecule source and React WIP — 10 November 2026"], check=True)
    assert not h.git(c, "status", "--porcelain", "-z")
    return h.git(c, "rev-parse", "HEAD").decode().strip()


def export_json(s):
    h = helpers()
    source = ROOT / "scenarios/alkanes-user-3.scenario.json"
    destination = Path("/Users/yannisskendros/Desktop/αρχεία  json/9Αλκάνια.json")
    before = h.sha(destination) if destination.exists() else None
    recovery = None
    if before and before != h.sha(source):
        recovery = Path(s["externalFolders"][1]) / ("9Αλκάνια-before-fullsave-" + s["stamp"] + ".json")
        h.verified_copy(destination, recovery)
    h.verified_copy(source, destination, replace=True)
    result = {"source": str(source), "destination": str(destination), "sha256": h.sha(source),
              "previousSHA256": before, "backupIfDifferent": str(recovery) if recovery else None,
              "identicalBytesVerified": h.sha(source) == h.sha(destination)}
    write(ROOT / "communication/checkpoints/alkanes-json-export-20261110-fullsave.json", result)
    return result


def copy_package(s, artifacts):
    h = helpers()
    lessons, counts = h.lesson_inventory(ROOT)
    app, app_files = h.launcher_inventory(ROOT, s)
    report = ROOT / s["reportDirectory"]
    copies = []
    for folder in s["externalFolders"]:
        d = Path(folder)
        d.mkdir(parents=True, exist_ok=True)
        files = {}
        for p in artifacts:
            p = Path(p)
            files[p.name] = h.verified_copy(p, d / p.name)
            files[p.name + ".sha256"] = h.atomic_bytes((files[p.name] + "  " + p.name + "\n").encode(), d / (p.name + ".sha256"))
        for name, data in h.portable_report(ROOT, s["reportLink"]).items():
            p = "Αναφορά καθηγητή/" + name
            files[p] = h.atomic_bytes(data, d / p, replace=True)
        for p in ("links.json", "links.txt", "message-to-professor.txt"):
            files[p] = h.verified_copy(report / p, d / p, replace=True)
        for label, url in (("Namelecule — Υποδοχή", s["finalLink"]), ("Αναφορά καθηγητή", s["reportLink"])):
            p = label + ".webloc"
            files[p] = h.atomic_bytes(plistlib.dumps({"URL": url}), d / p, replace=True)
        for name in lessons + [h.PILOT_REL]:
            p = ("Σενάρια JSON/" if name in lessons else "Χωριστός πιλότος/") + Path(name).name
            files[p] = h.verified_copy(ROOT / name, d / p, replace=True)
        for name in ("SESSION-NOTES.md", "YANNIS-CONTRIBUTIONS.md"):
            files[name] = h.verified_copy(ROOT / "docs" / name, d / name, replace=True)
        for path in app_files:
            p = "Namelecule.app/" + path.relative_to(app).as_posix()
            files[p] = h.verified_copy(path, d / p, replace=True)
        text = ("Namelecule — Συνολική αποθήκευση 10/11/2026\n" + s["finalLink"] + "\n" + s["reportLink"] +
                "\nΠλήρες αντίγραφο πηγών με React WIP, όχι ελεγμένο offline πακέτο συνεδρίου.\n"
                "14 ενεργά μαθήματα / 328 βήματα. Χωριστός παλιός πιλότος.\n"
                "Τα μεταγενέστερα receipts καταγράφονται σε χωριστό delta. Τα παλιότερα αντίγραφα διατηρούνται.\n"
                "Τα δύο αντίγραφα φακέλων βρίσκονται στον ίδιο υπολογιστή, όχι σε δύο φυσικούς δίσκους.\n")
        files["ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt"] = h.atomic_bytes(text.encode(), d / "ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt", replace=True)
        assert all(h.sha(d / p) == digest for p, digest in files.items())
        copies.append({"directory": str(d), "files": files, "allHashesVerified": True})
    return copies


def save():
    h = helpers()
    s = json.loads(STATE.read_text())
    invariant(s)
    assert s.get("candidateBrowserPassed") is True
    assert not s.get("saveComplete")
    s["currentAlkaneJSONExport"] = export_json(s)
    paths = h.source_paths(ROOT)
    recovery = h.recovery_paths(ROOT)
    assert not h.secret_findings(ROOT, sorted(set(paths + recovery)))
    assert max((ROOT / p).stat().st_size for p in paths) < 90 * 1024 * 1024
    hashes = {p: h.sha(ROOT / p) for p in paths}
    recovery_hashes = {p: h.sha(ROOT / p) for p in recovery}
    commit = commit_snapshot(s, paths, hashes)
    invariant(s)
    assert all(h.sha(ROOT / p) == digest for p, digest in hashes.items())
    cutoff = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest = {"date": s["date"], "cutoffUTC": cutoff, "checkpointSnapshotCommit": commit,
                "files": hashes, "recoveryFiles": recovery_hashes, "coreChangedThisSave": False,
                "scope": "All tracked/nonignored source plus explicit React public/dist; ignored communication saved separately, old archives/private Git/browserprofiles excluded. Later notes/receipts have separate delta."}
    stem = "Namelecule-" + s["stamp"] + "-full"
    artifacts = [ROOT / "communication/checkpoints" / (stem + x) for x in (".zip", ".bundle", "-recovery.zip")]
    h.create_zip(ROOT, hashes, artifacts[0], manifest)
    h.create_bundle(clone(s), artifacts[1])
    h.create_zip(ROOT, recovery_hashes, artifacts[2], {"files": recovery_hashes, "cutoffUTC": cutoff}, prefix="")
    assert all(h.sha(ROOT / p) == digest for p, digest in hashes.items())
    copies = copy_package(s, artifacts)
    s.update(saveComplete=True, checkpointSnapshotCommit=commit, latestLocalCheckpointCommit=commit,
             sourceFileCount=len(paths), sourceCutoffUTC=cutoff, sourceHashes=hashes,
             recoveryHashes=recovery_hashes, archives={str(p.relative_to(ROOT)): h.sha(p) for p in artifacts},
             sourceZIPAllHashesAndCRCVerified=True, bundleVerified=True, recoveryFiles=len(recovery),
             externalCopies=copies, coreChangedSinceSaveStart=False, sourceHeadIndexPreserved=True,
             secretPatternFindings=[], secretScanLimit="Recognizable byte patterns, not complete security audit",
             fullCheckpointRemoteUploaded=False)
    write(STATE, s)
    receipt = ROOT / "communication/checkpoints" / (stem + "-save-state.json")
    write(receipt, s)
    for copy in copies:
        h.verified_copy(receipt, Path(copy["directory"]) / receipt.name)
    invariant(s)
    print(json.dumps({"snapshotCommit": commit, "sourceFiles": len(paths), "archives": s["archives"],
                      "externalVerified": len(copies), "desktopJSONMatches": s["currentAlkaneJSONExport"]["identicalBytesVerified"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    save()
