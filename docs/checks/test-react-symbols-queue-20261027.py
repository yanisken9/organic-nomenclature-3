"""Actual Firefox regression: CHn waits for queued mode to become authoritative."""
from pathlib import Path
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'existing-viewer-harness','exec'))
result={'completed':False,'checks':[]}
try:
 navigate('react-preview/dist/?v=symbols-queued-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 cev("window.savedProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:savedProperty(a,p,...r)}")
 ev("document.querySelector('button[aria-label=Μεγέθυνση]').click()")
 wait(ev,'window.__etherSent>window.__etherAck')
 ev("document.querySelector('input[name=mode][value=skeletal]').click()")
 gated=ev("document.getElementById('skeletal-symbols').matches(':disabled')")
 assert gated,'CHn can be sent while an earlier queued mode is not yet applied'
 cev('Jmol.getPropertyAsArray=savedProperty');wait(ev,'window.__etherAck===window.__etherSent');visible()
 assert not ev("document.getElementById('skeletal-symbols').matches(':disabled')")
 action("document.getElementById('skeletal-symbols').click()")
 assert cev("mode2D==='condensedZigZag'")
 result['checks'].append('Delayed zoom then queued skeletal mode: CHn disabled until latest ACK, then native annotation succeeds without timeout')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-symbols-queue-20261027.json').write_text(json.dumps(result,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result),flush=True)
