"""Actual Firefox lesson checks. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
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



specs=json.load(open('docs/checks/other-aldehydes-specs-20261026.json'));rows=[]
try:
 navigate('mulermoc-nom-51.html?v=other-aldehydes-test-20261026')
 app_ready();until('window.JSmolReadyFlag===true')
 for spec in specs:
  key=spec['key'];print('CHECK',key,flush=True)
  ev('document.getElementById('+json.dumps(key)+').click()')
  until('selectedMol==='+json.dumps(key)+' && mainChainPool3DKey==='+json.dumps(key))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(len(spec['xy'])+int(spec['formula'].split('H')[1].split('O')[0])))
  assert ev("!!functionalGroupObj3D.aldehyde"),(key,'3D classification')
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   for chain in ['algorithmic','data']:
    ev('mode2D='+json.dumps(mode)+';mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();nameAnalysisMode="none";fShowNameAnalysis()')
    assert ev('currentMolName')==spec['name'],(key,mode,chain,actual_name())
    assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)'),(key,mode,chain)
    texts=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].map(e=>e.textContent.trim()))"))
    if mode=='expanded':assert texts.count('C')==spec['carbons'] and texts.count('H')==int(spec['formula'].split('H')[1].split('O')[0]) and texts.count('O')==len(spec['xy'])-spec['carbons'],(key,texts)
    geom=json.loads(ev("""JSON.stringify((()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),labels=[...svg.querySelectorAll('text:not([id^=number])')],outer=svg.getBoundingClientRect();const box=e=>e.getBoundingClientRect();const overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){const a=box(labels[i]),b=box(labels[j]);if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.5)overlaps.push([labels[i].textContent,labels[j].textContent]);}return {overlaps,clipped:labels.filter(e=>{const b=box(e);return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),fonts:labels.map(e=>parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b))};})())"""))
    assert not geom['overlaps'] and not geom['clipped'],(key,mode,chain,geom)
    if mode=='expanded':
     for slot in [1,2]:
      comp='comp'+str(2*slot-1)
      if not ev('!!document.getElementById('+json.dumps(comp)+')'):continue
      ev('document.getElementById('+json.dumps(comp)+').click()')
      expected=ev('JSON.stringify((()=>{const a=new Set(fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms);for(const b of bondList3D){if(a.has(b[0])&&allAtomsTypeList3D[b[1]-1]==="H")a.add(b[1]);if(a.has(b[1])&&allAtomsTypeList3D[b[0]-1]==="H")a.add(b[0]);}return [...a].sort((a,b)=>a-b)})())')
      until("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').filter(a=>a.color.toLowerCase()==='[xd8eedc]').map(a=>a.atomno).sort((a,b)=>a-b))==="+json.dumps(expected))
    rows.append(dict(molecule=key,mode=mode,chainMode=chain,name=actual_name(),texts=texts,geometry=geom))
   if mode in ['expanded','condensed','skeletal']:screenshot('/tmp/other-aldehydes-'+key+'-'+mode+'.png')
 assert not js_errors,js_errors
 Path('docs/checks/other-aldehydes-browser-20261026.json').write_text(json.dumps(dict(cases=rows,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 print('PASS',len(rows),'browser cases, names/3Dgraphs/explicitH/labels/highlights,0 JS errors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
