"""Developer runtime evidence: isolated Firefox, candidate57, genuine UI answers.

The canonical read-only oracles choose input; no solved state, storage receipt,
callback or bridge response is injected. Every correct answer uses trusted BiDi
pointer input and the existing production Check action. Own temporary profile,
HTTP server and PID only. Run only after the root marks the candidate STABLE.
"""
from pathlib import Path
import base64, datetime, hashlib, http.server, json, os, shutil, socket
import subprocess, tempfile, threading, time, traceback, urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PLAN = json.loads((HERE.parent/'plan.json').read_text())
if os.environ.get('NAMELECULE_V57_BROWSER_READY') != 'frozen': raise RuntimeError('Root frozen-target/browser permission is required')
FREEZE_PATH = Path(os.environ['NAMELECULE_V57_FROZEN_MANIFEST'])
FREEZE = json.loads(FREEZE_PATH.read_text())
CANDIDATE = Path(os.environ.get('NAMELECULE_V57_CANDIDATE', PLAN['candidate']))
GAME = os.environ.get('NAMELECULE_V57_GAME', 'puzzle')
RUN = os.environ.get('NAMELECULE_V57_RUN', GAME+'-run1')
DEST = HERE/RUN
DEST.mkdir(exist_ok=False)
SOURCE = PLAN['newFiles'] + PLAN['navigationFiles'] + [
 'js/namelecule-game-choice-checkpoint.js', 'js/namelecule-quiz-checkpoints.js',
 'js/namelecule-generated-repair-checkpoint.js', 'js/namelecule-game-repair.js',
 'js/namelecule-name-builder.js', 'js/namelecule-name-builder-engine.js',
 'js/namelecule-molecular-puzzle.js', 'js/namelecule-molecular-puzzle-engine.js',
 'js/namelecule-chemistry-client.js', 'js/namelecule-chemistry-worker.js',
 'js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js',
 'games/name-repair.html','games/name-builder.html','games/molecular-puzzle.html',
 'games/data/alkane-structures.json','scenarios/alkanes-user-3.scenario.json',
 'mulermoc-nom-55.html','js/mulermoc-nom-core-55.js',
 'mulermoc-nom-56.html','js/mulermoc-nom-core-56.js',
 'js/mulermoc-nom-molview-56.js','js/mulermoc-nom-teaching-56.js','js/mulermoc-nom-scenario-56.js',
 'js/namelecule-molecular-detective.js','js/namelecule-molecular-detective-engine.js',
 'js/namelecule-molecular-detective-host.js','games/molecular-detective.html',
 'games/molecular-detective-viewer.html','css/namelecule-molecular-detective.css']
FROZEN = {p:(v if isinstance(v,str) else v['sha256']) for p,v in FREEZE['files'].items()}
assert set(PLAN['newFiles']+PLAN['navigationFiles']).issubset(FROZEN), 'Frozen manifest must cover all17 new/navigation paths'
assert all(hashlib.sha256((CANDIDATE/p).read_bytes()).hexdigest()==v for p,v in FROZEN.items()), 'Frozen target content drift before browser'
assert all(p in SOURCE for p in FROZEN), 'All frozen paths must be in HTTP/before/after coverage'
def sha(root):
 return {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE}
