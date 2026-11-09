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



result={'completed':False,'checks':[],'models':{},'highlights':{}}
preview='react-preview/dist/?v=3d-'+str(time.time_ns())+'#/viewer'
child=None
catalog=json.loads(Path('react-preview/src/molecules.json').read_text())
def cev(expr):
 r=call('script.evaluate',{'expression':expr,'target':{'context':child},'awaitPromise':True})
 if r.get('type')=='exception':raise RuntimeError(r.get('exceptionDetails'))
 return r['result'].get('value')
def wait(evaluate,expr,seconds=15):
 for _ in range(seconds*10):
  if evaluate(expr):return
  time.sleep(.1)
 raise AssertionError('Timed out '+expr)
def visible():
 try:until("!!document.querySelector('.molecule-stage iframe:not([hidden])') && document.querySelector('.molecule-stage').getAttribute('aria-busy')==='false'",16 if child else 95)
 except Exception:
  if child:
   Path('/tmp/react-3d-timeout-diagnostic.json').write_text(json.dumps({'ui':ev('document.querySelector(".molecule-preview").textContent'),'source':cev("JSON.stringify({view:document.documentElement.dataset.view,mol:selectedMol,marker:Jmol.evaluateVar(jmolAppletNomeclature,'reactPreviewRevision'),model:Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo'),shapes:Jmol.getPropertyAsArray(jmolAppletNomeclature,'shapeInfo'),atoms:allAtomsTypeList3D,bonds:bondList3D})")},ensure_ascii=False,indent=2))
  raise
def pick(key):
 ev("(()=>{let x=document.getElementById('molecule-select');x.value="+json.dumps(key)+";x.dispatchEvent(new Event('change',{bubbles:true}))})()")
 visible();assert cev('selectedMol')==key

def view(kind):
 ev("document.querySelector('button[data-view=\""+kind+"\"]').click()")
 visible();assert cev('document.documentElement.dataset.view')==kind

def drain(evaluate):
 # Wait for original progressive numbering, then an actual queued JSmol marker.
 wait(evaluate,"!numberingFlag || nameAnalysisMode!=='compCarbonsCount' || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length")
 token=int(time.time_ns()%1000000000)
 evaluate('Jmol.script(jmolAppletNomeclature,"testQueueMarker = '+str(token)+';")')
 wait(evaluate,"+Jmol.evaluateVar(jmolAppletNomeclature,'testQueueMarker')==="+str(token))

scene="""JSON.stringify((()=>({
 atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').map(a=>({n:a.atomno,s:a.sym,x:a.x,y:a.y,z:a.z,color:a.color,visible:a.visible})),
 bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,'bondInfo','all').map(b=>({a:b.atom1.atomno,b:b.atom2.atomno,order:b.order,colix:b.colix,visible:b.visible})),
 selected:Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.atomno'),
 echoes:Jmol.getPropertyAsArray(jmolAppletNomeclature,'shapeInfo').Echo || [],
 chain:mainChainAtoms3D,
 explanation:document.querySelector('#nameAnalysisExplain .explainText')?.textContent || ''
}))())"""
def snapshot(evaluate):
 data=json.loads(evaluate(scene))
 # Echo pixel boxes depend on viewport; preserve labels and 3D anchors.
 for echo in data['echoes']:
  for val in echo.values():
   if isinstance(val,dict):val.pop('boxXY',None)
 return data
