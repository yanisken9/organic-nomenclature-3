"""Actual Firefox/JSME/JSmol five other-alcohol regression; artifacts only under /tmp."""
# Real Firefox BiDi/JSME/JSmol UI regression. Runtime fixtures only; no app data writes.
# Run with RDKit Python and isolated Firefox BiDi on port9237; app server8013.
import socket,base64,os,struct,json,time,unicodedata
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



from rdkit import Chem
specs=json.loads(Path('docs/checks/other-alcohols-specs-20261025.json').read_text());evidence=[]
if os.environ.get('NAMELECULE_ALCOHOL_KEYS'):specs=[s for s in specs if s['key'] in os.environ['NAMELECULE_ALCOHOL_KEYS'].split(',')]
try:
 navigate('mulermoc-nom-50.html?v=other-alcohols-validation');app_ready();until('window.JSmolReadyFlag===true')
 assert ev('Object.keys(nameExamples).length===98')
 ev("document.querySelector('[data-grouping-mode=series]').click()")
 until("!!document.querySelector('[data-group-key=alcohol]')")
 ev("document.querySelector('[data-group-key=alcohol]').click()")
 for spec in specs:
  print('START',spec['key'],flush=True)
  key=spec['key'];source=Chem.MolFromMolFile('mols/new_molecules/'+key+'_2D_Condensed.mol',removeHs=False)
  full=Chem.MolFromMolFile('mols/nomeclature-moc2/'+key+'_3D.sdf',removeHs=False);target=Chem.RemoveHs(full)
  total=full.GetNumAtoms();oxygenCount=sum(a.GetSymbol()=='O' for a in source.GetAtoms());hydrogenCount=sum(a.GetTotalNumHs() for a in source.GetAtoms())
  mappings=target.GetSubstructMatches(source,uniquify=False,maxMatches=1000)
  ev('document.getElementById('+json.dumps(key)+').click()');until('mainChainPool3DKey==='+json.dumps(key))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(total))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{_O}.count'))==="+str(oxygenCount))
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   for chain in ['algorithmic','data']:
    print('CASE',key,mode,chain,flush=True)
    ev('mode2D='+json.dumps(mode)+';mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();nameAnalysisMode="none";fShowNameAnalysis()')
    assert ev('currentMolName')==spec['name'],(key,mode,chain,ev('currentMolName'))
    assert ev("[...document.querySelectorAll('.nameCompBox')].map(e=>e.textContent).join('')")==spec['name'],(key,mode,chain)
    parent=json.loads(ev('JSON.stringify(mainChainAtomsList)'));parent3=json.loads(ev('JSON.stringify(mainChainAtoms3D)'))
    compatible=[m for m in mappings if all(m[a-1]+1==b for a,b in zip(parent,parent3))];assert compatible,(key,parent,parent3)
    assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
    if mode=='expanded':
     texts=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].map(e=>e.textContent.trim()))"))
     assert texts.count('O')==oxygenCount and texts.count('H')==hydrogenCount and texts.count('C')==spec['carbons'],(key,texts)
     assert ev("(()=>{const hs=[...document.querySelectorAll('#jsmeNomeclatureSVG text')].filter(e=>e.textContent.trim()==='H').map(e=>e.getBoundingClientRect());return hs.every((a,i)=>hs.slice(i+1).every(b=>a.right<=b.left+.5||b.right<=a.left+.5||a.bottom<=b.top+.5||b.bottom<=a.top+.5))})()"),(key,'H label overlap')
    groups=[]
    for slot in ([1,2] if spec['carbons']==9 else [1]):
     component='comp1' if slot==1 else 'comp3';expectedC=2 if spec['carbons']==9 and slot==1 else 1;expectedH=5 if expectedC==2 else 3
     result=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight('+str(slot)+'))'));types=json.loads(ev('JSON.stringify(allAtomsTypeList)'))
     carbons=sorted(a for a in result['atoms'] if types[a-1]=='C');hs=sum(types[a-1]=='H' for a in result['atoms']);assert len(carbons)==expectedC and hs==(expectedH if mode=='expanded' else 0),(key,mode,slot,result)
     carbons3=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms.filter(n=>allAtomsTypeList3D[n-1]==="C").sort((a,b)=>a-b))'))
     assert any(sorted(m[a-1]+1 for a in carbons)==carbons3 for m in compatible),(key,mode,slot)
     ev('document.getElementById('+json.dumps(component)+').click()')
     until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.count'))==="+str(expectedC+expectedH))
     assert 'διακλαδ' in ''.join(c for c in unicodedata.normalize('NFD',ev("document.getElementById('nameAnalysisExplain').textContent")) if not unicodedata.combining(c))
     groups.append({'slot':slot,'carbons2D':carbons,'carbons3D':carbons3})
    # Verify distinct C=C and C#C targets and actual selected3D endpoints.
    orders=sorted(set(o for a,b,o in spec['edges'] if o>1))
    for order in orders:
     ev("if(!fShowBondAtoms())document.getElementById('bondAtomsCheck').click()")
     component='comp7' if len(orders)==2 and order==3 else 'comp4'
     ev('document.getElementById('+json.dumps(component)+').click()')
     until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.count'))===2")
     actual=sorted(map(int,__import__('re').findall(r'atomno=(\d+)',ev('JmolSelection'))))
     expected=sorted(n+1 for b in target.GetBonds() if b.GetBondTypeAsDouble()==order for n in [b.GetBeginAtomIdx(),b.GetEndAtomIdx()])
     assert actual==expected,(key,order,actual,expected)
    # OH uses its own slot (or OH-locant+suffix box in mixed alcohols).
    component=ev('fAlcoholOHNameComponent()');ids={'compBondPos':'comp4','compEndNumber':'comp7','compSuffix':'comp9'};assert component in ids,(key,component)
    ev('document.getElementById('+json.dumps(ids[component])+').click()')
    until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.count'))==="+str(2*oxygenCount))
    assert 'υδροξυλομάδ' in ev("document.getElementById('nameAnalysisExplain').textContent"),(key,component)
    assert ev("!!document.querySelector('#ruleContainer [data-row=\"r3-alcohols\"].selected')"),(key,component)
    if mode in ['condensed','expanded']:
     positions=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y})))"))
     assert len(positions)==spec['parent'] and positions[0]['x']>positions[-1]['x'],(key,mode,positions)
     assert max(p['y'] for p in positions)-min(p['y'] for p in positions)<5,(key,mode,positions)
    evidence.append({'key':key,'mode':mode,'chainMode':chain,'name':spec['name'],'parent':parent,'parent3D':parent3,'groups':groups,'OHcomponent':component,'multipleBondOrders':orders,'atoms3D':total})
   if mode in ['expanded','skeletal']:screenshot('/tmp/other-alcohol-final-'+key+'-'+mode+'.png')
  Path('/tmp/other-alcohols-browser-evidence.json').write_text(json.dumps({'cases':evidence,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
  print('PASS',key,'four forms/two modes/branches/multiple bonds/OH',flush=True)
 Path('/tmp/other-alcohols-browser-evidence.json').write_text(json.dumps({'cases':evidence,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 assert not js_errors,js_errors
 print('PASS',len(evidence),'browser cases; zeroJSerrors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
