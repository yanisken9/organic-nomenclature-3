from pathlib import Path
import os,json,traceback,time,hashlib
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104'
os.environ['NAMELECULE_BIDI_PORT']='9244';os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'sourceHashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in Path('js').glob('*54.js')}}
def click(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 p=json.loads(ev('(()=>{const n=document.querySelector('+json.dumps(selector)+');const b=n.getBoundingClientRect(),hit=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return JSON.stringify({x:b.x+b.width/2,y:b.y+b.height/2,receivesClick:n.contains(hit),hit:hit&&hit.outerHTML.slice(0,300)})})()'))
 assert p['receivesClick'],(selector,p)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def model():
 return json.loads(ev('JSON.stringify({ready:window.JSmolReadyFlag,live:fJSmolLive(),pending:window.__mulerPending3D||null,model:fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo")||null})'))
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=features-'+str(time.time_ns()));app_ready()
 until('window.JSmolReadyFlag===true',seconds=60)
 until('!!fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo")&&fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo").models.length===1',seconds=30)
 out['checks'].append({'coldBoot3D':model()})
 for key in ['propene','dimethyl_2_3_butane','penten_2_yn_4_oic_acid','isopropyl_2_3_dimethylbutanoate']:
  ev('document.getElementById('+json.dumps(key)+').click();true')
  until('selectedMol==='+json.dumps(key),seconds=15)
  until('(()=>{const p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()',seconds=30)
  out['checks'].append({'selected':key,'3D':model(),'name':ev('currentMolName')})
 screenshot(HERE/'features-3d.png')
 click('#molInfoBtn');until('document.querySelector("#moleculeInfo").classList.contains("open")')
 out['checks'].append({'infoPanel':ev('document.querySelector("#moleculeInfo").innerText')})
 ev('fNameExpandOpen();true');until('window.nameExpanded===true')
 ev('fNameExpandClose();true');until('window.nameExpanded===false')
 out['checks'].append({'nameExpandedRoundtrip':True})
 ev('document.getElementById("propene").click();true')
 until('selectedMol==="propene"',seconds=15)
 out['beforeLang']=json.loads(ev('JSON.stringify({url:location.href,lang:fMulerLang(),stepLang:window.__mulerStepLang})'))
 print('3D/info/expanded-name checks passed; switching language',flush=True)
 click('[data-lang="en"]');until('location.search.includes("lang=en")&&typeof fMulerLang==="function"&&fMulerLang()==="en"',seconds=20);app_ready()
 until('selectedMol==="propene"')
 out['checks'].append({'languageEN':ev('document.querySelector("#nameAnalysis .nameCompContainer").textContent'),'selected':ev('selectedMol')})
 click('[data-lang="gr"]');until('location.search.includes("lang=gr")&&typeof fMulerLang==="function"&&fMulerLang()==="gr"',seconds=20);app_ready()
 out['checks'].append({'languageGR':ev('currentMolName'),'selected':ev('selectedMol')})
 # Preserve the same real drawing whose reload loss was recorded before.
 ev('document.getElementById("originalJSMECheck").click();true')
 click('#newMolBtn');until('!!window.MulerDraft')
 ev('jsmeEditDraftApplet.readMolFile(window.MOL2D.propene.condensed);true')
 out['beforeReloadDraft']=ev('fMolDraftReadDrawing().smiles')
 assert out['beforeReloadDraft']
 click('[data-lang="en"]')
 assert ev('!!window.MulerDraft&&fMulerLang()==="gr"')
 assert ev('fMolDraftReadDrawing().smiles')==out['beforeReloadDraft']
 out['checks'].append({'draftLanguageReloadBlocked':True,'drawingPreserved':True})
 click('#molDraftCancelBtn');until('!window.MulerDraft')
 click('[data-lang="en"]');until('location.search.includes("lang=en")&&typeof fMulerLang==="function"&&fMulerLang()==="en"',seconds=20);app_ready()
 out['checks'].append({'languageSwitchAfterCancel':True})
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:out['failureState']=model();out['languageState']=json.loads(ev('JSON.stringify({url:location.href,lang:fMulerLang(),stepLang:window.__mulerStepLang})'));screenshot(HERE/'features-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['error','warn']]
 (HERE/'features-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
