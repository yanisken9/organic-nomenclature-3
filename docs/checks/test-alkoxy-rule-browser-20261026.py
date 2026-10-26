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




rows=[];regressions=[];completed=False
try:
 navigate('design/theory-library.html?v=alkoxy-rule-test')
 ev("document.querySelector('a[href*=saturated-monoethers]').click()")
 until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
 app_ready();until('window.JSmolReadyFlag===true')
 source=json.loads(ev('JSON.stringify(fScenarioPresent().steps)'));assert len(source)==27
 ev('window.__valid=fScenarioValidate({scenarioVersion:1,steps:'+json.dumps(source,ensure_ascii=False)+'})')
 assert ev('window.__valid.ok && !window.__valid.warnings.length')
 for i,step in enumerate(source):
  until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol']))
  enabled=step['show'].get('alkoxyRule',False)
  assert ev('fScenarioShowAlkoxyRule()')==enabled
  count=ev("document.querySelectorAll('#ruleTheoryContainer .ruleAlkoxy').length")
  assert count==(1 if enabled else 0),(i+1,count)
  if enabled:
   assert ev("getComputedStyle(document.getElementById('ruleTheoryContainer')).display!=='none'")
   assert ev("document.querySelectorAll('.ruleAlkoxy [data-row]').length===5")
   expected=ev("fEtherPrefixGroups().find(g=>g.kind==='alkoxy').name")
   selected=ev("document.querySelector('.ruleAlkoxy [data-row].selected').getAttribute('data-row')")
   assert selected=='alkoxy-'+expected,(i+1,expected,selected)
   supplementary=ev("!!document.getElementById('alkoxyRuleTitle')")
   title='alkoxyRuleTitle' if supplementary else 'ruleTitle'
   container='alkoxyRuleContainer' if supplementary else 'ruleContainer'
   assert ev('document.getElementById('+json.dumps(title)+').textContent.trim()')=='Ονόματα αλκοξυομάδων και προθέματα'
   assert ev('getComputedStyle(document.getElementById('+json.dumps(container)+')).display')=='none'
   if supplementary and step['nameAnalysisMode']=='compCarbonsCount':
    assert ev("document.getElementById('ruleTitle').textContent.trim()")=='Κανόνας συνθετικού ανθρακικής αλυσίδας'
   if supplementary and step['nameAnalysisMode']=='compSecondSub2':
    assert ev("document.getElementById('ruleTitle').textContent.trim()")=='Ονόματα αλκυλίων και προθέματα'
   ev('document.getElementById('+json.dumps(title)+').click()')
   until('getComputedStyle(document.getElementById('+json.dumps(container)+')).display!=="none"')
   until('document.getElementById('+json.dumps(container)+').getBoundingClientRect().height>120')
   if supplementary and ev("!!document.getElementById('ruleContainer')"):
    assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
   if i==21:screenshot('/tmp/alkoxy-rule-isopropoxy-20261026.png')
   # Leave it open; the next authored step must reset to closed.
  rows.append(dict(step=i+1,molecule=step['selectedMol'],enabled=enabled,ruleCount=count,name=ev('currentMolName'),common=ev('currentMolCommonName')))
  if i<26:
   ev("document.getElementById('scNext').click()")
 # Per-step authored reference survives Update/Save, export and validation.
 ev('window.__savedSteps=JSON.parse(JSON.stringify(fScenarioPresent().steps));fScenarioGo(4)')
 until('fScenarioPresent().index===4')
 ev('fScenarioUpdateStep(fScenarioPresent().id,4)')
 assert ev('fScenarioPresent().steps[4].show.alkoxyRule===true')
 ev('fScenarioPresent().steps=window.__savedSteps;fScenarioGo(26)')
 until('fScenarioPresent().index===26')
 ev("window.__blob=null;window.__create=URL.createObjectURL;window.__click=HTMLAnchorElement.prototype.click;URL.createObjectURL=b=>(window.__blob=b,'blob:test');HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click")
 exported=json.loads(ev('window.__blob.text()'));ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
 assert ev('window.__round.ok && !window.__round.warnings.length && JSON.stringify(window.__round.steps)===JSON.stringify(window.__valid.steps)')
 assert sum(s['show'].get('alkoxyRule',False) for s in exported['steps'])==19
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 for lesson,index,expected in [('saturated-monoalcohols',10,'Ονόματα αλκυλίων και προθέματα'),('saturated-monoaldehydes',10,'Ονόματα αλκυλίων και προθέματα'),('alkanes-nomenclature',1,'Κανόνας συνθετικού ανθρακικής αλυσίδας')]:
  ev("document.querySelector('a[href*="+lesson+"]').click()")
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true')
  ev('fScenarioGo('+str(index)+')')
  until('fScenarioPresent().index==='+str(index))
  assert ev("!document.querySelector('#ruleTheoryContainer .ruleAlkoxy') && !fScenarioShowAlkoxyRule()")
  assert ev("document.getElementById('ruleTitle').textContent.trim()")==expected
  assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
  regressions.append(dict(lesson=lesson,step=index+1,title=expected))
  ev("document.getElementById('scExit').click()")
  until("location.pathname.endsWith('/design/theory-library.html')")
 unexpected=[e for e in js_errors if not ("this.viewer is null" in e.get('text','') and any('chemapps.stolaf.edu' in c.get('url','') for c in e.get('stackTrace',{}).get('callFrames',[])))]
 assert not unexpected,unexpected
 completed=True
 print('PASS 27steps/19rule tables closed+open/selected rows/existing rules/Update/export-schema/3other lesson regressions; knownJSmolErrors:',len(js_errors))
finally:
 Path('docs/checks/alkoxy-rule-browser-20261026.json').write_text(json.dumps(dict(completed=completed,steps=rows,regressions=regressions,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
