"""Actual Builder progression; construction actions never scroll test targets."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess, sys, tempfile, threading, time, traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MODE='reduced' if '--reduced' in sys.argv else ('remaining' if '--mobile' in sys.argv else ('interrupt' if '--interrupt' in sys.argv else 'normal'))
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

def install_scroll_trace():
    ev('''(() => {const d=document.getElementById('nlQuizDialog'),original=d.scrollTo;
      window.__workspaceScroll=[];
      d.scrollTo=function(options){__workspaceScroll.push({top:options.top,behavior:options.behavior,at:performance.now()});return original.apply(this,arguments)};
      return true})()''')

def entry(label):
    builder_ready();pause(1)
    data=bread('''(() => {const a=document.getElementById('answer-zone').getBoundingClientRect(),b=document.getElementById('bank-zone').getBoundingClientRect();
      return {gap:b.top-a.bottom,answerCount:document.querySelectorAll('#answer-tiles button').length,bankCount:document.querySelectorAll('#bank-tiles button').length,
        width:innerWidth,pageWidth:document.documentElement.scrollWidth,frameHeight:innerHeight}})()''')
    check(0<data['gap']<75,label+' compact answer/bank gap',data)
    check(data['pageWidth']<=data['width'],label+' no page horizontal overflow',data)
    for selector in ['#answer-zone','#bank-tiles li:first-child button','#bank-tiles li:last-child button']:
        point=_visible_point(selector)
        check(point['fullyVisible'],label+' interaction region fully visible '+selector,point)
    OUT.setdefault('geometry',[]).append({'label':label,'data':data,'dialogScrollTop':read('document.getElementById("nlQuizDialog").scrollTop')})
    return data

def complete_builder(label):
    entry(label)
    round_data=bread('__lessonLoad.round');ids=correct_tile_ids()
    for tid in ids:
        if tid not in builder_state()['answer']:
            no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
    check(builder_state()['candidate']==round_data['correctName'],label+' exact composed name')
    no_scroll_click('#check-answer')
    wait('!!document.querySelector(".round-next button")')
    state=builder_state()
    check(state['feedback']['success'],label+' correct answer earned')
    check(_visible_point('#feedback')['fullyVisible'],label+' success explanation visible')
    _visible_point('.round-next button',False)
    OUT['solved'].append({'label':label,'moleculeId':round_data['moleculeId'],'name':round_data['correctName']})
    print('SOLVED '+label+' '+round_data['moleculeId'],flush=True)
    return ids

def dismiss_orientation():
    if read('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):
        no_scroll_click('#rotatePromptDismiss',False)
        check(read('getComputedStyle(document.getElementById("rotatePrompt")).display')=='none','Existing portrait prompt dismissed by trusted user action')

def interrupt_active_motion(embedded):
    ev('''(() => {window.__keyEvents=[];window.__interruptMessages=[];
      addEventListener('keydown',e=>__keyEvents.push({key:e.key,trusted:e.isTrusted,id:e.target.id,at:Date.now()}),true);
      addEventListener('message',e=>{if(e.data?.channel==='namelecule-builder-lesson-v1')__interruptMessages.push({type:e.data.type,purpose:e.data.purpose,at:Date.now()})});return true})()''')
    if embedded:
        bread('''(() => {window.__keyEvents=[];addEventListener('keydown',e=>__keyEvents.push({key:e.key,trusted:e.isTrusted,id:e.target.id,at:Date.now()}),true);return true})()''')
    else:
        ev('''(() => {window.__workspaceScroll=[];const original=window.scrollTo;window.scrollTo=function(options){__workspaceScroll.push({top:options.top,behavior:options.behavior,at:performance.now()});return original.apply(this,arguments)};return true})()''')
    no_scroll_click('#bank-tiles li:first-child button',embedded)
    point=_visible_point('#check-answer',embedded)
    _pointer_actions([{'type':'pointerMove','x':point['x'],'y':point['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}])
    top=lambda:read('document.getElementById("nlQuizDialog").scrollTop' if embedded else 'scrollY')
    pause(.065);a=top();pause(.035);b=top()
    check(abs(b-a)>1,'Actual smooth motion observed before user interruption',{'embedded':embedded,'a':a,'b':b})
    focus=_builder_read('({id:document.activeElement?.id,tag:document.activeElement?.tagName,hasFocus:document.hasFocus()})',embedded)
    call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'interrupt-shift','actions':[{'type':'keyDown','value':'\ue008'},{'type':'keyUp','value':'\ue008'}]}]})
    pause(.04);stopped=top();pause(.45);later=top()
    empty=_builder_read('''(() => {const probe=document.createElement('div');probe.className='bank-zone';probe.style.cssText='position:absolute;left:-10000px;top:0;width:300px';document.body.append(probe);const h=probe.getBoundingClientRect().height;probe.remove();return {diagnosticEmptyBankHeight:h}})()''',embedded)
    detail={'embedded':embedded,'a':a,'b':b,'stopped':stopped,'later':later,'focusBeforeKey':focus,
      'rootKeys':read('__keyEvents'),'childKeys':bread('__keyEvents') if embedded else None,
      'messages':read('__interruptMessages'),'scrollCommands':read('__workspaceScroll'),'emptyBankCSSProbe':empty,
      'stoppedWithinTolerance':abs(later-stopped)<=1}
    OUT.setdefault('actualInterruptions',[]).append(detail)
    return detail['stoppedWithinTolerance']

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
    exec(compile((HERE/'gesture-helpers.py').read_text(),str(HERE/'gesture-helpers.py'),'exec'))
    exec(compile((HERE/'matrix.py').read_text(),str(HERE/'matrix.py'),'exec'))
    OUT['mode']=MODE;OUT['sourceSHA256']=source_hashes
    OUT['conditions']='Actual production UI/native viewer and canonical chemistry. Builder actions use trusted input with NO test scrolling/focus. Navigation/game selection and unchanged Workshop smoke use existing setup helpers.'
    viewport(390,760) if MODE=='remaining' else viewport(1500,900)
    lesson(3,55);dismiss_orientation();open_gate();install_scroll_trace();choose('builder')
    if MODE=='remaining':
        # Reproduce the actual failed order using only a recorded seed and empty
        # progress; all questions/answers are still created/checked by the engine.
        ev("(() => {const content=JSON.stringify({version:1,title:String(fScenarioPresent().title||''),author:String(fScenarioPresent().author||'Unknown'),steps:fScenarioPresent().steps});const item=Object.entries(sessionStorage).find(([k,v])=>{try{return JSON.parse(v)?.content===content}catch(_){return false}});if(!item)throw Error('No actual checkpoint record');const record=JSON.parse(item[1]);const game=record.states['3'].games.builder;game.seed='33755852321139648068';game.currentRound=0;game.states=[null,null,null];game.solved=false;sessionStorage.setItem(item[0],JSON.stringify(record));return true})()")
        call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();dismiss_orientation();open_gate();install_scroll_trace();builder_ready()
        check(bread('__lessonLoad.attemptId').endswith('33755852321139648068'),'Recorded real failed-sequence seed restored with empty progress')

    check(bread('matchMedia("(prefers-reduced-motion: reduce)").matches')==(MODE=='reduced'),'Actual disposable-profile motion preference')
    entry('initial-'+MODE)
    trace=read('__workspaceScroll');OUT['initialScrollTrace']=trace
    check(any(e['behavior']==('instant' if MODE=='reduced' else 'smooth') for e in trace),'Entry uses expected motion behavior',trace)
    if MODE=='reduced':
        no_scroll_click('#bank-tiles li:first-child button')
        no_scroll_click('#check-answer')
        check(not builder_state()['feedback']['hidden'],'Reduced wrong feedback shown')
        check(_visible_point('#feedback')['fullyVisible'],'Reduced feedback framed')
        check(not any(e['behavior']=='smooth' for e in read('__workspaceScroll')),'No smooth commands in reduced-motion flow')
        before=builder_state()
        for form in ['expanded','3d','condensed']:
            no_scroll_click('[data-representation='+json.dumps(form)+']')
            wait(bel('[data-representation='+json.dumps(form)+']')+'.getAttribute("aria-pressed")==="true"',55)
            check(builder_state()['answer']==before['answer'],'Partial answer preserved on '+form)
        heights=[]
        for _ in range(4):
            heights.append(read('document.querySelector(".nl-builder-frame").getBoundingClientRect().height'));pause(.2)
        check(max(heights)-min(heights)<=1,'Iframe height settles without a sizing loop',heights)
        shot('reduced-feedback.png')
        tid=builder_state()['answer'][0]
        no_scroll_click('#answer-tiles [data-tile-id='+json.dumps(tid)+']')
        if builder_state()['selected'] is None:no_scroll_click('#answer-tiles [data-tile-id='+json.dumps(tid)+']')
        key_selected('Delete')
        complete_builder('reduced-correct-round1')
        check(bread('getComputedStyle(document.querySelector(".keyboard-note")).display')=='none','Reduced correct answer hides editing-only footer')
        no_scroll_click('.round-next button',False);entry('reduced-next-round')
        check(bread('getComputedStyle(document.querySelector(".keyboard-note")).display')!='none','Reduced next round restores editing instructions')
        check(not any(e['behavior']=='smooth'for e in read('__workspaceScroll')),'Reduced completion and next round never animate scroll')

    elif MODE=='interrupt':
        first=interrupt_active_motion(True)
        open_page('games/name-builder.html?molecule=ethane')
        wait('!!document.querySelector("#bank-tiles button")',65);pause(1)
        second=interrupt_active_motion(False)
        check(first and second,'Event-traced user interruption stops embedded and standalone motion',OUT['actualInterruptions'])
        # Empty the bank through actual UI, then drag a tile back into it.
        for tid in builder_state(False)['bank']:
            no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']',False)
        empty=builder_state(False)
        check(not empty['bank'],'Bank genuinely empty after trusted additions')
        height=read('document.getElementById("bank-zone").getBoundingClientRect().height')
        check(height>=64,'Empty bank retains usable drag-return area',height)
        tid=empty['selected']
        start=_visible_point('#answer-tiles [data-tile-id='+json.dumps(tid)+']',False)
        end=_visible_point('#bank-zone',False)
        actions=[{'type':'pointerMove','x':start['x'],'y':start['y'],'duration':0},{'type':'pointerDown','button':0}]
        for step in range(1,10):
            actions.append({'type':'pointerMove','x':round(start['x']+(end['x']-start['x'])*step/9),'y':round(start['y']+(end['y']-start['y'])*step/9),'duration':65})
        actions.append({'type':'pointerUp','button':0});_pointer_actions(actions);pause(.7)
        returned=builder_state(False)
        check(tid in returned['bank'] and tid not in returned['answer'],'Actual drag returns tile to previously empty bank')
        open_page('games/name-builder.html?molecule=ethane')
        wait('!!document.querySelector("#bank-tiles button")',65);pause(1)
        native=read('__builderEvents.findLast(e=>e.type==="round")')
        bank=read('NameleculeNameBuilderEngine.createBank(__builderEvents.findLast(e=>e.type==="round"),{seed:__builderEvents.findLast(e=>e.type==="round").roundId})')
        used=set()
        for piece in native['pieces']:
            tile=next(t for t in bank if t['id'] not in used and t['text']==piece['text'] and t['separatorBefore']==piece['separatorBefore']);used.add(tile['id'])
            no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tile['id'])+']',False)
        no_scroll_click('#check-answer',False)
        check(builder_state(False)['feedback']['success'],'R2 genuine standalone round completes after corrected takeover')
        check(_visible_point('#feedback',False)['fullyVisible'],'R2 correct feedback revealed')
        OUT['solved'].append({'label':'R2-standalone','moleculeId':native['moleculeId'],'name':native['correctName']})
    elif MODE=='remaining':
        tid=builder_state()['bank'][0];no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
        gesture_drag(tid,'bottom')
        complete_builder('phone390-round1');no_scroll_click('.round-next button',False);entry('phone390-next-round')
        shot('phone390-next.png')
        viewport(320,740)
        call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();dismiss_orientation();open_gate();builder_ready();entry('phone320-restored-round')
        check(read('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 2/3','Phone refresh retains current round')
        tid=builder_state()['bank'][0];no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
        shot('phone320-controls.png');_visible_point('#remove-tile');_visible_point('#check-answer')
        gesture_drag(tid,'bottom',pointer_type='touch')
        complete_builder('phone320-round2')
        check(bread('__lessonLoad.moleculeId')=='methane','Exact previously failing methane success reproduced')
        note=bread("(() => {const n=document.querySelector('.keyboard-note'),display=getComputedStyle(n).display;const before=n.getBoundingClientRect().height;n.style.display='block';const counterfactual=n.getBoundingClientRect().height;n.style.removeProperty('display');return{display,actualHeight:before,counterfactualHeight:counterfactual}})()")
        check(note['display']=='none' and note['actualHeight']==0 and note['counterfactualHeight']>0,'Completed edit-note gap removed at its source',note)
        OUT['footerCauseMeasurement']=note
        no_scroll_click('.round-next button',False);builder_ready();pause(1)
        check(bread('getComputedStyle(document.querySelector(".keyboard-note")).display')!='none','Next editable lesson round restores keyboard instructions')

        check(not read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Two completed rounds do not unlock gate early')
        viewport(1024,768);lesson(3,54);dismiss_orientation();open_gate();choose('builder');entry('Main54-entry')
        check(bread('document.getElementById("answer-help").textContent.toLocaleLowerCase("el").includes("σύρε")'),'Main54 new guidance loaded')
        viewport(1500,1000)
        open_page('games/name-builder.html?molecule=ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid')
        wait('!!document.querySelector("#bank-tiles button")',65);pause(1)
        native=read('__builderEvents.findLast(e=>e.type==="round")')
        bank=read('NameleculeNameBuilderEngine.createBank(__builderEvents.findLast(e=>e.type==="round"),{seed:__builderEvents.findLast(e=>e.type==="round").roundId})')
        used=set();ids=[]
        for piece in native['pieces']:
            tile=next(t for t in bank if t['id']not in used and t['text']==piece['text']and t['separatorBefore']==piece['separatorBefore']);used.add(tile['id']);ids.append(tile['id'])
            no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tile['id'])+']',False)
        check(builder_state(False)['answerScrollLeft']>0,'Long answer genuinely horizontally scrolled before outside drag')
        result=gesture_drag(ids[-1],'left',False,expected_order=ids[:-1]);result['case']='long horizontally-scrolled answer outside-left';OUT.setdefault('gestureMatrix',[]).append(result)
        no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(ids[-1])+']',False)
        check(builder_state(False)['candidate']==native['correctName'],'Returned long-name tile reusable with exact composition')
        before=builder_state(False);source=_visible_point('#answer-tiles [data-tile-id='+json.dumps(ids[-1])+']',False);target=_gesture_target('bottom',False)
        _gesture_observe_start(False)
        _pointer_actions([{'type':'pointerMove','x':source['x'],'y':source['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerMove','x':target['global']['x'],'y':target['global']['y'],'duration':250}])
        check(read('!!document.querySelector(".touch-ghost")'),'Real active long-name drag before native capture loss')
        read("(() => {const e=__nameleculeGestureEvidence.records.find(e=>e.type==='pointerdown'&&e.trusted);const b=document.querySelector('#answer-tiles [data-tile-id='+CSS.escape(e.targetId)+']');b.releasePointerCapture(e.pointerId);return true})()")
        _pointer_actions([{'type':'pointerMove','x':target['global']['x']+1,'y':target['global']['y'],'duration':80},{'type':'pointerUp','button':0}]);pause(.7)
        events=_gesture_observe_stop(False)
        check(any(e['type']=='lostpointercapture'and e['trusted']for e in events),'Native trusted lostpointercapture observed after diagnostic API release',events)
        check(builder_state(False)['answer']==before['answer']and not read('!!document.querySelector(".touch-ghost")'),'Native capture-loss cancellation preserves long-name answer')
        OUT['nativeCaptureLoss']={'initiator':'diagnostic releasePointerCapture API after trusted drag','events':events}
        no_scroll_click('#check-answer',False)
        check(builder_state(False)['feedback']['success'],'Long native answer still validates after drag/remove/capture loss')
        shot('long-drag-success.png')
        check(read('getComputedStyle(document.querySelector(".keyboard-note")).display')=='none','Standalone correct answer also hides inactive editing footer')
        no_scroll_click('#next-molecule',False);wait('!!document.querySelector("#bank-tiles button")&&!document.getElementById("next-molecule").disabled',65);pause(.7)
        check(read('getComputedStyle(document.querySelector(".keyboard-note")).display')!='none','Standalone next molecule restores editing footer despite retained hidden success class')



    else:
        viewport(1500,1000);run_gesture_matrix(True);viewport(1500,900);entry('post-gesture-matrix')
        ids=correct_tile_ids();drag_tile(ids[0])
        OUT['trustedChildInterruptTrace']=read('__workspaceScroll')
        check(any(e['behavior']=='instant' for e in OUT['trustedChildInterruptTrace']),'Trusted iframe drag interrupts parent response scroll',OUT['trustedChildInterruptTrace'])
        no_scroll_click('#check-answer')
        check(not builder_state()['feedback']['hidden'] and not builder_state()['feedback']['success'],'Partial answer is incorrect')
        check(_visible_point('#feedback')['fullyVisible'],'Wrong feedback visible without manual scrolling')
        no_scroll_click('#answer-tiles button')
        # The first click toggles the already-selected tile off; a second selects it.
        if builder_state()['selected'] is None: no_scroll_click('#answer-tiles button')
        key_selected('Delete');key_add_focused()
        no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(ids[1])+']')
        key_selected('ArrowLeft');key_selected('ArrowRight')
        before=builder_state()
        call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();builder_ready();pause(1)
        after=builder_state()
        check(after['answer']==before['answer'] and after['selected']==before['selected'],'Partial refresh preserves exact tile answer/selection')
        check(not read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'First gate remains locked after partial answer')
        complete_builder('gate4-round1');no_scroll_click('.round-next button',False)
        complete_builder('gate4-round2');no_scroll_click('.round-next button',False)
        complete_builder('gate4-round3');footer('gate4 final')
        check(read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Three genuine Builder rounds unlock first gate')
        shot('gate4-earned.png')
        earned=rec()['states']['3']
        no_scroll_click('.round-next button:nth-child(2)',False);entry('optional-new-triple')
        check(rec()['states']['3']==earned,'Optional new triple preserves earned required evidence')
        no_scroll_click('#nlQuizPracticeContinue',False)
        check(not read('document.getElementById("nlQuizDialog").open'),'Optional return closes quiz')
        lesson(10,55);open_gate();choose('builder')
        for index in range(3):
            complete_builder('gate11-round'+str(index+1))
            if index<2:no_scroll_click('.round-next button',False)
        footer('gate11 final')
        check(read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Three genuine branched Builder rounds unlock second gate')
        shot('gate11-earned.png')
        no_scroll_click('.round-next button',False)
        wait('fScenarioPresent().index===11')
        check(read('fScenarioPresent().index')==11,'Continue reaches final molecule exploration')
        open_page('games/name-builder.html?molecule=ethane')
        wait('!!document.querySelector("#bank-tiles button")',65);pause(1)
        viewport(1500,1000);run_gesture_matrix(False);viewport(1500,900)
        # Standalone long name exercises the compact bank and preserved one-line answer.
        viewport(1500,900)
        open_page('games/name-builder.html?molecule=ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid')
        wait('!!document.querySelector("#bank-tiles button")',65);pause(1)
        native=read('__builderEvents.findLast(e=>e.type==="round")')
        bank=read('NameleculeNameBuilderEngine.createBank(__builderEvents.findLast(e=>e.type==="round"),{seed:__builderEvents.findLast(e=>e.type==="round").roundId})')
        used=set()
        for piece in native['pieces']:
            tile=next(t for t in bank if t['id'] not in used and t['text']==piece['text'] and t['separatorBefore']==piece['separatorBefore']);used.add(tile['id'])
            no_scroll_click('#bank-tiles [data-tile-id='+json.dumps(tile['id'])+']',False)
        check(builder_state(False)['candidate']==native['correctName'],'Longest standalone composed name remains exact')
        single=read('''(() => {const row=document.getElementById('answer-tiles'),n=document.getElementById('candidate-name');const r=document.createRange();r.selectNodeContents(n);return {rows:new Set([...row.querySelectorAll('button')].map(e=>Math.round(e.getBoundingClientRect().top))).size,lines:new Set([...r.getClientRects()].map(x=>Math.round(x.top))).size,page:document.documentElement.scrollWidth,width:innerWidth}})()''')
        check(single['rows']==1 and single['lines']==1 and single['page']<=single['width'],'Long name retains one-line containment',single)
        no_scroll_click('#check-answer',False)
        check(builder_state(False)['feedback']['success'],'Longest standalone genuine check correct')
        check(_visible_point('#feedback',False)['fullyVisible'],'Standalone success automatically revealed')
        shot('standalone-long-success.png')
        no_scroll_click('#next-molecule',False)
        wait('!!document.querySelector("#bank-tiles button")&&!document.getElementById("next-molecule").disabled',65);pause(1)
        check(builder_state(False)['answer']==[],'Standalone next molecule resets answer')
        _visible_point('#bank-tiles li:first-child button',False)
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
