"""Start only after exact17 installation; cleanup requires separate root release."""
from pathlib import Path
import json,subprocess,socket,os,sys,time,signal,hashlib
H=Path(__file__).resolve().parent;ROOT=Path.cwd();parent=json.loads((H.parent/'process.json').read_text());target=json.loads((H.parent.parent/'verification-target.json').read_text())
def command(pid):
 try:return subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True)
 except Exception:return ''
if sys.argv[1]=='start':
 assert os.environ.get('NAMELECULE_INSTALL_CONFIRMED')=='1','Root install-complete signal required'
 assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==s for p,s in target['files'].items()),'Primary17 mismatch'
 assert parent['profile']in command(parent['firefoxPID']),'Owned Firefox profile guard failed'
 assert not(H/'process.json').exists(),'Refuse overwrite existing primary process record'
 with socket.socket()as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 p=subprocess.Popen([sys.executable,'-B',str(H/'server.py'),str(port),str(ROOT)],stdout=(H/'server.log').open('w'),stderr=subprocess.STDOUT)
 r={'primaryRoot':str(ROOT),'http_port':port,'base_url':f'http://127.0.0.1:{port}/organic-nomenclature-3/','primaryServerPID':p.pid,'bidi_port':parent['bidi_port'],'firefoxPID':parent['firefoxPID'],'profile':parent['profile'],'candidateServerPID':parent['serverPID'],'candidateHTTPPort':parent['http_port'],'candidateRoot':parent['candidateRoot'],'launchedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'cleanupGuard':'Only recorded PIDs after exact owned profile or ASCII script+port signatures; no personal GUI process'}
 (H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
 for _ in range(50):
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.1):break
  except OSError:time.sleep(.1)
elif sys.argv[1]=='stop':
 assert os.environ.get('NAMELECULE_CLEANUP_RELEASED')=='1','Root cleanup release required'
 r=json.loads((H/'process.json').read_text());actions=[]
 for key,token in [('primaryServerPID','/primary-smoke/server.py '+str(r['http_port'])),('candidateServerPID','/browser/serve.py '+r['candidateRoot']+' '+str(r['candidateHTTPPort'])),('firefoxPID',r['profile'])]:
  pid=r[key];cmd=command(pid)
  if token in cmd:os.kill(pid,signal.SIGTERM);actions.append({'pid':pid,'signal':'TERM','matchedToken':token})
  else:actions.append({'pid':pid,'signal':None,'reason':'not running or signature does not match'})
 r['cleanup']=actions;r['cleanupUTC']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());(H/'process.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(actions),flush=True)
