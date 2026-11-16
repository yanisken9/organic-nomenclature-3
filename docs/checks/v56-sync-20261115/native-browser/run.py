"""Start and stop one owned headless browser and loopback candidate server."""
from pathlib import Path
import datetime,hashlib,http.server,json,os,socket,subprocess,sys,tempfile,threading,time,traceback
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
plan=json.loads((HERE.parent/'plan.json').read_text());candidate=Path(os.environ.get('NAMELECULE_NATIVE_SERVE_ROOT',plan['candidate']))
label='run-'+sys.argv[1]+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S')
outdir=HERE/label;outdir.mkdir();firefox=server=log=None
out={'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':label,'candidate':str(candidate),'ownOnly':True}
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(candidate),**kw)
    def log_message(self,*a):pass
try:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    profile=Path(tempfile.mkdtemp(prefix='namelecule-native56-',dir='/private/tmp'))
    log=(outdir/'firefox.log').open('w')
    firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
    proc={'candidateRoot':str(candidate),'base_url':f'http://127.0.0.1:{server.server_port}/','bidi_port':port,'pid':firefox.pid,'profile':str(profile)}
    (HERE/'process.json').write_text(json.dumps(proc,indent=2)+'\n');(outdir/'process.json').write_text(json.dumps(proc,indent=2)+'\n');print(json.dumps(proc),flush=True)
    deadline=time.monotonic()+30
    while True:
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=.4):break
        except OSError:
            if firefox.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned Firefox BiDi not ready')
            time.sleep(.2)
    env=dict(os.environ,NAMELECULE_NATIVE_RUN_LABEL=label,PYTHONUNBUFFERED='1')
    if sys.argv[1]=='raster':
        cmd=['python3','-B',str(HERE/'test-2d-labels56.py'),'--base-url',proc['base_url'],'--bidi-port',str(port),'--output',str(outdir/'raster.json.gz'),'--mode','expanded','--mode','skeletal']
        timeout=1200
    else:
        name={'native':'test-native56.py','primary':'test-primary56.py','bond-diagnostic':'test-visible-bond-diagnostic.py','review':'test-review-corrections56.py','native-extra':'test-native-extra56.py','authoring':'test-authoring.py','minimize':'test-real-minimize.py','minimize55':'test-real-minimize55.py','provisional':'test-provisional-save.py','navigation':'test-navigation-oracles.py'}[sys.argv[1]]
        cmd=['python3','-B',str(HERE/name)];timeout=600
    with (outdir/'driver.log').open('w') as driverlog:
        result=subprocess.run(cmd,env=env,stdout=driverlog,stderr=subprocess.STDOUT,timeout=timeout)
    out['exitCode']=result.returncode
except Exception:
    out['failure']=traceback.format_exc();out['exitCode']=1
finally:
    if firefox is not None:
        if firefox.poll() is None:
            firefox.terminate()
            try:firefox.wait(timeout=10)
            except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=10)
        out['ownedBrowserExited']=firefox.poll() is not None
    if server is not None:server.shutdown();server.server_close();out['ownedServerClosed']=True
    if log is not None:log.close()
    out['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (outdir/'run.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False),flush=True)
sys.exit(out['exitCode'])
