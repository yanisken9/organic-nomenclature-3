from pathlib import Path
import json,socket,subprocess,tempfile,time
h=Path(__file__).resolve().parent;t=Path(tempfile.mkdtemp(prefix='namelecule-live-20261109-',dir='/private/tmp'));profile=t/'profile';profile.mkdir();(profile/'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.startup.homepage_override.mstone", "ignore");\nuser_pref("browser.aboutwelcome.enabled", false);\n')
s=socket.socket();s.bind(('127.0.0.1',0));port=s.getsockname()[1];s.close();cmd=['/Applications/Firefox.app/Contents/MacOS/firefox','-headless','-no-remote','-profile',str(profile),'--remote-debugging-port',str(port),'about:blank'];log=open(t/'firefox.log','wb');proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);p={'owner':'/root/teacher_alkane_prefix_browser','temp':str(t),'profile':str(profile),'firefox_pid':proc.pid,'firefox_command':cmd,'bidi_port':port,'base_url':'https://yanisken9.github.io/organic-nomenclature-3/','release':'98c22050de2cd81f36db734fe1556e3871c9f91b'};(h/'process.json').write_text(json.dumps(p,indent=2)+'\n')
for _ in range(100):
 try:s=socket.create_connection(('127.0.0.1',port),timeout=.2);s.close();break
 except OSError:time.sleep(.1)
else:raise RuntimeError('Owned headless port not ready')
print(json.dumps(p),flush=True)
