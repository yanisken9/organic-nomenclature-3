"""Bounded diagnostic: same saved first gate, normal vs deferred loader release."""
from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/alkanes-two-part-20261105/browser/support.py').read_text(),'support','exec'))
LESSON='mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1'
fixture=json.loads((HERE/'two-part-browser.json').read_text())['finalStorage']
preload=None;out={'completed':False,'variants':[]}
FUNCTION=r'''()=>{
 const rows=[];const epoch=Date.now()+'-'+Math.random();window.testTrace={rows,epoch};let leaving=false;
 function state(){const a=window.jmolAppletNomeclature,p=a?._appletPanel||a?._applet,v=p?.viewer;return {ready:window.JSmolReadyFlag===true,live:!!window.Jmol?._nameleculeLifecycle?.live?.(a),panel:!!p,viewer:!!v,platform:!!v?.gdata?.platform,atoms:v?.ms?.ac,closing:leaving,loading:document.documentElement.classList.contains('lesson-loading'),step:typeof fScenarioPresent==='function'?fScenarioPresent()?.index:null}}
 function log(kind,detail){const row={kind,detail,epoch,date:Date.now(),state:state()};rows.push(row);if(['error','beforeunload','pagehide'].includes(kind))console.info('RESTORETRACE '+JSON.stringify(row))}
 addEventListener('beforeunload',()=>{leaving=true;log('beforeunload')},true);addEventListener('pagehide',()=>log('pagehide'));
 addEventListener('error',e=>log('error',{message:e.message,stack:e.error?.stack}));addEventListener('unhandledrejection',e=>log('error',{rejection:String(e.reason)}));
 function wrap(o,k){if(!o||typeof o[k]!=='function'||o[k].testWrapped)return;let original=o[k];function wrapped(...args){log(k+':before',k==='fJSmolScript'?String(args[1]).slice(0,100):null);if(k==='fLessonLoadingDone'&&new URL(location.href).searchParams.get('deferLoader')==='1'&&args[0]===false&&String(new Error().stack).includes('fScenarioPrepareCheckpointTarget')){log('suppressedEarlyLoader');return}try{return original.apply(this,args)}finally{log(k+':after')}}wrapped.testWrapped=true;o[k]=wrapped}
 const timer=setInterval(()=>{for(const k of ['fScenarioGo','fScenarioApply','fJSmolScript','fLessonLoadingDone'])wrap(window,k);for(const k of ['_destroy'])wrap(window.Jmol,k)},10);
 addEventListener('pagehide',()=>clearInterval(timer));
}'''
try:
 preload=call('script.addPreloadScript',{'functionDeclaration':FUNCTION,'contexts':[ctx]})['script']
 for variant in ['normal','deferred-loader']:
  start_errors=len(js_errors)
  navigate(LESSON+('&deferLoader=1' if variant!='normal' else '')+'#step=4');app_ready();until('typeof MuLERMoCScenario!=="undefined"&&MuLERMoCScenario.present&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation')
  ev('sessionStorage.clear();Object.entries('+json.dumps(fixture,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,JSON.stringify(v)));history.replaceState(null,"","#step=5");true')
  call('browsingContext.reload',{'context':ctx,'wait':'complete'});app_ready();until('typeof MuLERMoCScenario!=="undefined"&&MuLERMoCScenario.present&&fScenarioPresent().index===4&&!MuLERMoCScenario.checkpointPreparation');ev('new Promise(r=>setTimeout(r,800))')
  rows=json.loads(ev('JSON.stringify(testTrace.rows)'))
  out['variants'].append({'variant':variant,'errors':js_errors[start_errors:],'trace':rows})
  print(variant,'errors',len(js_errors)-start_errors,flush=True)
 out['completed']=True
except Exception as exc:out['failure']=str(exc);out['traceback']=traceback.format_exc()
finally:
 out['traceConsole']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('text','').startswith('RESTORETRACE')]
 (HERE/'restoration-trace.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 if preload:call('script.removePreloadScript',{'script':preload})
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'failure':out.get('failure')}),flush=True)
