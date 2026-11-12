"""Approved lesson integration: one owned transient headless Firefox, real inputs.
No answer/progress injection. Read-only observers capture own iframe load identity.
"""
from pathlib import Path
import base64, datetime, hashlib, http.server, json, os, socket, subprocess
import tempfile, threading, time, traceback
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=['js/namelecule-game-choice-checkpoint.js','js/namelecule-molecular-puzzle.js','css/namelecule-molecular-puzzle.css','games/molecular-puzzle.html','mulermoc-nom-54.html','mulermoc-nom-55.html']
sha=lambda:{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCE}
OUT={'checks':[],'rounds':[],'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceBefore':sha(),'scope':'Full Main55 alkane lesson gates 4/11 and Main54 smoke; actual palette/node/bond/check inputs, no injected answer or progress. Read-only bridge-load observer.'}
server=firefox=log=None
CATALOG=json.loads((ROOT/'games/data/alkane-structures.json').read_text())
MOLS={m['id']:m['mol'] for m in CATALOG['molecules']}
def check(value,label,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(value),'detail':detail})
 if not value:raise AssertionError((label,detail))
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def wait(expr,seconds=55):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if ev(expr):return
  time.sleep(.15)
 raise AssertionError('Timed out: '+expr)
def pause(seconds=.18):time.sleep(seconds)
def fe(expr):return read('document.querySelector(".nl-puzzle-frame").contentWindow.eval('+json.dumps(expr)+')')
def pstate():return fe('({nodes:[...document.querySelectorAll("#board-nodes button")].map(e=>({id:e.dataset.nodeId,label:e.textContent,left:e.style.left,top:e.style.top})),bonds:document.querySelectorAll("#board-svg .puzzle-bond:not(.puzzle-bond-hit)").length,feedback:document.querySelector("#feedback").textContent,feedbackHidden:document.querySelector("#feedback").hidden,solved:document.querySelector("#feedback").classList.contains("success"),load:window.__puzzleLoad})')
def rec():return read('(()=>{const content=JSON.stringify({version:1,title:String(fScenarioPresent().title||""),author:String(fScenarioPresent().author||"Unknown"),steps:fScenarioPresent().steps});return Object.values(sessionStorage).map(v=>{try{return JSON.parse(v)}catch(e){return null}}).find(v=>v?.content===content)})()')
def clickel(expr):
 ev('('+expr+').scrollIntoView({block:"center",inline:"nearest",behavior:"instant"});true');pause(.08)
 p=read('(()=>{const e='+expr+',r=e.getBoundingClientRect();let x=r.x+r.width/2,y=r.y+r.height/2,w=e.ownerDocument.defaultView;while(w!==window){const f=w.frameElement.getBoundingClientRect();x+=f.x;y+=f.y;w=w.parent}return{x:Math.round(x),y:Math.round(y),disabled:!!e.disabled}})()')
 if p['disabled']:raise AssertionError(('Disabled',expr,p))
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'puzzle-mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});pause(.07)
def click(selector):clickel('document.querySelector('+json.dumps(selector)+')')
def fc(selector):clickel('document.querySelector(".nl-puzzle-frame").contentDocument.querySelector('+json.dumps(selector)+')')
def ready():
 wait('typeof jsmeNomeclatureApplet!=="undefined"&&!!jsmeNomeclatureApplet&&typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',90)
def lesson(index=3,version=55):
 call('browsingContext.navigate',{'context':ctx,'url':OUT['process']['baseURL']+f'mulermoc-nom-{version}.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step={index+1}','wait':'none'});ready()
def open_gate():
 wait('!!document.getElementById("nlQuizOpen")&&!document.getElementById("nlQuizOpen").disabled');click('#nlQuizOpen');wait('document.getElementById("nlQuizDialog").open')
def choose(game):
 if ev('!!document.querySelector(".nl-game-choice-switch")'):click('.nl-game-choice-switch')
 wait('document.querySelectorAll(".nl-game-choice-card").length===3')
 cards=read('[...document.querySelectorAll(".nl-game-choice-card")].map(e=>e.textContent)')
 check(any('Μοριακό παζλ' in c for c in cards),'third puzzle choice available',cards)
 click('.nl-game-choice-card:nth-child('+str({'repair':1,'builder':2,'puzzle':3}[game])+')')
 if game=='puzzle':pready()
 elif game=='builder':wait('!!document.querySelector(".nl-builder-frame").contentDocument?.querySelector("#bank-tiles button")',70)
 else:wait('!!document.querySelector(".diagram-image.is-ready")',70)
