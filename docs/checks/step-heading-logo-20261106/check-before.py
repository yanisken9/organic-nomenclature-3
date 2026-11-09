from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/step-heading-logo-20261106')
meta=json.loads((HERE/'test-processes.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(meta['bidi_port'])
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:'+str(meta['baseline_port'])+'/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1#step=4')
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent()&&fScenarioPresent().index===3&&!document.documentElement.classList.contains("lesson-loading")')
 out['title']=ev('document.getElementById("pageTitle").textContent.trim()')
 out['headingImages']=ev('document.getElementById("pageTitle").querySelectorAll("img").length')
 assert out['title']=='logo' and out['headingImages']==0,out
 screenshot(HERE/'before-step4.png')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors
 (HERE/'before-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx});call('session.end',{})
 except Exception:pass
 print(json.dumps(out,ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
