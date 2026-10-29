"""Actual Firefox release smoke under Pages prefix; records third-party diagnostics separately."""
from pathlib import Path
import argparse,os
parser=argparse.ArgumentParser();parser.add_argument('--base',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();os.environ['NAMELECULE_TEST_BASE_URL']=args.base
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
r={'completed':False,'baseURL':args.base,'checks':[]};contexts=[ctx]
try:
 navigate('docs/professor-20261029/main-esters-update.html')
 assert ev("document.querySelectorAll('tbody tr').length===5 && document.body.textContent.includes('js/mulermoc-nom-core-52.js')")
 r['checks'].append('Professor report: five molecules, explicit core report and links')
 navigate('design/welcome-proposal.html');assert ev("!!document.querySelector('a[href*=mulermoc-nom-52]')")
 navigate('design/theory-library.html');assert ev("document.querySelectorAll('a[href*=scenario]').length===14 && !!document.getElementById('esters-card')")
 r['checks'].append('Main welcome52 and double ester card;14active lesson links')
 navigate('mulermoc-nom-52.html?v=release-smoke-20261029');app_ready();until('!!window.JSmolReadyFlag')
 assert ev("Object.keys(nameExamples).length===141 && Object.values(nameExamples).filter(v=>v.classification?.chemicalClass==='esters').length===9")
 ev("document.getElementById('tert_butyl_methanoate').click();document.querySelectorAll('#radio2DMode .mode2DOption')[1].click();true")
 until("mainChainPool3DKey==='tert_butyl_methanoate' && Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length===17")
 assert ev("[...document.querySelectorAll('#jsmeNomeclatureSVG svg line')].every(e=>Math.abs(+e.getAttribute('x1')-e.getAttribute('x2'))<.01 || Math.abs(+e.getAttribute('y1')-e.getAttribute('y2'))<.01)")
 assert ev("(()=>{const l=jsmeNomeclatureApplet.molFile().split('\\n'),p=i=>[+l[i+3].slice(0,10),+l[i+3].slice(10,20)];return p(8)[0]<p(1)[0]&&p(8)[1]===p(1)[1]})()")
 ev("document.getElementById('methyl_methanoate').click();document.querySelectorAll('#radio2DMode .mode2DOption')[0].click();true")
 assert ev("document.getElementById('C1').textContent==='C'")
 ev("document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();true")
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text')].some(e=>e.textContent==='H' && getComputedStyle(e).visibility!=='hidden')")
 r['checks'].append('Main141/9esters; new tertformate real3D17atoms, orthogonal expanded+leftH; first ester noextraH, skeletalHhidden')
 navigate('react-preview/dist/#/');until("document.querySelector('#root').textContent.length>100")
 ev("location.hash='#/library';true");until("document.querySelectorAll('a[href*=\"#/lesson/\"]').length===12")
 first=ev("document.querySelector('a[href*=\"#/lesson/\"]').getAttribute('href')")
 ev("location.hash='#/viewer';true");until("document.querySelectorAll('#molecule-select option').length===126")
 until("!document.querySelector('#molecule-select').disabled",seconds=95)
 assert ev("document.querySelector('#molecule-select').value==='ethanol'")
 ev("document.querySelector('[data-view=\"3d\"]').click();true")
 until("document.querySelector('[data-view=\"3d\"]').getAttribute('aria-pressed')==='true' && !document.querySelector('iframe').hidden",seconds=30)
 until("document.querySelector('iframe').contentWindow.document.documentElement.dataset.view==='3d'",seconds=20)
 r['checks'].append('Preserved React126/12lessons;ethanol2D→3D host')
 ctx=call('browsingContext.create',{'type':'tab'})['context'];contexts.append(ctx);call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
 navigate('react-preview/dist/'+first)
 until("!!document.querySelector('.lesson-stage iframe:not([hidden])') && document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false'",seconds=95)
 assert ev("document.querySelector('iframe').contentWindow.fScenarioPresent().steps.length===21")
 route=first.rsplit('/',1)[0]+'/2';ev('location.hash='+json.dumps(route)+';true')
 until("document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false' && document.querySelector('iframe').contentWindow.fScenarioPresent().index===1",seconds=25)
 r['checks'].append('Preserved React alkane lesson21steps, step1→2')
 r['functionalChecksPassed']=True
 external=[e for e in js_errors if 'JmolTracker.php' in e.get('text','') and ('X-Frame-Options' in e.get('text','') or 'sameorigin' in e.get('text',''))]
 unexpected=[e for e in js_errors if e not in external];r['externalTrackerDiagnostics']=external;r['unexpectedJavascriptErrors']=unexpected
 assert not unexpected,unexpected
 r['completed']=True
finally:
 r['javascriptErrors']=js_errors;args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 for target in contexts:call('browsingContext.close',{'context':target})
 call('session.end',{});print(json.dumps({'completed':r['completed'],'checks':len(r['checks']),'errors':len(js_errors)}),flush=True)
