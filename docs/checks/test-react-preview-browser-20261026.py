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

result={'completed':False};preview='react-preview/dist/'
def shot(name):
 data=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'})['data']
 Path('/tmp/react-preview-'+name+'-20261026.png').write_bytes(base64.b64decode(data))
try:
 navigate(preview)
 until("!!document.querySelector('.hero h1')")
 assert ev("document.title.includes('React preview')")
 ev("Promise.all([...document.images].map(i=>i.decode()))")
 assert ev("[...document.images].every(i=>i.naturalWidth>0)")
 assert ev("document.querySelector('.expanded-ethanol').getAttribute('viewBox')==='0 0 180 115'")
 shot('welcome-desktop')
 for name in ['login','games','teacher']:
  ev("document.querySelector('[data-panel=\""+name+"\"]').click()")
  until("!!document.querySelector('dialog[open]')")
  assert ev("document.querySelector('dialog h2').textContent.length>0")
  if name=='teacher':assert ev("document.querySelector('dialog a').href.endsWith('/mulermoc-nom-51.html')")
  ev("document.querySelector('dialog button').click()")
  until("!document.querySelector('dialog')")
  assert ev("document.activeElement.dataset.panel==='"+name+"'")
 ev("document.querySelector('[data-panel=login]').click()")
 until("!!document.querySelector('dialog[open]')")
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':'\ue00c'},{'type':'keyUp','value':'\ue00c'}]}]})
 until("!document.querySelector('dialog')")
 assert ev("document.activeElement.dataset.panel==='login'")
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 shot('welcome-mobile')
 ev("document.querySelector('a[href=\"#/library\"]').click()")
 until("document.querySelectorAll('article.lesson').length===9")
 assert ev("document.querySelectorAll('a[href*=scenario]').length===12")
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 parity=ev("""(async()=>{
 const original=new DOMParser().parseFromString(await(await fetch('../../design/theory-library.html')).text(),'text/html');
 const norm=x=>x.textContent.replace(/\\s+/g,' ').trim();
 const old=[...original.querySelectorAll('article.lesson')],now=[...document.querySelectorAll('article.lesson')];
 const links=[...original.querySelectorAll('a[href*=scenario]')].map(a=>new URL(a.getAttribute('href'),new URL('../../design/theory-library.html',location.href)).href);
 return JSON.stringify({cardTextParity:old.every((a,i)=>norm(a)===norm(now[i])),linksParity:links.every((href,i)=>href===document.querySelectorAll('a[href*=scenario]')[i].href),sourceCards:old.length,sourceLinks:links.length});
 })()""")
 parity=json.loads(parity);assert parity['cardTextParity'] and parity['linksParity'],parity
 result['parity']=parity
 shot('library-mobile')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 shot('library-desktop')
 call('browsingContext.traverseHistory',{'context':ctx,'delta':-1})
 until("!!document.querySelector('.hero h1')")
 call('browsingContext.traverseHistory',{'context':ctx,'delta':1})
 until("document.querySelectorAll('article.lesson').length===9")
 call('browsingContext.reload',{'context':ctx,'wait':'complete'})
 until("document.querySelectorAll('article.lesson').length===9")
 result['previewConsoleErrors']=list(js_errors);assert not js_errors,js_errors
 ev("document.querySelector('a[href*=other-ketones-nomenclature]').click()")
 until("typeof fScenarioPresent==='function' && fScenarioPresent().steps.length===28 && !document.documentElement.classList.contains('lesson-loading')")
 app_ready()
 assert ev("Object.keys(nameExamples).length===126")
 ev("document.getElementById('scNext').click()")
 until('fScenarioPresent().index===1')
 assert ev("typeof fScenarioReadNoteImageFile==='function' && typeof fScenarioInsertNoteImageByUrl==='function'")
 # Real browser FileReader with a genuine raster File; native OS picker interaction
 # itself isn't automated. The upstream input and button wiring are inspected too.
 ev("""window.__oldPrompt=window.prompt;window.prompt=()=> 'Δοκιμαστική εικόνα';
 window.__pickerTest={state:{note:'',noteFormat:'html'},input:document.createElement('textarea'),events:0};
 document.body.appendChild(__pickerTest.input);__pickerTest.input.addEventListener('input',()=>__pickerTest.events++);
 var bytes=Uint8Array.from(atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aL1sAAAAASUVORK5CYII='),c=>c.charCodeAt(0));
 var file=new File([bytes],'pixel.png',{type:'image/png'});
 fScenarioNoteImagePending={noteInput:__pickerTest.input,st:__pickerTest.state};
 fScenarioReadNoteImageFile({files:[file],value:''});""")
 until("__pickerTest.events===1 && __pickerTest.state.note.includes('data:image/png;base64,')")
 assert ev("__pickerTest.input.value===__pickerTest.state.note && __pickerTest.state.note.includes('alt=\"Δοκιμαστική εικόνα\"')")
 assert ev("fScenarioGetNoteImageInput().type==='file' && fScenarioGetNoteImageInput().accept.includes('.webp')")
 ev("""__pickerTest.input.value='';__pickerTest.state.note='';
 __pickerTest.trigger=document.createElement('button');document.body.appendChild(__pickerTest.trigger);
 fScenarioOpenNoteEditor(__pickerTest.state,__pickerTest.input,function(){},__pickerTest.trigger);
 __pickerTest.modal=document.querySelector('#scNoteEditor .scNoteEditorText');
 fScenarioNoteImagePending={noteInput:__pickerTest.modal,st:__pickerTest.state};
 fScenarioReadNoteImageFile({files:[file],value:''});""")
 until("__pickerTest.modal.value.includes('data:image/png;base64,')")
 assert ev("__pickerTest.input.value===__pickerTest.modal.value && __pickerTest.input.value===__pickerTest.state.note")
 assert ev("document.querySelectorAll('#scNoteEditor [aria-label^=\"Εικόνα από\"]').length===2")
 ev("fScenarioNoteEditorClose();window.prompt=__oldPrompt;__pickerTest.input.remove();__pickerTest.trigger.remove()")
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 # Pilot deliberately enters the existing player; Exit remains the existing library.
 result.update(completed=True,cards=9,lessons=12,molecules=126,viewports=[1500,390],dialogs=3,escapeClosesDialog=True,historyAndRefresh=True,lessonSmoke='Other ketones: entry, Next and existing library Exit',realBrowserFileReader=True,inlineModalSync=True,nativeOSPickerAutomated=False)
 print('PASS React preview:9cards/12links/source parity/dialogs/history/mobile/legacy lessonNextExit/real image FileReader')
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-preview-browser-20261026.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
