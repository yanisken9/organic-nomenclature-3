"""Actual Firefox CHn parity and transitions; only test artifacts are written."""
from pathlib import Path
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'existing-viewer-harness','exec'))
result={'completed':False,'checks':[],'cases':[],'parity':[]}
captured={}
source_paths=['react-preview/src/MoleculePreview.jsx','react-preview/src/NameAnalysis.jsx','react-preview/src/RulePanels.jsx','react-preview/src/rule-data.js','react-preview/src/rule-schema.json','react-preview/src/preview.css','react-preview/public/viewer-host-bridge.js','react-preview/public/viewer-host.html']+[str(p) for p in Path('react-preview/dist').rglob('*') if p.is_file()]
fingerprint={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in source_paths}
# The legacy engine names annotated skeletal mode condensedZigZag, while the
# React radio deliberately remains skeletal. Avoid clicking an already-checked
# radio and waiting for a change event which browsers do not dispatch.
def form(value):
 actual=cev("mode2D==='condensedZigZag'?'skeletal':mode2D")
 if actual!=value:action("document.querySelector('input[name=mode][value="+value+"]').click()")

legacy_drain=drain
def drain(evaluate):
 # Ketone locant components also use sequential numbering, not only comp5.
 wait(evaluate,"nameAnalysisMode==='none' || !numberingFlag || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",25)
 legacy_drain(evaluate)

def symbols(value):
 if ev("document.getElementById('skeletal-symbols').checked")!=value:
  action("document.getElementById('skeletal-symbols').click()")
 assert cev("mode2D==='condensedZigZag'")==value
 assert ev("document.getElementById('skeletal-symbols').checked")==value
 assert ev("document.querySelector('input[name=mode][value=skeletal]').checked")
def capture(key,value,ident):
 token=(key,value,ident)
 if token not in captured:result['cases'].append({'molecule':key,'symbols':value,'component':ident})
 captured[token]=snap(cev,'2d')
 assert ui_analysis()==json.loads(cev(signature))['analysis']

def source_symbol(value):
 if ev("mode2D==='condensedZigZag'")!=value:ev("$('#zigzagCheck').trigger('click')")
def checkpoint():
 Path('/tmp/react-symbols-capture-20261027.json').write_text(json.dumps({'sourceSHA256':fingerprint,'result':result,'rows':[[*key,value] for key,value in captured.items()]},ensure_ascii=False))
def invalid_commands(patches):
 before=ev('window.__etherReplies.length')
 for patch in patches:
  ev("(()=>{let d=window.__etherLast;document.querySelector('iframe').contentWindow.postMessage({channel:d.channel,session:d.session,id:d.id+100000,command:'symbols',value:true,molecule:d.molecule,..."+json.dumps(patch)+"},location.origin)})()")
 time.sleep(.15);assert ev('window.__etherReplies.length')==before
