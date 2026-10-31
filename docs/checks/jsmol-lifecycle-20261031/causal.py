from pathlib import Path
import os,json,gzip,time,traceback
root=Path('/tmp/namelecule-jsmol-lifecycle-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8027/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
preload=call('script.addPreloadScript',{'functionDeclaration':(root/'observe.js').read_text()})['script']
out={'cases':[],'completed':False,'scope':'Controlled teardown experiments, not ordinary user failure frequency or production fix'}
try:
 for repeat in range(2):
  for kind,cancel in [('raf',False),('raf',True),('resize',False),('resize',True)]:
   navigate('app/mulermoc-nom-52.html?audit=controlled-'+kind+'-'+str(cancel)+'-'+str(repeat));app_ready();until('window.JSmolReadyFlag===true&&!!jmolAppletNomeclature?._appletPanel?.viewer');time.sleep(.5)
   start=len(js_errors)
   result=json.loads(ev("""(()=>{const a=jmolAppletNomeclature,kind=KIND,cancel=CANCEL,ids=[],original=requestAnimationFrame;window.requestAnimationFrame=function(cb){const id=original.call(window,cb);ids.push(id);return id};try{if(kind==='raf')Jmol.repaint(a,true);else a._resize()}finally{window.requestAnimationFrame=original}const resizeKey='__resizeTimeout_'+a._id,timer=Jmol[resizeKey];if(cancel){for(const id of ids)cancelAnimationFrame(id);if(kind==='resize'&&timer){clearTimeout(timer);Jmol[resizeKey]=null}}__life.log('controlled-teardown',{kind,cancel,ids,timer:!!timer});Jmol._destroy(a);return JSON.stringify({ids,timer:!!timer,state:__life.state()})})()""".replace('KIND',json.dumps(kind)).replace('CANCEL',json.dumps(cancel))))
   time.sleep(.4);events=json.loads(ev('JSON.stringify(__life.rows)'))
   row={'repeat':repeat,'kind':kind,'cancelPending':cancel,'result':result,'javascriptErrors':js_errors[start:],'events':events};out['cases'].append(row);print(repeat,kind,'cancel',cancel,'errors',[(e['text']) for e in row['javascriptErrors']],flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['bidiEvents']=all_events;(root/'controlled-teardown.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{})
