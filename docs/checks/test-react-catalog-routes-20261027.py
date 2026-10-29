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
try:
 navigate('react-preview/dist/?v=catalog-routes-'+str(time.time_ns())+'#/')
 until("document.querySelectorAll('main a[href=\"#/viewer\"]').length===2 && document.querySelectorAll('footer a[href=\"#/viewer\"]').length===1")
 ev("document.querySelector('main a[href=\"#/viewer\"]').click()")
 until("!!document.querySelector('.molecule-stage iframe:not([hidden])')",95)
 assert ev("location.hash==='#/viewer' && document.querySelector('#molecule-select option[value=ethanol]')!==null")
 result['checks'].append('All three welcome Explore links target React viewer; actual click loads existing ethanol')
 ev("location.hash='#/library'")
 until("!document.querySelector('iframe') && !!document.querySelector('.lessons')")
 assert ev("document.querySelectorAll('.lessons a[href*=mulermoc-nom-52]').length===12")
 assert ev("!!document.querySelector('.react-preview-banner a[href*=welcome-proposal]')")
 result['checks'].append('Unmount to existing12lesson library; main-version fallback retained')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-catalog-routes-20261027.json').write_text(json.dumps(result,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result),flush=True)
