from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/author-checkpoint-preview-20261107/ap01')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'bounds':[],'scope':'AP-01 compact preview label only; prior 30-flow browser run preserved separately'}
def check(ok,label):
 assert ok,label
 out['checks'].append(label);print('PASS '+label,flush=True)
def pointer(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});true')
 r=json.loads(ev('JSON.stringify((()=>{const e=document.querySelector('+json.dumps(selector)+'),b=e.getBoundingClientRect();return{x:Math.round(b.x+b.width/2),y:Math.round(b.y+b.height/2),hit:e.contains(document.elementFromPoint(b.x+b.width/2,b.y+b.height/2))}})())'))
 assert r['hit'],(selector,r)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'layout-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':r['x'],'y':r['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=author-step-preview-20261107-r2')
 app_ready();until('fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();window.testPointer=[];document.addEventListener("click",e=>{if(e.target.closest("#scPrev,#scNext,#scExit"))testPointer.push({id:e.target.closest("button").id,trusted:e.isTrusted})},true);true')
 for width in [1500,390,320]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
  pointer('.scenarioPanel.active .srow[data-idx="4"] .scPresentStep');until('MuLERMoCScenario.present')
  ev('fScenarioGo(11);true')
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':844},'devicePixelRatio':1})
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':pointer('#rotatePromptDismiss')
  d=json.loads(ev('JSON.stringify((()=>{const ids=["scPrev","scPos","scNext","scExit"];return Object.fromEntries(ids.map(id=>{const e=document.getElementById(id),b=e.getBoundingClientRect();return[id,{left:b.left,right:b.right,top:b.top,bottom:b.bottom,hit:e.contains(document.elementFromPoint((b.left+b.right)/2,(b.top+b.bottom)/2))}]}))})())'))
  out['bounds'].append({'width':width,'elements':d})
  separated=all(max(a['left'],b['left'])>=min(a['right'],b['right']) or max(a['top'],b['top'])>=min(a['bottom'],b['bottom']) for i,a in enumerate(d.values()) for b in list(d.values())[i+1:])
  check(separated and all(x['left']>=0 and x['right']<=width and x['hit'] for x in d.values()),'Counter/Prev/Next/Exit fully separated and hittable '+str(width))
  screenshot(HERE/('preview-'+str(width)+'.png'))
  pointer('#scPrev');check(ev('fScenarioPresent().index===10'),'Real pointer Prev reaches optional quiz11 '+str(width))
  pointer('#scNext');check(ev('fScenarioPresent().index===11'),'Real pointer Next returns12 '+str(width))
  pointer('#scExit');check(ev('!MuLERMoCScenario.present&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Real pointer Exit returns editor '+str(width))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 ev('document.querySelector(".scenarioPanel.active .scPresent").click();fScenarioGo(4);true')
 check(ev('fScenarioPresent().index===3&&document.getElementById("scNext").disabled&&!document.querySelector("#scPos .scAuthorPreviewLabel")&&!document.getElementById("scPos").classList.contains("scAuthorPreview")'),'Compact label removed and ordinary learner gate preserved')
 check(ev('testPointer.length===9&&testPointer.every(e=>e.trusted)'),'All nine navigation/Exit pointer clicks trusted')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'layout-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
