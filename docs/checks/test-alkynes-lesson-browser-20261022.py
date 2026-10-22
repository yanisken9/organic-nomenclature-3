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
def actual_name():return ev("nameComponentsList.filter(Boolean).join('')")
def skeletal_clean():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")
try:
 navigate('mulermoc-nom-49.html?scenario=scenarios/alkynes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=ethyne-lesson-20261022')
 until("typeof fScenarioActive==='function' && !!fScenarioActive() && fScenarioActive().steps.length===22 && !document.documentElement.classList.contains('lesson-loading')")
 source=json.loads(Path('scenarios/alkynes-nomenclature-branches.scenario.json').read_text())
 ev('window.__expectedLesson=fScenarioValidate('+json.dumps(source,ensure_ascii=False)+')')
 assert ev("JSON.stringify(fScenarioActive().steps)===JSON.stringify(window.__expectedLesson.steps)")
 assert ev("selectedMol==='ethyne' && nameComponentsList.filter(Boolean).join('')==='αιθίνιο' && ['comp5','comp6','comp9'].every(id=>document.getElementById(id).classList.contains('comp-hidden'))")
 screenshots=[]
 for i in range(22):
  ev('fScenarioGo('+str(i)+')');time.sleep(.28)
  assert ev('selectedMol')==source['steps'][i].get('selectedMol'),i+1
  assert ev('viewerMaxH===420'),i+1
  assert ':' not in source['steps'][i]['note']+source['steps'][i]['title']
  if i<21:
   expected='αιθίνιο' if i<5 else '1-βουτίνιο' if i==5 else '3-μεθυλο-1-βουτίνιο' if i<10 else '4-μεθυλο-2-πεντίνιο' if i<14 else '4-αιθυλο-3,5-διμεθυλο-1-επτίνιο'
   assert actual_name()==expected,(i+1,actual_name())
  if i in [1,2,3]:
   row={1:'r1-c2',2:'r2-triple',3:'r3-hydrocarbons'}[i]
   assert ev("!!document.querySelector('#ruleContainer [data-row=\""+row+"\"].selected')"),i+1
  if i in [8,17]:
   row='alkyl-μεθυλο' if i==8 else 'alkyl-αιθυλο'
   assert ev("document.querySelectorAll('.ruleAlkyl [data-row^=\"alkyl-\"]').length===8 && !!document.querySelector('.ruleAlkyl [data-row=\""+row+"\"].selected')"),i+1
  if i in [6,7,8,9]:assert ev("JSON.stringify(mainChainAtomsList)==='[4,3,2,1]'"),i+1
  if i in [10,11,12,13]:assert ev("JSON.stringify(mainChainAtomsList)==='[5,4,3,2,1]'"),i+1
  if i in [14,15,16,17,18,19,20]:assert ev("JSON.stringify(mainChainAtomsList)==='[1,2,3,4,5,6,7]'"),i+1
  if i in [8,17,18,19]:
   r=json.loads(ev("JSON.stringify(fGetHydrocarbonBranchHighlight(fHydrocarbonBranchSlot()))"))
   carbon_expected=[5] if i==8 else [9,10] if i==17 else [8,11]
   types=json.loads(ev('JSON.stringify(allAtomsTypeList)'))
   assert sorted(a for a in r['atoms'] if types[a-1]=='C')==carbon_expected,(i+1,r)
   if i==19:assert len([a for a in r['atoms'] if types[a-1]=='H'])==6
  if i in [0,8,11,14,19]:
   path='design/assets/alkynes-lesson-step'+str(i+1)+'.png';screenshot(path);screenshots.append(path)
 assert ev("selectedMol===null && viewerBothH===840 && document.getElementById('nomeclature3D').getClientRects().length>0")
 for key in source['steps'][21]['menuSubset']:
  ev("selectedMol='"+key+"';fSelectMol()");time.sleep(.4)
  assert ev("nameExamples[selectedMol].classification.seriesKey==='alkynes'")
  # Both pure skeletal and CHn use the existing alkyne display policy.
  ev("mode2D='skeletal';fLoadMol2D();fShowNameAnalysis()");skeletal_clean()
 print('PASS all22steps, expectednames, rules2/3/4/9/18, horizontalchains, exactbranchcarbon/H sets, eightmenu molecules/skeletons',flush=True)
 # New ethyne in actual controls and both chain modes, including the triple highlight.
 ev("selectedMol='ethyne';fSelectMol()")
 until("mainChainPool3DKey==='ethyne' && Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))===4")
 for cm in ['algorithmic','data']:
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   ev("mainChainMode='"+cm+"';mode2D='"+mode+"';fLoadMol2D();nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('comp6').click()")
   assert actual_name()=='αιθίνιο',(cm,mode,actual_name())
   assert ev("!!document.querySelector('[data-row=\"r2-triple\"].selected') && JmolSelection.includes('atomno=1') && JmolSelection.includes('atomno=2')"),(cm,mode)
   if mode=='skeletal':skeletal_clean()
 for i,mode in enumerate(['condensed','expanded','skeletal']):
  ev("document.querySelectorAll('#radio2DMode .mode2DOption')["+str(i)+"].click();nameAnalysisMode='none';fShowNameAnalysis()")
  time.sleep(.2)
  if mode=='expanded':
   assert ev("document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])').length===4")
   screenshot('design/assets/ethyne-expanded.png')
  if mode=='skeletal':
   skeletal_clean();screenshot('design/assets/ethyne-skeletal.png')
 assert not js_errors,js_errors
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/theory-library.html')")
 evidence={'steps':22,'molecules':8,'start':'ethyne','newMolecule3DAtomCount':4,'ethyneFormChainModes':8,'heights':{'single':420,'bothTotal':840},'proseHasColons':False,'screenshots':screenshots,'checks':['all exact notes/settings match source','all expected names','rules2/3/4/9/18','horizontal chains','branch carbon sets and6methyl hydrogens at20','eight skeletal models without C labels','new ethyne actual2D controls and 3D triple atoms','Exit returns library'],'javascriptErrors':js_errors}
 Path('docs/checks/alkynes-lesson-20261022.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 print('PASS ethyne8form/chainmodes,actualcontrols,3D4atoms,Exit/library; noJSerrors',flush=True)
finally:
 call('session.end',{})
