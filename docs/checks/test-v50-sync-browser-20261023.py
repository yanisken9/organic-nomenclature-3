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

checks=[]
def passed(x):
 checks.append(x);print('PASS '+x,flush=True)
def viewport(w,h):
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});time.sleep(.7)
try:
 navigate('index.html');until("location.pathname.endsWith('/design/welcome-proposal.html')")
 assert ev("[...document.querySelectorAll('a')].some(a=>a.href.includes('mulermoc-nom-50.html'))")
 passed('index -> Namelecule welcome -> v50 links')
 navigate('design/theory-library.html')
 assert ev("[...document.querySelectorAll('a.action')].filter(a=>a.href.includes('mulermoc-nom-50.html')).length===3")
 passed('three library lessons point to v50')
 navigate('mulermoc-nom-50.html');app_ready();until('window.JSmolReadyFlag===true')
 ev('fDeselectMol()')
 assert ev("!!document.getElementById('nameSettingsBtn')&&!!document.querySelector('.nameEmptyHint')")
 passed('persistent naming shell and empty hint')
 for molecule,expected in [('propyne',True),('ethanenitrile',True),('propadiene',True),('penten_3_yne_1',True),('pentyn_4_one_2',True),('propynal',True),('ethane',False),('ethene',False)]:
  ev("selectedMol="+json.dumps(molecule)+";mode2D='skeletal';fLoadMol2D();fShowNameAnalysis()")
  assert ev('fMolHasSpCarbon()')==expected,molecule
  assert ev("!!document.querySelector('#jsmeNomeclatureSVG svg')"),molecule
  if expected:assert ev("[...document.querySelectorAll('#jsmeNomeclatureSVG svg text')].every(e=>e.textContent.trim()!=='C')"),molecule
 passed('generalized sp-carbon skeletal labels and alkane/alkene controls')
 for lesson in ['alkanes','alkenes','alkynes']:
  navigate('mulermoc-nom-50.html?scenario=scenarios/'+lesson+'-nomenclature-branches.scenario.json&present=1&from=theory-library')
  app_ready();until("MuLERMoCScenario.present&&!document.documentElement.classList.contains('lesson-loading')")
  assert ev('fScenarioPresent().steps.length===22')
  for i in range(22):
   ev('fScenarioGo('+str(i)+')');time.sleep(.15)
   assert ev('fScenarioPresent().index==='+str(i))
  ev('fScenarioExitPresent()');until("location.pathname.endsWith('/design/theory-library.html')")
  passed(lesson+' 22 steps and Exit to library')
 navigate('mulermoc-nom-50.html?scenario='+__import__('urllib.parse',fromlist=['quote']).quote('scenarios/Αλκάνια-Αιθάνιο-τεστ.scenario.json')+'&present=1')
 app_ready();until('MuLERMoCScenario.present');ev('fScenarioGo(4)');time.sleep(.7)
 viewport(1800,1000)
 for side in ['left','right',None]:
  ev('fScenarioPresent().steps[4].styleText.position='+json.dumps(side)+';fScenarioGo(4)');time.sleep(.8)
  actual=ev("document.getElementById('scStepText').parentElement.classList.contains('mainApp3Columns')")
  assert actual==(side is not None),(side,actual)
  if side:
   assert ev("document.getElementById('pageContainer').classList.contains('scText"+side.title()+"')")
   assert ev("Math.abs(document.getElementById('scStepText').getBoundingClientRect().width-parseFloat(getComputedStyle(document.getElementById('scStepText')).flexBasis))<2")
 assert ev("document.getElementById('pageTitle').getBoundingClientRect().top>=document.getElementById('scenarioPlayBar').getBoundingClientRect().bottom")
 passed('wide top/left/right text placement; title clears play bar')
 ev("fScenarioPresent().steps[4].styleText.position='left';fScenarioGo(4)")
 viewport(900,700)
 assert ev("!document.getElementById('pageContainer').classList.contains('scTextLeft')&&!document.getElementById('scStepText').parentElement.classList.contains('mainApp3Columns')")
 assert ev("getComputedStyle(document.getElementById('pageTitle')).display!=='none'")
 assert ev("document.getElementById('pageTitle').getBoundingClientRect().top>=document.getElementById('scenarioPlayBar').getBoundingClientRect().bottom")
 passed('900x700 fallback and title clears play bar')
 viewport(1800,1000)
 assert ev("document.getElementById('pageContainer').classList.contains('scTextLeft')")
 screenshot('/tmp/namelecule-v50-side-rail.png')
 ev('fScenarioExitPresent()');time.sleep(.5)
 assert ev("!document.getElementById('pageContainer').classList.contains('scTextLeft')")
 passed('resize restores rail; Exit clears rail')
 # Firefox reports document-encoding and external font failures as javascript logs.
 # Preserve them separately; they are not application exceptions.
 non_application=[e for e in js_errors if e.get('text','').startswith(('downloadable font:', 'Η κωδικοποίηση χαρακτήρων'))]
 application_errors=[e for e in js_errors if e not in non_application]
 assert not application_errors,application_errors
 passed('no application JavaScript errors; browser/resource diagnostics retained')
 Path('/tmp/namelecule-v50-browser-results.json').write_text(json.dumps({'checks':checks,'jsErrors':js_errors},ensure_ascii=False,indent=2))
finally:
 call('session.end',{})
