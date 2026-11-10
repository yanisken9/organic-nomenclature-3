"""Terminate only the two recorded parent processes after exact signature guards."""
from pathlib import Path
import json,subprocess,os,signal,time,socket
H=Path(__file__).resolve().parent;P=json.loads((H/'process.json').read_text());actions=[]
assert os.environ.get('NAMELECULE_CLEANUP_RELEASED')=='1','Developer must release owned processes explicitly'
for key,token in [('firefoxPID',P['profile']),('serverPID',str(Path(P['serverScript']).relative_to(Path.cwd())))]:
 pid=P[key]
 try:cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True)
 except subprocess.CalledProcessError:cmd=''
 if token in cmd:os.kill(pid,signal.SIGTERM);actions.append({'pid':pid,'signal':'TERM','matchedToken':token})
 else:actions.append({'pid':pid,'signal':None,'reason':'No longer running or signature mismatch'})
time.sleep(.5);ports={}
for key in ['bidi_port','before_port','after_port']:
 try:
  with socket.create_connection(('127.0.0.1',P[key]),timeout=.3):ports[key]='open'
 except OSError:ports[key]='closed'
(H/'cleanup.json').write_text(json.dumps({'actions':actions,'ports':ports,'UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'personalGUI':'Not targeted'},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actions':actions,'ports':ports}),flush=True)
