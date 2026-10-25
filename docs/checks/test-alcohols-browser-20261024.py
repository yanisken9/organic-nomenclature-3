"""Actual Firefox/JSME/JSmol four-alcohol regression; artifacts only under /tmp."""
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
specs=json.loads(Path('docs/checks/alcohols-specs-20261024.json').read_text());evidence=[]
if os.environ.get('NAMELECULE_ALCOHOL_KEYS'):specs=[s for s in specs if s['key'] in os.environ['NAMELECULE_ALCOHOL_KEYS'].split(',')]
try:
 navigate('mulermoc-nom-50.html?v=alcohols-validation');app_ready();until('window.JSmolReadyFlag===true')
 assert ev('Object.keys(nameExamples).length===93')
 ev("document.querySelector('[data-grouping-mode=series]').click();document.querySelector('[data-group-key=alcohol]').click()")
 for spec in specs:
  key=spec['key'];total=3*spec['carbons']+3
  source=Chem.MolFromMolFile('mols/new_molecules/'+key+'_2D_Condensed.mol',removeHs=False)
  target=Chem.RemoveHs(Chem.MolFromMolFile('mols/nomeclature-moc2/'+key+'_3D.sdf',removeHs=False))
  mappings=target.GetSubstructMatches(source,uniquify=False,maxMatches=1000)
  ev('document.getElementById('+json.dumps(key)+').click()')
  until('mainChainPool3DKey==='+json.dumps(key))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(total))
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   for chain in ['algorithmic','data']:
    ev('mode2D='+json.dumps(mode)+';mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();nameAnalysisMode="none";fShowNameAnalysis()')
    assert ev('currentMolName==='+json.dumps(spec['name'])),(key,mode,chain,ev('currentMolName'))
    assert ev("[...document.querySelectorAll('.nameCompBox')].map(e=>e.textContent).join('')==="+json.dumps(spec['name'])),(key,mode,chain)
    assert ev("nameExamples[selectedMol].classification.seriesKey==='alcohol'")
    parent=json.loads(ev('JSON.stringify(mainChainAtomsList)'));parent3=json.loads(ev('JSON.stringify(mainChainAtoms3D)'))
    compatible=[m for m in mappings if all(m[a-1]+1==b for a,b in zip(parent,parent3))];assert compatible,(key,mode,chain,parent,parent3)
    assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
    if mode=='expanded':
     texts=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].map(e=>e.textContent.trim()))"))
     assert texts.count('O')==1 and texts.count('H')==2*spec['carbons']+2 and texts.count('C')==spec['carbons'],(key,texts)
    groups=[]
    if spec['carbons']>4:
     for slot in ([1,2] if spec['carbons']==12 else [1]):
      component='comp1' if slot==1 else 'comp3'
      result=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight('+str(slot)+'))'));types=json.loads(ev('JSON.stringify(allAtomsTypeList)'))
      carbons=sorted(a for a in result['atoms'] if types[a-1]=='C');hs=sum(types[a-1]=='H' for a in result['atoms'])
      expectedC=3 if spec['carbons']==12 and slot==1 else 2 if spec['carbons'] in [7,12] else 1
      expectedH=7 if spec['carbons']==12 and slot==1 else expectedC*3
      assert len(carbons)==expectedC and hs==(expectedH if mode=='expanded' else 0),(key,mode,slot,result)
      carbons3=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms.filter(n=>allAtomsTypeList3D[n-1]==="C").sort((a,b)=>a-b))'))
      assert any(sorted(m[a-1]+1 for a in carbons)==carbons3 for m in compatible),(key,mode,slot,carbons,carbons3)
      ev('document.getElementById('+json.dumps(component)+').click()')
      until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.count'))==="+str(expectedC+expectedH))
      assert 'διακλαδ' in ''.join(c for c in unicodedata.normalize('NFD',ev("document.getElementById('nameAnalysisExplain').textContent")) if not unicodedata.combining(c)),(key,component)
      groups.append({'slot':slot,'carbons2D':carbons,'carbons3D':carbons3,'hydrogens':expectedH})
    # Click OH locant: O and its H, never an alkyl or all single bonds.
    component='comp0' if spec['carbons']==4 else 'comp4'
    ev('document.getElementById('+json.dumps(component)+').click()')
    until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.count'))===2")
    selection=ev('JmolSelection');oxygen3=next(a.GetIdx()+1 for a in target.GetAtoms() if a.GetSymbol()=='O')
    assert 'atomno='+str(oxygen3) in selection.replace(' ',''),(key,component,selection)
    if spec['carbons']>4:assert 'υδροξυλομάδ' in ev("document.getElementById('nameAnalysisExplain').textContent")
    if spec['carbons']>4:assert ev("!!document.querySelector('#ruleContainer [data-row=\"r3-alcohols\"].selected')"),(key,component)
    if mode in ['condensed','expanded']:
     positions=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>({text:e.textContent,x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y})))"))
     assert len(positions)==spec['parent'] and positions[0]['x']>positions[-1]['x'],(key,mode,positions)
     assert max(p['y'] for p in positions)-min(p['y'] for p in positions)<5,(key,mode,positions)
    evidence.append({'key':key,'mode':mode,'chainMode':chain,'name':spec['name'],'atoms3D':total,'parent':parent,'parent3D':parent3,'groups':groups,'OHselected':True})
   if mode in ['expanded','skeletal']:screenshot('/tmp/alcohol-final-'+key+'-'+mode+'.png')
  print('PASS',key,'four forms/two modes/actual OH and branch clicks',flush=True)
 Path('/tmp/alcohols-browser-evidence.json').write_text(json.dumps({'cases':evidence,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 local=[e for e in js_errors if not e.get('stackTrace',{}).get('callFrames',[{}])[0].get('url','').startswith('https://chemapps.stolaf.edu/')]
 assert not local,[e.get('text') for e in local]
 print('PASS',len(evidence),'browser cases; external errors',len(js_errors))
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
