"""Cold v55 startup, language/name modes, all14 structural replay plus representative presentation."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
def mode(m):
 if ev('mode2D')!=m:pointer('#radio2DMode .mode2DOption:nth-child('+str({'condensed':1,'expanded':2,'skeletal':3}[m])+')')
 wait('mode2D==='+json.dumps(m)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
try:
 navigate('mulermoc-nom-55.html?lang=gr&v=cold55-'+str(time.time_ns()));app_ready();call('browsingContext.activate',{'context':ctx});wait('window.JSmolReadyFlag===true',60)
 out['environment']=read('({userAgent:navigator.userAgent,url:location.href,jsmolVersion:Jmol._version,jquery:$.fn.jquery})')
 check(ev('Object.keys(nameExamples).length===141&&Object.values(MOL2D).reduce((n,v)=>n+Object.values(v).filter(s=>typeof s==="string"&&!!s.trim()).length,0)===422'),'Cold55 startup has141 molecules/422forms')
 check(ev('[...document.scripts].some(s=>s.src.includes("mulermoc-nom-core-55.js"))&&[...document.scripts].some(s=>s.src.includes("mulermoc-nom-molview-55.js"))'),'Cold55 actual core/viewer55 scripts loaded')
 wait('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))===5',40);check(True,'Cold real methane3D has5atoms')
 check(visible('#newMolBtn') and visible('#editMolBtn') and ev('!!document.querySelector("#saveMolBtn")'),'New/Edit and SaveAll chrome exists')
 # Keep initial real external lookup failures before controlling later authoring fixtures.
 out['coldExternalLookupState']=read('({entry:nameExamples.methane,info:document.getElementById("molInfoPanel")?.textContent})')
 call('script.addPreloadScript',{'functionDeclaration':'() => { window.MULER_QUIET_FETCH = true; }','contexts':[ctx]});ev('window.MULER_QUIET_FETCH=true;true');out['oracleSweepPolicy']='Quiet-fetch supported setting prevents naming service calls during language/14lesson/legacy sweeps. Initial cold methane oracle attempt is real.'
 for lang in ['gr','en','gr']:
  if ev('fMulerLang()')!=lang:pointer('#langSwitch [data-lang="'+lang+'"]');wait('typeof fMulerLang==="function"&&fMulerLang()==='+json.dumps(lang)+'&&document.readyState==="complete"');app_ready()
  pointer('#ethyl_4_isopropyl_3_methyl_2_hexanal');wait('selectedMol==="ethyl_4_isopropyl_3_methyl_2_hexanal"&&!!document.querySelector("#radioSubstNaming")')
  labels=read('[...document.querySelectorAll("#viewerSettingsPanel [data-lang],#controls3D [data-lang]")].map(e=>({key:e.dataset.lang,actual:[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.nodeValue.trim()).filter(Boolean).join(" "),expected:fMulerT(e.dataset.lang),widget:e.id==="atomSymbolsCheck"?!!e.querySelector(".checkBox"):true}))');check(len(labels)==10 and all(r['actual']==r['expected']and r['widget']for r in labels),lang+' settingsregistry/barlabels translatewithoutlosingwidgets',labels);check(ev('document.querySelector("#controls3D #atomSymbolsCheck")&&!document.querySelector("#customMolSetting")&&Array.isArray(MULER_VIEWER_SETTINGS)'),lang+' latestsettingsregistry andsingleSaveAlllocation')
  before=read('({name:currentMolName,text:document.querySelector("#nameAnalysis").textContent})');pointer('#radioSubstNaming [data-subst-mode="sys"]');wait('substNamingMode==="sys"');after=read('({name:currentMolName,text:document.querySelector("#nameAnalysis").textContent})')
  check(before['text']!=after['text'],lang+' actual traditional/common→systematic name display changes',{'before':before,'after':after})
  pointer('#radioSubstNaming [data-subst-mode="school"]');wait('substNamingMode==="school"');check(ev('!!document.querySelector("#nameAnalysis [id^=comp]")'),lang+' name components remain selectable')
  component=ev('[...document.querySelectorAll("#nameAnalysis [id^=comp]")].find(n=>n.getBoundingClientRect().width>0)?.id');pointer('#nameAnalysis #'+component);pause();check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),lang+' component selection keeps2D viewer usable')
 shot('name-systematic-gr')
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
 try:shot('shell-lessons-failure');out['failureURL']=ev('location.href');out['failureState']=read('({ready:document.readyState,playerReady:MuLERMoCScenario.ready,authoring:MuLERMoCScenario.authoring,present:MuLERMoCScenario.present,presentId:MuLERMoCScenario.presentId,actual:fScenarioPresent()?.id,card:window.__card&&{id:__card.id,steps:__card.steps.length,index:__card.index},toast:document.getElementById("scenarioToast")?.textContent})')
 except Exception:pass
finally:finish('shell-lessons-browser')
if not out['completed']:raise SystemExit(1)
