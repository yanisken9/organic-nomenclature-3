from pathlib import Path
import json,os,socket,subprocess,tempfile,time
here=Path(__file__).resolve().parent;candidate=json.loads((here.parent/'candidate.json').read_text());temp=Path(tempfile.mkdtemp(prefix='namelecule-teacher-prefix-20261109-',dir='/private/tmp'));profile=temp/'profile';profile.mkdir()
(profile/'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.startup.homepage_override.mstone", "ignore");\nuser_pref("browser.aboutwelcome.enabled", false);\nuser_pref("ui.prefersReducedMotion", 0);\n')
def freeport():
 s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p
http=freeport();bidi=freeport();server_cmd=['python3',str(here/'serve-prefix.py'),candidate['publicClone'],str(http)];firefox_cmd=['/Applications/Firefox.app/Contents/MacOS/firefox','-headless','-no-remote','-profile',str(profile),'--remote-debugging-port',str(bidi),'about:blank'];serverlog=open(temp/'http.log','wb');fflog=open(temp/'firefox.log','wb');server=subprocess.Popen(server_cmd,stdout=serverlog,stderr=subprocess.STDOUT,start_new_session=True);firefox=subprocess.Popen(firefox_cmd,stdout=fflog,stderr=subprocess.STDOUT,start_new_session=True)
data={'owner':'/root/teacher_alkane_prefix_browser','temp':str(temp),'profile':str(profile),'server_pid':server.pid,'firefox_pid':firefox.pid,'server_command':server_cmd,'firefox_command':firefox_cmd,'http_port':http,'bidi_port':bidi,'base_url':f'http://127.0.0.1:{http}/organic-nomenclature-3/'+candidate['prefix']+'/','candidate_metadata':str(here.parent/'candidate.json')};(here/'process.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data),flush=True)
for port in [http,bidi]:
 for _ in range(100):
  try:s=socket.create_connection(('127.0.0.1',port),timeout=.2);s.close();break
  except OSError:time.sleep(.1)
 else:raise RuntimeError('owned process port not ready '+str(port))
