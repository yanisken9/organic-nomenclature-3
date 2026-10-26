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




specs=json.load(open('docs/checks/ketones-specs-20261026.json'));rows=[];completed=False;rapid=None;switched=None;stopped=None;old=None
try:
 navigate('mulermoc-nom-51.html?v=ketone-numbering-test');app_ready();until('window.JSmolReadyFlag===true')
 ev("""window.__nums=()=>[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>e.textContent.trim());window.__tickOrig=fShowNumber;window.__threeOrig=fShowNumber3D;window.__ticks=[];window.__three=[];fShowNumber=function(){const idx=currNumberEl;window.__tickOrig();window.__ticks.push({i:idx,t:performance.now()-window.__start,numbers:window.__nums()});};fShowNumber3D=function(i,a){window.__three.push({i,t:performance.now()-window.__start});return window.__threeOrig(i,a);};""")
 def trace(comp,n):
  return json.loads(ev("""(async()=>{window.__ticks=[];window.__three=[];window.__start=performance.now();document.getElementById("""+json.dumps(comp)+""").click();const immediate=window.__nums();await new Promise(r=>setTimeout(r,"""+str(400*n+250)+"""));return JSON.stringify({immediate,ticks:window.__ticks,three:window.__three,final:window.__nums()});})()"""))
 def check(result,n):
  assert result['immediate']==[],result
  assert [t['i']for t in result['ticks']]==list(range(n)),result
  assert [t['i']for t in result['three']]==list(range(n)),result
  for i,t in enumerate(result['ticks']):
   assert t['numbers']==[str(j)for j in range(1,i+2)],result
   assert t['t']>=300 if i==0 else t['t']-result['ticks'][i-1]['t']>=250,result
  assert result['final']==[str(j)for j in range(1,n+1)],result
 for spec in specs:
  key=spec['key'];print('TRACE',key,flush=True)
  ev('document.getElementById('+json.dumps(key)+').click()');until('mainChainPool3DKey==='+json.dumps(key))
  for mi,mode in enumerate(['condensed','expanded','skeletal']):
   ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(mi)+'].click()')
   for comp in ['comp5','comp0' if spec['carbons']==spec['parent'] else 'comp4']:
    result=trace(comp,spec['parent']);check(result,spec['parent']);rows.append(dict(key=key,mode=mode,component=comp,**result))
 # Also cover the two alkyl-position slots on the largest new ketone.
 for comp in ['comp0','comp2']:
  result=trace(comp,7);check(result,7);rows.append(dict(key=specs[-1]['key'],mode='skeletal',component=comp,**result))
 # Rapid new selection cancels the previous interval and restarts at1.
 rapid=json.loads(ev("""(async()=>{document.getElementById('comp5').click();await new Promise(r=>setTimeout(r,500));window.__ticks=[];window.__three=[];window.__start=performance.now();document.getElementById('comp4').click();const immediate=window.__nums();await new Promise(r=>setTimeout(r,3050));return JSON.stringify({immediate,ticks:window.__ticks,three:window.__three,final:window.__nums()});})()"""));check(rapid,7)
 # Changing mode during animation produces one clean numbered chain.
 switched=json.loads(ev("""(async()=>{document.getElementById('comp5').click();await new Promise(r=>setTimeout(r,500));window.__ticks=[];window.__three=[];window.__start=performance.now();document.querySelectorAll('#radio2DMode .mode2DOption')[1].click();const immediate=window.__nums();await new Promise(r=>setTimeout(r,3050));return JSON.stringify({immediate,ticks:window.__ticks,three:window.__three,final:window.__nums()});})()"""));check(switched,7)
 # Zoom must retain the existing instantaneous complete restoration.
 ev('fZoom2D(1)');assert json.loads(ev('JSON.stringify(window.__nums())'))==[str(i)for i in range(1,8)]
 # Deselecting a molecule stops numbering; no stale tick can append afterward.
 stopped=json.loads(ev("""(async()=>{document.getElementById('comp4').click();await new Promise(r=>setTimeout(r,500));document.getElementById('methane').click();window.__ticks=[];await new Promise(r=>setTimeout(r,1000));return JSON.stringify({ticks:window.__ticks,numbers:window.__nums(),selected:selectedMol});})()"""));assert stopped=={'ticks':[],'numbers':[],'selected':'methane'},stopped
 # A pre-existing molecule keeps immediate locant numbering.
 ev("document.getElementById('methyl_2_propanal').click()")
 until("mainChainPool3DKey==='methyl_2_propanal'")
 ev("document.getElementById('comp0').click()")
 old=json.loads(ev('JSON.stringify(window.__nums())'));assert old==['1','2','3'],old
 assert not js_errors,js_errors
 completed=True
 Path('docs/checks/ketone-numbering-browser-20261026.json').write_text(json.dumps(dict(completed=completed,cases=rows,rapid=rapid,modeSwitch=switched,zoomInstant=True,moleculeCancellation=stopped,oldLocants=old,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 print('PASS',len(rows),'cumulative2D/3D timing cases;rapid/mode/molecule/zoom/oldregression,0JSerrors')
finally:
 if not completed:Path('/tmp/ketone-numbering-partial.json').write_text(json.dumps(dict(cases=rows,rapid=rapid,modeSwitch=switched,moleculeCancellation=stopped,javascriptErrors=js_errors),ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
