from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/workshop-stop-only-20261106')
meta=json.loads((HERE/'test-process.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(meta['bidi_port'])
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[]}
url='mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=workshop-stop-only-20261106-r1#step=4'
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS',name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def visible(id):return ev('document.getElementById('+json.dumps(id)+').getClientRects().length>0')
def ready():
 app_ready();until('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")')
def stop_hidden():
 return ev('["viewerCol","analysisCol","menuCol","jsmeNomeclatureSVG","nomeclature3D","nameAnalysisContainer","nameAnalysisExplain","ruleTheoryContainer","radio2DMode","controls3D"].every(id=>document.getElementById(id).getClientRects().length===0)')
try:
 navigate(url);ready();until('!!document.querySelector("#pageTitle .scStepHeadingVisual.is-loaded")')
 check(ev('fScenarioPresent().index===3&&fScenarioPresent().steps.length===12'),'Step4 imports as one of twelve steps')
 check(stop_hidden(),'Step4 hides molecule, naming, controls and entire empty columns')
 check(visible('pageTitle') and visible('scStepText') and visible('nlQuizOpen'),'Logo, instructions and Workshop entry remain visible')
 check(ev('document.querySelector("#nlQuizOpen").textContent')=='πήγαινε στο συνεργείο','Authored entry label retained')
 check(ev('document.querySelector("#scNext").disabled'),'Mandatory gate still locked')
 check(ev('!document.getElementById("scStepText").style.getPropertyValue("--scStepTextFitWidth")'),'No stale width reserved for hidden molecular columns')
 for width,height in [(1280,900),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  ev('new Promise(r=>setTimeout(r,150))')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  check(stop_hidden(),'Hidden columns stay hidden after resize '+str(width))
  check(ev('(()=>{let b=document.querySelector("#nlQuizOpen").getBoundingClientRect();return b.width>0&&b.left>=0&&b.right<=innerWidth&&b.height>=44})()'),'Workshop button fits viewport '+str(width))
  screenshot(HERE/('after-'+str(width)+'.png'))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':900},'devicePixelRatio':1})
 ev('fScenarioGo(2);true');until('fScenarioPresent().index===2')
 check(visible('viewerCol') and visible('analysisCol') and visible('jsmeNomeclatureSVG'),'Step3 restores molecular columns and 2D')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation')
 check(stop_hidden(),'Return 3→4 hides columns again')
 ev('fShowNameAnalysis();true')
 check(stop_hidden(),'Naming rebuild does not reveal hidden content')
 # Probe the shared visibility mechanism in memory, without changing saved steps.
 ev('window.testLesson=fScenarioPresent();window.testStep=testLesson.steps[3];window.savedStep=JSON.parse(JSON.stringify(testStep));window.savedTitle=testLesson.title;testStep.show.rule=true;fScenarioApplyNamingChrome(testStep.show);true')
 check(visible('analysisCol') and not visible('viewerCol'),'Explicit rule keeps analysis shell available when naming is hidden')
 ev('testStep.show.rule=false;testLesson.title="Αλκάνια-Ονοματολογία και διακλαδώσεις";testStep.nameAnalysisMode="compCarbonsCount";fScenarioApplyNamingChrome(testStep.show);true')
 check(visible('analysisCol'),'Effective component rule keeps analysis shell available')
 ev('testLesson.title=savedTitle;testStep.nameAnalysisMode="none";testStep.show.alkoxyRule=true;fScenarioApplyNamingChrome(testStep.show);true')
 check(visible('analysisCol'),'Effective alkoxy rule keeps analysis shell available')
 ev('testLesson.steps[3]=savedStep;fScenarioChrome(savedStep.show);true')
 check(stop_hidden(),'Restoring authored flags hides all molecular UI')
 ev('fScenarioExitPresent();true')
 check(ev('!MuLERMoCScenario.present') and visible('viewerCol') and visible('analysisCol'),'Exit restores both outer columns for authoring')
 check(visible('viewerVisBtns') and visible('nameAnalysisContainer'),'Exit restores viewer settings and naming access')
 ev('fScenarioPresentBegin(fScenarioActive().id,3);true');ready()
 check(stop_hidden(),'Reenter step4 returns to Workshop-only presentation')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")')
 check(ev('fScenarioPresent().index===3&&document.querySelector("#scNext").disabled'),'Quiz opens in place and preserves gate')
 click('#nlQuizBack')
 check(stop_hidden() and visible('nlQuizOpen'),'Returning unsolved quiz restores the clean Workshop stop')
 ev('window.testMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(h,o){window.testRound=JSON.parse(JSON.stringify(o.round));return testMount(h,o)};true')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testRound')
 for ri in range(3):
  d=json.loads(ev('JSON.stringify(testRound)'))
  if d['kind']=='replace':
   click('[id$="-part-'+d['targetPartId']+'"]')
   idx=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue'])
   click('[id$="-choice-'+str(idx)+'"]')
  else:
   click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]')
  click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector("#scNext").disabled')==(ri<2),'Three required repairs gate: round '+str(ri+1))
  click('.round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testRound.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
 check(visible('viewerCol') and visible('analysisCol') and visible('jsmeNomeclatureSVG'),'Completed quiz proceeds to step5 with molecular panels restored')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 check(stop_hidden() and not ev('document.querySelector("#scNext").disabled'),'Completed Workshop stop remains clean and unlocked')
 ev('window.testSave=fScenarioSaveBlob;window.testExport=null;fScenarioSaveBlob=(n,b)=>(window.testExport=b,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=testSave;true')
 exported=json.loads(ev('testExport.text()'))
 source=json.loads(Path('scenarios/alkanes-user-3.scenario.json').read_text())
 check(exported['steps']==source['steps'],'Export preserves every authored step including visibility flags')
 (HERE/'exported.json').write_text(json.dumps(exported,ensure_ascii=False,indent=2)+'\n')
 ev('window.testCount=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File(['+json.dumps(json.dumps(exported,ensure_ascii=False))+'],"roundtrip.json",{type:"application/json"}));true')
 until('MuLERMoCScenario.scenarios.length===testCount+1')
 check(ev('fScenarioActive().steps[3].show.viewers["2D"]===false&&fScenarioActive().steps[3].show.naming===false&&fScenarioActive().steps.length===12'),'FileReader reimport retains Workshop-only flags and twelve steps')
 # Existing receipts are reconstructed before proceeding past a checkpoint.
 navigate(url.replace('#step=4','#step=5'));ready()
 check(ev('fScenarioPresent().index===4') and visible('viewerCol'),'Reload revalidates completed repairs and restores step5 destination')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 check(stop_hidden() and not ev('document.querySelector("#scNext").disabled'),'Revalidated completion retains clean unlocked Workshop stop')
 ev('fScenarioGo(10);true');until('fScenarioPresent().index===10&&!MuLERMoCScenario.checkpointPreparation')
 check(visible('viewerCol') and visible('analysisCol') and visible('jsmeNomeclatureSVG'),'Unchanged step11 still shows its molecule and naming')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1#step=4');ready()
 check(visible('viewerCol') and visible('analysisCol') and visible('jsmeNomeclatureSVG'),'Canonical lesson retains its existing molecular presentation')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
