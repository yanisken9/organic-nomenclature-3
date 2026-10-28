"""Actual Firefox React 2D/name regression with the v4 3D bridge. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
import socket,base64,os,struct,json,time,sys
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9237),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9237\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
b=b''
while b'\r\n\r\n' not in b:b+=s.recv(1)
assert b'101' in b,b
seq=0;js_errors=[]
def exact(n):
 b=b''
 while len(b)<n:
  part=s.recv(n-len(b))
  if not part:raise RuntimeError('WebSocket closed')
  b+=part
 return b
def call(method,params):
 global seq
 seq+=1;payload=json.dumps({'id':seq,'method':method,'params':params}).encode();mask=os.urandom(4);n=len(payload)
 header=bytes([129,128|n]) if n<126 else (bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n))
 s.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(payload)))
 while True:
  h=exact(2);n=h[1]&127
  if n==126:n=struct.unpack('!H',exact(2))[0]
  elif n==127:n=struct.unpack('!Q',exact(8))[0]
  msg=json.loads(exact(n))
  if msg.get('method')=='log.entryAdded':
   item=msg.get('params',{})
   if item.get('level')=='error' and item.get('type')=='javascript':js_errors.append(item)
  if msg.get('id')==seq:
   if msg.get('type')=='error':raise RuntimeError(msg)
   return msg['result']
call('session.new',{'capabilities':{}})
ctx=call('browsingContext.create',{'type':'tab'})['context']
call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
def ev(expr):
 result=call('script.evaluate',{'expression':expr,'target':{'context':ctx},'awaitPromise':True})
 if result.get('type')=='exception':raise RuntimeError(result.get('exceptionDetails'))
 return result['result'].get('value')
def navigate(path):
 call('browsingContext.navigate',{'context':ctx,'url':os.environ.get('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8013/')+path,'wait':'complete'})
def until(expr,seconds=90):
 for _ in range(seconds*2):
  if ev(expr):return
  time.sleep(.5)
 raise AssertionError('Timed out: '+expr)
def app_ready():
 until("typeof jsmeNomeclatureApplet!=='undefined' && !!jsmeNomeclatureApplet && !!nameExamples.methyl_3_butene_1.classification")
def screenshot(path):
 result=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'document'});Path(path).write_bytes(base64.b64decode(result['data']))




result={'completed':False,'versions':{}}
lessons=['alkanes-nomenclature-branches.scenario.json','alkenes-nomenclature-branches.scenario.json','other-ketones-nomenclature.scenario.json']
try:
 for version in (51,52):
  start=len(js_errors);exits=[]
  for lesson in lessons:
   navigate('mulermoc-nom-'+str(version)+'.html?scenario=scenarios/'+lesson+'&present=1&from=theory-library&v=control-'+str(time.time_ns()))
   until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
   app_ready();until('window.JSmolReadyFlag===true')
   source=json.loads(ev('JSON.stringify(fScenarioPresent().steps)'))
   for i,step in enumerate(source):
    ev('fScenarioGo('+str(i)+')')
    until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol'])+' && nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
   exits.append({'lesson':lesson,'timestamp':ev('Date.now()')})
   ev("document.getElementById('scExit').click()")
   until("location.pathname.endsWith('/design/theory-library.html')")
   time.sleep(.4)
  errors=js_errors[start:]
  result['versions'][str(version)]={'lessons':lessons,'exits':exits,'errors':errors}
  print('Lifecycle control',version,'errors',len(errors),flush=True)
 result['baselineReproduces']=bool(result['versions']['51']['errors'])
 known={"TypeError: can't access property \"setDisplay\", this.viewer is null","TypeError: can't access property \"updateJS\", this.viewer is null"}
 result['onlyKnownJSmolSignatures']=all(e.get('text') in known for v in result['versions'].values() for e in v['errors'])
 result['completed']=True
finally:
 Path('/tmp/v52-jsmol-lifecycle-control-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'baselineReproduces':result.get('baselineReproduces'),'onlyKnownJSmolSignatures':result.get('onlyKnownJSmolSignatures')},ensure_ascii=False),flush=True)
