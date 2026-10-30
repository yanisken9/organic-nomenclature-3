"""Real Firefox native3D control parity, effects, gates and lifecycle. Test artifacts only."""
from pathlib import Path
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'existing-viewer-harness','exec'))
result={'completed':False,'checks':[],'parity':[]};captures=[]
source_paths=['react-preview/src/MoleculePreview.jsx','react-preview/public/viewer-host-bridge.js','react-preview/src/preview.css','react-preview/public/viewer-host.html']+[str(p) for p in Path('react-preview/dist').rglob('*') if p.is_file()]
fingerprint={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in source_paths}
controls=r"JSON.stringify({hydrogens:hydrogens3DFlag,labels:atomSymbols3DFlag,rotating:rotateFlag,style:vis3D})"
# Include real visibility, element label, atom sphere and bond radii, as well as
# unchanged coordinates/connectivity/highlight state. Rotation/camera excluded.
render=r"""JSON.stringify((()=>({scene:JSON.parse("""+json.dumps(scene)+r"""),labels:Jmol.evaluateVar(jmolAppletNomeclature,'{all}.label'),atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').map(a=>({n:a.atomno,spacefill:a.spacefill})),bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,'bondInfo','all').map(b=>({a:b.atom1.atomno,b:b.atom2.atomno,radius:b.radius}))}))())"""
# scene is a JS expression string, not a snapshot; evaluate directly.
render=render.replace('JSON.parse('+json.dumps(scene)+')','JSON.parse('+scene+')')
def control(key,value):
 if json.loads(cev(controls))[key]==value:return
 if key=='style':action("(()=>{let s=document.getElementById('style-3d');s.value="+json.dumps(value)+";s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 else:action("document.getElementById('"+{'hydrogens':'hydrogens','labels':'labels','rotating':'rotation'}[key]+"-3d').click()")
 assert json.loads(cev(controls))[key]==value
 assert ui_controls()==json.loads(cev(controls))
def ui_controls():return json.loads(ev("JSON.stringify({hydrogens:document.getElementById('hydrogens-3d').checked,labels:document.getElementById('labels-3d').checked,rotating:document.getElementById('rotation-3d').checked,style:document.getElementById('style-3d').value})"))
def scene_snapshot(evaluate):
 drain(evaluate);value=json.loads(evaluate(render))
 for echo in value['scene']['echoes']:
  for v in echo.values():
   if isinstance(v,dict):v.pop('boxXY',None)
 return value
def capture(key,ident):
 value=scene_snapshot(cev);assert ui_analysis()==json.loads(cev(signature))['analysis']
 captures.append({'molecule':key,'component':ident,'controls':json.loads(cev(controls)),'render':value})
def source_controls(evaluate,values):
 for key,ident,flag in [('hydrogens','hydrogensCheck','hydrogens3DFlag'),('labels','atomSymbolsCheck','atomSymbols3DFlag'),('rotating','rotateCheck','rotateFlag')]:
  if evaluate(flag)!=values[key]:evaluate("$('#"+ident+"').trigger('click')")
 if evaluate('vis3D')!=values['style']:evaluate("$('#dropLi"+str(['ballnstick','spacefill','sticks'].index(values['style']))+"').trigger('click')")
def save():
 Path('/tmp/namelecule-3d-controls-20261027/capture.json').write_text(json.dumps({'sourceSHA256':fingerprint,'result':result,'captures':captures},ensure_ascii=False))
def invalid(patches):
 before=ev('window.__etherReplies.length')
 for patch in patches:
  ev("(()=>{const d=window.__etherLast;document.querySelector('iframe').contentWindow.postMessage({channel:d.channel,session:d.session,id:d.id+100000,command:'hydrogens3d',value:true,molecule:d.molecule,..."+json.dumps(patch)+"},location.origin)})()")
 time.sleep(.15);assert ev('window.__etherReplies.length')==before
try:
 navigate('react-preview/dist/?v=controls-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 assert not ev("!!document.getElementById('style-3d')")
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{const r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 view('3d');assert ui_controls()=={'hydrogens':True,'labels':True,'rotating':False,'style':'ballnstick'}
 keys=['ethanol','ethyl_isopropyl_ether','isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5']
 for key in keys:
  pick(key);view('2d');before=snap(cev,'2d');view('3d')
  for style in ['ballnstick','spacefill','sticks']:
   control('style',style)
   for hydrogens in [True,False]:
    control('hydrogens',hydrogens)
    for labels in [True,False]:
     control('labels',labels);capture(key,'base')
  control('style','ballnstick');control('labels',False);control('hydrogens',False)
  component('comp5');capture(key,'comp5');control('labels',True);capture(key,'comp5');component('comp5')
  view('2d');assert snap(cev,'2d')==before,'3D controls altered 2D source rendering';view('3d')
  save();print('3D controls captured',key,flush=True)
 result['checks'].append('3representatives ×12style/H/label combinations plus numbered-chain labels; React analysis matches native; 2D depiction unchanged')
 pick('ethanol');control('hydrogens',False)
 atoms=json.loads(cev("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').map(a=>({n:a.atomno,s:a.sym,v:a.visible})))"))
 assert len([a for a in atoms if a['s']=='H' and a['v']])==1 and len([a for a in atoms if a['s']=='H' and not a['v']])==5
 result['checks'].append('Actual ethanol5C–H hidden, O–H hydrogen remains visible; atom count unchanged')
 # Rotation must move the camera, then really stop, while molecular xyz stays fixed.
 xyz=json.loads(cev(scene))['atoms'];control('rotating',True)
 orientation="JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').quaternion)"
 a=cev(orientation);time.sleep(.35);b=cev(orientation);assert a!=b
 control('rotating',False);a=cev(orientation);time.sleep(.35);assert a==cev(orientation)
 assert [{k:a[k] for k in ['n','s','x','y','z']} for a in xyz]==[{k:a[k] for k in ['n','s','x','y','z']} for a in json.loads(cev(scene))['atoms']]
 result['checks'].append('Rotation moves camera, stops on request, leaves molecular coordinates unchanged')
 # Preserve preferences through model, native naming, 2D/3D and zoom, reset on retry.
 control('style','sticks');control('labels',False);control('hydrogens',False)
 pref=ui_controls();pick('methane');assert ui_controls()==pref
 pick('ethyl_isopropyl_ether');naming('common');assert ui_controls()==pref;naming('iupac')
 view('2d');invalid([{'value':'false'},{'value':False},{'command':'style3d','value':'sticks'}]);view('3d');assert ui_controls()==pref
 action("document.querySelector('button[aria-label=Μεγέθυνση]').click()");assert ui_controls()==pref
 invalid([{'value':'false'},{'value':None},{'command':'style3d','value':'bad'},{'command':'style3d','value':1},{'molecule':'methane'},{'session':'old'}])
 before=ui_analysis()
 for patch in [None,{}, {'hydrogens':False,'labels':True,'rotating':False,'style':'sticks'}, {'hydrogens':False,'labels':False,'rotating':'false','style':'sticks'}]:
  ev("(()=>{const d=structuredClone(window.__etherLast);d.controls3D="+json.dumps(patch)+";d.analysis.explanation='FAKE';dispatchEvent(new MessageEvent('message',{origin:location.origin,source:document.querySelector('iframe').contentWindow,data:d}))})()")
  assert ui_analysis()==before
 result['checks'].append('Preferences preserved across methane/ether/naming/2D/zoom; invalid, stale, wrong-model/2D commands and forged control ACKs rejected')
 # Native keyboard activation.
 ev("document.getElementById('labels-3d').focus()");before=ev('window.__etherAck')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':' '},{'type':'keyUp','value':' '}]}]})
 wait(ev,'window.__etherSent>'+str(before)+' && window.__etherAck===window.__etherSent');visible();assert ui_controls()['labels']
 # Delayed model/script gate: no duplicate controls, old controls cannot queue behind zoom.
 cev("window.savedProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)}")
 ev("document.getElementById('labels-3d').click()")
 wait(ev,"document.querySelector('iframe').hidden && document.getElementById('labels-3d').matches(':disabled')")
 sent=ev('window.__etherSent');ev("document.getElementById('hydrogens-3d').click();document.getElementById('labels-3d').click()");assert ev('window.__etherSent')==sent
 # Allow a newer model command while the style command is still awaiting ACK.
 ev("(()=>{let s=document.getElementById('molecule-select');s.value='ethanol';s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 cev('Jmol.getPropertyAsArray=savedProperty');wait(ev,'window.__etherAck===window.__etherSent');visible()
 assert cev("selectedMol==='ethanol'") and not ui_controls()['labels']
 cev("Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)}")
 ev("document.querySelector('button[aria-label=Μεγέθυνση]').click()")
 wait(ev,'window.__etherSent>window.__etherAck');assert ev("document.getElementById('style-3d').matches(':disabled')")
 cev('Jmol.getPropertyAsArray=savedProperty');wait(ev,'window.__etherAck===window.__etherSent');visible()
 result['checks'].append('Space key works; pending controls hide graph/disable duplicates; pending control→new model keeps latest state; pending zoom gates style')
 # Mobile/desktop layout, actual screenshots.
 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.3)
  assert ev('document.documentElement.scrollWidth<=innerWidth')
  assert ev("[...document.querySelectorAll('.molecule-controls-3d input,.molecule-controls-3d select')].every(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})")
  screenshot('/tmp/namelecule-3d-controls-20261027/controls-'+str(width)+'.png')
 result['checks'].append('1500/390px no page/control overflow; screenshots captured')
 # Real model mismatch failure and retry reset (including flags).
 control('rotating',True)
 cev("Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[{file:'wrong.sdf'}]}:savedProperty(a,p,...r)}")
 start=time.monotonic();ev("document.getElementById('hydrogens-3d').click()")
 wait(ev,"!!document.querySelector('[role=alert]')",14);result['modelFailureSeconds']=round(time.monotonic()-start,2)
 assert ev("document.getElementById('hydrogens-3d').matches(':disabled')")
 ev("document.querySelector('[role=alert] button').click()");child=None;visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();view('3d')
 assert ui_controls()=={'hydrogens':True,'labels':True,'rotating':False,'style':'ballnstick'}
 control('rotating',True);old_child=child
 ev("location.hash='#/library'");wait(ev,"!document.querySelector('iframe')")
 ev("location.hash='#/viewer'");child=None;visible();child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();view('3d')
 assert ui_controls()=={'hydrogens':True,'labels':True,'rotating':False,'style':'ballnstick'} and child!=old_child
 result['checks'].append('Actual model mismatch yields bounded failure/retry resets defaults; leaving rotating viewer removes iframe, re-entry creates fresh default session')
 # Direct native main comparison at equal viewport, no production file edits.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=controls-main-'+str(time.time_ns()));app_ready();wait(ev,'!!window.JSmolReadyFlag')
 css=Path('react-preview/public/viewer-host.html').read_text().split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{const s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.documentElement.dataset.view='3d';document.getElementById('nomeclature3D').style.display='block';fResizeViewers()})()")
 for key in keys:
  ev('selectedMol='+json.dumps(key)+';fSelectMol();fResizeViewers()')
  wait(ev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models?.[0]?.file?.endsWith('/"+key+"_3D.sdf') && allAtomsTypeList3D.length>0");drain(ev)
  for row in [r for r in captures if r['molecule']==key]:
   source_controls(ev,row['controls'])
   if row['component']!='base':ev("$('#"+row['component']+"').trigger('click')")
   actual=scene_snapshot(ev)
   if actual!=row['render']:Path('/tmp/namelecule-3d-controls-20261027/mismatch.json').write_text(json.dumps({'case':row,'main':actual},ensure_ascii=False,indent=2))
   assert actual==row['render'],(key,row['component'],row['controls'],'see mismatch.json')
   result['parity'].append({'molecule':key,'component':row['component'],'controls':row['controls'],'exact':True})
   if row['component']!='base':ev("$('#"+row['component']+"').trigger('click')")
  print('3D controls native parity',key,flush=True)
 result['checks'].append('All42actual3Drender snapshots exactly equal unchanged native main52 controls at same viewport')
 assert len(result['parity'])==42
 result['knownJSmolErrors']=[e for e in js_errors if e.get('text')=="TypeError: can't access property \"setDisplay\", this.viewer is null" and any(f.get('url')=='https://chemapps.stolaf.edu/jmol/jsmol/j2s/core/corejmol.z.js' for f in e.get('stackTrace',{}).get('callFrames',[]))]
 result['unexpectedJavaScriptErrors']=[e for e in js_errors if e not in result['knownJSmolErrors']]
 assert not result['unexpectedJavaScriptErrors'],result['unexpectedJavaScriptErrors']
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;save()
 Path('/tmp/namelecule-3d-controls-20261027/browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'captures':len(captures),'parity':len(result['parity']),'errors':len(js_errors)}),flush=True)
