"""Explicitly invoked full save; import is read-only and has no side effects.

Adapted from save-helper-20261101.py. All Git writes target the disposable
checkpoint clone. No push, download, source staging, checkout or publication.
The source ZIP is the snapshot before receipt/bookkeeping updates; its manifest
identifies that cutoff. The caller owns subsequent bookkeeping and publication.
"""

from pathlib import Path
import argparse
import hashlib
import html
import json
import os
import plistlib
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import uuid
import zipfile


DATE = "2026-11-04"
STATE_REL = "communication/checkpoints/save-publish-20261104-state.json"
REPORT_REL = "docs/professor-20261104"
PILOT_REL = "scenarios/alkanes-name-repair-pilot.scenario.json"
SECRET_PATTERNS = tuple(re.compile(pattern) for pattern in (
    rb"gh[pousr]_[A-Za-z0-9]{30,}",
    rb"github_pat_[A-Za-z0-9_]{30,}",
    rb"AKIA[A-Z0-9]{16}",
    rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
))
ARCHIVE_SUFFIXES = {".zip", ".bundle", ".log", ".sha256"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args, **kwargs):
    return subprocess.check_output(["git", "-C", str(root), *args], **kwargs)


def relative_path(root, name):
    """Reject escapes and symlinked parents before any read, copy or deletion."""
    rel = Path(name)
    require(not rel.is_absolute() and rel.parts and ".." not in rel.parts,
            "Unsafe relative path: " + str(name))
    require(".git" not in rel.parts, "Git metadata cannot be a source file")
    path = root / rel
    require(path.parent.resolve().is_relative_to(root.resolve()),
            "Path parent escapes repository: " + str(name))
    require(not path.is_symlink(), "Unexpected symlink: " + str(name))
    return path


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def atomic_bytes(data, destination, *, replace=False):
    """Verify temporary bytes, then publish exclusively or replace atomically."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.is_symlink(), "Refusing symlink destination")
    descriptor, temporary = tempfile.mkstemp(prefix=".namelecule-", dir=destination.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        expected = hashlib.sha256(data).hexdigest()
        require(sha(temporary) == expected, "Temporary-file verification failed")
        if replace:
            os.replace(temporary, destination)
        else:
            os.link(temporary, destination)  # Exclusive; existing backups survive.
            temporary.unlink()
        require(sha(destination) == expected, "Written-file verification failed")
    finally:
        temporary.unlink(missing_ok=True)
    return expected


def verified_copy(source, destination, *, replace=False, expected=None):
    source, destination = Path(source), Path(destination)
    require(source.is_file() and not source.is_symlink(), "Invalid copy source: " + str(source))
    expected = expected or sha(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.is_symlink(), "Refusing symlink destination")
    descriptor, temporary = tempfile.mkstemp(prefix=".namelecule-copy-", dir=destination.parent)
    os.close(descriptor)
    temporary = Path(temporary)
    try:
        shutil.copy2(source, temporary)
        require(sha(temporary) == expected, "Copy differs: " + str(source))
        if replace:
            os.replace(temporary, destination)
        else:
            os.link(temporary, destination)
            temporary.unlink()
        require(sha(destination) == expected, "Destination differs: " + str(destination))
    finally:
        temporary.unlink(missing_ok=True)
    return expected


def secret_findings(root, paths):
    """Scan all bytes, including large/binary files; return paths only."""
    findings = []
    for name in paths:
        data = relative_path(root, name).read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            findings.append(name)
    return findings


def source_paths(root):
    names = {os.fsdecode(name) for name in
             git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0")
             if name}
    for directory in ("react-preview/dist", "react-preview/public"):
        base = relative_path(root, directory)
        require(base.is_dir(), "Required React directory missing: " + directory)
        for path in base.rglob("*"):
            require(not path.is_symlink(), "Unexpected React symlink: " + str(path))
            if path.is_file() and path.name != ".DS_Store" and path.suffix != ".log":
                names.add(path.relative_to(root).as_posix())
    # Missing tracked files are intentionally omitted, reproducing source deletions.
    return sorted(name for name in names if relative_path(root, name).is_file())


def recovery_paths(root):
    result = []
    for path in (root / "communication").rglob("*"):
        require(not path.is_symlink(), "Unexpected communication symlink: " + str(path))
        if path.is_file() and path.name != ".DS_Store" and path.suffix not in ARCHIVE_SUFFIXES:
            result.append(path.relative_to(root).as_posix())
    return sorted(result)


def invariant(root, state):
    require(git(root, "rev-parse", "HEAD").decode().strip() == state["activeHead"],
            "Source HEAD changed")
    require(git(root, "branch", "--show-current").decode().strip() == state["activeBranch"],
            "Source branch changed")
    index = Path(os.fsdecode(git(root, "rev-parse", "--git-path", "index")).strip())
    if not index.is_absolute():
        index = root / index
    require(sha(index) == state["indexSHA256"], "Source index changed")
    core52 = state.get("core52SHA256") or state.get("coreSHA256")
    require(bool(core52), "Missing unchanged core52 baseline SHA256")
    require(sha(root / "js/mulermoc-nom-core-52.js") == core52, "Core52 differs from baseline")
    require(sha(root / "js/mulermoc-nom-core-54.js") == state["core54SHA256"],
            "Core54 differs from final reviewed sync SHA256")
    for name, digest in state["sourceRuntimeHashes"].items():
        require(sha(relative_path(root, name)) == digest, "Runtime hash differs: " + name)


def prerequisites(root, state, generation):
    require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", generation) is not None,
            "Invalid generation name")
    for key in ("stamp", "job", "checkpointClone", "checkpointBranch", "activeHead",
                "activeBranch", "indexSHA256", "core54SHA256", "sourceRuntimeHashes", "externalFolders"):
        require(bool(state.get(key)), "Missing state prerequisite: " + key)
    require(re.fullmatch(r"[0-9]{8}-[0-9]{6}", state["stamp"]) is not None, "Invalid stamp")
    require(state.get("clonesReady") is True, "Disposable clones are not ready")
    require(state.get("syncReviewComplete") is True, "Sync review is incomplete")
    require(state.get("upstreamSyncInProgress") is not True, "Upstream sync is still in progress")
    if generation == "initial":
        require(state.get("allowPrepublicationSnapshot") is True,
                "Initial snapshot requires explicit caller state authorization")
    else:
        require(state.get("publicLiveVerified") is True, "Public live release is not verified")
        require(re.fullmatch(r"[0-9a-f]{40}", state.get("publicReleaseCommit", "")) is not None,
                "Missing public release commit")
    folders = [Path(folder) for folder in state["externalFolders"]]
    require(len(folders) == 2 and len({str(folder.resolve()) for folder in folders}) == 2,
            "Two distinct external folders are required")
    require(all(folder.is_absolute() and not folder.resolve().is_relative_to(root)
                for folder in folders), "External folders must be absolute and outside source")
    clone = Path(state["checkpointClone"])
    require(clone.is_absolute() and clone.is_dir() and not clone.is_symlink(),
            "Invalid disposable checkpoint clone")
    clone = clone.resolve()
    job = Path(state["job"]).resolve()
    require(clone.is_relative_to(job) and clone != job and not clone.is_relative_to(root),
            "Checkpoint clone must be inside the dedicated job, outside source")
    require(Path(os.fsdecode(git(clone, "rev-parse", "--show-toplevel")).strip()).resolve() == clone,
            "Checkpoint path is not a repository root")
    clone_git = Path(os.fsdecode(git(clone, "rev-parse", "--absolute-git-dir")).strip()).resolve()
    require(clone_git.is_relative_to(clone) and (clone / ".git").is_dir()
            and not (clone / ".git").is_symlink(), "Clone must own its disposable Git metadata")
    require(git(clone, "branch", "--show-current").decode().strip() == state["checkpointBranch"],
            "Checkpoint branch differs")
    require(not git(clone, "status", "--porcelain", "-z"), "Checkpoint clone is dirty")
    invariant(root, state)
    return clone


def lesson_inventory(root):
    text = (root / "design/theory-library.html").read_text()
    lessons = sorted(set(urllib.parse.unquote(html.unescape(path)) for path in
                         re.findall(r"scenario=(scenarios/[^&\"\s]+)", text)))
    require(len(lessons) == 14, "Expected 14 active theory lessons")
    require(len({Path(name).name for name in lessons}) == 14,
            "Active lesson filenames collide in external JSON folder")
    counts = {name: len(json.loads(relative_path(root, name).read_text())["steps"]) for name in lessons}
    require(sum(counts.values()) == 337, "Expected 337 active theory steps")
    pilot = relative_path(root, PILOT_REL)
    require(pilot.is_file() and PILOT_REL not in lessons, "Separate pilot JSON is missing or active")
    json.loads(pilot.read_text())
    return lessons, counts


def verify_staged_bytes(clone, hashes):
    entries = []
    for row in git(clone, "ls-files", "-s", "-z").split(b"\0"):
        if row:
            metadata, path = row.split(b"\t", 1)
            mode, object_id, stage = metadata.split()
            require(stage == b"0" and mode in (b"100644", b"100755"), "Unsupported staged entry")
            entries.append((os.fsdecode(path), object_id))
    require({path for path, _ in entries} == set(hashes), "Staged path set differs")
    process = subprocess.Popen(["git", "-C", str(clone), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for path, object_id in entries:
            process.stdin.write(object_id + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            require(len(header) == 3 and header[1] == b"blob", "Invalid staged blob response")
            remaining = int(header[2])
            digest = hashlib.sha256()
            while remaining:
                chunk = process.stdout.read(min(remaining, 1024 * 1024))
                require(bool(chunk), "Truncated staged blob")
                digest.update(chunk)
                remaining -= len(chunk)
            require(process.stdout.read(1) == b"\n", "Invalid staged blob terminator")
            require(digest.hexdigest() == hashes[path], "Staged bytes changed: " + path)
        process.stdin.close()
        require(process.wait() == 0, "Staged verification process failed")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()


def checkpoint_snapshot(root, clone, paths, hashes, generation):
    old = {os.fsdecode(name) for name in git(clone, "ls-files", "-z").split(b"\0") if name}
    for name in sorted(old - set(paths)):
        relative_path(clone, name).unlink(missing_ok=True)
    for name in paths:
        verified_copy(relative_path(root, name), relative_path(clone, name), replace=True,
                      expected=hashes[name])
    subprocess.run(["git", "-C", str(clone), "add", "-A"], check=True)
    subprocess.run(["git", "--literal-pathspecs", "-C", str(clone), "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul"],
                   input=b"\0".join(os.fsencode(name) for name in paths) + b"\0", check=True)
    verify_staged_bytes(clone, hashes)
    subprocess.run(["git", "-C", str(clone), "commit", "--quiet", "--allow-empty", "-m",
                    "Save complete Namelecule " + generation + " snapshot — 4 November 2026"], check=True)
    require(not git(clone, "status", "--porcelain", "-z"), "Checkpoint remains dirty after snapshot")
    return git(clone, "rev-parse", "HEAD").decode().strip()


def publish_temporary(temporary, destination):
    """Publish a previously verified archive, never replacing an existing name."""
    os.link(temporary, destination)
    temporary.unlink()


def create_zip(root, hashes, destination, manifest, prefix="Namelecule/"):
    destination = Path(destination)
    require(not destination.exists(), "Archive already exists: " + str(destination))
    temporary = destination.with_name("." + destination.name + ".partial-" + uuid.uuid4().hex)
    try:
        with zipfile.ZipFile(temporary, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name in hashes:
                archive.write(relative_path(root, name), prefix + name)
            archive.writestr(prefix + "SNAPSHOT-MANIFEST.json", json_bytes(manifest))
        with zipfile.ZipFile(temporary) as archive:
            require(archive.testzip() is None, "ZIP CRC verification failed")
            require(len(archive.namelist()) == len(hashes) + 1, "ZIP contains duplicate entries")
            require(set(archive.namelist()) == {prefix + name for name in hashes} |
                    {prefix + "SNAPSHOT-MANIFEST.json"}, "ZIP path set differs")
            for name, digest in hashes.items():
                require(hashlib.sha256(archive.read(prefix + name)).hexdigest() == digest,
                        "ZIP hash differs: " + name)
        publish_temporary(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def create_bundle(clone, destination):
    require(not destination.exists(), "Bundle already exists: " + str(destination))
    temporary = destination.with_name("." + destination.name + ".partial-" + uuid.uuid4().hex)
    try:
        subprocess.run(["git", "-C", str(clone), "bundle", "create", str(temporary), "--all"],
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(clone), "bundle", "verify", str(temporary)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        publish_temporary(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def portable_report(root, report_url):
    report = root / REPORT_REL
    require(report.is_dir(), "Professor report directory is missing")
    required = ("update.html", "links.json", "links.txt", "message-to-professor.txt")
    require(all((report / name).is_file() for name in required), "Professor report files are incomplete")
    files = {}
    for path in report.rglob("*"):
        require(not path.is_symlink(), "Unexpected professor report symlink")
        if path.is_file() and path.name != ".DS_Store":
            files[path.relative_to(report).as_posix()] = path.read_bytes()
    text = files["update.html"].decode()
    text = re.sub(r'href="([^"#][^"]*)"',
                  lambda match: 'href="' + html.escape(urllib.parse.urljoin(
                      report_url, html.unescape(match.group(1))), quote=True) + '"', text)
    for image_url in set(re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', text)):
        decoded = html.unescape(image_url)
        if urllib.parse.urlsplit(decoded).scheme or decoded.startswith("//"):
            continue
        source = (report / urllib.parse.unquote(urllib.parse.urlsplit(decoded).path)).resolve()
        require(source.is_relative_to(root), "Professor report image escapes source")
        require(source.is_file() and not source.is_symlink(), "Professor report image missing")
        target = "assets/" + sha(source)[:16] + "-" + source.name
        files[target] = source.read_bytes()
        text = text.replace('src="' + image_url + '"', 'src="' + html.escape(target, quote=True) + '"')
    files["update.html"] = text.encode()
    return files


def launcher_inventory(root, state):
    app = Path(state.get("launcherPath", str(root.parent.parent / "Namelecule.app")))
    require(app.is_absolute(), "Launcher path must be absolute")
    files = []
    if app.exists():
        require(app.is_dir() and not app.is_symlink(), "Invalid desktop launcher")
        for path in app.rglob("*"):
            require(not path.is_symlink(), "Unexpected desktop launcher symlink")
            if path.is_file() and path.name != ".DS_Store":
                files.append(path)
        require(len(files) == 10, "Expected 10 files in desktop Namelecule.app")
        findings = secret_findings(app, [path.relative_to(app).as_posix() for path in files])
        require(not findings, "Recognizable launcher secret patterns found; paths only: " + json.dumps(findings))
    return app, files


def copy_external(root, state, generation, commit, artifacts, lessons, step_counts):
    report_dir = root / REPORT_REL
    links = json.loads((report_dir / "links.json").read_text())
    require(all(isinstance(links.get(key), str) and links[key].startswith("https://")
                for key in ("report", "welcome")), "Professor report/welcome links are missing")
    report_files = portable_report(root, links["report"])
    app, app_files = launcher_inventory(root, state)
    copies = []
    for folder in state["externalFolders"]:
        destination = Path(folder)
        destination.mkdir(parents=True, exist_ok=True)
        hashes = {}
        for artifact in artifacts:
            digest = verified_copy(artifact, destination / artifact.name)
            hashes[artifact.name] = digest
            hashes[artifact.name + ".sha256"] = atomic_bytes(
                (digest + "  " + artifact.name + "\n").encode(), destination / (artifact.name + ".sha256"))
        for name, data in report_files.items():
            target = relative_path(destination, "Αναφορά καθηγητή/" + name)
            hashes[target.relative_to(destination).as_posix()] = atomic_bytes(data, target, replace=True)
        for name in ("links.json", "links.txt", "message-to-professor.txt"):
            hashes[name] = verified_copy(report_dir / name, destination / name, replace=True)
        for title, key in (("Αναφορά καθηγητή", "report"), ("Namelecule — Υποδοχή", "welcome")):
            name = title + ".webloc"
            hashes[name] = atomic_bytes(plistlib.dumps({"URL": links[key]}), destination / name, replace=True)
        for name in lessons:
            target = destination / "Σενάρια JSON" / Path(name).name
            hashes[target.relative_to(destination).as_posix()] = verified_copy(root / name, target, replace=True)
        pilot_target = destination / "Πιλοτικό σενάριο — χωριστά από τα 14 μαθήματα" / Path(PILOT_REL).name
        hashes[pilot_target.relative_to(destination).as_posix()] = verified_copy(
            root / PILOT_REL, pilot_target, replace=True)
        pilot_note = "Πιλοτικό σενάριο αποκατάστασης ονόματος. Δεν είναι 15ο ενεργό μάθημα θεωρίας.\n"
        pilot_readme = pilot_target.parent / "ΔΙΑΒΑΣΕ.txt"
        hashes[pilot_readme.relative_to(destination).as_posix()] = atomic_bytes(
            pilot_note.encode(), pilot_readme, replace=True)
        for path in app_files:
            target = destination / "Namelecule.app" / path.relative_to(app)
            hashes[target.relative_to(destination).as_posix()] = verified_copy(path, target, replace=True)
        for name in ("SESSION-NOTES.md", "YANNIS-CONTRIBUTIONS.md"):
            hashes[name] = verified_copy(root / "docs" / name, destination / name, replace=True)
        readme = ("Namelecule — Συνολική αποθήκευση 4/11/2026\nΓενιά: " + generation +
                  "\nΑναφορά: " + links["report"] + "\nΥποδοχή: " + links["welcome"] +
                  "\nCheckpoint πηγών: " + commit + "\n14 ενεργά μαθήματα / 337 βήματα. "
                  "Το πιλοτικό JSON αποθηκεύεται χωριστά.\nΤο πλήρες αντίγραφο πηγών δεν είναι "
                  "ελεγμένο offline πακέτο συνεδρίου. Τα παλιότερα αντίγραφα διατηρούνται.\n")
        hashes["ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt"] = atomic_bytes(readme.encode(), destination / "ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt", replace=True)
        require(all(sha(relative_path(destination, name)) == digest for name, digest in hashes.items()),
                "External final hash verification failed")
        copies.append({"directory": str(destination), "files": hashes, "allHashesVerified": True,
                       "activeScenarioJSON": len(lessons), "activeTheorySteps": sum(step_counts.values()),
                       "separatePilotJSON": PILOT_REL, "launcherFiles": len(app_files),
                       "launcherPresent": app.exists(), "linksAndPortableReportSaved": True})
    return copies


def refresh_receipts(root=None, state=None):
    """Caller may use after separately authorized final bookkeeping.

    Refreshes notes and receipts only; never commits or refreshes a
    bundle silently. The caller must record any bookkeeping commit separately.
    """
    root = Path(root or Path(__file__).resolve().parents[2]).resolve()
    state_path = root / STATE_REL
    state = state if state is not None else json.loads(state_path.read_text())
    invariant(root, state)
    require(state.get("saveComplete") is True, "Cannot refresh an incomplete save")
    archive_dir = root / "communication/checkpoints"
    receipt = archive_dir / ("final-save-state-" + state["stamp"] + ".json")
    for copy in state["externalCopies"]:
        destination = Path(copy["directory"])
        for name in ("SESSION-NOTES.md", "YANNIS-CONTRIBUTIONS.md"):
            copy["files"][name] = verified_copy(root / "docs" / name, destination / name, replace=True)
        for name, digest in copy["files"].items():
            require(sha(relative_path(destination, name)) == digest, "External refresh hash differs: " + name)
    data = json_bytes(state)
    atomic_bytes(data, receipt, replace=True)
    for copy in state["externalCopies"]:
        verified_copy(receipt, Path(copy["directory"]) / "final-save-state.json", replace=True)
    invariant(root, state)
    atomic_bytes(data, state_path, replace=True)
    return state


def save(generation, root=None):
    root = Path(root or Path(__file__).resolve().parents[2]).resolve()
    state_path = root / STATE_REL
    state = json.loads(state_path.read_text())
    clone = prerequisites(root, state, generation)
    archive_dir = root / "communication/checkpoints"
    name = "Namelecule-" + state["stamp"] + "-" + generation
    archive = archive_dir / (name + ".zip")
    bundle = archive_dir / (name + ".bundle")
    recovery = archive_dir / (name + "-recovery.zip")
    generation_receipt = archive_dir / (name + "-save-state.json")
    for path in (archive, bundle, recovery, generation_receipt):
        require(not path.exists(), "Generation output already exists: " + path.name)
    paths = source_paths(root)
    hashes = {path: sha(relative_path(root, path)) for path in paths}
    recovered = recovery_paths(root)
    recovery_hashes = {path: sha(relative_path(root, path)) for path in recovered}
    lessons, step_counts = lesson_inventory(root)
    for required in (*lessons, PILOT_REL, "docs/SESSION-NOTES.md", "docs/YANNIS-CONTRIBUTIONS.md",
                     "js/mulermoc-nom-core-52.js", "js/mulermoc-nom-core-54.js"):
        require(required in hashes, "Required source file missing from snapshot: " + required)
    findings = sorted(set(secret_findings(root, paths + recovered)))
    require(not findings, "Recognizable secret patterns found; paths only: " + json.dumps(findings))
    # Validate report and launcher before creating the checkpoint or archives.
    links = json.loads((root / REPORT_REL / "links.json").read_text())
    require(all(isinstance(links.get(key), str) and links[key].startswith("https://")
                for key in ("report", "welcome")), "Professor report/welcome links are missing")
    portable_report(root, links["report"])
    launcher_inventory(root, state)
    commit = checkpoint_snapshot(root, clone, paths, hashes, generation)
    invariant(root, state)
    require(all(sha(root / path) == digest for path, digest in hashes.items()),
            "Source changed while snapshotting; do not use this generation")
    manifest = {"date": DATE, "generation": generation, "checkpointSnapshotCommit": commit,
                "publicReleaseCommit": state.get("publicReleaseCommit"), "files": hashes,
                "activeTheoryLessons": step_counts, "separatePilotJSON": PILOT_REL,
                "core52SHA256": state.get("core52SHA256") or state.get("coreSHA256"),
                "core54SHA256": state["core54SHA256"],
                "cutoff": "Source bytes before this save's receipts and later bookkeeping updates",
                "exclusions": "Git metadata, ignored dependencies/caches/private settings and old communication archives; React dist/public explicitly included. Communication recovery and desktop launcher copied separately."}
    create_zip(root, hashes, archive, manifest)
    create_bundle(clone, bundle)
    create_zip(root, recovery_hashes, recovery,
               {"date": DATE, "generation": generation, "files": recovery_hashes,
                "exclusions": "Existing ZIP/bundle/log/hash archives and .DS_Store"}, prefix="")
    copies = copy_external(root, state, generation, commit, (archive, bundle, recovery), lessons, step_counts)
    invariant(root, state)
    require(all(sha(root / path) == digest for path, digest in hashes.items()),
            "Source changed during final save; snapshot is incomplete")
    state.update(latestLocalCheckpointCommit=commit, checkpointSnapshotCommit=commit,
                 sourceFileCount=len(paths), archive=str(archive.relative_to(root)), archiveSHA256=sha(archive),
                 bundle=str(bundle.relative_to(root)), bundleSHA256=sha(bundle), bundleVerified=True,
                 recoveryArchive=str(recovery.relative_to(root)), recoveryArchiveSHA256=sha(recovery),
                 recoveryFiles=len(recovered), externalCopies=copies, sourceZIPAllHashesAndCRCVerified=True,
                 coreChangedBySaveHelper=False, core52UnchangedFromBaseline=True,
                 core54MatchesReviewedSync=True, generation=generation,
                 activeBranchHeadIndexPreserved=True, secretPatternScanFindings=[],
                 secretPatternScanScope="All bytes of source and communication recovery files; pattern scan is not a complete secret audit",
                 saveComplete=True)
    atomic_bytes(json_bytes(state), generation_receipt)
    refresh_receipts(root, state)
    print(json.dumps({"generation": generation, "snapshotCommit": commit, "files": len(paths),
                      "ZIP": str(archive), "externalVerified": len(copies),
                      "coreChangedBySaveHelper": False}, ensure_ascii=False), flush=True)
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generation", help="Unique generation; initial additionally needs explicit state flag")
    arguments = parser.parse_args()
    save(arguments.generation)
