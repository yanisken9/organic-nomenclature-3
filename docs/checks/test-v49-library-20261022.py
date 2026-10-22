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
try:
 call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':"()=>{let original=window.fetch;window.__lessonFetch=[];window.fetch=function(input,options){if(String(input)==='scenarios/alkenes-nomenclature-branches.scenario.json')window.__lessonFetch.push(options&&options.cache);return original.apply(this,arguments);};}"})
 navigate('design/welcome-proposal.html?v=v49-test')
 ev("document.querySelector('a.action[href*=\"theory-library\"]').click()")
 until("location.pathname.endsWith('/theory-library.html') && !!document.querySelector('.lesson[aria-labelledby=alkenes-title] .action')")
 assert ev("document.querySelector('.lesson[aria-labelledby=alkenes-title] .action').href.includes('mulermoc-nom-49.html')")
 for width in (1500,390):
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  assert ev('document.documentElement.scrollWidth<=innerWidth'),width
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 ev("document.querySelector('.lesson[aria-labelledby=alkenes-title] .action').click()")
 until("typeof fScenarioActive==='function' && !!fScenarioActive() && fScenarioActive().steps.length===22 && !document.documentElement.classList.contains('lesson-loading')")
 assert ev("location.pathname.endsWith('49.html') && MuLERMoCScenario.present && selectedMol==='ethene' && window.__lessonFetch.includes('no-store')")
 expected=json.loads(Path('scenarios/alkenes-nomenclature-branches.scenario.json').read_text())
 assert ev('fScenarioActive().steps[0].note')==expected['steps'][0]['note']
 assert ev("!fScenarioActive().showStepNumbers && fScenarioActive().reserveTitleSpace")
 assert ev("['comp5','comp6','comp9'].every(id=>document.getElementById(id).classList.contains('comp-hidden'))")
 for i in range(22):
  ev('fScenarioGo('+str(i)+')');time.sleep(.2)
  assert ev('selectedMol')==expected['steps'][i]['selectedMol'],i+1
  assert ev('fScenarioActive().steps['+str(i)+'].note')==expected['steps'][i]['note'],i+1
  if i in (1,2,3):
   row={1:'r1-c2',2:'r2-double',3:'r3-hydrocarbons'}[i]
   assert ev("!!document.querySelector('#ruleContainer [data-row=\""+row+"\"].selected')"),i+1
  if i in (8,17):
   row='alkyl-μεθυλο' if i==8 else 'alkyl-αιθυλο'
   assert ev("document.querySelectorAll('.ruleAlkyl [data-row^=\"alkyl-\"]').length===8 && !!document.querySelector('.ruleAlkyl [data-row=\""+row+"\"].selected')")
   ev("if(getComputedStyle(document.getElementById('ruleContainer')).display==='none')document.getElementById('ruleTitle').click()")
   time.sleep(.35)
   assert ev("document.querySelector('.ruleAlkyl').scrollWidth<=document.querySelector('.ruleAlkyl').clientWidth+1")
   if i==8:screenshot('/tmp/v49-lesson-step9.png')
  if i in (14,15,16):assert ev("JSON.stringify(mainChainAtomsList)==='[1,2,3,4,5,6]'"),i+1
 assert ev("document.getElementById('jsmeNomeclatureDIV').getClientRects().length>0 && document.getElementById('nomeclature3D').getClientRects().length>0")
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/theory-library.html')")
 ev("document.querySelector('.back').click()")
 until("location.pathname.endsWith('/welcome-proposal.html')")
 print('PASS welcome/library/mobile + all22steps/exact notes/rules/hidden names/chains/3D/Exit/back',flush=True)
 navigate('mulermoc-nom-49.html?scenario=scenarios/missing-v49.json&present=1')
 until("document.getElementById('lessonLoadingText').textContent.includes('δεν μπόρεσε')")
 assert ev("document.documentElement.classList.contains('lesson-loading') && getComputedStyle(document.getElementById('pageContainer')).visibility==='hidden'")
 assert not js_errors,js_errors
 print('PASS missing-lesson error and no Javascript errors',flush=True)
finally:
 call('session.end',{})
