"""Real Firefox3D PNG queue, timeout, stale packet, retry and detached callback checks. Run after browser suite, not concurrently."""
from pathlib import Path
helper=Path('docs/checks/test-react-3d-png-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'real-prompt-download-harness-9238','exec'))
result={'completed':False,'checks':[]}
# Capture the actual native encoding call; delay only delivery to its unchanged
# save function. This is fault injection, not a claim of a real library outage.
def hold_save():
 cev("window.__nativeJmolSave=Jmol._saveFile;Jmol._saveFile=function(...args){window.__releaseSave=()=>__nativeJmolSave.apply(this,args);return 'OK'}")
def release_save():cev('Jmol._saveFile=__nativeJmolSave;__releaseSave();delete __releaseSave')
def attach():
 global child
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();observe_download(cev)
try:
 navigate('react-preview/dist/?v=3d-png-lifecycle-'+str(time.time_ns())+'#/viewer');visible();attach();view('3d')
 # Model/script gate is real, so a pending zoom cannot export an obsolete scene.
 cev("window.__nativeProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:__nativeProperty(a,p,...r)}")
 ev("document.querySelector('button[aria-label=Μεγέθυνση]').click()")
 wait(ev,'window.__etherSent>window.__etherAck');assert ev("document.getElementById('save-3d-png').disabled")
 sent=ev('window.__etherSent');ev("document.getElementById('save-3d-png').click()");assert ev('window.__etherSent')==sent
 cev('Jmol.getPropertyAsArray=__nativeProperty');wait(ev,'window.__etherSent===window.__etherAck');visible()
 # Reject wrong view/model/mode/naming/component/preferences/value/session.
 before={p.name for p in folder.glob('*')};count=ev('window.__etherReplies.length')
 for patch in [{'view':'2d'},{'view':None},{'molecule':'methane'},{'mode':'expanded'},{'naming':'common'},{'component':'comp12'},{'controls3D':None},{'controls3D':{'style':'sticks','hydrogens':True,'labels':True,'rotating':False}},{'value':'svg'},{'session':'stale'}]:
  ev("(()=>{const d=window.__etherLast;document.querySelector('iframe').contentWindow.postMessage({...d,type:undefined,id:d.id+10000,command:'export',value:'png',component:null,..."+json.dumps(patch)+"},location.origin)})()")
 time.sleep(.2);assert ev('window.__etherReplies.length')==count and {p.name for p in folder.glob('*')}==before
 result['checks'].append('Actual pendingzoom disables export; wrong view/model/mode/name/component/preferences/value/session packets start no download/ACK')
 # Native callback holds later model/view actions through PNG/echo cleanup.
 hold_save();before={p.name for p in folder.glob('*')};ev("document.getElementById('save-3d-png').click()")
 wait(cev,"typeof window.__releaseSave==='function'");assert ev("document.getElementById('save-3d-png').disabled")
 ev("(()=>{let s=document.getElementById('molecule-select');s.value='methane';s.dispatchEvent(new Event('change',{bubbles:true}));document.querySelector('[data-view=\\\"2d\\\"]').click()})()")
 # Regression: queued actions must retain the longer native-export budget,
 # rather than installing a fresh10s parent timeout behind a90s export.
 time.sleep(10.5);assert cev("selectedMol==='ethanol'")
 assert not ev("!!document.querySelector('[role=alert]')")
 release_save();path,info=downloaded(before);assert 'αιθανόλη' in unicodedata.normalize('NFC',path.name)
 wait(ev,'window.__etherAck===window.__etherSent');visible();assert cev("selectedMol==='methane' && document.documentElement.dataset.view==='2d'")
 assert not ev("document.getElementById('save-2d-png').disabled")
 result['checks'].append('Delayed native3D save holds queue; model→2D changes wait; old ethanol PNG is correctly named, latest methane2D then ready')
 # Keyboard Enter uses the same actual native prompt and download.
 pick('ethanol');view('3d');before={p.name for p in folder.glob('*')};ack=ev('window.__etherAck')
 ev("document.getElementById('save-3d-png').focus()")
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]})
 wait(ev,'window.__etherSent>'+str(ack)+' && window.__etherAck===window.__etherSent');path,info=downloaded(before);assert info['width']==info['height']==1200
 result['checks'].append('Native keyboard Enter requests actual1200square PNG')
 # Full production90s deadline, not a substituted clock. Late callbacks cannot
 # download an obsolete model after failure; retry starts a fresh default host.
 hold_save();before={p.name for p in folder.glob('*')};start=time.monotonic();ev("document.getElementById('save-3d-png').click()")
 wait(cev,"typeof window.__releaseSave==='function'")
 print('Waiting actual90s3Dexport deadline',flush=True)
 wait(ev,"!!document.querySelector('[role=alert]')",96)
 elapsed=time.monotonic()-start;assert 89<=elapsed<=94;result['nativeAsyncTimeoutSeconds']=round(elapsed,2)
 assert ev("document.querySelector('[role=alert]').textContent.includes('λήψη PNG')")
 release_save();time.sleep(.4);assert {p.name for p in folder.glob('*')}==before
 assert cev('window.prompt.toString().includes("[native code]")')
 ev("document.querySelector('[role=alert] button').click()");child=None;visible();attach()
 assert cev("selectedMol==='ethanol' && document.documentElement.dataset.view==='2d' && !rotateFlag")
 result['checks'].append('Actual90s native asynchronous timeout fails closed; late Jmol save suppressed; original prompt restored; fresh retry defaults')
 # Unmount while the native encoder/save callback is pending. Release that
 # detached callback from the parent and verify it cannot start a late download.
 view('3d');hold_save();before={p.name for p in folder.glob('*')};ev("document.getElementById('save-3d-png').click()")
 wait(cev,"typeof window.__releaseSave==='function'")
 ev("window.__releaseDetached=document.querySelector('iframe').contentWindow.__releaseSave;location.hash='#/library'")
 wait(ev,"!document.querySelector('iframe')");ev('window.__releaseDetached();delete window.__releaseDetached');time.sleep(.4)
 assert {p.name for p in folder.glob('*')}==before
 ev("location.hash='#/viewer'");child=None;visible();attach();assert cev("selectedMol==='ethanol' && !rotateFlag")
 result['checks'].append('Unmount during native3D encoding blocks detached late save; re-entry fresh and no stale export state')
 for width,height in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});view('3d');time.sleep(.2)
  assert ev('document.documentElement.scrollWidth<=innerWidth');screenshot(str(artifacts/('png-layout-'+str(width)+'.png')))
 result['checks'].append('1500/390px PNG3D action fits without page overflow; screenshots captured')
 result['knownJSmolErrors']=[e for e in js_errors if e.get('text')=="TypeError: can't access property \"setDisplay\", this.viewer is null" and any(f.get('url')=='https://chemapps.stolaf.edu/jmol/jsmol/j2s/core/corejmol.z.js' for f in e.get('stackTrace',{}).get('callFrames',[]))]
 result['unexpectedJavaScriptErrors']=[e for e in js_errors if e not in result['knownJSmolErrors']];assert not result['unexpectedJavaScriptErrors'],result['unexpectedJavaScriptErrors']
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 (artifacts/'lifecycle.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result,ensure_ascii=False),flush=True)
