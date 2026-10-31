from pathlib import Path
import os,json,gzip,time,traceback
root=Path('/tmp/namelecule-jsmol-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8030/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
preload=call('script.addPreloadScript',{'functionDeclaration':(root/'observe.js').read_text()})['script']
out={'cases':[],'completed':False}
try:
 for repeat in range(2):
  for version in ['baseline','main']:
   for kind in ['raf','resize','entryAfterDestroy','lateDeliveredFrame','resizeAfterDestroy']:
    navigate(version+'/mulermoc-nom-52.html?audit=causal-'+kind+'-'+str(repeat));app_ready();until('window.JSmolReadyFlag===true&&!!jmolAppletNomeclature?._appletPanel?.viewer');time.sleep(.5)
    assert ev("!!Jmol._nameleculeLifecycle")== (version=='main')
    before=len(js_errors)
    r=json.loads(ev("""(()=>{const a=jmolAppletNomeclature,kind=KIND;let captured=null,id=null,caught=null,pageRAF=false,pageTimer=false;const nativeRAF=requestAnimationFrame;if(kind==='lateDeliveredFrame')window.requestAnimationFrame=function(cb){captured=cb;id=nativeRAF.call(window,cb);return id};try{if(kind==='raf'||kind==='lateDeliveredFrame')Jmol.repaint(a,true);if(kind==='resize')a._resize()}finally{window.requestAnimationFrame=nativeRAF}if(kind==='lateDeliveredFrame')cancelAnimationFrame(id);requestAnimationFrame(()=>window.__pageRAF=true);setTimeout(()=>window.__pageTimer=true,40);Jmol._destroy(a);try{if(kind==='entryAfterDestroy')Jmol.repaint(a,false);if(kind==='lateDeliveredFrame')captured();if(kind==='resizeAfterDestroy')a._resize()}catch(e){caught=String(e)}return JSON.stringify({caught,captured:!!captured,viewer:!!a._appletPanel?.viewer})})()""".replace('KIND',json.dumps(kind))))
    time.sleep(.3);r['pageWork']=json.loads(ev('JSON.stringify({raf:window.__pageRAF,timer:window.__pageTimer})'));r.update(version=version,repeat=repeat,kind=kind,javascriptErrors=js_errors[before:]);r['events']=json.loads(ev('JSON.stringify(__life.rows)'));out['cases'].append(r);print(version,repeat,kind,'errors',len(r['javascriptErrors']),'caught',r['caught'],flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['bidiEvents']=all_events;(root/'causal.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{});print('complete',out['completed'],flush=True)
