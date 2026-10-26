"""Actual Firefox ketone checks. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
import socket,base64,os,struct,json,time
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
def actual_name():return ev("currentMolName")
def skeletal_clean():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")



specs=json.load(open('docs/checks/ketones-specs-20261026.json'));rows=[]
try:
 navigate('mulermoc-nom-51.html?v=ketones-narrow-20261026');app_ready();until('window.JSmolReadyFlag===true')
 key=specs[-1]['key'];ev('document.getElementById('+json.dumps(key)+').click()')
 until('mainChainPool3DKey==='+json.dumps(key))
 until("Number(Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').zoom)===60")
 for i in range(3):
  ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click()')
  assert ev('mode2D')==['condensed','expanded','skeletal'][i]
 ev('nameAnalysisMode="none";fShowNameAnalysis()')
 screenshot('/tmp/ketones-largest-framing.png')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 for spec in specs:
  key=spec['key'];ev('document.getElementById('+json.dumps(key)+').click()')
  for mode in ['condensed','expanded','skeletal']:
   ev('mode2D='+json.dumps(mode)+';mainChainMode="algorithmic";fLoadMol2D();nameAnalysisMode="none";fShowNameAnalysis()')
   assert actual_name()==spec['name']
   geom=json.loads(ev("""JSON.stringify((()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),labels=[...svg.querySelectorAll('text:not([id^=number])')],outer=svg.getBoundingClientRect();const box=e=>e.getBoundingClientRect();const overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){const a=box(labels[i]),b=box(labels[j]);if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.5)overlaps.push([labels[i].textContent,labels[j].textContent]);}return {overlaps,clipped:labels.filter(e=>{const b=box(e);return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),fonts:labels.map(e=>parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b))};})())"""))
   assert not geom['overlaps'] and not geom['clipped'],(key,mode,geom)
   rows.append(dict(key=key,mode=mode,geometry=geom))
 screenshot('/tmp/ketones-narrow-last.png')
 assert not js_errors,js_errors
 Path('docs/checks/ketones-narrow-20261026.json').write_text(json.dumps(dict(cases=rows,largestZoom3D=60,actualModeRadios=True,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 print('PASS',len(rows),'390px cases; no overlap/clipping,0JSerrors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
