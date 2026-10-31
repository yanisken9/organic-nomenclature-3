from pathlib import Path
import os,json,gzip,time,traceback
root=Path('/tmp/namelecule-jsmol-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8030/slow/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
preload=call('script.addPreloadScript',{'functionDeclaration':(root/'observe.js').read_text()})['script']
out={'flows':[],'completed':False}
try:
 version='main'
 navigate(version+'/mulermoc-nom-52.html?audit=active-switches');app_ready();until('window.JSmolReadyFlag===true')
 out['loadedFunctions']=json.loads(ev("JSON.stringify({repaint:String(Jmol.repaint),destroy:String(Jmol._destroy),resize:String(jmolAppletNomeclature._resize),panelDestroy:String(jmolAppletNomeclature._appletPanel.destroy),panelUpdate:String(jmolAppletNomeclature._appletPanel.update),panelDimension:String(jmolAppletNomeclature._appletPanel.setScreenDimension)})"))
 out['environment']=json.loads(ev("JSON.stringify({userAgent:navigator.userAgent,jsmolVersion:Jmol._version,engine:Jmol.getPropertyAsArray(jmolAppletNomeclature,'appletInfo'),jquery:$.fn.jquery,resources:performance.getEntriesByType('resource').filter(r=>/JSmol|corejmol|corescript/.test(r.name)).map(r=>({name:r.name,start:r.startTime,end:r.responseEnd}))})"))
 for i in range(3):
  before=len(js_errors)
  ev("new Promise(resolve=>{const keys=['methane','propene','pentanoic_acid','ethyl_4_isopropyl_3_methyl_2_hexanal'];let i=0;function pick(){const key=keys[i++];document.getElementById(key).click();if(i<keys.length)setTimeout(pick,30);else resolve(true)}pick()})")
  until("(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m?.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href}catch(e){return false}})()",seconds=15)
  time.sleep(2)
  out['flows'].append(json.loads(ev("JSON.stringify({round:"+str(i)+",state:__life.state(),model:Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo'),atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length,expected:new URL(nameExamples[selectedMol].file3D,document.baseURI).href})")))
  out['flows'][-1]['javascriptErrors']=js_errors[before:]
  print('active flow',i,'atoms',out['flows'][-1]['atoms'],'errors',len(js_errors)-before,flush=True)
 # The active 3D eye toggle is an actual user control, not direct DOM hiding.
 before=len(js_errors)
 ev('document.getElementById("view3DBtn").click();true');time.sleep(.3)
 ev('document.getElementById("view3DBtn").click();true');time.sleep(.4)
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':900,'height':800},'devicePixelRatio':1});time.sleep(.4)
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});time.sleep(.5)
 out['toggleResize']=json.loads(ev("JSON.stringify({state:__life.state(),models:Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length})"));out['toggleResize']['javascriptErrors']=js_errors[before:]
 screenshot(str(root/('active-3d-'+version+'.png')));out['pageEvents']=json.loads(ev('JSON.stringify(__life.rows)'));out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;out['bidiEvents']=all_events;(root/('active-flows-'+version+'.json.gz')).write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{});print('complete',out['completed'],'errors',len(js_errors),flush=True)
