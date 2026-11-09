"""Actual Firefox PNG downloads/parity. Downloads stay in the dedicated /tmp profile folder."""
from pathlib import Path
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0].replace('9237','9238')
exec(compile(helper,'existing-viewer-harness-png','exec'))
import struct
folder=Path('/tmp/namelecule-react-png-20261027/downloads');folder.mkdir(exist_ok=True)
result={'completed':False,'checks':[],'cases':[],'parity':[]}
captured={}
source_paths=['react-preview/src/MoleculePreview.jsx','react-preview/public/viewer-host-bridge.js','react-preview/src/preview.css','react-preview/public/viewer-host.html']+[str(p) for p in Path('react-preview/dist').rglob('*') if p.is_file()]
fingerprint={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in source_paths}
legacy_drain=drain
def drain(evaluate):
 wait(evaluate,"nameAnalysisMode==='none' || !numberingFlag || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",25)
 legacy_drain(evaluate)
def form(value):
 if cev("mode2D==='condensedZigZag'?'skeletal':mode2D")!=value:action("document.querySelector('input[name=mode][value="+value+"]').click()")
def symbols(value):
 if ev("document.getElementById('skeletal-symbols').checked")!=value:action("document.getElementById('skeletal-symbols').click()")
def observe_download(evaluate):
 evaluate("window.__pngIntents=[];document.addEventListener('click',e=>{let a=e.target;if(a instanceof HTMLAnchorElement && a.download.endsWith('_2D.png'))__pngIntents.push(a.download)},true)")
def downloaded(before):
 for _ in range(150):
  files=[p for p in folder.glob('*.png') if p.name not in before]
  if len(files)==1:
   data=files[0].read_bytes()
   if data.startswith(b'\x89PNG\r\n\x1a\n') and data.endswith(b'IEND\xaeB`\x82'):return files[0],data
  time.sleep(.1)
 raise AssertionError('No single complete PNG download: '+str([p.name for p in folder.glob('*') if p.name not in before]))
def exported(evaluate,react=True):
 before={p.name for p in folder.glob('*.png')};n=evaluate('window.__pngIntents.length')
 if react:action("document.getElementById('save-2d-png').click()")
 else:evaluate('fSave2DPng()')
 path,data=downloaded(before);assert evaluate('window.__pngIntents.length')==n+1
 name=evaluate('window.__pngIntents.at(-1)');expected=evaluate("(currentMolName||selectedMol||'molecule').replace(/\\s+/g,'_')+'_2D.png'")
 assert name==expected,(name,expected)
 w,h=struct.unpack('!II',data[16:24]);assert w==1200 and h>90
 return {'SHA256':hashlib.sha256(data).hexdigest(),'width':w,'height':h,'filename':name},str(path)
def checkpoint():
 Path('/tmp/namelecule-react-png-20261027/capture.json').write_text(json.dumps({'sourceSHA256':fingerprint,'rows':[[*k,v] for k,v in captured.items()],'result':result},ensure_ascii=False,indent=2))

cases=[]
for mode,sym in [('condensed',False),('expanded',False),('skeletal',False),('skeletal',True)]:
 cases.append(('ethanol',mode,sym,'iupac','base'))
 for ident in ['base','comp0','comp5']:cases.append(('dimethyl_2_3_butane',mode,sym,'iupac',ident))
 for style in ['iupac','common']:
  for ident in ['base','comp1' if style=='iupac' else 'comp10']:cases.append(('ethyl_isopropyl_ether',mode,sym,style,ident))
for mode,sym in [('condensed',False),('skeletal',True)]:
 for ident in ['base','comp0']:cases.append(('isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5',mode,sym,'iupac',ident))
