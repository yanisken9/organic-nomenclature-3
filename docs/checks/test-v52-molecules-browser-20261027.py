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




import hashlib
result={'completed':False,'moleculeCases':[],'parity':False}
rows={}
try:
 for version in (51,52):
  navigate('mulermoc-nom-'+str(version)+'.html?v=v52-parity-'+str(time.time_ns()));app_ready();until('!!window.JSmolReadyFlag')
  keys=json.loads(ev('JSON.stringify(Object.keys(nameExamples))'));assert len(keys)==126
  for key in keys:
   for mode in ('condensed','expanded','skeletal'):
    for chain in ('algorithmic','data'):
     value=json.loads(ev("JSON.stringify((()=>{selectedMol="+json.dumps(key)+";fInitProps();mode2D="+json.dumps(mode)+";mainChainMode="+json.dumps(chain)+";fLoadMol2D();nameAnalysisMode='none';fShowNameAnalysis();const svg=document.querySelector('#jsmeNomeclatureSVG svg');return {name:currentMolName,common:currentMolCommonName||'',chain:mainChainAtomsList,atoms:allAtomsTypeList,bonds:bondList,svg:svg?JSON.stringify({viewBox:svg.getAttribute('viewBox'),nodes:[...svg.querySelectorAll('line,text,tspan,path,polygon,rect')].filter(e=>!e.closest('defs')).map(e=>({tag:e.tagName,attrs:Object.fromEntries([...e.attributes].filter(a=>!['id','class'].includes(a.name)).map(a=>[a.name,a.value])),text:['text','tspan'].includes(e.tagName)?e.textContent:null}))}):null}})())"))
     assert isinstance(value['name'],str) and value['name'],(version,key,mode,chain)
     token=(key,mode,chain);value['svgSHA256']=hashlib.sha256(value.pop('svg').encode()).hexdigest()
     if version==51:rows[token]=value
     else:
      if value!=rows[token]:
       Path('/tmp/v52-parity-mismatch.json').write_text(json.dumps({'molecule':key,'mode':mode,'chainMode':chain,'before':rows[token],'after':value},ensure_ascii=False,indent=2))
      assert value==rows[token],(key,mode,chain,'See /tmp/v52-parity-mismatch.json')
      result['moleculeCases'].append({'molecule':key,'mode':mode,'chainMode':chain,'name':value['name'],'commonName':value['common'],'svgSHA256':value['svgSHA256'],'exactParity':True})
  print('Completed molecule pass',version,'cases',len(rows),flush=True)
 result['parity']=True;result['completed']=True
 assert not js_errors,js_errors
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/v52-molecules-browser-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['moleculeCases']),'javascriptErrors':len(js_errors)}),flush=True)
