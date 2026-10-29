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
ethers=[m for m in catalog if m['series']=='ether'];assert len(ethers)==11
result={'completed':False,'checks':[],'cases':[],'parity':[]}
child=None;captured={}
resume='--resume' in sys.argv
capture_path=Path('/tmp/react-ether-naming-capture-20261027.json')
paths=[Path(p) for p in ['react-preview/src/MoleculePreview.jsx','react-preview/src/NameAnalysis.jsx','react-preview/src/preview.css','react-preview/public/viewer-host-bridge.js','react-preview/public/viewer-host.html']]+list(Path('react-preview/dist/assets').glob('*'))
fingerprint={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
def cev(expr):
 r=call('script.evaluate',{'expression':expr,'target':{'context':child},'awaitPromise':True})
 if r.get('type')=='exception':raise RuntimeError(r.get('exceptionDetails'))
 return r['result'].get('value')
def wait(evaluate,expr,seconds=18):
 for _ in range(seconds*10):
  if evaluate(expr):return
  time.sleep(.1)
 raise AssertionError('Timed out: '+expr)
def visible():
 wait(ev,"!!document.querySelector('.molecule-stage iframe:not([hidden])') && document.querySelector('.molecule-stage').getAttribute('aria-busy')==='false'",95 if child is None else 18)
def observe():
 ev("window.__etherAck=0;window.__etherSent=0;window.__etherReplies=[];addEventListener('message',e=>{if(e.source===document.querySelector('iframe')?.contentWindow && e.data?.channel==='namelecule-viewer-v4' && e.data.type==='state'){window.__etherAck=e.data.id;window.__etherLast=e.data;window.__etherReplies.push(e.data.id)}})")
 cev("addEventListener('message',e=>{if(e.source===parent && e.data?.channel==='namelecule-viewer-v4' && e.data.command)parent.__etherSent=e.data.id})")
def action(expr):
 before=ev('window.__etherAck');ev(expr)
 wait(ev,'window.__etherSent>'+str(before)+' && window.__etherAck===window.__etherSent');visible()
def pick(key):
 if cev('selectedMol')==key:return
 action("(()=>{let s=document.getElementById('molecule-select');s.value="+json.dumps(key)+";s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 assert cev('selectedMol')==key
 assert bool(ev("!!document.querySelector('.react-ether-naming')"))==(next(m for m in catalog if m['id']==key)['series']=='ether')
def form(value):
 if cev('mode2D')!=value:action("document.querySelector('input[name=mode][value="+value+"]').click()")
def naming(value):
 if not ev("document.querySelector('input[name=ether-naming][value="+value+"]').checked"):
  action("document.querySelector('input[name=ether-naming][value="+value+"]').click()")
 assert cev('etherNamingMode')==value
def view(value):
 if cev('document.documentElement.dataset.view')!=value:action("document.querySelector('[data-view=\""+value+"\"]').click()")
def component(ident):action("document.querySelector('[data-component="+ident+"]').click()")
def drain(evaluate):
 wait(evaluate,"!numberingFlag || nameAnalysisMode!=='compCarbonsCount' || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",25)
 token=int(time.time_ns()%1000000000);evaluate('Jmol.script(jmolAppletNomeclature,"etherTestMarker = '+str(token)+';")')
 wait(evaluate,"+Jmol.evaluateVar(jmolAppletNomeclature,'etherTestMarker')==="+str(token))
signature=r"""JSON.stringify((()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg');
 const analysis={components:[...document.querySelectorAll('#nameAnalysis .nameCompBox:not(.comp-hidden)')].map(e=>({id:e.id,label:e.textContent,selected:e.classList.contains('selected')})),explanation:document.querySelector('#nameAnalysisExplain .explainText')?.textContent||''};
 return {analysis,naming:etherNamingMode,name:currentMolName,common:currentMolCommonName||'',chain:mainChainAtomsList,
 svg:svg?JSON.stringify({viewBox:svg.getAttribute('viewBox'),nodes:[...svg.querySelectorAll('line,text,tspan,path,polygon,rect')].filter(e=>!e.closest('defs')).map(e=>({tag:e.tagName,attrs:Object.fromEntries([...e.attributes].filter(a=>!['id','class'].includes(a.name)).map(a=>[a.name,a.value])),text:['text','tspan'].includes(e.tagName)?e.textContent:null}))}):null};
})())"""
scene=r"""JSON.stringify((()=>({atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').map(a=>({n:a.atomno,s:a.sym,x:a.x,y:a.y,z:a.z,color:a.color,visible:a.visible})),bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,'bondInfo','all').map(b=>({a:b.atom1.atomno,b:b.atom2.atomno,order:b.order,colix:b.colix,visible:b.visible})),selected:Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.atomno'),echoes:Jmol.getPropertyAsArray(jmolAppletNomeclature,'shapeInfo').Echo||[],chain:mainChainAtoms3D,explanation:document.querySelector('#nameAnalysisExplain .explainText')?.textContent||''}))())"""
def snap(evaluate,kind):
 drain(evaluate)
 if kind=='3d':
  value=json.loads(evaluate(scene))
  for echo in value['echoes']:
   for v in echo.values():
    if isinstance(v,dict):v.pop('boxXY',None)
  return value
 value=json.loads(evaluate(signature));value['svgSHA256']=hashlib.sha256(value.pop('svg').encode()).hexdigest();return value
def ui_analysis():return json.loads(ev("JSON.stringify({components:[...document.querySelectorAll('.react-name-components button')].map(e=>({id:e.dataset.component,label:e.textContent,selected:e.getAttribute('aria-pressed')==='true'})),explanation:document.querySelector('.react-name-explanation').textContent})"))
def store(key,mode,style,ident,kind):
 value=snap(cev,kind);assert ui_analysis()==json.loads(cev(signature))['analysis'],(key,mode,style,ident)
 token=(key,mode,style,ident,kind);captured[token]=value
 result['cases'].append({'molecule':key,'form':mode,'naming':style,'component':ident,'view':kind})
def baseline_name(style):ev("$('#radioEtherNaming .etherNamingRadio[data-naming-mode="+style+"]').trigger('click')")
def mismatch(token,actual):
 if captured[token]!=actual:
  Path('/tmp/react-ether-naming-mismatch-20261027.json').write_text(json.dumps({'case':token,'react':captured[token],'main':actual},ensure_ascii=False,indent=2))
 assert captured[token]==actual,(token,'see /tmp/react-ether-naming-mismatch-20261027.json')
 result['parity'].append({'case':token,'exact':True})
try:
 navigate('react-preview/dist/?v=ether-naming-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 assert not ev("!!document.querySelector('.react-ether-naming')")
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{const r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 original_src=ev("document.querySelector('iframe').src")
 if resume:
  saved=json.loads(capture_path.read_text());assert saved['sourceSHA256']==fingerprint
  assert result['iframeSize']==saved['result']['iframeSize']
  captured={tuple(row[:5]):row[5] for row in saved['rows']}
  assert len({key[0] for key in captured})==11
  result['cases']=saved['result']['cases']
  result['resumedCapture']=True
 else:
  for item in ethers:
   key=item['id'];pick(key)
   for mode in ('condensed','expanded','skeletal'):
    form(mode)
    for style in ('iupac','common'):
     naming(style);store(key,mode,style,'base','2d')
     ids=json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))"))
     for ident in ids:
      component(ident);assert any(c['id']==ident and c['selected'] for c in ui_analysis()['components'])
      store(key,mode,style,ident,'2d');component(ident)
   form('expanded');view('3d')
   for style in ('iupac','common'):
    naming(style);store(key,'expanded',style,'base','3d')
    for ident in json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))")):
     component(ident);store(key,'expanded',style,ident,'3d');component(ident)
   view('2d');assert ev("document.querySelector('iframe').src")==original_src
   print('Ether naming capture',key,flush=True)
 capture_path.write_text(json.dumps({'sourceSHA256':fingerprint,'result':result,'rows':[[*k,v] for k,v in captured.items()]},ensure_ascii=False))
 pick(ethers[0]['id']);naming('common')
 result['checks'].append('All11ethers/both variants/all3forms/components/visible3D; React analysis matches legacy; same iframe')
 pick('ethanol');assert not ev("!!document.querySelector('.react-ether-naming')")
 pick(ethers[0]['id']);assert ev("document.querySelector('input[name=ether-naming][value=common]').checked")
 naming('iupac')
 ev("document.querySelector('input[name=ether-naming][value=common]').focus()");before=ev('window.__etherSent')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':' '},{'type':'keyUp','value':' '}]}]})
 wait(ev,'window.__etherSent>'+str(before)+' && window.__etherAck===window.__etherSent');assert cev("etherNamingMode==='common'")
 result['checks'].append('Ether preference persists through non-ethers, conditional radios, native keyboard Space')
 before=ui_analysis()
 ev("(()=>{const d=structuredClone(window.__etherLast);d.naming='iupac';d.analysis.components[0].label='FAKE';dispatchEvent(new MessageEvent('message',{origin:location.origin,source:document.querySelector('iframe').contentWindow,data:d}))})()")
 time.sleep(.15);assert ui_analysis()==before
 count=ev('window.__etherReplies.length')
 ev("(()=>{const d=window.__etherLast;for(const patch of [{value:'invalid'},{molecule:'ethanol'},{session:'stale'}])document.querySelector('iframe').contentWindow.postMessage({...d,type:undefined,id:d.id+100000,command:'naming',value:'iupac',...patch},location.origin)})()")
 time.sleep(.2);assert ev('window.__etherReplies.length')==count;assert cev("etherNamingMode==='common'")
 naming('iupac');pick('ethanol');count=ev('window.__etherReplies.length')
 ev("(()=>{const d=window.__etherLast;document.querySelector('iframe').contentWindow.postMessage({...d,type:undefined,id:d.id+100000,command:'naming',value:'common'},location.origin)})()")
 time.sleep(.2);assert ev('window.__etherReplies.length')==count;pick(ethers[0]['id'])
 cev("window.__savedModelProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:__savedModelProperty(a,p,...r)}")
 ev("document.querySelector('input[name=ether-naming][value=common]').click()")
 wait(ev,"document.querySelector('.molecule-stage').getAttribute('aria-busy')==='true'")
 assert ev("document.querySelector('.react-ether-naming').disabled && [...document.querySelectorAll('.molecule-zoom button')].every(b=>b.disabled) && document.querySelector('iframe').hidden && !document.querySelector('[data-component]')")
 cev("Jmol.getPropertyAsArray=window.__savedModelProperty");visible();assert cev("etherNamingMode==='common'")
 result['checks'].append('Reject wrong naming ACK/invalid/stale/wrong-molecule/non-ether commands; naming pending gate hides old graph/components and disables radios/zoom; recovers')
 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.3)
  assert ev('document.documentElement.scrollWidth<=innerWidth')
  screenshot('/tmp/react-ether-naming-'+str(width)+'-20261027.png')
 result['checks'].append('Desktop/mobile panel fit; screenshots retained')
 Path('/tmp/react-ether-naming-capture-20261027.json').write_text(json.dumps({'sourceSHA256':fingerprint,'result':result,'rows':[[*k,v] for k,v in captured.items()]},ensure_ascii=False))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=ether-naming-baseline-'+str(time.time_ns()));app_ready();wait(ev,'!!window.JSmolReadyFlag')
 css=Path('react-preview/public/viewer-host.html').read_text().split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{const s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.getElementById('nomeclature3D').style.display='none';fResizeViewers()})()");time.sleep(.4)
 for item in ethers:
  key=item['id'];ev('selectedMol='+json.dumps(key)+';fSelectMol();fResizeViewers()')
  wait(ev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models?.[0]?.file?.endsWith('/"+key+"_3D.sdf') && allAtomsTypeList3D.length>0");drain(ev)
  for mode in ('condensed','expanded','skeletal'):
   ev("$('#radio2DMode .mode2DOption').eq("+str(['condensed','expanded','skeletal'].index(mode))+").trigger('click')");time.sleep(.15)
   for style in ('iupac','common'):
    baseline_name(style);mismatch((key,mode,style,'base','2d'),snap(ev,'2d'))
    ids=[t[3] for t in captured if t[:3]==(key,mode,style) and t[4]=='2d' and t[3]!='base']
    for ident in ids:
     ev("$('#"+ident+"').trigger('click')");mismatch((key,mode,style,ident,'2d'),snap(ev,'2d'));ev("$('#"+ident+"').trigger('click')")
  ev("$('#radio2DMode .mode2DOption').eq(1).trigger('click')")
  for style in ('iupac','common'):
   baseline_name(style);mismatch((key,'expanded',style,'base','3d'),snap(ev,'3d'))
   ids=[t[3] for t in captured if t[:3]==(key,'expanded',style) and t[4]=='3d' and t[3]!='base']
   for ident in ids:
    ev("$('#"+ident+"').trigger('click')");mismatch((key,'expanded',style,ident,'3d'),snap(ev,'3d'));ev("$('#"+ident+"').trigger('click')")
  print('Main naming parity',key,flush=True)
 result['checks'].append('All captured2D/3Dbase/active states exactly match unchanged main52')
 assert len(result['cases'])==len(result['parity']);assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 if captured:capture_path.write_text(json.dumps({'sourceSHA256':fingerprint,'result':result,'rows':[[*k,v] for k,v in captured.items()]},ensure_ascii=False))
 Path('/tmp/react-ether-naming-browser-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'parity':len(result['parity']),'javascriptErrors':len(js_errors)}),flush=True)
