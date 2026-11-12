"""Actual after measurements plus bounded genuine gate replay; no fabricated progress."""
from pathlib import Path
exec((Path(__file__).with_name('measurements.py')).read_text())
# Reuse only this focused feedback definition, without starting an old browser or matrix.
import ast
prior=(ROOT/'docs/checks/game-headers-parity-20261111/browser/parity.py').read_text()
node=next(n for n in ast.parse(prior).body if isinstance(n,ast.FunctionDef) and n.name=='feedback')
exec(compile(ast.Module(body=[node],type_ignores=[]),'reused-feedback-definition','exec'))
WIDTHS=[1500,850,830,800,768,760,650,390,320]
OUT.update({'matchedShots':{},'widthPairs':[],'limits':['Actual headless Firefox/macOS, current and six-file frozen baseline over ephemeral localhost HTTP; no public deployment, other browser, real touch, offline or conference guarantee.','Six genuine required completions: gate4 Builder and gate11 Workshop. No broad chemistry/3D regression repeat for this typography/cache unit.','Normal Builder loading/ready/success status typography is measured. An error status is not fabricated or forced in this main replay.','Independent game seeds produce potentially different molecules in the paired real screenshots.']})
try:
 lesson();open_gate();choose('builder');pause(.5);fonts('Current Builder parent+iframe','builder')
 d=sample('builder','Builder natural desktop');verify(d,'Builder natural desktop',natural=True);top_shot('builder-desktop.png');OUT['matchedShots']['builder']={'file':'builder-desktop.png','moleculeId':bread('__lessonLoad.moleculeId'),'viewport':[1500,1000]};stable('Builder desktop')
 for width in WIDTHS[1:]:
  viewport(width,760 if width<=650 else 1000);pause(.5);d=sample('builder','Builder '+str(width));verify(d,'Builder '+str(width));
  if width in [390,320]:top_shot('builder-'+str(width)+'.png');stable('Builder '+str(width))
 viewport(1500,1000);choose('repair');pause(.5);fonts('Current Workshop parent','repair');d=sample('repair','Workshop natural desktop');verify(d,'Workshop natural desktop',natural=True);top_shot('workshop-desktop.png');OUT['matchedShots']['repair']={'file':'workshop-desktop.png','moleculeId':rround(3)['moleculeId'],'viewport':[1500,1000]}
 for width in WIDTHS[1:]:
  viewport(width,760 if width<=650 else 1000);pause(.5);d=sample('repair','Workshop '+str(width));verify(d,'Workshop '+str(width));
  if width in [390,320]:top_shot('workshop-'+str(width)+'.png')
 for width in WIDTHS:
  pair=[d for d in OUT['textSamples'] if d['outerWidth']==width];check(len(pair)==2,'Both actual text samples at '+str(width))
  a,b=pair;check(a['allocation']==b['allocation'],'Exact iframe/container allocation parity '+str(width),[a['allocation'],b['allocation'],a['hostWidth'],b['hostWidth']])
  keys=['fontFamily','fontSize','fontWeight','lineHeight','letterSpacing']
  for field in ['title','objective','secondary']:
   check(all(a[field][k]==b[field][k] for k in keys),'Exact '+field+' typography parity '+str(width),[{k:d[field][k] for k in keys} for d in pair])
  OUT['widthPairs'].append({'width':width,'allocation':a['allocation'],'objective':a['objective']['fontSize'],'secondary':a['secondary']['fontSize']})
 viewport(1500,1000);choose('builder');d=sample('builder','Builder switch back');verify(d,'Builder switch back',natural=True)
 ids=[]
 for i in range(3):
  ids.append(bsolve('Gate4 Builder '+str(i+1),partial_refresh=i==0));footer('Gate4 Builder '+str(i+1),i==2)
  if i==0:feedback('gate4-builder','builder');stable('Builder feedback');verify(sample('builder','Builder after partial cold refresh'),'Builder after partial cold refresh')
  if i<2:check(not rec()['states']['3']['solved'],'Gate4 locked after '+str(i+1)+' successes');click('.round-next button');builder_ready();verify(sample('builder','Builder next '+str(i+2)),'Builder next '+str(i+2),natural=True)
 earned=rec()['states']['3']['earned'];check(len(set(ids))==3 and earned['game']=='builder','Gate4 genuine Builder triple earns access',ids)
 click('.round-next button:nth-child(2)');builder_ready();verify(sample('builder','Builder optional'),'Builder optional',natural=True);top_shot('builder-optional.png');check('Προαιρετική' in ev('document.getElementById("nlQuizDialogTitle").textContent'),'Optional practice heading retained')
 choose('repair');verify(sample('repair','Workshop optional'),'Workshop optional',natural=True);top_shot('workshop-optional.png');check(rec()['states']['3']['earned']==earned,'Optional switch preserves exact earned gate4');check(not ev('!!document.querySelector(".round-next button")'),'Unsolved optional has no duplicate footer')
 click('#nlQuizPracticeContinue');wait('!document.getElementById("nlQuizDialog").open');ev('location.hash="step=11";true');wait('fScenarioPresent().index===10');open_gate();choose('builder');verify(sample('builder','Gate11 Builder'),'Gate11 Builder',natural=True);choose('repair');verify(sample('repair','Gate11 Workshop'),'Gate11 Workshop',natural=True)
 ids=[]
 for i in range(3):
  if i==1:
   saved=rec()['states']['10']['games']['repair'];call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');restored=rec()['states']['10']['games']['repair'];check(all(restored[k]==saved[k] for k in ['seed','currentRound','solved']) and restored['states'][:saved['currentRound']+1]==saved['states'][:saved['currentRound']+1],'Workshop actual/current progress survives cold reload',{'before':saved,'after':restored});verify(sample('repair','Workshop cold reload'),'Workshop cold reload')
  if i==2:viewport(390,760);verify(sample('repair','Gate11 Workshop mobile390'),'Gate11 Workshop mobile390')
  ids.append(rsolve('Gate11 Workshop '+str(i+1),10)['moleculeId']);footer('Gate11 Workshop '+str(i+1),i==2)
  if i==2:feedback('gate11-workshop-mobile390','repair')
  if i<2:check(not rec()['states']['10']['solved'],'Gate11 locked after '+str(i+1)+' successes');click('.round-next button');wait('!!document.querySelector(".diagram-image.is-ready")')
 check(len(set(ids))==3 and rec()['states']['10']['earned']['game']=='repair','Gate11 genuine Workshop triple earns access',ids)
 viewport(1500,1000);lesson(3,54);check(ev('fScenarioPresent().index')==3,'Main54 own gate4');open_gate();choose('builder');verify(sample('builder','Main54 Builder'),'Main54 Builder');choose('repair');verify(sample('repair','Main54 Workshop'),'Main54 Workshop')
 open_page('games/name-builder.html?molecule=butane&textParity=20261111-r1');wait('!!document.querySelector("#bank-tiles button")',60);check(ev('!document.documentElement.classList.contains("lesson-mode")&&getComputedStyle(document.querySelector(".objective")).fontWeight==="750"&&getComputedStyle(document.querySelector(".site-header")).display!=="none"&&getComputedStyle(document.getElementById("next-molecule")).display!=="none"'),'Standalone Builder keeps prior objective weight/header/next outside lesson CSS')
 open_page('games/name-repair.html?textParity=20261111-r1');wait('!!document.querySelector("#game-root")');check(not ev('!!document.querySelector(".nl-game-choice-repair")'),'Standalone Workshop outside lesson game-choice text scope')
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1&textParity=20261111-r1#step=4');ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');check(not ev('!!document.querySelector(".nl-game-choice-repair")'),'Legacy Workshop outside new scope');check(ev('getComputedStyle(document.querySelector(".workshop-logo-small")).width')=='36px','Legacy Workshop retains prior 36px logo')
 OUT['passed']=True
except Exception as e:OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('after-failure.png');raise
finally:
 OUT['jsExceptions']=js_errors;OUT['consoleEntries']=[e.get('params') for e in all_events if e.get('method')=='log.entryAdded'];OUT['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in json.loads((HERE.parent/'baseline.json').read_text())['proposedTarget']};(HERE/'after-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