for mode in ['expanded','skeletal']:cases.append(('butanenitrile',mode,False,'iupac','comp9'))
cases.extend([('methanal','condensed',False,'iupac','base'),('methane','condensed',False,'iupac','base')])
try:
 navigate('react-preview/dist/?v=png-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();observe_download(cev)
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{let r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 if '--resume' in sys.argv:
  saved=json.loads(Path('/tmp/namelecule-react-png-20261027/capture.json').read_text())
  assert saved['sourceSHA256']==fingerprint and saved['result']['iframeSize']==result['iframeSize']
  captured={tuple(row[:5]):row[5] for row in saved['rows']};result['cases']=saved['result']['cases']
 for key,mode,sym,style,ident in cases:
  if (key,mode,sym,style,ident) in captured:continue
  pick(key);form(mode)
  if mode=='skeletal':symbols(sym)
  if next(m for m in catalog if m['id']==key)['series']=='ether':naming(style)
  if ident!='base':component(ident)
  # Do not drain first: the adapter itself must wait for native numbering.
  value,path=exported(cev);drain(cev)
  token=(key,mode,sym,style,ident);captured[token]=value
  assert ev("document.querySelector('.molecule-export-status').textContent==='Ζητήθηκε λήψη PNG.'")
  assert ui_analysis()==json.loads(cev(signature))['analysis']
  result['cases'].append({'case':token,'file':path,**value});checkpoint()
  if ident!='base':component(ident)
 print('Actual React PNGs',len(captured),flush=True)
 result['checks'].append('Actual native PNG files downloaded to temporary directory: signature/IEND/1200px/name; three2Dforms/CHn/selected and numbered components/IUPAC-common/Nhighlight/methanal/methane')
 pick('ethanol');form('expanded');form('condensed')
 # Prevent new downloads for all malformed/stale contexts, including 3D.
 def invalid(patch):
  before=len(list(folder.glob('*.png')));count=ev('window.__etherReplies.length')
  ev("(()=>{let d=window.__etherLast;document.querySelector('iframe').contentWindow.postMessage({channel:d.channel,session:d.session,id:d.id+10000,command:'export',value:'png',molecule:d.molecule,mode:d.mode,symbols:d.symbols,naming:d.naming,component:null,..."+json.dumps(patch)+"},location.origin)})()")
  time.sleep(.1);assert len(list(folder.glob('*.png')))==before and ev('window.__etherReplies.length')==count
 for patch in [{'value':'svg'},{'molecule':'methane'},{'mode':'expanded'},{'symbols':'false'},{'naming':'common' if cev('etherNamingMode')=='iupac' else 'iupac'},{'component':'comp12'},{'session':'stale'}]:invalid(patch)
 view('3d');assert ev("document.getElementById('save-2d-png').disabled");invalid({})
 view('2d')
 # Synchronous native error is a nonfatal export failure, never "saved".
 cev("window.__nativeSave=fSave2DPng;fSave2DPng=()=>{throw new Error('controlled export failure')}")
 action("document.getElementById('save-2d-png').click()")
 assert ev("document.querySelector('.molecule-export-status').textContent.includes('δεν ξεκίνησε') && !document.querySelector('iframe').hidden")
 cev('fSave2DPng=__nativeSave')
 # An export waiting for actual sequential numbering is cancelled by newer choice.
 pick('isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5');form('condensed');component('comp5')
 before=len(list(folder.glob('*.png')));ev("document.getElementById('save-2d-png').click()")
 wait(ev,"document.querySelector('.molecule-export-status')?.textContent.includes('Προετοιμασία')")
 pick('ethanol');time.sleep(.4);assert len(list(folder.glob('*.png')))==before
 # Hold native toBlob callback: later model/view commands must remain queued
 # until the old snapshot's correctly named download has been requested.
 cev("window.__toBlob=HTMLCanvasElement.prototype.toBlob;HTMLCanvasElement.prototype.toBlob=function(cb,...args){return __toBlob.call(this,b=>{window.__pendingBlob=()=>cb(b)},...args)}")
 before={p.name for p in folder.glob('*.png')};ev("document.getElementById('save-2d-png').click()")
 wait(cev,"typeof window.__pendingBlob==='function'")
 ev("(()=>{let s=document.getElementById('molecule-select');s.value='methane';s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 time.sleep(.2);assert cev("selectedMol==='ethanol'") and ev("document.getElementById('save-2d-png').disabled")
 cev('HTMLCanvasElement.prototype.toBlob=__toBlob;__pendingBlob();delete window.__pendingBlob')
 path,data=downloaded(before);assert 'αιθανόλη' in __import__('unicodedata').normalize('NFC',path.name)
 wait(ev,'window.__etherAck===window.__etherSent');visible();assert cev("selectedMol==='methane'")
 result['checks'].append('Reject invalid/stale/wrong target/3D export; native sync error remains nonfatal; cancel before snapshot; async native callback holds queue and preserves old filename/content')
 # Genuine native async timeout: stop the host, block a late download, retry.
 pick('ethanol')
 cev("window.__toBlob=HTMLCanvasElement.prototype.toBlob;HTMLCanvasElement.prototype.toBlob=function(cb,...args){return __toBlob.call(this,b=>{window.__pendingBlob=()=>cb(b)},...args)}")
 before={p.name for p in folder.glob('*.png')};started=time.monotonic();ev("document.getElementById('save-2d-png').click()")
 wait(ev,"!!document.querySelector('[role=alert]')",12)
 result['asyncTimeoutSeconds']=round(time.monotonic()-started,2);assert 7.5<result['asyncTimeoutSeconds']<10.5
 assert ev("document.querySelector('[role=alert]').textContent.includes('λήψη PNG')")
 cev('HTMLCanvasElement.prototype.toBlob=__toBlob;__pendingBlob();delete window.__pendingBlob');time.sleep(.4)
 assert {p.name for p in folder.glob('*.png')}==before
 ev("document.querySelector('[role=alert] button').click()");visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();observe_download(cev)
 assert cev("selectedMol==='ethanol' && mode2D==='condensed'")
 result['checks'].append('Actual8s native async timeout gives export-specific retry; late callback download prevented; fresh session default restored')
 before={p.name for p in folder.glob('*.png')};ev("document.getElementById('save-2d-png').focus()")
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]})
 wait(ev,'window.__etherSent>0 && window.__etherAck===window.__etherSent')
 path,data=downloaded(before);assert hashlib.sha256(data).hexdigest()==captured[('ethanol','condensed',False,'iupac','base')]['SHA256']
 result['checks'].append('Native keyboard Enter requests an actual PNG matching the original ethanol capture')

 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.2)
  assert ev('document.documentElement.scrollWidth<=innerWidth')
  screenshot('/tmp/namelecule-react-png-20261027/layout-'+str(width)+'.png')
 result['checks'].append('Desktop/mobile no page overflow; screenshots captured')
 checkpoint()
 # Standalone source exporter at equal dimensions, no adapter implementation.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=png-native-'+str(time.time_ns()));app_ready();wait(ev,'!!window.JSmolReadyFlag')
 css=Path('react-preview/public/viewer-host.html').read_text().split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{let s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.getElementById('nomeclature3D').style.display='none';fResizeViewers()})()")
 observe_download(ev)
 for token,expected in captured.items():
  key,mode,sym,style,ident=token
  ev('selectedMol='+json.dumps(key)+';fSelectMol();fResizeViewers()')
  wait(ev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models?.[0]?.file?.endsWith('/"+key+"_3D.sdf') && allAtomsTypeList3D.length>0");drain(ev)
  ev("$('#radio2DMode .mode2DOption').eq("+str(['condensed','expanded','skeletal'].index(mode))+").trigger('click')")
  if sym:ev("$('#zigzagCheck').trigger('click')")
  if next(m for m in catalog if m['id']==key)['series']=='ether':baseline_name(style)
  if ident!='base':ev("$('#"+ident+"').trigger('click')")
  drain(ev);actual,path=exported(ev,False)
  assert actual==expected,(token,expected,actual)
  result['parity'].append({'case':token,'exactPNG':True,'nativeFile':path});checkpoint()
 print('Native PNG parity',len(result['parity']),flush=True)
 assert len(result['parity'])==len(captured);assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;checkpoint()
 Path('/tmp/namelecule-react-png-20261027/browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'captures':len(captured),'parity':len(result['parity']),'appJSerrors':len(js_errors)}),flush=True)
