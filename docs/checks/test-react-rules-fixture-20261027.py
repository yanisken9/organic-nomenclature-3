"""Focused rule checks in actual Firefox; main source is not modified."""
from pathlib import Path
# Reuse the existing connection and ACK-aware helpers, not the ether suite.
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0]
exec(compile(helper,'existing-viewer-harness','exec'))

result={'completed':False,'checks':[],'syntheticFixture':True}
try:
 navigate('react-preview/dist/?v=rules-fixture-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe()
 ident=ev("document.querySelector('[data-component]').dataset.component");component(ident);assert ev('window.__etherLast.analysis.rules.length===1')
 # Explicit adapter fixture, not evidence that free exploration enables alkoxy.
 ev("""(()=>{const d=structuredClone(window.__etherLast),a=d.analysis.rules[0];a.title='Fixture <img src=x onerror=window.BAD=1>';a.text=['<script>window.BAD=1</script>',{tag:'sub',classes:[],row:null,children:['n']}];d.analysis.rules.push({...structuredClone(a),id:'alkoxy',title:'Second fixture'});dispatchEvent(new MessageEvent('message',{origin:location.origin,source:document.querySelector('iframe').contentWindow,data:d}))})()""")
 assert ev("document.querySelectorAll('.react-rule-panel').length===2 && [...document.querySelectorAll('.react-rule-body')].every(e=>e.hidden)")
 ev("document.querySelectorAll('.react-rule-toggle')[0].click()")
 assert ev("!document.querySelectorAll('.react-rule-body')[0].hidden && document.querySelectorAll('.react-rule-body')[1].hidden")
 ev("document.querySelectorAll('.react-rule-toggle')[1].click()")
 assert ev("[...document.querySelectorAll('.react-rule-body')].every(e=>!e.hidden)")
 ev("document.querySelectorAll('.react-rule-toggle')[0].click()")
 assert ev("document.querySelectorAll('.react-rule-body')[0].hidden && !document.querySelectorAll('.react-rule-body')[1].hidden")
 assert ev("!window.BAD && !document.querySelector('.react-rule-panel img') && !document.querySelector('.react-rule-panel script') && document.querySelector('.ruleText').textContent==='<script>window.BAD=1</script>n'")
 result['checks'].append('Synthetic valid two-panel fixture: independent manual toggles; titles/text with HTML-looking strings stay text; sub preserved. Does not assert free-explorer alkoxy availability.')
 form('expanded');assert ev("document.querySelectorAll('.react-rule-panel').length===1 && document.querySelector('.react-rule-body').hidden")
 component(ident);assert not ev("!!document.querySelector('.react-rule-panel')")
 result['checks'].append('Next authentic source ACK replaces fixture; no rule auto-opens or survives deselection')
 assert not js_errors,js_errors;result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-rules-fixture-20261027.json').write_text(json.dumps(result,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result),flush=True)
