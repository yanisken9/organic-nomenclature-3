"""Bounded real React UI verification against the publication candidate or live URL."""
from pathlib import Path
import os,json,traceback
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
os.environ.setdefault('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8051/organic-nomenclature-3/')
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'checks':[],'completed':False,'base':os.environ['NAMELECULE_TEST_BASE_URL']}
ready='!!document.querySelector(".molecule-stage iframe:not([hidden])")&&!document.getElementById("molecule-select").disabled&&document.querySelector(".molecule-stage").getAttribute("aria-busy")==="false"'
def inner(expr):return ev('document.querySelector("iframe").contentWindow.eval('+json.dumps(expr)+')')
def check_model(key,count):
 until(ready);until('document.querySelector("iframe").contentWindow.eval("selectedMol")==='+json.dumps(key))
 until('Number(document.querySelector("iframe").contentWindow.eval(\'Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count")\'))==='+str(count))
 assert inner('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG[data-label-error]")')
 out['checks'].append({'molecule':key,'3DAtoms':count,'has2DSVG':True,'hasMetrics':inner('!!window.NameleculeLabelMetrics')})
try:
 navigate('react-preview/dist/#/viewer');check_model('ethanol',9)
 assert ev('document.getElementById("molecule-results").textContent.includes("126")');out['checks'].append({'catalog126':True})
 ev('document.querySelector("input[name=mode][value=expanded]").click();true');until(ready);assert inner('mode2D')=='expanded'
 out['checks'].append({'ReactExpandedMode':True})
 ev('document.querySelectorAll(".molecule-views button")[1].click();true');until(ready);assert ev('document.getElementById("style-3d")!==null');out['checks'].append({'React3DView':True})
 ev('document.querySelectorAll(".molecule-views button")[0].click();true');until(ready)
 ev('document.getElementById("molecule-select").value="methane";document.getElementById("molecule-select").dispatchEvent(new Event("change",{bubbles:true}));true');check_model('methane',5)
 scripts=inner('JSON.stringify([...document.scripts].map(s=>s.src).filter(s=>s.includes("preserved-main-20261030")))');out['checks'].append({'pinnedScripts':json.loads(scripts)});assert len(json.loads(scripts))==2
 screenshot(HERE/('react-viewer-'+os.environ.get('NAMELECULE_EVIDENCE_SUFFIX','prefix')+'.png'))
 navigate('react-preview/dist/#/lesson/monoalcohols/step/1');until('!!document.querySelector(".lesson-stage iframe:not([hidden])")&&!document.getElementById("lesson-next").disabled')
 assert inner('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG[data-label-error]")')
 ev('document.getElementById("lesson-next").click();true');until('location.hash.endsWith("/step/2")&&!document.getElementById("lesson-prev").disabled&&!document.querySelector(".lesson-stage iframe").hidden')
 ev('document.getElementById("lesson-prev").click();true');until('location.hash.endsWith("/step/1")&&!document.querySelector(".lesson-stage iframe").hidden');out['checks'].append({'ReactLessonNextPrevious':True})
 ev('document.querySelector(".lesson-navigation a").click();true');until('location.hash==="#/library"');out['checks'].append({'ReactLessonExit':True});out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;out['allDiagnosticEntries']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['error','warn']]
 (HERE/('react-'+os.environ.get('NAMELECULE_EVIDENCE_SUFFIX','prefix')+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'jsErrors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
