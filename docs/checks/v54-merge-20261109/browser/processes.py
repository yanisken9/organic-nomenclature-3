"""Start/stop only recorded owned headless Firefox and candidate HTTP server."""
from pathlib import Path
import json,socket,subprocess,os,time,tempfile,signal,sys
H=Path(__file__).resolve().parent
C='/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate'
def free():
 with socket.socket()as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def owned(pid,token):
 try:return token in subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True)
 except Exception:return False
if sys.argv[1]=='start':
 if (H/'process.json').exists():raise SystemExit('Existing process record: inspect/stop owned processes first')
 hp,bp=free(),free();profile=tempfile.mkdtemp(prefix='namelecule-v55-owned-firefox-')
 server=subprocess.Popen([sys.executable,'-B',str(H/'serve.py'),C,str(hp)],stdout=(H/'server.log').open('w'),stderr=subprocess.STDOUT)
 ff='/Applications/Firefox.app/Contents/MacOS/firefox'
 browser=subprocess.Popen([ff,'--headless','--no-remote','--profile',profile,'--remote-debugging-port',str(bp),'about:blank'],env={**os.environ,'MOZ_HEADLESS':'1'},stdout=(H/'firefox.log').open('w'),stderr=subprocess.STDOUT)
 record={'candidateRoot':C,'http_port':hp,'bidi_port':bp,'base_url':f'http://127.0.0.1:{hp}/organic-nomenclature-3/','profile':profile,'serverPID':server.pid,'firefoxPID':browser.pid,'launchedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'cleanupGuard':'Only kill recorded PIDs when ps command includes exact owned profile/serve.py token; never personal GUI Firefox'}
 (H/'process.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
 for _ in range(150):
  try:
   with socket.create_connection(('127.0.0.1',bp),timeout=.1):break
  except OSError:time.sleep(.2)
 else:raise SystemExit('Owned Firefox BiDi not ready; inspect logs')
elif sys.argv[1]=='stop':
 r=json.loads((H/'process.json').read_text());actions=[]
 for k,t in [('firefoxPID',r['profile']),('serverPID','/docs/checks/v54-merge-20261109/browser/serve.py '+r['candidateRoot']+' '+str(r['http_port']))]:
  pid=r[k]
  if owned(pid,t):os.kill(pid,signal.SIGTERM);actions.append({'pid':pid,'signal':'TERM','token':t})
  else:actions.append({'pid':pid,'signal':None,'reason':'not running or ownership token does not match'})
 r['cleanup']=actions;r['cleanupUTC']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());(H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(actions))
