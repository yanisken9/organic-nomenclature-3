"""Actual Firefox lesson checks. Artifacts only under /tmp; requires localhost8013/BiDi9234."""
import socket,base64,os,struct,json,time
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9234),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9234\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
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



rows=[]
def rule_state():
 return json.loads(ev("JSON.stringify({outer:!!document.getElementById('ruleTheoryContainer').getClientRects().length,open:!!document.getElementById('ruleContainer') && !!document.getElementById('ruleContainer').getClientRects().length,title:document.getElementById('ruleTitle')?.textContent.trim(),selected:[...document.querySelectorAll('#ruleContainer [data-row].selected')].map(e=>e.dataset.row),flag:ruleFlag})"))
try:
 source=json.loads(Path('scenarios/alkanes-nomenclature-branches.scenario.json').read_text())
 navigate('mulermoc-nom-50.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=alkane-rule-test')
 until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
 app_ready();until('window.JSmolReadyFlag===true')
 for i,step in enumerate(source['steps']):
  ev('fScenarioGo('+str(i)+')')
  until('selectedMol==='+json.dumps(step['selectedMol'])+' && nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
  auto=step['nameAnalysisMode']!='none'
  if auto:
   until("!!document.getElementById('ruleTitle') && !document.getElementById('ruleContainer')?.getClientRects().length")
   state=rule_state();assert state['outer'] and not state['open'] and state['selected'],(i+1,state)
  rows.append({'step':i+1,'mode':step['nameAnalysisMode'],'rule':rule_state()})
 # On a synthesis step previously hiding the rule, all five relevant parts open it.
 ev('fScenarioGo(19)');until("nameAnalysisMode==='none'")
 cases=[('comp5','ανθρακικής','r1-c6'),('comp6','τύπου','r2-single'),('comp9','χημικής','r3-hydrocarbons'),('comp1','αλκυλίων','alkyl-αιθυλο'),('comp3','αλκυλίων','alkyl-μεθυλο')]
 for component,title,row in cases:
  ev('document.getElementById('+json.dumps(component)+').click()')
  state=rule_state();assert state['outer'] and not state['open'] and title in state['title'] and row in state['selected'],(component,state)
  ev("document.getElementById('ruleTitle').click()")
  until("!!document.getElementById('ruleContainer').getClientRects().length")
  assert ev("ruleFlag && document.getElementById('ruleTitle').classList.contains('open')")
 screenshot('/tmp/alkane-manual-rule-open.png')
 # Closing is still possible; the next component selection opens its own table.
 ev("document.getElementById('ruleTitle').click()")
 until("!document.getElementById('ruleContainer').getClientRects().length")
 assert not ev("ruleFlag || document.getElementById('ruleTitle').classList.contains('open')")
 ev("document.getElementById('comp5').click()")
 assert not rule_state()['open']
 ev("document.getElementById('ruleTitle').click()")
 until("!!document.getElementById('ruleContainer').getClientRects().length")
 ev('fScenarioGo(1)');until("nameAnalysisMode==='compCarbonsCount'")
 assert rule_state()['outer'] and not rule_state()['open']
 for series in ['alkenes','alkynes','alkadienes','enynes']:
  navigate('mulermoc-nom-50.html?scenario=scenarios/'+series+'-nomenclature-branches.scenario.json&present=1&v=alkane-isolation')
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true');ev('fScenarioGo(1)');until("nameAnalysisMode==='compCarbonsCount'")
  assert not ev("fScenarioShowComponentRule(nameAnalysisMode)")
  assert not rule_state()['open'],(series,rule_state())
 navigate('mulermoc-nom-50.html?v=alkane-free-isolation');app_ready();until('window.JSmolReadyFlag===true')
 assert not ev("fScenarioShowComponentRule('compCarbonsCount')")
 Path('/tmp/alkane-manual-rules-errors.json').write_text(json.dumps(js_errors,ensure_ascii=False,indent=2))
 local_errors=[e for e in js_errors if not e.get('stackTrace',{}).get('callFrames',[{}])[0].get('url','').startswith('https://chemapps.stolaf.edu/')]
 assert not local_errors,local_errors
 Path('/tmp/alkane-manual-rules-evidence.json').write_text(json.dumps({'steps':rows,'componentClicks':cases,'otherLessonsUnaffected':4,'freeExploreUnaffected':True,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 print('PASS 21 initially collapsed steps, five click/manual-open cases, open-to-next-step collapse, other lessons isolation')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
