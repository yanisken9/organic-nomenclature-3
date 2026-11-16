"""Bounded genuine Main56 → Main57 progress compatibility at one same origin.

Reuses frozen owned replay helpers. No receipt/state injection: actual palette,
bond, Undo and Check actions earn the required triple in56. All writes are new
evidence; all candidate application bytes remain frozen throughout the case.
"""
from pathlib import Path
import os, textwrap
os.environ.setdefault('NAMELECULE_V57_GAME','puzzle')
os.environ.setdefault('NAMELECULE_V57_RUN','migration-run1')
driver=Path(__file__).with_name('replay.py').read_text()
prefix,start=driver.split('\ntry:\n server=',1)
exec(compile(prefix,'migration-frozen-replay-helpers','exec'))
OUT['scope']='Same tab/origin Main56 genuine Puzzle partial → Main57; return56 and earn actual three distinct molecules; navigate57step5 and assess earned restore. Exact normalized steps/signature/storage captured at first divergence.'
def snapshot():
 return read('(()=>{const s=fScenarioPresent(),signature=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});return{url:location.href,index:s.index,title:s.title,author:s.author,steps:s.steps,signature,storage:Object.fromEntries(Object.entries(sessionStorage)),matchingKeys:Object.entries(sessionStorage).filter(([k,v])=>{try{return JSON.parse(v)?.content===signature}catch(e){return false}}).map(([k])=>k),nextDisabled:document.getElementById("scNext").disabled}})()')
def lesson_version(version,index):
 page('mulermoc-nom-'+str(version)+'.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step='+str(index+1));ready()
def reopen_puzzle():
 open_gate()
 if ev('document.querySelectorAll(".nl-game-choice-card").length===3'):choose('puzzle')
 else:game_ready('puzzle')
