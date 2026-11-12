"""Actual Builder progression; construction actions never scroll test targets."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess, sys, tempfile, threading, time, traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MODE='cancel-api'
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with socket.socket() as probe:
    probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
profile=Path(tempfile.mkdtemp(prefix='namelecule-builder-workspace-'+MODE+'-20261112-'))
(profile/'user.js').write_text('user_pref("ui.prefersReducedMotion", '+('1' if MODE=='reduced' else '0')+');\n')
log=(HERE/('flow-'+MODE+'-firefox.log')).open('w')
firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
process={'serverPID':os.getpid(),'serverScript':str(Path(__file__).resolve()),'firefoxPID':firefox.pid,'profile':str(profile),'bidiPort':port,'baseURL':f'http://127.0.0.1:{server.server_port}/','mode':MODE,'scope':'Only owned temporary headless profile/server; personal browsers untouched.'}
(HERE/'process.json').write_text(json.dumps(process,indent=2)+'\n')
(HERE/('flow-'+MODE+'-process.json')).write_text(json.dumps(process,indent=2)+'\n')
print(json.dumps(process),flush=True)

results={'conditions':'Isolated native CSSOM scroll APIs only, no application; fresh disposable profile','entries':[],'completed':False}
try:
 deadline=time.monotonic()+25
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.3):break
  except OSError:
   if time.monotonic()>deadline:raise
   time.sleep(.2)
 exec(compile((HERE/'driver.py').read_text(),str(HERE/'driver.py'),'exec'))
 open_page('docs/checks/builder-tile-workspace-20261112/browser/cancel-control.html')
 wait('!!document.getElementById("box")')
 for target in ['element','window']:
  ref='document.getElementById("box")' if target=='element' else 'window'
  pos='document.getElementById("box").scrollTop' if target=='element' else 'scrollY'
  for method in ['same-instant','same-auto','assignment','offset-instant','zero-relative','control']:
   ev('('+ref+').scrollTo({top:0,behavior:"instant"});true');time.sleep(.6)
   ev('('+ref+').scrollTo({top:800,behavior:"smooth"});true');time.sleep(.08)
   a=read(pos);time.sleep(.035);b=read(pos)
   code={'same-instant':'t.scrollTo({top:p,behavior:"instant"})','same-auto':'t.scrollTo({top:p,behavior:"auto"})','assignment':'e.scrollTop=p','offset-instant':'t.scrollTo({top:p+1,behavior:"instant"});t.scrollTo({top:p,behavior:"instant"})','zero-relative':'t.scrollBy({top:0,behavior:"instant"})','control':''}[method]
   ev('(()=>{const t='+ref+',e='+('document.getElementById("box")' if target=='element' else 'document.scrollingElement')+',p='+pos+';'+code+';return true})()')
   time.sleep(.05);after=read(pos);time.sleep(.5);later=read(pos)
   entry={'target':target,'method':method,'a':a,'b':b,'after':after,'later':later,'movingBefore':abs(b-a)>1,'stableAfter':abs(later-after)<=1}
   results['entries'].append(entry);print(json.dumps(entry),flush=True)
 results['completed']=True
except Exception:
 results['failure']=traceback.format_exc();print(results['failure'],flush=True)
finally:
 (HERE/'cancel-api-results.json').write_text(json.dumps(results,indent=2)+'\n')
 try:
  if 'finish' in globals():finish()
 except Exception:pass
 server.shutdown();server.server_close()
 if firefox.poll() is None:
  firefox.terminate()
  try:firefox.wait(timeout=10)
  except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
 log.close();process['ownedFirefoxExited']=firefox.poll() is not None;process['ownedServerClosed']=True
 (HERE/'cancel-api-cleanup.json').write_text(json.dumps(process,indent=2)+'\n')
if not results['completed']:raise SystemExit(1)
