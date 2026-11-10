"""Guard exact recorded test signatures; no personal browser or other server targets."""
from pathlib import Path
import json,subprocess,os,signal,time,socket
H=Path(__file__).resolve().parent;assert os.environ.get('NAMELECULE_CLEANUP_RELEASED')=='1';out={'actions':[],'ports':{},'personalGUI':'Not targeted'}
for record in ('process.json','process-reduced.json'):
 p=json.loads((H/record).read_text())
 for key,token in (('firefoxPID',p['profile']),('serverPID',p['serverScript'].split('organic-nomenclature-3/',1)[-1])):
  try:cmd=subprocess.check_output(['ps','-p',str(p[key]),'-o','command='],text=True,stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError:cmd=''
  if token in cmd and (key!='firefoxPID' or ('--headless' in cmd and '--no-remote' in cmd)):
   os.kill(p[key],signal.SIGTERM);out['actions'].append({'record':record,'pid':p[key],'signal':'TERM','matchedToken':token})
  else:out['actions'].append({'record':record,'pid':p[key],'signal':None,'reason':'Not running or exact signature absent'})
 time.sleep(.5)
 for key in ('bidi_port','before_port','after_port'):
  try:
   with socket.create_connection(('127.0.0.1',p[key]),timeout=.3):status='open'
  except OSError:status='closed'
  out['ports'][str(p[key])]=status
out['UTC']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());(H/'cleanup.json').write_text(json.dumps(out,indent=2)+'\n');assert all(v=='closed' for v in out['ports'].values()),out;print(json.dumps(out))