def diff(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:out.append({'path':path+'/'+str(k),'beforePresent':k in a,'afterPresent':k in b,'before':a.get(k),'after':b.get(k)})
   else:out+=diff(a[k],b[k],path+'/'+str(k))
  return out
 if isinstance(a,list) and isinstance(b,list):
  return sum((diff(a[i] if i<len(a) else None,b[i] if i<len(b) else None,path+'/'+str(i)) for i in range(max(len(a),len(b)))),[])
 return [] if a==b else [{'path':path,'before':a,'after':b}]
try:
 startup=' server='+start.split(" if GAME=='author':",1)[0]
 exec(compile(textwrap.dedent(startup),'migration-owned-startup','exec'))
 lesson_version(56,3);check(read('fScenarioPresent().index')==3,'Main56 cold gate4 is actual test source')
 reopen_puzzle();load=puzzle_state()['load'];graph=frame_read('puzzle','NameleculeMolecularPuzzleEngine.parseMol('+json.dumps(MOLS[load['moleculeId']])+')')
 frame_click('puzzle','[data-hydrogens="'+str(graph['nodes'][0]['hydrogens'])+'"]');pause(.3)
 OUT['before56Partial']={'page':snapshot(),'puzzle':puzzle_state(),'record':rec()};shot('56-partial')
 check(len(OUT['before56Partial']['puzzle']['nodes'])==1,'Main56 partial genuinely created via palette')
 lesson_version(57,3);OUT['after57PartialBeforeOpen']=snapshot();reopen_puzzle()
 OUT['after57Partial']={'page':snapshot(),'puzzle':puzzle_state(),'record':rec()};shot('57-partial-restore')
 a=OUT['before56Partial'];b=OUT['after57Partial']
 OUT['normalizedStepDifferences']=diff(a['page']['steps'],b['page']['steps'])
 OUT['partialPreserved']=a['puzzle']['nodes']==b['puzzle']['nodes'] and a['puzzle']['load']['moleculeId']==b['puzzle']['load']['moleculeId']
 OUT['signaturesEqual']=a['page']['signature']==b['page']['signature']
 print(json.dumps({'partialPreserved':OUT['partialPreserved'],'signaturesEqual':OUT['signaturesEqual'],'normalizedDifferences':len(OUT['normalizedStepDifferences']),'firstDifference':OUT['normalizedStepDifferences'][:1]},ensure_ascii=False),flush=True)
 check(OUT['signaturesEqual'] and not OUT['normalizedStepDifferences'],'Main56→57 normalized lesson steps and content signature identical')
 check(OUT['partialPreserved'],'Main56→57 genuine partial answer and molecule preserved')
 # Continue the very same genuine56 record after checking57 compatibility.
 lesson_version(56,3);reopen_puzzle();OUT['returned56Partial']={'page':snapshot(),'puzzle':puzzle_state(),'record':rec()}
 check(puzzle_state()['nodes']==a['puzzle']['nodes'] and puzzle_state()['load']['moleculeId']==load['moleculeId'],'same-origin return56 restores the exact genuine original partial')
 # Reload does not retain Undo history. Finish the real restored partial using
 # the remaining actual palette groups and real bond tool instead of resetting.
 for node in graph['nodes'][1:]:frame_click('puzzle','[data-hydrogens="'+str(node['hydrogens'])+'"]')
 ids=[n['id'] for n in puzzle_state()['nodes']];mapping={n['id']:ids[i] for i,n in enumerate(graph['nodes'])}
 check(len(ids)==len(graph['nodes']),'restored56 partial completed with actual remaining palette groups')
 if graph['bonds']:
  frame_click('puzzle','#bond-tool')
  for edge in graph['bonds']:
   frame_click('puzzle','[data-node-id="'+mapping[edge['a']]+'"]');frame_click('puzzle','[data-node-id="'+mapping[edge['b']]+'"]')
 frame_click('puzzle','#check-answer');wait('!!document.querySelector(".round-next button")')
 check(puzzle_state()['solved'] and game_state(3)['states'][0]['solved'],'actual restored56 partial Check earns first genuine result')
 OUT['rounds'].append({'label':'Main56 migration required round1 from restored partial','moleculeId':load['moleculeId'],'practice':False,'state':game_state(3)})
 OUT['earned56IDs']=[load['moleculeId']];footer('Main56 migration required round1',False)
 for i in [1,2]:
  check(not rec()['states']['3']['solved'],'56 remains locked before all three genuine molecules')
  click('.round-next button:first-child');game_ready();OUT['earned56IDs'].append(solve('Main56 migration required round'+str(i+1),3));footer('Main56 migration required round'+str(i+1),i==2)
 check(len(set(OUT['earned56IDs']))==3,'Main56 migration actually earns three distinct molecules',OUT['earned56IDs'])
 check(rec()['states']['3']['solved'],'Main56 genuine complete triple unlocks gate4')
 earned=rec()['states']['3']['earned'];OUT['before56Earned']={'page':snapshot(),'record':rec(),'earned':earned};shot('56-earned-triple')
 lesson_version(57,4);OUT['after57EarnedBeforeOpen']={'page':snapshot(),'record':rec()}
 OUT['earnedGateAllowsStep5']=read('fScenarioPresent().index')==4
 if not OUT['earnedGateAllowsStep5']:reopen_puzzle()
 OUT['after57Earned']={'page':snapshot(),'record':rec()};shot('57-earned-restore')
 new=rec();OUT['earnedPreserved']=bool(new and new.get('states',{}).get('3',{}).get('solved') and new['states']['3'].get('earned')==earned)
 OUT['compatibilityPassed']=OUT['partialPreserved'] and OUT['earnedGateAllowsStep5'] and OUT['earnedPreserved']
 check(OUT['compatibilityPassed'],'Main56→57 earned gate and exact original receipt preserved')
 OUT['completed']=True
 print(json.dumps({'compatibilityPassed':OUT['compatibilityPassed'],'partialPreserved':OUT['partialPreserved'],'earnedPreserved':OUT['earnedPreserved'],'earnedGateAllowsStep5':OUT['earnedGateAllowsStep5']}),flush=True)
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']={'page':snapshot(),'record':rec()};shot('failure')
 except Exception as e:OUT['failureCaptureError']=repr(e)
finally:
 cleanup=driver.rsplit("\nfinally:\n OUT['javascriptErrors']",1)[1].split("\nif not OUT.get('completed')",1)[0]
 exec(compile(textwrap.dedent(" OUT['javascriptErrors']"+cleanup),'migration-owned-cleanup','exec'))
if not OUT.get('completed'):raise SystemExit(1)
