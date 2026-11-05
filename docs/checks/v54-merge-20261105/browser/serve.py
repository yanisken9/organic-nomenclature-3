"""Owned local test server, root and GitHub Pages-shaped prefix."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[4]
os.chdir(ROOT)


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        prefix = "/organic-nomenclature-3/"
        if path.startswith(prefix):
            path = "/" + path[len(prefix):]
        return super().translate_path(path)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8056), Handler)
    print("Engine pilot test server", os.getpid(), ROOT, flush=True)
    server.serve_forever()
