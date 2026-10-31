from pathlib import Path
import os,json,traceback
ROOT=Path.cwd();HERE=ROOT/'docs/checks/publication-20261031'
os.environ['NAMELECULE_TEST_BASE_URL']='https://yanisken9.github.io/organic-nomenclature-3/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'base':os.environ['NAMELECULE_TEST_BASE_URL'],'checks':[],'completed':False}
try:
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  navigate('docs/professor-20261031/update.html');assert ev('document.body.textContent.includes("31 Οκτωβρίου 2026")');assert ev('document.documentElement.scrollWidth<=innerWidth');out['checks'].append({'reportWidth':width,'noOverflow':True})
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 navigate('design/welcome-proposal.html?v=release-20261031');assert ev('!!document.querySelector("a[href*=mulermoc-nom-52]")');out['checks'].append({'welcome':True})
 navigate('mulermoc-nom-52.html');app_ready();assert ev('Object.keys(nameExamples).length')==141;assert ev('!!window.NameleculeLabelMetrics');out['checks'].append({'MainMolecules':141,'newMetrics':True})
 for key,count in [('propene',9),('isopropyl_4_dimethyl_3_5_heptanol_2',39),('ethyne',4)]:
  ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true')
  until('selectedMol==='+json.dumps(key)+'&&mode2D==="expanded"');until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))==='+str(count))
  until('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG[data-label-error]")')
  out['checks'].append({'key':key,'3Datoms':count,'expandedSVG':True})
 screenshot(HERE/'main-public.png')
 navigate('mulermoc-nom-52.html?scenario=scenarios/saturated-monoalcohols-nomenclature.scenario.json&present=1&from=theory-library')
 until('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&!document.documentElement.classList.contains("lesson-loading")');app_ready()
 ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index===1')
 ev('document.getElementById("scPrev").click();true');until('fScenarioPresent().index===0')
 ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("/organic-nomenclature-3/design/theory-library.html")');out['checks'].append({'publicLessonNavigationExit':True});out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;out['allDiagnosticEntries']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['error','warn']]
 (HERE/'main-public.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'jsErrors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