def pready():
 wait('!!document.querySelector(".nl-puzzle-frame")',70)
 wait('!!document.querySelector(".nl-puzzle-frame").contentDocument?.querySelector("#assembly-board[aria-busy=false]")||!!document.querySelector(".nl-builder-error")',70)
 check(not ev('!!document.querySelector(".nl-builder-error")'),'puzzle safely prepared',ev('document.querySelector(".nl-builder-error")?.textContent'))
 wait('!!document.querySelector(".nl-puzzle-frame").contentWindow.__puzzleLoad')
def footer(label,final=True):
 pause(.4)
 data=read('({buttons:[...document.querySelectorAll(".round-next button")].map(e=>e.textContent),header:[...document.querySelectorAll(".nl-quiz-dialog-header button")].map(e=>({text:e.textContent,hidden:e.hidden})),count:document.getElementById("nlQuizProgress").textContent})')
 check(len(data['buttons'])==(3 if final else 1),label+' footer action count',data)
 if final:check(all(e['hidden'] for e in data['header']),label+' final has no duplicate header action',data)
 return data
def target():
 load=pstate()['load'];mol=MOLS[load['moleculeId']]
 return fe('NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(mol)+')')
def build(graph,start=0):
 for node in graph['nodes'][start:]:fc('[data-hydrogens="'+str(node['hydrogens'])+'"]')
 ids=[n['id'] for n in pstate()['nodes']]
 check(len(ids)==len(graph['nodes']),'actual group inventory complete')
 mapping={n['id']:ids[i] for i,n in enumerate(graph['nodes'])}
 if graph['bonds']:
  if fe('document.getElementById("bond-tool").getAttribute("aria-pressed")')!='true':fc('#bond-tool')
  for edge in graph['bonds']:
   fc('[data-node-id="'+mapping[edge['a']]+'"]');fc('[data-node-id="'+mapping[edge['b']]+'"]')
 check(pstate()['bonds']==len(graph['bonds']),'actual carbon bonds complete')
 return ids
def solve(label,index,practice=False,partial=False,wrong=False):
 pready();before=pstate();load=before['load'];graph=target();original_count=read('document.getElementById("nlQuizProgress").textContent')
 check(original_count.endswith(str(load.get('roundIndex',0)+1)+'/3') if 'roundIndex' in load else '/3' in original_count,label+' visible counter',original_count)
 if wrong:
  fc('[data-hydrogens="0"]');fc('#check-answer')
  check(not pstate()['solved'] and not pstate()['feedbackHidden'],label+' actual incorrect construction rejected')
  check(not rec()['states'][str(index)]['solved'],label+' wrong response never unlocks')
  fc('#undo-action');check(len(pstate()['nodes'])==0,label+' actual undo retains recoverable attempt')
 if partial:
  fc('[data-hydrogens="'+str(graph['nodes'][0]['hydrogens'])+'"]');pause(.3)
  before_partial=pstate();storage_before=rec()
  call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();pready()
  restored=pstate()
  check(restored['nodes']==before_partial['nodes'] and restored['load']['moleculeId']==load['moleculeId'],label+' real reload restores exact partial groups and round')
  OUT['partialRestore']={'before':before_partial,'after':restored,'recordBefore':storage_before,'recordAfter':rec()}
  build(graph,1)
 else:build(graph)
 fc('#check-answer');wait('!!document.querySelector(".round-next button")')
 check(pstate()['solved'],label+' genuine construction accepted')
 snapshot=rec();game=snapshot['practices' if practice else 'states'][str(index)]['games']['puzzle']
 check(game['states'][game['currentRound']]['solved'],label+' parent independently accepted graph')
 OUT['rounds'].append({'label':label,'moleculeId':load['moleculeId'],'correctName':load['correctName'],'currentRound':game['currentRound'],'practice':practice,'state':game})
 print(json.dumps({'label':label,'moleculeId':load['moleculeId'],'currentRound':game['currentRound']}),flush=True)
 return load['moleculeId']
def shot(name):
 result=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/name).write_bytes(base64.b64decode(result['data']))
