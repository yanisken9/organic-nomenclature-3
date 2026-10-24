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

def state():
 return json.loads(ev("JSON.stringify({name:currentMolName,parts:nameComponentsList,chain:mainChainAtomsList,chain3:mainChainAtoms3D,boxes:[...document.querySelectorAll('.nameCompContainer .nameCompBox')].map(e=>({id:e.id,text:e.textContent})),explain:document.getElementById('nameAnalysisExplain').textContent,h:fGetHydrocarbonBranchHighlight(fHydrocarbonBranchSlot()),h3:fGetHydrocarbonBranchHighlight3D(fHydrocarbonBranchSlot()),selection:JmolSelection})"))

# Runtime-only graph fixtures. Production MOL/SDF/scenario files stay unchanged.
fixture_js=r"""
window.__p2chain=n=>Array.from({length:n-1},(_,i)=>[i+1,i+2,1]);
window.__p2mol=(n,edges,expanded=false)=>{
 const types=Array(n).fill('C'), es=edges.map(e=>e.slice());
 if(expanded)for(let i=1;i<=n;i++){
  const val=edges.reduce((v,e)=>v+(e[0]===i||e[1]===i?e[2]:0),0);
  for(let h=val;h<4;h++){types.push('H');es.push([i,types.length,1]);}
 }
 const atom=types.map((t,i)=>{
  const x=i<n?(i<10?i*1.4:(i-10)*1.4+1.4):(i-n)*.6;
  const y=i<n?(i<10?0:2+(i%2)):-(1+(i%3)*.6);
  return x.toFixed(4).padStart(10)+y.toFixed(4).padStart(10)+'    0.0000 '+t.padEnd(3)+' 0  0  0  0  0  0  0  0  0  0  0  0';
 });
 return 'P2 runtime fixture\n  Test 3D\n\n'+String(types.length).padStart(3)+String(es.length).padStart(3)+'  0  0  0  0  0  0  0999 V2000\n'+atom.join('\n')+'\n'+es.map(e=>e.map(v=>String(v).padStart(3)).join('')+'  0  0  0  0').join('\n')+'\nM  END\n';
};
window.__p2load=(n,edges,expanded=false,stored=null)=>{
 const mol=window.__p2mol(n,edges,expanded);
 selectedMol='__p2_runtime';nameExamples[selectedMol]={
 structure2D_Condensed:window.__p2mol(n,edges),structure2D_Expanded:window.__p2mol(n,edges,true),structure2D_Skeletal:window.__p2mol(n,edges),
 mainChain_Condensed:stored,mainChain_Expanded:stored,mainChain_Skeletal:stored,mainChain3D:stored};
 window.nameHiddenComps=[];nameAnalysisMode='none';mode2D=expanded?'expanded':'condensed';
 fLoadMol2D();fParseSDF3D(mol);fDetectMolType3D();fCalcMainChain3D();
 Jmol.script(jmolAppletNomeclature,'load DATA "p2"\n'+mol+'\nend "p2";select all;center selected;spacefill 23%;wireframe 0.15;');
 fShowNameAnalysis();return true;
};
"""
try:
 navigate('mulermoc-nom-49.html?v=alkane-p2-browser-20261023');app_ready()
 until("window.JSmolReadyFlag===true")
 ev(fixture_js)
 # All original red regressions run through actual JSME and visible name panel.
 cases=[(13,"__p2chain(10).concat([[5,11,1],[11,12,1],[12,13,1]])",'5-προπυλοδεκάνιο'),
 (10,"__p2chain(7).concat([[5,8,1],[8,9,1],[3,10,1]])",'3-αιθυλο-5-μεθυλοεπτάνιο'),
 (16,"__p2chain(10).concat([[2,11,1],[4,12,1],[12,13,1],[5,14,1],[14,15,1],[14,16,1]])",'4-αιθυλο-5-ισοπροπυλο-2-μεθυλοδεκάνιο')]
 for n,edges,name in cases:
  for chain_mode in ['algorithmic','data']:
   ev("mainChainMode='algorithmic';__p2load("+str(n)+','+edges+")")
   stored=ev('JSON.stringify(mainChainAtomsList)')
   for mode in ['condensed','expanded','skeletal']:
    ev("mainChainMode='"+chain_mode+"';__p2load("+str(n)+','+edges+','+str(mode=='expanded').lower()+','+stored+");mode2D='"+mode+"';fLoadMol2D();fShowNameAnalysis()")
    until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{carbon}.count'))==="+str(n),20)
    r=state();assert r['name']==name,r
    assert ''.join(b['text'] for b in r['boxes'])==name,r
    assert len(r['parts'])==12,r
    for comp in ['comp0','comp1']+(['comp2','comp3'] if n in [10,16] else []):
     ev("nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('"+comp+"').click()")
     r=state();slot=1 if comp in ['comp0','comp1'] else 2
     expected=([12,13] if slot==1 else [11,14,15,16]) if n==16 else None
     if expected:
      actual=json.loads(ev("JSON.stringify(fGetHydrocarbonBranchHighlight("+str(slot)+").atoms.filter(a=>allAtomsTypeList[a-1]==='C').sort((a,b)=>a-b))"))
      assert actual==expected,(comp,r)
      assert sorted(r['h3']['atoms'])==expected,(comp,r)
      if slot==2:assert 'ισοπροπύλιο' in r['explain'] and 'μεθύλιο' in r['explain'],r
      rows=json.loads(ev("JSON.stringify([...document.querySelectorAll('.ruleAlkyl [data-row].selected')].map(e=>e.dataset.row))"))
      assert set(rows)==({'alkyl-αιθυλο'} if slot==1 else {'alkyl-ισοπροπυλο','alkyl-μεθυλο'}),rows
     import re
     assert set(map(int,re.findall(r'atomno=([0-9]+)',r['selection'])))==set(r['h3']['atoms']),r
    if n==16:
     # Existing hidden-comp IDs remain stable; actual eye click hides grouped label.
     ev("window.nameEyeEdit=true;fShowNameAnalysis();document.querySelector('.compEye[data-comp=comp3]').click()")
     assert ev("window.nameHiddenComps.includes('comp3')&&document.getElementById('comp3').classList.contains('comp-hidden')")
     assert ev('currentMolName')==name
     # DOM narration must skip hidden grouped content.
     ev("window.__spoken=[];window.__origSpeak=window.speechSynthesis.speak.bind(window.speechSynthesis);window.speechSynthesis.speak=u=>window.__spoken.push(u.text);fSpeakNameWithPauses()")
     assert ev("!window.__spoken.join(' ').includes('ισοπροπυλ')")
     ev("window.speechSynthesis.speak=window.__origSpeak;window.nameHiddenComps=[];fShowNameAnalysis()")
  print('PASS browser',name,':3forms x2modes,visible/fullname agreement,click highlights/rules/hidden/narration',flush=True)
 # Exercise real stepper UI against the alpha tie and separately permuted3D numbering.
 ev("mainChainMode='algorithmic';__p2load(10,"+cases[1][1]+")")
 ev("window.__p2sdf=__p2mol(10,"+cases[1][1]+");window.__p2lines=window.__p2sdf.split('\\n');window.__p2order=[8,3,10,1,6,9,4,7,2,5];window.__p2map={};window.__p2order.forEach((n,i)=>window.__p2map[n]=i+1);window.__p2permuted=window.__p2lines.slice(0,4).concat(window.__p2order.map(n=>window.__p2lines[n+3]),window.__p2lines.slice(14,23).map(b=>String(window.__p2map[Number(b.slice(0,3))]).padStart(3)+String(window.__p2map[Number(b.slice(3,6))]).padStart(3)+b.slice(6)).reverse(),['M  END','']).join('\\n');fParseSDF3D(window.__p2permuted);fDetectMolType3D();fCalcMainChain3D();mainChainPool3D.unshift({chain:mainChainPool3D[0].chain.slice().reverse()});fShowNameAnalysis();document.getElementById('chainNextBtn').click()")
 assert ev("currentMolName==='3-αιθυλο-5-μεθυλοεπτάνιο'&&fCarbonChainSignature(mainChainAtomsList,atomConnectivityList,allAtomsTypeList)===fCarbonChainSignature(mainChainAtoms3D,atomConnectivityList3D,allAtomsTypeList3D)")
 print('PASS browser actual next-chain click, permuted3D+misordered pool graph signature',flush=True)
 assert not js_errors,js_errors
 print('PASS no browser JavaScript errors',flush=True)
finally:
 call('session.end',{})
