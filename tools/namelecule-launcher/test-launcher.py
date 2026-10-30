"""Bounded launcher checks using temporary roots, cache and loopback ports."""

import concurrent.futures
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import BadStatusLine, IncompleteRead
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request


spec = importlib.util.spec_from_file_location("launcher", Path(__file__).with_name("launcher.py"))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class LauncherChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="Namelecule έλεγχος ' ")
        self.root = Path(self.temporary.name)
        (self.root / "index.html").write_text("fixture welcome", encoding="utf-8")
        self.cache = self.root / "cache"
        self.children = []
        original_popen = subprocess.Popen

        def track(*args, **kwargs):
            child = original_popen(*args, **kwargs)
            self.children.append(child)
            return child

        self.popen_patch = patch.object(launcher.subprocess, "Popen", side_effect=track)
        self.popen_patch.start()

    def tearDown(self):
        self.popen_patch.stop()
        for child in self.children:
            if child.poll() is None:
                child.terminate()
            child.wait(timeout=3)
        self.temporary.cleanup()

    def test_start_reuse_and_correct_root(self):
        (self.root / "index.html").write_text("fixture welcome", encoding="utf-8")
        port = free_port()
        self.assertEqual(launcher.ensure_server(self.root, self.cache, [port]), port)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open("http://127.0.0.1:%d/index.html" % port, timeout=2) as response:
            self.assertEqual(response.read(), b"fixture welcome")
        self.assertTrue(launcher.running_here(port, launcher.project_id(self.root)))
        self.assertFalse(launcher.running_here(port, launcher.project_id(self.root / "other")))
        self.assertEqual(launcher.ensure_server(self.root, self.cache, [port]), port)
        self.assertEqual(len(self.children), 1)
        self.assertIsNone(self.children[0].poll())

    def test_unrelated_occupied_port_is_preserved(self):
        class ForeignHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"unrelated server")

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), ForeignHandler) as foreign:
            thread = threading.Thread(target=foreign.serve_forever, daemon=True)
            thread.start()
            try:
                busy = foreign.server_port
                available = free_port()
                self.assertEqual(launcher.ensure_server(self.root, self.cache, [busy, available]), available)
                self.assertTrue(thread.is_alive())
                self.assertFalse(launcher.running_here(busy, launcher.project_id(self.root)))
                with self.assertRaises(RuntimeError):
                    launcher.ensure_server(self.root, self.cache, [busy])
            finally:
                foreign.shutdown()
                thread.join(timeout=2)

    def test_simultaneous_launches_share_one_server(self):
        port = free_port()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            ports = list(pool.map(lambda _: launcher.ensure_server(self.root, self.cache, [port]), range(2)))
        self.assertEqual(ports, [port, port])
        self.assertEqual(len(self.children), 1)

    def test_malformed_or_truncated_foreign_response_is_skipped(self):
        for error in (BadStatusLine("not HTTP"), IncompleteRead(b"partial", 10)):
            with self.subTest(error=type(error).__name__):
                with patch.object(urllib.request.OpenerDirector, "open", side_effect=error):
                    self.assertFalse(launcher.running_here(8013, "expected project"))

    def test_missing_project_fails_before_starting_server(self):
        config = self.root / "project.json"
        config.write_text(json.dumps({"project_root": str(self.root / "moved")}), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Δεν βρέθηκε ο φάκελος"):
            launcher.launch(config)
        self.assertEqual(self.children, [])

    def test_missing_firefox_fails_before_starting_server(self):
        (self.root / "design").mkdir()
        (self.root / "design/welcome-proposal.html").write_text("welcome")
        (self.root / "mulermoc-nom-52.html").write_text("app")
        config = self.root / "project.json"
        config.write_text(json.dumps({"project_root": str(self.root)}), encoding="utf-8")
        with patch.object(launcher, "FIREFOX", self.root / "missing Firefox.app"):
            with self.assertRaisesRegex(RuntimeError, "Δεν βρέθηκε το Firefox"):
                launcher.launch(config)
        self.assertEqual(self.children, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
