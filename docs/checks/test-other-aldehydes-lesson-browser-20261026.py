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



rows=[];completed=False;ruleToggle=False
names={'propenal': 'προπενάλη', 'methyl_2_propenal': '2-μεθυλοπροπενάλη', 'propanedial': 'προπανοδιάλη', 'methyl_3_penten_2_dial': '3-μεθυλο-2-πεντενοδιάλη', 'ethyl_4_penten_4_yn_2_al': '4-αιθυλο-4-πεντεν-2-ινάλη', 'isopropyl_2_buten_2_dial': '2-ισοπροπυλο-2-βουτενοδιάλη', 'ethyl_2_methyl_3_hexen_2_yn_4_dial': '2-αιθυλο-3-μεθυλο-2-εξεν-4-ινοδιάλη', 'propynal': 'προπινάλη'}
try:
 navigate('design/welcome-proposal.html?v=other-aldehydes-test')
 ev("document.querySelector('a[href*=theory-library]').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 assert ev("document.querySelectorAll('article.lesson').length===8 && document.querySelectorAll('a[href*=scenario]').length===10")
 assert ev("document.querySelector('[aria-labelledby=monoaldehydes-title] .series-formula').textContent==='CνH2νOν ≥ 1'")
 assert ev("!!document.querySelector('[aria-labelledby=other-aldehydes-title] a') && !document.querySelector('[aria-labelledby=other-aldehydes-title] .pending')")
 ev("document.querySelector('a[href*=other-aldehydes]').click()")
 until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
 app_ready();until('window.JSmolReadyFlag===true')
 source=json.loads(ev('JSON.stringify(fScenarioPresent().steps)'))
 assert len(source)==26
 ev('window.__validated=fScenarioValidate({scenarioVersion:1,steps:'+json.dumps(source,ensure_ascii=False)+'})')
 assert ev('window.__validated.ok && !window.__validated.warnings.length')
 for i,step in enumerate(source):
  # Advance naturally using Next below; do not apply each step twice.
  until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol']))
  until('mode2D==='+json.dumps(step['mode2D'])+' && nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
  assert ev('currentMolName')==names[step['selectedMol']]
  assert ev('JSON.stringify(window.nameHiddenComps)')==json.dumps(step['styleName']['hidden'],separators=(',',':'))
  assert ev("!!document.querySelector('#jsmeNomeclatureSVG svg')")
  assert ev('viewerMaxH')==420
  if step['nameAnalysisMode']!='none':
   assert ev('fScenarioShowComponentRule(nameAnalysisMode)')
   assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
   if not ruleToggle:
    ev("document.getElementById('ruleTitle').click()")
    until("getComputedStyle(document.getElementById('ruleContainer')).display!=='none'")
    ev("document.getElementById('ruleTitle').click()")
    until("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
    ruleToggle=True
  clipped=json.loads(ev("""JSON.stringify((()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),r=s.getBoundingClientRect();return [...s.querySelectorAll('text')].filter(e=>{const b=e.getBoundingClientRect();return b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1}).map(e=>e.textContent)})())"""))
  assert not clipped,(i+1,clipped)
  if i==22:screenshot('/tmp/other-aldehydes-lesson-tie-20261026.png')
  if i==24:
   shown=json.loads(ev("JSON.stringify([...document.querySelectorAll('#molMenu .menuLi')].map(e=>e.id))"))
   # Some builds name the menu container differently; inspect subset through IDs.
   if not shown:shown=json.loads(ev("JSON.stringify([...document.querySelectorAll('.menuLi')].filter(e=>getComputedStyle(e).display!=='none').map(e=>e.id))"))
   assert shown==source[0]['menuSubset'],shown
  rows.append(dict(step=i+1,molecule=step['selectedMol'],name=ev('currentMolName'),analysis=step['nameAnalysisMode'],hidden=step['styleName']['hidden'],clipped=clipped))
  if i<25:
   ev("document.getElementById('scNext').click()")
   until('fScenarioPresent().index==='+str(i+1))
 assert ruleToggle
 # The final step uses the existing per-molecule camera and complete3D model.
 until('mainChainPool3DKey==='+json.dumps(source[-1]['selectedMol']))
 until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))===21")
 assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
 for component in ['comp1','comp3','comp9']:
  ev('document.getElementById('+json.dumps(component)+').click()')
  assert ev("!!document.querySelector('#jsmeNomeclatureSVG svg')")
 ev('fScenarioGo(25)')
 until('fScenarioPresent().index===25')
 screenshot('/tmp/other-aldehydes-lesson-final-20261026.png')
 ev("window.__exportBlob=null;window.__create=URL.createObjectURL;URL.createObjectURL=b=>(window.__exportBlob=b,'blob:lesson-test');window.__click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click")
 exported=json.loads(ev('window.__exportBlob.text()'))
 ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
 assert ev('window.__round.ok && !window.__round.warnings.length && JSON.stringify(window.__round.steps)===JSON.stringify(window.__validated.steps)')
 ev("document.getElementById('scPrev').click()")
 until('fScenarioPresent().index===24')
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 navigate('design/theory-library.html?v=other-aldehydes-mobile')
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 assert ev("document.querySelectorAll('article.lesson').length===8")
 screenshot('/tmp/other-aldehydes-library-mobile-20261026.png')
 unexpected=[e for e in js_errors if not ("this.viewer is null" in e.get('text','') and any('chemapps.stolaf.edu' in c.get('url','') for c in e.get('stackTrace',{}).get('callFrames',[])))]
 assert not unexpected,unexpected
 completed=True
 print('PASS functional26steps/8molecules/names/hidden/rules/open-close/Next/Prev/export/schema/Exit/menu order/final3D/library390px; knownJSmolErrors:',len(js_errors))
finally:
 Path('docs/checks/other-aldehydes-lesson-browser-20261026.json').write_text(json.dumps(dict(completed=completed,steps=rows,ruleToggle=ruleToggle,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
