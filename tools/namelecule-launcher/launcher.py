"""Local macOS launcher; does not modify the Namelecule application."""

import argparse
import fcntl
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPException
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request


IDENTITY_PATH = "/.namelecule-launcher"
PORTS = range(8013, 8033)
FIREFOX = Path("/Applications/Firefox.app")


def project_id(root):
    return hashlib.sha256(os.fsencode(str(root.resolve()))).hexdigest()


def running_here(port, identity):
    # Ignore proxy environment settings for a strictly loopback request.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open("http://127.0.0.1:%d%s" % (port, IDENTITY_PATH), timeout=0.3) as response:
            payload = json.loads(response.read(4096))
        return payload == {"namelecule_project": identity}
    except (OSError, ValueError, HTTPException):
        return False


def serve(root, port):
    # Fail explicitly if the detached process cannot read the project (e.g.
    # macOS Desktop access), rather than reporting readiness and serving 404s.
    (root / "index.html").read_bytes()
    identity = project_id(root)

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == IDENTITY_PATH:
                payload = json.dumps({"namelecule_project": identity}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                super().do_GET()

    handler = functools.partial(Handler, directory=str(root))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        server.serve_forever()


def ensure_server(root, cache, ports=PORTS):
    identity = project_id(root)
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Serialize launches from double-clicks. The child does not inherit the lock.
    with (cache / (identity + ".lock")).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for port in ports:
            if running_here(port, identity):
                return port
        for port in ports:
            with (cache / (identity + ".log")).open("ab") as log:
                child = subprocess.Popen(
                    ["/usr/bin/python3", "-B", str(Path(__file__).resolve()),
                     "--serve", str(root), str(port)],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                    start_new_session=True, close_fds=True,
                )
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if child.poll() is not None:
                    break  # Occupied/unavailable port: never stop its owner.
                if running_here(port, identity):
                    return port
                time.sleep(0.08)
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
    raise RuntimeError("Δεν ξεκίνησε ο τοπικός server. Κλείσε και άνοιξε ξανά το Namelecule.\nΑρχείο ελέγχου: " + str(cache))


def launch(config):
    root = Path(json.loads(config.read_text(encoding="utf-8"))["project_root"]).resolve()
    if not all((root / name).is_file() for name in (
            "index.html", "design/welcome-proposal.html", "mulermoc-nom-52.html")):
        raise RuntimeError("Δεν βρέθηκε ο φάκελος του Namelecule. Αν τον μετακίνησες, χρειάζεται ενημέρωση του εικονιδίου.\n" + str(root))
    if not FIREFOX.is_dir():
        raise RuntimeError("Δεν βρέθηκε το Firefox στον φάκελο Applications. Εγκατάστησέ το και δοκίμασε ξανά.")
    try:
        (root / "index.html").read_bytes()
    except PermissionError:
        raise RuntimeError("Το macOS δεν επιτρέπει πρόσβαση στον φάκελο του Namelecule. Επίτρεψε την πρόσβαση στην Επιφάνεια Εργασίας για το Namelecule στις Ρυθμίσεις συστήματος → Απόρρητο και ασφάλεια → Αρχεία και φάκελοι.")
    cache = Path.home() / "Library/Caches/Namelecule"
    port = ensure_server(root, cache)
    url = "http://127.0.0.1:%d/design/welcome-proposal.html" % port
    subprocess.run(["/usr/bin/open", "-a", str(FIREFOX), url], check=True)
    print(url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", nargs=2, metavar=("ROOT", "PORT"))
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    try:
        if args.serve:
            serve(Path(args.serve[0]).resolve(), int(args.serve[1]))
        elif args.config:
            launch(args.config)
        else:
            parser.error("--config or --serve required")
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
