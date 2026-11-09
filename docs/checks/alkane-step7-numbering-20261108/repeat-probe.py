from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/alkane-step7-numbering-20261108');os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=step7-numbering-directions-20261108-r1');app_ready();until('fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();document.querySelector(\'.scenarioPanel.active .srow[data-idx="6"] .scPresentStep\').click();true')
 until('MuLERMoCScenario.present&&fScenarioPresent().index===6&&!!document.getElementById("scNumberingRight")',seconds=12)
 until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===4',seconds=10)
 out['before']=json.loads(ev('JSON.stringify({chain:mainChainAtomsList,name:currentMolName,numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(e=>({text:e.textContent,x:e.getAttribute("x")})),choices:fEquivalentParentNumberingDirections(jsmeNomeclatureApplet.molFile(),mainChainAtomsList,allAtomsTypeList,bondList)})'))
 screenshot(HERE/'initial-left.png');ev('document.getElementById("scNumberingRight").click();true')
 out['after']=json.loads(ev('JSON.stringify({chain:mainChainAtomsList,name:currentMolName,numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(e=>({text:e.textContent,x:e.getAttribute("x")})),direction:MuLERMoCScenario.numberingDirection.direction})'));screenshot(HERE/'repeat-right.png');out['firstMol']=ev('jsmeNomeclatureApplet.molFile()');ev('document.getElementById("scNumberingRight").click();true');ev('new Promise(resolve=>setTimeout(()=>resolve(true),1100))');out['secondMol']=ev('jsmeNomeclatureApplet.molFile()');out['repeat']=json.loads(ev('JSON.stringify({mode:nameAnalysisMode,flag:numberingFlag,chain:mainChainAtomsList,direction:MuLERMoCScenario.numberingDirection.direction,numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(e=>({text:e.textContent,x:e.getAttribute("x")}))})'));out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:
  out['guardDiagnostic']=json.loads(ev('JSON.stringify({present:MuLERMoCScenario.present,step:fScenarioPresent().index,mode:nameAnalysisMode,chain:mainChainAtomsList,types:allAtomsTypeList,bonds:bondList,mol:jsmeNomeclatureApplet.molFile(),parsed:fParseMolV2000(jsmeNomeclatureApplet.molFile())})'));screenshot(HERE/'probe-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'repeat-probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps(out,ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