try:
 navigate(preview);visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 frame_src=ev("document.querySelector('iframe').src")
 # Preserve selected 2D mode/zoom while adding the visible 3D view.
 ev("document.querySelector('input[value=expanded]').click()")
 wait(cev,"mode2D==='expanded'")
 ev("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').click()")
 wait(cev,'molZoom2D===2.5')
 view('3d')
 assert ev("document.querySelector('.molecule-controls fieldset').disabled")
 assert cev('molZoom2D')==2.5
 actual={}
 for item in catalog:
  key=item['id'];pick(key);drain(cev)
  model=json.loads(cev("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0])"))
  assert model['file'].endswith('/mols/nomeclature-moc2/'+key+'_3D.sdf'),model
  assert 'error' not in cev("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'shapeInfo'))").lower()
  result['models'][key]=snapshot(cev)
  ids=json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(b=>b.dataset.component))"))
  actual[key]={}
  for ident in ids:
   ev("document.querySelector('[data-component="+ident+"]').click()")
   wait(ev,"document.querySelector('[data-component="+ident+"]').getAttribute('aria-pressed')==='true'")
   drain(cev);actual[key][ident]=snapshot(cev)
   ev("document.querySelector('[data-component="+ident+"]').click()")
   wait(ev,"document.querySelector('[data-component="+ident+"]').getAttribute('aria-pressed')==='false'")
   drain(cev)
  result['highlights'][key]={'components':ids}
  screenshot('/tmp/react-3d-'+key+'-20261026.png')
  print('3D model/highlights',key,flush=True)
 # Rotation is an actual pointer drag in the JSmol child context.
 before=cev("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').rotationMatrix)")
 call('input.performActions',{'context':child,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':350,'y':200},{'type':'pointerDown','button':0},{'type':'pointerMove','x':430,'y':240,'duration':450},{'type':'pointerUp','button':0}]}]})
 wait(cev,"JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').rotationMatrix)!=="+json.dumps(before))
 result['checks'].append('native pointer drag changes 3D rotation')
 z=cev("Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').zoom")
 ev("document.querySelector('.molecule-zoom button[aria-label=Μεγέθυνση]').click()")
 wait(cev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').zoom>"+str(z))
 ev("document.querySelector('.molecule-zoom button[aria-label=Σμίκρυνση]').click()")
 wait(cev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').zoom<"+str(z*1.2))
 assert cev('molZoom2D')==2
 result['checks'].append('3D zoom in/out changes actual camera without 2D zoom')
 view('2d');assert cev('mode2D')=='expanded'
 assert not ev("document.querySelector('.molecule-controls fieldset').disabled")
 view('3d')
 # False model metadata cannot reveal a stale model even if the applet exists.
 cev("window.originalProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){if(p==='modelInfo')return {models:[{file:'wrong-model.sdf'}]};return originalProperty(a,p,...r)}")
 ev("document.querySelector('button[data-view=\"2d\"]').click()")
 time.sleep(.5)
 assert ev("document.querySelector('iframe').hidden && [...document.querySelectorAll('[data-component]')].every(b=>b.disabled)")
 cev('Jmol.getPropertyAsArray=window.originalProperty');visible()
 result['checks'].append('model mismatch hides iframe and disables components until recovery')
 # Rapid A -> B -> A and view toggles use the same frame and latest queued state.
 ev("(()=>{const s=document.querySelector('#molecule-select');for(const value of ['ethanol','propanone','ethanol']){s.value=value;s.dispatchEvent(new Event('change',{bubbles:true}))}for(const view of ['3d','2d','3d'])document.querySelector('button[data-view=\"'+view+'\"]').click()})()")
 visible();assert cev("selectedMol==='ethanol' && document.documentElement.dataset.view==='3d'")
 assert cev("Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0].file.endsWith('/ethanol_3D.sdf')")
 assert ev("document.querySelector('iframe').src")==frame_src
 result['checks'].append('rapid molecule/view changes acknowledge latest model without frame reload')
 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  for item in catalog:
   pick(item['id'])
   wait(cev,"(()=>{const h=document.querySelector('#nomeclature3D'),c=document.querySelector('canvas');return h.clientWidth===c.clientWidth && h.clientHeight===c.clientHeight && c.clientWidth>300})()")
   assert ev('document.documentElement.scrollWidth<=innerWidth')
  screenshot('/tmp/react-3d-layout-'+str(width)+'-20261026.png')
 result['checks'].append('all three 3D canvases match host at desktop/mobile without page overflow')
 # Compare actual legacy highlights, numbers, selected atom serials and colors.
 navigate('mulermoc-nom-51.html?v=3d-reference-'+str(time.time_ns()));app_ready()
 until("!!window.JSmolReadyFlag")
 ev("$('#radio2DMode .mode2DOption').eq(1).trigger('click')")
 for item in catalog:
  key=item['id'];ev('selectedMol='+json.dumps(key)+';fSelectMol()')
  wait(ev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models?.[0]?.file?.endsWith('/"+key+"_3D.sdf') && allAtomsTypeList3D.length==="+str(len(result['models'][key]['atoms'])),40)
  drain(ev)
  for ident,expected in actual[key].items():
   ev("$('#"+ident+"').trigger('click')");drain(ev)
   observed=snapshot(ev)
   if observed!=expected:
    Path('/tmp/react-3d-highlight-mismatch.json').write_text(json.dumps({'molecule':key,'component':ident,'react':expected,'legacy':observed},ensure_ascii=False,indent=2))
   assert observed==expected,(key,ident,'See /tmp/react-3d-highlight-mismatch.json')
   ev("$('#"+ident+"').trigger('click')");drain(ev)
  result['highlights'][key]['exactLegacyParity']=True
  print('3D legacy parity',key,flush=True)
 result['checks'].append('all 11 components: actual 3D atom/bond colors, selection property, numbering echoes, chain and explanation match unchanged legacy app')
 assert not js_errors,js_errors
 result['javascriptErrors']=js_errors;result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-3d-browser-20261026.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'checks':result['checks'],'components':result['highlights'],'javascriptErrors':len(js_errors)},ensure_ascii=False,indent=2),flush=True)
