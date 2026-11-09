from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/alkane-step11-stop-20261109')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
helper=Path('tools/namelecule_bidi.py').read_text().replace("def call(method,params):\n global seq","def call(method,params):\n print('BIDI '+method,flush=True)\n global seq")
exec(compile(helper,'bidi','exec'))
out={'completed':False,'steps':{},'checks':[],'classification':'Developer actual UI evidence; author preview used to inspect11 without fabricating learner receipts'}
def check(ok,desc):
 assert ok,desc
 out['checks'].append(desc);print('PASS '+desc,flush=True)
def click(sel):ev('document.querySelector('+json.dumps(sel)+').click();true')
def ready():
 print('APP_READY_WAIT',flush=True);app_ready();print('APP_READY_OK',flush=True);until('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',45)
def snapshot():
 return json.loads(ev('JSON.stringify({index:fScenarioPresent().index,preview:NameleculeQuizCheckpoints.isPreview(fScenarioPresent()),contentOnly:document.getElementById("pageContainer").classList.contains("scContentOnly"),note:document.getElementById("scStepText").innerHTML,heading:document.getElementById("pageTitle").innerHTML,nextDisabled:document.getElementById("scNext").disabled,ids:[...document.querySelectorAll("[id]")].filter(e=>e.id.match(/viewer|nameAnalysis|molecule|jsme|jsmol|scStepText|pageTitle/i)).map(e=>{const r=e.getBoundingClientRect();return{id:e.id,visible:!!(r.width&&r.height)&&getComputedStyle(e).visibility!=="hidden",display:getComputedStyle(e).display,width:r.width,height:r.height}})})'))
try:
 navigate('design/theory-library.html?v=step11-before-20261109');click('article[aria-labelledby=alkanes-title] a.action');ready()
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3&&!!document.getElementById("nlQuizOpen")',30)
 out['steps']['learner4']=snapshot();check(out['steps']['learner4']['contentOnly'] and out['steps']['learner4']['nextDisabled'],'Before normal learner4 is content-only and blocked')
 ev('fScenarioGo(4);true');until('!!document.getElementById("scCheckpointNotice")&&!document.getElementById("scCheckpointNotice").hidden')
 screenshot(HERE/'before-step4-blocked-desktop.png')
 check(ev('fScenarioPresent().index===3'),'Before jump to5 remains at unsolved4')
 # Direct preview is explicitly separate from learner receipts.
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=step11-author-before-20261109');ready()
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true')
 click('.scenarioPanel.active .srow[data-idx="10"] .scPresentStep');until('MuLERMoCScenario.present&&fScenarioPresent().index===10')
 out['steps']['author11']=snapshot();screenshot(HERE/'before-step11-desktop.png')
 check(out['steps']['author11']['preview'] and not out['steps']['author11']['contentOnly'],'Before preview11 still molecular, unlike4')
 check(ev('document.getElementById("jsmeNomeclatureSVG").getBoundingClientRect().height>0&&document.getElementById("nameAnalysisContainer").getBoundingClientRect().height>0'),'Before11 visibly retains molecule and name')
 check(ev('!!document.getElementById("scStepText").querySelector("b")&&!document.getElementById("pageTitle").querySelector("img")'),'Before11 already renders bold markup but has no workshop logo')
 out['completed']=True
except Exception as exc:
 out['failure']=str(exc);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'before-failure.png')
 except:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'browser-before.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
