"""Isolated helper tests. Never call save/create_zip/create_bundle or real Git."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location(
    "save_helper_20261105", REPO / "communication/checkpoints/save-helper-20261105.py")
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="namelecule-save-helper-test-")
        self.root = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def file(self, name, data=b"fixture"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_atomic_new_file_refuses_overwrite(self):
        target = self.root / "new.txt"
        digest = HELPER.atomic_bytes(b"original", target)
        self.assertEqual(digest, HELPER.sha(target))
        with self.assertRaises(FileExistsError):
            HELPER.atomic_bytes(b"replacement", target)
        self.assertEqual(target.read_bytes(), b"original")
        self.assertEqual(list(self.root.glob(".namelecule-*")), [])

    def test_atomic_replace_and_verified_copy(self):
        source = self.file("source.txt", b"first")
        target = self.root / "nested/target.txt"
        HELPER.verified_copy(source, target)
        source.write_bytes(b"second")
        HELPER.verified_copy(source, target, replace=True)
        self.assertEqual(target.read_bytes(), b"second")
        with self.assertRaises(RuntimeError):
            HELPER.verified_copy(source, target, replace=True, expected="0" * 64)
        self.assertEqual(target.read_bytes(), b"second")

    def test_relative_paths_reject_escapes_git_and_symlinks(self):
        for name in ("../bad", "/tmp/absolute", ".git/index"):
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                HELPER.relative_path(self.root, name)
        target = self.file("real.txt")
        (self.root / "alias").symlink_to(target)
        with self.assertRaises(RuntimeError):
            HELPER.relative_path(self.root, "alias")
        outside = self.root.parent
        (self.root / "escape").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            HELPER.relative_path(self.root, "escape/file")

    def test_secret_scan_covers_large_binary_files_and_returns_only_paths(self):
        token = b"gh" + b"p_" + b"X" * 34
        self.file("clean.txt", b"clean")
        self.file("large.bin", b"\x00" * 2_100_000 + token + b"\x00")
        findings = HELPER.secret_findings(self.root, ["clean.txt", "large.bin"])
        self.assertEqual(findings, ["large.bin"])
        self.assertNotIn(token.decode(), json.dumps(findings))

    def test_source_inventory_adds_dist_public_and_keeps_untracked_deliverables(self):
        for name in ("tracked.txt", "docs/new-report.md", "react-preview/dist/index.html",
                     "react-preview/public/viewer.js", "react-preview/dist/.DS_Store",
                     "react-preview/dist/debug.log"):
            self.file(name)
        with patch.object(HELPER, "git", return_value=b"tracked.txt\0docs/new-report.md\0deleted.txt\0"):
            paths = HELPER.source_paths(self.root)
        self.assertEqual(paths, ["docs/new-report.md", "react-preview/dist/index.html",
                                 "react-preview/public/viewer.js", "tracked.txt"])

    def test_source_inventory_requires_both_react_directories(self):
        with patch.object(HELPER, "git", return_value=b""), self.assertRaises(RuntimeError):
            HELPER.source_paths(self.root)

    def test_recovery_inventory_excludes_old_archives_logs_and_hashes(self):
        for name in ("letter.txt", "state.json", "old.zip", "old.bundle", "old.log", "old.sha256", ".DS_Store"):
            self.file("communication/" + name)
        self.assertEqual(HELPER.recovery_paths(self.root),
                         ["communication/letter.txt", "communication/state.json"])

    def prepare_lessons(self, steps=328):
        names = ["scenarios/theory-" + str(index) + ".json" for index in range(14)]
        for index, name in enumerate(names):
            count = steps - 13 if index == 0 else 1
            self.file(name, json.dumps({"steps": [None] * count}).encode())
        self.file("design/theory-library.html", "\n".join(
            '<a href="app.html?scenario=' + name + '&amp;present=1">lesson</a>'
            for name in names).encode())
        self.file(HELPER.PILOT_REL, b'{"steps":[{}]}')
        return names

    def test_exact_active_lesson_counts_and_separate_pilot(self):
        names = self.prepare_lessons()
        lessons, counts = HELPER.lesson_inventory(self.root)
        self.assertEqual(set(lessons), set(names))
        self.assertEqual(sum(counts.values()), 328)
        self.assertNotIn(HELPER.PILOT_REL, lessons)

    def test_wrong_step_count_or_active_pilot_blocks_save(self):
        self.prepare_lessons(336)
        with self.assertRaises(RuntimeError):
            HELPER.lesson_inventory(self.root)
        self.prepare_lessons()
        path = self.root / "design/theory-library.html"
        path.write_text(path.read_text() + '?scenario=' + HELPER.PILOT_REL + '&amp;present=1')
        with self.assertRaises(RuntimeError):
            HELPER.lesson_inventory(self.root)

    def report_fixture(self):
        base = HELPER.REPORT_REL + "/"
        self.file(base + "update.html", b'<a href="../../design/welcome.html?a=1&amp;b=2">link</a>'
                  b'<img src="../../fixture-image.svg">')
        for name in ("links.json", "links.txt", "message-to-professor.txt"):
            self.file(base + name, b"{}")
        self.file("fixture-image.svg", b"<svg></svg>")

    def test_portable_report_expands_links_and_embeds_local_image(self):
        self.report_fixture()
        files = HELPER.portable_report(self.root, "https://example.test/docs/professor-20261105/update.html")
        self.assertIn(b'https://example.test/design/welcome.html?a=1&amp;b=2', files["update.html"])
        images = [name for name in files if name.startswith("assets/")]
        self.assertEqual(len(images), 1)
        self.assertEqual(files[images[0]], b"<svg></svg>")
        self.assertIn(images[0].encode(), files["update.html"])

    def test_portable_report_rejects_missing_image(self):
        self.report_fixture()
        (self.root / "fixture-image.svg").unlink()
        with self.assertRaises(RuntimeError):
            HELPER.portable_report(self.root, "https://example.test/report.html")

    def test_launcher_absent_is_recordable_but_wrong_present_count_fails(self):
        absent = self.root / "absent.app"
        app, files = HELPER.launcher_inventory(self.root, {"launcherPath": str(absent)})
        self.assertEqual((app, files), (absent, []))
        self.file("present.app/Contents/a")
        with self.assertRaises(RuntimeError):
            HELPER.launcher_inventory(self.root, {"launcherPath": str(self.root / "present.app")})
        for index in range(9):
            self.file("present.app/Contents/" + str(index))
        self.assertEqual(len(HELPER.launcher_inventory(
            self.root, {"launcherPath": str(self.root / "present.app")})[1]), 10)

    def state_fixture(self):
        return {"stamp": "20261105-123456", "job": str(self.root / "job"),
                "checkpointClone": str(self.root / "job/checkpoint"), "checkpointBranch": "checkpoint/test",
                "activeHead": "a" * 40, "activeBranch": "test", "indexSHA256": "b" * 64,
                "core54SHA256": "c" * 64, "sourceRuntimeHashes": {"runtime.js": "d" * 64},
                "externalFolders": ["/tmp/external-one", "/tmp/external-two"], "clonesReady": True,
                "syncReviewComplete": True, "publicLiveVerified": True, "publicReleaseCommit": "e" * 40}

    def test_final_gate_blocks_before_git_or_mutations(self):
        for key in ("syncReviewComplete", "publicLiveVerified", "clonesReady"):
            state = self.state_fixture()
            state[key] = False
            with self.subTest(key=key), patch.object(HELPER, "git") as git:
                with self.assertRaises(RuntimeError):
                    HELPER.prerequisites(self.root, state, "final")
                git.assert_not_called()

    def test_initial_requires_explicit_authorization_and_review(self):
        state = self.state_fixture()
        state["publicLiveVerified"] = False
        with patch.object(HELPER, "git") as git, self.assertRaisesRegex(RuntimeError, "explicit"):
            HELPER.prerequisites(self.root, state, "initial")
        git.assert_not_called()

    def test_invalid_generation_cannot_name_output(self):
        with patch.object(HELPER, "git") as git, self.assertRaises(RuntimeError):
            HELPER.prerequisites(self.root, self.state_fixture(), "../../escape")
        git.assert_not_called()

    def test_invariant_checks_core52_final_core54_and_runtime(self):
        self.file(".git/index", b"index")
        core52 = self.file("js/mulermoc-nom-core-52.js", b"core52")
        core54 = self.file("js/mulermoc-nom-core-54.js", b"final-reviewed-core54")
        runtime = self.file("runtime.js", b"runtime")
        state = self.state_fixture()
        state.update(indexSHA256=HELPER.sha(self.root / ".git/index"), core52SHA256=HELPER.sha(core52),
                     core54SHA256=HELPER.sha(core54), sourceRuntimeHashes={"runtime.js": HELPER.sha(runtime)})

        def fake_git(root, *args):
            return {("rev-parse", "HEAD"): (state["activeHead"] + "\n").encode(),
                    ("branch", "--show-current"): b"test\n",
                    ("rev-parse", "--git-path", "index"): b".git/index\n"}[args]

        with patch.object(HELPER, "git", side_effect=fake_git):
            HELPER.invariant(self.root, state)
            core54.write_bytes(b"old-baseline-core54")
            with self.assertRaisesRegex(RuntimeError, "final reviewed"):
                HELPER.invariant(self.root, state)
            core54.write_bytes(b"final-reviewed-core54")
            runtime.write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "Runtime hash"):
                HELPER.invariant(self.root, state)

    def test_staged_blob_verification_rejects_transformation(self):
        class FakeProcess:
            def __init__(self, data):
                self.stdin = io.BytesIO()
                self.stdout = io.BytesIO(b"a blob " + str(len(data)).encode() + b"\n" + data + b"\n")
            def wait(self):
                return 0
            def poll(self):
                return 0

        original = self.file("original.txt", b"original\r\n")
        entry = b"100644 abcdef 0\tfile.txt\0"
        with patch.object(HELPER, "git", return_value=entry):
            with patch.object(HELPER.subprocess, "Popen", return_value=FakeProcess(original.read_bytes())):
                HELPER.verify_staged_bytes(self.root, {"file.txt": HELPER.sha(original)})
            with patch.object(HELPER.subprocess, "Popen", return_value=FakeProcess(b"original\n")):
                with self.assertRaisesRegex(RuntimeError, "Staged bytes changed"):
                    HELPER.verify_staged_bytes(self.root, {"file.txt": HELPER.sha(original)})

    def test_receipt_refresh_preserves_snapshot_and_records_updated_notes(self):
        for name in ("SESSION-NOTES.md", "YANNIS-CONTRIBUTIONS.md"):
            self.file("docs/" + name, ("new " + name).encode())
        external = self.root / "fictional-external"
        external.mkdir()
        state = {"stamp": "20261105-123456", "saveComplete": True,
                 "checkpointSnapshotCommit": "a" * 40, "finalBookkeepingCommit": "b" * 40,
                 "externalCopies": [{"directory": str(external), "files": {}}]}
        with patch.object(HELPER, "invariant"), patch.object(HELPER, "git") as git:
            updated = HELPER.refresh_receipts(self.root, state)
        git.assert_not_called()
        self.assertEqual(updated["checkpointSnapshotCommit"], "a" * 40)
        self.assertEqual(updated["finalBookkeepingCommit"], "b" * 40)
        recorded = json.loads((external / "final-save-state.json").read_text())
        self.assertEqual(recorded, json.loads((self.root / HELPER.STATE_REL).read_text()))
        self.assertEqual(recorded["externalCopies"][0]["files"]["SESSION-NOTES.md"],
                         HELPER.sha(self.root / "docs/SESSION-NOTES.md"))

    def test_receipt_refresh_refuses_incomplete_save_before_writes(self):
        with patch.object(HELPER, "invariant"), self.assertRaisesRegex(RuntimeError, "incomplete"):
            HELPER.refresh_receipts(self.root, {"saveComplete": False})
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
