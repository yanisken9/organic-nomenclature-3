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




result={'completed':False,'checks':[]}
child=None
def cev(expr):
 r=call('script.evaluate',{'expression':expr,'target':{'context':child},'awaitPromise':True})
 if r.get('type')=='exception':raise RuntimeError(r.get('exceptionDetails'))
 return r['result'].get('value')
def ready():
 global child
 until("!!document.querySelector('.molecule-stage iframe:not([hidden])')")
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
try:
 navigate('react-preview/dist/?transitions='+str(time.time_ns())+'#/viewer');ready()
 ev("window.acks=[];addEventListener('message',e=>{if(e.data?.channel==='namelecule-viewer-v4')acks.push(e.data)})")
 ev("document.querySelector('[data-view=\"3d\"]').click()")
 until("acks.some(a=>a.type==='state' && a.view==='3d')")
 ev("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').click()")
 time.sleep(.15)
 ev("document.querySelector('.molecule-zoom button[aria-label=Σμίκρυνση]').click();document.querySelector('[data-view=\"2d\"]').click()")
 until("acks.some(a=>a.type==='state' && a.id===4 && a.view==='2d')",10)
 assert ev("!document.querySelector('iframe').hidden && !document.querySelector('[role=alert]')")
 assert abs(cev("Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').zoom")-80)<1e-6
 result['zoomAcknowledgements']=json.loads(ev("JSON.stringify(acks.map(a=>({id:a.id,type:a.type,view:a.view})))"))
 result['checks'].append('overlapping native zoom in/out followed immediately by 2D: ordered ACKs and restored 80% camera, no deadlock')
 # Reviewer P2: delayed model load, request 3D -> 2D, immediate zoom.
 ev("document.querySelector('[data-view=\"3d\"]').click()")
 until("!document.querySelector('iframe').hidden")
 cev("window.savedProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)}")
 ev("(()=>{const s=document.querySelector('#molecule-select');s.value='propanone';s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 until("document.querySelector('iframe').hidden")
 ev("document.querySelector('[data-view=\"2d\"]').click()")
 until("document.querySelector('[data-view=\"2d\"]').getAttribute('aria-pressed')==='true'")
 assert ev("[...document.querySelectorAll('.molecule-zoom button')].every(b=>b.disabled)")
 ev("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').click()")
 time.sleep(.2)
 assert ev("document.querySelector('iframe').hidden && !document.querySelector('[role=alert]')")
 cev("Jmol.getPropertyAsArray=window.savedProperty")
 until("!document.querySelector('iframe').hidden")
 assert cev("selectedMol==='propanone' && document.documentElement.dataset.view==='2d' && molZoom2D===2")
 assert not ev("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').disabled")
 ev("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').click()")
 until("acks.some(a=>a.type==='state' && a.molecule==='propanone' && a.view==='2d' && a.zoom===2.5)")
 assert cev("molZoom2D===2.5")
 result['checks'].append('Reviewer P2 regression: pending 3D molecule -> 2D keeps both zoom buttons disabled; premature click sends no command; completion and subsequent zoom succeed')
 # Real model-readiness deadline, not a simulated parent timeout callback.
 cev("window.savedProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[{file:'wrong-model.sdf'}]}:savedProperty(a,p,...r)}")
 started=time.monotonic()
 ev("document.querySelector('[data-view=\"3d\"]').click()")
 until("!!document.querySelector('[role=alert]')",12)
 elapsed=time.monotonic()-started
 assert 8.5<elapsed<12,elapsed
 assert ev("document.querySelector('iframe').hidden && document.querySelector('#molecule-select').disabled && [...document.querySelectorAll('[data-component]')].every(b=>b.disabled)")
 result['modelMismatchFailureSeconds']=round(elapsed,2)
 ev("document.querySelector('[role=alert] button').click()");ready()
 assert cev("selectedMol==='ethanol' && document.documentElement.dataset.view==='2d'")
 result['checks'].append('actual 9s incorrect-model gate fails closed; retry loads fresh valid ethanol in 2D')
 # Unmount during a pending 3D gate and confirm a clean new session.
 cev("window.savedProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)}")
 ev("document.querySelector('[data-view=\"3d\"]').click();location.hash='#/library'")
 until("!document.querySelector('iframe')")
 ev("location.hash='#/viewer'");ready()
 assert cev("selectedMol==='ethanol' && document.documentElement.dataset.view==='2d'")
 assert not ev("!!document.querySelector('[role=alert]')")
 result['checks'].append('unmount during pending 3D readiness then remount gives clean default session')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/v52-react-3d-transitions-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
