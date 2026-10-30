"""Deployment smoke: report, welcome, eight expanded alkanes and existing lesson."""
from pathlib import Path
import argparse,traceback
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-setup','exec'))
result={'functionalCompleted':False,'checks':[]}
try:
 navigate('docs/professor-20261030/update.html?v=release-20261030')
 assert ev("document.title.includes('30 Οκτωβρίου')&&document.querySelector('nav a').href.includes('design/welcome-proposal.html')")
 result['checks'].append('Professor report has welcome link');screenshot(str(args.output/'report.png'))
 navigate('design/welcome-proposal.html?v=release-20261030')
 assert ev("!![...document.querySelectorAll('a')].find(a=>a.textContent.includes('Εξερεύνησε ελεύθερα')&&a.href.includes('mulermoc-nom-52.html'))")
 result['checks'].append('Welcome has Main exploration entry')
 navigate('mulermoc-nom-52.html?v=release-20261030');app_ready();ev('document.fonts.ready.then(()=>true)')
 assert ev('Object.keys(window.MOL2D).length===141')
 for key in ['methane','ethane','propane','butane','pentane','methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:
  ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true')
  until('selectedMol==='+json.dumps(key)+'&&mode2D==="expanded"&&!!molSvg.node.dataset.alkaneFixedCCScale')
  row=json.loads(ev("JSON.stringify((()=>{const s=molSvg.node,b=s.getBoundingClientRect(),labels=[...s.querySelectorAll('text:not([id^=number])')];return{key:selectedMol,atomLabels:labels.length,font:parseFloat(getComputedStyle(labels[0]).fontSize)*Math.hypot(labels[0].getScreenCTM().a,labels[0].getScreenCTM().b),clipped:labels.some(t=>{const r=t.getBoundingClientRect();return r.left<b.left-1||r.top<b.top-1||r.right>b.right+1||r.bottom>b.bottom+1})}})())"))
  assert row['atomLabels']>=5 and row['font']>10 and not row['clipped'],row
  result['checks'].append(row)
 navigate('design/theory-library.html?v=release-20261030')
 assert ev("document.querySelectorAll('a[href*=\"scenario=\"]').length===14")
 result['checks'].append('Library has14active lesson links')
 navigate('mulermoc-nom-52.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=release-20261030')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')")
 app_ready();ev('fScenarioGo(17);true')
 until("selectedMol==='ethyl_3_dimethyl_2_5_hexane'&&mode2D==='expanded'&&!!molSvg.node.dataset.alkaneFixedCCScale")
 assert ev("molSvg.node.querySelectorAll('text:not([id^=number])').length===32")
 result['checks'].append('Existing lesson step18 renders32expanded atom labels')
 result['functionalCompleted']=True
except Exception as error:
 result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors;result['strictJavaScriptConsoleClean']=not js_errors
 (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'functionalCompleted':result['functionalCompleted'],'checks':len(result['checks']),'jsErrors':len(js_errors)}),flush=True)
if not result['functionalCompleted']:raise SystemExit(1)