def viewport(w,h):call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});pause()
def gate_rounds(index,partial=False):
 ids=[]
 for i in range(3):
  ids.append(solve('gate'+str(index+1)+' round'+str(i+1),index,partial=partial and i==0,wrong=partial and i==0))
  footer('gate'+str(index+1)+' round'+str(i+1),i==2)
  check(read('document.getElementById("nlQuizProgress").textContent').endswith(str(i+1)+'/3'),'counter correct after round '+str(i+1))
  if i<2:
   check(not rec()['states'][str(index)]['solved'],'first/second correct alone remain locked');click('.round-next button:first-child');pready()
 check(len(set(ids))==3,'gate'+str(index+1)+' three different molecules',ids)
 check(rec()['states'][str(index)]['solved'] and rec()['states'][str(index)]['earned']['game']=='puzzle','gate'+str(index+1)+' unlock earned only after full puzzle triple')
 return ids
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
 def send_error(self,code,message=None,explain=None):
  OUT.setdefault('httpErrors',[]).append({'code':code,'path':self.path});super().send_error(code,message,explain)
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-puzzle-full-lesson-20261112-'));log=(HERE/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'serverPort':server.server_port,'bidiPort':port,'baseURL':f'http://127.0.0.1:{server.server_port}/'}
 print(json.dumps(OUT['process']),flush=True)
 deadline=time.monotonic()+25
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4):break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned BiDi endpoint unavailable')
   time.sleep(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['process']['baseURL']
 exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-puzzle-full-lesson-bidi','exec'))
 call('script.addPreloadScript',{'functionDeclaration':'''() => {window.__puzzleLoad=null;window.__puzzleMessages=[];addEventListener('message',e=>{if(e.data?.channel==='namelecule-puzzle-lesson-v1'){window.__puzzleMessages.push(e.data);if(e.data.command==='load')window.__puzzleLoad=e.data}})}'''})
 viewport(1440,1000);lesson(3,55);check(read('fScenarioPresent().index')==3,'cold lesson reaches first gate');check(ev('document.getElementById("scNext").disabled'),'cold first gate blocks continuation')
 open_gate();choose('repair');check(not rec()['states']['3']['solved'],'legacy Workshop remains accessible and not auto solved');choose('builder');check(not rec()['states']['3']['solved'],'legacy Builder remains accessible and independent');choose('puzzle')
 OUT['gate4IDs']=gate_rounds(3,True);shot('gate4-solved.png')
 earned=rec()['states']['3']['earned'];call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();check(rec()['states']['3']['earned']==earned and rec()['states']['3']['solved'],'cold solved reload reconstructs earned evidence');open_gate();pready();footer('restored required triple')
 click('.round-next button:nth-child(2)');pready();check('Προαιρετική' in read('document.getElementById("nlQuizDialogTitle").textContent'),'new optional puzzle triple opens');check(rec()['states']['3']['earned']==earned,'new optional practice preserves earned proof')
 optional=[]
 for i in range(3):
  optional.append(solve('optional gate4 round'+str(i+1),3,True));footer('optional round'+str(i+1),i==2)
  if i<2:click('.round-next button:first-child');pready()
 check(len(set(optional))==3,'optional triple contains three distinct structures',optional);check(rec()['states']['3']['earned']==earned,'completed optional triple preserves initial receipt');shot('optional-third-complete.png')
 click('.round-next button:nth-child(3)');wait('document.querySelectorAll(".nl-game-choice-card").length===3');check(rec()['states']['3']['earned']==earned,'other-game choice preserves earned proof')
 click('#nlQuizPracticeContinue');wait('fScenarioPresent().index===4');check(not ev('document.getElementById("nlQuizDialog").open'),'continue theory advances to step5 and closes dialog')
 for expected in range(5,11):
  pause(1);click('#scNext');wait('fScenarioPresent().index==='+str(expected));print('navigation reached step '+str(expected+1),flush=True)
 check(ev('document.getElementById("scNext").disabled'),'second gate blocks next independently');open_gate();choose('puzzle');OUT['gate11IDs']=gate_rounds(10);shot('gate11-solved.png')
 check(set(OUT['gate4IDs']).isdisjoint(OUT['gate11IDs']),'unbranched and branched gate inventories separate')
 check(set(OUT['gate11IDs'])=={'methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane'},'second gate includes all three approved branched structures')
 viewport(390,844);pause(.3);check(ev('document.documentElement.scrollWidth<=innerWidth'),'phone lesson no horizontal page overflow');check(fe('document.documentElement.scrollWidth<=innerWidth'),'phone puzzle no horizontal frame overflow');check(fe('!document.getElementById("instructions").open'),'phone instructions collapse');shot('phone-gate11-solved.png')
 click('.round-next button:first-child');wait('fScenarioPresent().index===11');check(not ev('document.getElementById("nlQuizDialog").open'),'third puzzle opens final step12')
 viewport(1440,1000);lesson(3,54);open_gate();choose('puzzle');check(fe('!!document.getElementById("target-name").textContent&&document.getElementById("assembly-board").getAttribute("aria-busy")==="false"'),'Main54 loads verified puzzle engine and target');shot('main54-third-game.png')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure.png')
 except Exception:pass
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[]);OUT['sourceAfter']=sha();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
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
