"""Compare approved Main compact padding against legacy fitting in real Firefox.
Artifacts are written only under /tmp; no chemistry/model mutation.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0], 'existing-bidi-harness', 'exec'))
folder=Path('/tmp/namelecule-name-font-20261028');folder.mkdir(exist_ok=True)
result={'completed':False,'cases':[]}
measure="""(()=>{const h=document.querySelector('#nameAnalysis .nameContainer'),r=h.querySelector('.nameCompContainer'),b=[...r.querySelectorAll('.nameCompBox')];const s=getComputedStyle(h);return JSON.stringify({font:parseFloat(getComputedStyle(b[0]).fontSize),width:r.getBoundingClientRect().width,available:h.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight)-4,tight:r.classList.contains('nl-name-tight'),padding:getComputedStyle(b[0]).paddingLeft,lines:[...new Set(b.map(e=>Math.round(e.getBoundingClientRect().top)))].length,ids:b.map(e=>e.id),labels:b.map(e=>e.textContent)})})()"""
try:
 navigate('mulermoc-nom-52.html?scenario=scenarios/saturated-monocarboxylic-acids-nomenclature.scenario.json&present=1&from=theory-library&v=name-font-test')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready()
 ev('document.fonts.ready.then(()=>true)')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7)
  if width==390:ev("document.getElementById('rotatePromptDismiss').click();true")
  # Real lesson navigation, including long/short and staged hidden labels.
  for step in range(28):
   ev('fScenarioGo('+str(step)+');true');time.sleep(.12)
   ev("document.documentElement.dataset.nameleculeCompactNamePadding='false';fFitNameToWidth();true")
   old=json.loads(ev(measure))
   ev("document.documentElement.dataset.nameleculeCompactNamePadding='true';fFitNameToWidth();true")
   new=json.loads(ev(measure))
   assert old['ids']==new['ids'] and old['labels']==new['labels'],(step,old,new)
   assert new['width']<=new['available']+.1 and new['lines']==1,(width,step,new)
   assert new['font']>=old['font']-.01,(width,step,old,new)
   if not old['tight'] and old['font']==17.6:assert not new['tight'],(width,step,new)
   result['cases'].append(dict(width=width,step=step+1,before=old,after=new))
  ev('fScenarioGo(24);true');time.sleep(.3)
  screenshot(str(folder/('step25-'+str(width)+'.png')))
  # Existing settings controls: boxes, plus separators, and eye editor.
  for control in ['nameStyleBoxToggle','nameStyleBoxToggle','nameStyleCrossToggle','nameStyleEyeToggle','nameStyleEyeToggle','nameStyleCrossToggle']:
   ev('document.getElementById('+json.dumps(control)+').click();true');time.sleep(.15);ev('fFitNameToWidth();true')
   actual=json.loads(ev(measure));assert actual['width']<=actual['available']+.1 and actual['lines']==1,(control,actual)
  ev('fScenarioGo(0);true');time.sleep(.3)
  assert not json.loads(ev(measure))['tight'],'Tight padding must reset for a short name'
 # Same content without Main opt-in keeps original 6px padding and font.
 ev('fScenarioGo(24);true');time.sleep(.3)
 ev("delete document.documentElement.dataset.nameleculeCompactNamePadding;fFitNameToWidth();true")
 legacy=json.loads(ev(measure));assert not legacy['tight'] and legacy['padding']=='6px',legacy
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'errors':len(js_errors)}),flush=True)
