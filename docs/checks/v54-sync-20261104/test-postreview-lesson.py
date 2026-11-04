from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/v54-sync-20261104/test-final-interactions.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[]}
try:
 path='scenarios/other-carboxylic-acids-nomenclature.scenario.json';source=json.loads(Path(path).read_text());steps=source['steps'];n=len(steps);last=steps[-1]
 navigate('mulermoc-nom-54.html?scenario='+path+'&present=1&from=theory-library&v=post-review-'+str(time.time_ns())+'#step='+str(n))
 until('typeof fScenarioPresent==="function"&&MuLERMoCScenario.ready&&fScenarioPresent().index==='+str(n-1)+'&&!document.documentElement.classList.contains("lesson-loading")')
 until('window.JSmolReadyFlag===true&&selectedMol==='+json.dumps(last['selectedMol']))
 until('(()=>{let p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()',seconds=30)
 check(True,'Cold direct final3Dstep loads actual correct model',model())
 click('#scPrev');until('fScenarioPresent().index==='+str(n-2))
 check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Actual Previous returns2D drawing')
 click('#scNext');until('fScenarioPresent().index==='+str(n-1))
 until('(()=>{let p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()',seconds=30)
 check(True,'Next reloads final3Dmodel after2D')
 call('browsingContext.activate',{'context':ctx});ev('document.getElementById("scNext").focus();window.__lastKeys=[];document.addEventListener("keydown",e=>window.__lastKeys.push({key:e.key,target:e.target.id}));true')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':'\ue00c'},{'type':'keyUp','value':'\ue00c'}]}]})
 until('location.pathname.endsWith("/design/theory-library.html")',seconds=20)
 check(True,'Actual keyboardEscape returns theorylibrary')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:out['keyEvents']=ev('JSON.stringify(window.__lastKeys)');screenshot(HERE/'postreview-lesson-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['externalCIR']=[e for e in js_errors if 'cactus.nci.nih.gov'in e.get('text','')and'404'in e.get('text','')]
 out['applicationErrors']=[e for e in js_errors if e not in out['externalCIR']]
 (HERE/'postreview-lesson-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or out['applicationErrors']:raise SystemExit(1)
