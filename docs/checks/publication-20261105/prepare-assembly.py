"""Freeze, assemble and verify a curated public tree; no commit/push/network.

Nothing executes on import. `freeze` writes local evidence only. `assemble`
writes only the dedicated disposable public clone and its local evidence.
"""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from datetime import datetime, timezone
import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
import tempfile
import urllib.parse


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = "docs/checks/publication-20261105"
STATE = "communication/checkpoints/save-publish-20261105-state.json"
MANIFEST = "curated-source-manifest.json"
PUBLIC_PREFIX = "https://yanisken9.github.io/organic-nomenclature-3/"
REPORT = "docs/professor-20261105"
REPORT_FILES = {"update.html", "links.json", "links.txt", "message-to-professor.txt", "verified-facts.json"}
HTML_ENTRIES = ("mulermoc-nom-54.html", "design/welcome-proposal.html",
                "design/theory-library.html", "games/name-repair.html", REPORT + "/update.html")
PILOT = "scenarios/alkanes-name-repair-pilot.scenario.json"
COMPACT = "scenarios/alkanes-two-part-workshop.scenario.json"
SECRET_PATTERNS = tuple(re.compile(pattern) for pattern in (
    rb"gh[pousr]_[A-Za-z0-9]{30,}", rb"github_pat_[A-Za-z0-9_]{30,}",
    rb"AKIA[A-Z0-9]{16}", rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def safe(root, name):
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and relative.parts and ".." not in relative.parts
            and ".git" not in relative.parts, "Unsafe relative path: " + name)
    path = root / name
    require(path.parent.resolve().is_relative_to(root.resolve()) and not path.is_symlink(),
            "Symlink or escaping path: " + name)
    return path


def atomic_bytes(data, path, replace=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.is_symlink(), "Refusing symlink destination")
    descriptor, temporary = tempfile.mkstemp(prefix=".assembly-", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        require(sha(temporary) == hashlib.sha256(data).hexdigest(), "Temporary bytes differ")
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
            temporary.unlink()
    finally:
        temporary.unlink(missing_ok=True)


def git(root, *arguments):
    return subprocess.check_output(["git", "-C", str(root), *arguments])


def load_state(root):
    return json.loads((root / STATE).read_text())


def source_invariant(root, state):
    require(git(root, "rev-parse", "HEAD").decode().strip() == state["activeHead"], "Source HEAD changed")
    require(git(root, "branch", "--show-current").decode().strip() == state["activeBranch"], "Source branch changed")
    index = Path(os.fsdecode(git(root, "rev-parse", "--git-path", "index")).strip())
    require(sha(index if index.is_absolute() else root / index) == state["indexSHA256"], "Source index changed")
    require(state.get("syncReviewComplete") is True and not state.get("upstreamSyncInProgress"),
            "Final upstream sync/review is not complete")
    require(sha(root / "js/mulermoc-nom-core-54.js") == state["core54SHA256"], "Reviewed core54 differs")
    require(sha(root / "js/mulermoc-nom-core-52.js") ==
            (state.get("core52SHA256") or state.get("coreSHA256")), "Baseline core52 differs")
    require(bool(state.get("sourceRuntimeHashes")), "Missing reviewed runtime hash map")
    for name, digest in state["sourceRuntimeHashes"].items():
        require(sha(safe(root, name)) == digest, "Reviewed runtime differs: " + name)


def clone_path(root, state):
    clone = Path(state["publicClone"])
    require(clone.is_absolute() and clone.is_dir() and not clone.is_symlink(), "Missing disposable public clone")
    clone = clone.resolve()
    require(clone.is_relative_to(Path(state["job"]).resolve()) and not clone.is_relative_to(root),
            "Public clone must be inside dedicated job and outside source")
    git_dir = Path(os.fsdecode(git(clone, "rev-parse", "--absolute-git-dir")).strip()).resolve()
    require(git_dir.is_relative_to(clone) and (clone / ".git").is_dir()
            and not (clone / ".git").is_symlink(), "Public clone must own its disposable Git metadata")
    require(git(clone, "rev-parse", "--show-toplevel").decode().strip() == str(clone), "Clone is not repository root")
    require(git(clone, "rev-parse", "HEAD").decode().strip() == state["previousPublic"], "Public clone base changed")
    require(git(clone, "branch", "--show-current").decode().strip() == state["publicBranch"], "Public branch differs")
    return clone


def protected(name):
    return name.startswith("react-preview/") or bool(re.search(r"(?:-|_)52\.", name))


def publishable(name):
    """Allow new runtime/deliverables and dated historical evidence, no live internals."""
    if name.startswith(EVIDENCE + "/") or any(part in (".git", ".codex", "node_modules", "__pycache__")
                                             for part in PurePosixPath(name).parts):
        return False
    if name.endswith("/.DS_Store") or protected(name):
        return False
    if name in {"README.md", "docs/YANNIS-CONTRIBUTIONS.md", "docs/CHANGELOG.md", "docs/STAGE2-AUTHORING-54.md", *HTML_ENTRIES, PILOT, COMPACT, "spt/init-54.spt"}:
        return True
    if name.startswith("games/") or name.startswith(REPORT + "/"):
        return True
    if name.startswith("js/chemistry-engines/"):
        return bool(re.fullmatch(r"js/chemistry-engines/[0-9a-f]{64}\.js", name))
    if name.startswith("js/"):
        return bool(re.fullmatch(r"js/[^/]*(?:-54|_54)\.js", name)) or name in {
            "js/namelecule-game-repair.js", "js/namelecule-quiz-checkpoints.js",
            "js/namelecule-chemistry-client.js", "js/namelecule-chemistry-worker.js",
            "js/namelecule-repair-generator.js", "js/namelecule-generated-repair-checkpoint.js"}
    if name.startswith("css/"):
        return bool(re.fullmatch(r"css/[^/]*-54\.css", name)) or name in {
            "css/namelecule-games.css", "css/namelecule-quiz-checkpoints.css", "css/namelecule-repair-round.css"}
    if name.startswith("docs/checks/"):
        return bool(re.search(r"2026110[345](?:/|\.|-)", name))
    return bool(re.fullmatch(r"docs/[^/]*2026110[345]\.md", name))


def curated_paths(root, seed):
    names = set(seed)
    for directory in ("js", "css", "games", "docs", "scenarios", "spt"):
        for path in (root / directory).rglob("*"):
            if path.is_file() and publishable(path.relative_to(root).as_posix()):
                names.add(path.relative_to(root).as_posix())
    names.update({"README.md", *HTML_ENTRIES, PILOT, COMPACT})
    names = sorted(name for name in names if publishable(name))
    for name in names:
        require(safe(root, name).is_file(), "Curated source file missing: " + name)
    required = {REPORT + "/" + name for name in REPORT_FILES}
    require(required <= set(names), "Current five professor report files are incomplete")
    require(not any(protected(name) for name in names), "Protected React/52 update attempted")
    return names


def scan(root, names):
    findings = []
    for name in names:
        data = safe(root, name).read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            findings.append(name)
    require(not findings, "Recognizable secret patterns found; paths only: " + json.dumps(findings))


def base_hashes(clone, revision):
    entries = []
    for row in git(clone, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if row:
            metadata, name = row.split(b"\t", 1)
            mode, kind, object_id = metadata.split()
            require(kind == b"blob" and mode in (b"100644", b"100755"), "Unsupported public tree entry")
            entries.append((os.fsdecode(name), object_id))
    hashes = {}
    process = subprocess.Popen(["git", "-C", str(clone), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for name, object_id in entries:
            process.stdin.write(object_id + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            require(len(header) == 3 and header[1] == b"blob", "Invalid public blob")
            remaining = int(header[2])
            digest = hashlib.sha256()
            while remaining:
                chunk = process.stdout.read(min(remaining, 1024 * 1024))
                require(bool(chunk), "Truncated public blob")
                digest.update(chunk)
                remaining -= len(chunk)
            require(process.stdout.read(1) == b"\n", "Invalid public blob terminator")
            hashes[name] = digest.hexdigest()
        process.stdin.close()
        require(process.wait() == 0, "Public blob inspection failed")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()
    return hashes


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"src", "href", "poster"} and value:
                self.urls.append(value)


def resolve_reference(owner, value):
    value = html.unescape(value.strip())
    if not value or value.startswith("#"):
        return None
    if value.startswith(PUBLIC_PREFIX):
        value = "/" + value[len(PUBLIC_PREFIX):]
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    path = urllib.parse.unquote(parsed.path)
    if not path:
        path = owner
    elif path.startswith("/"):
        path = path.lstrip("/")
    else:
        path = posixpath.join(posixpath.dirname(owner), path)
    path = posixpath.normpath(path)
    require(path != ".." and not path.startswith("../"), "Dependency escapes public tree: " + owner)
    if parsed.path.endswith("/"):
        path = posixpath.join(path, "index.html")
    return path


def molecule_keys(text):
    # The current library registers 136 initial entries and five later esters.
    initial = text.split("\n};", 1)[0]
    names = set(re.findall(r"^  ([A-Za-z0-9_]+):\s*\{", initial, re.MULTILINE))
    names.update(re.findall(r'''nameExamples\[['"]([A-Za-z0-9_]+)['"]\]\s*=\s*\{''', text))
    return sorted(names)


def dependency_inventory(root, available):
    dependencies = {}
    external = set()

    def add(owner, value):
        target = resolve_reference(owner, value)
        if target is None:
            if value and not value.startswith("#"):
                external.add(value)
            return
        require(target in available, "Missing local dependency: " + owner + " -> " + target)
        dependencies.setdefault(target, set()).add(owner)
        for scenario in urllib.parse.parse_qs(urllib.parse.urlsplit(html.unescape(value)).query).get("scenario", []):
            add(target, scenario)

    for name in HTML_ENTRIES:
        parser = References()
        parser.feed(safe(root, name).read_text())
        for value in parser.urls:
            add(name, value)
    for name in available:
        if name.startswith("css/") and publishable(name):
            for value in re.findall(r"url\(\s*['\"]?([^'\")]+)", safe(root, name).read_text()):
                add(name, value)
    add("mulermoc-nom-54.html", "js/vendor/jsmol/namelecule-20261031-r1/JSmol.min.js")
    add("mulermoc-nom-54.html", "spt/init-54.spt")
    add("games/name-repair.html", "./data/name-repair-alkanes.json")
    game = json.loads((root / "games/data/name-repair-alkanes.json").read_text())
    for group in game["sets"]:
        require(len(group["rounds"]) == 3, "Each alkane set must retain three questions")
        for question in group["rounds"]:
            add("games/name-repair.html", question["asset"])
    require(len(game["sets"]) == 2, "Expected two alkane sets")
    theory = References()
    theory.feed((root / "design/theory-library.html").read_text())
    lessons = set()
    for value in theory.urls:
        for scenario in urllib.parse.parse_qs(urllib.parse.urlsplit(value).query).get("scenario", []):
            target = resolve_reference("mulermoc-nom-54.html", scenario)
            require(target in available, "Active theory scenario missing")
            lessons.add(target)
    require(len(lessons) == 14 and PILOT not in lessons, "Expected 14 active lessons plus separate pilot")
    require(sum(len(json.loads(safe(root, name).read_text())["steps"]) for name in lessons) == 328,
            "Active theory step count differs")
    add("mulermoc-nom-54.html", PILOT)
    add("mulermoc-nom-54.html", COMPACT)
    for runtime in ["js/namelecule-chemistry-client.js", "js/namelecule-chemistry-worker.js", "js/namelecule-repair-generator.js", "js/namelecule-generated-repair-checkpoint.js", "games/data/alkane-structures.json", "js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js"]:
        add("mulermoc-nom-54.html", runtime)
    molecules = molecule_keys((root / "js/jsme-nick-nomeclature-moc2-data_54.js").read_text())
    require(len(molecules) == 141, "Expected 141 library molecule keys")
    for molecule in molecules:
        add("mulermoc-nom-54.html", "mols/nomeclature-moc2/" + molecule + "_3D.sdf")
    def scenario_references(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "asset" and isinstance(item, str):
                    add("games/name-repair.html", item)
                if key in {"selectedMol", "moleculeId"} and item:
                    require(item in molecules, "Scenario references unknown molecule: " + str(item))
                scenario_references(item)
        elif isinstance(value, list):
            for item in value:
                scenario_references(item)
    for name in sorted(lessons | {PILOT}):
        scenario_references(json.loads(safe(root, name).read_text()))
    return {name: sorted(owners) for name, owners in sorted(dependencies.items())}, sorted(external)


def freeze(root):
    state = load_state(root)
    source_invariant(root, state)
    clone = clone_path(root, state)
    require(not git(clone, "status", "--porcelain", "-z"), "Public clone must be clean before freeze")
    seed = json.loads((root / EVIDENCE / "assembly-plan.json").read_text())
    require(seed["base"] == state["previousPublic"], "Seed public base differs")
    preservation = json.loads((root / EVIDENCE / "public-preservation.json").read_text())
    require(preservation["publicBase"] == state["previousPublic"], "Preservation base differs")
    baseline = base_hashes(clone, state["previousPublic"])
    require(all(sha(safe(clone, name)) == digest for name, digest in baseline.items()),
            "Public clone working bytes differ from original Git blobs")
    react = {name: digest for name, digest in baseline.items() if name.startswith("react-preview/")}
    require(len(react) == 39 and react == preservation["preservedReact"], "39-path public React baseline differs")
    require(baseline["js/mulermoc-nom-core-52.js"] == preservation["core52SHA256"]
            and baseline["mulermoc-nom-52.html"] == preservation["main52SHA256"], "Public v52 baseline differs")
    paths = curated_paths(root, seed["paths"])
    scan(root, paths)
    files = {name: sha(safe(root, name)) for name in paths}
    available = dict(baseline, **files)
    dependencies, external = dependency_inventory(root, available)
    for name in dependencies:
        if name not in files and not protected(name) and safe(root, name).is_file():
            require(sha(root / name) == baseline[name], "Inherited active dependency differs locally: " + name)
    require(all(sha(root / name) == digest for name, digest in files.items()), "Source changed during freeze")
    source_invariant(root, state)
    manifest = {"schemaVersion": 1, "publicBase": state["previousPublic"],
                "sourceCutoffUTC": datetime.now(timezone.utc).isoformat(), "sourceHead": state["activeHead"],
                "sourceIndexSHA256": state["indexSHA256"], "core54SHA256": state["core54SHA256"],
                "files": files, "baseFiles": baseline,
                "protectedFiles": {name: digest for name, digest in baseline.items() if protected(name)},
                "dependencyHashes": {name: available[name] for name in dependencies},
                "dependencyOwners": dependencies, "externalReferences": external,
                "exclusions": "Publication folder, live internal source instructions/plans/session/state, communication and React/52 updates. Dated historical evidence remains eligible.",
                "cutoff": "These exact source bytes; manifest and publication bookkeeping are excluded, avoiding self-hash recursion.",
                "secretScanFindings": [], "reactPreservedPaths": len(react), "activeTheoryLessons": 14,
                "activeTheorySteps": 328, "separatePilot": PILOT, "compactLesson": COMPACT, "molecules": 141}
    path = root / EVIDENCE / MANIFEST
    data = canonical(manifest)
    atomic_bytes(data, path)
    atomic_bytes((hashlib.sha256(data).hexdigest() + "  " + MANIFEST + "\n").encode(), path.with_suffix(".json.sha256"))
    atomic_bytes(b"\0".join(os.fsencode(name) for name in paths) + b"\0", root / EVIDENCE / "curated-stage-paths.nul")
    print(json.dumps({"manifest": str(path), "SHA256": hashlib.sha256(data).hexdigest(),
                      "files": len(files), "baseFilesRetained": len(baseline),
                      "localDependencies": len(dependencies), "ReactPreserved": len(react)}))
    return manifest


def frozen_manifest(root, state):
    path = root / EVIDENCE / MANIFEST
    data = path.read_bytes()
    manifest = json.loads(data)
    require(data == canonical(manifest), "Manifest bytes are not canonical")
    detached = path.with_suffix(".json.sha256")
    require(detached.is_file() and detached.read_text().split()[0] == sha(path),
            "Frozen manifest differs from detached SHA256")
    require(manifest["publicBase"] == state["previousPublic"], "Frozen public base differs")
    require(manifest["sourceHead"] == state["activeHead"] and
            manifest["sourceIndexSHA256"] == state["indexSHA256"] and
            manifest["core54SHA256"] == state["core54SHA256"], "Frozen source baseline differs")
    require(all(publishable(name) for name in manifest["files"]), "Manifest contains excluded source updates")
    require(all(sha(safe(root, name)) == digest for name, digest in manifest["files"].items()),
            "Source no longer matches frozen cutoff; regenerate frozen manifest")
    return manifest


def verify_tree(root, clone, manifest):
    expected = dict(manifest["baseFiles"], **manifest["files"])
    for name, digest in expected.items():
        require(safe(clone, name).is_file() and sha(clone / name) == digest,
                "Assembled public bytes differ or file deleted: " + name)
    for name, digest in manifest["protectedFiles"].items():
        require(sha(clone / name) == digest, "Protected React/52 bytes changed: " + name)
    actual = {path.relative_to(clone).as_posix() for path in clone.rglob("*")
              if ".git" not in path.relative_to(clone).parts and path.is_file()}
    require(actual == set(expected), "Unexpected files exist in assembled clone")
    for name, digest in manifest["dependencyHashes"].items():
        require(sha(clone / name) == digest, "Assembled local dependency differs: " + name)
    scan(clone, manifest["files"])
    return {"allPublicFiles": len(expected), "curatedSourceFiles": len(manifest["files"]),
            "preservedReactPaths": manifest["reactPreservedPaths"], "protectedPaths": len(manifest["protectedFiles"]),
            "baseFilesDeleted": 0, "allHashesVerified": True, "localDependencyHashesVerified": True,
            "secretPatternFindings": [], "sourceCutoffUTC": manifest["sourceCutoffUTC"],
            "manifestSHA256": hashlib.sha256(canonical(manifest)).hexdigest()}


def assemble(root, verify_only=False):
    state = load_state(root)
    source_invariant(root, state)
    clone = clone_path(root, state)
    manifest = frozen_manifest(root, state)
    if not verify_only:
        require(not git(clone, "status", "--porcelain", "-z"), "Public clone must be clean before assembly")
        scan(root, manifest["files"])
        for name, digest in manifest["files"].items():
            target = safe(clone, name)
            atomic_bytes(safe(root, name).read_bytes(), target, replace=True)
            shutil.copymode(root / name, target)
            require(sha(target) == digest, "Copied public bytes differ: " + name)
    result = verify_tree(root, clone, manifest)
    source_invariant(root, state)
    require(all(sha(root / name) == digest for name, digest in manifest["files"].items()),
            "Source changed during assembly/verification")
    atomic_bytes(canonical(result), root / EVIDENCE / "curated-assembly-verified.json", replace=True)
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "assemble", "verify"))
    arguments = parser.parse_args()
    if arguments.action == "freeze":
        freeze(ROOT)
    else:
        assemble(ROOT, verify_only=arguments.action == "verify")
