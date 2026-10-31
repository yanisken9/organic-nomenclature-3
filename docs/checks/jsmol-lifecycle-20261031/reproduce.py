from pathlib import Path
import os,json,time,gzip,traceback
root=Path('/tmp/namelecule-jsmol-lifecycle-20261031');repo=Path.cwd()
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8027/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
preload=call('script.addPreloadScript',{'functionDeclaration':(root/'observe.js').read_text()})['script']
out={'runs':[],'completed':False}
lesson='scenarios/saturated-monoaldehydes-nomenclature.scenario.json';source=json.loads((repo/lesson).read_text())['steps'];last=len(source)-1
snapshot="""JSON.stringify((()=>{let model,atoms,error;try{model=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo');atoms=Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length}catch(e){error=String(e)}return {state:__life.state(),model,atoms,error,expected:selectedMol?new URL(nameExamples[selectedMol].file3D,document.baseURI).href:null}})())"""
def savepage(row):
 row['events']=json.loads(ev('JSON.stringify(__life.rows)'));row['errorsSoFar']=len(js_errors)
try:
 for i in range(4):
  row={'round':i,'steps':[]};out['runs'].append(row)
  navigate('app/mulermoc-nom-52.html?scenario='+lesson+'&present=1&audit=lifecycle-'+str(i))
  app_ready();until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')")
  for method,idx in [('initial',0),('next',1),('prev',0),('jump',last-1),('next',last)]:
   if method=='jump':ev('fScenarioGo('+str(idx)+');true')
   elif method!='initial':ev('document.getElementById('+json.dumps('scNext'if method=='next'else'scPrev')+').click();true')
   until('fScenarioPresent().index==='+str(idx))
   row['steps'].append({'index':idx,'snapshot':json.loads(ev(snapshot))})
  time.sleep(2)
  row['settled']=json.loads(ev(snapshot));savepage(row)
  print('round',i,'viewer',row['settled']['state']['viewer'],'atoms',row['settled'].get('atoms'),'errors',len(js_errors),flush=True)
  if i%2==0:
   ev('fScenarioGo(0);true');until('fScenarioPresent().index===0');savepage(row)
  else:
   ev('document.getElementById("scExitPresent").click();true') if ev('!!document.getElementById("scExitPresent")') else ev('fScenarioExitPresent();true')
   time.sleep(.3);savepage(row)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 try:
  out['finalSnapshot']=json.loads(ev(snapshot));out['finalPageEvents']=json.loads(ev('JSON.stringify(__life.rows)'))
 except Exception as e:out['finalReadFailure']=str(e)
 out['javascriptErrors']=js_errors;out['bidiEvents']=all_events
 (root/'reproduction.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
 call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{})
 print('complete',out['completed'],'runs',len(out['runs']),'errors',len(js_errors),flush=True)
