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



import hashlib
catalog=json.loads(Path('react-preview/src/molecules.json').read_text())
result={'completed':False,'molecules':[],'checks':[],'parity':[]}
source_paths=list(Path('react-preview/src').glob('*'))+[Path('react-preview/public/viewer-host-bridge.js'),Path('react-preview/public/viewer-host.html')]+list(Path('react-preview/dist/assets').glob('*'))
fingerprint={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths if p.is_file()}
resume='--resume' in sys.argv
capture_path=Path('/tmp/react-catalog-capture-20261027.json')
child=None
react_rows={}
def cev(expr):
 r=call('script.evaluate',{'expression':expr,'target':{'context':child},'awaitPromise':True})
 if r.get('type')=='exception':raise RuntimeError(r.get('exceptionDetails'))
 return r['result'].get('value')
def visible():
 until("!!document.querySelector('.molecule-stage iframe:not([hidden])') && document.querySelector('.molecule-stage').getAttribute('aria-busy')==='false'",95 if child is None else 18)
def select(key):
 ev("(()=>{let s=document.getElementById('molecule-select');s.value="+json.dumps(key)+";s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 
 for _ in range(180):
  if cev('selectedMol')==key and ev("window.__catalogAck===window.__catalogSent"):break
  time.sleep(.1)
 else:raise AssertionError('Selection timeout '+key)
 visible();assert cev('selectedMol')==key

def mode(value):
 ev("document.querySelector('input[value="+value+"]').click()")
 
 for _ in range(180):
  if cev('mode2D')==value and ev("window.__catalogAck===window.__catalogSent"):break
  time.sleep(.1)
 else:raise AssertionError('Mode timeout '+value)
 visible();assert cev('mode2D')==value
snapshot=r"""JSON.stringify((()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg');
 const attrs=e=>Object.fromEntries([...e.attributes].filter(a=>!['id','class'].includes(a.name)).map(a=>[a.name,a.value]));
 const analysis={components:[...document.querySelectorAll('#nameAnalysis .nameCompBox:not(.comp-hidden)')].map(e=>({id:e.id,label:e.textContent,selected:e.classList.contains('selected')})),explanation:document.querySelector('#nameAnalysisExplain .explainText')?.textContent||''};
 return {name:currentMolName,common:currentMolCommonName||'',series:nameExamples[selectedMol].classification.seriesKey,chain:mainChainAtomsList,atoms:allAtomsTypeList,bonds:bondList,analysis,
 svg:svg?JSON.stringify({viewBox:svg.getAttribute('viewBox'),nodes:[...svg.querySelectorAll('line,text,tspan,path,polygon,rect')].filter(e=>!e.closest('defs')).map(e=>({tag:e.tagName,attrs:attrs(e),text:['text','tspan'].includes(e.tagName)?e.textContent:null}))}):null};
})())"""
def snap(evaluate):
 value=json.loads(evaluate(snapshot));value['svgSHA256']=hashlib.sha256(value.pop('svg').encode()).hexdigest();return value
def ui_analysis():
 return json.loads(ev("JSON.stringify({components:[...document.querySelectorAll('.react-name-components button')].map(e=>({id:e.dataset.component,label:e.textContent,selected:e.getAttribute('aria-pressed')==='true'})),explanation:document.querySelector('.react-name-explanation').textContent})"))
def input_value(selector,value):
 ev("(()=>{const x=document.querySelector("+json.dumps(selector)+");Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(x,"+json.dumps(value)+");x.dispatchEvent(new Event('input',{bubbles:true}))})()")
 time.sleep(.12)
def series(value):
 ev("(()=>{const x=document.getElementById('molecule-series');x.value="+json.dumps(value)+";x.dispatchEvent(new Event('change',{bubbles:true}))})()")
 time.sleep(.1)
def settle(evaluate):
 for _ in range(80):
  if evaluate("!numberingFlag || nameAnalysisMode!=='compCarbonsCount' || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length"):time.sleep(.05);return
  time.sleep(.1)
 raise AssertionError('Numbering timeout')
try:
 navigate('react-preview/dist/?v=catalog-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 assert cev("selectedMol==='ethanol'")
 ev("window.__catalogAck=0;window.__catalogSent=0;addEventListener('message',e=>{if(e.source===document.querySelector('iframe')?.contentWindow && e.data?.channel==='namelecule-viewer-v4' && e.data.type==='state')window.__catalogAck=e.data.id})")
 cev("addEventListener('message',e=>{if(e.source===parent && e.data?.channel==='namelecule-viewer-v4' && e.data.command)parent.__catalogSent=e.data.id})")
 assert set(json.loads(ev("JSON.stringify([...document.querySelectorAll('#molecule-select option')].map(e=>e.value))")))=={m['id'] for m in catalog}
 assert ev("document.getElementById('molecule-results').textContent.startsWith('126 από 126')")
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{const r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 frame_url=ev("document.querySelector('iframe').src")
 cev("window.__catalogDocument='same'")
 # Filtering never replaces the selected model, even when it has no matches.
 series('ether');assert ev("document.querySelector('#molecule-select optgroup').label.includes('Τρέχον')")
 assert cev("selectedMol==='ethanol'")
 input_value('.molecule-filters input','αιθυλο');assert ev("document.getElementById('molecule-results').textContent.startsWith('4 από 126')"),ev("document.getElementById('molecule-results').textContent")
 input_value('.molecule-filters input','ανυπαρκτομοριο');assert ev("document.getElementById('molecule-results').textContent.includes('Δεν βρέθηκαν')")
 assert ev("document.getElementById('molecule-select').value==='ethanol'")
 ev("document.querySelector('.molecule-filters button').click()")
 assert ev("document.activeElement===document.querySelector('.molecule-filters input')")
 input_value('.molecule-filters input','C2H6O');assert ev("document.getElementById('molecule-results').textContent.startsWith('2 από 126')")
 ev("document.querySelector('.molecule-filters button').click()")
 result['checks'].append('126 distinct IDs; Greek/formula search, combined series filtering, empty state, selected-model retention, clear/focus')
 representatives={}
 if resume:
  saved=json.loads(capture_path.read_text());assert saved['sourceSHA256']==fingerprint
  react_rows={(key,form):row for key,form,row in saved['rows']}
  result=saved['result'];result['resumedAfterHarnessCorrection']=True
  for item in catalog:representatives.setdefault(item['series'],item['id'])
 else:
  for index,item in enumerate(catalog):
   key=item['id'];select(key)
   representatives.setdefault(item['series'],key)
   model=json.loads(cev("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0])"))
   assert model['file'].endswith('/'+key+'_3D.sdf'),(key,model)
   assert ev("document.querySelector('h1').textContent").startswith(item['title']),key
   for form in item['modes']:
    mode(form)
    value=snap(cev)
    assert value['name']==item['title'],(key,item['title'],value['name'])
    assert value['series']==item['series'],key
    assert ui_analysis()==value['analysis'],(key,form)
    react_rows[(key,form)]=value
   if key=='methane':
    assert ev("document.querySelector('input[value=skeletal]').disabled")
   assert ev("document.querySelector('iframe').src")==frame_url
   assert cev("window.__catalogDocument==='same'")
   result['molecules'].append({'id':key,'forms':item['modes'],'actual3DFile':model['file'],'name':value['name'],'analysisComponents':len(value['analysis']['components'])})
   if index%15==0:print('React molecules',index+1,flush=True)
  capture_path.write_text(json.dumps({'sourceSHA256':fingerprint,'rows':[[*k,v] for k,v in react_rows.items()],'result':result},ensure_ascii=False))
 # Switching from skeletal to methane must fall back to condensed without timeout.
 select('ethanol');mode('skeletal');select('methane');assert cev("mode2D==='condensed'")
 result['checks'].append('All126 actual SDF loads, catalog names/classification,377available2Dforms/name components, stable iframe, methane fallback')
 # Exercise one component per series in actual visible 3D, then return to 2D.
 for key in representatives.values():
  select(key);ev("document.querySelector('[data-view=\"3d\"]').click()");visible()
  assert cev("document.documentElement.dataset.view==='3d'")
  assert cev("document.querySelector('#jmolAppletNomeclature_canvas2d').getBoundingClientRect().width>100")
  ev("document.querySelector('.react-name-components button').click()");until("!!document.querySelector('.react-name-components button[aria-pressed=true]')",15);visible()
  assert any(c['selected'] for c in ui_analysis()['components']),key
  ev("document.querySelector('.react-name-components button[aria-pressed=true]').click()");until("!document.querySelector('.react-name-components button[aria-pressed=true]')",15);visible()
  ev("document.querySelector('[data-view=\"2d\"]').click()");visible()
 result['checks'].append('Visible3D/component toggle/2D return for '+str(len(representatives))+'existing series')
 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.3)
  input_value('.molecule-filters input','ισοπροπυλο');series('ketone')
  assert ev('document.documentElement.scrollWidth<=innerWidth'),width
  screenshot('/tmp/react-catalog-'+str(width)+'-20261027.png')
  ev("document.querySelector('.molecule-filters button').click()")
 result['checks'].append('Desktop/mobile filter and selector fit without page overflow')
 # Compare all377exact snapshots against the unmodified standalone main app.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=react-catalog-baseline-'+str(time.time_ns()));app_ready();until('!!window.JSmolReadyFlag')
 css=Path('react-preview/public/viewer-host.html').read_text().split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{const s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.getElementById('nomeclature3D').style.display='none';fResizeViewers()})()")
 time.sleep(.4)
 for item in catalog:
  for form in item['modes']:
   ev("selectedMol="+json.dumps(item['id'])+";fInitProps();mode2D="+json.dumps(form)+";mainChainMode='algorithmic';fLoadMol2D();fResizeViewers();nameAnalysisMode='none';fShowNameAnalysis()")
   time.sleep(.12)
   value=snap(ev)
   original=react_rows[(item['id'],form)]
   if value!=original:
    Path('/tmp/react-catalog-parity-mismatch.json').write_text(json.dumps({'id':item['id'],'form':form,'react':original,'main':value},ensure_ascii=False,indent=2))
   assert value==original,(item['id'],form,'See /tmp/react-catalog-parity-mismatch.json')
   result['parity'].append({'id':item['id'],'form':form,'svgSHA256':value['svgSHA256'],'exact':True})
 result['checks'].append('377exact main/React SVG/name/graph/parent/analysis parity comparisons')
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-catalog-browser-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'molecules':len(result['molecules']),'parity':len(result['parity']),'errors':len(js_errors)}),flush=True)
