"""Actual Firefox lifecycle checks using the same naming parity harness."""
from pathlib import Path
# Reuse the connection, ACK-aware actions and bounded waits without running the
# parity suite. The helper prelude creates a fresh BiDi session, not app mocks.
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'ether-naming-harness','exec'))
result={'completed':False,'checks':[]}
def reconnect():
 global child
 visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']
 ev("window.__etherAck=0;window.__etherSent=0")
 cev("addEventListener('message',e=>{if(e.source===parent && e.data?.channel==='namelecule-viewer-v4' && e.data.command)parent.__etherSent=e.data.id})")
try:
 navigate('react-preview/dist/?v=ether-lifecycle-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 pick('dimethylether')
 # A real naming command followed by a model change before the model ACK.
 cev("window.__savedModelProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...r){return p==='modelInfo'?{models:[]}:__savedModelProperty(a,p,...r)};setTimeout(()=>{Jmol.getPropertyAsArray=__savedModelProperty},600)")
 ev("document.querySelector('input[name=ether-naming][value=common]').click()")
 wait(ev,"document.querySelector('.react-ether-naming').disabled")
 pick('ethanol')
 assert cev("selectedMol==='ethanol' && etherNamingMode==='common'")
 assert not ev("!!document.querySelector('.react-ether-naming')")
 pick('dimethylether')
 assert ev("document.querySelector('input[name=ether-naming][value=common]').checked")
 result['checks'].append('Pending IUPAC-to-common then non-ether model switch preserves preference and finishes on latest model; return to ether remains common')
 old=ev("document.querySelector('iframe').src")
 ev("document.querySelector('iframe').dispatchEvent(new Event('error'))")
 wait(ev,"!!document.querySelector('[role=alert]')")
 assert ev("document.querySelector('.react-ether-naming').disabled && document.querySelector('iframe').hidden")
 ev("document.querySelector('[role=alert] button').click()")
 reconnect()
 assert ev("document.querySelector('iframe').src")!=old
 assert cev("selectedMol==='ethanol' && etherNamingMode==='iupac'")
 pick('dimethylether');assert ev("document.querySelector('input[name=ether-naming][value=iupac]').checked")
 result['checks'].append('Controlled actual iframe-error handler/retry clears common preference and analysis; fresh session starts ethanol/IUPAC; ether radio is IUPAC')
 naming('common')
 ev("location.hash='#/library'");wait(ev,"!document.querySelector('iframe')")
 ev("location.hash='#/viewer'");reconnect()
 assert cev("selectedMol==='ethanol' && etherNamingMode==='iupac'")
 pick('dimethylether');assert ev("document.querySelector('input[name=ether-naming][value=iupac]').checked")
 result['checks'].append('Unmount/remount resets common preference without persistent storage or main changes')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-ether-naming-lifecycle-20261027.json').write_text(json.dumps(result,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result),flush=True)
