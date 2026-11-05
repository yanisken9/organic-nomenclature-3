"""Developer Firefox: cancellation/stale results and generated checkpoint recovery.
Delayed calls still use the actual chemistry client and Workers. Faults injected
only in this owned test tab, never in source files.
"""
from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/alkanes-two-part-20261105/browser/support.py').read_text(),'support','exec'))
LESSON='mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1'

def ready():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")');call('browsingContext.activate',{'context':ctx})

def receipt():return json.loads(ev("JSON.stringify(Object.entries(sessionStorage).filter(([k])=>k.startsWith('namelecule:lesson-checkpoints:v1:')).map(([key,value])=>({key,value:JSON.parse(value)})))"))

try:
 navigate(LESSON+'#step=4');ready()
 # Delay entry to real analysis, leaving an observable cancellation interval.
 ev('''window.testAnalyze=NameleculeChemistryClient.analyze;NameleculeChemistryClient.analyze=(m,o)=>new Promise((resolve,reject)=>setTimeout(()=>testAnalyze(m,o).then(resolve,reject),700));true''')
 click('#nlQuizOpen');until('!!document.querySelector(".nl-quiz-loading")');until('sessionStorage.length>0');click('#nlQuizBack')
 saved=receipt();check(len(saved)==1 and saved[0]['value']['states']['3']['seed'],'Seed persists before async generation')
 before=state();ev('fScenarioGo(11);true');until('!!document.querySelector("#scCheckpointPreparation")')
 check(index()==3 and state()==before and ev('document.querySelector("#scNext").disabled'),'Preparation retains viewer/index and disables Next')
 ev('fScenarioGo(2);true');until('fScenarioPresent().index===2&&!MuLERMoCScenario.checkpointPreparation');ev('new Promise(r=>setTimeout(r,1800))')
 check(index()==2 and not ev('!!document.querySelector("#scCheckpointPreparation")'),'Replacement navigation cancels obsolete preparation without late apply')
 ev('fScenarioGo(11);true');until('!!MuLERMoCScenario.checkpointPreparation');click('#scCheckpointPreparation button:last-child');until('!MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation');ev('new Promise(r=>setTimeout(r,1800))')
 check(not ev('MuLERMoCScenario.present'),'Exit during async work cannot reopen presentation')
 ev('window.testScenario=fScenarioActive();fScenarioPresentBegin(testScenario.id,11);true');until('!!MuLERMoCScenario.checkpointPreparation')
 check(not ev('MuLERMoCScenario.present'),'Author presentation start waits for validation')
 ev('window.testOther=fScenarioNew("owned cancellation test",true);true');ev('new Promise(r=>setTimeout(r,1800))')
 check(ev('fScenarioActive()===testOther&&!MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation'),'Switch/new card cancels pending presentation start')
 ev('fScenarioSetActive(testScenario.id);fScenarioPresentBegin(testScenario.id,11);true');until('!!MuLERMoCScenario.checkpointPreparation')
 ev('testScenario.steps[0].note+=" ";true');until('!MuLERMoCScenario.checkpointPreparation',seconds=15)
 check(not ev('MuLERMoCScenario.present||MuLERMoCScenario.checkpointPreparation'),'Authored-content edit invalidates pending callbacks and clears surface')
 ev('testScenario.steps[0].note=testScenario.steps[0].note.slice(0,-1);NameleculeChemistryClient.analyze=testAnalyze;fScenarioPresentBegin(testScenario.id,3);true');until('MuLERMoCScenario.present&&fScenarioPresent().index===3')
 ev('history.replaceState(null,"",'+json.dumps(LESSON+'#step=4')+');true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
 # Deliberate catalog rejection on fresh generated mount; the real adapter checks bytes.
 ev('window.testFetch=window.fetch;window.testBadCatalog=true;window.fetch=(input,options)=>testBadCatalog&&String(input).includes("games/data/alkane-structures.json")?Promise.resolve(new Response("{}",{status:200})):testFetch(input,options);true')
 click('#nlQuizOpen');until('!!document.querySelector(".nl-quiz-error")')
 check(ev('document.querySelector("#scNext").disabled') and ev('!!document.querySelector("#nlQuizBack")'),'Invalid catalog bytes fail closed with usable return')
 screenshot_here('generated-catalog-error.png');ev('window.testBadCatalog=false;true');click('#nlQuizHost .nl-quiz-button');until('!!document.querySelector(".diagram-image.is-ready")')
 check(True,'Generated mount Retry recovers actual catalog and engine')
 click('#nlQuizBack')
 # Source/canonical rounds are now prepared; image failures must still gate assessment.
 ev('window.testBadImage=true;window.testImageDescriptor=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,"src");Object.defineProperty(HTMLImageElement.prototype,"src",{...testImageDescriptor,set(value){testImageDescriptor.set.call(this,testBadImage&&String(value).endsWith(".svg")?"games/assets/name-repair/owned-deliberate-missing.svg":value)}});true')
 click('#nlQuizOpen');until('document.querySelector(".image-status")?.textContent.includes("δεν εμφανίστηκε")')
 check(ev('[...document.querySelectorAll(".part-button")].every(n=>n.disabled)&&document.querySelector("#scNext").disabled'),'Missing generated diagram disables repair and keeps gate')
 check(not ev('document.querySelector("#nlQuizRetry").hidden'),'Diagram error exposes outer reload')
 ev('window.testBadImage=false;true');click('#nlQuizRetry');until('!!document.querySelector(".diagram-image.is-ready")')
 check(ev('[...document.querySelectorAll(".part-button")].every(n=>!n.disabled)'),'Reload recovers actual diagram')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':844,'height':390},'devicePixelRatio':1})
 check(ev('(()=>{let n=document.querySelector("#nlQuizDialog"),r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&n.scrollWidth<=n.clientWidth+1})()'),'Three-round embedded dialog fits landscape viewport')
 screenshot_here('generated-dialog-landscape.png')
 click('.diagram-tools button',True);until('!!document.querySelector("#nlQuizDialog .zoom-dialog")');key('\ue00c');until('!document.querySelector("#nlQuizDialog .zoom-dialog")')
 check(ev('document.querySelector("#nlQuizDialog").open'),'Zoom Escape stays in generated quiz')
 key('\ue00c');until('!document.querySelector("#nlQuizDialog[open]")');check(index()==3,'Next Escape returns to same theory checkpoint')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 # A saved aggregate flag with no canonical checked answers must not pass refresh.
 ev('''for(const [key,text] of Object.entries(sessionStorage)){if(key.startsWith('namelecule:lesson-checkpoints:v1:')){const r=JSON.parse(text);r.states[3]={version:1,seed:r.states[3].seed,currentRound:2,solved:true,states:[{solved:true,submitted:true,attempts:1},{solved:true,submitted:true,attempts:1},{solved:true,submitted:true,attempts:1}]};sessionStorage.setItem(key,JSON.stringify(r))}}history.replaceState(null,"","#step=12");true''')
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();until('!MuLERMoCScenario.checkpointPreparation')
 check(index()==3 and ev('document.querySelector("#scNext").disabled'),'Forged aggregate/skipped answers rejected by actual refresh regeneration')
 normalized=receipt()[0]['value']['states']['3'];check(not normalized['solved'] and all(not s['solved'] for s in normalized['states']),'All forged round flags normalized incomplete')
 # Unavailable tab storage remains usable in-memory with an explicit notice.
 ev('window.testSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new Error("owned unavailable storage")};true')
 click('#nlQuizOpen');until('!!document.querySelector(".diagram-image.is-ready")')
 check(ev('!document.querySelector(".nl-quiz-storage-note").hidden'),'Storage write failure disclosed while quiz remains usable')
 click('#nlQuizBack');ev('Storage.prototype.setItem=testSetItem;true')
 ev('window.testOriginalSpec=fScenarioPresent().steps[3].checkpoint;fScenarioPresent().steps[3].checkpoint={...testOriginalSpec,type:"unknown-required-quiz"};fScenarioGo(11);true')
 check(index()==3,'Unknown required type cannot bypass generated gate')
 ev('fScenarioPresent().steps[3].checkpoint=testOriginalSpec;true')
 out['completed']=True
except Exception as exc:
 out['failure']=str(exc);out['traceback']=traceback.format_exc()
 try:screenshot_here('recovery-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['consoleErrors']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')=='error']
 (HERE/'recovery-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
