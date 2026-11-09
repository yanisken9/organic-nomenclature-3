"""Targeted R1 verification. Real saved receipts regenerate through actual Workers.
Analysis is delayed in this owned tab to observe the cold loading boundary.
"""
from pathlib import Path
import json,traceback
exec(compile(Path('docs/checks/alkanes-two-part-20261105/browser/support.py').read_text(),'support','exec'))
LESSON='mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1'
fixture=json.loads((HERE/'two-part-browser.json').read_text())['finalStorage'];preload=None
FUNCTION=r'''()=>{window.testAnalysisFault=undefined;let api;Object.defineProperty(window,'NameleculeChemistryClient',{configurable:true,get(){return api},set(value){const original=value.analyze;api={...value,analyze:(m,o)=>new Promise((resolve,reject)=>setTimeout(()=>{if(window.testAnalysisFault===true||(window.testAnalysisFault!==false&&String(location.href).includes('coldFault=1'))){reject(new Error('owned deliberate analysis failure'));return}original(m,o).then(resolve,reject)},1200))}}})}'''

def pending():
 until('typeof MuLERMoCScenario!=="undefined"&&!!MuLERMoCScenario.checkpointPreparation');call('browsingContext.activate',{'context':ctx})

def cold_status():return ev('document.documentElement.classList.contains("lesson-loading")&&!!document.querySelector("#lessonLoading #scCheckpointPreparation.is-cold")&&getComputedStyle(document.getElementById("pageContainer")).visibility==="hidden"')
try:
 preload=call('script.addPreloadScript',{'functionDeclaration':FUNCTION,'contexts':[ctx]})['script']
 navigate(LESSON+'#step=4');app_ready();until('typeof MuLERMoCScenario!=="undefined"&&MuLERMoCScenario.present&&fScenarioPresent().index===3&&!document.documentElement.classList.contains("lesson-loading")')
 ev('sessionStorage.clear();Object.entries('+json.dumps(fixture,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,JSON.stringify(v)));history.replaceState(null,"",'+json.dumps(LESSON+'&coldFault=1#step=5')+');true')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});pending();check(cold_status(),'Cold preparation keeps bootstrap molecule hidden and status inside loader')
 until('!!document.querySelector("#scCheckpointPreparation.is-error")');check(cold_status(),'Cold failure retains loading boundary and visible recovery surface')
 check(ev('getComputedStyle(document.querySelector("#scCheckpointPreparation button:last-child")).visibility==="visible"&&!document.querySelector("#scCheckpointPreparation button").hidden'),'Retry and Exit visible inside cold loader')
 screenshot_here('cold-error-recovery.png');ev('window.testAnalysisFault=false;true');click('#scCheckpointPreparation button')
 until('!MuLERMoCScenario.checkpointPreparation&&fScenarioPresent().index===4&&!document.documentElement.classList.contains("lesson-loading")');check(ev('selectedMol==="methyl_2_pentane"&&!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Retry reveals resolved lesson snapshot after actual canonical verification')
 check(not ev('!!document.querySelector("#scCheckpointPreparation")'),'Preparation panel removed after resolved snapshot')
 screenshot_here('cold-restored-step5.png')
 # A warm delayed preparation keeps the existing molecular stage visible/unchanged.
 click('#zoomInBtn');initial=state()
 ev('window.testPrepare=NameleculeQuizCheckpoints.prepareTarget;NameleculeQuizCheckpoints.prepareTarget=function(){NameleculeQuizCheckpoints.prepareTarget=testPrepare;return new Promise(resolve=>setTimeout(resolve,500))};fScenarioGo(5);true')
 check(ev('!!document.querySelector("body > #scCheckpointPreparation")&&!document.documentElement.classList.contains("lesson-loading")') and state()==initial,'Warm preparation preserves visible viewer state')
 until('fScenarioPresent().index===5&&!MuLERMoCScenario.checkpointPreparation');check(True,'Warm continuation applies intended next step')
 ev('history.replaceState(null,"",'+json.dumps(LESSON+'#step=5')+');true');call('browsingContext.reload',{'context':ctx,'wait':'none'});pending();check(cold_status(),'Successful refresh also hides bootstrap state while reconstructing')
 until('fScenarioPresent().index===4&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")')
 check(ev('selectedMol==="methyl_2_pentane"'),'Successful refresh preserves requested destination')
 # Exit must release the cold loading surface only after returning to app chrome.
 call('browsingContext.reload',{'context':ctx,'wait':'none'});pending();click('#scCheckpointPreparation button:last-child')
 until('!MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")');ev('new Promise(r=>setTimeout(r,1800))')
 check(not ev('MuLERMoCScenario.present'),'Cold Exit returns to usable app and late work cannot reopen it')
 call('browsingContext.navigate',{'context':ctx,'url':'http://127.0.0.1:8055/'+LESSON+'&from=theory-library#step=5','wait':'none'});pending();click('#scCheckpointPreparation button:last-child');until('location.pathname.endsWith("/design/theory-library.html")')
 check(True,'Cold library-launched Exit returns to library')
 out['completed']=True
except Exception as exc:
 out['failure']=str(exc);out['traceback']=traceback.format_exc()
 try:screenshot_here('cold-restoration-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['consoleErrors']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')=='error']
 (HERE/'cold-restoration-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 if preload:call('script.removePreloadScript',{'script':preload})
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
