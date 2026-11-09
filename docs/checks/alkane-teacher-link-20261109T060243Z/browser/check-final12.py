"""Targeted final12 author rehearsal after preserved successful6repair normal traversal."""
from pathlib import Path
p=Path(__file__).resolve().parent/'check-prefix.py';source=p.read_text().split('\ntry:\n cr=Path(candidate')[0].replace("HERE/'browser.json'","HERE/'final12-browser.json'")
exec(compile(source,'prefix-shared-helpers','exec'))
out={'completed':False,'role':'Developer targeted final12 author rehearsal; not independent review','checks':[],'geometry':[],'models3D':[],'notes':['Normal actual6repair flow reached12 and passed in normal-six-repairs.json; its erroneous2D-vs3D count comparator was stopped and preserved. This targeted run uses actual sourceSDF atom counts.','No sessionStorage writes or solved receipts fabricated/restored; author rehearsal mode used only for final12 molecules/representation/zoom/resize checks.'],'limitations':['Owned headless Firefox; desktop/mobile viewport emulation only','Author rehearsal complements normal6repair traversal; no second full normal replay','No Safari/physical mobile/screen reader/conference guarantee; externalJSmol/fonts retained'],'candidateSHA256':hashlib.sha256((HERE.parent/'candidate.json').read_bytes()).hexdigest()}
try:
 cr=Path(candidate['candidateRoot']);check(all(hashlib.sha256((cr/k).read_bytes()).hexdigest()==sha for k,sha in candidate['files'].items()),'All282 candidate hashes match frozen metadata')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1});navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=teacher-final12-targeted');ready();ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true');pointer('.scenarioPanel.active .srow[data-idx="11"] .scPresentStep');wait('MuLERMoCScenario.present&&fScenarioPresent().index===11&&NameleculeQuizCheckpoints.isPreview(fScenarioPresent())',30);check(True,'Actual authored final12 opened in explicit rehearsal mode')
 keys=read('fScenarioPresent().steps[11].menuSubset');check(len(keys)==8,'Final12 has8alkanes')
 for width,height in [(1280,800),(390,760)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});dismiss_rotate()
  for key in keys:
   pointer('#'+key);wait('selectedMol==='+json.dumps(key),15)
   for mode in ['condensed','expanded']+([] if key=='methane' else ['skeletal']):
    idx={'condensed':1,'expanded':2,'skeletal':3}[mode];pointer('#radio2DMode .mode2DOption:nth-child('+str(idx)+')');wait('mode2D==='+json.dumps(mode),15);geometry(key,mode,width)
   if key=='methane':check(ev('document.querySelectorAll("#radio2DMode .mode2DOption")[2].classList.contains("disabledRadio")&&!nameExamples.methane.structure2D_Skeletal'),'Methane skeletal choice disabled '+str(width))
   if width==1280:
    file=ev('nameExamples['+json.dumps(key)+'].file3D');expected=int((cr/file).read_text().splitlines()[3][:3]);wait('(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length==='+str(expected)+'}catch(e){return false}})()',25)
    model=read('({key:selectedMol,file:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length})');model['expectedFromSourceSDF']=expected;out['models3D'].append(model);check(True,key+' actual3D prefixedURL and sourceSDF atom count')
  shot('targeted-step12-'+str(width))
 check(not out.get('geometryExceptions'),'All46 available2D forms fit full drawing at1280/390')
 check(len(out['models3D'])==8,'All8 actual3D models verified')
 pointer('#zoomInBtn');pointer('#zoomOutBtn');check(ev('selectedMol==="ethyl_3_dimethyl_2_5_hexane"&&mode2D==="skeletal"'),'Mobile zoom pair preserves final molecule/mode');out['resources']=read('performance.getEntriesByType("resource").map(r=>({name:r.name,initiatorType:r.initiatorType,duration:r.duration,responseStatus:r.responseStatus}))');check(all(hashlib.sha256((cr/k).read_bytes()).hexdigest()==sha for k,sha in candidate['files'].items()),'Candidate282files unchanged after targeted checks');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('targeted-final12-failure');out['failureURL']=ev('location.href')
 except Exception as e:out['captureFailure']=str(e)
finally:
 out['allDiagnosticEntries']=[e['params'] for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level') in ['error','warn']];save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'forms':len(out['geometry']),'models3D':len(out['models3D']),'pageErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
