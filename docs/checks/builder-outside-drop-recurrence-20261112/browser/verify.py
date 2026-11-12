"""Bounded approved-fix verification; one owned headless browser, trusted inputs."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess
import tempfile, threading, time, traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FREEZE = HERE.parent / 'runtime-source-freeze.json'
manifest = json.loads(FREEZE.read_text())
expected = {**manifest['sourceSHA256'], **manifest['protectedSHA256']}
hashes = lambda: {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in expected}
before = hashes()
assert before == expected, 'Application/protected source differs from approved AFTER freeze'
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

def restore(tile_id,embedded=True):
    current=builder_state(embedded)
    if tile_id not in current['answer']:return
    if current['selected'] != tile_id:
        no_scroll_click('#answer-tiles [data-tile-id='+json.dumps(tile_id)+']',embedded)
    no_scroll_click('#remove-tile',embedded)

def clear(embedded=True):
    for tid in builder_state(embedded)['answer'][:]:restore(tid,embedded)

def record_gesture(label,*args,**kwargs):
    result=gesture_drag(*args,**kwargs)
    OUT.setdefault('additionalGestures',[]).append({'label':label,**result})
    print(json.dumps({'case':label,'status':'pass','actualDistance':result['actualDistance'],
      'release':result['release'],'answerAfter':result['after']['answer']}),flush=True)
    return result

def guard(kind,tile_id):
    """Real trusted drag activation, explicitly synthetic/induced termination."""
    no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tile_id)+']')
    original=builder_state()
    source=_visible_point('#answer-tiles [data-tile-id='+json.dumps(tile_id)+']')
    target=_gesture_target('bottom')['global']
    _gesture_observe_start();extra_start()
    _pointer_actions([{'type':'pointerMove','x':source['x'],'y':source['y'],'duration':0},
        {'type':'pointerDown','button':0},{'type':'pointerMove','x':target['x'],'y':target['y'],'duration':250}])
    check(bread('!!document.querySelector(".touch-ghost")'),kind+' real trusted drag activated before induced guard')
    if kind=='synthetic-pointercancel':
        bread('''(() => {const e=__nameleculeGestureEvidence.records.find(e=>e.type==='pointerdown'&&e.trusted);
          const b=document.querySelector('#answer-tiles [data-tile-id='+CSS.escape(e.targetId)+']');
          b.dispatchEvent(new PointerEvent('pointercancel',{pointerId:e.pointerId,pointerType:e.pointerType,bubbles:true}));return true;})()''')
    elif kind=='programmatic-capture-release':
        bread('''(() => {const e=__nameleculeGestureEvidence.records.find(e=>e.type==='pointerdown'&&e.trusted);
          const b=document.querySelector('#answer-tiles [data-tile-id='+CSS.escape(e.targetId)+']');
          b.releasePointerCapture(e.pointerId);return true;})()''')
        _pointer_actions([{'type':'pointerMove','x':target['x'],'y':target['y'],'duration':60}])
    elif kind=='synthetic-window-blur':
        bread('window.dispatchEvent(new Event("blur"));true')
    else:raise ValueError(kind)
    pause(.2)
    check(not bread('!!document.querySelector(".touch-ghost")'),kind+' cancellation cleaned ghost before release')
    _pointer_actions([{'type':'pointerUp','button':0}]);pause(.7)
    events=_gesture_observe_stop();extra=extra_stop();after=builder_state()
    check(after['answer']==original['answer'] and after['bank']==original['bank'],kind+' preserves exact answer and bank order')
    OUT.setdefault('guardChecks',[]).append({'kind':kind,'nativeDeviceCancellationClaim':False,
      'before':original,'after':after,'events':events,'eventsWithBlur':extra,
      'limitation':'Guard induced by synthetic dispatch or DOM capture API after genuine trusted drag; not native hardware/OS cancellation proof.'})
    restore(tile_id)

def fresh_context():
    global ctx
    old=ctx;ctx=call('browsingContext.create',{'type':'tab'})['context']
    call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
    call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'''() => {
      window.__builderEvents=[];addEventListener('message',event=>{
        if(event.data?.channel==='namelecule-name-builder-v1')window.__builderEvents.push(event.data);});}'''})
    call('browsingContext.close',{'context':old})

def header_point():
    return read('''(() => {const r=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect();
      return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()''')

def compact_extensions(original_bank,tile_id):
    ids=original_bank[:3]
    for tid in ids:no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
    record_gesture('desktop-inside-reorder',ids[0],'inside',answer_index=3,expected_order=ids[1:]+ids[:1])
    record_gesture('desktop-exit-reenter-answer',ids[0],'reentry',answer_index=0,expected_order=ids)
    clear()
    record_gesture('desktop-bank-origin-header-no-op',tile_id,'global',origin='bank',global_point=header_point(),expected_order=[])
    check(builder_state()['bank']==original_bank,'bank-origin header no-op preserves exact original bank order')
    no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tile_id)+']');no_scroll_click('#check-answer')
    check(not builder_state()['feedback']['hidden'] and not builder_state()['feedback']['success'],'partial wrong answer produced genuine wrong feedback')
    record_gesture('desktop-wrong-feedback-header-correction',tile_id,'global',global_point=header_point(),expected_order=[])
    check(builder_state()['feedback']['hidden'] and builder_state()['bank']==original_bank,'header removal clears wrong feedback and restores original bank order')
    for kind in ['synthetic-pointercancel','programmatic-capture-release','synthetic-window-blur']:guard(kind,tile_id)
    genuine=correct_tile_ids()
    for tid in genuine[:2]:no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
    partial=builder_state();progress=rec();load=partial['load']
    call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();builder_ready();pause(.8)
    restored=builder_state();restored_progress=rec()
    check(restored['answer']==partial['answer'] and restored['bank']==partial['bank'],'actual parent reload preserves exact partial answer and bank order')
    check(restored['load']['round']==load['round'] and restored['load']['bankSeed']==load['bankSeed'],'actual parent reload preserves genuine round and seeded bank')
    check(progress['states']['3']['earned']==restored_progress['states']['3']['earned'],'partial reload preserves earned count')
    OUT['partialRefresh']={'before':partial,'after':restored,'progressBefore':progress,'progressAfter':restored_progress}
    for tid in genuine[2:]:no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
    check(builder_state()['candidate']==load['round']['correctName'],'genuine seeded correct IDs form exact canonical name')
    no_scroll_click('#check-answer');wait('!!document.querySelector(".round-next button")');pause(.8)
    solved=builder_state()
    check(solved['feedback']['success'],'one genuine correct response accepted by real Builder')
    lock=bread('''({tiles:[...document.querySelectorAll('.tile-button')].map(e=>({id:e.dataset.tileId,disabled:e.disabled})),
      controlsHidden:document.getElementById('tile-controls').hidden,check:document.getElementById('check-answer').disabled,
      before:document.getElementById('move-before').disabled,after:document.getElementById('move-after').disabled})''')
    check(all(t['disabled'] for t in lock['tiles']) and all(lock[k] for k in ['controlsHidden','check','before','after']),'solved answer locks every tile, hides editing controls and disables Check')
    # A real pointerdown/up on the disabled solved tile cannot alter the answer.
    source=_gesture_probe(selector='#answer-tiles [data-tile-id='+json.dumps(genuine[0])+']')
    _pointer_actions([{'type':'pointerMove',**source['global'],'duration':0},{'type':'pointerDown','button':0},
      {'type':'pointerMove','x':source['global']['x']+30,'y':source['global']['y'],'duration':150},{'type':'pointerUp','button':0}]);pause(.3)
    check(builder_state()['answer']==solved['answer'] and not bread('!!document.querySelector(".touch-ghost")'),'trusted solved-tile gesture preserves locked answer')
    OUT['solvedResponse']={'state':solved,'lock':lock,'progress':rec()};shot('desktop-one-genuine-solved.png')
    # Phone case uses genuine fresh lesson state, not edited storage or synthetic loads.
    fresh_context();viewport(390,760);lesson(3,55)
    if read('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):
        no_scroll_click('#rotatePromptDismiss',False)
    open_gate();choose('builder');pause(.8)
    phone_bank=builder_state()['bank'][:];tid=phone_bank[0]
    no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
    record_gesture('phone390-parent-header-return',tid,'global',global_point=header_point(),expected_order=[])
    check(builder_state()['bank']==phone_bank,'phone390 header release restores exact original bank order')
    no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
    record_gesture('phone390-visible-bank-return',tid,'bank',expected_order=[])
    check(builder_state()['bank']==phone_bank,'phone390 visible bank release restores exact original bank order');shot('phone390-bank-return.png')
    # Shared standalone entry; actual native viewer and actual bank.
    fresh_context();viewport(1280,600);open_page('games/name-builder.html?molecule=ethane')
    wait('!!document.querySelector("#bank-tiles button")',65);pause(.8)
    standalone_bank=builder_state(False)['bank'][:];tid=standalone_bank[0]
    no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']',False)
    record_gesture('standalone-visible-bottom-return',tid,'bottom',embedded=False,expected_order=[])
    check(builder_state(False)['bank']==standalone_bank,'standalone removal restores exact original bank order')
    record_gesture('standalone-bank-origin-outside-no-op',tid,'bottom',embedded=False,origin='bank',expected_order=[])
    check(builder_state(False)['bank']==standalone_bank,'standalone bank-origin outside no-op preserves original order');shot('standalone-return.png')

try:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    profile=Path(tempfile.mkdtemp(prefix='namelecule-outside-drop-after-20261112-'))
    log=(HERE/'firefox.log').open('w')
    firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote',
        '--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
    process.update({'serverPID':os.getpid(),'serverPort':server.server_port,'firefoxPID':firefox.pid,
        'profile':str(profile),'bidiPort':port,'baseURL':f'http://127.0.0.1:{server.server_port}/',
        'helperOrigins':'Copies of builder-placement-controls-20261112/browser helpers; gesture oracle adapted to approved topviewport+visibleanswer contract.'})
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
    compact_extensions(original_bank,tile_id)
    OUT['completed']=True;complete=all(c.get('contractPassed') for c in OUT['cases'])
except Exception:
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
    try:shot('preflight-diagnostic-failure.png')
    except Exception:pass
finally:
    OUT['javascriptErrors']=globals().get('js_errors',[])
    OUT['httpErrors']=HTTP_ERRORS
    OUT['sourceAfter']=hashes()
    OUT['allSourceAndProtectedUnchanged']=OUT['sourceAfter']==expected==before
    OUT['sourceCount']=len(manifest['sourceSHA256']);OUT['protectedCount']=len(manifest['protectedSHA256'])
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
        'sourceUnchanged':OUT['allSourceAndProtectedUnchanged'],'cleanup':process}),flush=True)
if not complete:raise SystemExit(1)
