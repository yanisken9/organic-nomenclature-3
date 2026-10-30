"""Actual PNG lifecycle regression: unmount while native callback is pending."""
from pathlib import Path
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0].replace('9237','9238')
exec(compile(helper,'existing-viewer-harness-png','exec'))
folder=Path('/tmp/namelecule-react-png-20261027/downloads')
result={'completed':False,'checks':[]}
try:
 navigate('react-preview/dist/?v=png-unmount-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 cev("window.__toBlob=HTMLCanvasElement.prototype.toBlob;HTMLCanvasElement.prototype.toBlob=function(cb,...args){return __toBlob.call(this,b=>{window.__pendingBlob=()=>cb(b)},...args)}")
 before={p.name for p in folder.glob('*.png')}
 ev("document.getElementById('save-2d-png').click()")
 wait(cev,"typeof window.__pendingBlob==='function'")
 ev("window.__releaseDetached=document.querySelector('iframe').contentWindow.__pendingBlob;location.hash='#/library'")
 wait(ev,"!document.querySelector('iframe')")
 ev('window.__releaseDetached();delete window.__releaseDetached');time.sleep(.5)
 assert {p.name for p in folder.glob('*.png')}==before,'Late detached native callback downloaded a file'
 ev("location.hash='#/viewer'");visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 assert cev("selectedMol==='ethanol' && mode2D==='condensed'")
 assert not ev("!!document.querySelector('.molecule-export-status') || !!document.querySelector('[role=alert]')")
 result['checks'].append('Pending native callback after unmount starts no late download; remount is clean ethanol/condensed with no stale export status')
 assert not js_errors,js_errors;result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/namelecule-react-png-20261027/lifecycle.json').write_text(json.dumps(result,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result),flush=True)
