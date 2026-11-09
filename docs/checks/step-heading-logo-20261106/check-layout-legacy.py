from pathlib import Path
import os,json,traceback,re
HERE=Path('docs/checks/step-heading-logo-20261106');meta=json.loads((HERE/'test-processes.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(meta['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[]}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS',label,flush=True)
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1#step=4');app_ready()
 until('MuLERMoCScenario.present&&fScenarioPresent().index===3&&!document.documentElement.classList.contains("lesson-loading")&&!!document.querySelector("#pageTitle .scStepHeadingVisual.is-loaded")')
 for width,height in [(390,844),(320,640),(844,390)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  ev('new Promise(r=>setTimeout(r,150))')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  until('getComputedStyle(document.getElementById("rotatePrompt")).display==="none"')
  ev('scrollTo(0,0);true')
  check(ev('(()=>{const e=document.querySelector("#pageTitle img"),b=e.getBoundingClientRect(),hit=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return e.contains(hit)&&b.width>0&&b.x>=0&&b.right<=innerWidth})()'),'Unobscured logo within viewport '+str(width))
  screenshot(HERE/('after-step4-clean-'+str(width)+'.png'))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 ev('window.testSavedHeadingStep=JSON.parse(JSON.stringify(fScenarioPresent().steps[3]));window.testLogoOnly=JSON.parse(JSON.stringify(testSavedHeadingStep));testLogoOnly.title="";testLogoOnly.note="";fScenarioFillStepPanel(testLogoOnly);true')
 until('!!document.querySelector("#pageTitle .scStepHeadingVisual.is-loaded")')
 check(ev('showTextOn(testLogoOnly)&&document.getElementById("pageTitle").textContent.trim()==="Συνεργείο ονομάτων"'),'Logo-only step remains visible and meaningfully named')
 ev('fScenarioFillStepPanel(testSavedHeadingStep);true')
 links=list(dict.fromkeys(re.findall(r'scenario=([^&]+)',Path('design/theory-library.html').read_text())))
 for name in links:
  original=json.loads(Path(name).read_text())
  result=json.loads(ev('JSON.stringify((()=>{const r=fScenarioValidate('+json.dumps(original,ensure_ascii=False)+');return{ok:r.ok,warnings:r.warnings.length,hasLogo:r.steps.some(s=>Object.prototype.hasOwnProperty.call(s,"titleLogo"))}})())'))
  check(result['ok'] and result['warnings']==0 and not result['hasLogo'],'Legacy import unchanged '+name)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors
 (HERE/'layout-legacy-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx});call('session.end',{})
 except Exception:pass
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
