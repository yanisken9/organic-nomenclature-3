"""Actual Firefox React 2D/name regression with the v4 3D bridge. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
import socket,base64,os,struct,json,time,sys
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




result={'completed':False,'checks':[]}
try:
 navigate('mulermoc-nom-52.html?v=rich-editor-'+str(time.time_ns()));app_ready();until('window.JSmolReadyFlag===true')
 until("MuLERMoCScenario.scenarios.length>=2 && MuLERMoCScenario.scenarios.some(s=>s.steps.length>0)")
 sample=json.loads(Path('scenarios/alkanes-nomenclature-branches.scenario.json').read_text())['steps'][0]
 ev('window.testStep='+json.dumps(sample,ensure_ascii=False)+";testStep.note='Τιμή 2 < 3\\n<b>παλιό</b>';testStep.noteFormat='text';MuLERMoCScenario.scenarios=[];MuLERMoCScenario.activeId=null;fScenarioNew('Δοκιμή επεξεργαστή',true).steps=[testStep];fScenarioBuildPanels();fScenarioSetAuthoring(true)")
 until("!!document.querySelector('.scNoteExpandBtn')")
 assert ev("document.querySelector('.snoteRich').isContentEditable && document.querySelector('.snoteRich').textContent.includes('2 < 3')")
 ev("window.originalLegacy=testStep.note;window.promptCount=0;window.confirm=()=>{promptCount++;return true};document.querySelector('.scNoteExpandBtn').click()")
 until('fScenarioNoteEditorIsOpen()')
 assert ev("fScenarioNoteEditorState.st===testStep && document.querySelector('.scNoteEditorPreview').isContentEditable && testStep.noteFormat==='text' && testStep.note===originalLegacy")
 ev("document.querySelector('.scNoteSourceBtn').click();document.querySelector('.scNoteSourceBtn').click();document.querySelector('.scNoteEditorFooter button').click()")
 until('!fScenarioNoteEditorIsOpen()')
 assert ev("promptCount===0 && testStep.note===originalLegacy && testStep.noteFormat==='text'")
 result['checks'].append('real inline contenteditable and modal; legacy literal < preserved; untouched source toggle/cancel does not mutate or prompt')
 ev("document.querySelector('.scNoteExpandBtn').click()")
 until('fScenarioNoteEditorIsOpen()')
 ev("document.querySelector('.scNoteSourceBtn').click();const t=document.querySelector('.scNoteEditorSource');t.value='<p onclick=\"window.__pwn=1\">Νέο <b>κείμενο</b></p><script>window.__pwn=2</script><a href=\"javascript:alert(1)\">link</a><div data-note-include=\"rule-table:alkoxy\"></div>';window.__pwn=0;t.dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('.scNoteSourceBtn').click()")
 assert ev("!document.querySelector('.scNoteEditorPreview script,.scNoteEditorPreview [onclick],.scNoteEditorPreview a[href^=javascript]') && __pwn===0")
 assert ev("!!document.querySelector('.scNoteEditorPreview .note-embed [contenteditable=false],.scNoteEditorPreview [data-note-include][contenteditable=false]')")
 screenshot('/tmp/v52-note-editor-desktop-20261027.png')
 ev("document.querySelector('.scNoteEditorApply').click()")
 until('!fScenarioNoteEditorIsOpen()')
 assert ev("testStep.noteFormat==='html' && testStep.note.includes('data-note-include') && !testStep.note.includes('onclick') && !testStep.note.includes('javascript:') && !testStep.note.includes('<script') && !testStep.note.includes('note-table-scroll') && document.querySelector('.snoteRich b').textContent==='κείμενο'")
 result['checks'].append('source edit upgrades on Apply; sanitizer strips script/event/javascript URL; alkoxy include renders noneditable and serializes as placeholder; inline refreshes')
 ev("window.savedNote=testStep.note;document.querySelector('.scNoteExpandBtn').click()")
 until('fScenarioNoteEditorIsOpen()')
 ev("(()=>{const p=document.querySelector('.scNoteEditorPreview');p.innerHTML='<p>Να απορριφθεί</p>';p.dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('.scNoteEditorFooter button').click()})()")
 until('!fScenarioNoteEditorIsOpen()')
 assert ev("promptCount===1 && testStep.note===savedNote")
 result['checks'].append('modified Cancel confirms and discards draft without changing step')
 ev("document.querySelector('.scNoteExpandBtn').click()")
 until('fScenarioNoteEditorIsOpen()')
 ev("(()=>{const p=document.querySelector('.scNoteEditorPreview');p.innerHTML='<p>Εκκρεμές</p>';p.dispatchEvent(new Event('input',{bubbles:true}));window.savedPurify=window.DOMPurify;window.DOMPurify=null;document.querySelector('.scNoteEditorApply').click()})()")
 assert ev("fScenarioNoteEditorIsOpen() && testStep.note===savedNote")
 ev("window.DOMPurify=window.savedPurify;document.querySelector('.scNoteEditorFooter button').click()")
 until('!fScenarioNoteEditorIsOpen()')
 result['checks'].append('controlled missing-sanitizer fault fails closed without committing draft')
 ev("(()=>{const e=document.querySelector('.snoteRich');e.innerHTML='<p>Άμεση <i>επεξεργασία</i></p>';e.dispatchEvent(new Event('input',{bubbles:true}))})()")
 assert ev("testStep.noteFormat==='html' && testStep.note.includes('<i>επεξεργασία</i>') && !document.querySelector('.snoteRich + .scNoteToolbar .scNoteFormatBtn')")
 result['checks'].append('inline input commits HTML through existing handler; obsolete inline format toggle absent')
 ev("window.savedCreate=URL.createObjectURL;window.savedClick=HTMLAnchorElement.prototype.click;URL.createObjectURL=b=>(window.testExport=b,'blob:export-check');HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=savedCreate;HTMLAnchorElement.prototype.click=savedClick")
 assert json.loads(ev('testExport.text()'))['app']=='mulermoc-nom-52'
 result['checks'].append('new exports identify v52 while scenarioVersion stays1')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 ev("document.querySelector('.scNoteExpandBtn').click()")
 until('fScenarioNoteEditorIsOpen()')
 assert ev("(()=>{const r=document.querySelector('#scNoteEditor').getBoundingClientRect();return r.left>=0 && r.right<=innerWidth && r.height<=innerHeight})()")
 screenshot('/tmp/v52-note-editor-mobile-20261027.png')
 result['checks'].append('modal fits 390px viewport')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/v52-editor-browser-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
