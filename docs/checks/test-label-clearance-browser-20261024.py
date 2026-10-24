"""Compare old/new rendering in memory; only /tmp artifacts. Requires local Firefox
and task backup /tmp/namelecule-before-label-clearance-20261024 (archival baseline)."""
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
def actual_name():return ev("nameComponentsList.filter(Boolean).join('')")
def skeletal_clean():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")

try:
 navigate('mulermoc-nom-50.html?v=label-clearance-test');app_ready()
 old=Path('/tmp/namelecule-before-label-clearance-20261024/js/mulermoc-nom-molview-50.js').read_text()
 old=old[old.index('function fAddHydrogens2SVG()'):old.index('\nfunction fGetCompactedAtomSkipSet')]
 ev('window.__newHydrogens=fAddHydrogens2SVG;window.__oldHydrogens=('+old+');')
 helper=r"""
 window.__labelSnapshot=()=>{
  const svg=document.querySelector('#jsmeNomeclatureSVG svg');
  const raw=new DOMParser().parseFromString(jsmeNomeclatureApplet.getMolecularAreaGraphicsString(),'image/svg+xml');
  const rt=[...raw.querySelectorAll('text')],rects=[...svg.querySelectorAll('rect')];
  const box=e=>{let b=e.getBBox();return [b.x,b.y,b.width,b.height]};
  const labels=[...svg.querySelectorAll('text.svgAtomLabel[id^=C]')].filter(e=>/^CH[0-4]?$|^C$/.test(e.textContent)).map(e=>{
   const i=Number(e.id.slice(1))-1;return {i,text:e.textContent,x:Number(e.getAttribute('x')),rawX:Number(rt[i]?.getAttribute('x')),box:box(e),plate:rects[i+1]?box(rects[i+1]):null};
  });
  return {name:currentMolName,mode:mode2D,labels,lines:[...svg.querySelectorAll('line')].map(l=>['x1','y1','x2','y2'].map(k=>Number(l.getAttribute(k)))),texts:[...svg.querySelectorAll('text:not([id^=number])')].map(e=>e.textContent)};
 };
 """
 ev(helper);keys=json.loads(ev('JSON.stringify(Object.keys(nameExamples))'));rows=[];changed=[];anchors=0
 for key in keys:
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   ev('selectedMol='+json.dumps(key)+';fInitProps();mode2D='+json.dumps(mode)+';fLoadMol2D()')
   new=json.loads(ev('JSON.stringify(window.__labelSnapshot())'))
   ev('fAddHydrogens2SVG=window.__oldHydrogens;fLoadMol2D()')
   old=json.loads(ev('JSON.stringify(window.__labelSnapshot())'))
   ev('fAddHydrogens2SVG=window.__newHydrogens')
   assert new['name']==old['name'] and new['texts']==old['texts'],(key,mode,'name/text changed')
   assert new['lines']==old['lines'],(key,mode,'bond segment changed')
   if new['mode'] in ['expanded','skeletal']:assert new==old,(key,mode,'unaffected form changed')
   for label in new['labels']:
    assert abs(label['x']-label['rawX'])<.01,(key,mode,label)
    assert all(isinstance(v,(float,int)) for v in label['box']),label
    anchors+=1
   if new['labels']!=old['labels']:changed.append([key,mode])
   rows.append({'key':key,'mode':mode,'name':new['name']})
 print('PASS86x4: names/texts/linegeometry unchanged; expanded/skeletal unchanged;',anchors,'C anchors preserved',flush=True)
 # Symmetric no-H expanded endpoints: two identical double-bond visible lengths.
 ev("selectedMol='butadiene_1_3';fInitProps();mode2D='expanded';fLoadMol2D()")
 ev("window.__lines=[...document.querySelectorAll('#jsmeNomeclatureSVG svg line')];window.__lengths=bondList.flatMap((b,i)=>b[2]===2?[__lines.slice(svgBondList[i]-1,svgBondList[i]+1).map(l=>Math.hypot(l.x2.baseVal.value-l.x1.baseVal.value,l.y2.baseVal.value-l.y1.baseVal.value))]:[])")
 lengths=json.loads(ev('JSON.stringify(window.__lengths)'));assert max(sum(lengths,[]))-min(sum(lengths,[]))<.01,lengths
 for mode in ['condensed','condensedZigZag']:
  ev('mode2D='+json.dumps(mode)+';fLoadMol2D()')
  # Bounds, not forced equal segment lengths: CH2 must consume more space on its H side.
  labels=json.loads(ev('JSON.stringify(window.__labelSnapshot().labels)'))
  assert all(x['plate'][0]<=x['box'][0] and x['plate'][0]+x['plate'][2]>=x['box'][0]+x['box'][2] for x in labels)
  assert any(x['text']=='CH2' for x in labels)
  screenshot('/tmp/label-clearance-butadiene-'+mode+'.png')
 # Highlight/zoom redraws must not reintroduce anchor shifts.
 ev("mode2D='condensed';fLoadMol2D();fShowNameAnalysis();document.getElementById('comp6').click()")
 for zoom in [1,2,3]:
  ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D()')
  snapshot=json.loads(ev('JSON.stringify(window.__labelSnapshot())'))
  assert all(abs(x['x']-x['rawX'])<.01 for x in snapshot['labels'])
 assert not js_errors,js_errors
 evidence={'views':len(rows),'anchorsChecked':anchors,'changedLabelViews':changed,'unchangedNamesTextsSegments':True,'expandedSkeletalUnchanged':True,'zoomAndHighlight':True,'javascriptErrors':js_errors}
 Path('/tmp/label-clearance-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
 print('PASS symmetric expanded C=C, actual H-space retained, plate coverage, highlight/zoom; noJSerrors',flush=True)
finally:call('session.end',{})
