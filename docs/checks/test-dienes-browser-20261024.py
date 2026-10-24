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

cases=[('butadiene_1_3','1,3-βουταδιένιο',10,[]),('butadiene_1_2','1,2-βουταδιένιο',10,[]),('pentadiene_1_4','1,4-πενταδιένιο',13,[]),('methyl_3_pentadiene_1_3','3-μεθυλο-1,3-πενταδιένιο',16,[[[6],3]]),('dimethyl_2_3_pentadiene_1_3','2,3-διμεθυλο-1,3-πενταδιένιο',19,[[[6,7],6]]),('ethyl_3_dimethyl_4_5_hexadiene_1_4','3-αιθυλο-4,5-διμεθυλο-1,4-εξαδιένιο',28,[[[7,8],5],[[9,10],6]])]
try:
 navigate('mulermoc-nom-50.html?v=dienes-20261024');app_ready();until('window.JSmolReadyFlag===true')
 assert ev('Object.keys(nameExamples).length===86')
 ev("document.querySelector('[data-grouping-mode=series]').click();document.querySelector('[data-group-key=alkadienes]').click()")
 for key,name,total,branches in cases:
  provenance=json.loads(Path('mols/new_molecules',key+'_3D.provenance.json').read_text())
  mapping=provenance.get('atomMapping2Dto3D',{})
  def mapped(n):return mapping.get(str(n),n)
  ev("document.getElementById("+json.dumps(key)+").click()")
  until("mainChainPool3DKey==="+json.dumps(key))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(total))
  for mode in ['condensed','expanded','skeletal']:
   for chain in ['algorithmic','data']:
    ev("mode2D="+json.dumps(mode)+";mainChainMode="+json.dumps(chain)+";fLoadMol2D();fCalcMainChain3D();fShowNameAnalysis()")
    assert ev('currentMolName==='+json.dumps(name)),(key,mode,chain)
    assert ev("[...document.querySelectorAll('.nameCompBox')].map(e=>e.textContent).join('')==="+json.dumps(name)),(key,mode,chain,'visible name')
    for index,(carbons,hydrogens) in enumerate(branches,1):
     for side in ['', '3D']:
      expr="fGetHydrocarbonBranchHighlight"+side+"("+str(index)+")"
      types='allAtomsTypeList3D' if side else 'allAtomsTypeList'
      result=json.loads(ev("JSON.stringify((()=>{let h="+expr+";return {c:h.atoms.filter(n=>"+types+"[n-1]==='C').sort((a,b)=>a-b),h:h.atoms.filter(n=>"+types+"[n-1]==='H').length}})())"))
      expectedC=sorted(mapped(n) for n in carbons) if side else carbons
      if key=='ethyl_3_dimethyl_4_5_hexadiene_1_4' and index==2:
       parent=json.loads(ev('JSON.stringify('+('mainChainAtoms3D' if side else 'mainChainAtomsList')+')'))
       transform=mapped if side else lambda n:n
       expectedC=sorted([transform(9),transform(6) if transform(10) in parent else transform(10)])
      assert result['c']==expectedC,(key,mode,chain,side,result)
      assert result['h']==(hydrogens if not side and mode=='expanded' else 0),(key,mode,side,result)
     attached=ev("bondList3D.filter(b=>("+json.dumps(expectedC)+".includes(b[0])&&allAtomsTypeList3D[b[1]-1]==='H')||("+json.dumps(expectedC)+".includes(b[1])&&allAtomsTypeList3D[b[0]-1]==='H')).length")
     assert attached==hydrogens,(key,attached,hydrogens)
    ev("[...document.querySelectorAll('.nameCompBox')].forEach(e=>e.click())")
   if mode=='skeletal':screenshot('/tmp/diene-'+key+'.png')
  print('PASS browser '+key+':3forms x2modes, name,realSDF,components,branchC/H2D3D',flush=True)
 assert not js_errors,js_errors
 print('PASS86 molecules; no browser JavaScript errors',flush=True)
finally:
 call('session.end',{})
