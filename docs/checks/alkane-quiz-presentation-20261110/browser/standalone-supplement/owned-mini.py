from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import tempfile,os,json,socket,subprocess,sys,time
H=Path(__file__).resolve().parent;ROOT=Path.cwd()
def port():
 with socket.socket()as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
http_port,bidi_port=port(),port();profile=tempfile.mkdtemp(prefix='namelecule-standalone-objective-20261110-');Path(profile,'user.js').write_text('user_pref("remote.active-protocols",1);\nuser_pref("browser.shell.checkDefaultBrowser",false);\n');ff=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',profile,'--remote-debugging-port',str(bidi_port)],stdout=(H/'firefox.log').open('w'),stderr=subprocess.STDOUT)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
r={'serverPID':os.getpid(),'serverScript':'docs/checks/alkane-quiz-presentation-20261110/browser/standalone-supplement/owned-mini.py','firefoxPID':ff.pid,'profile':profile,'http_port':http_port,'bidi_port':bidi_port,'base_url':f'http://127.0.0.1:{http_port}/','scope':'One bounded standalone objective probe; no personalGUI'};assert not(H/'process.json').exists();(H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True);ThreadingHTTPServer(('127.0.0.1',http_port),Handler).serve_forever()
