"""Own two localhost HTTP servers and one isolated headless Firefox only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import os,sys,json,socket,tempfile,subprocess,threading,time
H=Path(__file__).resolve().parent;ROOT=Path.cwd();BEFORE=H/'before'
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def handler(before):
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
  def translate_path(self,path):
   clean=path.split('?',1)[0].lstrip('/')
   if before and (BEFORE/clean).is_file():return str(BEFORE/clean)
   return super().translate_path(path)
  def log_message(self,*args):pass
 return Handler
p_before,p_after,p_bidi=port(),port(),port();profile=tempfile.mkdtemp(prefix='namelecule-required-completion-navigation-20261110-')
Path(profile,'user.js').write_text('user_pref("remote.active-protocols", 1);\nuser_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.sessionstore.resume_from_crash", false);\n')
ff=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',profile,'--remote-debugging-port',str(p_bidi)],stdout=(H/'firefox.log').open('w'),stderr=subprocess.STDOUT)
r={'serverPID':os.getpid(),'serverScript':str(Path(__file__).resolve()),'firefoxPID':ff.pid,'profile':profile,'bidi_port':p_bidi,'before_port':p_before,'after_port':p_after,'before_url':f'http://127.0.0.1:{p_before}/','after_url':f'http://127.0.0.1:{p_after}/','launchedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'Only new headless isolated profile; before overlay uses exact frozen three files; no personal GUI control'}
assert not(H/'process.json').exists();(H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
for pp,bb in [(p_before,True),(p_after,False)]:threading.Thread(target=ThreadingHTTPServer(('127.0.0.1',pp),handler(bb)).serve_forever,daemon=True).start()
while ff.poll() is None:time.sleep(.5)
