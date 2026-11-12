"""Read-only application diagnosis; owned headless browser and diagnostic artifacts only."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess
import tempfile, threading, time, traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FREEZE = ROOT / 'docs/checks/builder-methods-guidance-20261112/runtime-source-freeze.json'
manifest = json.loads(FREEZE.read_text())
expected = {**manifest['sourceSHA256'], **manifest['protectedSHA256']}
hashes = lambda: {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in expected}
before = hashes()
assert before == expected, 'Application/protected source differs from reviewed R3'
HTTP_ERRORS = []

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
    def log_message(self, *a): pass
    def send_error(self, code, message=None, explain=None):
        HTTP_ERRORS.append({'code': code, 'path': self.path, 'message': message})
        super().send_error(code, message, explain)

def port_closed(number):
    with socket.socket() as p:
        p.settimeout(.3)
        return p.connect_ex(('127.0.0.1', number)) != 0

server = firefox = log = None
OUT = {'checks': [], 'cases': [], 'startedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'scope': 'Actual current-source embedded lesson step4, read-only observers and trusted pointer gestures. No app, seed or answer-state mutations; no personal/GUI profile access.',
       'contract': 'A placed tile actually released outside answer returns to its exact original bank position.',
       'sourceFreeze': str(FREEZE.relative_to(ROOT)), 'sourceBefore': before}
process = {'diagnosticPID': os.getpid(), 'script': str(Path(__file__).resolve()), 'ownedHeadlessOnly': True}
complete = False

def save():
    (HERE / 'results.json').write_text(json.dumps(OUT, ensure_ascii=False, indent=2) + '\n')

def extra_start():
    return ev('''(() => {
      const game=document.querySelector('.nl-builder-frame').contentWindow, records=[], clean=[];
      for(const [win,label] of [[window,'parent'],[game,'game']]) {
        for(const type of ['blur','focus','pointerdown','pointerup','pointercancel','gotpointercapture','lostpointercapture']) {
          const listener=e=>records.push({window:label,type:e.type,trusted:e.isTrusted,time:e.timeStamp,
            pointerId:e.pointerId??null,pointerType:e.pointerType??null,x:e.clientX??null,y:e.clientY??null,
            targetId:e.target?.closest?.('[data-tile-id]')?.dataset.tileId||null,
            answer:[...game.document.querySelectorAll('#answer-tiles button')].map(e=>e.dataset.tileId),
            ghost:!!game.document.querySelector('.touch-ghost')});
          win.addEventListener(type,listener,true);clean.push(()=>win.removeEventListener(type,listener,true));
        }
      }
      window.__outsideDropObserver={records,stop:()=>clean.forEach(f=>f())};return true;
    })()''')

def extra_stop():
    return read('''(() => {const o=window.__outsideDropObserver;o?.stop();const r=o?.records||[];
      delete window.__outsideDropObserver;return r;})()''')

def restore(tile_id):
    current=builder_state()
    if tile_id not in current['answer']:return
    if current['selected'] != tile_id:
        no_scroll_click('#answer-tiles [data-tile-id='+json.dumps(tile_id)+']')
    no_scroll_click('#remove-tile')

try:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    profile=Path(tempfile.mkdtemp(prefix='namelecule-outside-drop-preflight-20261112-'))
    log=(HERE/'firefox.log').open('w')
    firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote',
        '--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
    process.update({'serverPID':os.getpid(),'serverPort':server.server_port,'firefoxPID':firefox.pid,
        'profile':str(profile),'bidiPort':port,'baseURL':f'http://127.0.0.1:{server.server_port}/',
        'helperOrigins':'Unmodified copies of builder-placement-controls-20261112/browser/{helpers,interaction-helpers,gesture-helpers,driver}.py'})
    (HERE/'process.json').write_text(json.dumps(process,indent=2)+'\n')
    print(json.dumps(process),flush=True)
    deadline=time.monotonic()+25
    while True:
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=.4):break
        except OSError:
            if firefox.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned BiDi endpoint unavailable')
            time.sleep(.2)
    # Helpers are definitions/transport only; page instrumentation observes messages/events.
    exec(compile((HERE/'helpers.py').read_text(),str(HERE/'helpers.py'),'exec'))
    exec(compile((HERE/'interaction-helpers.py').read_text(),str(HERE/'interaction-helpers.py'),'exec'))
    exec(compile((HERE/'gesture-helpers.py').read_text(),str(HERE/'gesture-helpers.py'),'exec'))
    # helpers supplies OUT; restore the diagnostic outcome container explicitly.
    OUT.update({'cases':[],'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'scope':'Read-only current-source embedded step4; trusted pointer gestures, transient observers.',
       'contract':'A placed tile actually released outside answer returns to exact original bank position.',
       'sourceFreeze':str(FREEZE.relative_to(ROOT)),'sourceBefore':before})
    viewport(1280,600)
    lesson(3,55)
    if read('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):
        no_scroll_click('#rotatePromptDismiss',False)
    open_gate();choose('builder');pause(1)
    OUT['servedCacheToken']=read('[...document.querySelector(".nl-builder-frame").contentDocument.scripts].map(e=>e.src).find(s=>s.includes("namelecule-name-builder.js"))')
    OUT['genuineLoad']=bread('__lessonLoad')
    original_bank=builder_state()['bank'][:]
    tile_id=original_bank[0]
    OUT['originalBankIDs']=original_bank
    OUT['diagnosticTileID']=tile_id
    for width,height in [(1280,600),(1500,900)]:
        viewport(width,height);pause(.8)
        for endpoint in ['bank','bottom','molecule','parent-header']:
            label=f'embedded-{width}x{height}-{endpoint}'
            check(builder_state()['answer']==[],label+' starts with empty answer')
            check(builder_state()['bank']==original_bank,label+' starts with exact original bank order')
            no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tile_id)+']')
            case={'label':label,'viewport':[width,height],'endpoint':endpoint,'before':builder_state()}
            try:
                if endpoint=='parent-header':
                    target=read('''(() => {const r=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect();
                      return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()''')
                    case['targetProbe']=gesture_global_point(target['x'],target['y'])
                else:
                    target=None
                    # Record inability to reach a molecule that user construction framing has scrolled away.
                    case['targetProbe']=_gesture_target(endpoint)
                extra_start()
                result=gesture_drag(tile_id,'global' if endpoint=='parent-header' else endpoint,
                    global_point=target)
                case.update({'gesture':result,'eventsWithBlur':extra_stop(),'after':builder_state()})
                case['returnedToExactOriginalBankOrder']=case['after']['answer']==[] and case['after']['bank']==original_bank
                case['contractPassed']=case['returnedToExactOriginalBankOrder']
                case['status']='pass' if case['contractPassed'] else 'contract-failure'
                shot(label+('.png' if case['contractPassed'] else '-failure.png'))
                terminal=[e for e in result['events'] if e['type'] in ['pointerup','pointercancel','lostpointercapture']]
                print(json.dumps({'case':label,'status':case['status'],'release':result['release'],
                    'answerAfter':case['after']['answer'],'terminal':terminal}),flush=True)
            except Exception:
                case['status']='diagnostic-error-or-unreachable'
                case['diagnosticError']=traceback.format_exc()
                try:case['eventsWithBlur']=extra_stop()
                except Exception:pass
                print(json.dumps({'case':label,'status':case['status'],'error':case['diagnosticError']}),flush=True)
            finally:
                OUT['cases'].append(case);save()
                restore(tile_id)
                check(builder_state()['answer']==[] and builder_state()['bank']==original_bank,
                    label+' actual remove/control cleanup restores exact original order')
    OUT['completed']=True;complete=True
except Exception:
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
    try:shot('preflight-diagnostic-failure.png')
    except Exception:pass
finally:
    OUT['javascriptErrors']=globals().get('js_errors',[])
    OUT['httpErrors']=HTTP_ERRORS
    OUT['sourceAfter']=hashes()
    OUT['all7SourceAnd15ProtectedUnchanged']=OUT['sourceAfter']==expected==before
    try:
        if 'finish' in globals():finish()
    except Exception as error:OUT['sessionCleanupError']=repr(error)
    if server is not None:
        server.shutdown();server.server_close()
    if firefox is not None and firefox.poll() is None:
        firefox.terminate()
        try:firefox.wait(timeout=10)
        except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
    if log is not None:log.close()
    process.update({'ownedFirefoxExited':firefox is None or firefox.poll() is not None,
        'ownedServerClosed':server is None or port_closed(process['serverPort']),
        'ownedBidiClosed':'bidiPort' not in process or port_closed(process['bidiPort']),
        'cleanupUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    (HERE/'cleanup.json').write_text(json.dumps(process,indent=2)+'\n')
    save()
    print(json.dumps({'complete':complete,'cases':len(OUT.get('cases',[])),
        'contractFailures':[c['label'] for c in OUT.get('cases',[]) if c.get('contractPassed') is False],
        'sourceUnchanged':OUT['all7SourceAnd15ProtectedUnchanged'],'cleanup':process}),flush=True)
if not complete:raise SystemExit(1)
