"""Controlled slow-readiness and synchronous absent-API checks, not CDN certification."""
from pathlib import Path
import os,json,traceback
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104'
os.environ['NAMELECULE_BIDI_PORT']='9244';os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'controlledReadiness':True,'realCDNOutage':False,'checks':[]}
preload=call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'''()=>{Object.defineProperty(window,'JSmolReadyFlag',{configurable:true,get(){return false},set(v){window.__testReadyAttempt=v}})}'''})['script']
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=readiness-check');app_ready()
 until('!!document.querySelector("#nameAnalysis .nameCompBox")')
 assert ev('!fJSmolLive()')
 out['checks'].append({'cold2DNamingDespiteUnreadiness':ev('currentMolName')})
 ev('selectedMol="propene";fSelectMol();true')
 assert ev('currentMolName==="προπένιο"&&window.__mulerPending3D==="propene"')
 out['checks'].append({'pendingMoleculeSelection':True,'2D':ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')})
 until('window.__testReadyAttempt===true',seconds=60)
 ev('delete window.JSmolReadyFlag;window.JSmolReadyFlag=true;jmol_isReady(jmolAppletNomeclature);true')
 until('(()=>{const p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file.endsWith("/propene_3D.sdf")})()',seconds=30)
 out['checks'].append({'readyResendCorrectModel':True})
 # Isolate only synchronous select/API absence; restore before any real
 # vendor callbacks can run. This does not simulate an absent library boot.
 row=json.loads(ev('JSON.stringify((()=>{const saved=window.Jmol;try{window.Jmol=undefined;selectedMol="ethane";fSelectMol();return {name:currentMolName,svg:!!document.querySelector("#jsmeNomeclatureSVG svg"),pending:window.__mulerPending3D}}finally{window.Jmol=saved}})())'))
 assert row['name']=="αιθάνιο"and row['svg']and row['pending']=='ethane',row
 out['checks'].append({'syncMissingAPIDegrades2D':row})
 ev('jmol_isReady(jmolAppletNomeclature);true')
 until('(()=>{const p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,"modelInfo");return p&&p.models.length===1&&p.models[0].file.endsWith("/ethane_3D.sdf")})()',seconds=30)
 out['checks'].append({'APIRecoveryCorrectModel':True})
 out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['error','warn']]
 (HERE/'readiness-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'appErrors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
