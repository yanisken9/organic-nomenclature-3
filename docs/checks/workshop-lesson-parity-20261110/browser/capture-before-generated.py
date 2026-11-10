from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
BASE_CAPTURE=json.loads((H/'before-attempt2-generated-selector.json').read_text())
OUT['checks']=BASE_CAPTURE['checks'];OUT['measurements']=BASE_CAPTURE['measurements'];OUT['beforeWrongPart']=BASE_CAPTURE['beforeWrongPart'];OUT['beforeNoReveal']=BASE_CAPTURE['beforeNoReveal'];OUT['priorCapture']='before-attempt2-generated-selector.json'
try:
 source_guard();viewport(1280,800);direct(True);geometry('generated-basic-entry',1280);click('.part-button');OUT['generatedWrongPart']=ev('document.querySelector(".part-selection-status").textContent');shot('generated-basic-wrongpart')
 ev('sessionStorage.clear();true');direct(True,'alkanes-branched','challenge');geometry('generated-challenge-entry',1280);OUT['challengeObjective']=ev('document.querySelector(".round-objective").textContent');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
finally:finish()
if not OUT['completed']:raise SystemExit(1)
