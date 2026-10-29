"""Actual Firefox three-molecule React bridge checks. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
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


result={'completed':False,'checks':[]}
catalog=json.loads(Path('react-preview/src/molecules.json').read_text())
expected={'ethanol':{'C':2,'H':6,'O':1},'dimethyl_2_3_butane':{'C':6,'H':14},'propanone':{'C':3,'H':6,'O':1}}
preview='react-preview/dist/#/viewer'
child=None

def cev(expr):
 value=call('script.evaluate',{'expression':expr,'target':{'context':child},'awaitPromise':True})
 if value.get('type')=='exception':raise RuntimeError(value.get('exceptionDetails'))
 return value['result'].get('value')
def ready():
 global child
 until("document.querySelector('.molecule-stage')?.getAttribute('aria-busy')==='false' && !!document.querySelector('.molecule-stage iframe:not([hidden])')",95)
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 assert cev("selectedMol==='ethanol' && !!document.querySelector('#jsmeNomeclatureSVG svg text')")
def pick(value):
 ev("(()=>{const x=document.getElementById('molecule-select');x.value="+json.dumps(value)+";x.dispatchEvent(new Event('change',{bubbles:true}))})()")
 until("!document.querySelector('iframe').hidden && document.querySelector('#molecule-select').value==="+json.dumps(value))
 assert cev('selectedMol')==value
 assert ev("document.querySelector('h1').textContent").startswith(next(m['title'] for m in catalog if m['id']==value))
def mode(value):
 ev("document.querySelector('input[value="+value+"]').click()")
 until("document.querySelector('input[value="+value+"]').checked")
 for _ in range(30):
  if cev('mode2D')==value:return
  time.sleep(.1)
 raise AssertionError('Mode not applied')
def zoom(direction):
 old=cev('molZoom2D')
 ev("document.querySelector('.molecule-zoom button[aria-label="+('Μεγέθυνση' if direction>0 else 'Σμίκρυνση')+"]').click()")
 target=min(6,max(.5,old*(1.25 if direction>0 else .8)))
 for _ in range(30):
  if abs(cev('molZoom2D')-target)<1e-8:return target
  time.sleep(.1)
 raise AssertionError('Zoom not applied')
# Canonical renderer output: geometry/text/styles, excluding generated IDs.
signature="""JSON.stringify((()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg');
 const attrs=el=>Object.fromEntries([...el.attributes].filter(a=>!['id','class'].includes(a.name)).map(a=>[a.name,a.value]));
 return {viewBox:svg.getAttribute('viewBox'),elements:[...svg.querySelectorAll('line,text,tspan,path,polygon,rect')].filter(el=>!el.closest('defs')).map(el=>({tag:el.tagName,attrs:attrs(el),text:['text','tspan'].includes(el.tagName)?el.textContent:null}))};
})())"""
def sources(key):return "JSON.stringify(Object.fromEntries(['Condensed','Expanded','Skeletal'].map(m=>[m,nameExamples["+json.dumps(key)+"]['structure2D_'+m]])))"
def shot(name):screenshot('/tmp/react-molecules-'+name+'-20261026.png')
try:
 started=time.monotonic();navigate(preview)
 until("!!document.querySelector('.molecule-status')")
 assert ev("document.querySelector('fieldset').disabled")
 ready();result['readySeconds']=round(time.monotonic()-started,2)
 result['checks'].append('loading disables controls; ready defaults to ethanol')
 assert ev("document.querySelector('#molecule-select').labels[0].textContent==='Μόριο'")
 assert json.loads(ev("JSON.stringify([...document.querySelectorAll('#molecule-select option')].map(x=>x.value))"))==[m['id'] for m in catalog]
 assert cev("document.getElementById('scenarioAuthorTab').getClientRects().length===0")
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{const r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 originalFrame=ev("document.querySelector('iframe').src")
 cev("window.__selectionTestStamp='retained'")
 captured={};raw={};labels={}
 for item in catalog:
  key=item['id'];pick(key);raw[key]=json.loads(cev(sources(key)));captured[key]={}
  for value in ['condensed','expanded','skeletal']:
   mode(value);time.sleep(.25);captured[key][value]=json.loads(cev(signature))
   if value=='expanded':
    visible=json.loads(cev("JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG svg text')].map(t=>t.textContent))"))
    labels[key]=visible;assert sum(t.count('H') for t in visible)==expected[key]['H'],(key,visible)
   shot(key+'-'+value)
  assert ev("document.querySelector('iframe').src")==originalFrame
  assert cev("window.__selectionTestStamp==='retained'")
 result['sourceMOLs']=raw;result['expandedLabels']=labels
 result['checks'].append('three molecules x three modes; displayed H counts6/14/6; same iframe document')
 pick('ethanol')
 mode('expanded');assert zoom(1)==2.5;assert zoom(-1)==2
 for _ in range(10):zoom(1)
 until("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').disabled")
 assert cev('molZoom2D')==6
 for _ in range(20):zoom(-1)
 until("document.querySelector('.molecule-zoom button[aria-label=Σμίκρυνση]').disabled")
 assert cev('molZoom2D')==.5
 result['checks'].append('zoom changes actual renderer and clamps 0.5..6')
 ev("for(const m of ['skeletal','condensed','expanded','skeletal','expanded'])document.querySelector('input[value='+m+']').click()")
 time.sleep(.4);assert cev('mode2D')=='expanded';assert ev("document.querySelector('input[value=expanded]').checked")
 result['checks'].append('rapid mode commands end consistently')
 # Molecule switching retains mode, resets zoom and never reloads iframe.
 mode('expanded');zoom(1);pick('propanone')
 assert cev("mode2D==='expanded' && molZoom2D===2")
 assert ev("document.querySelector('input[value=expanded]').checked")
 ev("""(()=>{const select=document.getElementById('molecule-select');
 for(const [mol,mode] of [['dimethyl_2_3_butane','skeletal'],['ethanol','condensed'],['propanone','expanded'],['ethanol','skeletal']]){
 select.value=mol;select.dispatchEvent(new Event('change',{bubbles:true}));document.querySelector('input[value='+mode+']').click();}
 })()""")
 until("!document.querySelector('iframe').hidden")
 assert cev("selectedMol==='ethanol' && mode2D==='skeletal' && molZoom2D===2")
 assert ev("document.querySelector('input[value=skeletal]').checked")
 assert ev("document.querySelector('iframe').src")==originalFrame
 result['checks'].append('molecule preserves mode/resets zoom; rapid interleaved molecule/mode commands agree without reload')
 # Host command authentication: reject sibling/self, bad token/origin/id/value.
 initial=cev('mode2D')
 ev("""(()=>{const f=document.querySelector('iframe'),session=new URL(f.src).searchParams.get('session');
 for(const d of [{session,id:1100,command:'molecule',value:'methane'},{session,id:1200,command:'molecule',value:'__proto__'},{session:'wrong',id:999,command:'mode',value:'skeletal'},{session,id:1000,command:'mode',value:'bogus'},{session,id:-1,command:'mode',value:'skeletal'}])f.contentWindow.postMessage({channel:'namelecule-viewer-v2',...d},location.origin);
 window.postMessage({channel:'namelecule-viewer-v2',session,type:'failed'},location.origin);
 })()""")
 cev("window.dispatchEvent(new MessageEvent('message',{source:parent,origin:'https://invalid.example',data:{channel:'namelecule-viewer-v2',session:new URLSearchParams(location.search).get('session'),id:2000,command:'mode',value:'skeletal'}}))")
 time.sleep(.2);assert cev('mode2D')==initial;assert ev("!document.querySelector('[role=alert]')")
 result['checks'].append('wrong source/token/origin/mode/id rejected')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 time.sleep(.6)
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 assert cev('document.documentElement.scrollWidth<=innerWidth')
 assert cev("document.querySelector('#jsmeNomeclatureSVG svg').getBoundingClientRect().width>300")
 for item in catalog:
  pick(item['id'])
  for value in ['condensed','expanded','skeletal']:mode(value)
  assert ev('document.documentElement.scrollWidth<=innerWidth')
  shot(item['id']+'-mobile')
 result['checks'].append('390px resize and three modes; no horizontal overflow')
 # Unmount removes the iframe; remount gets a new token and default state.
 first=ev("document.querySelector('iframe').src")
 ev("location.hash='#/library'");until("document.querySelectorAll('article.lesson').length===9")
 assert ev("document.querySelectorAll('a[href*=scenario]').length===12 && !document.querySelector('iframe')")
 ev("location.hash='#/viewer'");ready();second=ev("document.querySelector('iframe').src")
 assert first!=second and cev("mode2D==='condensed' && molZoom2D===2")
 shot('mobile-default')
 result['checks'].append('library 9 cards/12 links; unmount/remount fresh session/defaults')
 # Force a real missing document plus its native error path, then retry.
 ev("document.querySelector('iframe').src='missing-viewer-for-test.html'")
 time.sleep(.2);ev("document.querySelector('iframe').dispatchEvent(new Event('error'))")
 until("!!document.querySelector('[role=alert]')")
 assert ev("document.querySelector('.molecule-stage').getAttribute('aria-busy')==='false'")
 assert ev("document.querySelector('fieldset').disabled && !!document.querySelector('[role=alert] a')")
 ev("document.querySelector('[role=alert] button').click()")
 ready();assert cev("selectedMol==='ethanol'")
 result['checks'].append('missing document/native error UI and retry recovery (error event injected)')
 # Exercise the actual loading deadline without waiting 90 seconds: capture
 # its callback in the browser, then fire it while the real iframe is loading.
 ev("location.hash='#/library'");until("!document.querySelector('iframe')")
 ev("""(()=>{window.__nativeTimer=window.setTimeout;window.__previewDeadline=null;
 window.setTimeout=function(fn,ms,...args){if(ms===90000)window.__previewDeadline=fn;return window.__nativeTimer(fn,ms,...args)}})()""")
 ev("location.hash='#/viewer'");until("typeof window.__previewDeadline==='function'")
 ev("window.__previewDeadline();window.setTimeout=window.__nativeTimer")
 until("!!document.querySelector('[role=alert]')")
 assert ev("document.querySelector('.molecule-stage').getAttribute('aria-busy')==='false'")
 # Valid-looking late ready from the actual frame must not resurrect failure.
 until("!!document.querySelector('iframe').contentDocument?.querySelector('#pageContainer')")
 tree=call('browsingContext.getTree',{'root':ctx});child=tree['contexts'][0]['children'][0]['context']
 cev("parent.postMessage({channel:'namelecule-viewer-v2',session:new URLSearchParams(location.search).get('session'),type:'ready',mode:'condensed',zoom:2,molecule:'ethanol'},location.origin)")
 time.sleep(.2);assert ev("!!document.querySelector('[role=alert]')")
 ev("document.querySelector('[role=alert] button').click()")
 ready()
 result['checks'].append('loading deadline and terminal failure reject late ready; retry succeeds (deadline callback fired by test)')
 # Leaving while a fresh iframe loads must remove it and its listeners/timers.
 ev("location.hash='#/library'");until("!document.querySelector('iframe')")
 ev("location.hash='#/viewer'");until("!!document.querySelector('iframe')")
 ev("location.hash='#/library'");until("!document.querySelector('iframe')")
 time.sleep(.2);assert ev("document.querySelectorAll('article.lesson').length===9 && !document.querySelector('[role=alert]')")
 ev("location.hash='#/viewer'");ready()
 result['checks'].append('unmount during loading and remount recover without stale error')
 # Exercise the actual 10-second command deadline while selecting a molecule.
 # Drop only state acknowledgements, retaining a real loaded/rendering host.
 ev("""(()=>{window.__nativePost=window.postMessage;window.__lastAck=null;
 window.postMessage=function(data,...rest){if(data?.channel==='namelecule-viewer-v2'&&data.type==='state'){window.__lastAck=data;return;}return window.__nativePost.call(this,data,...rest)}})()""")
 ev("(()=>{const s=document.getElementById('molecule-select');s.value='propanone';s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 until("!!window.__lastAck")
 assert ev("document.querySelector('iframe').hidden && document.querySelector('.molecule-stage').getAttribute('aria-busy')==='true'")
 assert cev("selectedMol==='propanone'")
 # A matching request ID with the wrong molecule must not expose the old graph.
 cev("parent.__nativePost.call(parent,{...parent.__lastAck,molecule:'ethanol'},location.origin)")
 time.sleep(.2);assert ev("document.querySelector('iframe').hidden")
 until("!!document.querySelector('[role=alert]')",12)
 assert ev("document.querySelector('.molecule-stage').getAttribute('aria-busy')==='false' && document.getElementById('molecule-select').disabled")
 ev("window.postMessage=window.__nativePost")
 cev("parent.postMessage(parent.__lastAck,location.origin)")
 time.sleep(.2);assert ev("!!document.querySelector('[role=alert]')")
 ev("document.querySelector('[role=alert] button').click()")
 ready()
 result['checks'].append('molecule ack withheld: pending graph hidden, wrong-molecule reply rejected, real10s deadline, late ack ignored, retry defaults restored')
 # Compare to the unmodified legacy app at exactly the host viewport and layout.
 legacy=call('browsingContext.create',{'type':'tab'})['context']
 oldctx=ctx;ctx=legacy
 call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-51.html')
 until("typeof jsmeNomeclatureApplet!=='undefined' && !!jsmeNomeclatureApplet && !!nameExamples.ethanol.classification && window.JSmolReadyFlag")
 host=Path('react-preview/public/viewer-host.html').read_text();css=host.split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{const s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.getElementById('nomeclature3D').style.display='none'})()")
 parity={}
 for item in catalog:
  key=item['id'];assert json.loads(ev(sources(key)))==raw[key]
  ev("selectedMol="+json.dumps(key)+";fSelectMol();fResizeViewers()")
  parity[key]={}
  for i,value in enumerate(['condensed','expanded','skeletal']):
   ev("$('#radio2DMode .mode2DOption').eq("+str(i)+").trigger('click')");time.sleep(.3)
   actual=json.loads(ev(signature));parity[key][value]=actual==captured[key][value]
   if not parity[key][value]:
    Path('/tmp/react-molecules-parity-'+key+'-'+value+'.json').write_text(json.dumps({'host':captured[key][value],'original':actual},ensure_ascii=False,indent=2))
 assert all(all(v.values()) for v in parity.values()),parity
 result['exactSVGParity']=parity
 result['checks'].append('all nine raw MOLs and exact SVG geometry/text/styles match unchanged renderer at same viewport')
 call('browsingContext.close',{'context':ctx});ctx=oldctx
 result['resources']=json.loads(cev("JSON.stringify(performance.getEntriesByType('resource').map(r=>({name:r.name,duration:Math.round(r.duration)})))"))
 result['completed']=True
except Exception as error:
 result['failure']=repr(error)
 raise
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-molecules-browser-20261026.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({k:v for k,v in result.items() if k not in ['resources','sourceMOLs']},ensure_ascii=False,indent=2))
