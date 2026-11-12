"""Actual Builder progression; construction actions never scroll test targets."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess, sys, tempfile, threading, time, traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MODE='before' if '--before' in sys.argv else 'after'
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
    OUT['mode']=MODE;OUT['sourceSHA256']=source_hashes
    OUT['conditions']='Actual current production UI and native viewer; genuine trusted mouse drag; no test scrolling/focus inside Builder.'
    viewport(1500,900)
    for embedded in [True,False]:
        if embedded:
            lesson(3,55);open_gate();choose('builder')
        else:
            open_page('games/name-builder.html?molecule=ethane');wait('!!document.querySelector("#bank-tiles button")',65)
        pause(1)
        tid=builder_state(embedded)['bank'][0]
        no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']',embedded)
        before=builder_state(embedded)
        source=_visible_point('#answer-tiles [data-tile-id='+json.dumps(tid)+']',embedded)
        box=_visible_point('#answer-zone',embedded)
        target={'x':round(box['bounds']['left']-12),'y':round((box['bounds']['top']+box['bounds']['bottom'])/2)}
        actions=[{'type':'pointerMove','x':source['x'],'y':source['y'],'duration':0},{'type':'pointerDown','button':0}]
        for step in range(1,10):
            actions.append({'type':'pointerMove','duration':50,'x':round(source['x']+(target['x']-source['x'])*step/9),'y':round(source['y']+(target['y']-source['y'])*step/9)})
        actions.append({'type':'pointerUp','button':0});_pointer_actions(actions);pause(.8)
        after=builder_state(embedded)
        check(after['answer']==before['answer'] and tid not in after['bank'],'Baseline: placed tile released outside answer stays placed',{'embedded':embedded,'source':source,'target':target,'before':before['answer'],'after':after['answer']})
        shot(('lesson'if embedded else'standalone')+'-before.png')
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
