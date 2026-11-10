"""Owned release browser/server, guarded cleanup; no personal GUI control."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import os,sys,json,socket,tempfile,subprocess,threading,time,signal,shutil
H=Path(__file__).resolve().parent

def port():
 with socket.socket()as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def command(pid):
 try:return subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True)
 except subprocess.CalledProcessError:return ''
if sys.argv[1]=='serve':
 root=Path(sys.argv[2]).resolve();hp,bp=port(),port();profile=tempfile.mkdtemp(prefix='namelecule-release-live-20261110-')
 Path(profile,'user.js').write_text('user_pref("remote.active-protocols",1);\nuser_pref("browser.shell.checkDefaultBrowser",false);\nuser_pref("browser.sessionstore.resume_from_crash",false);\n')
 ff=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',profile,'--remote-debugging-port',str(bp),'about:blank'],stdout=(H/'firefox.log').open('w'),stderr=subprocess.STDOUT,env={**os.environ,'MOZ_HEADLESS':'1'})
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**k):super().__init__(*a,directory=str(root),**k)
  def translate_path(self,path):
   prefix='/organic-nomenclature-3/'
   if path.startswith(prefix):path='/'+path[len(prefix):]
   return super().translate_path(path)
  def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
  def log_message(self,fmt,*args):
   with (H/'server-requests.log').open('a')as log:log.write(fmt%args+'\n')
 r={'candidateRoot':str(root),'serverPID':os.getpid(),'serverScript':str(Path(__file__).resolve()),'firefoxPID':ff.pid,'profile':profile,'http_port':hp,'bidi_port':bp,'base_url':f'http://127.0.0.1:{hp}/organic-nomenclature-3/','launchedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'Owned local prefix server and isolated headlessFirefox only; no personalFirefox control'}
 assert not(H/'process.json').exists();(H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
 threading.Thread(target=ThreadingHTTPServer(('127.0.0.1',hp),Handler).serve_forever,daemon=True).start()
 while ff.poll()is None:time.sleep(.5)
elif sys.argv[1]=='stop':
 r=json.loads((H/'process.json').read_text());actions=[]
 for field,token in [('firefoxPID',r['profile']),('serverPID',r['serverScript']+' serve '+r['candidateRoot'])]:
  pid=r[field];cmd=command(pid)
  if token in cmd:os.kill(pid,signal.SIGTERM);actions.append({'pid':pid,'signal':'TERM','matched':token})
  else:actions.append({'pid':pid,'signal':None,'reason':'not running or exact ownership guard failed'})
 time.sleep(.5)
 checks={}
 for label,pp in [('http',r['http_port']),('bidi',r['bidi_port'])]:
  try:
   with socket.create_connection(('127.0.0.1',pp),timeout=.2):checks[label]='still-listening'
  except OSError:checks[label]='refused'
 if checks['bidi']=='refused' and r['profile'].startswith('/var/folders/')or checks['bidi']=='refused' and 'namelecule-release-live-20261110-'in r['profile']:
  shutil.rmtree(r['profile']);checks['profileRemoved']=not Path(r['profile']).exists()
 r['cleanup']={'actions':actions,'ports':checks,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(H/'cleanup.json').write_text(json.dumps(r['cleanup'],indent=2)+'\n');print(json.dumps(r['cleanup']),flush=True)
