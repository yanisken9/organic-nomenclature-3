"""Actual2Dcontrols/new-prefix replay in the lesson, and visible acid card."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
folder=Path('/tmp/namelecule-monoacids-lesson-20261028');result={'completed':False,'cases':[]}
try:
 navigate('design/theory-library.html?v=monoacid-controls')
 ev("document.getElementById('carboxylic-acids-card').scrollIntoView({block:'center'});true");time.sleep(1)
 assert ev("(()=>{const e=document.getElementById('carboxylic-acids-card');return Number(getComputedStyle(e).opacity)>.99&&e.textContent.includes('28 βήματα')})()")
 screenshot(str(folder/'acid-card-desktop.png'))
 ev("document.querySelector('a[href*=saturated-monocarboxylic-acids]').click();true")
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();until('!!window.JSmolReadyFlag')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7)
  if width==390:ev("document.getElementById('rotatePromptDismiss').click();true")
  for step,mode in [(6,'none'),(23,'compAcidNumber3'),(24,'compAcidSub3')]:
   ev('fScenarioGo('+str(step)+');true');until('nameAnalysisMode==='+json.dumps(mode),seconds=15)
   for i,form in enumerate(['condensed','expanded','skeletal']):
    ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click();true');until('mode2D==='+json.dumps(form),seconds=10)
    assert ev('nameAnalysisMode')==mode
    if mode!='none':assert ev("fScenarioCompIdFor(nameAnalysisMode)!==null&&getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
    assert ev("(()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),r=s.getBoundingClientRect();return [...s.querySelectorAll('text')].every(e=>{const b=e.getBoundingClientRect();return b.left>=r.left-1&&b.right<=r.right+1&&b.top>=r.top-1&&b.bottom<=r.bottom+1})})()")
    # Capture/apply preserves new modes in each supported 2D form.
    if mode!='none':
     ev('window.__testCapture=fScenarioCapture();fScenarioApply(__testCapture);true');until('mode2D==='+json.dumps(form)+'&&nameAnalysisMode==='+json.dumps(mode),seconds=15)
    result['cases'].append(dict(width=width,step=step+1,form=form,mode=mode))
 navigate('design/theory-library.html?v=monoacid-card-narrow')
 ev("document.getElementById('carboxylic-acids-card').scrollIntoView({block:'center'});true");time.sleep(1)
 assert ev('document.documentElement.scrollWidth<=innerWidth');screenshot(str(folder/'acid-card-narrow.png'))
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'controls.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'errors':len(js_errors)}),flush=True)
