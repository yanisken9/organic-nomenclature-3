from pathlib import Path
import os,json,time,traceback
HERE=Path('docs/checks/step-heading-logo-20261106')
meta=json.loads((HERE/'test-processes.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(meta['bidi_port'])
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'rounds':[]}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS',len(out['checks']),label,flush=True)
def click(selector):
 ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent()&&fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")&&!MuLERMoCScenario.checkpointPreparation')
def logo_loaded():
 until('!!document.querySelector("#pageTitle .scStepHeadingImage")&&document.querySelector("#pageTitle .scStepHeadingImage").complete&&document.querySelector("#pageTitle .scStepHeadingImage").naturalWidth>0&&!document.querySelector("#pageTitle .scStepHeadingImage").hidden')
def index():return ev('fScenarioPresent().index')
def goto(i):ev('fScenarioGo('+str(i)+');true');until('!MuLERMoCScenario.checkpointPreparation')
def export_current():
 ev('window.testSave=fScenarioSaveBlob;window.testExport=null;fScenarioSaveBlob=(name,blob)=>(window.testExport=blob,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=testSave;true')
 return json.loads(ev('window.testExport.text()'))
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=heading-logo-20261106#step=4');ready();logo_loaded()
 check(index()==3,'Direct step4 presentation opens requested user lesson')
 check(ev('document.getElementById("pageTitle").textContent.trim()')=='Συνεργείο ονομάτων','Heading retains accessible semantic name')
 check(ev('document.querySelector("#pageTitle img").getAttribute("src")')=='games/assets/name-repair/workshop-logo-3d-v1.png','Accepted local3D workshop logo loaded')
 check(ev('fScenarioPresent().steps.filter(s=>s.titleLogo).length===1&&fScenarioPresent().steps[3].titleLogo==="workshop"'),'Only step4 opts in')
 check(ev('document.querySelector("#scNext").disabled'),'Required quiz remains locked before solving')
 exported=export_current();(HERE/'exported-before-authoring.json').write_text(json.dumps(exported,ensure_ascii=False,indent=2)+'\n')
 check(exported['steps'][3]['titleLogo']=='workshop','Real export retains logo preset')
 check(ev('fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+').ok'),'Exported lesson validates on reimport')
 for width,height in [(1500,1000),(390,844),(844,390)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  ev('new Promise(r=>setTimeout(r,180))');logo_loaded()
  bounds=json.loads(ev('JSON.stringify((()=>{const a=document.querySelector("#pageTitle img").getBoundingClientRect(),h=document.getElementById("pageTitle").getBoundingClientRect();return{x:a.x,y:a.y,width:a.width,height:a.height,right:a.right,innerWidth,hx:h.x,hright:h.right}})())'))
  check(bounds['width']>0 and bounds['x']>=-1 and bounds['right']<=width+1,'Logo fits '+str(width)+'px viewport',bounds)
  screenshot(HERE/('after-step4-'+str(width)+'.png'))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 for i in range(3):
  goto(2);check(index()==2 and not ev('!!document.querySelector("#pageTitle img")'),'Step3 plain title remains plain '+str(i+1))
  goto(3);logo_loaded();check(index()==3,'Return to step4 logo '+str(i+1))
 goto(4);check(index()==3 and ev('document.querySelector("#scNext").disabled'),'Jump past unsolved checkpoint still blocked')
 # Complete the real3round set through its actual UI and canonical engine data.
 ev('window.testMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.testRound=JSON.parse(JSON.stringify(options.round));return testMount(host,options)};true')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testRound')
 for ri in range(3):
  data=json.loads(ev('JSON.stringify(testRound)'));out['rounds'].append({'molecule':data['moleculeId'],'kind':data['kind'],'correctName':data['correctName']})
  if data['kind']=='replace':
   click('[id$="-part-'+data['targetPartId']+'"]')
   choice=next(i for i,c in enumerate(data['choices']) if c['value']==data['correctValue']);click('[id$="-choice-'+str(choice)+'"]')
  else:
   click('[id$="-part-'+data['correctOrder'][0]+'"]');click('[id$="-move-left"]')
  click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector("#scNext").disabled')==(ri<2),'Gate completion logic unchanged round '+str(ri+1))
  click('.round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testRound.id!=='+json.dumps(data['id']))
  else:until('fScenarioPresent().index===4')
 check(not ev('!!document.querySelector("#pageTitle img")'),'After quiz step5 has no stale logo')
 for i in [3,4,2,3,4,3]:
  goto(i);until('fScenarioPresent().index==='+str(i))
  if i==3:logo_loaded()
  else:check(not ev('!!document.querySelector("#pageTitle img")'),'Plain title restored on step'+str(i+1))
 ev('fScenarioPresent().showStepNumbers=true;fScenarioFillStepPanel(fScenarioPresent().steps[3]);true');logo_loaded()
 check(ev('document.querySelector("#pageTitle .scStepNumberTitle").textContent')=='4.','Numbered heading preserves step pill')
 ev('fScenarioPresent().showStepNumbers=false;fScenarioFillStepPanel(fScenarioPresent().steps[3]);true');logo_loaded()
 ev('window.staleHeadingImage=document.querySelector("#pageTitle img");staleHeadingImage.src="games/assets/name-repair/owned-missing-logo-test.png";true')
 until('document.querySelector("#pageTitle img").hidden&&!document.querySelector("#pageTitle .scStepHeadingVisual").classList.contains("is-loaded")')
 check(ev('document.querySelector("#pageTitle .scStepHeadingFallback").getBoundingClientRect().width')>0,'Real missing image shows visible meaningful fallback')
 goto(2);ev('staleHeadingImage.dispatchEvent(new Event("load"));staleHeadingImage.dispatchEvent(new Event("error"));true')
 check(ev('document.getElementById("pageTitle").textContent')==exported['steps'][2]['title'] and not ev('!!document.querySelector("#pageTitle img")'),'Detached image callbacks do not mutate later title')
 goto(3);logo_loaded()
 ev('window.testLessonId=fScenarioPresent().id;MuLERMoCScenario.returnToTheoryLibrary=false;fScenarioExitPresent();true')
 until('!MuLERMoCScenario.present')
 check(not ev('!!document.querySelector("#pageTitle img")') and ev('document.getElementById("pageTitle").textContent')==ev('MuLERMoCScenario.appTitle'),'Exit restores original app title and removes artwork')
 check(not ev('document.getElementById("pageTitle").classList.contains("scStepHeadingHasLogo")'),'Exit removes artwork layout class')
 ev('fScenarioSetAuthoring(true);fScenarioSetActive(testLessonId);fScenarioBuildPanels();true')
 selector='.scenarioPanel[data-scenario-id="'+ev('testLessonId')+'"] .srow[data-idx="3"] .scTitleLogoSelect'
 until('!!document.querySelector('+json.dumps(selector)+')')
 check(ev('document.querySelector('+json.dumps(selector)+').value')=='workshop','Authoring selector reflects imported preset')
 check(ev('document.querySelector('+json.dumps(selector)+').closest("label").textContent.includes("Μορφή τίτλου")'),'Native selector has accessible label')
 ev('fScenarioGo(3);true');until('!MuLERMoCScenario.present&&fScenarioActive().index===3')
 check(not ev('!!document.querySelector("#pageTitle img")'),'Authoring Go preserves app title contract')
 ev('fScenarioUpdateStep(testLessonId,3);true')
 check(ev('fScenarioGet(testLessonId).steps[3].titleLogo==="workshop"'),'Update retains logo')
 ev('fScenarioDuplicateStep(testLessonId,3);true')
 check(ev('fScenarioGet(testLessonId).steps[4].titleLogo==="workshop"'),'Duplicate retains logo')
 # Reorder duplicate with existing UI, preserving attachment to cloned step.
 duplicate_up='.scenarioPanel[data-scenario-id="'+ev('testLessonId')+'"] .srow[data-idx="4"] .scUp'
 click(duplicate_up)
 check(ev('fScenarioGet(testLessonId).steps[3].title.endsWith("(αντίγραφο)")&&fScenarioGet(testLessonId).steps[3].titleLogo==="workshop"'),'Reorder keeps artwork with its step')
 selector='.scenarioPanel[data-scenario-id="'+ev('testLessonId')+'"] .srow[data-idx="3"] .scTitleLogoSelect'
 ev('(()=>{const s=document.querySelector('+json.dumps(selector)+');s.value="";s.dispatchEvent(new Event("change",{bubbles:true}));return true})()')
 check(ev('!Object.prototype.hasOwnProperty.call(fScenarioGet(testLessonId).steps[3],"titleLogo")'),'Clearing selection deletes optional field')
 ev('(()=>{const s=document.querySelector('+json.dumps(selector)+');s.value="workshop";s.dispatchEvent(new Event("change",{bubbles:true}));return true})()')
 check(ev('fScenarioGet(testLessonId).steps[3].titleLogo==="workshop"'),'Selector can re-enable artwork')
 # Roundtrip pristine export through actual FileReader import, not authored mutations.
 ev('window.testImportCount=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File(['+json.dumps(json.dumps(exported,ensure_ascii=False))+'],"roundtrip.json",{type:"application/json"}));true')
 until('MuLERMoCScenario.scenarios.length===testImportCount+1')
 check(ev('fScenarioActive().steps.length===12&&fScenarioActive().steps[3].titleLogo==="workshop"'),'File import restores12steps and artwork')
 roundtrip=export_current();check(roundtrip['steps']==exported['steps'],'Export-import-export preserves full normalized steps')
 # Malicious/invalid values are never used as image URLs or HTML.
 for value in ['javascript:alert(1)','https://example.invalid/logo.png','<img src=x onerror=alert(1)>','__proto__',{},True,None]:
  trial=json.loads(json.dumps(exported));trial['steps'][3]['titleLogo']=value
  result=json.loads(ev('JSON.stringify((()=>{const r=fScenarioValidate('+json.dumps(trial,ensure_ascii=False)+');return{ok:r.ok,removed:!Object.prototype.hasOwnProperty.call(r.steps[3],"titleLogo"),warnings:r.warnings}})())'))
  check(result['ok'] and result['removed'] and any('title logo' in w for w in result['warnings']),'Unsafe/invalid preset discarded '+repr(value))
 legacy=json.loads(Path('scenarios/alkanes-two-part-workshop.scenario.json').read_text())
 ev('window.testLegacy=fScenarioValidate('+json.dumps(legacy,ensure_ascii=False)+');true')
 check(ev('testLegacy.ok&&testLegacy.steps.every(s=>!Object.prototype.hasOwnProperty.call(s,"titleLogo"))'),'Legacy lesson gains no metadata default')
 # Other plain-title lesson through actual presentation path.
 other=json.loads(Path('scenarios/alkenes-nomenclature-branches.scenario.json').read_text())
 ev('window.testOther=fScenarioValidate('+json.dumps(other,ensure_ascii=False)+');window.testCard=fScenarioNew(testOther.title,true);Object.assign(testCard,{showStepNumbers:false,steps:testOther.steps,index:0});fScenarioPresentBegin(testCard.id,0);true')
 until('MuLERMoCScenario.present&&fScenarioPresent().id===testCard.id')
 check(not ev('!!document.querySelector("#pageTitle img")') and ev('document.getElementById("pageTitle").textContent')==other['steps'][0]['title'],'Other-series text heading behavior unchanged')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'after-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['consoleErrors']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')=='error']
 (HERE/'after-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx});call('session.end',{})
 except Exception:pass
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
