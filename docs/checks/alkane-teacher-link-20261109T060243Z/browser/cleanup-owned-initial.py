from pathlib import Path
import json,subprocess,os,signal,time,shutil,socket
h=Path(__file__).resolve().parent;p=json.loads((h/'process.json').read_text());events=[]
for kind in ['firefox','server']:
 pid=p[kind+'_pid'];r=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True);command=r.stdout.strip()
 if kind=='firefox':safe=('-headless' in command and '-no-remote' in command and p['profile'] in command and '--remote-debugging-port '+str(p['bidi_port']) in command)
 else:safe=(str(h/'serve-prefix.py') in command and str(p['http_port']) in command and p['server_command'][2] in command)
 assert safe,(kind,pid,command)
 pgid=os.getpgid(pid);assert pgid==pid,(kind,pid,pgid);os.killpg(pgid,signal.SIGTERM);events.append({'kind':kind,'pid':pid,'exactCommandVerified':command,'processGroup':pgid,'signal':'SIGTERM only owned isolated processgroup'})
for _ in range(30):
 alive=[]
 for port in [p['http_port'],p['bidi_port']]:
  try:c=socket.create_connection(('127.0.0.1',port),timeout=.1);c.close();alive.append(port)
  except OSError:pass
 if not alive:break
 time.sleep(.1)
assert not alive,alive
for name in ['http.log','firefox.log']:shutil.copy2(Path(p['temp'])/name,h/name)
result={'completed':True,'events':events,'portsClosed':[p['http_port'],p['bidi_port']],'no_personal_gui_or_other_driver_touched':True,'retainedOwnedTempForEvidence':p['temp']};(h/'cleanup.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