OUT = {'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'game':GAME,'frozenManifest':str(FREEZE_PATH),'frozenManifestSHA256':hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest(),'frozenFiles':FROZEN,'candidate':str(CANDIDATE),'checks':[],'rounds':[],
 'scope':'Candidate57 welcome/library and 12-step alkane replay; genuine required triples at both gates, partial/earned reload and optional triple. Isolated headless desktop with bounded phone resize. Developer execution, not independent review.',
 'sourceBefore':sha(CANDIDATE),'harnessSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
server = firefox = log = profile = None
MOLS = {m['id']:m['mol'] for m in json.loads((CANDIDATE/'games/data/alkane-structures.json').read_text())['molecules']}

def check(ok,label,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 if not ok: raise AssertionError((label,detail))
def read(expr): return json.loads(ev('JSON.stringify('+expr+')'))
def pause(seconds=.12): time.sleep(seconds)
def wait(expr,seconds=75):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(expr): return
  pause(.15)
 raise AssertionError('Timed out: '+expr)
def page(path):
 call('browsingContext.navigate',{'context':ctx,'url':OUT['process']['baseURL']+path,'wait':'none'})
 wait('document.readyState!=="loading"')
def shot(name):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'})
 (DEST/(name+'.png')).write_bytes(base64.b64decode(r['data']))
def viewport(w,h):
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});pause(.2)
def clickel(expr):
 # Scrolling is harness preparation. The click itself is trusted pointer input.
 # Verify child and parent hit-testing to avoid sticky dialog header misclicks.
 for attempt in range(12):
  ev('('+expr+').scrollIntoView({block:"center",inline:"nearest",behavior:"instant"});true');pause(.2)
  q=read('(()=>{const e='+expr+',r=e.getBoundingClientRect();let x=r.x+r.width/2,y=r.y+r.height/2,w=e.ownerDocument.defaultView,hit=e.contains(w.document.elementFromPoint(x,y));while(w!==window){const f=w.frameElement.getBoundingClientRect();x+=f.x;y+=f.y;w=w.parent;hit=hit&&w.document.elementFromPoint(x,y)===e.ownerDocument.defaultView.frameElement}const d=document.getElementById("nlQuizDialog"),h=d?.open?d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect():null;return{x:Math.round(x),y:Math.round(y),hit,disabled:!!e.disabled,headerAction:!!e.closest(".nl-quiz-dialog-header"),headerBottom:h?.bottom??0,dialogBottom:d?.open?d.getBoundingClientRect().bottom:innerHeight}})()')
  if q['disabled']: raise AssertionError(('Disabled UI action',expr,q))
  if q['hit'] and (q['y']>=q['headerBottom']+5 or q['headerAction'] or 'scNext' in expr): break
  if q['y']<q['headerBottom']+10:
   ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['headerBottom']-25)+',behavior:"instant"});true')
  elif q['y']>q['dialogBottom']-10:
   ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['dialogBottom']+25)+',behavior:"instant"});true')
 else: raise AssertionError(('Harness cannot find visible hit point',expr,q))
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'v57-replay-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':q['x'],'y':q['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});pause(.12)
def click(sel): clickel('document.querySelector('+json.dumps(sel)+')')
def frame_read(kind,expr): return read('document.querySelector(".nl-'+kind+'-frame").contentWindow.eval('+json.dumps(expr)+')')
def frame_click(kind,sel): clickel('document.querySelector(".nl-'+kind+'-frame").contentDocument.querySelector('+json.dumps(sel)+')')
def ready():
 wait('typeof jsmeNomeclatureApplet!=="undefined"&&!!jsmeNomeclatureApplet&&typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',100)
def rec():
 return read('(()=>{const c=JSON.stringify({version:1,title:String(fScenarioPresent().title||""),author:String(fScenarioPresent().author||"Unknown"),steps:fScenarioPresent().steps});return Object.values(sessionStorage).map(v=>{try{return JSON.parse(v)}catch(e){return null}}).find(v=>v?.content===c)??null})()')
def game_state(index,practice=False): return rec()['practices' if practice else 'states'][str(index)]['games'][GAME]
def open_gate():
 wait('!!document.getElementById("nlQuizOpen")&&!document.getElementById("nlQuizOpen").disabled');click('#nlQuizOpen');wait('document.getElementById("nlQuizDialog").open')
def game_ready(game=GAME):
 if game=='repair': wait('!!document.querySelector(".diagram-image.is-ready")')
 else:
  wait('!!document.querySelector(".nl-'+game+'-frame")')
  wait('!!document.querySelector(".nl-'+game+'-frame").contentDocument?.querySelector('+json.dumps('#assembly-board[aria-busy=false]' if game=='puzzle' else '#bank-tiles button')+')||!!document.querySelector(".nl-builder-error")')
  check(not ev('!!document.querySelector(".nl-builder-error")'),game+' prepared without adapter failure',ev('document.querySelector(".nl-builder-error")?.textContent'))
  wait('!!document.querySelector(".nl-'+game+'-frame").contentWindow.'+('__puzzleLoad' if game=='puzzle' else '__lessonLoad'))
def choose(game=GAME):
 if ev('!!document.querySelector(".nl-game-choice-switch")'): click('.nl-game-choice-switch')
 wait('document.querySelectorAll(".nl-game-choice-card").length===3')
 cards=read('[...document.querySelectorAll(".nl-game-choice-card")].map(e=>e.textContent)')
 check(any('Μοριακό παζλ' in c for c in cards),'all three current game choices visible',cards)
 click('.nl-game-choice-card:nth-child('+str({'repair':1,'builder':2,'puzzle':3}[game])+')');game_ready(game)
def footer(label,final):
 pause(.3)
 data=read('({buttons:[...document.querySelectorAll(".round-next button")].map(e=>e.textContent),header:[...document.querySelectorAll(".nl-quiz-dialog-header button")].map(e=>({text:e.textContent,hidden:e.hidden})),count:document.getElementById("nlQuizProgress").textContent})')
 check(len(data['buttons'])==(3 if final else 1),label+' footer count',data)
 if final: check(all(e['hidden'] for e in data['header']),label+' final header avoids duplicate actions',data)
 return data
def reload_gate():
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();game_ready()
def puzzle_state():
 return frame_read('puzzle','({nodes:[...document.querySelectorAll("#board-nodes button")].map(e=>({id:e.dataset.nodeId,label:e.textContent,left:e.style.left,top:e.style.top})),bonds:document.querySelectorAll("#board-svg .puzzle-bond:not(.puzzle-bond-hit)").length,feedback:document.querySelector("#feedback").textContent,solved:document.querySelector("#feedback").classList.contains("success"),load:window.__puzzleLoad})')
def psolve(label,index,practice=False,partial=False):
 load=puzzle_state()['load'];graph=frame_read('puzzle','NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(MOLS[load['moleculeId']])+')')
 start=0
 if partial:
  frame_click('puzzle','[data-hydrogens="0"]');frame_click('puzzle','#check-answer')
  check(not puzzle_state()['solved'] and not rec()['states'][str(index)]['solved'],label+' wrong graph rejected without unlock')
  frame_click('puzzle','#undo-action')
  frame_click('puzzle','[data-hydrogens="'+str(graph['nodes'][0]['hydrogens'])+'"]');pause(.3)
  before=puzzle_state();reload_gate();after=puzzle_state()
  check(after['nodes']==before['nodes'] and after['load']['moleculeId']==load['moleculeId'],label+' exact partial graph survives real reload')
  OUT['partialRestore']={'before':before,'after':after};start=1
 for node in graph['nodes'][start:]: frame_click('puzzle','[data-hydrogens="'+str(node['hydrogens'])+'"]')
 ids=[n['id'] for n in puzzle_state()['nodes']];mapping={n['id']:ids[i] for i,n in enumerate(graph['nodes'])}
 check(len(ids)==len(graph['nodes']),label+' actual group inventory')
 if graph['bonds']:
  if frame_read('puzzle','document.getElementById("bond-tool").getAttribute("aria-pressed")')!='true':frame_click('puzzle','#bond-tool')
  for edge in graph['bonds']:
   frame_click('puzzle','[data-node-id="'+mapping[edge['a']]+'"]');frame_click('puzzle','[data-node-id="'+mapping[edge['b']]+'"]')
 check(puzzle_state()['bonds']==len(graph['bonds']),label+' actual bonds')
 frame_click('puzzle','#check-answer');wait('!!document.querySelector(".round-next button")')
 check(puzzle_state()['solved'],label+' genuine graph Check accepted')
 return load['moleculeId'],load['correctName']
def bsolve(label,index,practice=False,partial=False):
 load=frame_read('builder','__lessonLoad');rnd=load['round']
 bank=frame_read('builder','NameleculeNameBuilderEngine.createBank(__lessonLoad.round,{seed:__lessonLoad.bankSeed})');used=set();ids=[]
 for piece in rnd['pieces']:
  tile=next(t for t in bank if t['id'] not in used and t['text']==piece['text'] and t['separatorBefore']==piece['separatorBefore']);used.add(tile['id']);ids.append(tile['id'])
 frame_click('builder','#bank-tiles [data-tile-id='+json.dumps(ids[0])+']')
 if partial:
  before=frame_read('builder','[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId)');reload_gate()
  after=frame_read('builder','[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId)')
  check(after==before==[ids[0]],label+' exact partial tile survives real reload');OUT['partialRestore']={'before':before,'after':after,'moleculeId':rnd['moleculeId']}
  check(frame_read('builder','!!document.querySelector("iframe")'),'legacy native Builder viewer frame exists')
 for tid in ids[1:]:frame_click('builder','#bank-tiles [data-tile-id='+json.dumps(tid)+']')
 check(frame_read('builder','document.getElementById("candidate-name").textContent')==rnd['correctName'],label+' composed exact name')
 frame_click('builder','#check-answer');wait('!!document.querySelector(".round-next button")')
 check(frame_read('builder','document.getElementById("feedback").classList.contains("success")'),label+' genuine name Check accepted')
 check(bool(frame_read('builder','document.querySelector(".lesson-explanation")?.textContent')),label+' explanation exists')
 return rnd['moleculeId'],rnd['correctName']
def rround(index,practice):
 state=game_state(index,practice)
 expr='(async()=>{const c=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput();return JSON.stringify(NameleculeRepairGenerator.createGame(c.catalog,c.analyses,{seed:'+json.dumps(state['seed'])+',difficulty:"basic"}).sets.find(s=>s.id==='+json.dumps('alkanes-unbranched' if index==3 else 'alkanes-branched')+').rounds['+str(state['currentRound'])+'])})()'
 return json.loads(ev(expr))
def rsolve(label,index,practice=False,partial=False):
 rnd=rround(index,practice)
 if rnd['kind']=='replace':
  click('[id$="part-'+rnd['targetPartId']+'"]')
  if partial:
   before=game_state(index,practice);reload_gate();after=game_state(index,practice)
   OUT['partialRestore']={'before':before,'after':after}
   check(after['seed']==before['seed'] and after['currentRound']==before['currentRound'] and after['states'][after['currentRound']]==before['states'][before['currentRound']],label+' selected repair survives real reload',OUT['partialRestore'])
  good=next(i for i,c in enumerate(rnd['choices']) if c['value']==rnd['correctValue']);click('[id$="choice-'+str(good)+'"]')
 else:
  if partial:
   click('.part-button');before=game_state(index,practice);reload_gate();after=game_state(index,practice)
   OUT['partialRestore']={'before':before,'after':after}
   check(after['seed']==before['seed'] and after['currentRound']==before['currentRound'] and after['states'][after['currentRound']]==before['states'][before['currentRound']],label+' selected sequence repair survives real reload',OUT['partialRestore'])
  for dest,pid in enumerate(rnd['correctOrder']):
   order=read('[...document.querySelectorAll(".part-button")].map(e=>e.id.split("part-")[1])');pos=order.index(pid)
   if pos>dest:
    click('[id$="part-'+pid+'"]')
    for _ in range(pos-dest):click('[id$="move-left"]')
 click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")&&!!document.querySelector(".round-next button")')
 check(True,label+' genuine repair Check accepted')
 return rnd['moleculeId'],rnd.get('correctName',rnd.get('kind'))
def solve(label,index,practice=False,partial=False):
 game_ready();mol,name={'puzzle':psolve,'builder':bsolve,'repair':rsolve}[GAME](label,index,practice,partial)
 state=game_state(index,practice)
 check(state['states'][state['currentRound']]['solved'],label+' parent independently accepts production receipt')
 OUT['rounds'].append({'label':label,'moleculeId':mol,'name':name,'practice':practice,'state':state})
 print(json.dumps({'label':label,'moleculeId':mol},ensure_ascii=False),flush=True)
 return mol
def triple(index,practice=False,partial=False):
 ids=[]
 for i in range(3):
  label=GAME+' '+('optional ' if practice else '')+'gate'+str(index+1)+' round'+str(i+1)
  ids.append(solve(label,index,practice,partial and i==0));footer(label,i==2)
  check(read('document.getElementById("nlQuizProgress").textContent').endswith(str(i+1)+'/3'),label+' correct visible counter')
  if not practice and i<2:check(not rec()['states'][str(index)]['solved'],label+' remains locked before complete same-game triple')
  if i<2:click('.round-next button:first-child');game_ready()
 check(len(set(ids))==3,GAME+' '+str(index+1)+' triple has three distinct molecules',ids)
 if not practice:
  check(rec()['states'][str(index)]['solved'] and rec()['states'][str(index)]['earned']['game']==GAME,GAME+' '+str(index+1)+' earned only after complete triple')
 return ids

class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(CANDIDATE),**kw)
 def log_message(self,*a):pass
 def send_error(self,code,message=None,explain=None):
  OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)

