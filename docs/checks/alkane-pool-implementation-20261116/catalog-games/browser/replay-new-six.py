"""Bounded Developer UI replay: six real Builder and six real Puzzle answers.

Preparation only until the root supplies the frozen manifest and browser slot.
No receipts, graph/answer state, solved flags or production messages are injected.
Read-only native messages/engines select trusted input to production controls.
Trusted pointer helper adapted from v57-sync-20261115/browser/replay.py.
"""
from pathlib import Path
import base64, datetime, hashlib, http.server, json, os, shutil, socket
import subprocess, tempfile, threading, time, traceback, urllib.request

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_ALKANE_BROWSER_READY') == 'frozen', 'Root frozen-target/browser-slot permission required'
FREEZE_PATH = Path(os.environ['NAMELECULE_ALKANE_FROZEN_MANIFEST'])
FREEZE = json.loads(FREEZE_PATH.read_text())
FROZEN = {p:(v if isinstance(v,str) else v['sha256']) for p,v in FREEZE['files'].items()}
assert FROZEN and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in FROZEN.items()), 'Frozen target drift before browser'
CATALOG = json.loads((ROOT/'games/data/alkane-structures-v2.json').read_text())
PACK = json.loads((ROOT/'data/namelecule-alkanes-v1/manifest.json').read_text())
NEW = PACK['molecules']
MOLS = {m['id']:m['mol'] for m in CATALOG['molecules']}
SOURCES = set(FROZEN) | {'games/name-builder.html','games/name-builder-viewer.html','games/molecular-puzzle.html',
 'games/data/alkane-structures.json','games/data/alkane-structures-v2.json','data/namelecule-alkanes-v1/manifest.json',
 'js/MULERMOC_namelecule_alkanes_v1_data.js','js/namelecule-name-builder.js','js/namelecule-name-builder-host.js',
 'js/namelecule-name-builder-engine.js','js/namelecule-molecular-puzzle.js','js/namelecule-molecular-puzzle-engine.js',
 'js/namelecule-chemistry-client.js','js/namelecule-chemistry-worker.js','scenarios/alkanes-user-3.scenario.json',
 'js/mulermoc-nom-core-55.js','js/mulermoc-nom-core-57.js','js/mulermoc-nom-molview-55.js','js/mulermoc-nom-molview-57.js',
 'js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js'}
