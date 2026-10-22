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
def orientation():
 return json.loads(ev("Jmol.getPropertyAsJSON(jmolAppletNomeclature,'orientationInfo')"))['orientationInfo']
def wait_zoom(z):
 until("Math.abs(JSON.parse(Jmol.getPropertyAsJSON(jmolAppletNomeclature,'orientationInfo')).orientationInfo.zoom-"+str(z)+")<0.05")
def select(key,count,zoom):
 ev("selectedMol='"+key+"';fSelectMol()")
 until("mainChainPool3DKey==='"+key+"' && Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(count))
 wait_zoom(zoom)
 time.sleep(.3)
def radii():
 atoms=json.loads(ev("Jmol.getPropertyAsJSON(jmolAppletNomeclature,'atomInfo')"))['atomInfo']
 return {e:sorted(set(a['spacefill'] for a in atoms if a['sym']==e)) for e in ['C','H']}
large='ethyl_4_dimethyl_3_5_heptyne_1'
evidence={'checks':[], 'screenshots':[]}
try:
 navigate('mulermoc-nom-49.html?v=alkyne-3d-scale-20261022');app_ready()
 until("window.JSmolReadyFlag===true")
 select(large,31,94.4)
 info=orientation()
 import math
 c=math.cos(math.radians(14));sn=math.sin(math.radians(14))
 cx=math.cos(math.radians(95));sx=math.sin(math.radians(95))
 assert all(abs(a-b)<1e-6 for row,expected in zip(info['rotationMatrix'],[[c,-sn*cx,sn*sx],[sn,c*cx,-c*sx],[0,sx,cx]]) for a,b in zip(row,expected)),info
 assert radii()=={'C':[0.408],'H':[0.264]},radii()
 evidence['large']={'zoom':info['zoom'],'modelRadius':info['modelRadius'],'radii':radii()}
 screenshot('design/assets/large-alkyne-3d.png');evidence['screenshots'].append('design/assets/large-alkyne-3d.png')
 evidence['canvas']=json.loads(ev("JSON.stringify([...document.querySelectorAll('canvas')].filter(c=>c.id.includes('jmol')).map(c=>({id:c.id,width:c.width,height:c.height,rect:c.getBoundingClientRect().toJSON()})))"))
 # Framing at a smaller desktop viewport and with only 3D visible.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1});time.sleep(.6)
 wait_zoom(94.4);screenshot('/tmp/large-alkyne-3d-narrow.png')
 ev('fToggleViewer2D()');time.sleep(.6)
 wait_zoom(94.4);screenshot('/tmp/large-alkyne-3d-only.png')
 ev('fToggleViewer2D()');time.sleep(.3)
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});time.sleep(.4)
 evidence['checks'].append('resize and 3D-only visibility preserve initial zoom; screenshots inspected separately')
 # A style change must not reset the camera or physical ball radii.
 ev("fSetMolVis3D('sticks')");time.sleep(.2);wait_zoom(94.4)
 ev("fSetMolVis3D('ballnstick')");time.sleep(.2);wait_zoom(94.4)
 assert radii()=={'C':[0.408],'H':[0.264]}
 ev('fZoom3D(1)');until("JSON.parse(Jmol.getPropertyAsJSON(jmolAppletNomeclature,'orientationInfo')).orientationInfo.zoom>95")
 evidence['manualZoom']=orientation()['zoom']
 ev('fLoadMol3D()');wait_zoom(94.4)
 evidence['checks'].append('initial scale, orientation, physical radii, styles, manual zoom and reload')
 # Existing molecules retain zoom 80 and identical physical sphere radii.
 for key,count in [('ethyl_3_dimethyl_2_5_hexene_2',30),('ethyl_3_dimethyl_2_5_hexane',32),('methyl_4_pentyne_2',16)]:
  select(key,count,80);assert radii()=={'C':[0.408],'H':[0.264]},(key,radii())
  if 'hexene' in key:
   ref=orientation();evidence['reference']={'zoom':ref['zoom'],'modelRadius':ref['modelRadius']}
 evidence['checks'].append('three existing comparison molecules retain default zoom and radii')
 select(large,31,94.4)
 ratio=(evidence['large']['zoom']/evidence['large']['modelRadius'])/(evidence['reference']['zoom']/evidence['reference']['modelRadius'])
 assert abs(ratio-1)<.001,ratio
 evidence['projectedScaleRatio']=ratio
 # Invalid config is ignored; never interpolate a nonnumeric Jmol command.
 for val in ['0','-5','NaN',"'zoom 999'",'Infinity']:
  ev("nameExamples['"+large+"'].initialZoom3D="+val+";fLoadMol3D()")
  wait_zoom(80)
 ev("nameExamples['"+large+"'].initialZoom3D=94.4;fLoadMol3D()")
 wait_zoom(94.4)
 evidence['checks'].append('invalid per-model zoom values fall back to shared default')
 # Apply an actual scenario step with its own camera after the load batch.
 ev("window.__scaleStep=fScenarioCapture();window.__scaleStep.view3D.moveto='moveto 0 {0 0 1 30} 63;';fScenarioApply(window.__scaleStep)")
 wait_zoom(63);time.sleep(.6);wait_zoom(63)
 evidence['checks'].append('scenario per-step camera overrides the model initial zoom')
 assert not js_errors,js_errors
 evidence['jsErrors']=js_errors
 Path('docs/checks/alkyne-3d-scale-20261022.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(evidence,ensure_ascii=False),flush=True)
finally:
 call('session.end',{})
