"""Actual visible JSmol model checks for14 final lessonsteps and Prev/Next recovery."""
from pathlib import Path
import os,json,time,traceback,hashlib,re
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104/shell'
os.environ['NAMELECULE_BIDI_PORT']='9245';os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
paths=re.findall(r'scenario=([^&]+)',(ROOT/'design/theory-library.html').read_text())
out={'completed':False,'checks':0,'rows':[],'sourceHashesStart':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'js').glob('*54.js')}}
def check(ok,label,detail=None):
 out['checks']+=1
 if not ok:raise AssertionError(label+': '+str(detail))
try:
 for i,path in enumerate(paths):
  source=json.loads((ROOT/path).read_text());last=source['steps'][-1]
  navigate('mulermoc-nom-54.html?scenario='+path+'&present=1&from=theory-library&v=3d-probe-'+str(time.time_ns())+'#step='+str(len(source['steps'])))
  until("typeof fScenarioPresent==='function' && MuLERMoCScenario.ready && fScenarioPresent().steps.length>0 && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true')
  sdf=ev('nameExamples[selectedMol].file3D');p=(ROOT/sdf).resolve();check(p.is_relative_to(ROOT),'Runtime3D source stays inrepo')
  expected=int(p.read_text().splitlines()[3][:3])
  atomexpr="Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))"
  until('fScenarioPresent().index==='+str(len(source['steps'])-1)+' && '+atomexpr+'==='+str(expected),seconds=30)
  state=json.loads(ev("JSON.stringify({title:fScenarioPresent().title,molecule:selectedMol,atomCount:"+atomexpr+",live:fJSmolLive(),orientation:fScenarioGetMoveto(),canvas:!!document.querySelector('#nomeclature3D canvas'),height:document.getElementById('nomeclature3D').clientHeight,width:document.getElementById('nomeclature3D').clientWidth})"))
  check(state['live'] and state['atomCount']==expected,'Actual final3D model '+str(i+1),state)
  check(state['canvas'] and state['height']>0 and state['width']>0,'Actual final3D canvas '+str(i+1),state)
  if i in [0,7,13]:
   time.sleep(.25);screenshot(HERE/('visible3d-lesson-'+str(i+1)+'.png'))
  ev("document.getElementById('scPrev').click()")
  until(atomexpr+'===0',seconds=20)
  check(True,'Previous2D step clears hidden3D '+str(i+1))
  ev("document.getElementById('scNext').click()")
  until(atomexpr+'==='+str(expected),seconds=30)
  check(True,'Next restores real3D model '+str(i+1))
  out['rows'].append({'path':path,'file3D':sdf,'expectedAtoms':expected,'state':state})
  print('Actual3D checked',i+1,expected,state['title'],flush=True)
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:
  out['failureState']=json.loads(ev("JSON.stringify({href:location.href,molecule:selectedMol,ready:window.JSmolReadyFlag,live:fJSmolLive(),count:Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count')),orientation:fScenarioGetMoveto(),step:fScenarioPresent().index})"));screenshot(HERE/'visible3d-failure.png')
 except Exception as sub:out['diagnosticFailure']=str(sub)
finally:
 out['javascriptErrors']=js_errors;out['sourceHashesEnd']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'js').glob('*54.js')}
 out['changedDuringRun']=[p for p,h in out['sourceHashesStart'].items() if out['sourceHashesEnd'].get(p)!=h]
 (HERE/'visible3d-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':out['checks'],'lessons':len(out['rows']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
