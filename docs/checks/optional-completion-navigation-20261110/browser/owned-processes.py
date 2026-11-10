"""Own two localhost HTTP servers and one isolated headless Firefox only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import os,sys,json,socket,tempfile,subprocess,threading,time
from urllib.parse import urlsplit
H=Path(__file__).resolve().parent;ROOT=Path.cwd();BEFORE=H/'before'
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def handler(before):
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
  def do_GET(self):
   clean=urlsplit(self.path).path
   fault=json.loads((H/'fault-control.json').read_text())
   if clean==fault.get('path') and fault.get('mode')!='normal':
    mode=fault['mode']; started=time.monotonic()
    with (H/'fault-requests.jsonl').open('a') as log:log.write(json.dumps({'path':clean,'mode':mode,'phase':'start','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})+'\n')
    if mode=='delay':
     while time.monotonic()-started<30 and json.loads((H/'fault-control.json').read_text()).get('mode')=='delay':time.sleep(.05)
    elif mode=='error':
     self.send_response(503);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b'Controlled test image failure');return
   return super().do_GET()
  def end_headers(self):
   self.send_header('Cache-Control','no-store');super().end_headers()
  def translate_path(self,path):
   clean=path.split('?',1)[0].lstrip('/')
   if before and (BEFORE/clean).is_file():return str(BEFORE/clean)
   return super().translate_path(path)
  def log_message(self,*args):pass
 return Handler
p_before,p_after,p_bidi=port(),port(),port();profile=tempfile.mkdtemp(prefix='namelecule-optional-completion-navigation-20261110-')
Path(profile,'user.js').write_text('user_pref("remote.active-protocols", 1);\nuser_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.sessionstore.resume_from_crash", false);\n')
ff=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',profile,'--remote-debugging-port',str(p_bidi)],stdout=(H/'firefox.log').open('w'),stderr=subprocess.STDOUT)
r={'serverPID':os.getpid(),'serverScript':str(Path(__file__).resolve()),'firefoxPID':ff.pid,'profile':profile,'bidi_port':p_bidi,'before_port':p_before,'after_port':p_after,'before_url':f'http://127.0.0.1:{p_before}/','after_url':f'http://127.0.0.1:{p_after}/','launchedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'Only new headless isolated profile; before overlay uses exact frozen three files; no personal GUI control'}
assert not(H/'process.json').exists();(H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
for pp,bb in [(p_before,True),(p_after,False)]:threading.Thread(target=ThreadingHTTPServer(('127.0.0.1',pp),handler(bb)).serve_forever,daemon=True).start()
while ff.poll() is None:time.sleep(.5)
