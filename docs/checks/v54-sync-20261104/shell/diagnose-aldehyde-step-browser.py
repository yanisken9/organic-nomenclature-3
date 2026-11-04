from pathlib import Path
import os,json,time,traceback
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104/shell'
os.environ['NAMELECULE_BIDI_PORT']='9245'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'rows':[]}
try:
 for version in [52,54]:
  navigate('mulermoc-nom-'+str(version)+'.html?scenario=scenarios/saturated-monoaldehydes-nomenclature.scenario.json&present=1&from=theory-library&v=aldehyde-diagnostic-'+str(time.time_ns())+'#step=21')
  until("typeof fScenarioPresent==='function' && MuLERMoCScenario.ready && fScenarioPresent().steps.length===24 && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();time.sleep(.5)
  state=json.loads(ev("JSON.stringify({version:"+str(version)+",index:fScenarioPresent().index,molecule:selectedMol,mode:nameAnalysisMode,name:currentMolName,sourceMode:fScenarioPresent().steps[fScenarioPresent().index].nameAnalysisMode,components:[...document.querySelectorAll('#nameAnalysis .nameCompBox')].map(x=>({id:x.id,selected:x.classList.contains('selected'),text:x.textContent,html:x.outerHTML})),chain:mainChainAtomsList,componentMap:(typeof fScenarioModeBoxId==='function'?fScenarioModeBoxId('compSecondSub2'):null),groups:typeof prefixSubs==='undefined'?null:prefixSubs})"))
  out['rows'].append(state);screenshot(HERE/('aldehyde-step21-v'+str(version)+'.png'))
 out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc())
finally:
 out['javascriptErrors']=js_errors;(HERE/'aldehyde-step21-diagnostic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
