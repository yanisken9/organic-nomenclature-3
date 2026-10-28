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
 navigate('react-preview/dist/?v=3d-controls-smoke-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();observe_download(cev)
 form('skeletal');symbols(True);view('3d')
 action("document.getElementById('hydrogens-3d').click()")
 action("(()=>{let s=document.getElementById('style-3d');s.value='spacefill';s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 view('2d');assert ev("document.getElementById('skeletal-symbols').checked")
 value,path=exported(cev);result['png']={**value,'path':path}
 ev("location.hash='#/library'");wait(ev,"!document.querySelector('iframe')")
 assert ev("document.querySelectorAll('a[href^=\"#/lesson/\"]').length") ==12
 ev("document.querySelector('a[href=\"#/lesson/other-ketones/step/1\"]').click()")
 wait(ev,"!!document.querySelector('.lesson-stage iframe:not([hidden])')",95)
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 assert cev("fScenarioPresent().index===0") and ev("document.getElementById('lesson-position').textContent==='1/28'")
 ev("document.getElementById('lesson-next').click()")
 wait(ev,"document.getElementById('lesson-position').textContent==='2/28' && !!document.querySelector('.lesson-stage iframe:not([hidden])')")
 assert cev('fScenarioPresent().index===1')
 result['checks'].append('Native1200pxPNG download succeeds after3Dstyles/H→2DCHn;12libraryactions; other-ketone lesson1→2 executes')
 result['javascriptErrors']=js_errors;assert not js_errors,js_errors;result['completed']=True
finally:
 Path('/tmp/namelecule-3d-controls-20261027/smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result,ensure_ascii=False),flush=True)
