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



helper="\nwindow.__checkDieneParallels=(svg=document.querySelector('#jsmeNomeclatureSVG svg'))=>{\n const lines=svg.querySelectorAll('line');\n return bondList.every((bond,b)=>{\n  if(bond[2]!==2)return true;\n  const pair=[lines[svgBondList[b]-1],lines[svgBondList[b]]];if(pair.some(l=>!l))return false;\n  const p=pair.map(l=>['x1','y1','x2','y2'].map(k=>Number(l.getAttribute(k))));\n  const u=[p[0][2]-p[0][0],p[0][3]-p[0][1]],v=[p[1][2]-p[1][0],p[1][3]-p[1][1]];\n  const n=Math.hypot(...u)*Math.hypot(...v);if(n<1)return false;\n  return Math.abs(u[0]*v[1]-u[1]*v[0])/n<.002 &&\n   Math.abs(u[0]*(p[1][1]-p[0][1])-u[1]*(p[1][0]-p[0][0]))/Math.hypot(...u)>.1;\n });\n};\n"
rows=[]
expected={'butadiene_1_3':('1,3-βουταδιένιο',10),'butadiene_1_2':('1,2-βουταδιένιο',10),'pentadiene_1_4':('1,4-πενταδιένιο',13),'methyl_3_pentadiene_1_3':('3-μεθυλο-1,3-πενταδιένιο',16),'dimethyl_2_3_pentadiene_1_3':('2,3-διμεθυλο-1,3-πενταδιένιο',19),'ethyl_3_dimethyl_4_5_hexadiene_1_4':('3-αιθυλο-4,5-διμεθυλο-1,4-εξαδιένιο',28),'ethyl_3_methyl_4_hexen_3_yn_5_ol_2':('3-αιθυλο-4-μεθυλο-3-εξεν-5-ιν-2-όλη',24)}
try:
 navigate('mulermoc-nom-50.html?v=mol-only-test')
 app_ready();until('window.JSmolReadyFlag===true')
 assert ev("typeof fDrawDieneParallelDoubleBonds==='undefined'")
 ev(helper)
 for key,(name,atoms) in expected.items():
  ev('document.getElementById('+json.dumps(key)+').click()')
  until('selectedMol==='+json.dumps(key)+' && mainChainPool3DKey==='+json.dumps(key))
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(atoms))
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   for chain in ['algorithmic','data']:
    ev('mode2D='+json.dumps(mode)+';mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();nameAnalysisMode="none";fShowNameAnalysis()')
    assert ev('currentMolName')==name,(key,mode,chain,ev('currentMolName'))
    assert ev('window.__checkDieneParallels()'),(key,mode,chain,'double not parallel')
    assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)'),(key,mode,chain,'2D3Dparent')
    for comp in ['comp5','comp6']+(['comp1'] if key.startswith(('methyl','dimethyl','ethyl')) else []):
     ev('document.getElementById('+json.dumps(comp)+').click()')
     assert ev('window.__checkDieneParallels()'),(key,mode,comp)
    rows.append({'molecule':key,'mode':mode,'chainMode':chain,'name':name,'parallelAfterHighlights':True,'parent2D3DMatch':True})
   if key in ['dimethyl_2_3_pentadiene_1_3','ethyl_3_methyl_4_hexen_3_yn_5_ol_2'] and mode!='condensedZigZag':screenshot('/tmp/mol-files-only-'+key+'-'+mode+'.png')
 # Processed SVG export must retain the native parallel lines.
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};fSave2DPng()")
 until('!!window.__png && !!window.__exportSvg')
 assert ev("window.__png.size>1000 && window.__checkDieneParallels(new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').documentElement)")
 assert not js_errors,js_errors
 Path('/tmp/mol-files-only-browser-final.json').write_text(json.dumps({'cases':rows,'PNGBlobAndExportSVG':True,'javascriptErrors':js_errors},ensure_ascii=False,indent=2))
 print('PASS',len(rows),'cases, native parallel doubles/highlights/2D3D/name/PNG export, zero JSerrors')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
