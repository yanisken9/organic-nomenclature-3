"""Bounded actual final3D paint capture after cold lesson load (Developer evidence)."""
from pathlib import Path
import os,json,time,traceback,hashlib
ROOT=Path.cwd();HERE=ROOT/'docs/checks/alkane-checkpoint-pilot-20261104/legacy'
os.environ['NAMELECULE_BIDI_PORT']='9245'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
previous=json.loads((HERE/'lessons-browser.json').read_text())
paths=list(previous['sourceHashesEnd'])
def hashes():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'sourceHashesStart':hashes(),'limits':['Developer check, not independent review.','One cold desktop final3D paint capture; no mobile geometry or offline assurance.']}
PAINT="""(()=>{const c=document.querySelector('#nomeclature3D canvas');if(!c)return {canvas:false};const g=c.getContext('2d');if(!g)return {canvas:true,context2D:false};const d=g.getImageData(0,0,c.width,c.height).data;let nonWhite=0,samples=0;for(let i=0;i<d.length;i+=64){samples++;if(d[i+3]>0&&(d[i]<235||d[i+1]<235||d[i+2]<235))nonWhite++;}return {canvas:true,context2D:true,width:c.width,height:c.height,samples,nonWhite};})()"""
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=legacy-paint-'+str(time.time_ns())+'#step=21')
 until("typeof fScenarioPresent==='function' && MuLERMoCScenario.ready && fScenarioPresent().index===20 && !document.documentElement.classList.contains('lesson-loading')")
 app_ready();until('window.JSmolReadyFlag===true')
 until("(()=>{const p=fJSmolGetPropertyAsArray(jmolAppletNomeclature,'modelInfo');return p&&p.models.length===1&&p.models[0].atomCount===32&&p.models[0].file.endsWith('/ethyl_3_dimethyl_2_5_hexane_3D.sdf')})()",seconds=30)
 until('('+PAINT+').nonWhite>20',seconds=20)
 out['model']=json.loads(ev("JSON.stringify(fJSmolGetPropertyAsArray(jmolAppletNomeclature,'modelInfo'))"))
 out['paint']=json.loads(ev('JSON.stringify('+PAINT+')'))
 screenshot(HERE/'actual-3d-cold-alkane-last.png')
 out['completed']=True
except Exception as exc:
 out.update(failure=str(exc),traceback=traceback.format_exc())
 try:screenshot(HERE/'actual-3d-cold-failure.png')
 except Exception:pass
finally:
 out['sourceHashesEnd']=hashes();out['changedDuringRun']=[p for p,h in out['sourceHashesStart'].items() if out['sourceHashesEnd'].get(p)!=h]
 out['javascriptErrors']=js_errors
 out['diagnostics']=[e['params'] for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level') in ['error','warn']]
 (HERE/'actual-model-paint.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'failure':out.get('failure'),'paint':out.get('paint'),'errors':len(js_errors),'changedDuringRun':out['changedDuringRun']}))
if not out['completed'] or js_errors:raise SystemExit(1)