def hashes(): return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(SOURCES)}
DEST = HERE/('run-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'))
DEST.mkdir(exist_ok=False)
OUT = {'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Developer browser execution; not independent review',
 'scope':'Six new standalone Builder names and six new Puzzle graphs via trusted controls; partial/wrong/empty checks, native55 inventory, representations/zoom and bounded legacy lesson partial reload.',
 'frozenManifest':str(FREEZE_PATH),'frozenManifestSHA256':hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest(),'frozenFiles':FROZEN,
 'sourceBefore':hashes(),'checks':[],'correctUIAttempts':[],'helperSource':'docs/checks/v57-sync-20261115/browser/replay.py',
 'helperSHA256':hashlib.sha256((ROOT/'docs/checks/v57-sync-20261115/browser/replay.py').read_bytes()).hexdigest(),
 'harnessSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'limitations':['Isolated headless Firefox with CSS viewport emulation; no physical mobile, personal Firefox, conference or offline qualification.','JSmol remote j2s/fonts/services remain external dependencies.','Firefox native select keyboard input did not change selection in retained harness attempts; actual Puzzle fixture cycling uses the production Next button instead, so native select interaction is unqualified.']}
server = firefox = log = profile = None

def check(ok,label,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError((label,detail))
 print('PASS '+label,flush=True)
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def pause(seconds=.14):time.sleep(seconds)
def wait(expr,seconds=75):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if ev(expr):return
  pause(.12)
 raise AssertionError('Timed out: '+expr)
def page(path):
 call('browsingContext.navigate',{'context':ctx,'url':path if path.startswith('http') else OUT['process']['baseURL']+path,'wait':'none'})
 wait('document.readyState!=="loading"');call('browsingContext.activate',{'context':ctx})
def shot(name):
 item=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(DEST/(name+'.png')).write_bytes(base64.b64decode(item['data']))
def viewport(width,height):
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});pause(.3)
def press_key(value):
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'alkane-pool-keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]});pause(.1)
def clickel(expr):
 # Reused v57 helper: scroll preparation, hit-test in each frame, trusted input.
 for attempt in range(12):
  ev('('+expr+').scrollIntoView({block:"center",inline:"nearest",behavior:"instant"});true');pause(.2)
  q=read('(()=>{const e='+expr+',r=e.getBoundingClientRect();let x=r.x+r.width/2,y=r.y+r.height/2,w=e.ownerDocument.defaultView,hit=e.contains(w.document.elementFromPoint(x,y));while(w!==window){const f=w.frameElement.getBoundingClientRect();x+=f.x;y+=f.y;w=w.parent;hit=hit&&w.document.elementFromPoint(x,y)===e.ownerDocument.defaultView.frameElement}const d=document.getElementById("nlQuizDialog"),h=d?.open?d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect():null;return{x:Math.round(x),y:Math.round(y),hit,disabled:!!e.disabled,headerAction:!!e.closest(".nl-quiz-dialog-header"),headerBottom:h?.bottom??0,dialogBottom:d?.open?d.getBoundingClientRect().bottom:innerHeight}})()')
  if q['disabled']:raise AssertionError(('Disabled UI action',expr,q))
  if q['hit'] and (q['y']>=q['headerBottom']+5 or q['headerAction'] or 'scNext' in expr):break
  if q['y']<q['headerBottom']+10:ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['headerBottom']-25)+',behavior:"instant"});true')
  elif q['y']>q['dialogBottom']-10:ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['dialogBottom']+25)+',behavior:"instant"});true')
 else:raise AssertionError(('Harness could not find visible hit point',expr,q))
 check(0<=q['x']<1500 and 0<=q['y']<1000,'trusted pointer inside CSS/physical input surface',q)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'alkane-pool-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':q['x'],'y':q['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});pause(.15)
def click(selector):clickel('document.querySelector('+json.dumps(selector)+')')
def native(expr):return read('document.getElementById("molecule-viewer").contentWindow.eval('+json.dumps(expr)+')')
def last_message(kind):return read('[...window.__poolMessages].reverse().find(m=>m.type==='+json.dumps(kind)+')??null')
def answer():return read('[...document.querySelectorAll("#answer-tiles button")].map(e=>({id:e.dataset.tileId,text:e.textContent}))')
def puzzle_snapshot(prefix='document'):
 return read('(()=>{const d='+prefix+';return {nodes:[...d.querySelectorAll("#board-nodes button")].map(e=>({id:e.dataset.nodeId,label:e.textContent,left:e.style.left,top:e.style.top})),bonds:d.querySelectorAll("#board-svg .puzzle-bond:not(.puzzle-bond-hit)").length,solved:d.querySelector("#feedback").classList.contains("success"),feedback:d.querySelector("#feedback").textContent}})()')
def builder_round(record):
 mid=record['id'];page('games/name-builder.html?molecule='+mid+'&v=alkane-pool-20261116-browser')
 wait('!!window.__poolMessages?.some(m=>m.type==="round")&&!!document.querySelector("#bank-tiles button")&&document.getElementById("viewer-mask").hidden',100)
 rnd=last_message('round');ready=last_message('ready')
 check(rnd['moleculeId']==mid and rnd['correctName']==record['nameGR'],'Builder native55 target '+mid,rnd)
 check(len(ready['inventory'])==147 and all(any(e['id']==m['id'] and set(e['representations'])=={'condensed','expanded','skeletal','3d'} for e in ready['inventory']) for m in NEW),'Builder native55 inventory147 includes all six representations',len(ready['inventory']))
 sources=native('[...document.scripts].map(s=>s.src)')
 check(any('/js/mulermoc-nom-core-55.js' in s for s in sources) and any('/js/MULERMOC_namelecule_alkanes_v1_data.js' in s for s in sources),'Builder uses native55 and curated bundle',sources)
 check(ev('document.getElementById("check-answer").disabled'),'Builder empty answer disabled '+mid)
 bank=read('[...document.querySelectorAll("#bank-tiles button")].map(e=>({id:e.dataset.tileId,text:e.textContent}))')
 remaining=bank.copy();ids=[]
 for piece in rnd['pieces']:
  match=next(t for t in remaining if t['text']==piece['text']);remaining.remove(match);ids.append(match['id'])
 # A nonanswer root and partial correct assembly are rejected by production Check.
 distractor=next(t for t in bank if t['id'] not in ids)
 click('#bank-tiles [data-tile-id='+json.dumps(distractor['id'])+']');click('#check-answer')
 check(not ev('document.getElementById("feedback").classList.contains("success")'),'Builder wrong root rejected '+mid)
 click('#remove-tile')
 click('#bank-tiles [data-tile-id='+json.dumps(ids[0])+']');click('#check-answer')
 check(not ev('document.getElementById("feedback").classList.contains("success")'),'Builder partial correct answer rejected '+mid)
 partial=answer()
 for mode in ['expanded','skeletal','3d','condensed']:
  mode_selector='[data-representation='+json.dumps(mode)+']'
  click(mode_selector)
  wait('document.querySelector('+json.dumps(mode_selector)+').getAttribute("aria-pressed")==="true"&&document.getElementById("viewer-mask").hidden',60)
  check(answer()==partial and native('selectedMol')==mid and native('currentMolName')==record['nameGR'],'Builder '+mode+' preserves partial/name '+mid)
  if mode=='3d':
   model=native('({models:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all").length,bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,"bondInfo","all").length})')
   check(len(model['models'])==1 and model['atoms']>0 and model['bonds']==model['atoms']-1,'Builder actual3D model loaded '+mid,model)
  else:check(native('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Builder '+mode+' actual SVG '+mid)
 zoom=native('molZoom2D');click('#zoom-in');wait('document.getElementById("molecule-viewer").contentWindow.eval("molZoom2D")>'+str(zoom))
 check(answer()==partial,'Builder zoom preserves partial '+mid);click('#zoom-out');wait('Math.abs(document.getElementById("molecule-viewer").contentWindow.eval("molZoom2D")-'+str(zoom)+')<.000001')
 for tid in ids[1:]:click('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
 check(ev('document.getElementById("candidate-name").textContent')==record['nameGR'],'Builder composed actual name '+mid)
 click('#check-answer');wait('document.getElementById("feedback").classList.contains("success")')
 check(ev('document.getElementById("check-answer").disabled'),'Builder genuine production answer accepted '+mid)
 OUT['correctUIAttempts'].append({'game':'builder','moleculeId':mid,'correctName':record['nameGR'],'answer':answer()});shot('builder-'+mid)

def select_puzzle(index):
 # Root-approved public Next control avoids unsupported native popup input.
 # Values/round changes are observed; no assignment or synthetic change occurs.
 for _ in range(14):
  current=read('document.getElementById("round-select").selectedIndex')
  if current==index:return
  click('#next-molecule')
  wait('document.getElementById("round-select").selectedIndex==='+str((current+1)%14),5)
 raise AssertionError('Production Next did not reach requested Puzzle fixture')

def puzzle_round(record):
 mid=record['id'];index=next(i for i,m in enumerate(CATALOG['molecules']) if m['id']==mid)
 select_puzzle(index)
 check(ev('document.getElementById("target-name").textContent')==record['nameGR'],'Puzzle actual select chooses '+mid)
 graph=read('NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(MOLS[mid])+')')
 check(ev('document.getElementById("check-answer").disabled'),'Puzzle empty graph disabled '+mid)
 click('[data-hydrogens="4"]');click('#check-answer')
 check(not puzzle_snapshot()['solved'],'Puzzle wrong methane graph rejected '+mid);click('#undo-action')
 for i,node in enumerate(graph['nodes']):
  click('[data-hydrogens="'+str(node['hydrogens'])+'"]')
  if i==0:
   click('#check-answer');check(not puzzle_snapshot()['solved'],'Puzzle partial disconnected graph rejected '+mid)
 snapshot=puzzle_snapshot();ids=[n['id'] for n in snapshot['nodes']];mapping={n['id']:ids[i] for i,n in enumerate(graph['nodes'])}
 check(len(ids)==len(graph['nodes']),'Puzzle correct real group count '+mid)
 if mid in ['dimethyl_2_2_propane','dimethyl_2_2_butane']:check(any(n['label']=='C' for n in snapshot['nodes']),'Puzzle zero-H C piece genuinely added '+mid)
 click('#bond-tool')
 for bond in graph['bonds']:
  click('[data-node-id='+json.dumps(mapping[bond['a']])+']');click('[data-node-id='+json.dumps(mapping[bond['b']])+']')
 check(puzzle_snapshot()['bonds']==len(graph['bonds']),'Puzzle real bonds count '+mid)
 click('#check-answer');wait('document.getElementById("feedback").classList.contains("success")')
 check(ev('document.getElementById("check-answer").disabled'),'Puzzle genuine production graph accepted '+mid)
 OUT['correctUIAttempts'].append({'game':'puzzle','moleculeId':mid,'correctName':record['nameGR'],'graphUI':puzzle_snapshot()});shot('puzzle-'+mid)

def legacy_probe():
 page('design/theory-library.html');wait('!!document.querySelector(".lesson:first-child .action")');click('.lesson:first-child .action')
 wait('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',100)
 for index in range(1,4):pause(.9);click('#scNext');wait('fScenarioPresent().index==='+str(index))
 check(ev('document.getElementById("scNext").disabled'),'current lesson old gate4 remains locked')
 click('#nlQuizOpen');wait('document.querySelectorAll(".nl-game-choice-card").length===3');click('.nl-game-choice-card:nth-child(3)')
 wait('!!document.querySelector(".nl-puzzle-frame")?.contentDocument?.querySelector("#assembly-board[aria-busy=false]")')
 wait('!!document.querySelector(".nl-puzzle-frame").contentWindow.__poolLessonLoad')
 frame='document.querySelector(".nl-puzzle-frame").contentDocument'
 load=read('document.querySelector(".nl-puzzle-frame").contentWindow.__poolLessonLoad')
 check(read(frame+'.querySelectorAll("#round-select option").length')==8,'current controlled lesson still uses old8')
 check(ev('fScenarioPresent().steps[3].checkpoint.round.catalogRevision')=='275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690','current required lesson recipe keeps legacy revision')
 clickel(frame+'.querySelector("[data-hydrogens=\\"3\\"]")');pause(.4);before=puzzle_snapshot(frame)
 call('browsingContext.reload',{'context':ctx,'wait':'none'});wait('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',100)
 click('#nlQuizOpen');wait('!!document.querySelector(".nl-puzzle-frame")?.contentDocument?.querySelector("#assembly-board[aria-busy=false]")');wait('!!document.querySelector(".nl-puzzle-frame").contentWindow.__poolLessonLoad')
 after=puzzle_snapshot(frame);loaded=read('document.querySelector(".nl-puzzle-frame").contentWindow.__poolLessonLoad')
 check(after['nodes']==before['nodes'] and after['bonds']==before['bonds'] and loaded['moleculeId']==load['moleculeId'] and not after['solved'],'real legacy partial board reload restores exactly')
 OUT['legacyPartial']={'before':before,'after':after,'moleculeId':load['moleculeId']};shot('legacy-partial-restored')

class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def log_message(self,*args):pass
 def send_error(self,code,message=None,explain=None):OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-alkane-game-replay-',dir='/private/tmp'));log=(DEST/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--width','1800','--height','1400','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,MOZ_HEADLESS_WIDTH='1800',MOZ_HEADLESS_HEIGHT='1400'))
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'bidiPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
 deadline=time.monotonic()+30
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4):break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned BiDi endpoint unavailable')
   pause(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['process']['baseURL']
 exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-alkane-games-bidi','exec'))
 call('session.subscribe',{'events':['network.beforeRequestSent','network.responseCompleted','network.fetchError'],'contexts':[ctx]})
 call('script.addPreloadScript',{'functionDeclaration':'''() => {window.__poolMessages=[];addEventListener('message',e=>{if(e.origin!==location.origin)return;if(e.data?.channel==='namelecule-name-builder-v1')window.__poolMessages.push(e.data);if(e.data?.channel==='namelecule-puzzle-lesson-v1'&&e.data.command==='load')window.__poolLessonLoad=e.data;});}'''})
 OUT['httpSourceSHA256']={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p).read()).hexdigest() for p in sorted(SOURCES)}
 check(OUT['httpSourceSHA256']==OUT['sourceBefore'],'HTTP serves exact frozen sources')
 viewport(1500,1000);OUT['inputSurface']=read('({innerWidth,innerHeight,outerWidth,outerHeight,screenWidth:screen.width,screenHeight:screen.height})')
 check(OUT['inputSurface']['outerWidth']>=1500 and OUT['inputSurface']['outerHeight']>=1000,'physical headless surface covers CSS viewport',OUT['inputSurface'])
 # BEGIN_GAME_REPLAY
 stage=os.environ.get('NAMELECULE_ALKANE_REPLAY_STAGE','all')
 if stage=='all':
  for record in NEW:builder_round(record)
 page('games/molecular-puzzle.html?v=alkane-pool-20261116-browser')
 wait('document.querySelectorAll("#round-select option").length===14&&!document.getElementById("round-select").disabled',100)
 check(ev('document.querySelectorAll("#round-select option").length')==14,'fresh Puzzle verified14 choices')
 for record in NEW:puzzle_round(record)
 before=puzzle_snapshot();viewport(390,844)
 check(ev('document.documentElement.scrollWidth<=innerWidth'),'solved narrow Puzzle no horizontal overflow')
 check(read('[...document.querySelectorAll("#board-nodes button")].every(e=>{const a=e.getBoundingClientRect(),b=document.getElementById("assembly-board").getBoundingClientRect();return a.left>=b.left-.5&&a.right<=b.right+.5&&a.top>=b.top-.5&&a.bottom<=b.bottom+.5})'),'narrow Puzzle all complete labels inside board')
 after=puzzle_snapshot();check([(n['id'],n['label']) for n in before['nodes']]==[(n['id'],n['label']) for n in after['nodes']] and before['bonds']==after['bonds'] and after['solved'],'resize preserves solved graph labels and bonds');shot('puzzle-solved-narrow');viewport(1500,1000)
 legacy_probe()
 check(len(OUT['correctUIAttempts'])==(12 if stage=='all' else 6),'all requested genuine answers completed for '+stage)
 check(not js_errors,'no captured page JavaScript exceptions',js_errors)
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']={'url':read('location.href'),'body':read('document.body.innerText.slice(-9000)'),'messages':read('window.__poolMessages??null'),'focus':read('document.activeElement?.outerHTML'),'surface':read('({innerWidth,innerHeight,outerWidth,outerHeight})')};shot('failure')
 except Exception as capture:OUT['failureCaptureError']=repr(capture)
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[])
 OUT['diagnostics']=[e for e in globals().get('all_events',[]) if e.get('method')=='log.entryAdded']
 OUT['networkErrors']=[e for e in globals().get('all_events',[]) if e.get('method')=='network.fetchError']
 OUT['sourceAfter']=hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
 if firefox is not None and firefox.poll() is None:
  firefox.terminate()
  try:firefox.wait(timeout=10)
  except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=10)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
 OUT['ownedServerClosed']=server is None or server.fileno()==-1
 if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith('namelecule-alkane-game-replay-') and not profile.is_symlink():shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
 OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'correctUIAttempts':len(OUT['correctUIAttempts']),'JSexceptions':len(OUT['javascriptErrors']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
