"""Explicit Nov12 delivery commands; import performs no save or network action.

Only owned job clones are staged/committed/pushed. Report status and later
metadata are managed separately; Actions success does not establish HTTP bytes.
"""
from pathlib import Path
import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("nov12_release_ops", HERE / "release-ops.py")
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)
h = ops.h
ROOT = ops.R
REPO = "yanisken9/organic-nomenclature-3"
REMOTE = "https://github.com/" + REPO + ".git"
API = "https://api.github.com/repos/" + REPO
PUBLIC = "https://yanisken9.github.io/organic-nomenclature-3/"
require = h.require


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def git(clone, *args, input=None, timeout=180):
    # Never stream credential-helper, Git trace or remote error output.
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_TRACE") and k != "GIT_CURL_VERBOSE"}
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(["git", "-C", str(clone), *args], input=input,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env, timeout=timeout)
    require(result.returncode == 0, "Git operation failed: " + args[0])
    return result.stdout


def clone(s, key, branch):
    c = ops.ownclone(s, key)
    require(git(c, "branch", "--show-current").decode().strip() == branch,
            "Unexpected owned clone branch")
    require(git(c, "remote", "get-url", "origin").decode().strip() == REMOTE
            and s["publicRemote"] == REMOTE, "Unexpected publication remote")
    return c


def target(s):
    t = json.loads(ops.exact(HERE / "runtime-target.json"))
    require(t["releaseFiles"] == s["releaseFiles"] and len(t["releaseFiles"]) == s["releaseFileCount"],
            "Frozen release target changed")
    require(t["files"] == s["runtimeFiles"] and len(t["files"]) == s["runtimeFileCount"],
            "Frozen runtime target changed")
    require(t["sourceHEAD"] == s["activeHead"] and t["publicPrevious"] == s["previousPublic"],
            "Release baseline changed")
    expected = json.loads(ops.exact(HERE / "public-baseline-hashes.json"))
    expected.update(t["releaseFiles"])
    return t, expected


def worktree(c, expected):
    paths = set()
    for directory, dirs, files in os.walk(c, followlinks=False):
        if Path(directory) == c:
            dirs.remove(".git")
        for name in dirs + files:
            require(not (Path(directory) / name).is_symlink(), "Symlink in public tree")
        paths.update((Path(directory) / name).relative_to(c).as_posix() for name in files)
    require(paths == set(expected), "Public worktree path set differs from baseline plus overlay")
    for p, digest in expected.items():
        require(ops.sha(h.relative_path(c, p)) == digest, "Public worktree bytes changed: " + p)


def save_guard(s):
    ops.invariant(s)
    require(s.get("saveComplete") is True and s.get("candidateBrowserPassed") is True,
            "Verified full save and candidate browser checks are required")
    frozen = Path(s["frozenSource"])
    require(frozen.resolve().is_relative_to(Path(s["job"]).resolve())
            and not frozen.is_symlink(), "Unexpected frozen source location")
    t, expected = target(s)
    saved = {**s["sourceHashes"], **s["recoveryHashes"]}
    for p, digest in t["releaseFiles"].items():
        require(saved.get(p) == digest and ops.sha(frozen / p) == digest,
                "Release differs from saved frozen source: " + p)
    return t, expected


def receipt(name, data):
    ops.write(HERE / name, data)
    print(json.dumps(data, ensure_ascii=False), flush=True)


