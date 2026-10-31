"""Real propene UI numbering/highlights/zoom/labels and native PNG generation.
Capture uses JSmol's existing local-file-save hook, avoiding an external download.
"""
from pathlib import Path
import os,json,gzip,time,traceback,base64,struct
root=Path('/tmp/namelecule-svg-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
helper=(root/'bidi.py').read_text().replace("call('session.new',{'capabilities':{}})","call('session.new',{'capabilities':{'alwaysMatch':{'unhandledPromptBehavior':'ignore'}}})")
helper=helper.replace('seq=0;js_errors=[];all_events=[]','''seq=0;js_errors=[];all_events=[];promptRecords=[]
def reply_prompt(params):
 payload=json.dumps({'id':1000000+len(promptRecords),'method':'browsingContext.handleUserPrompt','params':{'context':params['context'],'accept':True,'userText':params.get('defaultValue','')}}).encode();mask=os.urandom(4);n=len(payload)
 header=bytes([129,128|n]) if n<126 else bytes([129,254])+struct.pack('!H',n)
 s.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(payload)))''')
helper=helper.replace("  if msg.get('method')=='log.entryAdded':","  if msg.get('method')=='browsingContext.userPromptOpened':\n   promptRecords.append(msg['params']);reply_prompt(msg['params'])\n  if msg.get('method')=='log.entryAdded':")
helper=helper.replace("['log.entryAdded']","['log.entryAdded','browsingContext.userPromptOpened']")
exec(compile(helper,'bidi-with-native-prompt-answer','exec'))
out={'completed':False}
try:
 navigate('main/mulermoc-nom-52.html?audit=actual-controls');app_ready();until('window.JSmolReadyFlag===true');ev('document.getElementById("propene").click();true')
 until("(()=>{try{return Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length===9&&Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0].file===new URL(nameExamples.propene.file3D,document.baseURI).href}catch(e){return false}})()");time.sleep(1)
 out['before']=json.loads(ev('JSON.stringify({chain:mainChainAtoms3D,orientation:Jmol.getPropertyAsArray(jmolAppletNomeclature,"orientationInfo"),atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo")})'))
 ev('document.getElementById("comp5").click();true');time.sleep(2)
 out['numbered']=json.loads(ev('JSON.stringify({mode:nameAnalysisMode,chain:mainChainAtoms3D,shapes:Jmol.getPropertyAsArray(jmolAppletNomeclature,"shapeInfo"),atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo"),numbers2D:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(n=>n.textContent)})'))
 r=out['numbered'];assert r['mode']=='compCarbonsCount';assert r['numbers2D']==['1','2','3'],r['numbers2D']
 echoes=r['shapes']['Echo'][0];atoms={a['atomno']:a for a in r['atoms']}
 for i,n in enumerate(r['chain'],1):
  item=echoes['thegroupecho'+str(i)];assert item['text']==str(i);assert all(abs(a-b)<1e-6 for a,b in zip(item['xyz'],atoms[n]['coord']))
 assert all(a['color'].lower()=='[xd8eedc]' for a in r['atoms'] if a['atomno'] in r['chain'])
 assert all(a['color'].lower()!='[xd8eedc]' for a in r['atoms'] if a['elemno']==1)
 screenshot(str(root/'actual-numbering-main.png'))
 # Real zoom controls must alter zoom and preserve echoes/highlight.
 out['zoomBefore']=json.loads(ev('JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,"orientationInfo"))'))
 ev('document.getElementById("zoomIn3DBtn").click();true');time.sleep(1.5)
 out['zoomIn']=json.loads(ev('JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,"orientationInfo"))'));assert out['zoomIn']['zoom']>out['zoomBefore']['zoom']
 ev('document.getElementById("zoomOut3DBtn").click();true');time.sleep(1.5)
 out['zoomOut']=json.loads(ev('JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,"orientationInfo"))'));assert out['zoomOut']['zoom']<out['zoomIn']['zoom']
 out['afterZoomShapes']=json.loads(ev('JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,"shapeInfo"))'));assert len(out['afterZoomShapes']['Echo'][0])==6
 # Toggle atom labels off and back via actual control; record native state each time.
 out['labelsBefore']=ev('Jmol.evaluateVar(jmolAppletNomeclature,"{*}.label")')
 ev('document.getElementById("atomSymbolsCheck").click();true');time.sleep(.5)
 out['labelsOff']=ev('Jmol.evaluateVar(jmolAppletNomeclature,"{*}.label")')
 ev('document.getElementById("atomSymbolsCheck").click();true');time.sleep(.5)
 out['labelsRestored']=ev('Jmol.evaluateVar(jmolAppletNomeclature,"{*}.label")')
 assert out['labelsBefore']==out['labelsRestored'] and out['labelsBefore']!=out['labelsOff']
 ev('window.__png=null;Jmol._localFileSaveFunction=function(name,data){const bytes=typeof data==="string"?null:Uint8Array.from(data,v=>v&255);window.__png={name,base64:bytes?btoa(Array.from(bytes,v=>String.fromCharCode(v)).join("")):data};return true};document.getElementById("save3DBtn").click();true')
 until('window.__png!==null',seconds=30);png=json.loads(ev('JSON.stringify(__png)'));raw=base64.b64decode(png['base64']);assert raw[:8]==b'\x89PNG\r\n\x1a\n';size=struct.unpack('!II',raw[16:24]);assert size==(1200,1200),size
 (root/'native-main-3d.png').write_bytes(raw);out['png']={'filename':png['name'],'dimensions':list(size),'bytes':len(raw),'handoff':'native JSmol _localFileSaveFunction capture; no external download'};time.sleep(.7)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['prompts']=promptRecords;out['javascriptErrors']=js_errors;(root/'controls3d.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('controls complete',out['completed'],'errors',len(js_errors),flush=True)
