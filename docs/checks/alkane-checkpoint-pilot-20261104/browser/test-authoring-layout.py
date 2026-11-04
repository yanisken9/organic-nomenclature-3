from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/alkane-checkpoint-pilot-20261104/browser/test-pilot.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[]}
try:
 navigate(PILOT+'#step=10');lesson_ready();until('!!document.querySelector("#nlQuizOpen")')
 # Real existing portrait bypass, not hidden via test CSS.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 until('getComputedStyle(document.querySelector("#rotatePrompt")).display!=="none"');click('#rotatePromptDismiss',True);open_quiz(True)
 check(ev('(()=>{const d=document.querySelector("#nlQuizDialog"),r=d.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&d.scrollWidth<=d.clientWidth+1})()'),'390px portrait after actual dismiss fits without overflow')
 fonts=json.loads(ev('JSON.stringify([...document.querySelectorAll("#nlQuizDialog .round-heading h1,#nlQuizDialog .part-button,#nlQuizDialog .choice-button")].map(n=>({text:n.textContent,display:getComputedStyle(n).display,font:getComputedStyle(n).fontSize})))'))
 out['fonts']=fonts;check(fonts[0]['display']!='none','Embedded mission title remains visible in portrait')
 screenshot_here('pilot-mission-portrait.png');click(part('root'),True);click(choice(1),True);click(submit(),True);until('!!document.querySelector(".feedback.is-success")');click('.round-next button',True);until('fScenarioPresent().index===10')
 check(True,'390px portrait simulated-touch answer and Continue')
 # Authoring Update uses real live capture, export actual Blob, import real FileReader.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 ev('fScenarioExitPresent();fScenarioSetAuthoring(true);fScenarioGo(9);window.__oldSpec=JSON.stringify(fScenarioActive().steps[9].checkpoint);window.__sc=fScenarioActive();fScenarioUpdateStep(window.__sc.id,9);true')
 check(ev('JSON.stringify(fScenarioActive().steps[9].checkpoint)===window.__oldSpec'),'Actual author Update preserves exact required question')
 ev('window.__saveOriginal=fScenarioSaveBlob;window.__exportBlob=null;fScenarioSaveBlob=(name,blob)=>(window.__exportBlob=blob,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=window.__saveOriginal;true')
 exp=json.loads(ev('window.__exportBlob.text()'))
 check(exp['scenarioVersion']==2 and exp['steps'][9]['checkpoint']['round']==ROUND,'Actual exported pilot uses version2 and unchanged authored question')
 ev('window.__beforeImport=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File(['+json.dumps(json.dumps(exp,ensure_ascii=False))+'],"alkane-pilot.scenario.json",{type:"application/json"}));true')
 until('MuLERMoCScenario.scenarios.length===window.__beforeImport+1')
 check(ev('JSON.stringify(fScenarioActive().steps[9].checkpoint)===window.__oldSpec'),'Actual FileReader import retains checkpoint metadata')
 # Duplicating an authored step preserves metadata; cloned ID does not grant a receipt.
 ev('fScenarioActive().steps.splice(10,0,JSON.parse(JSON.stringify(fScenarioActive().steps[9])));fScenarioPresentBegin(fScenarioActive().id,20);true');until('MuLERMoCScenario.present')
 check(index()==9 and ev('NameleculeQuizCheckpoints.resolveTarget(fScenarioPresent(),20)===9'),'Edited/duplicated lesson does not reuse original completion')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('authoring-layout-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'authoring-layout-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
