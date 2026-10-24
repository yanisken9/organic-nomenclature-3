"""Actual Firefox/JSME/JSmol enyne regression; artifacts only under /tmp."""
# Real Firefox BiDi/JSME/JSmol UI regression. Runtime fixtures only; no app data writes.
# Run: python3 docs/checks/test-alkanes-p2-browser-v49.py
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


specs=json.loads(Path('docs/checks/enynes-specs-20261024.json').read_text());evidence=[]
if os.environ.get('NAMELECULE_ENYNE_KEYS'):specs=[s for s in specs if s['key'] in os.environ['NAMELECULE_ENYNE_KEYS'].split(',')]
try:
 navigate('mulermoc-nom-50.html?v=three-enynes-validation');app_ready();until('window.JSmolReadyFlag===true')
 assert ev('Object.keys(nameExamples).length===89')
 ev("document.querySelector('[data-grouping-mode=series]').click();document.querySelector('[data-group-key=enynes]').click()")
 for spec in specs:
  key=spec['key'];total=int(spec['formula'].split('H')[1])+int(spec['formula'][1:].split('H')[0])
  provenance=json.loads(Path('mols/new_molecules',key+'_3D.provenance.json').read_text());mapping=provenance['atomMapping2Dto3D']
  ev('document.getElementById('+json.dumps(key)+').click()')
  until('mainChainPool3DKey==='+json.dumps(key))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(total))
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   for chain in ['algorithmic','data']:
    ev('mode2D='+json.dumps(mode)+';mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();fShowNameAnalysis()')
    assert ev('currentMolName==='+json.dumps(spec['name'])),(key,mode,chain)
    assert ev("[...document.querySelectorAll('.nameCompBox')].map(e=>e.textContent).join('')==="+json.dumps(spec['name'])),(key,mode,chain)
    assert ev("nameExamples[selectedMol].classification.seriesKey==='enynes'")
    for index,carbons in enumerate(spec['groups'],1):
     result=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight('+str(index)+'))'));types=json.loads(ev('JSON.stringify(allAtomsTypeList)'))
     assert sorted(a for a in result['atoms'] if types[a-1]=='C')==carbons,(key,mode,index,result)
     expectedH=5 if len(carbons)==2 and index==1 and len(spec['groups'])==2 else 3*len(carbons)
     assert len([a for a in result['atoms'] if types[a-1]=='H'])==(expectedH if mode=='expanded' else 0),(key,mode,index)
     result3=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight3D('+str(index)+').atoms.filter(n=>allAtomsTypeList3D[n-1]==="C").sort((a,b)=>a-b))'))
     assert result3==sorted(mapping[str(c)] for c in carbons),(key,mode,index,result3)
    if mode=='expanded':assert ev("document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])').length==="+str(total)),key
    if mode=='skeletal':assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C')"),key
    # Existing renderer must keep both double and triple line sets parallel.
    assert ev("(()=>{const ls=document.querySelectorAll('#jsmeNomeclatureSVG line');return bondList.every((b,i)=>{if(b[2]<2)return true;const pair=[...ls].slice(svgBondList[i]-1,svgBondList[i]-1+b[2]);const dirs=pair.map(l=>[l.x2.baseVal.value-l.x1.baseVal.value,l.y2.baseVal.value-l.y1.baseVal.value]);return dirs.every(d=>Math.hypot(...d)>0&&Math.abs(d[0]*dirs[0][1]-d[1]*dirs[0][0])/(Math.hypot(...d)*Math.hypot(...dirs[0]))<.002)})})()"),(key,mode,'parallel')
    assert ev("(()=>{const ls=document.querySelectorAll('#jsmeNomeclatureSVG line');let middle={};bondList.forEach((b,i)=>{if(b[2]===2||b[2]===3){const l=ls[svgBondList[i]-1];middle[b[2]]=(l.x1.baseVal.value+l.x2.baseVal.value)/2}});return middle[3]<middle[2]})()"),(key,mode,'triple must be left of double')
    assert ev('mainChainAtomsList[0]===1'),(key,mode,chain,'numbering start')
    # Exercise actual component-click highlight handlers, not only helper arrays.
    ev("[...document.querySelectorAll('.nameCompBox')].forEach(e=>e.click())")
   screenshot('/tmp/new-enyne-'+key+'-'+mode+'.png')
  evidence.append({'key':key,'formula':spec['formula'],'name':spec['name'],'atoms3D':total,'formChainCases':8,'branchGroups':spec['groups']})
  print('PASS browser',key,'4forms x2chain modes, exactnames/components/C/H2D3D/multiplebonds',flush=True)
 # Existing enynes remain selectable in their own menu and keep their original names.
 for key in ['buten_1_yne_3','hexen_2_yne_4']:
  ev('document.getElementById('+json.dumps(key)+').click()')
  until('mainChainPool3DKey==='+json.dumps(key))
  assert ev("nameExamples[selectedMol].classification.seriesKey==='enynes'")
  print('PASS existing enyne',key,ev('currentMolName'),flush=True)
 assert not js_errors,js_errors
 Path('/tmp/enynes-browser-evidence-20261024.json').write_text(json.dumps({'molecules':evidence,'cases':len(evidence)*8,'javascriptErrors':js_errors,'oldEnyneSamples':2},ensure_ascii=False,indent=2)+'\n')
 print('PASS89 registry entries; noJSerrors',flush=True)
finally:call('session.end',{})
