"""Prepared Developer replay; root must grant frozen-target and one browser slot.

Modes: detective-required, detective, old3-repair, old3-builder, old3-puzzle. Uses actual production
UI actions and read-only verified-engine oracles. No seed, answer, mission,
receipt, solved flag or bridge response is injected. Own loopback server,
temporary Firefox profile and PID only; user preview8013 stays untouched.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import base64, datetime, hashlib, http.server, json, os, shutil, socket
import subprocess, tempfile, threading, time, traceback, urllib.request

PROTOCOL_TIMEOUT = float(os.environ.get('NAMELECULE_FOUR_GAME_PROTOCOL_TIMEOUT','30'))
RUN_TIMEOUT = float(os.environ.get('NAMELECULE_FOUR_GAME_RUN_TIMEOUT','900'))
assert 0 < PROTOCOL_TIMEOUT <= 60 and 0 < RUN_TIMEOUT <= 1800, 'Bounded protocol/process deadlines required'
RUN_DEADLINE = time.monotonic() + RUN_TIMEOUT
def check_deadline(deadline=None):
 remaining=min(RUN_DEADLINE,deadline if deadline is not None else RUN_DEADLINE)-time.monotonic()
 if remaining<=0: raise TimeoutError('Absolute owned replay protocol/process deadline expired')
 return remaining
def bounded_bidi_source(source):
 # Continuous browser events must not keep an unanswered command alive.
 source=source.replace('seq=0;js_errors=[];all_events=[]','seq=0;js_errors=[];all_events=[];ACTIVE_PROTOCOL_DEADLINE=RUN_DEADLINE',1)
 source=source.replace('global seq\n seq+=1;', 'global seq, ACTIVE_PROTOCOL_DEADLINE\n ACTIVE_PROTOCOL_DEADLINE=min(RUN_DEADLINE,time.monotonic()+PROTOCOL_TIMEOUT)\n seq+=1;',1)
 source=source.replace('  part=s.recv(n-len(b))','  s.settimeout(check_deadline(ACTIVE_PROTOCOL_DEADLINE))\n  part=s.recv(n-len(b))',1)
 return source.replace('s.settimeout(60)','s.settimeout(PROTOCOL_TIMEOUT)',1)

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_FOUR_GAME_BROWSER_READY') == 'frozen', 'Root frozen-target/browser-slot grant required'
MANIFEST = Path(os.environ['NAMELECULE_FOUR_GAME_FROZEN_MANIFEST'])
FREEZE = json.loads(MANIFEST.read_text())
FROZEN = {p:(v if isinstance(v,str) else v.get('sha256',v.get('SHA256'))) for p,v in FREEZE['files'].items()}
MODE = os.environ.get('NAMELECULE_FOUR_GAME_REPLAY_MODE','detective')
assert MODE in ['detective-required','detective','old3-repair','old3-builder','old3-puzzle'], 'Unsupported bounded replay mode'
GAME = MODE.removeprefix('old3-') if MODE.startswith('old3-') else 'detective'
CONTINUE_INPUT = os.environ.get('NAMELECULE_FOUR_GAME_CONTINUE_INPUT','keyboard')
assert CONTINUE_INPUT in ['keyboard','pointer'], 'Unsupported Continue input mode'
PRIOR = HERE.parent/'before'
SOURCES = set(FROZEN) | {'mulermoc-nom-57.html','scenarios/alkanes-user-3.scenario.json',
 'js/namelecule-game-choice-checkpoint.js','js/namelecule-molecular-detective-lesson.js',
 'js/namelecule-quiz-checkpoints.js','js/namelecule-generated-repair-checkpoint.js',
 'js/namelecule-molecular-detective.js','js/namelecule-molecular-detective-engine.js',
 'js/namelecule-molecular-detective-host.js','games/molecular-detective.html','games/molecular-detective-viewer.html',
 'games/data/alkane-structures.json','js/namelecule-chemistry-client.js','js/namelecule-chemistry-worker.js',
 'js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js',
 'js/mulermoc-nom-core-55.js','js/mulermoc-nom-core-56.js','js/mulermoc-nom-core-57.js',
 'js/mulermoc-nom-molview-56.js','js/mulermoc-nom-teaching-56.js','js/mulermoc-nom-scenario-57.js',
 'games/name-builder.html','games/molecular-puzzle.html','js/namelecule-name-builder.js','js/namelecule-molecular-puzzle.js'}
HYDRATION_PACK=json.loads((ROOT/'data/namelecule-alkanes-v1/manifest.json').read_text())
SOURCES.update({'js/MULERMOC_namelecule_alkanes_v1_data.js','data/namelecule-alkanes-v1/manifest.json',
 'js/jsme-nick-nomeclature-moc2-data_55.js','js/jsme-nick-nomeclature-moc2-data_56.js','js/jsme-nick-nomeclature-moc2-data_57.js'})
for molecule in HYDRATION_PACK['molecules']: SOURCES.update(molecule['files'].values())
if MODE.startswith('old3-'):
 for item in ['js/namelecule-game-choice-checkpoint.js','scenarios/alkanes-user-3.scenario.json']:
  assert (PRIOR/item).is_file(), 'Exact archived prior composite/scenario required'
  SOURCES.add(str((PRIOR/item).relative_to(ROOT)))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def hashes(): return {p:sha(ROOT/p) for p in sorted(SOURCES)}
assert FROZEN and all(sha(ROOT/p)==v for p,v in FROZEN.items()), 'Frozen target drift before browser'
DEST = HERE/('run-'+MODE+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'))
DEST.mkdir(exist_ok=False)
OUT = {'role':'Developer browser execution; not independent review','mode':MODE,'continueInput':CONTINUE_INPUT,'checks':[],'correctUIAttempts':[],
 'sourceBefore':hashes(),'manifest':str(MANIFEST),'manifestSHA256':sha(MANIFEST),'harnessSHA256':sha(Path(__file__)),
 'helperSHA256':sha(HERE/'legacy-solve-helpers.py'),
 'scope':'Both actual Detective lesson gates, genuine raw native SVG picks and production Check; partial/earned reload, optional/switch flow, resize. Separate modes create genuine archived three-game partial/earned records before exact migration.',
 'limits':['Isolated headless Firefox CSS emulation; physical mobile/personal Firefox/conference/offline reliability unqualified.',
 'JSmol j2s/fonts/services remain external dependencies. No exhaustive84 seeded triples.',
 'Checkpoint Continue uses trusted keyboard Enter after DOM focus preparation; pointer Continue remains unqualified after the retained Firefox RemoteAgent actor/timeout failure.',
 'Lesson reset has no observed visible control; current/reset-wins are primarily covered by root memory checks. No programmatic reset is performed by default.']}
MOLS = {m['id']:m['mol'] for m in json.loads((ROOT/'games/data/alkane-structures.json').read_text())['molecules']}
server = firefox = log = profile = None

def check(ok,label,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 if not ok: raise AssertionError((label,detail))
 print('PASS '+label,flush=True)
def read(expr): return json.loads(ev('JSON.stringify('+expr+')'))
def pause(seconds=.15): time.sleep(seconds)
def wait(expr,seconds=90):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  check_deadline()
  if ev(expr): return
  pause(.15)
 raise AssertionError('Timed out: '+expr)
def page(path):
 call('browsingContext.navigate',{'context':ctx,'url':OUT['process']['baseURL']+path,'wait':'none'})
 wait('document.readyState!=="loading"');call('browsingContext.activate',{'context':ctx})
def shot(name):
 item=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(DEST/(name+'.png')).write_bytes(base64.b64decode(item['data']))
def viewport(width,height=1000):
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});pause(.3)
def pointer(point,label):
 surface=read('({w:innerWidth,h:innerHeight})')
 check(point['hit'] and 0<=point['x']<surface['w'] and 0<=point['y']<surface['h'],'trusted visible input '+label,point)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'four-game-lesson-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':point['x'],'y':point['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});pause()
def clickel(expr):
 for _ in range(12):
  ev('('+expr+').scrollIntoView({block:"center",inline:"nearest",behavior:"instant"});true');pause(.2)
  q=read('''(()=>{const e=EXPR,r=e.getBoundingClientRect();let x=r.x+r.width/2,y=r.y+r.height/2,w=e.ownerDocument.defaultView,hit=e.contains(w.document.elementFromPoint(x,y));while(w!==window){const f=w.frameElement,b=f.getBoundingClientRect();x+=b.x;y+=b.y;w=w.parent;hit=hit&&w.document.elementFromPoint(x,y)===f}const d=document.getElementById('nlQuizDialog'),h=d?.open?d.querySelector('.nl-quiz-dialog-header').getBoundingClientRect():null;return{x:Math.round(x),y:Math.round(y),hit,disabled:!!e.disabled,headerAction:!!e.closest('.nl-quiz-dialog-header'),headerBottom:h?.bottom??0,dialogBottom:d?.open?d.getBoundingClientRect().bottom:innerHeight}})()'''.replace('EXPR',expr))
  if q['disabled']: raise AssertionError(('Disabled UI action',expr,q))
  if q['hit'] and (q['y']>=q['headerBottom']+5 or q['headerAction'] or 'scNext' in expr): break
  if q['y']<q['headerBottom']+10: ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['headerBottom']-25)+',behavior:"instant"});true')
  elif q['y']>q['dialogBottom']-10: ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['dialogBottom']+25)+',behavior:"instant"});true')
 else: raise AssertionError(('Harness has no visible hit point',expr,q))
 pointer(q,expr)
def click(selector): clickel('document.querySelector('+json.dumps(selector)+')')
def activate_button(selector):
 if CONTINUE_INPUT=='pointer': click(selector);return
 # Focus/scroll are input preparation only. Enter is trusted BiDi keyboard
 # input; no HTMLElement.click(), application callback or state setter runs.
 expression='document.querySelector('+json.dumps(selector)+')'
 ev('('+expression+').scrollIntoView({block:"center",behavior:"instant"});('+expression+').focus({preventScroll:true});true');pause(.2)
 check(read('(()=>{const e='+expression+';return !!e&&document.activeElement===e&&!e.disabled&&getComputedStyle(e).display!=="none"})()'),'keyboard Continue focused and enabled '+selector)
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'four-game-lesson-keyboard','actions':[{'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]});pause(.15)
def frame_read(kind,expr): return read('document.querySelector(".nl-'+kind+'-frame").contentWindow.eval('+json.dumps(expr)+')')
def frame_click(kind,selector): clickel('document.querySelector(".nl-'+kind+'-frame").contentDocument.querySelector('+json.dumps(selector)+')')
def ready():
 wait('typeof jsmeNomeclatureApplet!=="undefined"&&!!jsmeNomeclatureApplet&&typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',110)
def rec():
 return read('(()=>{const s=fScenarioPresent(),c=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});return Object.values(sessionStorage).map(v=>{try{return JSON.parse(v)}catch(e){return null}}).find(v=>v?.content===c)??null})()')
def game_state(index,practice=False): return rec()['practices' if practice else 'states'][str(index)]['games'][GAME]
def lesson(prior=False,index=0):
 page(('__prior__/' if prior else '')+'mulermoc-nom-57.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step='+str(index+1));ready()
def open_gate():
 wait('!!document.getElementById("nlQuizOpen")&&!document.getElementById("nlQuizOpen").disabled');click('#nlQuizOpen');wait('document.getElementById("nlQuizDialog").open')
def game_ready(game=GAME):
 if game=='repair': wait('!!document.querySelector(".diagram-image.is-ready")');return
 if game=='detective':
  wait('!!document.querySelector(".nl-detective-frame")?.contentWindow?.NameleculeMolecularDetective&&document.querySelector(".nl-detective-frame").contentWindow.NameleculeMolecularDetective.snapshot().phase==="active"&&document.querySelector(".nl-detective-frame").parentElement.parentElement.getAttribute("aria-busy")!=="true"',110)
 else:
  wait('!!document.querySelector(".nl-'+game+'-frame")?.contentDocument?.querySelector('+json.dumps('#assembly-board[aria-busy=false]' if game=='puzzle' else '#bank-tiles button')+')',110)
  wait('!!document.querySelector(".nl-'+game+'-frame").contentWindow.'+('__puzzleLoad' if game=='puzzle' else '__lessonLoad'))
def choose(game=GAME,expected=4):
 if ev('!!document.querySelector(".nl-game-choice-switch")'): click('.nl-game-choice-switch')
 wait('document.querySelectorAll(".nl-game-choice-card").length==='+str(expected))
 check(read('document.querySelectorAll(".nl-game-choice-card").length')==expected,'exact '+str(expected)+' game choices')
 click('.nl-game-choice-card:nth-child('+str({'repair':1,'builder':2,'puzzle':3,'detective':4}[game])+')');game_ready(game)
def footer(label,final):
 data=read('({buttons:[...document.querySelectorAll(".round-next button")].map(e=>e.textContent),header:[...document.querySelectorAll(".nl-quiz-dialog-header button")].map(e=>({text:e.textContent,hidden:e.hidden})),count:document.getElementById("nlQuizProgress").textContent})')
 check(len(data['buttons'])==(3 if final else 1),label+' expected footer',data)
 if final: check(all(item['hidden'] for item in data['header']),label+' no duplicate final header actions',data)
def reload_gate():
 call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready()
def ds(): return frame_read('detective','NameleculeMolecularDetective.snapshot()')
def oracle(index,practice=False):
 state=game_state(index,practice)
 expression='''(async()=>{const c=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput();return JSON.stringify(NameleculeMolecularDetectiveLesson.getSet(fScenarioPresent().steps[INDEX].checkpoint.round,SEED,c,PRACTICE).rounds[ROUND])})()'''
 return json.loads(ev(expression.replace('INDEX',str(index)).replace('SEED',json.dumps(state['seed'])).replace('PRACTICE','true' if practice else 'false').replace('ROUND',str(state['currentRound']))))
def detective_pick(kind,target,expected=True):
 outer='document.querySelector(".nl-detective-frame")'
 native=outer+'.contentDocument.getElementById("molecule-viewer")'
 ev(native+'.scrollIntoView({block:"center",behavior:"instant"});true');pause(.2)
 expression='''(()=>{const f=NATIVE,w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg');let a;if(KIND==='atoms'){a=g.anchors.find(a=>a.atom+1===TARGET);if(!a){const i=g.vassign.findIndex(a=>a+1===TARGET);a=g.verts[i]}}else{const b=g.groups.find(b=>b.bond+1===TARGET),l=b?.rep||b?.lines[0];if(l)a={x:(l.x1+l.x2)/2,y:(l.y1+l.y2)/2}}if(!a)throw Error('Missing native target geometry');const p=svg.createSVGPoint();p.x=a.x;p.y=a.y;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM());let x=s.x,y=s.y,v=w,hit=true;while(v!==window){const frame=v.frameElement,r=frame.getBoundingClientRect();x+=r.x;y+=r.y;v=v.parent;hit=hit&&v.document.elementFromPoint(x,y)===frame}return{x:Math.round(x),y:Math.round(y),hit,target:TARGET,kind:KIND}})()'''
 q=read(expression.replace('NATIVE',native).replace('KIND',json.dumps(kind)).replace('TARGET',str(target)))
 before=ds()['selectionRevision'];pointer(q,'native '+kind+str(target));wait('document.querySelector(".nl-detective-frame").contentWindow.NameleculeMolecularDetective.snapshot().selectionRevision>'+str(before),10)
 check((target in ds()[kind])==expected,'native raw ID '+('selected' if expected else 'blocked for wrong kind'),{'target':target,'actual':ds()[kind]})
def dsolve(label,index,practice=False,partial=False):
 entry=oracle(index,practice);mission=entry['mission'];snapshot=entry['snapshot'];state=ds()
 if 'native56Hydration' not in OUT:
  native='document.querySelector(".nl-detective-frame").contentDocument.getElementById("molecule-viewer").contentWindow'
  expression='({entries:Object.keys(nameExamples).length,expanded:Object.keys(nameExamples).filter(id=>!!nameExamples[id].structure2D_Expanded).length,customs:Object.fromEntries(Object.keys(window.nameExamplesCustom||{}).map(id=>[id,{condensed:!!nameExamples[id]?.structure2D_Condensed,expanded:!!nameExamples[id]?.structure2D_Expanded,skeletal:!!nameExamples[id]?.structure2D_Skeletal,file3D:nameExamples[id]?.file3D,sameOwner:nameExamples[id]===window.nameExamplesCustom[id]}]))})'
  actual=read(native+'.eval('+json.dumps(expression)+')');OUT['native56Hydration']=actual
  check(actual['entries']==147 and actual['expanded']==147 and len(actual['customs'])==6,label+' actual native56 all147 forms available')
  for molecule in HYDRATION_PACK['molecules']:
   record=actual['customs'][molecule['id']]
   check(record['condensed'] and record['expanded'] and record['skeletal'] and record['sameOwner'] and record['file3D']==molecule['files']['sdf'],label+' native56 custom forms and exact SDF source '+molecule['id'])
 check(state['moleculeId']==snapshot['moleculeId'] and state['missionId']==mission['id'],label+' canonical assigned mission')
 check(not state['atoms'] and not state['bonds'],label+' new round selection empty')
 check(frame_read('detective','getComputedStyle(document.getElementById("molecule-select")).display')=='none',label+' controlled molecule picker hidden')
 frame_click('detective','#check-answer');check(not ds()['correct'],label+' empty rejected')
 wrongkind='bonds' if mission['kind']=='atoms' else 'atoms'
 detective_pick(wrongkind,1,False);check(not ds()['atoms'] and not ds()['bonds'],label+' wrong kind leaves empty raw selection')
 if mission['kind']=='atoms': wrong=next(a['id'] for a in snapshot['atoms'] if a['element']=='H')
 else:
  atoms={a['id']:a for a in snapshot['atoms']};wrong=next(b['id'] for b in snapshot['bonds'] if atoms[b['a']]['element']=='H' or atoms[b['b']]['element']=='H')
 detective_pick(mission['kind'],wrong);frame_click('detective','#check-answer');check(not ds()['correct'],label+' H or C-H rejected')
 if partial:
  before=game_state(index,practice);raw=ds();reload_gate();after=game_state(index,practice)
  check(after==before and ds()['atoms']==raw['atoms'] and ds()['bonds']==raw['bonds'] and ds()['missionId']==raw['missionId'],label+' exact wrong partial IDs/seed/mission/attempt survives cold reload')
  OUT['partialRestore']={'before':before,'after':after,'rawBefore':raw,'rawAfter':ds()};shot(label.replace(' ','-')+'-partial-restored')
  viewport(390,844);game_ready();check(ds()['atoms']==raw['atoms'] and ds()['bonds']==raw['bonds'],label+' narrow resize retains partial native raw IDs');shot('gate4-partial-phone')
  viewport(1500,1000);game_ready()
 frame_click('detective','#clear-selection');wait('document.querySelector(".nl-detective-frame").contentWindow.NameleculeMolecularDetective.snapshot().atoms.length===0&&document.querySelector(".nl-detective-frame").contentWindow.NameleculeMolecularDetective.snapshot().bonds.length===0')
 target=mission['accepted'][-1]
 for i,identifier in enumerate(target):
  detective_pick(mission['kind'],identifier)
  if i==0 and len(target)>1: frame_click('detective','#check-answer');check(not ds()['correct'],label+' incomplete target rejected')
 frame_click('detective','#check-answer');wait('!!document.querySelector(".round-next button")')
 check(ds()['correct'] and game_state(index,practice)['states'][game_state(index,practice)['currentRound']]['solved'],label+' native production Check independently accepted by parent')
 check(frame_read('detective','document.querySelector("#feedback p")?.textContent??null')==mission['explanation'],label+' exact canonical chemical explanation visible')
 OUT['correctUIAttempts'].append({'label':label,'game':'detective','moleculeId':snapshot['moleculeId'],'missionId':mission['id'],'family':mission['family'],'acceptedAlternatives':len(mission['accepted']),'selected':target,'practice':practice})
 return snapshot['moleculeId']
def triple(index,practice=False,partial=False):
 ids=[]
 for i in range(3):
  label='detective gate'+str(index+1)+' round'+str(i+1)+(' practice' if practice else '')
  ids.append(dsolve(label,index,practice,partial and i==0));footer(label,i==2)
  check(read('document.getElementById("nlQuizProgress").textContent').endswith(str(i+1)+'/3'),label+' common counter')
  if not practice and i<2: check(not rec()['states'][str(index)]['solved'],label+' locked until three distinct molecules')
  if i<2: click('.round-next button:first-child');game_ready()
 check(len(set(ids))==3,'three distinct same-game molecules gate'+str(index+1),ids)
 return ids
def detective_replay(required_only=False):
 lesson();OUT['replayIndices']=[0]
 for index in range(1,4): pause(.9);click('#scNext');wait('fScenarioPresent().index==='+str(index));OUT['replayIndices'].append(index)
 check(ev('document.getElementById("scNext").disabled'),'cold gate4 locked')
 open_gate();choose();OUT['gate4IDs']=triple(3,partial=True);earned=rec()['states']['3']['earned'];shot('gate4-earned')
 reload_gate();check(rec()['states']['3']['earned']==earned and rec()['states']['3']['solved'],'earned gate4 exact revalidated reload');footer('restored gate4',True)
 if required_only:
  activate_button('.round-next button:first-child')
 else:
  click('.round-next button:nth-child(2)');game_ready();check('Προαιρετική' in read('document.getElementById("nlQuizDialogTitle").textContent'),'optional attempt explicit')
  OUT['optionalIDs']=triple(3,practice=True);check(rec()['states']['3']['earned']==earned,'optional triple retains required receipt')
  click('.round-next button:nth-child(3)');wait('document.querySelectorAll(".nl-game-choice-card").length===4')
  for game in ['repair','builder','puzzle']:
   choose(game);check(rec()['states']['3']['earned']==earned and rec()['practices']['3']['selected']==game,'other '+game+' retains earned access');shot('other-'+game)
   if game!='puzzle': click('.nl-game-choice-switch');wait('document.querySelectorAll(".nl-game-choice-card").length===4')
  activate_button('#nlQuizPracticeContinue')
 wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');OUT['replayIndices'].append(4)
 for index in range(5,11): pause(.9);click('#scNext');wait('fScenarioPresent().index==='+str(index));OUT['replayIndices'].append(index)
 check(ev('document.getElementById("scNext").disabled'),'gate11 independently locked')
 open_gate();choose();OUT['gate11IDs']=triple(10);earned11=rec()['states']['10']['earned'];shot('gate11-earned')
 reload_gate();check(rec()['states']['3']['earned']==earned and rec()['states']['10']['earned']==earned11,'both earned receipts cold revalidated')
 viewport(390,844);game_ready();check(ev('document.documentElement.scrollWidth<=innerWidth'),'narrow lesson no horizontal overflow');check(frame_read('detective','document.documentElement.scrollWidth<=innerWidth'),'narrow Detective no horizontal overflow')
 check(frame_read('detective','document.getElementById("molecule-viewer").contentWindow.NameleculeMolecularDetectiveHost.getSnapshot().moleculeId')==ds()['moleculeId'],'narrow resize retains actual native molecule/IDs');shot('gate11-earned-phone')
 activate_button('.round-next button:first-child');wait('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open');OUT['replayIndices'].append(11)
 check(OUT['replayIndices']==list(range(12)),'all12 lesson steps traversed with production Next')
 check(any(r['acceptedAlternatives']>1 and r['family']=='parent-chain' for r in OUT['correctUIAttempts']),'equivalent parent chain actually accepted')
 OUT['finalRecord']=rec();shot('step12')

# Reuse only the recorded solver functions, not that script's startup/cleanup.
exec(compile((HERE/'legacy-solve-helpers.py').read_text(),'recorded-v57-legacy-ui-answer-helpers','exec'))
def legacy_replay():
 # Current/old normalized records are obtained through real lesson rendering.
 # A fresh tab gives each case clean tab-scoped storage without deleting/injecting it.
 global ctx
 for case in ['partial','earned']:
  if case=='earned':
   prior_ctx=ctx;ctx=call('browsingContext.create',{'type':'tab'})['context'];call('browsingContext.close',{'context':prior_ctx});viewport(1500,1000)
  lesson(True,3);open_gate();choose(GAME,3)
  scripts=read('[...document.scripts].map(s=>s.src).filter(Boolean)')
  check(any('/__prior__/js/namelecule-game-choice-checkpoint.js' in p for p in scripts),'actual archived three-game composite loaded')
  if case=='partial':
   if GAME=='repair':
    rnd=rround(3,False)
    click('[id$="part-'+(rnd['targetPartId'] if rnd['kind']=='replace' else rnd['parts'][0]['id'])+'"]')
   elif GAME=='builder':
    load=frame_read('builder','__lessonLoad');bank=frame_read('builder','NameleculeNameBuilderEngine.createBank(__lessonLoad.round,{seed:__lessonLoad.bankSeed})');tile=next(t for t in bank if t['text']==load['round']['pieces'][0]['text']);frame_click('builder','#bank-tiles [data-tile-id='+json.dumps(tile['id'])+']')
   else:
    load=frame_read('puzzle','__puzzleLoad');graph=frame_read('puzzle','NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(MOLS[load['moleculeId']])+')');frame_click('puzzle','[data-hydrogens="'+str(graph['nodes'][0]['hydrogens'])+'"]')
   pause(.3);before=game_state(3);oldrecord=rec();lesson(False,3);open_gate();game_ready();after=game_state(3)
   check(after==before,'old3 '+GAME+' exact partial migration seed/round/raw state');check(not rec()['states']['3']['solved'],'old partial does not unlock')
   OUT['legacyPartial']={'before':before,'after':after,'oldRecord':oldrecord,'newRecord':rec()};shot('old3-'+GAME+'-partial-migrated')
   # Revisit genuine old code and submit its first answer. The already-present
   # current record must win when returning; the old key is never rescanned.
   lesson(True,3);open_gate();game_ready()
   if GAME=='repair':
    rnd=rround(3,False)
    if rnd['kind']=='replace': click('[id$="choice-0"]')
    else: click('[id$="move-right"]')
   elif GAME=='builder':
    frame_click('builder','#bank-tiles button')
   else: frame_click('puzzle','[data-hydrogens="4"]')
   pause(.3);check(game_state(3)!=before,'genuine archived '+GAME+' partial changed after migration')
   lesson(False,3);open_gate();game_ready();check(game_state(3)==after,'present current progress wins over later old-key changes')
  else:
   ids=[]
   for index in range(3):
    if index: click('.round-next button:first-child');game_ready()
    mid,_={'repair':rsolve,'builder':bsolve,'puzzle':psolve}[GAME]('actual old3 '+GAME+' round'+str(index+1),3,False,False);ids.append(mid)
    OUT['correctUIAttempts'].append({'game':GAME,'case':'old3-earned','moleculeId':mid,'round':index})
   check(len(set(ids))==3 and rec()['states']['3']['solved'],'old three-game UI genuinely earns distinct complete triple')
   earned=rec()['states']['3']['earned'];before=rec();lesson(False,4)
   check(read('fScenarioPresent().index')==4 and rec()['states']['3']['earned']==earned,'old3 '+GAME+' exact earned receipt migrates and permits step5')
   OUT['legacyEarned']={'before':before,'after':rec(),'ids':ids};shot('old3-'+GAME+'-earned-migrated')

class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a): pass
 def send_error(self,code,message=None,explain=None):
  OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)
 def translate_path(self,url):
  requested=unquote(urlsplit(url).path)
  if requested.startswith('/__prior__/'):
   relative=Path(requested.removeprefix('/__prior__/'))
   if relative.is_absolute() or '..' in relative.parts: raise ValueError('Unsafe prior alias')
   archive=PRIOR/relative
   return str(archive if archive.is_file() else ROOT/relative)
  return super().translate_path(url)

try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket() as probe: probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-four-game-lesson-',dir='/private/tmp'));log=(DEST/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--width','1800','--height','1400','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,MOZ_HEADLESS_WIDTH='1800',MOZ_HEADLESS_HEIGHT='1400'))
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'bidiPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
 deadline=time.monotonic()+30
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4): break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Owned BiDi endpoint unavailable')
   pause(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['process']['baseURL']
 exec(compile(bounded_bidi_source((ROOT/'tools/namelecule_bidi.py').read_text()),'owned-four-game-lesson-bidi','exec'))
 call('session.subscribe',{'events':['network.beforeRequestSent','network.responseCompleted','network.fetchError'],'contexts':[ctx]})
 call('script.addPreloadScript',{'functionDeclaration':'''()=>{window.__lessonMessages=[];addEventListener('message',e=>{if(e.origin!==location.origin)return;const d=e.data;if(d?.channel==='namelecule-builder-lesson-v1'&&d.command==='load')window.__lessonLoad=d;if(d?.channel==='namelecule-puzzle-lesson-v1'&&d.command==='load')window.__puzzleLoad=d;if(d?.channel==='namelecule-detective-lesson-v1')window.__lessonMessages.push(d);});}'''})
 OUT['servedSHA256']={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p).read()).hexdigest() for p in sorted(SOURCES)}
 check(OUT['servedSHA256']==OUT['sourceBefore'],'HTTP exact frozen/application source bytes')
 if MODE.startswith('old3-'):
  for item in ['js/namelecule-game-choice-checkpoint.js','scenarios/alkanes-user-3.scenario.json']:
   check(hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+'__prior__/'+item).read()).hexdigest()==sha(PRIOR/item),'prior alias serves exact archived '+item)
 viewport(1500,1000);OUT['inputSurface']=read('({innerWidth,innerHeight,outerWidth,outerHeight})')
 check(OUT['inputSurface']['outerWidth']>=1500 and OUT['inputSurface']['outerHeight']>=1000,'physical1800x1400 supports CSS1500x1000',OUT['inputSurface'])
 if MODE.startswith('detective'): detective_replay(MODE=='detective-required')
 else: legacy_replay()
 check(not js_errors,'no captured JavaScript exceptions',js_errors);OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try: OUT['failureState']={'url':read('location.href'),'body':read('document.body.innerText.slice(-10000)'),'record':rec(),'messages':read('window.__lessonMessages??null')};shot('failure')
 except Exception as capture: OUT['failureCaptureError']=repr(capture)
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[])
 OUT['networkErrors']=[e for e in globals().get('all_events',[]) if e.get('method')=='network.fetchError']
 OUT['sourceAfter']=hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
 if firefox is not None and firefox.poll() is None:
  firefox.terminate()
  try: firefox.wait(timeout=10)
  except subprocess.TimeoutExpired: firefox.kill();firefox.wait(timeout=10)
 if server: server.shutdown();server.server_close()
 if log: log.close()
 OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None;OUT['ownedServerClosed']=server is None or server.fileno()==-1
 if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith('namelecule-four-game-lesson-') and not profile.is_symlink(): shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
 OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':OUT.get('completed',False),'mode':MODE,'checks':len(OUT['checks']),'correctUIAttempts':len(OUT['correctUIAttempts']),'JSexceptions':len(OUT['javascriptErrors']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'): raise SystemExit(1)
