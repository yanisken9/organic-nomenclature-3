from pathlib import Path
import json,os,signal,socket,subprocess,time,shutil
H=Path(__file__).resolve().parent
p=json.loads((H/'process.json').read_text())
def command(pid):
 r=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
 return r.stdout.strip()
def alive(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False
out={'scope':'Only exact owned Firefox profile and own test-server script, never personal Firefox or localhost8013','before':{'firefox':command(p['firefoxPID']),'server':command(p['serverPID'])},'ports':{}}
assert '--profile '+p['profile']in out['before']['firefox'],out
relative=str(Path(p['serverScript']).relative_to(Path.cwd()))
assert out['before']['server'].endswith(' '+relative),out
os.kill(p['firefoxPID'],signal.SIGTERM)
end=time.monotonic()+12
while alive(p['firefoxPID'])and time.monotonic()<end:time.sleep(.15)
assert not alive(p['firefoxPID']),'Owned Firefox did not exit'
end=time.monotonic()+4
while alive(p['serverPID'])and time.monotonic()<end:time.sleep(.15)
if alive(p['serverPID']):
 assert command(p['serverPID']).endswith(' '+relative)
 os.kill(p['serverPID'],signal.SIGTERM)
 time.sleep(.3)
for name in ['before_port','after_port','bidi_port']:
 with socket.socket()as s:out['ports'][str(p[name])]=s.connect_ex(('127.0.0.1',p[name]))!=0
assert all(out['ports'].values()),out
profile=Path(p['profile'])
assert profile.name.startswith('namelecule-optional-triples-20261110-')and str(profile.parent).startswith('/var/folders/')
shutil.rmtree(profile)
out.update({'firefoxExited':not alive(p['firefoxPID']),'serverExited':not alive(p['serverPID']),'profileRemoved':not profile.exists(),'UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
(H/'cleanup.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
