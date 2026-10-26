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


rows=[]; naming_rows=[]; completed=False
try:
 navigate('design/welcome-proposal.html?v=v51-test')
 until("location.pathname.endsWith('/design/welcome-proposal.html')")
 assert ev("document.title.includes('Namelecule')")
 screenshot('/tmp/namelecule-public-welcome-20261026.png')
 ev("document.querySelector('a[href*=theory-library]').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 assert ev("document.querySelectorAll('article.lesson').length===7")
 links=json.loads(ev("JSON.stringify([...document.querySelectorAll('a[href*=scenario]')].map(a=>a.getAttribute('href')))"))
 assert len(links)==8 and all('mulermoc-nom-51.html' in x for x in links),links
 assert ev("document.querySelector('[aria-labelledby=other-alcohols-title] .series-formula').textContent==='CxHy(OH)n'")
 links=[x for x in links if "saturated-monoethers" in x]
 for link in links:
  ev('document.querySelector('+json.dumps('a[href='+json.dumps(link)+']')+').click()')
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true')
  assert ev("typeof MuSVG==='function' && typeof Snap==='undefined' && typeof fDrawDieneParallelDoubleBonds==='undefined' && !!MuLERMoCNote.isAvailable()")
  source=json.loads(ev("JSON.stringify(fScenarioPresent().steps)"))
  ev('window.__validated=fScenarioValidate({scenarioVersion:1,steps:'+json.dumps(source,ensure_ascii=False)+'})')
  assert ev('window.__validated.ok && window.__validated.warnings.length===0')
  for i,step in enumerate(source):
   ev('fScenarioGo('+str(i)+')')
   until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol']))
   until('mode2D==='+json.dumps(step['mode2D'])+' && nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
   assert ev("!!document.querySelector('#jsmeNomeclatureSVG') && typeof currentMolName==='string' && currentMolName.length>0")
   assert ev('viewerMaxH')==step['show']['viewerMaxHeight']
   if ev('fScenarioShowComponentRule(nameAnalysisMode)'):
    assert ev('fScenarioShowComponentRule(nameAnalysisMode)')
    assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
   assert ev('etherNamingMode')==step['etherNamingMode']
   rows.append({'lesson':ev('fScenarioPresent().title'),'step':i+1,'molecule':step['selectedMol'],'name':ev('currentMolName')})
   if i<26:
    ev("document.getElementById('scNext').click()")
    until('fScenarioPresent().index==='+str(i+1))
  naming_expected=[
   ('διμεθυλαιθέρας','μεθοξυμεθάνιο'),('αιθυλομεθυλαιθέρας','μεθοξυαιθάνιο'),
   ('διαιθυλαιθέρας','αιθοξυαιθάνιο'),('μεθυλοπροπυλαιθέρας','1-μεθοξυπροπάνιο'),
   ('ισοπροπυλομεθυλαιθέρας','2-μεθοξυπροπάνιο'),('αιθυλοπροπυλαιθέρας','1-αιθοξυπροπάνιο'),
   ('βουτυλομεθυλαιθέρας','1-μεθοξυβουτάνιο'),('αιθυλοϊσοπροπυλαιθέρας','2-αιθοξυπροπάνιο'),
   ('αιθυλο-sec-βουτυλαιθέρας','2-αιθοξυβουτάνιο'),('ισοβουτυλοϊσοπροπυλαιθέρας','1-ισοπροποξυ-2-μεθυλοπροπάνιο'),
   ('tert-βουτυλοϊσοπροπυλαιθέρας','2-ισοπροποξυ-2-μεθυλοπροπάνιο')]
  keys=source[0]['menuSubset']
  for key,(common,systematic) in zip(keys,naming_expected):
   ev("document.getElementById("+json.dumps(key)+").click()")
   until('selectedMol==='+json.dumps(key))
   for mode,expected in [('common',common),('iupac',systematic)]:
    ev("document.querySelector('#radioEtherNaming [data-naming-mode="+mode+"]').click()")
    until('etherNamingMode==='+json.dumps(mode))
    shown=ev("document.querySelector('.nameCompContainer').textContent.replace(/\\s/g,'')")
    assert shown.replace('+','')==expected,(key,mode,shown,expected)
    ev("document.querySelector('.nameCompContainer [id^=comp]').click()")
    assert ev("!!document.querySelector('#jsmeNomeclatureSVG')")
    naming_rows.append({'molecule':key,'mode':mode,'displayed':shown})
  ev('fScenarioGo(26)')
  until('fScenarioPresent().index===26')
  ev("window.__exportBlob=null;window.__create=URL.createObjectURL;URL.createObjectURL=b=>(window.__exportBlob=b,'blob:lesson-test');window.__click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click")
  exported=json.loads(ev('window.__exportBlob.text()'))
  ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
  assert ev('window.__round.ok && !window.__round.warnings.length && JSON.stringify(window.__round.steps)===JSON.stringify(window.__validated.steps)')
  ev("document.getElementById('scPrev').click()")
  until('fScenarioPresent().index==='+str(len(source)-2))
  if link==links[-1]:
   ev("window.__probe=document.createElement('div');window.__pwn=0;MuLERMoCNote.renderInto(window.__probe,'<p onclick=\"window.__pwn=1\">Κανόνας <b>OH</b></p><script>window.__pwn=2<'+ '/script><a href=\"javascript:alert(1)\">link</a><table><tr><td>δοκιμή</td></tr></table>','html')")
   assert ev("!!window.__probe.querySelector('b') && !!window.__probe.querySelector('table') && !window.__probe.querySelector('script,[onclick],a[href^=javascript]') && window.__pwn===0")
   ev("MuLERMoCNote.renderInto(window.__probe,'<div data-note-include=\"rule-table:1\"></div>','html')")
   assert ev("!!window.__probe.querySelector('.note-embed--rule [data-row=\"r1-c1\"]') && !window.__probe.querySelector('.note-embed--missing')")
   ev("window.__htmlStep=JSON.parse(JSON.stringify(fScenarioPresent().steps[0]));window.__htmlStep.note='<p>HTML <b>OH</b></p>';window.__htmlStep.noteFormat='html';window.__htmlValid=fScenarioValidate({scenarioVersion:1,steps:[window.__htmlStep]})")
   assert ev("window.__htmlValid.ok && window.__htmlValid.steps[0].noteFormat==='html'")
  ev("document.getElementById('scExit').click()")
  until("location.pathname.endsWith('/design/theory-library.html')")
 assert len(rows)==27,len(rows)
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 navigate('design/theory-library.html?v=v51-mobile')
 assert ev("document.querySelectorAll('article.lesson').length===7")
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 screenshot('/tmp/namelecule-public-report-mobile-20261026.png')
 completed=True
 print('PASS monoethers welcome/library/27steps/export/rules/nativeSVG/richNotes/PrevExit/library390px; JSerrors:',len(js_errors))
finally:
 Path('docs/checks/monoethers-browser-20261026.json').write_text(json.dumps({'completed':completed,'steps':rows,'dualNaming':naming_rows,'javascriptErrors':js_errors,'viewport':{'desktop':[1500,1000],'libraryMobile':[390,844]}},ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