try:
 navigate('react-preview/dist/?v=symbols-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 assert ev("document.getElementById('skeletal-symbols').matches(':disabled') && !document.getElementById('skeletal-symbols').checked")
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{const r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 representatives=[next(m['id'] for m in reversed(catalog) if m['series']==series) for series in dict.fromkeys(m['series'] for m in catalog)]
 if '--resume' in sys.argv:
  saved=json.loads(Path('/tmp/react-symbols-capture-20261027.json').read_text())
  assert saved['sourceSHA256']==fingerprint and saved['result']['iframeSize']==result['iframeSize']
  captured={tuple(row[:3]):row[3] for row in saved['rows']}
  result['cases']=saved['result']['cases']
 for key in representatives:
  if all((key,value,ident) in captured for value in (False,True) for ident in ('base','comp5')):continue
  pick(key);form('skeletal');symbols(False);capture(key,False,'base')
  symbols(True);capture(key,True,'base')
  component('comp5');capture(key,True,'comp5')
  symbols(False);capture(key,False,'comp5');component('comp5')
  checkpoint();print('CHn capture',key,flush=True)
 # Rich highlights on branched and multiply bonded structures; original
 # rule panels and selected components are retained across symbol changes.
 for key in ['dimethyl_2_3_butane','ethyl_isopropyl_ether','isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5']:
  pick(key);form('skeletal');symbols(True)
  for ident in json.loads(ev("JSON.stringify([...document.querySelectorAll('[data-component]')].map(e=>e.dataset.component))")):
   component(ident);capture(key,True,ident);component(ident)
  checkpoint()
 result['checks'].append('19series base and numbered-chain states with CHn on/off; all visible components on3branched representatives; React analysis agrees with engine')
 pick('dimethyl_2_3_butane');symbols(True);component('comp5')
 ev("document.querySelector('.react-rule-toggle').click()")
 symbols(False);assert ev("!document.querySelector('.react-rule-body').hidden && document.querySelector('[data-component=comp5]').getAttribute('aria-pressed')==='true'")
 # Native keyboard checkbox and preserved 3D graph/coordinates.
 before_scene=json.loads(cev(scene));before_atoms=[{k:a[k] for k in ['n','s','x','y','z']} for a in before_scene['atoms']]
 ev("document.getElementById('skeletal-symbols').focus()")
 before=ev('window.__etherAck')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':' '},{'type':'keyUp','value':' '}]}]})
 wait(ev,'window.__etherSent>'+str(before)+' && window.__etherAck===window.__etherSent');visible()
 assert cev("mode2D==='condensedZigZag'")
 after_scene=json.loads(cev(scene));assert before_atoms==[{k:a[k] for k in ['n','s','x','y','z']} for a in after_scene['atoms']]
 view('3d');assert ev("document.getElementById('skeletal-symbols').matches(':disabled') && document.getElementById('skeletal-symbols').checked")
 before=ev('window.__etherSent');ev("document.getElementById('skeletal-symbols').click()");assert ev('window.__etherSent')==before
 view('2d');assert not ev("document.getElementById('skeletal-symbols').matches(':disabled')")
 pick('ethyl_isopropyl_ether');assert ev("document.getElementById('skeletal-symbols').checked");naming('common');assert ev("document.getElementById('skeletal-symbols').checked")
 naming('iupac');form('expanded');assert ev("document.getElementById('skeletal-symbols').matches(':disabled') && !document.getElementById('skeletal-symbols').checked")
 form('condensed');assert ev("document.getElementById('skeletal-symbols').matches(':disabled')")
 invalid_commands([{}, {'value':'true'}, {'molecule':'methane'}, {'session':'stale'}])
 form('skeletal');symbols(True);pick('methane')
 assert cev("mode2D==='condensed'") and ev("document.getElementById('skeletal-symbols').matches(':disabled') && !document.getElementById('skeletal-symbols').checked")
 pick('ethanol');form('skeletal');assert not ev("document.getElementById('skeletal-symbols').checked")
 invalid_commands([{'value':1},{'value':None},{'molecule':'methane'},{'session':'stale'}])
 before=ui_analysis()
 for value in [True, 'true',None]:
  ev("(()=>{const d=structuredClone(window.__etherLast);d.symbols="+json.dumps(value)+";d.analysis.explanation='FAKE';dispatchEvent(new MessageEvent('message',{origin:location.origin,source:document.querySelector('iframe').contentWindow,data:d}))})()")
  assert ui_analysis()==before
 result['checks'].append('Native Space, open rule retained; model coordinates unchanged; CHn preserved over model/naming/3D, disabled3D; explicit-form reset; methane fallback; wrong/malformed/stale packets rejected')
 # Delay the real model/script ACK. Old graph and checkbox must stay gated;
 # switching form or molecule during the wait must finish on the latest choice.
 cev("window.savedProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)}")
 before=ev('window.__etherAck');ev("document.getElementById('skeletal-symbols').click()")
 wait(ev,"document.querySelector('iframe').hidden && document.getElementById('skeletal-symbols').matches(':disabled')")
 sent=ev('window.__etherSent');ev("document.getElementById('skeletal-symbols').click()");assert ev('window.__etherSent')==sent
 ev("document.querySelector('input[name=mode][value=expanded]').click()")
 cev('Jmol.getPropertyAsArray=savedProperty');wait(ev,'window.__etherAck===window.__etherSent');visible()
 assert cev("mode2D==='expanded'") and not ev("document.getElementById('skeletal-symbols').checked")
 form('skeletal')
 cev("Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)};setTimeout(()=>{Jmol.getPropertyAsArray=savedProperty},600)")
 ev("document.getElementById('skeletal-symbols').click()");wait(ev,"document.querySelector('iframe').hidden")
 pick('methane');assert cev("mode2D==='condensed'") and not ev("document.getElementById('skeletal-symbols').checked")
 result['checks'].append('Delayed actual ACK gates checkbox/graph/duplicate clicks; pendingCHn→expanded and pendingCHn→methane finish on latest mode/model')
 pick('dimethyl_2_3_butane');form('skeletal');symbols(True)
 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.3)
  assert ev('document.documentElement.scrollWidth<=innerWidth')
  screenshot('/tmp/react-symbols-'+str(width)+'-20261027.png')
 result['checks'].append('1500/390px layout without page overflow; screenshots captured')
 # Retry and remount are fresh sessions, not saved CHn preferences.
 ev("document.querySelector('iframe').dispatchEvent(new Event('error'))")
 wait(ev,"!!document.querySelector('[role=alert]')")
 assert ev("document.getElementById('skeletal-symbols').matches(':disabled')")
 ev("document.querySelector('[role=alert] button').click()");visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 ev("window.__etherAck=0;window.__etherSent=0")
 cev("addEventListener('message',e=>{if(e.source===parent && e.data?.channel==='namelecule-viewer-v4' && e.data.command)parent.__etherSent=e.data.id})")
 assert cev("selectedMol==='ethanol' && mode2D==='condensed'") and ev("!document.getElementById('skeletal-symbols').checked")
 form('skeletal');symbols(True)
 ev("location.hash='#/library'");wait(ev,"!document.querySelector('iframe')")
 ev("location.hash='#/viewer'");visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 assert cev("selectedMol==='ethanol' && mode2D==='condensed'") and ev("!document.getElementById('skeletal-symbols').checked")
 result['checks'].append('Actual iframe-error/retry and unmount/remount reset CHn to unchecked ethanol/condensed; error disables checkbox')
 checkpoint()
 # Same original engine, same viewport. Compare exact SVG attributes/text,
 # original name/chain/analysis, rather than merely checking CH text exists.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=symbols-baseline-'+str(time.time_ns()));app_ready();wait(ev,'!!window.JSmolReadyFlag')
 css=Path('react-preview/public/viewer-host.html').read_text().split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{const s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.getElementById('nomeclature3D').style.display='none';fResizeViewers()})()");time.sleep(.4)
 for key in dict.fromkeys(token[0] for token in captured):
  ev('selectedMol='+json.dumps(key)+';fSelectMol();fResizeViewers()')
  wait(ev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models?.[0]?.file?.endsWith('/"+key+"_3D.sdf') && allAtomsTypeList3D.length>0");drain(ev)
  ev("$('#radio2DMode .mode2DOption').eq(2).trigger('click')")
  for token,expected in [(token,value) for token,value in captured.items() if token[0]==key]:
   _,value,ident=token;source_symbol(value)
   if ident!='base':ev("$('#"+ident+"').trigger('click')")
   actual=snap(ev,'2d')
   if actual!=expected:Path('/tmp/react-symbols-mismatch-20261027.json').write_text(json.dumps({'case':token,'react':expected,'main':actual},ensure_ascii=False,indent=2))
   assert actual==expected,(token,'see mismatch JSON')
   result['parity'].append({'case':token,'exact':True})
   if ident!='base':ev("$('#"+ident+"').trigger('click')")
  print('CHn main parity',key,flush=True)
 result['checks'].append('All captured source SVG/name/chain/highlights/numbering exactly match unchanged main52 at equal viewport')
 assert len(result['parity'])==len(captured);assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;checkpoint()
 Path('/tmp/react-symbols-browser-20261027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'captures':len(captured),'parity':len(result['parity']),'javascriptErrors':len(js_errors)}),flush=True)
