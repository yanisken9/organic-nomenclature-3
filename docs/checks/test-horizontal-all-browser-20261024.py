"""Actual Firefox lesson checks. Artifacts only under /tmp; requires localhost8013/BiDi9236."""
import socket,base64,os,struct,json,time
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9236),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9236\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
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



rows=[];clicks=[]
def state():
 return json.loads(ev("JSON.stringify({outer:!!document.getElementById('ruleTheoryContainer').getClientRects().length,open:!!document.getElementById('ruleContainer')?.getClientRects().length,title:document.getElementById('ruleTitle')?.textContent,selected:[...document.querySelectorAll('#ruleContainer [data-row].selected')].map(e=>e.dataset.row)})"))
try:
 for series in ['alkanes','alkenes','alkynes','alkadienes','enynes']:
  source=json.loads(Path('scenarios/'+series+'-nomenclature-branches.scenario.json').read_text())
  navigate('mulermoc-nom-50.html?scenario=scenarios/'+series+'-nomenclature-branches.scenario.json&present=1&from=theory-library&v=horizontal-rules-test')
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true')
  ev('window.__validated=fScenarioValidate('+json.dumps(source,ensure_ascii=False)+')');assert ev('window.__validated.ok && !window.__validated.warnings.length')
  for i,step in enumerate(source['steps']):
   ev('fScenarioGo('+str(i)+')')
   until('selectedMol==='+json.dumps(step['selectedMol'])+' && nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
   until('mainChainPool3DKey==='+json.dumps(step['selectedMol']))
   result=json.loads(ev("JSON.stringify({chain:mainChainAtomsList,name:currentMolName,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),signature3:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)})"))
   assert result['signature']==result['signature3'],(series,i+1,result)
   if step['nameAnalysisMode']!='none':
    r=state();assert r['outer'] and not r['open'] and r['selected'],(series,i+1,r)
   if series=='alkanes' and i==11:
    assert result['chain']==[1,2,3,4],result
    assert ev("JSON.stringify(fGetHydrocarbonBranchHighlight(1).atoms.filter(n=>allAtomsTypeList[n-1]==='C').sort((a,b)=>a-b))")=='[5,6]'
    positions=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>({text:e.textContent,x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y})))"))
    assert len(positions)==4,positions
    assert max(p['y'] for p in positions)-min(p['y'] for p in positions)<5,positions
    screenshot('/tmp/horizontal-dimethylbutane.png')
   if series=='alkanes' and i==11:
    # Runtime-only fixture: old bent stored parent must not bypass resolved UI.
    ev("nameExamples.dimethyl_2_3_butane.mainChain_Condensed=[1,2,3,6];mainChainMode='data';fLoadMol2D();fCalcMainChain3D();fShowNameAnalysis();nameAnalysisMode='compCarbonsCount';fExplainNameComp()")
    assert ev('JSON.stringify(mainChainAtomsList)')=='[1,2,3,4]'
    assert ev('JSON.stringify(highAtoms)')=='[1,2,3,4]'
    ev("window.__labels=[];window.__realScript=Jmol.script;Jmol.script=function(a,s){window.__labels.push(s);return window.__realScript(a,s)};fShowNumbering3D();Jmol.script=window.__realScript")
    labels=json.loads(ev('JSON.stringify(window.__labels)'))
    chain3=json.loads(ev('JSON.stringify(mainChainAtoms3D)'))
    assert len(labels)==len(chain3)
    for j,atom in enumerate(chain3):assert 'atomno = '+str(atom)+'}' in labels[j],(j,atom,labels[j])
    until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===4")
    positions=json.loads(ev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>({text:e.textContent,y:e.getBoundingClientRect().y})))"))
    assert len(positions)==4 and max(p['y'] for p in positions)-min(p['y'] for p in positions)<5,positions
    screenshot('/tmp/horizontal-data-mode.png')
    ev("nameExamples.dimethyl_2_3_butane.mainChain_Condensed=[]")
   rows.append({'series':series,'step':i+1,'molecule':step['selectedMol'],**result})
  # All five principal/alkyl component types available on the large completed example.
  ev('fScenarioGo('+str(len(source['steps'])-3)+')');until("nameAnalysisMode==='none'")
  for component in ['comp5','comp6','comp9','comp1','comp3']:
   ev('document.getElementById('+json.dumps(component)+').click()')
   r=state();assert r['outer'] and not r['open'] and r['selected'],(series,component,r)
   ev("document.getElementById('ruleTitle').click()")
   until("!!document.getElementById('ruleContainer').getClientRects().length")
   clicks.append({'series':series,'component':component,'rule':r})
  if series=='enynes':
   for component in ['comp4','comp7','comp8']:
    ev('document.getElementById('+json.dumps(component)+').click()');r=state();assert r['outer'] and not r['open'] and r['selected'],(component,r)
  ev('fScenarioGo(1)');until("nameAnalysisMode==='compCarbonsCount'");assert not state()['open']
  print('PASS',series,len(source['steps']),flush=True)
 Path('/tmp/horizontal-all-browser-evidence.json').write_text(json.dumps({'steps':rows,'clicks':clicks,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 local=[e for e in js_errors if not e.get('stackTrace',{}).get('callFrames',[{}])[0].get('url','').startswith('https://chemapps.stolaf.edu/')]
 assert not local,[e.get('text') for e in local]
 print('PASS111 steps, 25componentclicks, mixedbondcomponents, 2D3Dchemistry, horizontal numbering; external errors',len(js_errors))
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