def prepare(_args):
    s = ops.load()
    t, expected = save_guard(s)
    c = clone(s, "publicClone", s["publicBranch"])
    worktree(c, expected)
    head = git(c, "rev-parse", "HEAD").decode().strip()
    if s.get("publicPrepared"):
        require(head == s["publicRuntimeCommit"] and not git(c, "status", "--porcelain", "-z"),
                "Prepared public clone changed")
        h.verify_staged_bytes(c, expected)
        print("Public candidate already prepared: " + head, flush=True)
        return
    require(head == s["previousPublic"], "Public baseline HEAD changed")
    git(c, "add", "-A")
    git(c, "--literal-pathspecs", "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul",
        input=("\0".join(sorted(expected)) + "\0").encode())
    h.verify_staged_bytes(c, expected)
    git(c, "commit", "--quiet", "-m", "Publish Namelecule lesson game choices and professor report — 12 November 2026")
    commit = git(c, "rev-parse", "HEAD").decode().strip()
    require(git(c, "rev-parse", "HEAD^").decode().strip() == s["previousPublic"],
            "Unexpected public commit parent")
    require(not git(c, "status", "--porcelain", "-z"), "Public clone is not clean")
    h.verify_staged_bytes(c, expected)
    ops.invariant(s)
    proof = {"preparedUTC": now(), "publicCommit": commit, "parent": s["previousPublic"],
             "releaseFiles": len(t["releaseFiles"]), "fullTreeFiles": len(expected),
             "stagedEveryBlobSHA256Verified": True, "sourceGitUntouched": True}
    s.update(publicPrepared=True, publicRuntimeCommit=commit, publicReleaseCommit=commit,
             publicPreparedUTC=proof["preparedUTC"], publicTreeFiles=len(expected))
    ops.write(ops.STATE, s)
    receipt("public-prepare.json", proof)


def refs(c, s):
    names = ["refs/heads/" + s["publicBranch"], "refs/heads/" + s["checkpointBranch"]]
    data = git(c, "ls-remote", "--heads", REMOTE, *names, timeout=60)
    result = {}
    for line in data.decode().splitlines():
        digest, name = line.split("\t")
        require(name in names and name not in result, "Unexpected remote ref response")
        result[name] = digest
    return result


def push(_args):
    s = ops.load()
    _, expected = save_guard(s)
    require(s.get("independentReviewComplete") is True and s.get("publicPrepared") is True,
            "Independent review and prepared public commit are required before push")
    c = clone(s, "publicClone", s["publicBranch"])
    cp = clone(s, "checkpointClone", s["checkpointBranch"])
    public = s["publicRuntimeCommit"]
    checkpoint = s["latestLocalCheckpointCommit"]
    require(checkpoint == s["checkpointSnapshotCommit"], "Unexpected checkpoint metadata scope")
    for path, commit in ((c, public), (cp, checkpoint)):
        require(git(path, "rev-parse", "HEAD").decode().strip() == commit
                and not git(path, "status", "--porcelain", "-z"), "Delivery clone changed")
    worktree(c, expected)
    h.verify_staged_bytes(c, expected)
    h.verify_staged_bytes(cp, s["sourceHashes"])
    git(c, "merge-base", "--is-ancestor", s["previousPublic"], public)
    git(cp, "merge-base", "--is-ancestor", s["previousCheckpoint"], checkpoint)
    publicref = "refs/heads/" + s["publicBranch"]
    cpref = "refs/heads/" + s["checkpointBranch"]
    before = refs(c, s)
    require(before.get(publicref) in (s["previousPublic"], public), "Remote public branch advanced")
    require(before.get(cpref) in (None, checkpoint), "Dated remote checkpoint already differs")
    if before.get(cpref) is None:
        git(cp, "push", "--porcelain", "origin", checkpoint + ":" + cpref)
    aftercp = refs(c, s)
    require(aftercp.get(cpref) == checkpoint and aftercp.get(publicref) == before.get(publicref),
            "Remote refs changed during checkpoint upload")
    s.update(fullCheckpointRemoteUploaded=True, latestRemoteCheckpointCommit=checkpoint)
    ops.write(ops.STATE, s)
    # Recheck immediately before the second normal, non-force update.
    require(refs(c, s) == aftercp, "Remote refs changed before public upload")
    ops.invariant(s)
    if aftercp.get(publicref) != public:
        git(c, "push", "--porcelain", "origin", public + ":" + publicref)
    final = refs(c, s)
    require(final.get(cpref) == checkpoint and final.get(publicref) == public,
            "Remote refs do not match the reviewed delivery")
    ops.invariant(s)
    proof = {"pushedUTC": now(), "refsBefore": before, "refsAfter": final,
             "runtimeCommit": public, "checkpointSnapshot": checkpoint,
             "nonForcePush": True, "sourceGitUntouched": True}
    s.update(publicRuntimeRemoteUploaded=True, latestUploadedPublicCommit=public,
             runtimePushedUTC=proof["pushedUTC"], remoteRefsAfterRuntimePush=final)
    ops.write(ops.STATE, s)
    receipt("runtime-push.json", proof)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise RuntimeError("Unexpected HTTP redirect")


