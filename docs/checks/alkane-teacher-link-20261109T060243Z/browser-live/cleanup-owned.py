from pathlib import Path
import os,signal,subprocess,json,socket,time,shutil
h=Path(__file__).resolve().parent;p=json.loads((h/'process.json').read_text());pid=p['firefox_pid'];cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip();assert '-headless' in cmd and '-no-remote' in cmd and p['profile'] in cmd and '--remote-debugging-port '+str(p['bidi_port']) in cmd,cmd;pgid=os.getpgid(pid);assert pgid==pid;os.killpg(pgid,signal.SIGTERM)
for _ in range(30):
 try:s=socket.create_connection(('127.0.0.1',p['bidi_port']),timeout=.1);s.close();time.sleep(.1)
 except OSError:break
else:raise RuntimeError('Owned endpoint still open')
shutil.copy2(Path(p['temp'])/'firefox.log',h/'firefox.log');out={'completed':True,'verifiedCommand':cmd,'pid':pid,'ownedGroup':pgid,'signal':'SIGTERM only exactownedheadlessgroup','portClosed':p['bidi_port'],'personalGUIAndDriversUntouched':True,'retainedOwnedTemp':p['temp']};(h/'cleanup.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
