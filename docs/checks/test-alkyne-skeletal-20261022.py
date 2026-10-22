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
def clean():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(t=>t.textContent.trim()==='C')")
 assert ev("document.querySelectorAll('#jsmeNomeclatureSVG rect[rx]').length===0")
 assert ev("(()=>{const src=new DOMParser().parseFromString(jsmeNomeclatureApplet.getMolecularAreaGraphicsString(),'text/html');const coords=r=>[...r.querySelectorAll('line')].map(l=>['x1','y1','x2','y2'].map(a=>l.getAttribute(a)).join(','));return JSON.stringify(coords(src))===JSON.stringify(coords(document.querySelector('#jsmeNomeclatureSVG svg')));})()"),'bond geometry changed'
try:
 navigate('mulermoc-nom-49.html?v=alkyne-skeletal-20261022');app_ready()
 until("window.JSmolReadyFlag===true")
 keys=json.loads(ev("JSON.stringify(Object.keys(nameExamples).filter(k=>nameExamples[k].classification.seriesKey==='alkynes'))"))
 assert keys==['propyne','butyne_1','butyne_2','methyl_3_butyne_1','methyl_3_pentyne_1','methyl_4_pentyne_2','ethyl_4_dimethyl_3_5_heptyne_1','ethyne']
 ev("document.querySelector('[data-grouping-mode=series]').click();document.querySelector('[data-group-key=alkynes]').click()")
 # Capture the actual SVG->PNG export pipeline without initiating OS downloads.
 ev("window.__exportSvg=null;window.__png=null;window.__download=null;window.__makeURL=URL.createObjectURL.bind(URL);URL.createObjectURL=function(blob){if(blob.type.startsWith('image/svg'))blob.text().then(s=>window.__exportSvg=s);if(blob.type==='image/png')window.__png=blob;return window.__makeURL(blob);};HTMLAnchorElement.prototype.click=function(){window.__download=this.download;}")
 for key in keys:
  ev("mode2D='skeletal';document.getElementById('"+key+"').click()")
  until("mainChainPool3DKey==='"+key+"'")
  name=ev("nameComponentsList.filter(Boolean).join('')")
  for chain_mode in ['algorithmic','data']:
   ev("mainChainMode='"+chain_mode+"';fLoadMol2D();nameAnalysisMode='none';fShowNameAnalysis()")
   clean()
   for comp in (['comp5','comp6'] if key not in ['methyl_3_butyne_1','methyl_3_pentyne_1','methyl_4_pentyne_2'] else ['comp5','comp6','comp0','comp1','comp4']):
    ev("nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('"+comp+"').click()")
    clean()
    assert ev("document.querySelectorAll('#jsmeNomeclatureSVG polygon[fill=\"rgb(216,238,220)\"],#jsmeNomeclatureSVG ellipse[fill=\"rgb(216,238,220)\"]').length>0"),(key,comp)
    if comp=='comp5':
     ev("clearInterval(myNumberingTimeout);document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').forEach(e=>e.remove());currNumberEl=0;fShowNumbering(0)")
     assert ev("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===mainChainAtomsList.length"),(key,chain_mode)
    assert ev("nameComponentsList.filter(Boolean).join('')")==name
  ev("nameAnalysisMode='none';fShowNameAnalysis();document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();document.getElementById('zigzagCheck').click()")
  assert ev("mode2D==='condensedZigZag' && document.querySelectorAll('#jsmeNomeclatureSVG text').length>=nameExamples[selectedMol].classification.carbonCount"),key
  ev("document.getElementById('zigzagCheck').click()")
  assert ev("mode2D==='skeletal'");clean()
  for i,mode in [(0,'condensed'),(1,'expanded')]:
   ev("document.querySelectorAll('#radio2DMode .mode2DOption')["+str(i)+"].click()")
   assert ev('mode2D')==mode
   assert ev("[...document.querySelectorAll('#jsmeNomeclatureSVG text')].filter(t=>t.textContent.trim().startsWith('C')).length===nameExamples[selectedMol].classification.carbonCount"),key
  ev("document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();nameAnalysisMode='none';fShowNameAnalysis()")
  clean()
  # Zoom redraws and highlight redraws must apply the same post-processing.
  ev("fReapplyZoomScale2D()")
  clean()
  if key=='methyl_3_butyne_1':ev("document.getElementById('comp1').click()")
  screenshot('/tmp/alkyne-skeletal-'+key+'.png')
  ev("window.__exportSvg=null;window.__png=null;window.__download=null;fSave2DPng()")
  until("!!window.__png && !!window.__exportSvg && !!window.__download",20)
  assert ev("! [...new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').querySelectorAll('text')].some(t=>t.textContent.trim()==='C')"),key
  assert ev("window.__png.size>1000 && window.__download.endsWith('_2D.png')"),key
  if key=='butyne_2':
   encoded=ev("new Promise(resolve=>{let r=new FileReader();r.onload=()=>resolve(r.result.split(',')[1]);r.readAsDataURL(window.__png)})")
   Path('/tmp/butyne-2-skeletal-export.png').write_bytes(base64.b64decode(encoded))
  print('PASS',key,': no C/backplates, exact bond geometry, highlights/numbering,CHn/form restoration,redraw,PNG export',flush=True)
 # A guarded display pass must leave other series and heteroatom labels intact.
 ev("window.__labelPass=fHideAlkyneSkeletalCarbons;window.__shapeState=()=>JSON.stringify([...document.querySelectorAll('#jsmeNomeclatureSVG line,#jsmeNomeclatureSVG text')].map(e=>e.outerHTML))")
 for key in ['butene_1','methyl_3_butene_1','ethyl_3_dimethyl_2_5_hexene_2','propanol_1','ethanenitrile','hexen_1_yne_4']:
  ev("selectedMol='"+key+"';mode2D='skeletal';nameAnalysisMode='none';fSelectMol()")
  before=ev('__shapeState()')
  ev("fHideAlkyneSkeletalCarbons=function(){};fUpdateSVG()")
  assert ev('__shapeState()')==before,key
  ev("fHideAlkyneSkeletalCarbons=window.__labelPass")
 assert not js_errors,js_errors
 print('PASS selected alkenes/heteroatoms/enyne exactly unchanged; no JS errors',flush=True)
finally:
 call('session.end',{})
