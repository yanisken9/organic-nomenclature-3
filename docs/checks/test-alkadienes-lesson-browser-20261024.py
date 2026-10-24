"""Actual Firefox lesson checks. Artifacts only under /tmp; requires localhost8013/BiDi9225."""
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
def actual_name():return ev("currentMolName")
def skeletal_clean():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")

source=json.loads(Path('scenarios/alkadienes-nomenclature-branches.scenario.json').read_text())
expected_names=['1,3-βουταδιένιο']*5+['1,2-βουταδιένιο']+['3-μεθυλο-1,3-πενταδιένιο']*4+['2,3-διμεθυλο-1,3-πενταδιένιο']*4+['3-αιθυλο-4,5-διμεθυλο-1,4-εξαδιένιο']*7
rows=[]
try:
 navigate('design/theory-library.html?v=alkadienes-test')
 assert ev("document.querySelectorAll('.lesson').length===4")
 for series in ['alkanes','alkenes','alkynes','alkadienes']:
  assert ev("!!document.querySelector('a[href*=\"scenarios/"+series+"-nomenclature-branches.scenario.json\"]')")
 ev("document.querySelector('a[href*=\"scenarios/alkadienes-\"]').click()")
 until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
 app_ready();until('window.JSmolReadyFlag===true')
 ev('window.__validated=fScenarioValidate('+json.dumps(source,ensure_ascii=False)+')')
 assert ev('window.__validated.ok && window.__validated.warnings.length===0')
 assert ev('JSON.stringify(fScenarioActive().steps)===JSON.stringify(window.__validated.steps)')
 # Capture the actual exported Blob while suppressing only its download click.
 ev("window.__exportBlob=null;window.__urlCreate=URL.createObjectURL;URL.createObjectURL=b=>(window.__exportBlob=b,'blob:lesson-test');window.__anchorClick=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__urlCreate;HTMLAnchorElement.prototype.click=window.__anchorClick")
 exported=json.loads(ev('window.__exportBlob.text()'))
 ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
 assert ev('window.__round.ok && window.__round.warnings.length===0 && JSON.stringify(window.__round.steps)===JSON.stringify(window.__validated.steps)')
 for i,step in enumerate(source['steps']):
  ev('fScenarioGo('+str(i)+')')
  until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol']))
  if i<21:
   until('currentMolName==='+json.dumps(expected_names[i]))
   until("JSON.stringify([...document.querySelectorAll('.comp-hidden')].map(e=>e.id).sort())==="+json.dumps(json.dumps(sorted(step['styleName']['hidden']),separators=(',',':'))))
   # Wait for asynchronous molecule-load restoration before judging highlights.
   until('nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
   until('mainChainPool3DKey==='+json.dumps(step['selectedMol']))
   ev('fCalcMainChain3D();fShowNameAnalysis()')
   assert actual_name()==expected_names[i],i+1
   if not step['styleName']['hidden']:
    assert ev("[...document.querySelectorAll('.nameCompBox')].map(e=>e.textContent).join('')==="+json.dumps(expected_names[i])),i+1
   assert ev('mode2D')==step['mode2D'],i+1
   if 6<=i<21:
    n=6 if i>=14 else 5
    assert json.loads(ev('JSON.stringify(mainChainAtomsList)'))==list(range(1,n+1)),(i+1,ev('JSON.stringify(mainChainAtomsList)'))
  assert ev('viewerMaxH===420'),i+1
  assert ':' not in step['title']+step['note']
  # Actual rendered note, not just source/model equality.
  ev('window.__expectedNote=document.createElement("div");window.__expectedNote.innerHTML='+json.dumps(step['note'])+';')
  assert ev("document.getElementById('scStepText').textContent.includes(window.__expectedNote.textContent)"),i+1
  assert ev('fScenarioPresent().steps['+str(i)+'].show.rule')==step['show']['rule']
  if i in [1,2,3,8,17]:
   row={1:'r1-c4',2:'r2-didouble',3:'r3-hydrocarbons',8:'alkyl-μεθυλο',17:'alkyl-αιθυλο'}[i]
   assert ev("!!document.querySelector('#ruleContainer [data-row=\""+row+"\"].selected')"),(i+1,row)
  if i in [5,11,15]:
   # Positions are comp0 for unsubstituted dienes, comp4 for substituted dienes.
   comp='comp0' if i==5 else 'comp4'
   assert ev('nameAnalysisMode==='+json.dumps(step['nameAnalysisMode'])),i+1
   provenance=json.loads(Path('mols/new_molecules',step['selectedMol']+'_3D.provenance.json').read_text())
   mapping=provenance.get('atomMapping2Dto3D',{})
   positions=[1,2,3] if i==5 else [1,2,3,4] if i==11 else [1,2,4,5]
   targets=[mapping.get(str(n),n) for n in positions]
   assert ev('JSON.stringify(JmolSelection)') is not None
   import re
   selected=set(map(int,re.findall(r'atomno\s*=\s*(\d+)',ev('JmolSelection'))))
   assert selected==set(targets),(i+1,selected,targets)
  if i in [8,12,17,18,19]:
   result=json.loads(ev('JSON.stringify(fGetHydrocarbonBranchHighlight(fHydrocarbonBranchSlot()))'))
   types=json.loads(ev('JSON.stringify(allAtomsTypeList)'))
   carbons=[6] if i==8 else [6,7] if i==12 else [7,8] if i==17 else [9,10]
   assert sorted(a for a in result['atoms'] if types[a-1]=='C')==carbons,(i+1,result)
   if i==19:assert len([a for a in result['atoms'] if types[a-1]=='H'])==6
   provenance=json.loads(Path('mols/new_molecules',step['selectedMol']+'_3D.provenance.json').read_text())
   mapping=provenance['atomMapping2Dto3D']
   expected3=sorted(mapping[str(n)] for n in carbons)
   if i>=18:
    parent=json.loads(ev('JSON.stringify(mainChainAtoms3D)'))
    expected3=sorted([mapping['9'],mapping['6'] if mapping['10'] in parent else mapping['10']])
   actual3=json.loads(ev("JSON.stringify(fGetHydrocarbonBranchHighlight3D(fHydrocarbonBranchSlot()).atoms.filter(n=>allAtomsTypeList3D[n-1]==='C').sort((a,b)=>a-b))"))
   assert actual3==expected3,(i+1,actual3,expected3)
  if i in [0,5,12,19]:screenshot('/tmp/alkadienes-lesson-step'+str(i+1)+'.png')
  rows.append({'step':i+1,'molecule':step['selectedMol'],'name':actual_name() if i<21 else None})
  print('PASS lesson step',i+1,flush=True)
 assert ev("selectedMol===null && viewerBothH===840 && document.getElementById('nomeclature3D').getClientRects().length>0")
 assert json.loads(ev('JSON.stringify(fScenarioPresent().steps[21].menuSubset)'))==source['steps'][21]['menuSubset']
 for key in source['steps'][21]['menuSubset']:
  ev('document.getElementById('+json.dumps(key)+').click()')
  until('mainChainPool3DKey==='+json.dumps(key))
  assert ev("nameExamples[selectedMol].classification.seriesKey==='alkadienes'")
  total=7 if key=='propadiene' else 10 if key.startswith('butadiene') else 13 if key.startswith('pentadiene') else 16 if key.startswith('methyl_') else 19 if key.startswith('dimethyl_') else 28
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(total))
  for mode in ['condensed','expanded','skeletal']:
   ev('mode2D='+json.dumps(mode)+";fLoadMol2D();fShowNameAnalysis()")
   assert ev('currentMolName.length>0 && !!document.querySelector("#jsmeNomeclatureSVG svg")')
  print('PASS exploration',key,flush=True)
 # Mobile-width layout and return through the real Exit button.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':700,'height':900},'devicePixelRatio':1})
 ev('fScenarioGo(19)');time.sleep(.6)
 ev("document.getElementById('rotatePromptDismiss').click()")
 until("document.getElementById('rotatePrompt').getClientRects().length===0")
 time.sleep(.3);screenshot('/tmp/alkadienes-lesson-narrow.png')
 assert ev("document.getElementById('scExit').getClientRects().length>0 && document.getElementById('scStepText').getClientRects().length>0")
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 assert ev("document.querySelectorAll('.lesson').length===4")
 assert not js_errors,js_errors
 Path('/tmp/alkadienes-lesson-evidence.json').write_text(json.dumps({'steps':rows,'validatorWarnings':[],'roundTrip':True,'menuMolecules':8,'explorationForms':3,'javascriptErrors':js_errors,'libraryAndExit':True,'narrowWidth':700},ensure_ascii=False,indent=2))
 print('PASS22steps, actual export roundtrip, eight2D3D molecules, library/Exit, narrow700, noJSerrors',flush=True)
finally:call('session.end',{})
