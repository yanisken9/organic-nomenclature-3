"""Own one ephemeral localhost server and one headless test Firefox only."""
from pathlib import Path
import http.server, json, os, signal, socket, subprocess, tempfile, threading, time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

BEFORE = HERE.parent / 'before'
BASELINE = json.loads((HERE.parent / 'baseline.json').read_text())
class BeforeHandler(Handler):
    def translate_path(self, path):
        current = Path(super().translate_path(path))
        try: relative = current.relative_to(ROOT).as_posix()
        except ValueError: return str(current)
        return str(BEFORE / relative) if relative in BASELINE['proposedTarget'] else str(current)
before_server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), BeforeHandler)
threading.Thread(target=before_server.serve_forever, daemon=True).start()
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    bidi_port = probe.getsockname()[1]
profile = tempfile.mkdtemp(prefix='namelecule-header-text-headless-20261111-')
log = (HERE / 'firefox.log').open('w')
firefox = subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox', '--headless',
    '--no-remote', '--profile', profile, '--remote-debugging-port', str(bidi_port)],
    stdout=log, stderr=subprocess.STDOUT)
record = {'serverPID':os.getpid(), 'serverScript':str(Path(__file__).resolve()),
    'firefoxPID':firefox.pid, 'profile':profile, 'bidiPort':bidi_port,
    'baseURL':f'http://127.0.0.1:{server.server_port}/',
    'baselineURL':f'http://127.0.0.1:{before_server.server_port}/',
    'beforePaths':list(BASELINE['proposedTarget']),
    'scope':'Only this newly owned headless profile/server. No personal GUI browser control.'}
(HERE / 'process.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record), flush=True)
def stop(*args):
    raise SystemExit(0)
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
try:
    while firefox.poll() is None:
        time.sleep(.5)
finally:
    server.shutdown()
    before_server.shutdown()
    if firefox.poll() is None:
        firefox.terminate()
        try:
            firefox.wait(timeout=10)
        except subprocess.TimeoutExpired:
            firefox.kill()
    log.close()
