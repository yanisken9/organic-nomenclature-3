"""Bounded fresh gate replay after first diagnostic closed its tab; no width-suite repeat."""
from pathlib import Path
exec((Path(__file__).with_name('measurements.py')).read_text())
import ast
prior=(ROOT/'docs/checks/game-headers-parity-20261111/browser/parity.py').read_text();n=next(n for n in ast.parse(prior).body if isinstance(n,ast.FunctionDef) and n.name=='feedback');exec(compile(ast.Module(body=[n],type_ignores=[]),'feedback-definition','exec'))
def diff(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):return sum((diff(a.get(k),b.get(k),path+'.'+k) for k in sorted(set(a)|set(b))),[])
 if isinstance(a,list) and isinstance(b,list):return sum((diff(a[i] if i<len(a)else None,b[i]if i<len(b)else None,path+'['+str(i)+']') for i in range(max(len(a),len(b)))),[])
 return [] if a==b else [{'path':path,'before':a,'after':b}]
def semantic(s):
 keys=['selectedPartId','selectedValue','attempts','selectionMisses','solved','submitted','order','choiceOrder']
 states=[]
 for index,r in enumerate(s['states']):
  fields=keys
  if isinstance(r,dict) and index>s['currentRound'] and not r.get('solved') and not r.get('submitted') and not r.get('attempts') and not r.get('selectionMisses') and r.get('selectedPartId') is None and r.get('selectedValue') is None and not r.get('order'):
   fields=[k for k in keys if k!='choiceOrder']
  states.append({k:r.get(k) for k in fields} if isinstance(r,dict) else r)
 return {**{k:s.get(k) for k in ['seed','currentRound','solved']},'states':states}
try:
 lesson();open_gate();choose('builder')
 for i in range(3):
  bsolve('Replay gate4 Builder '+str(i+1))
  if i<2:click('.round-next button');builder_ready()
 check(rec()['states']['3']['earned']['game']=='builder','Fresh replay earns gate4 through genuine Builder triple');click('.round-next button');wait('!document.getElementById("nlQuizDialog").open');ev('location.hash="step=11";true');wait('fScenarioPresent().index===10');open_gate();choose('repair')
 ids=[]
 for i in range(3):
  if i==1:
   pause(.6);before=rec()['states']['10']['games']['repair'];OUT['restore']={'before':before};(HERE/'restore-before.json').write_text(json.dumps(OUT['restore'],ensure_ascii=False,indent=2)+'\n')
   call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');pause(.6);after=rec()['states']['10']['games']['repair'];OUT['restore'].update({'after':after,'fullDiff':diff(before,after),'semanticBefore':semantic(before),'semanticAfter':semantic(after),'semanticDiff':diff(semantic(before),semantic(after))});(HERE/'restore-diff.json').write_text(json.dumps(OUT['restore'],ensure_ascii=False,indent=2)+'\n')
   check(not OUT['restore']['semanticDiff'],'Exact meaningful Workshop progress survives cold reload',OUT['restore']);verify(sample('repair','Workshop after semantic restore'),'Workshop after semantic restore')
  if i==2:viewport(390,760);verify(sample('repair','Gate11 Workshop mobile390'),'Gate11 Workshop mobile390')
  ids.append(rsolve('Replay gate11 Workshop '+str(i+1),10)['moleculeId']);footer('Replay gate11 Workshop '+str(i+1),i==2)
  if i==2:feedback('gate11-workshop-mobile390','repair')
  if i<2:click('.round-next button');wait('!!document.querySelector(".diagram-image.is-ready")')
 check(len(set(ids))==3 and rec()['states']['10']['earned']['game']=='repair','Gate11 genuine distinct Workshop triple earns access',ids)
 viewport(1500,1000);lesson(3,54);check(ev('fScenarioPresent().index')==3,'Main54 own gate4');open_gate();choose('builder');verify(sample('builder','Main54 Builder'),'Main54 Builder');choose('repair');verify(sample('repair','Main54 Workshop'),'Main54 Workshop')
 open_page('games/name-builder.html?molecule=butane&textParity=remaining-20261111-r1');wait('!!document.querySelector("#bank-tiles button")',60);check(ev('!document.documentElement.classList.contains("lesson-mode")&&getComputedStyle(document.querySelector(".objective")).fontWeight==="750"&&getComputedStyle(document.querySelector(".site-header")).display!=="none"&&getComputedStyle(document.getElementById("next-molecule")).display!=="none"'),'Standalone Builder retains previous objective/navigation outside lesson-only CSS')
 open_page('games/name-repair.html?textParity=remaining-20261111-r1');wait('!!document.querySelector("#game-root")');check(not ev('!!document.querySelector(".nl-game-choice-repair")'),'Standalone Workshop outside scoped changes')
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1&textParity=remaining-20261111-r1#step=4');ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');check(not ev('!!document.querySelector(".nl-game-choice-repair")'),'Legacy Workshop outside new scope');check(ev('getComputedStyle(document.querySelector(".workshop-logo-small")).width')=='36px','Legacy keeps existing logo')
 OUT['passed']=True
except Exception as e:OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('remaining-failure.png');raise
finally:
 OUT['sessionStorage']=read('Object.fromEntries(Object.entries(sessionStorage))');OUT['jsExceptions']=js_errors;(HERE/'remaining-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
