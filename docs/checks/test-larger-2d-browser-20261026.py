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
 navigate('mulermoc-nom-51.html?v=larger-2d-test');app_ready()
 for width in [1500,900,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.5)
  result=ev("""(()=>{const rows=[];for(const key of Object.keys(window.MOL2D)){for(const mode of ['condensed','expanded','skeletal']){if(!window.MOL2D[key][mode])continue;selectedMol=key;mode2D=mode;nameAnalysisMode='none';numberingFlag=false;molZoom2D=MOL_ZOOM_DEFAULT;fInitNamingProps();fLoadMol2D();const svg=document.querySelector('#jsmeNomeclatureSVG svg');const labels=[...svg.querySelectorAll('text:not([id^=number])')];const atomLabels=labels.filter(e=>/[CHO]/.test(e.textContent));const fonts=atomLabels.map(e=>parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b));const outer=svg.getBoundingClientRect();const clipped=labels.filter(e=>{const b=e.getBoundingClientRect();return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent);const original3D=fShowNumber3D;fShowNumber3D=()=>{};try{numberingFlag=true;currNumberEl=0;fShowNumbering(0)}finally{fShowNumber3D=original3D}const numberClipped=[...svg.querySelectorAll('text[id^=number]')].filter(e=>{const b=e.getBoundingClientRect();return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent);rows.push({key,mode,fonts,target:Number(svg.dataset.uniformAtomFontPixels),clipped,numberClipped,numberCount:svg.querySelectorAll('text[id^=number]').length,viewport:[outer.width,outer.height],name:currentMolName})}}return JSON.stringify(rows)})()""")
  items=json.loads(result);assert len(items)==314
  assert len(set(r['key'] for r in items))==105
  for item in items:
   assert not item['clipped'] and not item['numberClipped'],(width,item)
   assert item['numberCount']>0,(width,item)
   assert all(abs(f-item['target'])<.02 for f in item['fonts']),(width,item)
  allFonts=[f for item in items for f in item['fonts']]
  assert max(allFonts)-min(allFonts)<.02,(width,min(allFonts),max(allFonts))
  rows.extend([dict(width=width,**r) for r in items]);fonts=[f for r in items for f in r['fonts']];print('VIEWPORT',width,'cases',len(items),'fonts',min(fonts),max(fonts),'clipped',sum(bool(r['clipped']) for r in items),flush=True)
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 ev('document.getElementById("ethyl_isopropyl_ether").click()')
 until('window.JSmolReadyFlag===true && mainChainPool3DKey==="ethyl_isopropyl_ether"')
 for i,mode in enumerate(['condensed','expanded','skeletal']):
  ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click()')
  assert ev('mode2D')==mode
  screenshot('/tmp/larger-2d-ether-'+mode+'.png')
 ev('document.querySelectorAll("#radio2DMode .mode2DOption")[1].click()')
 before=ev("parseFloat(getComputedStyle(document.querySelector('#jsmeNomeclatureSVG text')).fontSize)*document.querySelector('#jsmeNomeclatureSVG text').getScreenCTM().a")
 ev('document.getElementById("zoomInBtn").click()')
 after=ev("parseFloat(getComputedStyle(document.querySelector('#jsmeNomeclatureSVG text')).fontSize)*document.querySelector('#jsmeNomeclatureSVG text').getScreenCTM().a")
 assert abs(after/before-1.25)<.01,(before,after)
 ev('document.getElementById("zoomOutBtn").click()')
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click()")
 until('!!window.__png && !!window.__exportSvg')
 assert ev("window.__png.size>1000 && !new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').querySelector('parsererror')")
 print('PASS actual mode radio clicks, zoom in/out and PNG/SVG export',flush=True)
 ev('document.getElementById("isopropyl_4_dimethyl_3_5_heptanol_2").click()')
 until('mainChainPool3DKey==="isopropyl_4_dimethyl_3_5_heptanol_2"')
 for i,mode in enumerate(['condensed','expanded','skeletal']):
  ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click()')
  ev('numberingFlag=true;currNumberEl=0;fShowNumbering(0)')
  screenshot('/tmp/larger-2d-largest-'+mode+'.png')
 assert not js_errors,js_errors
 Path('/tmp/larger-2d-fonts-20261026.json').write_text(json.dumps(dict(cases=rows,javascriptErrors=js_errors),ensure_ascii=False,indent=2))
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
