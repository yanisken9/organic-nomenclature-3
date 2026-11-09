"""Smoke the extracted ZIP through its own serve.py, never the workspace HTTP root."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
assert os.environ.get('NAMELECULE_TEST_BASE_URL'), 'Set URL printed by extracted serve.py'
r={'completed':False,'baseURL':os.environ['NAMELECULE_TEST_BASE_URL'],'checks':[]};contexts=[ctx]
try:
 navigate('design/welcome-proposal.html');assert ev("!!document.querySelector('a[href*=mulermoc-nom-52]')")
 navigate('design/theory-library.html');assert ev("document.querySelectorAll('a[href*=scenario]').length===14");r['checks'].append('Packaged Main welcome52 and14lesson actions')
 navigate('react-preview/dist/#/');until("document.querySelector('#root').textContent.length>100")
 ev("location.hash='#/library';true");until("document.querySelectorAll('a[href*=\"#/lesson/\"]').length===12")
 first=ev("document.querySelector('a[href*=\"#/lesson/\"]').getAttribute('href')")
 ev("location.hash='#/viewer';true");until("document.querySelectorAll('#molecule-select option').length===126")
 until("!document.querySelector('#molecule-select').disabled",seconds=95)
 assert ev("document.querySelector('#molecule-select').value==='ethanol'")
 assert ev("document.querySelector('iframe').contentWindow.location.origin===location.origin")
 ev("document.querySelector('[data-view=\"3d\"]').click();true")
 until("document.querySelector('[data-view=\"3d\"]').getAttribute('aria-pressed')==='true' && !document.querySelector('iframe').hidden",seconds=30)
 until("document.querySelector('iframe').contentWindow.document.documentElement.dataset.view==='3d'",seconds=20)
 r['checks'].append('Packaged React welcome/library12/viewer126, ethanol2D and3D, same-originhost')
 viewer=ctx
 ctx=call('browsingContext.create',{'type':'tab'})['context'];contexts.append(ctx)
 call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
 navigate('react-preview/dist/'+first)
 until("!!document.querySelector('.lesson-stage iframe:not([hidden])') && document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false'",seconds=95)
 assert ev("document.querySelector('iframe').contentWindow.fScenarioPresent().steps.length===21")
 route=first.rsplit('/',1)[0]+'/2';ev('location.hash='+json.dumps(route)+';true')
 until("document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false' && document.querySelector('iframe').contentWindow.fScenarioPresent().index===1",seconds=25)
 assert ev("document.querySelector('iframe').contentWindow.location.origin===location.origin")
 r['checks'].append('Packaged native lesson host loads alkane lesson21steps and advances1→2')
 assert not js_errors,js_errors
 r['completed']=True
finally:
 r['javascriptErrors']=js_errors;Path('/tmp/namelecule-react-package-20261028/browser.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 for target in contexts:call('browsingContext.close',{'context':target})
 call('session.end',{});print(json.dumps(r),flush=True)
