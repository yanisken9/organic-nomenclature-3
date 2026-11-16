"""Developer checks in one owned headless Firefox; never attach to a user profile."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, shutil, socket, subprocess, sys, tempfile, threading, traceback

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
label = 'run-' + sys.argv[1] + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S')
outdir = HERE / label
outdir.mkdir()
out = {'startedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'ownOnly': True, 'label': label}
server = browser = profile = log = None

class Handler(http.server.SimpleHTTPRequestHandler):
    fail_child_once = sys.argv[1] == 'retry'
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
    def log_message(self, *a): pass
    def do_GET(self):
        if Handler.fail_child_once and self.path.startswith('/games/molecular-detective-viewer.html'):
            Handler.fail_child_once = False
            self.send_error(404, 'Controlled initial child failure for retry acceptance')
            return
        return super().do_GET()

try:
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    profile = Path(tempfile.mkdtemp(prefix='namelecule-detective-test-', dir='/private/tmp'))
    log = (outdir / 'firefox.log').open('w')
    browser = subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox', '--headless', '--no-remote', '--profile', str(profile), '--remote-debugging-port', str(port)], stdout=log, stderr=subprocess.STDOUT)
    process = {'root': str(ROOT), 'base_url': 'http://127.0.0.1:' + str(server.server_port) + '/', 'bidi_port': port, 'profile': str(profile), 'pid': browser.pid}
    (outdir / 'process.json').write_text(json.dumps(process, indent=2) + '\n')
    env = dict(os.environ, NAMELECULE_BIDI_PORT=str(port), NAMELECULE_TEST_BASE_URL=process['base_url'], DETECTIVE_TEST_OUT=str(outdir), PYTHONUNBUFFERED='1')
    print(json.dumps(process), flush=True)
    import time
    deadline = time.monotonic() + 30
    while True:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=.3): break
        except OSError:
            if browser.poll() is not None or time.monotonic() > deadline: raise RuntimeError('Owned browser did not start')
            time.sleep(.2)
    with (outdir / 'driver.log').open('w') as output:
        result = subprocess.run(['python3', '-B', str(HERE / (sys.argv[1] + '.py'))], env=env, stdout=output, stderr=subprocess.STDOUT, timeout=600)
    out['exitCode'] = result.returncode
except Exception:
    out['exitCode'] = 1
    out['failure'] = traceback.format_exc()
finally:
    if browser is not None:
        if browser.poll() is None:
            browser.terminate()
            try: browser.wait(timeout=8)
            except subprocess.TimeoutExpired: browser.kill(); browser.wait(timeout=8)
        out['ownedBrowserExited'] = browser.poll() is not None
    if server is not None:
        server.shutdown(); server.server_close(); out['ownedServerClosed'] = True
    if log is not None: log.close()
    if profile is not None:
        assert profile.parent == Path('/private/tmp') and profile.name.startswith('namelecule-detective-test-') and not profile.is_symlink()
        shutil.rmtree(profile)
        out['ownedProfileRemoved'] = not profile.exists()
    out['finishedUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (outdir / 'run.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(out), flush=True)
sys.exit(out['exitCode'])
