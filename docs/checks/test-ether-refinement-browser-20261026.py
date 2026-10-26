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



specs=[r for r in json.loads(Path('docs/checks/ethers-specs-20261026.json').read_text()) if r['key'] in ['ethyl_isopropyl_ether','ethyl_sec_butyl_ether','tert_butyl_isopropyl_ether']];rows=[]
try:
 navigate('mulermoc-nom-51.html?v=ethers-test-20261026')
 app_ready();until('window.JSmolReadyFlag===true')
 ev("window.__coloredEtherAtoms=()=>Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').filter(a=>a.color.toLowerCase()==='[xd8eedc]').map(a=>a.atomno).sort((a,b)=>a-b);window.__etherWithH=(cs)=>{const atoms=new Set(cs);for(const b of bondList3D){if(atoms.has(b[0])&&allAtomsTypeList3D[b[1]-1]==='H')atoms.add(b[1]);if(atoms.has(b[1])&&allAtomsTypeList3D[b[0]-1]==='H')atoms.add(b[0]);}return [...atoms].sort((a,b)=>a-b)}")
 # Expanded glyph ink bounds exclude empty font-cell padding. Subscript-rich
 # condensed labels retain their full SVG box for clipping/overlap checks.
 ev("""window.__etherInkBox=(e)=>{if(mode2D!=='expanded'||!/^([CHO])$/.test(e.textContent.trim()))return e.getBoundingClientRect();const canvas=document.createElement('canvas'),c=canvas.getContext('2d'),style=getComputedStyle(e.firstElementChild||e);c.font=style.fontStyle+' '+style.fontWeight+' '+style.fontSize+' '+style.fontFamily;const m=c.measureText(e.textContent.trim()),start=e.getStartPositionOfChar(0),matrix=e.getScreenCTM();const points=[[start.x-m.actualBoundingBoxLeft,start.y-m.actualBoundingBoxAscent],[start.x+m.actualBoundingBoxRight,start.y-m.actualBoundingBoxAscent],[start.x-m.actualBoundingBoxLeft,start.y+m.actualBoundingBoxDescent],[start.x+m.actualBoundingBoxRight,start.y+m.actualBoundingBoxDescent]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(matrix));return{left:Math.min(...points.map(p=>p.x)),right:Math.max(...points.map(p=>p.x)),top:Math.min(...points.map(p=>p.y)),bottom:Math.max(...points.map(p=>p.y))}}""")
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.5)
  ev("[...document.querySelectorAll('button')].find(b=>b.textContent.includes('Συνέχεια ως έχει'))?.click()")
  for spec in specs:
   key=spec['key'];print('CHECK',width,key,flush=True);ev('document.getElementById('+json.dumps(key)+').click()')
   until('selectedMol==='+json.dumps(key)+' && mainChainPool3DKey==='+json.dumps(key))
   assert ev('document.getElementById('+json.dumps(key)+').textContent.replace(/\\s/g,"").endsWith('+json.dumps(spec['displayFormula'])+')'),(key,'library formula')
   until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(3*spec['carbons']+3))
   for mode in ['condensed','expanded','skeletal','condensedZigZag']:
    for chain in ['algorithmic','data']:
     ev('mode2D='+json.dumps(mode)+';mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();nameAnalysisMode="none";etherNamingMode="iupac";fShowNameAnalysis()')
     assert ev('currentMolName')==spec['name'],(key,mode,chain,actual_name())
     assert ev('currentMolCommonName')==spec['common']
     assert ev("(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),r=svg.getBoundingClientRect(),nodes=[...svg.querySelectorAll('text:not([id^=number])')],a=nodes.map(window.__etherInkBox);return nodes.map(e=>e.getBoundingClientRect()).every(b=>b.left>=r.left-1&&b.right<=r.right+1&&b.top>=r.top-1&&b.bottom<=r.bottom+1)&&a.every((b,i)=>a.slice(i+1).every(c=>Math.min(b.right,c.right)-Math.max(b.left,c.left)<=1||Math.min(b.bottom,c.bottom)-Math.max(b.top,c.top)<=1))})()"),(key,width,mode,'overlap/clipping')
     assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)'),(key,mode,chain)
     if mode=='expanded':
      texts=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].map(e=>e.textContent.trim()))"))
      assert texts.count('C')==spec['carbons'] and texts.count('H')==2*spec['carbons']+2 and texts.count('O')==1,(key,texts)
     if mode=='skeletal':assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>['C','H'].includes(e.textContent.trim()))"),(key,'skeletal labels')
     for comp in ['comp0','comp1','comp5','comp6']+(['comp2','comp3'] if 'isobutyl' in key or 'tert_butyl' in key else []):
      assert ev('!!document.getElementById('+json.dumps(comp)+')'),(key,comp)
      ev('document.getElementById('+json.dumps(comp)+').click()')
      if comp=='comp1':
       until("JSON.stringify(window.__coloredEtherAtoms())===JSON.stringify(window.__etherWithH([functionalGroupObj3D.ether.O[0]+1].concat(fGetEtherAlkoxyChain3D())))")
      if comp=='comp3':until("JSON.stringify(window.__coloredEtherAtoms())===JSON.stringify(window.__etherWithH(fGetHydrocarbonBranchHighlight3D(2).atoms))")
     ev('document.querySelector("#radioEtherNaming [data-naming-mode=common]").click()')
     assert ev('etherNamingMode')=='common'
     parts=json.loads(ev('JSON.stringify(fGetEtherCommonParts().parts)'))
     for i,p in enumerate(parts):
      ev('document.getElementById('+json.dumps('comp'+str(10+i))+').click()')
      if p['kind']=='alkyl':
       until("JSON.stringify(window.__coloredEtherAtoms())===JSON.stringify(window.__etherWithH("+json.dumps(p['chain3D'])+"))")
     rendered=ev("[10,11,12].map(i=>document.getElementById('comp'+i).textContent.trim()).join('')")
     assert rendered==spec['common'],(key,rendered,spec['common'])
     rows.append(dict(width=width,molecule=key,mode=mode,chainMode=chain,name=actual_name(),common=ev('currentMolCommonName')))
     ev('document.querySelector("#radioEtherNaming [data-naming-mode=iupac]").click()')
    if mode in ['condensed','expanded','skeletal']:screenshot('/tmp/ether-refinement-'+str(width)+'-'+key+'-'+mode+'.png')
 assert not js_errors,js_errors
 Path('/tmp/ether-refinement-browser-20261026.json').write_text(json.dumps(dict(cases=rows,javascriptErrors=js_errors),ensure_ascii=False,indent=2))
 print('PASS',len(rows),'browser cases: both names/toggle, every prefix/common group highlight, fullH, 2D3D parent; zero JS errors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
