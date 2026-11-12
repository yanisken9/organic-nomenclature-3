from pathlib import Path
import json,os,signal,subprocess,time
h=Path(__file__).resolve().parent;r=json.loads((h/'process.json').read_text())
def args(pid):
 p=subprocess.run(['ps','-p',str(pid),'-o','args='],capture_output=True,text=True);return p.stdout.strip() if p.returncode==0 else ''
a=args(r['serverPID']);b=args(r['firefoxPID'])
assert str(h.relative_to(Path(__file__).resolve().parents[4]))+'/owned-processes.py' in a,(r['serverPID'],'identity mismatch')
assert r['profile'] in b and '--headless' in b,(r['firefoxPID'],'identity mismatch')
os.kill(r['serverPID'],signal.SIGTERM)
end=time.monotonic()+15
while time.monotonic()<end and (args(r['serverPID']) or args(r['firefoxPID'])):time.sleep(.2)
out={'serverPID':r['serverPID'],'firefoxPID':r['firefoxPID'],'identityGuardsPassed':True,'serverExited':not bool(args(r['serverPID'])),'firefoxExited':not bool(args(r['firefoxPID'])),'scope':'Only owned headless and its server; no personal or user-facing GUI browser control.'}
(h/'cleanup.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['serverExited']and out['firefoxExited']
