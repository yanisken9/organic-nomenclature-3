"""Developer export runner: one disposable Firefox/server; invoke only with a granted slot."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import hashlib
import html
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def now():
    return datetime.now(timezone.utc).isoformat()


def gallery(outdir, base_url):
    """Use the browser's own SVG image rendering; no second molecular renderer."""
    manifest = json.loads((ROOT / "data/namelecule-alkanes-v1/manifest.json").read_text())
    provenance = json.loads((ROOT / "games/assets/name-repair/pool-v2-provenance.json").read_text())
    cards = []
    for row in manifest["molecules"]:
        for mode in ("expanded", "condensed"):
            asset = f"games/assets/name-repair/{mode}-v2/{row['id']}.svg"
            digest = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()
            cards.append('<article><h2>' + html.escape(row["nameGR"]) + ' · ' + mode +
                '</h2><img src="/' + asset + '?v=' + digest + '" alt="' + html.escape(row["nameGR"]) + '"></article>')
    page = ('<!doctype html><meta charset="utf-8"><title>Native Main57 alkane SVG exports</title>'
        '<style>body{margin:24px;background:#fafaf8;color:#254c50;font:18px system-ui}'
        'main{display:grid;grid-template-columns:1fr 1fr;gap:18px}article{background:white;'
        'border:1px solid #d4dada;border-radius:8px;padding:18px;display:flex;flex-direction:column;'
        'align-items:center}h1{font-size:24px}h2{font-size:18px;margin:0 0 16px}img{max-width:100%;'
        'height:auto;margin:auto}</style><h1>Actual Main57 exports · nominal labels 22px</h1><main>' +
        ''.join(cards) + '</main>')
    page_path = outdir / "gallery.html"
    page_path.write_text(page, encoding="utf-8")
    bidi = {"__name__": "namelecule_alkane_export_gallery"}
    try:
        exec(compile((ROOT / "tools/namelecule_bidi.py").read_text(), "namelecule_bidi", "exec"), bidi)
        bidi["call"]("browsingContext.setViewport", {"context": bidi["ctx"],
            "viewport": {"width": 1800, "height": 1400}, "devicePixelRatio": 1})
        bidi["navigate"](str(page_path.relative_to(ROOT)))
        bidi["until"]("document.images.length===12&&[...document.images].every(image=>image.complete&&image.naturalWidth>0)", seconds=30)
        metrics = json.loads(bidi["ev"]("JSON.stringify([...document.images].map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,height:i.naturalHeight})))"))
        screenshot = bidi["call"]("browsingContext.captureScreenshot", {"context": bidi["ctx"], "origin": "document"})
        (outdir / "gallery.png").write_bytes(base64.b64decode(screenshot["data"]))
        (outdir / "gallery.json").write_text(json.dumps({"role": "Developer real headless Firefox SVG image rendering",
            "metrics": metrics, "javascriptErrors": bidi["js_errors"], "assets": len(provenance["assets"]),
            "limits": "Screenshot requires visual inspection; no physical/mobile/offline/conference qualification"}, indent=2) + "\n")
    finally:
        try:
            if "ctx" in bidi:
                try:
                    bidi["call"]("browsingContext.close", {"context": bidi["ctx"]})
                finally:
                    bidi["call"]("session.end", {})
        finally:
            if "s" in bidi:
                bidi["s"].close()


def run():
    outdir = HERE / ("export-run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    outdir.mkdir()
    report = {"startedUTC": now(), "role": "Developer owned headless Firefox export, not independent review", "ownOnly": True}
    server = browser = profile = log = None

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, *args):
            pass

    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with socket.socket() as port_socket:
            port_socket.bind(("127.0.0.1", 0))
            port = port_socket.getsockname()[1]
        profile = Path(tempfile.mkdtemp(prefix="namelecule-alkane-export-", dir="/private/tmp"))
        log = (outdir / "firefox.log").open("w")
        env = dict(os.environ, NAMELECULE_BIDI_PORT=str(port),
            NAMELECULE_TEST_BASE_URL=f"http://127.0.0.1:{server.server_port}/",
            MOZ_HEADLESS_WIDTH="1800", MOZ_HEADLESS_HEIGHT="1400", PYTHONUNBUFFERED="1")
        browser = subprocess.Popen(["/Applications/Firefox.app/Contents/MacOS/firefox",
            "--headless", "--no-remote", "--profile", str(profile), "--width", "1800", "--height", "1400",
            "--remote-debugging-port", str(port)], env=env, stdout=log, stderr=subprocess.STDOUT)
        process = {"pid": browser.pid, "profile": str(profile), "bidiPort": port,
            "baseURL": env["NAMELECULE_TEST_BASE_URL"], "viewport": [1800, 1400]}
        (outdir / "process.json").write_text(json.dumps(process, indent=2) + "\n")
        print(json.dumps(process), flush=True)
        deadline = time.monotonic() + 40
        while True:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=.3):
                    break
            except OSError:
                if browser.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("Owned Firefox did not start")
                time.sleep(.2)
        with (outdir / "export.log").open("w") as output:
            result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/export-alkane-pool-assets.py"),
                "--bidi-port", str(port), "--base-url", env["NAMELECULE_TEST_BASE_URL"]],
                cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=600)
        report["exportExitCode"] = result.returncode
        if result.returncode:
            raise RuntimeError("Exporter failed; inspect export.log")
        os.environ["NAMELECULE_BIDI_PORT"] = str(port)
        os.environ["NAMELECULE_TEST_BASE_URL"] = env["NAMELECULE_TEST_BASE_URL"]
        gallery(outdir, env["NAMELECULE_TEST_BASE_URL"])
        report["exitCode"] = 0
    except Exception:
        report["exitCode"] = 1
        report["failure"] = traceback.format_exc()
    finally:
        if browser is not None:
            if browser.poll() is None:
                browser.terminate()
                try:
                    browser.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    browser.kill()
                    browser.wait(timeout=8)
            report["ownedBrowserExited"] = browser.poll() is not None
        if server is not None:
            server.shutdown()
            server.server_close()
            report["ownedServerClosed"] = True
        if log is not None:
            log.close()
        if profile is not None:
            assert profile.parent == Path("/private/tmp") and profile.name.startswith("namelecule-alkane-export-") and not profile.is_symlink()
            shutil.rmtree(profile)
            report["ownedProfileRemoved"] = not profile.exists()
        report["finishedUTC"] = now()
        (outdir / "run.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"outdir": str(outdir.relative_to(ROOT)), **report}), flush=True)
    return report["exitCode"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Run after the primary agent grants the browser slot")
    args = parser.parse_args()
    if not args.run:
        parser.error("Pass --run only after the browser slot is granted")
    raise SystemExit(run())
