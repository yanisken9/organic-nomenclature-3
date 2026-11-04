"""Fictional temporary-file tests; no real Git, clone, network or assembly."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("prepare_assembly", Path(__file__).with_name("prepare-assembly.py"))
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="namelecule-assembly-test-")
        self.root = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def file(self, name, data=b"fictional"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_canonical_json_is_order_independent_and_has_no_self_hash(self):
        self.assertEqual(HELPER.canonical({"b": 2, "a": 1}), HELPER.canonical({"a": 1, "b": 2}))
        self.assertEqual(HELPER.canonical({"a": 1}), b'{"a":1}\n')

    def test_live_internal_files_and_publication_files_are_excluded(self):
        for name in ("AGENTS.md", "docs/SESSION-NOTES.md", "docs/PROJECT-PLAN.md",
                     "communication/checkpoints/state.json", "docs/checks/publication-20261104/REPORT.md",
                     ".codex/agents/reviewer.toml", "games/node_modules/unsafe.js"):
            with self.subTest(name=name):
                self.assertFalse(HELPER.publishable(name))

    def test_new_runtime_and_dated_historical_evidence_are_eligible(self):
        for name in ("README.md", "docs/YANNIS-CONTRIBUTIONS.md", "js/mulermoc-nom-core-54.js",
                     "js/jsme-nick-nomeclature-moc2-data_54.js", "css/namelecule-54.css",
                     "games/data/name-repair-alkanes.json", HELPER.PILOT,
                     "docs/checks/example-20261104/before/docs/SESSION-NOTES.md",
                     "docs/checks/example-20261103/run.log", "docs/V54-SYNC-20261104.md"):
            with self.subTest(name=name):
                self.assertTrue(HELPER.publishable(name))

    def test_react_and_all_52_paths_are_protected(self):
        for name in ("react-preview/dist/index.html", "react-preview/src/new.jsx",
                     "js/mulermoc-nom-core-52.js", "js/jsme-nick-nomeclature-moc2-data_52.js",
                     "css/namelecule-52.css", "mulermoc-nom-52.html"):
            with self.subTest(name=name):
                self.assertTrue(HELPER.protected(name))
                self.assertFalse(HELPER.publishable(name))

    def test_local_url_resolution_handles_queries_and_public_absolute_urls(self):
        self.assertEqual(HELPER.resolve_reference("design/welcome.html", "../mulermoc-nom-54.html?v=x"),
                         "mulermoc-nom-54.html")
        self.assertEqual(HELPER.resolve_reference("design/welcome.html", "../react-preview/dist/?v=x"),
                         "react-preview/dist/index.html")
        self.assertEqual(HELPER.resolve_reference("docs/report/index.html", HELPER.PUBLIC_PREFIX + "games/name-repair.html"),
                         "games/name-repair.html")
        self.assertIsNone(HELPER.resolve_reference("index.html", "https://external.test/app.js"))
        self.assertIsNone(HELPER.resolve_reference("index.html", "data:image/png;base64,AA=="))
        self.assertIsNone(HELPER.resolve_reference("index.html", "#inside"))

    def test_escaping_urls_and_symlink_paths_are_rejected(self):
        with self.assertRaises(RuntimeError):
            HELPER.resolve_reference("index.html", "../../outside")
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            HELPER.safe(self.root, "escape/file")

    def test_molecule_inventory_includes_later_explicit_registrations(self):
        text = 'let nameExamples = {\n  first: {\n  },\n  second: {\n  }\n};\n'
        text += 'nameExamples["third"] = {};\nnameExamples["first"] = {};\n'
        self.assertEqual(HELPER.molecule_keys(text), ["first", "second", "third"])

    def test_secret_scan_checks_large_binary_bytes_paths_only(self):
        secret = b"github" + b"_pat_" + b"X" * 34
        self.file("data.bin", b"\x00" * 2_100_000 + secret)
        with self.assertRaises(RuntimeError) as error:
            HELPER.scan(self.root, ["data.bin"])
        self.assertIn("data.bin", str(error.exception))
        self.assertNotIn(secret.decode(), str(error.exception))

    def dependency_fixture(self):
        for name in HELPER.HTML_ENTRIES:
            self.file(name, b"<!doctype html><html></html>")
        self.file("mulermoc-nom-54.html", b'<script src="js/example-54.js"></script>'
                  b'<script src="https://external.test/library.js"></script>')
        lessons = ["scenarios/theory-" + str(index) + ".json" for index in range(14)]
        links = []
        for index, name in enumerate(lessons):
            count = 324 if index == 0 else 1
            self.file(name, json.dumps({"steps": [{"selectedMol": "m0"}] * count}).encode())
            links.append('<a href="../mulermoc-nom-54.html?scenario=' + name + '&amp;present=1">lesson</a>')
        self.file("design/theory-library.html", "\n".join(links).encode())
        self.file(HELPER.PILOT, b'{"steps":[{"selectedMol":"m0","checkpoint":{"asset":"assets/pilot.svg"}}]}')
        self.file("games/data/name-repair-alkanes.json", json.dumps({"sets": [
            {"rounds": [{"asset": "assets/shared.svg"}] * 3},
            {"rounds": [{"asset": "assets/shared.svg"}] * 3}]}).encode())
        data = 'let nameExamples = {\n' + '\n'.join('  m' + str(index) + ': {' for index in range(136)) + '\n};\n'
        data += '\n'.join('nameExamples["m' + str(index) + '"] = {};' for index in range(136, 141))
        self.file("js/jsme-nick-nomeclature-moc2-data_54.js", data.encode())
        self.file("css/namelecule-54.css", b'.icon{background:url("../assets/icon.svg")}')
        names = {path.relative_to(self.root).as_posix() for path in self.root.rglob("*") if path.is_file()}
        names.update({"js/example-54.js", "assets/icon.svg", "games/assets/pilot.svg", "games/assets/shared.svg",
                      "js/vendor/jsmol/namelecule-20261031-r1/JSmol.min.js", "spt/init-54.spt"})
        names.update("mols/nomeclature-moc2/m" + str(index) + "_3D.sdf" for index in range(141))
        return {name: "fictional-digest" for name in names}

    def test_dependency_inventory_covers_game_pilot_theory_css_and_all_3d_paths(self):
        available = self.dependency_fixture()
        dependencies, external = HELPER.dependency_inventory(self.root, available)
        self.assertIn("games/assets/pilot.svg", dependencies)
        self.assertIn("games/assets/shared.svg", dependencies)
        self.assertIn("assets/icon.svg", dependencies)
        self.assertEqual(len([name for name in dependencies if name.endswith("_3D.sdf")]), 141)
        self.assertEqual(len([name for name in dependencies if name.startswith("scenarios/theory-")]), 14)
        self.assertIn("https://external.test/library.js", external)

    def test_dependency_inventory_rejects_missing_pilot_asset(self):
        available = self.dependency_fixture()
        del available["games/assets/pilot.svg"]
        with self.assertRaisesRegex(RuntimeError, "Missing local dependency"):
            HELPER.dependency_inventory(self.root, available)

    def test_dependency_inventory_rejects_unknown_pilot_molecule(self):
        available = self.dependency_fixture()
        self.file(HELPER.PILOT, b'{"steps":[{"selectedMol":"unknown"}]}')
        with self.assertRaisesRegex(RuntimeError, "unknown molecule"):
            HELPER.dependency_inventory(self.root, available)

    def test_frozen_manifest_requires_matching_detached_digest(self):
        self.file(HELPER.EVIDENCE + "/" + HELPER.MANIFEST, HELPER.canonical({"files": {}}))
        with self.assertRaisesRegex(RuntimeError, "detached SHA256"):
            HELPER.frozen_manifest(self.root, {})

    def test_tree_verification_retains_baseline_and_rejects_unexpected_files(self):
        base = self.file("retained.txt", b"old")
        protected = self.file("react-preview/dist/index.html", b"preserved")
        updated = self.file("games/new.json", b"new")
        manifest = {"baseFiles": {"retained.txt": HELPER.sha(base), "react-preview/dist/index.html": HELPER.sha(protected)},
                    "files": {"games/new.json": HELPER.sha(updated)},
                    "protectedFiles": {"react-preview/dist/index.html": HELPER.sha(protected)},
                    "dependencyHashes": {"games/new.json": HELPER.sha(updated)},
                    "reactPreservedPaths": 1, "sourceCutoffUTC": "fictional-cutoff"}
        result = HELPER.verify_tree(self.root, self.root, manifest)
        self.assertEqual(result["baseFilesDeleted"], 0)
        self.assertEqual(result["allPublicFiles"], 3)
        self.file("unexpected.txt")
        with self.assertRaisesRegex(RuntimeError, "Unexpected files"):
            HELPER.verify_tree(self.root, self.root, manifest)

    def test_atomic_output_refuses_existing_manifest(self):
        target = self.root / "manifest.json"
        HELPER.atomic_bytes(b"first", target)
        with self.assertRaises(FileExistsError):
            HELPER.atomic_bytes(b"second", target)
        self.assertEqual(target.read_bytes(), b"first")


if __name__ == "__main__":
    unittest.main(verbosity=2)
