"""Actual Firefox ketone checks. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
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
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C')")



lesson=json.loads(Path('scenarios/other-ketones-nomenclature.scenario.json').read_text());keys=lesson['steps'][0]['menuSubset']
names={'penten_1_one_3':'1-πεντεν-3-όνη','pentyn_4_one_2':'4-πεντιν-2-όνη','penten_1_yn_4_one_3':'1-πεντεν-4-ιν-3-όνη','dimethyl_4_5_hexen_5_yn_1_one_3':'4,5-διμεθυλο-5-εξεν-1-ιν-3-όνη','methyl_6_hepten_3_dione_2_5':'6-μεθυλο-3-επτεν-2,5-διόνη','ethyl_3_methyl_4_octen_3_yn_5_dione_2_7':'3-αιθυλο-4-μεθυλο-3-οκτεν-5-ιν-2,7-διόνη','isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5':'4-ισοπροπυλο-3,6-διμεθυλο-3-οκτεν-7-ιν-2,5-διόνη'}
changed=['pentyn_4_one_2','penten_1_yn_4_one_3','ethyl_3_methyl_4_octen_3_yn_5_dione_2_7'];rows=[];completed=False
geometry="""JSON.stringify((()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),r=svg.getBoundingClientRect(),ls=[...svg.querySelectorAll('text')],clipped=[],overlap=[];for(let i=0;i<ls.length;i++){const a=ls[i].getBoundingClientRect();if(a.left<r.left-1||a.right>r.right+1||a.top<r.top-1||a.bottom>r.bottom+1)clipped.push(ls[i].textContent);for(let j=0;j<i;j++){const b=ls[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.5)overlap.push([ls[i].textContent,ls[j].textContent]);}}return {clipped,overlap};})())"""
try:
 navigate('mulermoc-nom-51.html?v=horizontal-ketones-test');app_ready();until('window.JSmolReadyFlag===true')
 for key in keys:
  print('SKELETAL',key,flush=True)
  ev('document.getElementById('+json.dumps(key)+').click()');until('mainChainPool3DKey==='+json.dumps(key))
  for chain in ['algorithmic','data']:
   ev('mode2D="skeletal";mainChainMode='+json.dumps(chain)+';fLoadMol2D();fCalcMainChain3D();nameAnalysisMode="none";fShowNameAnalysis()')
   assert actual_name()==names[key]
   assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
   ev('fClearHighlights();fUpdateSVG()')
   skeletal_clean()
   ev("document.getElementById('comp5').click()")
   until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===mainChainAtomsList.length")
   g=json.loads(ev(geometry));assert not g['clipped']and not g['overlap'],(key,chain,g)
   rows.append(dict(key=key,chainMode=chain,geometry=g,numbered=True))
  ev('nameAnalysisMode="none";fClearHighlights();fUpdateSVG();fShowNameAnalysis()')
  if key in changed:screenshot('/tmp/horizontal-ketones-'+key+'.png')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 for key in changed:
  ev('document.getElementById('+json.dumps(key)+').click()');until('mainChainPool3DKey==='+json.dumps(key))
  ev('mode2D="skeletal";mainChainMode="algorithmic";fLoadMol2D();nameAnalysisMode="none";fShowNameAnalysis()')
  assert actual_name()==names[key]
  g=json.loads(ev(geometry));assert not g['clipped']and not g['overlap'],(key,'390px',g)
  rows.append(dict(key=key,viewport=390,geometry=g))
 assert not js_errors,js_errors
 completed=True
 print('PASS',len(rows),'skeletal browser cases, names/2D3Dnumbering/nooverlap-clipping,0JSerrors')
finally:
 Path('docs/checks/horizontal-ketones-browser-20261026.json').write_text(json.dumps(dict(completed=completed,cases=rows,javascriptErrors=js_errors),ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
