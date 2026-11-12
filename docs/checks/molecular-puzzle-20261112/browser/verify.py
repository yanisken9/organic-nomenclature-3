"""One owned headless Firefox; real pointer/keyboard interaction, no user profiles."""
from pathlib import Path
import base64, datetime, hashlib, http.server, json, os, socket, subprocess
import tempfile, threading, time, traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT={'checks':[], 'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
server=firefox=log=None
def check(value,label):
    OUT['checks'].append({'label':label,'passed':bool(value)})
    if not value:raise AssertionError(label)
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def click(selector):
    ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"nearest",behavior:"instant"})')
    point=read('(() => {const e=document.querySelector('+json.dumps(selector)+');const r=e.getBoundingClientRect();return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2),disabled:e.disabled}})()')
    check(not point.get('disabled'), 'enabled control '+selector)
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[
      {'type':'pointerMove','x':point['x'],'y':point['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
    time.sleep(.05)
def drag_to(selector,x,y,pointer_type='mouse'):
    ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"nearest",behavior:"instant"})')
    p=read('(() => {const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()')
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':pointer_type,'parameters':{'pointerType':pointer_type},'actions':[
      {'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},
      {'type':'pointerMove','x':x,'y':y,'duration':350},{'type':'pointerUp','button':0}]}]})
    time.sleep(.1)
def state():return read('({nodes:[...document.querySelectorAll("#board-nodes button")].map(e=>({id:e.dataset.nodeId,label:e.textContent,left:e.style.left,top:e.style.top})),bonds:document.querySelectorAll("#board-svg .puzzle-bond:not(.puzzle-bond-hit)").length,feedback:document.querySelector("#feedback").textContent,feedbackHidden:document.querySelector("#feedback").hidden,solved:document.querySelector("#feedback").classList.contains("success")})')
def keys(*values):
    actions=[]
    for value in values: actions += [{'type':'keyDown','value':value},{'type':'keyUp','value':value}]
    call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':actions}]})
def select_round(i):
    # Round navigation via actual Next control. Native macOS select popup keys
    # could not be driven reliably in earlier headless runs (retained evidence).
    for _ in range(8):
        if ev('Number(document.querySelector("#round-select").value)')==i:break
        click('#next-molecule')
    check(ev('Number(document.querySelector("#round-select").value)')==i,'next-control round navigation '+str(i))
def build(target):
    for node in target['nodes']:click('[data-hydrogens="'+str(node['hydrogens'])+'"]')
    ids=[n['id'] for n in state()['nodes']]
    mapping={n['id']:ids[i] for i,n in enumerate(target['nodes'])}
    if target['bonds']:
        click('#bond-tool')
        for edge in target['bonds']:
            click('[data-node-id="'+mapping[edge['a']]+'"]')
            click('[data-node-id="'+mapping[edge['b']]+'"]')
    return ids
def shot(name):
    data=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'})
    (HERE/name).write_bytes(base64.b64decode(data['data']))
