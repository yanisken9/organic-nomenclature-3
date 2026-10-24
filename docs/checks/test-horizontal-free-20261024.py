"""Actual Firefox lesson checks. Artifacts only under /tmp; requires localhost8013/BiDi9236."""
import socket,base64,os,struct,json,time
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9236),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9236\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
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




rows=[]
try:
 navigate('mulermoc-nom-50.html?v=horizontal-free-test');app_ready();until('window.JSmolReadyFlag===true')
 ev("mainChainMode='algorithmic';selectedMol='dimethyl_2_3_butane';fSelectMol()")
 until("mainChainPool3DKey==='dimethyl_2_3_butane'")
 for mode in ['condensed','expanded','skeletal']:
  ev('mode2D='+json.dumps(mode)+";mainChainMode='algorithmic';fLoadMol2D();fCalcMainChain3D();fShowNameAnalysis();nameAnalysisMode='compNumber1';fExplainNameComp()")
  assert ev('JSON.stringify(mainChainAtomsList)')=='[1,2,3,4]',(mode,ev('JSON.stringify(mainChainAtomsList)'))
  until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===4")
  assert ev("fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)")
  assert not ev("fScenarioShowComponentRule('compCarbonsCount')")
  screenshot('/tmp/horizontal-free-'+mode+'.png')
  idx=ev('mainChainPoolIdx');ev('fStepMainChain(1)');assert ev('mainChainPoolIdx')!=idx
  assert ev("fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)")
  rows.append({'mode':mode,'preferred':[1,2,3,4],'manualStepper':True})
 Path('/tmp/horizontal-free-evidence.json').write_text(json.dumps({'forms':rows,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 print('PASS free exploration three forms + numbering + manual stepper')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
