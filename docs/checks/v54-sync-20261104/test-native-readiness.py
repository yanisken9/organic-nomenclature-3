from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/v54-sync-20261104/test-features.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[],'instrumentation':'Holds the vendor-invoked registered callback, then releases its exact delegate; real JSmol engine/models. No direct globaljmol_isReady invocation and no vendor source edit. Controlledcallbackdelay, not network/CDNoutage.'}
preload=call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'''()=>{let info;Object.defineProperty(window,'JSmol_Applet',{configurable:true,get(){return info},set(value){info=value;const registered=value.readyFunction;value.readyFunction=function(applet){window.__nativeReadyCaptured=true;window.__releaseNativeReady=function(){return registered(applet)};};}})}'''})['script']
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=native-readiness-'+str(time.time_ns()));app_ready()
 until('window.__nativeReadyCaptured===true',seconds=60)
 assert ev('!fJSmolLive()&&!!document.querySelector("#nameAnalysis .nameCompBox")')
 out['checks'].append({'actualRegisteredVendorCallbackHeld':True,'2Dname':ev('currentMolName')})
 click('#propene');until('selectedMol==="propene"&&window.__mulerPending3D==="propene"')
 assert ev('currentMolName==="προπένιο"&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
 out['checks'].append({'pendingPropeneDuringActualCallbackDelay':True})
 ev('window.__releaseNativeReady();true')
 until('fJSmolLive()&&window.__mulerPending3D===null',seconds=30)
 until('(()=>{const p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file.endsWith("/propene_3D.sdf")&&p.models[0].atomCount===9})()',seconds=30)
 out['checks'].append({'registeredDelegateReplayedActual9AtomPropene':model()})
 click('#ethane');until('selectedMol==="ethane"')
 until('(()=>{const p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file.endsWith("/ethane_3D.sdf")&&p.models[0].atomCount===8})()',seconds=30)
 out['checks'].append({'subsequentSelectionLoadsActualEthane':True})
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:out['state']=model();screenshot(HERE/'native-readiness-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'native-readiness-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
