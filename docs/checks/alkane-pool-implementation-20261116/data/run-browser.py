"""Run one bounded task-owned native headless browser, then clean it up."""
from pathlib import Path
import datetime,http.server,json,os,socket,subprocess,sys,tempfile,threading,time,traceback,shutil
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
label='run-'+sys.argv[1]+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S');OUT=HERE/label;OUT.mkdir()
out={'role':'Developer browser evidence','root':str(ROOT),'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};firefox=server=log=None
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket()as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-alkane-data-',dir='/private/tmp'));log=(OUT/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--width','1800','--height','1400','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,MOZ_HEADLESS_WIDTH='1800',MOZ_HEADLESS_HEIGHT='1400'))
 proc={'base_url':f'http://127.0.0.1:{server.server_port}/','bidi_port':port,'pid':firefox.pid,'profile':str(profile)};(OUT/'process.json').write_text(json.dumps(proc,indent=2)+'\n');(HERE/'process.json').write_text(json.dumps(proc,indent=2)+'\n')
 deadline=time.monotonic()+30
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4):break
  except OSError:
   if firefox.poll()is not None or time.monotonic()>deadline:raise RuntimeError('Owned Firefox BiDi not ready')
   time.sleep(.2)
 env=dict(os.environ,NAMELECULE_DATA_RUN=label,PYTHONUNBUFFERED='1')
 with (OUT/'driver.log').open('w')as driverlog:r=subprocess.run(['python3','-B',str(HERE/('test-'+sys.argv[1]+'.py'))],env=env,stdout=driverlog,stderr=subprocess.STDOUT,timeout=900)
 out['exitCode']=r.returncode
except Exception:out['failure']=traceback.format_exc();out['exitCode']=1
finally:
 if firefox is not None:
  if firefox.poll()is None:
   firefox.terminate()
   try:firefox.wait(timeout=10)
   except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=10)
  out['ownedBrowserExited']=firefox.poll()is not None
 if server is not None:server.shutdown();server.server_close();out['ownedServerClosed']=True
 if log is not None:log.close()
 if 'profile'in locals()and profile.exists():
  assert profile.parent==Path('/private/tmp')and profile.name.startswith('namelecule-alkane-data-')and not profile.is_symlink();shutil.rmtree(profile);out['ownedProfileRemoved']=not profile.exists()
 out['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(OUT/'run.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
sys.exit(out['exitCode'])