class AuthorProbeComplete(Exception): pass
def author_probe():
 page('mulermoc-nom-57.html?scenario=scenarios/alkanes-user-3.scenario.json#step=1');ready()
 wait('document.readyState==="complete"&&MuLERMoCScenario.ready===true');pause(1)
 OUT['authorFocusBeforeActivate']=read('({hasFocus:document.hasFocus(),visibility:document.visibilityState,active:document.activeElement?.id})')
 call('browsingContext.activate',{'context':ctx})
 ev('window.__authorInput=[];["pointerdown","pointerup","click","keydown"].forEach(type=>document.addEventListener(type,e=>{if(e.target.closest?.("#scenarioAuthorTab,#scExit"))window.__authorInput.push({type,trusted:e.isTrusted,key:e.key??null,target:e.target.id||e.target.className,authoring:MuLERMoCScenario.authoring,present:MuLERMoCScenario.present,preview:fScenarioIsAuthorPreview(fScenarioPresent()),defaultPrevented:e.defaultPrevented,x:e.clientX,y:e.clientY})},true));true')
 OUT['authorBeforeClick']=read('({ready:document.readyState,hasFocus:document.hasFocus(),visibility:document.visibilityState,authoring:MuLERMoCScenario.authoring,onclick:String(document.getElementById("scenarioAuthorTab").onclick),rect:document.getElementById("scenarioAuthorTab").getBoundingClientRect().toJSON()})')
 check(not ev('MuLERMoCScenario.present'),'author import opens outside presentation')
 check(rec() is None,'fresh author tab has no learner receipt')
 shot('author-before-tab');click('#scenarioAuthorTab');pause(.4)
 OUT['authorAfterClick']=read('({authoring:MuLERMoCScenario.authoring,events:__authorInput,rect:document.getElementById("scenarioAuthorTab").getBoundingClientRect().toJSON()})')
 wait('MuLERMoCScenario.authoring',5)
 click('.scenarioPanel.active .scList');wait('!!document.querySelector(".scenarioPanel.active .scenarioDrawer.open")')
 click('.scenarioPanel.active .srow[data-idx="4"] .scPresentStep')
 wait('MuLERMoCScenario.present&&fScenarioPresent().index===4&&fScenarioIsAuthorPreview(fScenarioPresent())')
 check(not ev('document.getElementById("scNext").disabled'),'actual step5 author preview bypasses unsolved gate4');shot('author-preview-step5')
 preview_indices=[4]
 for i in range(5,12):
  pause(1);click('#scNext');wait('fScenarioPresent().index==='+str(i));preview_indices.append(i)
 check(preview_indices==list(range(4,12)),'author rehearsal traverses steps5 through12 including gate11',preview_indices)
 check(rec() is None,'author rehearsal creates no stored learner receipt');OUT['authorPreviewIndices']=preview_indices;shot('author-preview-step12')
 OUT['authorExitBefore']=read('({url:location.href,hasFocus:document.hasFocus(),visibility:document.visibilityState,present:MuLERMoCScenario.present,preview:fScenarioIsAuthorPreview(fScenarioPresent()),inner:[innerWidth,innerHeight],outer:[outerWidth,outerHeight],onclick:String(document.getElementById("scExit").onclick),rect:document.getElementById("scExit").getBoundingClientRect().toJSON()})')
 click('#scExit');pause(.4)
 OUT['authorExitAfter']=read('({url:location.href,hasFocus:document.hasFocus(),visibility:document.visibilityState,present:MuLERMoCScenario.present,preview:fScenarioIsAuthorPreview(fScenarioPresent()),inner:[innerWidth,innerHeight],outer:[outerWidth,outerHeight],events:__authorInput,windowEvents:window.__authorWindowInput??[]})')
 wait('!MuLERMoCScenario.present&&!fScenarioIsAuthorPreview(fScenarioPresent())')
 check(ev('MuLERMoCScenario.authoring'),'preview Exit returns to authoring')
 click('.scenarioPanel.active .scPresent');wait('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&fScenarioPresent().index===0')
 check(not ev('fScenarioIsAuthorPreview(fScenarioPresent())'),'normal card Play ends transient author bypass')
 ev('location.hash="step=5";true');wait('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('document.getElementById("scNext").disabled'),'normal learner Play still requires unsolved gate4')
 record=rec();check(record is None or not record.get('states',{}).get('3',{}).get('solved',False),'preview never earns learner unlock')
 OUT['afterNormalPlayRecord']=record;shot('learner-gate-after-author-preview')

try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-v57-replay-20261115-',dir='/private/tmp'));log=(DEST/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'bidiPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
 end=time.monotonic()+30
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4):break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>end:raise RuntimeError('Own BiDi endpoint unavailable')
   pause(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['process']['baseURL']
 exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'v57-own-bidi','exec'))
 call('session.subscribe',{'events':['network.beforeRequestSent','network.responseCompleted','network.fetchError'],'contexts':[ctx]})
 call('script.addPreloadScript',{'functionDeclaration':'''() => {addEventListener('message',e=>{if(e.data?.channel==='namelecule-builder-lesson-v1'&&e.data.command==='load')window.__lessonLoad=e.data;if(e.data?.channel==='namelecule-puzzle-lesson-v1'&&e.data.command==='load')window.__puzzleLoad=e.data;})}'''})
 call('script.addPreloadScript',{'functionDeclaration':'''() => {window.__authorWindowInput=[];for(const type of ['pointermove','pointerdown','pointerup','mousedown','mouseup','click','keydown'])window.addEventListener(type,e=>{if(e.target?.closest?.('#scExit'))window.__authorWindowInput.push({type,trusted:e.isTrusted,key:e.key??null,target:e.target?.id||e.target?.className,x:e.clientX,y:e.clientY,defaultPrevented:e.defaultPrevented})},true)}'''})
 OUT['httpSourceSHA256']={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p).read()).hexdigest() for p in SOURCE}
 check(OUT['httpSourceSHA256']==OUT['sourceBefore'],'HTTP serves exact candidate source hashes',len(SOURCE))
 viewport(int(os.environ.get('NAMELECULE_V57_VIEWPORT_WIDTH','1440')),int(os.environ.get('NAMELECULE_V57_VIEWPORT_HEIGHT','1000')))
 OUT['browserSurface']=read('({inner:[innerWidth,innerHeight],outer:[outerWidth,outerHeight],screen:[screenX,screenY]})')
 if GAME=='author':
  OUT['scope']='Actual step5 author rehearsal through12 bypasses both learner gates; Exit/card Play restores learner gate4 without creating a stored earned receipt.'
  author_probe();raise AuthorProbeComplete()
 page('design/welcome-proposal.html');wait('!!document.querySelector(".card.one .action")')
 wait('document.querySelector(".brand img").complete&&document.querySelector(".brand img").naturalWidth>0')
 check(ev('document.title.includes("Namelecule")'),'welcome title/brand ready');shot('welcome')
 click('.card.one .action');wait('location.pathname.endsWith("/design/theory-library.html")&&!!document.querySelector("#alkanes-title")')
 href=read('document.querySelector(".lesson:first-child .action").href')
 check('mulermoc-nom-57.html?' in href and 'alkanes-user-3.scenario.json' in href,'library actual alkane entry uses Main57',href)
 click('.lesson:first-child .action');ready();check(read('fScenarioPresent().index')==0,'welcome/library actual clicks begin step1');OUT['lessonURL']=read('location.href')
 OUT['replayIndices']=[0]
 for i in range(1,4):
  pause(.85);click('#scNext');wait('fScenarioPresent().index==='+str(i));OUT['replayIndices'].append(i)
 check(ev('document.getElementById("scNext").disabled'),'cold step4 blocks before earned results')
 ev('location.hash="step=11";true');wait('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation')
 check(read('location.hash')=='#step=4','actual hash jump cannot bypass unsolved gate4')
 open_gate();choose();shot('gate4-choice-'+GAME)
 OUT['gate4IDs']=triple(3,partial=True);earned=rec()['states']['3']['earned'];shot('gate4-earned')
 reload_gate();check(rec()['states']['3']['earned']==earned and rec()['states']['3']['solved'],'real reload preserves and revalidates earned gate4');footer('restored required gate4',True)
 click('.round-next button:nth-child(2)');game_ready()
 check('Προαιρετική' in read('document.getElementById("nlQuizDialogTitle").textContent'),'same-game optional triple is explicitly optional')
 OUT['optionalIDs']=triple(3,practice=True)
 check(rec()['states']['3']['earned']==earned,'complete optional triple preserves exact required receipt');shot('gate4-optional-complete')
 click('.round-next button:nth-child(3)');wait('document.querySelectorAll(".nl-game-choice-card").length===3')
 check(rec()['states']['3']['earned']==earned,'other-game chooser preserves earned receipt')
 other={'puzzle':'builder','builder':'repair','repair':'puzzle'}[GAME];choose(other)
 check(rec()['practices']['3']['selected']==other,'other-game chooser loads chosen distinct game')
 click('#nlQuizPracticeContinue');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');OUT['replayIndices'].append(4)
 for i in range(5,11):
  pause(1);click('#scNext');wait('fScenarioPresent().index==='+str(i));OUT['replayIndices'].append(i);print('replay reached step '+str(i+1),flush=True)
 check(ev('document.getElementById("scNext").disabled'),'second gate11 independently blocks')
 open_gate();choose();OUT['gate11IDs']=triple(10);earned11=rec()['states']['10']['earned'];shot('gate11-earned')
 check(set(OUT['gate4IDs']).isdisjoint(OUT['gate11IDs']),'straight and branched gate pools are separate')
 check(set(OUT['gate11IDs'])=={'methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane'},'all approved branched molecules actually solved')
 reload_gate();check(rec()['states']['3']['earned']==earned and rec()['states']['10']['earned']==earned11,'cold reload revalidates both exact earned receipts');footer('restored required gate11',True)
 viewport(390,844);pause(.3)
 check(ev('document.documentElement.scrollWidth<=innerWidth'),'solved phone lesson has no horizontal overflow')
 if GAME!='repair':check(frame_read(GAME,'document.documentElement.scrollWidth<=innerWidth'),'solved phone game has no horizontal overflow')
 shot('phone-gate11-earned');click('.round-next button:first-child');wait('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open');OUT['replayIndices'].append(11)
 check(OUT['replayIndices']==list(range(12)),'all twelve lesson steps replayed in order',OUT['replayIndices']);OUT['finalRecord']=rec();shot('step12')
 OUT['completed']=True
