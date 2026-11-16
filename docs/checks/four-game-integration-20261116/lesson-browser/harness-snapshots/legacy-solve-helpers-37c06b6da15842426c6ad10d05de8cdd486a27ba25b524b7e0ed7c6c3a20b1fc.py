"""Verbatim bounded read-only-oracle/UI-answer helpers from the recorded v57 replay.
Imported by the current owned runner; this module has no startup or side effects.
"""
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
