"""Developer actual Firefox: page lifecycle, export and unaffected lesson paths."""
from pathlib import Path
import json,re,time,traceback,hashlib
exec(compile(Path('docs/checks/alkanes-two-part-20261105/browser/support.py').read_text(),'support','exec'))
LESSON='mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1'

def ready():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")');call('browsingContext.activate',{'context':ctx})
try:
 navigate(LESSON+'#step=4');ready()
 ev('window.testAnalyze=NameleculeChemistryClient.analyze;NameleculeChemistryClient.analyze=(m,o)=>new Promise((resolve,reject)=>setTimeout(()=>testAnalyze(m,o).then(resolve,reject),1000));true')
 click('#nlQuizOpen');until('!!document.querySelector(".nl-quiz-loading")');click('#nlQuizBack')
 initial=state();ev('fScenarioGo(11);window.testPending=MuLERMoCScenario.checkpointPreparation;true');until('!!MuLERMoCScenario.checkpointPreparation')
 ev('window.dispatchEvent(new PageTransitionEvent("pagehide",{persisted:true}));true');ev('new Promise(r=>setTimeout(r,1400))')
 check(ev('testPending.controller.signal.aborted&&!MuLERMoCScenario.checkpointPreparation') and state()==initial,'Page exit cancels old validation and prevents late snapshot apply')
 ev('window.dispatchEvent(new PageTransitionEvent("pageshow",{persisted:true}));true');until('!MuLERMoCScenario.checkpointPreparation&&!!document.querySelector("#nlQuizOpen")',seconds=30)
 check(index()==3 and ev('location.hash')=='#step=4','Cached return revalidates original destination and clamps incomplete set')
 initial=state();ev('window.dispatchEvent(new PageTransitionEvent("pagehide",{persisted:true}));window.dispatchEvent(new PageTransitionEvent("pageshow",{persisted:true}));true')
 check(ev('!!document.querySelector("#nlQuizOpen")') and state()==initial,'Cached return recreates quiz entry without resetting live viewer')
 # Actual browser history return, which may use BFCache or perform a new load.
 navigate('design/theory-library.html');until('location.pathname.endsWith("theory-library.html")')
 call('browsingContext.traverseHistory',{'context':ctx,'delta':-1});ready();until('!!document.querySelector("#nlQuizOpen")')
 check(index()==3,'Actual browser Back restores a usable checkpoint')
 # Version2 export includes both recipes and every final gallery permission.
 ev('window.testSave=fScenarioSaveBlob;window.testExport=null;fScenarioSaveBlob=(name,blob)=>(window.testExport=blob,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=testSave;true')
 exported=json.loads(ev('window.testExport.text()'));check(exported['app']=='mulermoc-nom-54' and exported['scenarioVersion']==2 and len(exported['steps'])==12,'New lesson export retains version2 and12steps')
 check([i for i,s in enumerate(exported['steps']) if 'checkpoint' in s]==[3,10],'Export retains both mandatory checkpoints')
 ev('window.testValidated=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+');true');check(ev('testValidated.ok&&!testValidated.warnings.length'),'Export/import validates without warnings')
 # All other13 existing library lessons still use the synchronous common path.
 links=re.findall(r'scenario=([^&]+)',Path('design/theory-library.html').read_text())
 links=[p for p in links if not p.endswith('alkanes-two-part-workshop.scenario.json')]
 check(len(links)==13,'Thirteen other lesson links preserved')
 out['otherLessons']=[]
 ev('MuLERMoCScenario.returnToTheoryLibrary=false;fScenarioExitPresent();true')
 for path in links:
  data=json.loads(Path(path).read_text())
  ev('window.testLesson=fScenarioValidate('+json.dumps(data,ensure_ascii=False)+');true')
  check(ev('testLesson.ok&&!testLesson.warnings.length'),'Validate unaffected '+data.get('title',path))
  ev('window.testCard=fScenarioNew(testLesson.title,true);Object.assign(testCard,{scenarioVersion:testLesson.scenarioVersion,showStepNumbers:testLesson.showStepNumbers,reserveTitleSpace:testLesson.reserveTitleSpace,author:testLesson.author||"Unknown",steps:testLesson.steps,index:0});fScenarioSetActive(testCard.id);fScenarioPresentBegin(testCard.id,0);true')
  until('MuLERMoCScenario.present&&fScenarioPresent()===testCard&&fScenarioPresent().index===0')
  check(ev('!MuLERMoCScenario.checkpointPreparation&&!document.querySelector("#nlQuizCheckpoint")&&!document.querySelector("#scNext").disabled'),'Ordinary lesson starts synchronously '+data.get('title',path))
  last=len(data['steps'])-1;ev('fScenarioGo('+str(last)+');true');until('fScenarioPresent().index==='+str(last))
  until('!MuLERMoCScenario.pending3D||MuLERMoCScenario.pending3D.done',seconds=30)
  check(ev('selectedMol')==data['steps'][-1]['selectedMol'] and ev('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG").getAttribute("data-label-error")'),'Final snapshot/drawing '+data.get('title',path))
  click('#scPrev');until('fScenarioPresent().index==='+str(last-1));click('#scNext');until('fScenarioPresent().index==='+str(last))
  check(not ev('!!MuLERMoCScenario.checkpointPreparation'),'Ordinary Prev/Next retains sync behavior')
  out['otherLessons'].append({'path':path,'steps':len(data['steps']),'finalMol':ev('selectedMol')})
  ev('fScenarioExitPresent();true')
 out['completed']=True
except Exception as exc:
 out['failure']=str(exc);out['traceback']=traceback.format_exc()
 try:screenshot_here('compatibility-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['consoleErrors']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')=='error']
 (HERE/'compatibility-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