except AuthorProbeComplete:
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']={'url':read('location.href'),'index':read('typeof fScenarioPresent==="function"?fScenarioPresent()?.index:null'),'record':rec(),'body':read('document.body.innerText.slice(-9000)'),'authorInput':read('window.__authorInput??null'),'authoring':read('typeof MuLERMoCScenario!=="undefined"?MuLERMoCScenario.authoring:null'),'present':read('typeof MuLERMoCScenario!=="undefined"?MuLERMoCScenario.present:null'),'preview':read('typeof fScenarioIsAuthorPreview==="function"?fScenarioIsAuthorPreview(fScenarioPresent()):null'),'visibility':read('document.visibilityState'),'hasFocus':read('document.hasFocus()')};shot('failure')
 except Exception as capture:OUT['failureCaptureError']=repr(capture)
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[])
 events=globals().get('all_events',[])
 OUT['consoleEntries']=[e for e in events if e.get('method')=='log.entryAdded']
 def external_event(e):
  p=e.get('params',{});u=p.get('request',{}).get('url','')
  return e.get('method')=='network.fetchError' or any(s in u.lower() for s in ['pubchem','cactus','fonts.googleapis','fonts.gstatic','jsmoltracker','3dmol','rdkit'])
 OUT['providerDiagnostics']=[e for e in events if e.get('method','').startswith('network.') and external_event(e)]
 OUT['sourceAfter']=sha(CANDIDATE);OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
 if firefox is not None and firefox.poll() is None:
  firefox.terminate()
  try:firefox.wait(timeout=8)
  except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
 OUT['ownedServerClosed']=server is None or server.fileno()==-1
 if profile and OUT['ownedBrowserExited'] and profile.name.startswith('namelecule-v57-replay-20261115-'):shutil.rmtree(profile);OUT['ownProfileRemoved']=not profile.exists()
 OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'javascriptErrors':len(OUT['javascriptErrors']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
