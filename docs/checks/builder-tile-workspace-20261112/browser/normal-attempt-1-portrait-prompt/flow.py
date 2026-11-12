"""Actual Builder progression; construction actions never scroll test targets."""
from pathlib import Path
import datetime, hashlib, http.server, json, os, socket, subprocess, sys, tempfile, threading, time, traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MODE='reduced' if '--reduced' in sys.argv else 'normal'
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with socket.socket() as probe:
    probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
profile=Path(tempfile.mkdtemp(prefix='namelecule-builder-workspace-'+MODE+'-20261112-'))
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
    OUT['conditions']='Actual production UI/native viewer and canonical chemistry. Builder actions use trusted input with NO test scrolling/focus. Navigation/game selection and unchanged Workshop smoke use existing setup helpers.'
    viewport(1500,900);lesson(3,55);open_gate();install_scroll_trace();choose('builder')
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
        shot('reduced-feedback.png')
    else:
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
        lesson(10,55);open_gate();choose('repair');rsolve('shared Workshop smoke',10)
        choose('builder')
        for index in range(3):
            complete_builder('gate11-round'+str(index+1))
            if index<2:no_scroll_click('.round-next button',False)
        footer('gate11 final')
        check(read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Three genuine branched Builder rounds unlock second gate')
        shot('gate11-earned.png')
        no_scroll_click('.round-next button',False)
        wait('fScenarioPresent().index===11')
        check(read('fScenarioPresent().index')==11,'Continue reaches final molecule exploration')
        # A new optional triple on a phone; navigation setup may scroll outside a loaded Builder.
        viewport(390,760);lesson(3,55)
        click('#nlQuizPracticeOpen');wait('document.getElementById("nlQuizDialog").open');builder_ready();entry('phone390-new-triple')
        complete_builder('phone390-round1');no_scroll_click('.round-next button',False);entry('phone390-next-round')
        shot('phone390-next.png')
        viewport(320,740)
        call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
        click('#nlQuizPracticeOpen');wait('document.getElementById("nlQuizDialog").open');builder_ready();entry('phone320-restored-triple')
        shot('phone320-entry.png')
        check(read('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Phone refresh retains earned gate')
        # Same shared controller in the retained v54.
        viewport(1024,768);lesson(3,54);open_gate();choose('builder');entry('Main54-entry')
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