def api(path, *, token=None, post=False):
    headers = {"User-Agent": "Namelecule-Nov12-delivery", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if post:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(API + path, headers=headers,
                                     data=b"{}" if post else None, method="POST" if post else "GET")
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=25) as response:
            return response.status, json.loads(response.read(2 * 1024 * 1024))
    except urllib.error.HTTPError as error:
        # Do not log API bodies, request headers or credential-helper output.
        raise RuntimeError("GitHub API HTTP " + str(error.code)) from None
    except urllib.error.URLError:
        raise RuntimeError("GitHub API network request failed") from None


def build_request(s, c):
    commit = s.get("publicReleaseCommit", s["publicRuntimeCommit"])
    prior = s.get("pagesBuildRequest", {})
    require(prior.get("commit") != commit, "A build request was already attempted for this commit")
    # Record the attempt before POST so retries cannot silently duplicate it.
    request = {"commit": commit, "attemptedUTC": now(), "accepted": False}
    s["pagesBuildRequest"] = request
    ops.write(ops.STATE, s)
    try:
        credentials = git(c, "credential", "fill", input=("protocol=https\nhost=github.com\npath=" + REPO + ".git\n\n").encode(), timeout=30)
        fields = dict(line.split("=", 1) for line in credentials.decode().splitlines() if "=" in line)
        token = fields.get("password")
        require(bool(token), "No private GitHub credential is available")
        status, value = api("/pages/builds", token=token, post=True)
        require(status == 201, "GitHub did not confirm the Pages build request")
        request.update(accepted=True, httpStatus=status, status=value.get("status"))
    except Exception as error:
        request["failure"] = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        ops.write(ops.STATE, s)
        ops.write(HERE / "pages-build-request.json", request)
        raise
    finally:
        # No credential is printed, placed in argv, or persisted in an artifact.
        credentials = fields = token = None
    ops.write(ops.STATE, s)
    ops.write(HERE / "pages-build-request.json", request)


def delivery_guard(s):
    ops.invariant(s)
    require(s.get("publicRuntimeRemoteUploaded") is True, "Upload must be verified first")
    c = clone(s, "publicClone", s["publicBranch"])
    require(refs(c, s).get("refs/heads/" + s["publicBranch"]) == s.get("publicReleaseCommit", s["publicRuntimeCommit"]),
            "Remote public commit changed")
    return c


def pages(args):
    s = ops.load()
    c = delivery_guard(s)
    commit = s.get("publicReleaseCommit", s["publicRuntimeCommit"])
    attempted = False
    for attempt in range(args.attempts):
        _, result = api("/actions/runs?head_sha=" + commit + "&per_page=30")
        runs = [r for r in result["workflow_runs"] if r.get("head_sha") == commit
                and r.get("name", "").lower() == "pages build and deployment"]
        runs.sort(key=lambda r: (r.get("created_at", ""), r["id"]), reverse=True)
        safe = [{k: r.get(k) for k in ("id", "name", "head_sha", "status", "conclusion", "created_at", "html_url")} for r in runs]
        latest = safe[0] if safe else None
        success = bool(latest and latest["status"] == "completed" and latest["conclusion"] == "success")
        proof = {"checkedUTC": now(), "commit": commit, "runs": safe,
                 "currentCommitWorkflowSucceeded": success, "httpBytesVerifiedBySeparateCommand": False}
        ops.write(HERE / "pages-status.json", proof)
        s.update(pagesWorkflowSucceeded=success, pagesWorkflowEvidence=str((HERE / "pages-status.json").relative_to(ROOT)))
        ops.write(ops.STATE, s)
        print(json.dumps({"pagesAttempt": attempt + 1, "commit": commit,
                          "latest": latest, "workflowSucceeded": success}), flush=True)
        if success:
            ops.invariant(s)
            return
        # An active run remains an external pending condition; do not submit a competing build.
        if args.request_build and not attempted and (not latest or latest["status"] == "completed"):
            build_request(s, c)
            attempted = True
        if attempt + 1 < args.attempts:
            time.sleep(args.interval)
    raise RuntimeError("Pages workflow is pending or unsuccessful; HTTP delivery remains unproven")


