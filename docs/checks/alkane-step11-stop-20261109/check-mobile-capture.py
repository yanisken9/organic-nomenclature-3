from pathlib import Path
import json,os,base64
HERE=Path('docs/checks/alkane-step11-stop-20261109')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=step11-mobile-capture-20261109');app_ready();until('fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")',45)
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();document.querySelector(\'.scenarioPanel.active .srow[data-idx="10"] .scPresentStep\').click();true')
 until('MuLERMoCScenario.present&&fScenarioPresent().index===10&&!!document.querySelector("#pageTitle img")&&document.querySelector("#pageTitle img").complete',12)
 for width,height in [(390,760),(320,700)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  ev('window.scrollTo(0,0);new Promise(resolve=>setTimeout(()=>resolve(true),150))')
  screenshot(HERE/('after-step11-mobile-top-document-'+str(width)+'.png'))
  r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/('after-step11-mobile-top-viewport-'+str(width)+'.png')).write_bytes(base64.b64decode(r['data']))
 print('Captured top-of-document and viewport screenshots; separate author-preview screenshot capture only, learner gates covered in browser-after.json')
finally:
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
