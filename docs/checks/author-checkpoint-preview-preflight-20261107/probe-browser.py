from pathlib import Path
import os,json,traceback
folder=Path('docs/checks/author-checkpoint-preview-preflight-20261107')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((folder/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'observations':[],'limitations':['Owned headless profile, not user browser or unsaved JSON','Existing project lesson used; only test-profile in-memory title edited','No implementation or source JSON edits']}
def info(label):
 d=json.loads(ev('JSON.stringify({present:MuLERMoCScenario.present,authoring:MuLERMoCScenario.authoring,index:fScenarioPresent().index+1,hash:location.hash,selectedMol:selectedMol,title:fScenarioPresent().steps[fScenarioPresent().index].title,traces:window.testTrace||[],storedKeys:Object.keys(sessionStorage).filter(k=>k.includes("lesson-checkpoints"))})'))
 d['label']=label;out['observations'].append(d);print(json.dumps(d,ensure_ascii=False),flush=True)
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=author-preview-preflight-20261107-r1')
 app_ready();until('fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();window.testTrace=[];["fScenarioPresentBegin","fScenarioGo","fScenarioResolveCheckpointTarget"].forEach(k=>{const orig=window[k];window[k]=function(...args){const entry={fn:k,requested:typeof args[0]==="number"?args[0]+1:typeof args[1]==="number"?args[1]+1:null,present:MuLERMoCScenario.present};testTrace.push(entry);const value=orig.apply(this,args);if(k==="fScenarioResolveCheckpointTarget")entry.result=value+1;return value}});true')
 ev('const t=document.querySelector(".scenarioPanel.active .srow:nth-child(5) .scStepTitle");t.value=t.value+" [δοκιμή προεπισκόπησης]";t.dispatchEvent(new Event("change",{bubbles:true}));true')
 info('Before edited-step launch')
 ev('testTrace=[];document.querySelector(".scenarioPanel.active .srow:nth-child(5) .scGo").click();true')
 until('fScenarioPresent().index===4',seconds=10);info('Author row Preview/Go');screenshot(folder/'author-go-step5.png')
 ev('testTrace=[];document.querySelector(".scenarioPanel.active .srow:nth-child(5) .scPresentStep").click();true')
 until('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation',seconds=40);info('Author row Present from step');screenshot(folder/'author-present-clamped-step4.png')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=author-preview-preflight-20261107-r1#step=5')
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45);info('Normal learner direct step5 URL')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors
 (folder/'browser-observations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'failure':out.get('failure'),'javascriptErrors':len(js_errors)},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
