"""All14 current lesson structures and representative live presentation transitions.
Cold/settings evidence remains in the preserved frozen-target pre-player-ready attempt.
"""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
out['coldSettingsEvidence']='shell-lessons-browser-before-player-ready.json; first19 checks passed before the separate lesson harness-ready failure'
try:
 navigate('design/theory-library.html?v=55-all-lessons');links=read('[...document.querySelectorAll("a[href*=scenario]")].map(a=>new URL(a.href).searchParams.get("scenario"))');links=list(dict.fromkeys(links));check(len(links)==14,'Library exposes14active lessons')
 out['lessons']=[]
 for path in links:
  data=json.loads((CR/path).read_text());navigate('mulermoc-nom-55.html?v=replay55-'+str(time.time_ns()));app_ready();wait('MuLERMoCScenario.ready===true&&document.readyState==="complete"',60)
  ev('window.__validated=fScenarioValidate('+json.dumps(data,ensure_ascii=False)+');true');check(ev('__validated.ok&&!__validated.warnings.length'),'All steps structurally validate '+path)
  report=read('(()=>{const s=__validated.steps;return{steps:s.length,missingMolecules:s.filter(x=>x.selectedMol&&!nameExamples[x.selectedMol]).map(x=>x.selectedMol),missingForms:s.filter(x=>x.selectedMol&&x.mode2D&&!MOL2D[x.selectedMol]?.[x.mode2D]).map(x=>({key:x.selectedMol,mode:x.mode2D})),checkpoints:s.map((x,i)=>x.checkpoint?i+1:null).filter(Boolean)}})()')
  check(not report['missingMolecules'] and not report['missingForms'],'All snapshots resolve molecule/form '+path,report)
  ev('fScenarioSetAuthoring(true);window.__card=fScenarioNew(__validated.title,true);Object.assign(__card,{scenarioVersion:__validated.scenarioVersion,showStepNumbers:__validated.showStepNumbers,reserveTitleSpace:__validated.reserveTitleSpace,author:__validated.author||"Unknown",steps:__validated.steps,index:0});fScenarioSetActive(__card.id);fScenarioAuthorPreviewBegin(__card.id,0);true')
  wait('MuLERMoCScenario.present&&fScenarioPresent()===__card&&fScenarioPresent().index===0');rows=[]
  for index in sorted(set([0,len(data['steps'])//2,len(data['steps'])-1])):
   ev('fScenarioGo('+str(index)+');true');wait('fScenarioPresent().index==='+str(index)+'&&!MuLERMoCScenario.checkpointPreparation');pause(160)
   row=read('({index:fScenarioPresent().index,selectedMol,mode2D,svg:!!document.querySelector("#jsmeNomeclatureSVG svg"),error:document.querySelector("#jsmeNomeclatureSVG")?.getAttribute("data-label-error"),contentOnly:document.getElementById("pageContainer").classList.contains("scContentOnly")})');rows.append(row)
   check(row['selectedMol']==data['steps'][index].get('selectedMol',row['selectedMol']) and (row['contentOnly'] or row['svg']) and not row['error'],'Representative snapshot'+str(index+1)+' renders '+path,row)
  last=len(data['steps'])-1
  if last:pointer('#scPrev');wait('fScenarioPresent().index==='+str(last-1));pointer('#scNext');wait('fScenarioPresent().index==='+str(last));check(True,'Actual Prev/Next presentation transition '+path)
  out['lessons'].append({'path':path,**report,'representativeSnapshots':rows});ev('MuLERMoCScenario.returnToTheoryLibrary=false;fScenarioExitPresent();true')
 out['totalSteps']=sum(r['steps'] for r in out['lessons']);check(out['totalSteps']==328,'All14 current lesson structures total328steps')
 navigate('mulermoc-nom-54.html?v=legacy-browser-smoke');app_ready();wait('!!document.querySelector("#jsmeNomeclatureSVG svg")');check(ev('Object.keys(nameExamples).length===141&&!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Preserved54 bounded runtime smoke')
 navigate('mulermoc-nom-52.html?v=legacy-browser-smoke');app_ready();wait('!!document.querySelector("#jsmeNomeclatureSVG svg")');check(ev('Object.keys(nameExamples).length===141&&!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Preserved52 bounded runtime smoke')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('lessons-failure');out['failureURL']=ev('location.href');out['failureState']=read('({ready:document.readyState,playerReady:MuLERMoCScenario.ready,authoring:MuLERMoCScenario.authoring,present:MuLERMoCScenario.present,presentId:MuLERMoCScenario.presentId,actual:fScenarioPresent()?.id,card:window.__card&&{id:__card.id,steps:__card.steps.length,index:__card.index},toast:document.getElementById("scenarioToast")?.textContent})')
 except Exception:pass
finally:finish('lessons-browser')
if not out['completed']:raise SystemExit(1)