def viewport(w,h):
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});time.sleep(.2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,*a):pass
try:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with socket.socket() as p:p.bind(('127.0.0.1',0));port=p.getsockname()[1]
    profile=Path(tempfile.mkdtemp(prefix='namelecule-puzzle-test-'))
    log=(HERE/'firefox.log').open('w')
    firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
    OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'serverPort':server.server_port,'bidiPort':port}
    print(json.dumps(OUT['process']),flush=True)
    deadline=time.monotonic()+25
    while True:
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=.4):break
        except OSError:
            if time.monotonic()>deadline:raise
            time.sleep(.2)
    os.environ['NAMELECULE_BIDI_PORT']=str(port)
    os.environ['NAMELECULE_TEST_BASE_URL']=f'http://127.0.0.1:{server.server_port}/'
    exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),str(ROOT/'tools/namelecule_bidi.py'),'exec'))
    viewport(1440,1000)
    navigate('games/molecular-puzzle.html')
    until('document.querySelector("#round-select").options.length===8 && !document.querySelector("#next-molecule").disabled',40)
    OUT['names']=read('[...document.querySelector("#round-select").options].map(e=>e.textContent)')
    OUT['typography']=read('(()=>{const s=getComputedStyle(document.querySelector("#game-title"));return{fontFamily:s.fontFamily,fontSize:s.fontSize,fontWeight:s.fontWeight,lineHeight:s.lineHeight,letterSpacing:s.letterSpacing}})()')
    OUT['entry']=read('({height:innerHeight,bank:document.querySelector("#piece-bank").getBoundingClientRect().toJSON(),board:document.querySelector("#assembly-board").getBoundingClientRect().toJSON(),scrollHeight:document.documentElement.scrollHeight})')
    targets=json.loads(ev('(async()=>{const c=await(await fetch("data/alkane-structures.json")).json();return JSON.stringify(c.molecules.map(m=>NameleculeMolecularPuzzleEngine.parseMol(m.mol)))})()'))
    check(len(targets)==8,'8 real source targets parsed in browser')
    OUT['engineChecks']=json.loads(ev((HERE/'engine-checks.js').read_text()))
    check(all(c['passed'] for c in OUT['engineChecks']),'all pure engine/source checks in actual browser')
    for i,target in enumerate(targets):
        if i:click('#next-molecule')
        check(state()['nodes']==[],'round starts empty '+str(i))
        ids=build(target)
        check(len(ids)==len(target['nodes']),'piece additions '+str(i))
        check(state()['bonds']==len(target['bonds']),'bond connections '+str(i))
        check(ev('[...document.querySelectorAll("#board-nodes button")].every(e=>{const r=e.getBoundingClientRect(),b=document.querySelector("#assembly-board").getBoundingClientRect();return r.left>=b.left&&r.right<=b.right&&r.top>=b.top&&r.bottom<=b.bottom})'),'complete node labels framed round '+str(i))
        if i==7:shot('largest-construction.png')
        click('#check-answer')
        check(state()['solved'],'genuine correct UI construction '+str(i))
        check(ev('document.querySelector("#check-answer").disabled && [...document.querySelectorAll("[data-hydrogens],#board-nodes button")].every(e=>e.disabled)'),'solved state locks '+str(i))
        print('correct round '+str(i),flush=True)
    click('#next-molecule')
    # Wrong response keeps actual work; editing clears the stale feedback.
    click('[data-hydrogens="3"]');click('#check-answer')
    check(not state()['solved'] and len(state()['nodes'])==1 and not state()['feedbackHidden'],'wrong work retained')
    click('[data-hydrogens="2"]')
    check(state()['feedbackHidden'],'editing clears stale feedback')
    click('#undo-action');check(len(state()['nodes'])==1,'undo addition')
    first=state()['nodes'][0]['id'];click('[data-node-id="'+first+'"]')
    before=state()['nodes'][0]['left'];keys('\ue014')
    check(state()['nodes'][0]['left']!=before,'keyboard arrow moves actual group')
    keys('\ue017');check(state()['nodes']==[],'keyboard Delete removes group')
    click('#undo-action');check(len(state()['nodes'])==1,'undo removal')
    # Trusted palette drag into board; trusted placed drag out returns reusable piece.
    ev('document.querySelector("#piece-bank").scrollIntoView({block:"end",behavior:"instant"})')
    b=read('document.querySelector("#assembly-board").getBoundingClientRect().toJSON()')
    drag_to('[data-hydrogens="2"]',round(b['left']+b['width']*.25),round(b['top']+b['height']*.5))
    check(len(state()['nodes'])==2,'trusted palette drag adds group')
    second=state()['nodes'][-1]['id']
    ev('document.querySelector("#piece-bank").scrollIntoView({block:"nearest",behavior:"instant"})')
    p=read('document.querySelector("#piece-bank").getBoundingClientRect().toJSON()')
    drag_to('[data-node-id="'+second+'"]',round(p['left']+p['width']*.8),round(p['top']+p['height']*.5))
    check(len(state()['nodes'])==1,'trusted completed outside-board drop removes group')
    check(ev("!document.querySelector('[data-hydrogens=\"2\"]').disabled"),'removed group reusable in palette')
    # Remove a real bond by its visible SVG control, preserving its two groups.
    click('#next-molecule');build(targets[1])
    click('#board-svg .puzzle-bond:not(.puzzle-bond-hit)');keys('\ue017')
    check(state()['bonds']==0 and len(state()['nodes'])==2,'keyboard removal of selected SVG bond')
    click('#undo-action');check(state()['bonds']==1,'undo bond removal')
    # Correct formula and fragment counts are insufficient: wrong branched isomer.
    select_round(5)
    wrong={'nodes':[{'id':str(i),'hydrogens':h} for i,h in enumerate([3,2,1,2,3,3])],
           'bonds':[{'a':str(a),'b':str(b),'order':1} for a,b in [(0,1),(1,2),(2,3),(3,4),(2,5)]]}
    build(wrong);click('#check-answer')
    check(not state()['solved'] and len(state()['nodes'])==6 and 'δεν αντιστοιχεί' in state()['feedback'],'actual UI rejects same-formula same-count wrong isomer without clearing candidate')
    shot('desktop-interaction.png')
    # Compact phone view, no target-shaped slots, native instructions disclosure.
    viewport(390,844);navigate('games/molecular-puzzle.html?embedded=1')
    until('!document.querySelector("#next-molecule").disabled',40)
    time.sleep(.9)
    check(ev('document.querySelector("#piece-bank").getBoundingClientRect().bottom<=innerHeight'),'phone entry automatically reveals initial palette')
    check(ev('!document.querySelector("#instructions").open'),'phone instructions start collapsed')
    check(ev('document.documentElement.scrollWidth<=innerWidth'),'phone no page horizontal overflow')
    check(ev('getComputedStyle(document.querySelector(".site-header")).display==="none"'),'embedded has no standalone header')
    click('#instructions summary');check(ev('document.querySelector("#instructions").open'),'phone instructions open')
    click('#instructions summary');check(not ev('document.querySelector("#instructions").open'),'phone instructions close')
    click('[data-hydrogens="4"]');click('#check-answer');check(state()['solved'],'phone genuine methane success')
    time.sleep(.8)
    check(ev('document.querySelector("#feedback").getBoundingClientRect().bottom<=innerHeight+2'),'phone success automatically revealed')
    click('#next-molecule');build(targets[1]);click('#check-answer');check(state()['solved'],'phone genuine ethane with bond')
    time.sleep(.8);shot('phone-success.png')
    viewport(320,680);time.sleep(.3)
    check(ev('document.documentElement.scrollWidth<=innerWidth'),'320px no horizontal overflow')
    check(ev('[...document.querySelectorAll("#board-nodes button")].every(e=>{const r=e.getBoundingClientRect(),b=document.querySelector("#assembly-board").getBoundingClientRect();return r.left>=b.left&&r.right<=b.right&&r.top>=b.top&&r.bottom<=b.bottom})'),'320px complete node labels framed')
    # Same-origin lesson shell receives size only from its own child.
    viewport(1440,1000);navigate('design/molecular-puzzle-preview.html')
    until('document.querySelector("iframe").contentDocument.querySelector("#round-select").options.length===8',40)
    time.sleep(.2)
    check(ev('document.querySelector("iframe").getBoundingClientRect().height>300 && document.querySelector("iframe").getBoundingClientRect().bottom<=innerHeight'),'lesson preview frame fits available viewport with own scrolling')
    check(ev('document.documentElement.scrollWidth<=innerWidth'),'lesson shell no horizontal overflow')
    check(ev('getComputedStyle(document.querySelector("iframe").contentDocument.querySelector("#game-title")).fontSize==="40px"'),'embedded title matches existing parent-page 40px game title at 1440px')
    shot('lesson-preview.png')
    def fread(expression):
        return read('document.querySelector("iframe").contentWindow.eval('+json.dumps(expression)+')')
    def fclick(selector):
        fread('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"nearest",behavior:"instant"});true')
        p=fread('(()=>{const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()')
        f=read('document.querySelector("iframe").getBoundingClientRect().toJSON()')
        call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[
            {'type':'pointerMove','x':round(f['left']+p['x']),'y':round(f['top']+p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
        time.sleep(.06)
    fclick('[data-hydrogens="4"]');fclick('#check-answer')
    check(fread('document.querySelector("#feedback").classList.contains("success")'),'actual lesson-shell trusted methane construction')
    fclick('#next-molecule');fclick('[data-hydrogens="3"]');fclick('[data-hydrogens="3"]');fclick('#bond-tool')
    ids=fread('[...document.querySelectorAll("#board-nodes button")].map(e=>e.dataset.nodeId)')
    for node in ids:fclick('[data-node-id="'+node+'"]')
    fclick('#check-answer')
    check(fread('document.querySelector("#feedback").classList.contains("success")'),'actual lesson-shell trusted ethane construction')
    OUT['completed']=True
except Exception:
    OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
    try:shot('failure.png')
    except Exception:pass
finally:
    OUT['javascriptErrors']=globals().get('js_errors',[])
    if firefox is not None and firefox.poll() is None:
        firefox.terminate()
        try:firefox.wait(timeout=8)
        except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
    if server:server.shutdown();server.server_close()
    if log:log.close()
    OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
    (HERE/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'javascriptErrors':len(OUT['javascriptErrors']),'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
