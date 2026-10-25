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


rows=[]
try:
 for series,count in [('other-alcohols',22)]:
  if os.environ.get('THEORY_SERIES') and series not in os.environ['THEORY_SERIES'].split(','): continue
  source=json.loads(Path('scenarios/'+series+'-nomenclature.scenario.json').read_text())
  navigate('mulermoc-nom-50.html?scenario=scenarios/'+series+'-nomenclature.scenario.json&present=1&from=theory-library&v=progressive-test')
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true')
  ev('window.__validated=fScenarioValidate('+json.dumps(source,ensure_ascii=False)+')')
  assert ev('window.__validated.ok && window.__validated.warnings.length===0')
  assert ev('JSON.stringify(fScenarioActive().steps)===JSON.stringify(window.__validated.steps)')
  for i,step in enumerate(source['steps']):
   ev('fScenarioGo('+str(i)+')')
   until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol']))
   until('mode2D==='+json.dumps(step['mode2D']))
   until('nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
   until("JSON.stringify([...document.querySelectorAll('.comp-hidden')].map(e=>e.id).sort())==="+json.dumps(json.dumps(sorted(step['styleName']['hidden']),separators=(',',':'))))
   ev('window.__expectedNote=document.createElement("div");window.__expectedNote.innerHTML='+json.dumps(step['note'])+';')
   assert ev("document.getElementById('scStepText').textContent.includes(window.__expectedNote.textContent)"),(series,i+1)
   assert ev('viewerMaxH')==step['show']['viewerMaxHeight'],(series,i+1,ev('viewerMaxH'),step['show']['viewerMaxHeight'])
   assert ev('fScenarioPresent().steps['+str(i)+'].show.rule')==step['show']['rule']
   assert ev("!!document.querySelector('#jsmeNomeclatureSVG')")
   expected={'propanediol_1_2': '1,2-προπανοδιόλη', 'propanetriol': '1,2,3-προπανοτριόλη', 'methyl_2_propanediol_1_2': '2-μεθυλο-1,2-προπανοδιόλη', 'butene_3_ol_2': '3-βουτεν-2-όλη', 'penten_4_ol_2': '4-πεντεν-2-όλη', 'penten_2_ol_1': '2-πεντεν-1-όλη', 'methyl_3_buten_3_ol_2': '3-μεθυλο-3-βουτεν-2-όλη', 'methyl_3_pentyn_4_ol_2': '3-μεθυλο-4-πεντιν-2-όλη', 'methyl_4_penten_4_yn_2_ol_1': '4-μεθυλο-4-πεντεν-2-ιν-1-όλη', 'ethyl_3_methyl_4_hexen_3_yn_5_ol_2': '3-αιθυλο-4-μεθυλο-3-εξεν-5-ιν-2-όλη'}
   assert ev('currentMolName')==expected[step['selectedMol']],(i+1,ev('currentMolName'))
   if step['nameAnalysisMode']!='none':
    assert ev('fScenarioShowComponentRule(nameAnalysisMode)')
    assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'"),(i+1,'rule not collapsed')
    if i in [1,2,6,8,9,15]:
     assert ev("document.getElementById('ruleTitle').textContent.includes('χημικής τάξης')"),(i+1,'wrong OH rule')
     assert ev("!!document.querySelector('#ruleContainer [data-row=\"r3-alcohols\"].selected')"),(i+1,'wrong OH row')
    ev("document.getElementById('ruleTitle').click()")
    until("getComputedStyle(document.getElementById('ruleContainer')).display!=='none'")
    ev("document.getElementById('ruleTitle').click()")
    until("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
   if i>=count-2:
    until('window.JSmolReadyFlag===true')
    if i==count-1: screenshot('/tmp/theory-'+series+'-3d.png')
    else: screenshot('/tmp/theory-'+series+'-2d.png')
   rows.append({'series':series,'step':i+1,'molecule':step['selectedMol'],'name':ev('currentMolName')})
  ev("window.__exportBlob=null;window.__urlCreate=URL.createObjectURL;URL.createObjectURL=b=>(window.__exportBlob=b,'blob:lesson-test');window.__anchorClick=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__urlCreate;HTMLAnchorElement.prototype.click=window.__anchorClick")
  exported=json.loads(ev('window.__exportBlob.text()'))
  ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
  assert ev('window.__round.ok && window.__round.warnings.length===0 && JSON.stringify(window.__round.steps)===JSON.stringify(window.__validated.steps)')
 assert not js_errors,js_errors
 Path('/tmp/other-alcohols-theory-evidence.json').write_text(json.dumps({'steps':rows,'roundTrip':True,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 print('PASS',len(rows),'steps, selected lesson validators and export roundtrips, no JavaScript errors')
finally:
 call('browsingContext.close',{'context':ctx})
 call('session.end',{})
