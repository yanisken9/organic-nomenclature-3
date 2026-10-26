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



specs=json.load(open('docs/checks/other-ketones-specs-20261026.json'));rows=[]
try:
 navigate('mulermoc-nom-51.html?v=other-ketones-highlights');app_ready();until('window.JSmolReadyFlag===true')
 # Explicitly enable endpoint-atom highlighting; default bond-only mode has no green atoms.
 ev("$('#bondAtomsCheck').addClass('selectedCheck')")
 for spec in specs:
  key=spec['key'];ev('document.getElementById('+json.dumps(key)+').click()');until('mainChainPool3DKey==='+json.dumps(key))
  prov=json.load(open('mols/new_molecules/'+key+'_3D.provenance.json'));mapping=prov['atomMapping2Dto3D']
  atoms=set()
  for c in spec['carbonyls']:
   atoms.update([c-1,c,c+1])
   atoms.update(b if a==c else a for a,b,o in spec['edges'] if o==2 and c in [a,b] and (a>spec['carbons'] or b>spec['carbons']))
  tests=[('compSuffix' if any(e[2]==3 for e in spec['edges']) else 'compEndNumber',atoms)]
  if any(e[2]==3 for e in spec['edges']):
   tests.append(('compEndNumber',{v for a,b,o in spec['edges'] if o==3 for v in [a,b]}))
  tests.append(('compBondPos' if spec['carbons']>spec['parent'] else 'compNumber1',{v for a,b,o in spec['edges'] if o==2 and a<=spec['carbons'] and b<=spec['carbons'] for v in [a,b]}))
  for component,atoms in tests:
   expected=sorted(mapping[str(i)] for i in atoms)
   print('HIGHLIGHT',key,component,flush=True)
   compid={'compSuffix':'comp9','compEndNumber':'comp7','compBondPos':'comp4','compNumber1':'comp0'}[component]
   ev('document.getElementById('+json.dumps(compid)+').click()')
   until("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').filter(a=>a.color.toLowerCase()==='[xd8eedc]').map(a=>a.atomno).sort((a,b)=>a-b))==="+json.dumps(json.dumps(expected,separators=(',',':'))))
   rows.append(dict(key=key,component=component,expected3DAtoms=expected))
 assert not js_errors,js_errors
 Path('docs/checks/other-ketones-highlights-20261026.json').write_text(json.dumps(dict(cases=rows,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 print('PASS',len(rows),'actual3D carbonyl/double/triple highlight cases,0JSerrors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