def verify(args):
    s = ops.load()
    require(s.get("publicReleaseCommit", s["publicRuntimeCommit"]) == s["publicRuntimeCommit"],
            "Frozen initial-release HTTP verification must precede later report publication")
    c = delivery_guard(s)
    t, expected = target(s)
    old = json.loads(ops.exact(ROOT / "communication/checkpoints/save-publish-20261110-state.json"))
    protected = old["publicProtected"]
    require(len(protected) == 49 ,
            "Protected-public verification target changed")
    hashes = {**t["releaseFiles"], **protected}
    require(all(expected.get(p) == digest for p, digest in hashes.items()), "Protected bytes differ from public baseline")
    results = {}

    def item(p):
        url = PUBLIC + urllib.parse.quote(p, safe="/") + "?verify=" + s["stamp"] + "-" + str(time.time_ns())
        request = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "Accept-Encoding": "identity",
                                                       "User-Agent": "Namelecule-Nov12-byte-verification"})
        result = {"path": p, "expectedSHA256": hashes[p], "ok": False}
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
                limit = (c / p).stat().st_size
                data = response.read(limit + 1)
                result.update(status=response.status, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
                result["ok"] = response.status == 200 and len(data) == limit and result["sha256"] == hashes[p]
        except urllib.error.HTTPError as error:
            result["status"] = error.code
        except Exception as error:
            result["error"] = type(error).__name__
        return p, result

    for attempt in range(args.attempts):
        pending = sorted(p for p in hashes if not results.get(p, {}).get("ok"))
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for p, result in pool.map(item, pending):
                results[p] = result
        passed = all(results[p]["ok"] for p in hashes)
        proof = {"checkedUTC": now(), "commit": s["publicRuntimeCommit"], "attempts": attempt + 1,
                 "releaseFiles": len(t["releaseFiles"]), "protectedFiles": 49, "allSHA256Verified": passed,
                 "files": {p: results[p] for p in sorted(results)},
                 "limits": "Exact HTTP bytes only; browser replay and final report status are separate."}
        ops.write(HERE / "public-runtime-http.json", proof)
        s.update(publicRuntimeLiveVerified=passed, publicReleaseHTTPVerified=passed,
                 publicRuntimeHTTPCount=sum(r["ok"] for r in results.values()),
                 publicHTTPProof=str((HERE / "public-runtime-http.json").relative_to(ROOT)))
        if passed:
            delivery_guard(s)
            s["publicRuntimeVerifiedUTC"] = proof["checkedUTC"]
        ops.write(ops.STATE, s)
        print(json.dumps({"httpAttempt": attempt + 1, "exactFiles": s["publicRuntimeHTTPCount"],
                          "expectedFiles": len(hashes), "allSHA256Verified": passed}), flush=True)
        if passed:
            return
        if attempt + 1 < args.attempts:
            time.sleep(args.interval)
    raise RuntimeError("Public HTTP bytes remain missing or different; inspect public-runtime-http.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "push", "pages", "verify"))
    parser.add_argument("--attempts", type=int, default=3, help="Bounded polls/check rounds, 1–20")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between rounds, 0–30")
    parser.add_argument("--request-build", action="store_true", help="Attempt one official Pages build if no active current run")
    args = parser.parse_args()
    require(__debug__, "Run without Python -O; imported invariant checks use assertions")
    require(1 <= args.attempts <= 20 and 0 <= args.interval <= 30, "Polling bounds exceeded")
    require(not args.request_build or args.command == "pages", "--request-build is only valid for pages")
    globals()[args.command](args)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Delivery stopped: " + (str(error) if isinstance(error, RuntimeError) else type(error).__name__), file=sys.stderr)
        sys.exit(2)
