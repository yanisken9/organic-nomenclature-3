"""Actual Builder progression; construction actions never scroll test targets."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess, sys, tempfile, threading, time, traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MODE='layout'
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with socket.socket() as probe:
    probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
profile=Path(tempfile.mkdtemp(prefix='namelecule-builder-placement-'+MODE+'-20261112-'))
(profile/'user.js').write_text('user_pref("ui.prefersReducedMotion", '+('1' if MODE=='reduced' else '0')+');\n')
log=(HERE/('flow-'+MODE+'-firefox.log')).open('w')
firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
process={'serverPID':os.getpid(),'serverScript':str(Path(__file__).resolve()),'firefoxPID':firefox.pid,'profile':str(profile),'bidiPort':port,'baseURL':f'http://127.0.0.1:{server.server_port}/','mode':MODE,'scope':'Only owned temporary headless profile/server; personal browsers untouched.'}
(HERE/'process.json').write_text(json.dumps(process,indent=2)+'\n')
(HERE/('flow-'+MODE+'-process.json')).write_text(json.dumps(process,indent=2)+'\n')
print(json.dumps(process),flush=True)
paths=json.loads((HERE.parent/'baseline.json').read_text())['proposedTarget']
source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
complete=False

try:
    deadline=time.monotonic()+25
    while True:
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=.4): break
        except OSError:
            if firefox.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Owned BiDi endpoint unavailable')
            time.sleep(.2)
    exec(compile((HERE/'helpers.py').read_text(),str(HERE/'helpers.py'),'exec'))
    exec(compile((HERE/'interaction-helpers.py').read_text(),str(HERE/'interaction-helpers.py'),'exec'))
    OUT['mode']=MODE;OUT['sourceSHA256']=source_hashes;OUT['layouts']=[]
    for width,height in [(1500,900),(390,760),(320,740)]:
        viewport(width,height);lesson(3,55)
        if read('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):click('#rotatePromptDismiss')
        open_gate();choose('builder');pause(1)
        _visible_point('#bank-tiles button')
        no_scroll_click('#bank-tiles button');pause(.5)
        data=bread("(() => {const rect=s=>{const e=document.querySelector(s),r=e.getBoundingClientRect(),c=getComputedStyle(e);return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,height:r.height,fontSize:c.fontSize,fontWeight:c.fontWeight}};return {answer:rect('#answer-zone'),bank:rect('#bank-zone'),help:rect('#answer-help'),controls:rect('#tile-controls'),check:rect('#check-answer'),button:rect('#remove-tile'),width:innerWidth,pageWidth:document.documentElement.scrollWidth}})()")
        parent=read("(() => {const f=document.querySelector('.nl-builder-frame').getBoundingClientRect(),h=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect(),d=document.getElementById('nlQuizDialog').getBoundingClientRect();return {frameTop:f.top,headerBottom:h.bottom,dialogBottom:d.bottom}})()")
        data['viewport']=[width,height];data['parent']=parent;OUT['layouts'].append(data)
        shot('layout-'+str(width)+'.png')
        check(data['bank']['top']-data['answer']['bottom']<75,'Layout retains nearby bank '+str(width),data)
        check(data['button']['height']>=44,'Action target44px '+str(width),data['button'])
        check(float(data['button']['fontWeight'])>=700,'Action button bold '+str(width),data['button'])
    OUT['completed']=True;complete=True
except Exception:
    if 'OUT' not in globals():OUT={'checks':[],'solved':[]}
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
    try:shot('flow-'+MODE+'-failure.png')
    except Exception:pass
finally:
    if 'OUT' not in globals():OUT={'checks':[],'solved':[]}
    OUT['javascriptErrors']=globals().get('js_errors',[])
    OUT['sourceUnchangedDuringRun']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in source_hashes.items()}
    (HERE/('flow-'+MODE+'-results.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
    try:
        if 'finish' in globals():finish()
    except Exception as error:OUT['sessionCleanupError']=repr(error)
    server.shutdown();server.server_close()
    if firefox.poll() is None:
        firefox.terminate()
        try:firefox.wait(timeout=10)
        except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
    log.close();process['ownedFirefoxExited']=firefox.poll() is not None;process['ownedServerClosed']=True
    (HERE/('flow-'+MODE+'-cleanup.json')).write_text(json.dumps(process,ensure_ascii=False,indent=2)+'\n')
    (HERE/('flow-'+MODE+'-results.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'completed':complete,'mode':MODE,'checks':len(OUT['checks']),'solved':len(OUT['solved']),'ownedFirefoxExited':process['ownedFirefoxExited']}),flush=True)
if not complete:raise SystemExit(1)
