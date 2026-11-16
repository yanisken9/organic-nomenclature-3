"""Prepared bounded Developer browser acceptance; main() owns all side effects.

Prepare/check: python3 .../browser/replay-levels.py --prepare-check
Run only after root freezes product and grants the ONE browser slot:
 NAMELECULE_LEVELS_BROWSER_GRANT=frozen NAMELECULE_LEVELS_FROZEN_MANIFEST=/abs/manifest.json \
 python3 .../browser/replay-levels.py --engine chrome --mode standalone-builder

Uses genuine pointer/keyboard production controls and read-only engine, native
DOM and stored-progress oracles. Never writes app progress/seeds/receipts, sends
bridge replies, calls app handlers or changes browser security preferences.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote, urlparse
import argparse, ast, base64, datetime, hashlib, http.server, json, os, shutil, socket
import struct, subprocess, tempfile, threading, time, traceback, urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRIOR = HERE.parent/'before'
RECORDED = ROOT/'docs/checks/four-game-integration-20261116/lesson-browser'
OWNED_PREFIX = 'namelecule-levels-browser-'
PROTOCOL_TIMEOUT = 30
RUN_TIMEOUT = 1200
CONTINUE_INPUT = 'pointer'
CACHE_COMMON = {'js/namelecule-game-repair.js', 'js/namelecule-generated-repair-checkpoint.js', 'js/namelecule-game-choice-checkpoint.js'}
CACHE_VARIANTS = {
 'old':dict.fromkeys(CACHE_COMMON,'old'), 'new':dict.fromkeys(CACHE_COMMON,'new'),
 'mix-a':{'js/namelecule-game-repair.js':'new','js/namelecule-generated-repair-checkpoint.js':'old','js/namelecule-game-choice-checkpoint.js':'new'},
 'mix-b':{'js/namelecule-game-repair.js':'old','js/namelecule-generated-repair-checkpoint.js':'new','js/namelecule-game-choice-checkpoint.js':'old'}}
BASE_SOURCES = {
 'mulermoc-nom-55.html','mulermoc-nom-56.html','mulermoc-nom-57.html',
 'games/name-builder-viewer.html','games/molecular-detective-viewer.html',
 'js/namelecule-name-builder-host.js','js/namelecule-molecular-detective-host.js',
 'js/namelecule-name-builder-engine.js','js/namelecule-molecular-puzzle-engine.js',
 'js/namelecule-repair-generator.js','js/namelecule-quiz-checkpoints.js',
 'js/namelecule-chemistry-client.js','js/namelecule-chemistry-worker.js',
 'js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js',
 'games/data/alkane-structures.json','games/data/alkane-structures-v2.json',
 'js/mulermoc-nom-core-55.js','js/mulermoc-nom-core-56.js','js/mulermoc-nom-core-57.js',
 'js/mulermoc-nom-molview-56.js','js/mulermoc-nom-scenario-57.js',
 'js/MULERMOC_namelecule_alkanes_v1_data.js','data/namelecule-alkanes-v1/manifest.json'}

def load_functions(filename, names, include_classes=()):
 tree = ast.parse(filename.read_text())
 selected = [node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names or isinstance(node,ast.ClassDef) and node.name in include_classes]
 assert {node.name for node in selected} == set(names)|set(include_classes), ('Recorded helper seam changed',filename)
 class BoundLocalHTTP(ast.NodeTransformer):
  def visit_Call(self,node):
   self.generic_visit(node)
   if isinstance(node.func,ast.Attribute) and node.func.attr=='urlopen' and not any(k.arg=='timeout' for k in node.keywords):node.keywords.append(ast.keyword(arg='timeout',value=ast.parse('min(30,check_deadline())',mode='eval').body))
   return node
 module=BoundLocalHTTP().visit(ast.Module(body=selected,type_ignores=[]));ast.fix_missing_locations(module)
 exec(compile(module,str(filename),'exec'),globals())

# AST imports execute definitions only, excluding the archived runners' startup,
# filesystem writes, environment grants and original scenario assertions.
COMMON_NAMES = {'check_deadline','bounded_bidi_source','sha','hashes','check','read','pause','wait','page','shot','viewport','pointer','clickel','click','activate_button','frame_read','frame_click','ready','rec','open_gate'}
load_functions(RECORDED/'replay-detective.py', COMMON_NAMES)

def parse_args():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--prepare-check',action='store_true')
 parser.add_argument('--engine',choices=['chrome','firefox'],default='chrome')
 parser.add_argument('--mode',choices=['standalone-builder','standalone-puzzle','standalone-detective','standalone-repair','lesson-required-builder','lesson-required-puzzle','lesson-required-detective','lesson-required-repair','lesson-optional-detective','native-cache','legacy-migration'],default='standalone-builder')
 parser.add_argument('--timeout',type=int,default=1200)
 parser.add_argument('--cache-variants',default='old,new')
 return parser.parse_args()

class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a): pass
 def send_error(self,code,message=None,explain=None):
  OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)
 def translate_path(self,url):
  requested=unquote(urlsplit(url).path)
  if requested.startswith('/__cache__/'):
   pieces=requested.removeprefix('/__cache__/').split('/',1)
   assert len(pieces)==2 and pieces[0] in CACHE_VARIANTS, 'Unknown fixed cache version'
   variant,relative=pieces[0],Path(pieces[1])
   assert not relative.is_absolute() and '..' not in relative.parts,'Unsafe cache alias'
   archive = PRIOR/relative
   # Both aliases use the recorded exact v1 lesson. Only the three shared JS
   # inputs vary; viewer/native/source/pure-engine files remain current bytes.
   previous = str(relative)=='scenarios/alkanes-user-3.scenario.json' or str(relative) in CACHE_COMMON and CACHE_VARIANTS[variant][str(relative)]=='old'
   return str(archive if previous else ROOT/relative)
  return super().translate_path(url)

def window_expr(game,controlled):
 return 'document.querySelector(".nl-'+game+'-frame")?.contentWindow' if controlled else 'window'
def game_read(game,expr,controlled=False):
 return read('('+window_expr(game,controlled)+').eval('+json.dumps(expr)+')')
def game_click(game,selector,controlled=False):
 if controlled: frame_click(game,selector)
 else: click(selector)
def game_ready(game,controlled=False):
 w=window_expr(game,controlled)
 if game=='repair': wait('!!document.querySelector(".diagram-image.is-ready")',110);return
 if controlled:wait('!!('+w+')',110)
 if game=='detective': wait('('+w+').NameleculeMolecularDetective?.snapshot().phase==="active"',110)
 elif game=='builder': wait('('+w+').document.getElementById("viewer-mask").hidden&&!!('+w+').document.querySelector("#bank-tiles button")',110)
 else: wait('('+w+').document.getElementById("assembly-board").getAttribute("aria-busy")==="false"',110)
 if controlled and game in ['builder','puzzle']:
  wait('!!('+w+').'+('__lessonLoad' if game=='builder' else '__puzzleLoad'),110)

def select_level(level,controlled=False):
 selector=('#nlQuizDialog ' if controlled else '')+'[data-level="'+str(level)+'"]'
 if ev('!!document.querySelector('+json.dumps(selector)+')'):
  click(selector)
 elif controlled:
  check(level==1 and gate_state()['selectedLevel']==1,'single level1 shown without redundant selector')
 else: raise AssertionError('Standalone level selector missing')

def builder_info(controlled=False):
 native='document.getElementById("molecule-viewer").contentWindow'
 return game_read('builder','(()=>{const w='+native+';return {...w.NameleculeNameBuilderHost.serializeName(),native:w.NameleculeNameBuilderHost.snapshot(),answer:[...document.querySelectorAll("#answer-tiles button")].map(e=>({id:e.dataset.tileId,text:e.textContent})),bank:[...document.querySelectorAll("#bank-tiles button")].map(e=>({id:e.dataset.tileId,text:e.textContent})),solved:document.getElementById("feedback").classList.contains("success")}})()',controlled)

def solve_builder(label,controlled=False,partial=False):
 info=builder_info(controlled);already=len(info['answer']);used=set(n['id'] for n in info['answer'])
 for piece in info['pieces'][already:]:
  info_now=builder_info(controlled)
  tile=next(t for t in info_now['bank'] if t['id'] not in used and t['text']==piece['text']);used.add(tile['id'])
  game_click('builder','#bank-tiles [data-tile-id='+json.dumps(tile['id'])+']',controlled)
  if partial: return info['native']['selectedMol']
 check(game_read('builder','document.getElementById("candidate-name").textContent',controlled)==info['correctName'],label+' exact native composed name')
 game_click('builder','#check-answer',controlled)
 wait('('+window_expr('builder',controlled)+').document.getElementById("feedback").classList.contains("success")')
 OUT['correctUIAttempts'].append({'game':'builder','moleculeId':info['native']['selectedMol'],'label':label,'controlled':controlled})
 return info['native']['selectedMol']

def puzzle_info(controlled=False):
 return game_read('puzzle','({name:document.getElementById("target-name").textContent,nodes:[...document.querySelectorAll("#board-nodes button")].map(e=>({id:e.dataset.nodeId,label:e.textContent,left:e.style.left,top:e.style.top})),bonds:document.querySelectorAll("#board-svg .puzzle-bond:not(.puzzle-bond-hit)").length,solved:document.querySelector("#feedback").classList.contains("success"),load:window.__puzzleLoad??null})',controlled)

def solve_puzzle(label,controlled=False,partial=False):
 info=puzzle_info(controlled);mid=info['load']['moleculeId'] if controlled else NAME_IDS[info['name']]
 graph=game_read('puzzle','NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(MOLS[mid])+')',controlled)
 start=len(info['nodes'])
 for node in graph['nodes'][start:]:
  game_click('puzzle','[data-hydrogens="'+str(node['hydrogens'])+'"]',controlled)
  if partial:return mid
 ids=[n['id'] for n in puzzle_info(controlled)['nodes']];mapping={n['id']:ids[i] for i,n in enumerate(graph['nodes'])}
 if graph['bonds']:
  if game_read('puzzle','document.getElementById("bond-tool").getAttribute("aria-pressed")',controlled)!='true':game_click('puzzle','#bond-tool',controlled)
  # Solvers are invoked on blank or one-node partial graphs only.
  for edge in graph['bonds']:
   game_click('puzzle','[data-node-id='+json.dumps(mapping[edge['a']])+']',controlled);game_click('puzzle','[data-node-id='+json.dumps(mapping[edge['b']])+']',controlled)
 check(puzzle_info(controlled)['bonds']==len(graph['bonds']),label+' actual complete C-C adjacency')
 game_click('puzzle','#check-answer',controlled);wait('('+window_expr('puzzle',controlled)+').document.getElementById("feedback").classList.contains("success")')
 OUT['correctUIAttempts'].append({'game':'puzzle','moleculeId':mid,'label':label,'controlled':controlled});return mid

def ds(controlled=True):return game_read('detective','NameleculeMolecularDetective.snapshot()',controlled)

def detective_oracle(controlled=False):
 return game_read('detective','(()=>{const s=NameleculeMolecularDetective.snapshot(),snapshot=document.getElementById("molecule-viewer").contentWindow.NameleculeMolecularDetectiveHost.getSnapshot();return{snapshot,mission:NameleculeMolecularDetectiveEngine.missions(snapshot).find(m=>m.id===s.missionId)}})()',controlled)

def detective_pick(kind,target,controlled=False):
 game=window_expr('detective',controlled);native='('+game+').document.getElementById("molecule-viewer")'
 ev(native+'.scrollIntoView({block:"center",behavior:"instant"});true');pause(.2)
 expression='''(()=>{const f=NATIVE,w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg');let a;if(KIND==='atoms'){a=g.anchors.find(a=>a.atom+1===TARGET);if(!a){const i=g.vassign.findIndex(a=>a+1===TARGET);a=g.verts[i]}}else{const b=g.groups.find(b=>b.bond+1===TARGET),l=b?.rep||b?.lines[0];if(l)a={x:(l.x1+l.x2)/2,y:(l.y1+l.y2)/2}}if(!a)throw Error('Missing native target geometry');const p=svg.createSVGPoint();p.x=a.x;p.y=a.y;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM());let x=s.x,y=s.y,v=w,hit=true;while(v!==window){const frame=v.frameElement,r=frame.getBoundingClientRect();x+=r.x;y+=r.y;v=v.parent;hit=hit&&v.document.elementFromPoint(x,y)===frame}return{x:Math.round(x),y:Math.round(y),hit,target:TARGET,kind:KIND}})()'''
 q=read(expression.replace('NATIVE',native).replace('KIND',json.dumps(kind)).replace('TARGET',str(target)))
 before=ds(controlled)['selectionRevision'];pointer(q,'native '+kind+str(target));wait('('+game+').NameleculeMolecularDetective.snapshot().selectionRevision>'+str(before),10)
 check(target in ds(controlled)[kind],'genuine native raw selection '+kind+'/'+str(target))

def solve_detective(label,controlled=False,partial=False):
 entry=detective_oracle(controlled);mission=entry['mission'];target=mission['accepted'][-1]
 current=ds(controlled);assert current['missionId']==mission['id']
 for identifier in target:
  if identifier not in current[mission['kind']]:detective_pick(mission['kind'],identifier,controlled)
  if partial:return current['moleculeId']
 game_click('detective','#check-answer',controlled);wait('('+window_expr('detective',controlled)+').NameleculeMolecularDetective.snapshot().correct')
 OUT['correctUIAttempts'].append({'game':'detective','moleculeId':current['moleculeId'],'missionId':mission['id'],'family':mission['family'],'acceptedAlternatives':len(mission['accepted']),'label':label,'controlled':controlled});return current['moleculeId']

def workshop_record():
 return read('(()=>{const level=sessionStorage.getItem("namelecule-repair-levels-v1-current");return JSON.parse(sessionStorage.getItem("namelecule-repair-levels-v1-"+level)||"null")})()')

def repair_oracle(controlled=False):
 if controlled:
  gate=gate_state()
  if gate.get('version')==2:
   entry=active_attempt('repair');context,progress=entry['context'],entry['progress'];seed=progress['seed'];round_index=progress['currentRound']
   prefix='const context='+json.dumps(context)+',base=fScenarioPresent().steps[fScenarioPresent().index].checkpoint.round,recipe=NameleculeGeneratedRepairCheckpoint.roundRecipe(base,context);const input=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(null,context.catalogRevision);const view=context.source==="enriched"?NameleculeGameLevels.createGenerationInput(input,context.level):input;'
   set_id='alkanes-unbranched' if context['level']==1 or context['source']=='legacy' and INDEX==3 else 'alkanes-branched'
  else:
   progress=gate['games']['repair'];seed=progress['seed'];round_index=progress['currentRound'];set_id='alkanes-unbranched' if INDEX==3 else 'alkanes-branched'
   prefix='const base=fScenarioPresent().steps[fScenarioPresent().index].checkpoint.round;const input=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(null,base.catalogRevision);const view=input;'
 else:
  state=workshop_record();seed=state['seed'];round_index=state['roundIndex'];set_id=state['setId']
  prefix='const input=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(null,"enriched");const view=NameleculeGameLevels.createGenerationInput(input,'+str(state['level'])+');'
 expression='(async()=>{'+prefix+'return NameleculeRepairGenerator.createGame(view.catalog,view.analyses,{seed:'+json.dumps(seed)+',difficulty:"basic"}).sets.find(s=>s.id==='+json.dumps(set_id)+').rounds['+str(round_index)+']})()'
 return json.loads(ev('(async()=>JSON.stringify(await '+expression+'))()'))

def solve_repair(label,controlled=False,partial=False):
 rnd=repair_oracle(controlled)
 if rnd['kind']=='replace':
  click('[id$="part-'+rnd['targetPartId']+'"]')
  if partial:return rnd['moleculeId']
  good=next(i for i,c in enumerate(rnd['choices']) if c['value']==rnd['correctValue']);click('[id$="choice-'+str(good)+'"]')
 else:
  for dest,pid in enumerate(rnd['correctOrder']):
   order=read('[...document.querySelectorAll(".part-button")].map(e=>e.id.split("part-")[1])');position=order.index(pid)
   if position>dest:
    click('[id$="part-'+pid+'"]')
    if partial:return rnd['moleculeId']
    for _ in range(position-dest):click('[id$="move-left"]')
 click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")')
 OUT['correctUIAttempts'].append({'game':'repair','moleculeId':rnd['moleculeId'],'kind':rnd['kind'],'label':label,'controlled':controlled});return rnd['moleculeId']
SOLVERS={'builder':solve_builder,'puzzle':solve_puzzle,'detective':solve_detective,'repair':solve_repair}

# V2 parent access is intentionally read-only. These helpers use the documented
# normalized record rather than creating synthetic receipts/progress.
def gate_state():
 record=rec();assert record is not None,'No genuine lesson record';return record['states'][str(INDEX)]
def active_attempt(game=None,level=None):
 gate=gate_state();game=game or gate['selected'];level=level if level is not None else gate['selectedLevel'];return gate['games'][game][str(level)]
def lesson(index=0,path='mulermoc-nom-57.html'):
 global INDEX
 INDEX=index;page(path+'?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step='+str(index+1));ready()
def choose(game,level=None):
 if ev('!!document.querySelector(".nl-game-choice-switch")'):click('.nl-game-choice-switch')
 wait('document.querySelectorAll(".nl-game-choice-card").length===4')
 click('.nl-game-choice-card:nth-child('+str({'repair':1,'builder':2,'puzzle':3,'detective':4}[game])+')')
 if level is not None:
  wait('!!document.querySelector("#nlQuizDialog [data-level]")')
  if gate_state()['selectedLevel']!=level:select_level(level,True)
 game_ready(game,True)
def next_round(game,controlled=False):
 if controlled:click('.round-next button:first-child');game_ready(game,True)
 elif game in ['builder','puzzle']:click('#next-molecule');game_ready(game)
 elif game=='detective':click('#next-mission');game_ready(game)
 else:click('.round-next button:first-child');game_ready(game)
def scoped_level(game,controlled=False):
 if game=='builder':mid=builder_info(controlled)['native']['selectedMol']
 elif game=='puzzle':mid=NAME_IDS[puzzle_info(controlled)['name']]
 elif game=='detective':mid=ds(controlled)['moleculeId']
 else:mid=repair_oracle(controlled)['moleculeId']
 return mid

def builder_modes():
 native='document.getElementById("molecule-viewer").contentWindow'
 mid=builder_info()['native']['selectedMol']
 for mode in ['condensed','expanded','skeletal','3d']:
  selector='[data-representation='+json.dumps(mode)+']'
  if read('document.querySelector('+json.dumps(selector)+').disabled'):
   OUT.setdefault('unavailableForms',[]).append({'moleculeId':mid,'mode':mode});continue
  click(selector);wait('document.querySelector('+json.dumps(selector)+').getAttribute("aria-pressed")==="true"&&document.getElementById("viewer-mask").hidden',110)
  check(builder_info()['native']['selectedMol']==mid,'Builder actual '+mode+' retains assigned level2 molecule')
  if mode=='3d':check(read(native+'.NameleculeNameBuilderHost.modelReady()'),'Builder actual3D single verified model ready')
 click('#zoom-in');click('#zoom-out');viewport(1200,900);game_ready('builder');viewport(1500,1000)
 click('[data-representation="condensed"]');game_ready('builder')

def practice_partial_restore(game):
 # L3 currently has a fresh unsolved refill assignment after its first full bag.
 mid=SOLVERS[game](game+' L3 partial before level switch',False,True)
 if game=='builder':before=builder_info()['answer']
 elif game=='puzzle':before=puzzle_info()['nodes']
 else:before={k:ds(False)[k] for k in ['moleculeId','missionId','atoms','bonds','attempts','submitted']}
 select_level(1);game_ready(game);select_level(3);game_ready(game)
 if game=='builder':after=builder_info()['answer']
 elif game=='puzzle':after=puzzle_info()['nodes']
 else:after={k:ds(False)[k] for k in before}
 check(scoped_level(game)==mid and before==after,game+' exact current-page partial restored after level switch')
 OUT.setdefault('partialRestores',[]).append({'game':game,'moleculeId':mid,'before':before,'after':after})

def standalone(game):
 page('games/'+{'builder':'name-builder','puzzle':'molecular-puzzle','detective':'molecular-detective','repair':'name-repair'}[game]+'.html?molecule=ethane&mission=parent-chain')
 wait('document.querySelectorAll("[data-level]").length===3',120)
 check(read('[...document.querySelectorAll("[data-level]")].map(e=>e.getAttribute("aria-pressed"))')==['false']*3,game+' explicit three-level choice before assignment')
 if game=='builder':check(read('document.getElementById("next-molecule").disabled&&!document.querySelector("#bank-tiles button")'),game+' no eager or URL assignment')
 if game=='puzzle':check(read('!document.querySelector("#round-select")&&document.getElementById("next-molecule").disabled'),game+' no molecule dropdown or eager assignment')
 if game=='detective':check(read('!document.querySelector("#molecule-select")&&!document.querySelector("#mission-select")&&NameleculeMolecularDetective.snapshot().moleculeId===null'),game+' automatic molecule/mission assignment only')
 for level,size in [(1,5),(2,4),(3,5)]:
  if game=='repair' and level>1:
   # Use the existing set-return control to reach the standalone level picker.
   button='[...document.querySelectorAll("button")].find(e=>e.textContent.includes("Επιστροφή στα σετ"))'
   clickel(button);wait('document.querySelectorAll("[data-level]").length===3')
  select_level(level);game_ready(game)
  count=3 if game=='repair' else size+1;assigned=[]
  for round_index in range(count):
   mid=scoped_level(game);assigned.append(mid)
   if game=='detective' and level>1:check(detective_oracle()['mission']['family']!='single-bonds','branched level excludes simple all-bonds mission')
   check(mid in BANDS[str(level)],game+' level'+str(level)+' assignment '+str(round_index+1),mid)
   if round_index==0:
    if game=='builder' and level==2:builder_modes()
    SOLVERS[game](game+' level'+str(level)+' genuine answer',False)
    viewport(390,844);game_ready(game);check(read('document.documentElement.scrollWidth<=innerWidth'),game+' narrow no page overflow');shot(game+'-level'+str(level)+'-narrow');viewport(1500,1000)
   elif game in ['repair','detective']:SOLVERS[game](game+' level'+str(level)+' round'+str(round_index+1),False)
   if round_index<count-1:next_round(game)
  if game=='repair':
   check(len(set(assigned))==3,'Workshop distinct same-level seeded triple '+str(level),assigned)
   click('.round-next button:first-child');wait('!!document.querySelector(".results")')
  else:
   check(len(set(assigned[:size]))==size and assigned[-1]!=assigned[-2],game+' complete bag and refill no immediate repeat level'+str(level),assigned)
  OUT.setdefault('assignedPools',[]).append({'game':game,'level':level,'ids':assigned})
 if game!='repair':
  if game=='detective':next_round(game)
  practice_partial_restore(game)
 else:
  before=workshop_record();call('browsingContext.reload',{'context':ctx,'wait':'none'});wait('!!document.querySelector(".results")',120);check(workshop_record()==before,'Workshop level3 complete attempt exact cold restore')
 if game in ['builder','detective']:
  clickel('[...document.querySelectorAll(".nl-game-levels__category")].find(e=>e.textContent.includes("Άλλες διαθέσιμες ενώσεις"))');game_ready(game)
  mid=scoped_level(game);check(mid not in ALL_IDS,game+' other-series automatic assignment retained',mid)
  SOLVERS[game](game+' other-series genuine answer',False)
 shot(game+'-final')

def triple(game,level):
 assigned=[]
 for round_index in range(3):
  assigned.append(SOLVERS[game]('lesson gate'+str(INDEX+1)+' '+game+' L'+str(level)+' round'+str(round_index+1),True))
  wait('!!document.querySelector(".round-next button")')
  check(active_attempt(game,level)['progress']['states'][round_index]['solved'],'parent regraded raw correct answer '+game+' L'+str(level))
  if round_index<2:next_round(game,True)
 check(len(set(assigned))==3 and all(mid in BANDS[str(level)] for mid in assigned),'lesson distinct compatible triple '+game+' L'+str(level),assigned)
 return assigned

def enter_gate11(game):
 global INDEX
 lesson();OUT['replayIndices']=[0]
 for index in range(1,4):pause(.4);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index;OUT['replayIndices'].append(index)
 check(read('document.getElementById("scNext").disabled'),'fresh gate4 locked')
 open_gate();choose(game,1)
 OUT['gate4IDs']=triple(game,1);gate4=gate_state();check(gate4['solved'] and bool(gate4['receipts']['1']),'gate4 own level1 receipt unlocks')
 shot(game+'-gate4-earned');activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');INDEX=4;OUT['replayIndices'].append(4)
 for index in range(5,11):pause(.4);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index;OUT['replayIndices'].append(index)
 check(read('document.getElementById("scNext").disabled'),'fresh gate11 independent locked')

def required_replay(game):
 global INDEX
 enter_gate11(game)
 open_gate();choose(game,1);OUT['gate11Level1IDs']=triple(game,1)
 check(not gate_state()['solved'] and bool(gate_state()['receipts']['1']) and not gate_state()['receipts'].get('2'),'gate11 level1 alone cannot unlock')
 # Level controls remain available after a completed compatible triple.
 select_level(2,True);game_ready(game,True);OUT['gate11Level2IDs']=triple(game,2)
 earned=gate_state()['receipts'];check(gate_state()['solved'] and bool(earned['1']) and bool(earned['2']),'gate11 independent level1 and2 receipts unlock')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready(game,True)
 check(gate_state()['receipts']==earned and gate_state()['solved'],'cold reload retains and revalidates separate earned level receipts')
 viewport(390,844);game_ready(game,True);check(read('document.documentElement.scrollWidth<=innerWidth'),'lesson narrow no page overflow');shot(game+'-gate11-restored-narrow');viewport(1500,1000)
 activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open');INDEX=11;OUT['replayIndices'].append(11)
 check(OUT['replayIndices']==list(range(12)),'all12 lesson steps and both actual Continue transitions')
 OUT['finalRecord']=rec();shot(game+'-step12')

def optional_replay():
 global INDEX
 enter_gate11('detective');open_gate();choose('detective',3);triple('detective',3)
 check(not gate_state()['solved'] and not gate_state()['receipts'].get('1') and not gate_state()['receipts'].get('2'),'optional level3 triple alone does not unlock required levels')
 shot('level3-optional-cannot-unlock')
 select_level(1,True);game_ready('detective',True);triple('detective',1)
 check(not gate_state()['solved'] and bool(gate_state()['receipts'].get('1')) and bool(gate_state()['receipts'].get('3')) and not gate_state()['receipts'].get('2'),'level1 plus optional3 still cannot replace required level2')
 choose('puzzle',2);triple('puzzle',2)
 earned=gate_state()['receipts'];check(gate_state()['solved'] and bool(earned['1']) and bool(earned['2']),'cross-game DetectiveL1/PuzzleL2 unlocks with separate complete receipts')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready('puzzle',True)
 check(gate_state()['receipts']==earned and gate_state()['solved'],'cross-game and optional earned receipts exact cold revalidation')
 viewport(390,844);game_ready('puzzle',True);check(frame_read('puzzle','document.documentElement.scrollWidth<=innerWidth'),'controlled Puzzle narrow no horizontal overflow');shot('cross-game-earned-Puzzle-narrow');viewport(1500,1000)
 activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open');INDEX=11
 check(True,'cross-game optional replay actual Continue reaches step12');OUT['finalRecord']=rec();shot('cross-game-optional-step12')

def controlled_detective_smoke():
 lesson(3);open_gate();choose('detective',1)
 solve_detective('final-cut controlled Detective partial',True,True)
 before=active_attempt('detective',1);raw_before={k:ds(True)[k] for k in ['moleculeId','missionId','atoms','bonds','attempts','submitted']}
 call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready('detective',True)
 after=active_attempt('detective',1);raw_after={k:ds(True)[k] for k in raw_before}
 check(before==after and raw_before==raw_after,'final-cut controlled Detector context/rawpartial exact cold restore')
 solve_detective('final-cut controlled Detective genuine restored Check',True)
 wait('!!document.querySelector(".round-next button")')
 check(active_attempt('detective',1)['progress']['states'][0]['solved'] and not gate_state()['solved'],'final-cut parent regrades restored answer without premature triple unlock')
 OUT['controlledDetectiveSmoke']={'before':before,'after':after,'rawBefore':raw_before,'rawAfter':raw_after}
 shot('final-cut-controlled-detective-partial-restored')

def native_cache(variants):
 global INDEX,ctx
 assert variants and len(set(variants))==len(variants) and all(v in CACHE_VARIANTS for v in variants),'Unsupported cache version selection'
 OUT['cacheAliases']={};OUT['cacheVariantSourceMap']={v:CACHE_VARIANTS[v] for v in variants}
 for variant in variants:
  OUT['cacheAliases'][variant]={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+'__cache__/'+variant+'/'+p,timeout=min(30,check_deadline())).read()).hexdigest() for p in sorted(CACHE_COMMON)}
  check(OUT['cacheAliases'][variant]=={p:sha(PRIOR/p if CACHE_VARIANTS[variant][p]=='old' else ROOT/p) for p in CACHE_COMMON},'exact fixed '+variant+' shared-JS cache bytes')
  for version,game in [(55,'builder'),(56,'detective')]:
   old_ctx=ctx;ctx=call('browsingContext.create',{'type':'tab'})['context'];call('browsingContext.close',{'context':old_ctx});viewport(1500,1000)
   lesson(3,'__cache__/'+variant+'/mulermoc-nom-'+str(version)+'.html');open_gate();choose(game)
   # These parents/embedded generated native hosts omit the level module; v1
   # remains functional with old/new shared JS selected by HTTP alias only.
   check(read('typeof NameleculeGameLevels')=='undefined','native Main'+str(version)+' '+variant+' common JS without Levels global')
   SOLVERS[game]('native'+str(version)+' '+variant+' v1 genuine answer',True)
   before=rec();call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();open_gate();game_ready(game,True)
   check(rec()['states']['3']['games'][game]['states'][0]['solved'],'native'+str(version)+' '+variant+' warm reload retains genuine v1 answer')
   native=window_expr(game,True)+'.document.getElementById("molecule-viewer").contentWindow'
   check(read('typeof ('+native+').NameleculeGameLevels')=='undefined','actual generated native'+str(version)+' '+variant+' no Levels dependency')
   shot('native-'+str(version)+'-'+variant+'-warm')

PRELOAD = '''()=>{window.__lessonMessages=[];addEventListener('message',e=>{if(e.origin!==location.origin)return;const d=e.data;if(d?.channel==='namelecule-builder-lesson-v1'&&d.command==='load')window.__lessonLoad=d;if(d?.channel==='namelecule-puzzle-lesson-v1'&&d.command==='load')window.__puzzleLoad=d;if(['namelecule-builder-lesson-v1','namelecule-puzzle-lesson-v1','namelecule-detective-lesson-v1'].includes(d?.channel))window.__lessonMessages.push(d);});}'''

exec(compile((HERE/'legacy-api-helpers.py').read_text(),str(HERE/'legacy-api-helpers.py'),'exec'),globals())

def main():
 global OUT,DEST,FROZEN,SOURCES,RUN_TIMEOUT,RUN_DEADLINE,PROTOCOL_TIMEOUT,MODE,GAME,INDEX,MOLS,NAME_IDS,BANDS,ALL_IDS,ctx,connection,port,preload,connections,all_events,js_errors
 args=parse_args()
 if args.prepare_check:
  # Parsing helper definitions and listing declared scope cannot start browsers.
  print(json.dumps({'prepared':True,'root':str(ROOT),'entrypoint':str(Path(__file__)),'engines':['chrome','firefox'],'modes':['standalone-{builder,puzzle,detective,repair}','lesson-required-{builder,puzzle,detective,repair}','lesson-optional-detective','native-cache'],'helpers':'AST definitions only; no browser startup','runtimeEdited':False}));return
 assert os.environ.get('NAMELECULE_LEVELS_BROWSER_GRANT')=='frozen','Root frozen-target AND exclusive browser-slot grant required'
 manifest=Path(os.environ['NAMELECULE_LEVELS_FROZEN_MANIFEST']).resolve();freeze=json.loads(manifest.read_text())
 assert 0<args.timeout<=1800,'Absolute run deadline max1800seconds'
 RUN_TIMEOUT=args.timeout;RUN_DEADLINE=time.monotonic()+RUN_TIMEOUT;MODE=args.mode;GAME=MODE.split('-')[-1];INDEX=0
 FROZEN={p:(v if isinstance(v,str) else v.get('sha256',v.get('SHA256'))) for p,v in freeze['files'].items()}
 assert FROZEN and all(sha(ROOT/p)==v for p,v in FROZEN.items()),'Frozen source drift before run'
 assert set(CACHE_COMMON).issubset(FROZEN),'Manifest must cover all shared checkpoint JS'
 SOURCES=set(FROZEN)|BASE_SOURCES
 if MODE in ['native-cache','legacy-migration']:SOURCES.update(str((PRIOR/p).relative_to(ROOT)) for p in CACHE_COMMON|{'scenarios/alkanes-user-3.scenario.json'})
 pack=json.loads((ROOT/'data/namelecule-alkanes-v1/manifest.json').read_text())
 for m in pack['molecules']:SOURCES.update(m['files'].values())
 catalog=json.loads((ROOT/'games/data/alkane-structures-v2.json').read_text());MOLS={m['id']:m['mol'] for m in catalog['molecules']}
 facts=json.loads((ROOT/'docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json').read_text());NAME_IDS={facts[mid]['correctName']:mid for mid in MOLS}
 BANDS={'1':['methane','ethane','propane','butane','pentane'],'2':['methyl_2_butane','methyl_2_pentane','methyl_3_pentane','ethyl_3_pentane'],'3':['dimethyl_2_2_propane','dimethyl_2_2_butane','dimethyl_2_3_butane','ethyl_3_methyl_2_pentane','ethyl_3_dimethyl_2_5_hexane']};ALL_IDS=sum(BANDS.values(),[])
 DEST=HERE/('run-'+args.engine+'-'+MODE+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'));DEST.mkdir(exist_ok=False)
 OUT={'role':'Developer browser execution; not independent review','engine':args.engine,'mode':MODE,'checks':[],'correctUIAttempts':[],'sourceBefore':hashes(),'manifest':str(manifest),'manifestSHA256':sha(manifest),'harnessSHA256':sha(Path(__file__)),'recordedHelperSHA256':{p.name:sha(p) for p in [RECORDED/'replay-detective.py',RECORDED/'replay-chrome.py']},'limits':['Isolated headless browser CSS emulation; physical mobile, personal Firefox, conference and offline reliability unqualified.','Actual external JSmol/fonts/services remain dependencies; captured network failures are reported.','Canonical oracles are read-only; completion evidence comes from trusted production input and parent records.']}
 archive=DEST/'harness.py';shutil.copyfile(Path(__file__),archive)
 OUT['legacyHelperSHA256']=sha(HERE/'legacy-api-helpers.py');shutil.copyfile(HERE/'legacy-api-helpers.py',DEST/'legacy-api-helpers.py')
 browser=server=profile=log=None;connections=[];all_events=[];js_errors=[];preload=None
 lock=HERE/'.owned-browser.lock';lock_fd=None
 try:
  lock_fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(lock_fd,json.dumps({'pid':os.getpid(),'run':str(DEST)}).encode());os.close(lock_fd);lock_fd=None
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  profile=Path(tempfile.mkdtemp(prefix=OWNED_PREFIX+args.engine+'-',dir='/private/tmp'));log=(DEST/(args.engine+'.log')).open('w')
  if args.engine=='chrome':
   load_functions(RECORDED/'replay-chrome.py',{'configure_connection','connect_target','cdp','ev','wait_document','call'},include_classes={'CDP'})
   executable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
   browser=subprocess.Popen([executable,'--headless=new','--no-first-run','--no-default-browser-check','--user-data-dir='+str(profile),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1800,1400','about:blank'],stdout=log,stderr=subprocess.STDOUT)
   deadline=min(RUN_DEADLINE,time.monotonic()+40)
   while not (profile/'DevToolsActivePort').is_file():
    if browser.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned Chrome startup failed')
    time.sleep(.1)
   port=int((profile/'DevToolsActivePort').read_text().splitlines()[0]);ctx,connection=connect_target()
  else:
   with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
   executable='/Applications/Firefox.app/Contents/MacOS/firefox'
   browser=subprocess.Popen([executable,'--headless','--no-remote','--width','1800','--height','1400','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,MOZ_HEADLESS_WIDTH='1800',MOZ_HEADLESS_HEIGHT='1400'))
   deadline=min(RUN_DEADLINE,time.monotonic()+30)
   while True:
    try:
     with socket.create_connection(('127.0.0.1',port),timeout=.4):break
    except OSError:
     if browser.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned Firefox startup failed')
     time.sleep(.2)
   os.environ['NAMELECULE_BIDI_PORT']=str(port);exec(compile(bounded_bidi_source((ROOT/'tools/namelecule_bidi.py').read_text()),'owned-levels-bidi','exec'),globals())
   call('session.subscribe',{'events':['network.beforeRequestSent','network.responseCompleted','network.fetchError'],'contexts':[ctx]})
  OUT['process']={'ownedPID':browser.pid,'profile':str(profile),'debugPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
  call('script.addPreloadScript',{'functionDeclaration':PRELOAD})
  served={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p,timeout=min(30,check_deadline())).read()).hexdigest() for p in sorted(SOURCES)}
  check(served==OUT['sourceBefore'],'HTTP serves exact frozen/native/source bytes');OUT['servedSHA256']=served
  viewport(1500,1000)
  if MODE.startswith('standalone-'):
   standalone(GAME)
   if GAME=='detective':controlled_detective_smoke()
  elif MODE.startswith('lesson-required-'):required_replay(GAME)
  elif MODE=='lesson-optional-detective':optional_replay()
  elif MODE=='native-cache':native_cache(args.cache_variants.split(','))
  else:legacy_migration()
  check(not js_errors,'no captured runtime JavaScript exceptions',js_errors);OUT['completed']=True
 except Exception:
  OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
  if browser is not None:
   OUT['failureState']={}
   for name,expression in [('url','location.href'),('body','document.body.innerText.slice(-10000)'),('messages','window.__lessonMessages??null'),('detective','window.NameleculeMolecularDetective?.snapshot()??null'),('nextMission','(()=>{const e=document.getElementById("next-mission");return e?{hidden:e.hidden,disabled:e.disabled,rect:e.getBoundingClientRect().toJSON()}:null})()')]:
    try:OUT['failureState'][name]=read(expression)
    except Exception as capture:OUT['failureState'][name+'CaptureError']=repr(capture)
   try:
    if read('typeof fScenarioPresent==="function"'):OUT['failureState']['record']=rec()
    shot('failure')
   except Exception as capture:OUT['failureCaptureError']=repr(capture)
 finally:
  OUT['javascriptErrors']=js_errors;OUT['events']=all_events;OUT['sourceAfter']=hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
  if not OUT['sourceUnchangedDuringRun']:OUT['completed']=False
  for item in connections:
   try:item.sock.close()
   except OSError:pass
  if args.engine=='firefox' and 's' in globals():
   try:globals()['s'].close()
   except OSError:pass
  if browser is not None and browser.poll() is None:
   browser.terminate()
   try:browser.wait(timeout=10)
   except subprocess.TimeoutExpired:browser.kill();browser.wait(timeout=10)
  if server:server.shutdown();server.server_close()
  if log:log.close()
  OUT['ownedBrowserExited']=browser is None or browser.poll() is not None;OUT['ownedServerClosed']=server is None or server.fileno()==-1
  if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith(OWNED_PREFIX) and not profile.is_symlink():shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
  if lock.exists():
   try:
    if json.loads(lock.read_text()).get('pid')==os.getpid():lock.unlink()
   except Exception:pass
  OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps({'completed':OUT.get('completed',False),'engine':args.engine,'mode':MODE,'checks':len(OUT['checks']),'correctUIAttempts':len(OUT['correctUIAttempts']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
 if not OUT.get('completed'):raise SystemExit(1)

if __name__=='__main__':main()
