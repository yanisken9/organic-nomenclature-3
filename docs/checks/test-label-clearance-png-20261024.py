import socket,base64,os,struct,json,time
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9225),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9225\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
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
def actual_name():return ev("nameComponentsList.filter(Boolean).join('')")
def skeletal_clean():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")

try:
 navigate('mulermoc-nom-50.html?scenario=scenarios/alkadienes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=label-clearance');app_ready()
 until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && selectedMol==='butadiene_1_3' && mainChainPool3DKey==='butadiene_1_3' && window.JSmolReadyFlag===true")
 time.sleep(.5)
 ev("window.__makeURL=URL.createObjectURL.bind(URL);URL.createObjectURL=function(blob){if(blob.type.startsWith('image/svg'))blob.text().then(s=>window.__exportSvg=s);if(blob.type==='image/png')window.__png=blob;return window.__makeURL(blob)};HTMLAnchorElement.prototype.click=function(){window.__download=this.download}")
 for mode in ['condensed','condensedZigZag']:
  ev("mode2D="+json.dumps(mode)+";fLoadMol2D();fShowNameAnalysis();window.__png=null;window.__exportSvg=null;window.__download=null;window.__exportExpected=[...document.querySelectorAll('#jsmeNomeclatureSVG text.svgAtomLabel[id^=C]')].map(e=>({id:e.id,x:e.getAttribute('x')}));fSave2DPng()")
  until('!!window.__png&&!!window.__exportSvg&&!!window.__download',20)
  assert ev("window.__png.size>1000")
  svg=ev('window.__exportSvg');assert 'CH' not in svg or '<tspan' in svg
  assert ev("(()=>{const root=new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml');return JSON.stringify([...root.querySelectorAll('text.svgAtomLabel[id^=C]')].map(e=>({id:e.id,x:e.getAttribute('x')})))===JSON.stringify(window.__exportExpected)})()")
  screenshot('/tmp/label-clearance-lesson-'+mode+'.png')
  print('PASS actual PNG Blob/export SVG label anchors',mode,flush=True)
 assert not js_errors,js_errors
finally:call('session.end',{})
