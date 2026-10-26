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


try:
 navigate('mulermoc-nom-51.html?v=note-authoring-test')
 app_ready();until('window.JSmolReadyFlag===true')
 until('MuLERMoCScenario.scenarios.length>=2 && MuLERMoCScenario.scenarios[0].steps.length>0')
 ev("window.__sc=fScenarioNew('Έλεγχος v51',true);window.__st=fScenarioCapture();window.__st.n=1;window.__st.title='HTML';window.__st.note='<p>Αλκοόλες <b>OH</b></p>';window.__st.noteFormat='html';window.__sc.steps=[window.__st];fScenarioSyncLegacy();fScenarioBuildPanels()")
 ev("window.__input=document.createElement('textarea');window.__button=document.createElement('button');document.body.append(window.__input,window.__button);fScenarioOpenNoteEditor(window.__st,window.__input,function(){},window.__button)")
 assert ev("document.getElementById('scNoteEditor').open && !!document.querySelector('#scNoteEditor .scNoteComponentBtn')")
 ev("document.querySelector('#scNoteEditor .scNoteEditorText').value='<p>Νέο <b>OH</b></p>';document.querySelector('#scNoteEditor .scNoteEditorText').dispatchEvent(new Event('input',{bubbles:true}))")
 assert ev("window.__input.value===window.__st.note && window.__st.note.includes('Νέο')")
 ev("document.querySelector('#scNoteEditor .scNoteComponentBtn').click()")
 assert ev("document.querySelectorAll('#scNoteEditor .scNoteComponentOpt').length===5")
 ev("document.querySelector('#scNoteEditor .scNoteComponentOpt').click()")
 assert ev("window.__st.note.includes('data-note-include')")
 ev("document.querySelector('#scNoteEditor .scNoteEditorClose').click()")
 until("!document.getElementById('scNoteEditor').open && document.activeElement===window.__button")
 ev("window.__beforeNote=window.__st.note;fScenarioUpdateStep(window.__sc.id,0)")
 assert ev("window.__sc.steps[0].noteFormat==='html' && window.__sc.steps[0].note===window.__beforeNote")
 ev("window.__exportBlob=null;window.__create=URL.createObjectURL;URL.createObjectURL=b=>(window.__exportBlob=b,'blob:test');window.__click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click")
 exported=json.loads(ev('window.__exportBlob.text()'))
 ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
 assert ev("window.__round.ok && !window.__round.warnings.length && window.__round.steps[0].noteFormat==='html' && window.__round.steps[0].note===window.__beforeNote")
 assert not js_errors,js_errors
 Path('/tmp/v51-authoring-20261026.json').write_text(json.dumps({'modalOpenLiveSyncCloseFocus':True,'fiveComponentMenu':True,'updatePreservesHTML':True,'exportValidationPreservesHTML':True,'javascriptErrors':js_errors},indent=2))
 print('PASS v51 HTML note modal/live sync/five-key menu/Update/export/validation, zeroJSerrors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
