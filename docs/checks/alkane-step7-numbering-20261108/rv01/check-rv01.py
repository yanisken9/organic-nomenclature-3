from pathlib import Path
import json,os,sys,traceback
HERE=Path('docs/checks/alkane-step7-numbering-20261108/rv01');mode=sys.argv[1];os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'mode':mode,'completed':False,'checks':[],'observations':[]}
def check(value,label):assert value,label;out['checks'].append(label);print('PASS '+label,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def snap(label):
 value=json.loads(ev('JSON.stringify({state:MuLERMoCScenario.numberingDirection&&MuLERMoCScenario.numberingDirection.direction,left:document.getElementById("scNumberingLeft")?.getAttribute("aria-pressed"),right:document.getElementById("scNumberingRight")?.getAttribute("aria-pressed"),numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].sort((a,b)=>Number(a.getAttribute("x"))-Number(b.getAttribute("x"))).map(e=>Number(e.textContent)),chain:mainChainAtomsList,name:currentMolName})'));value['label']=label;out['observations'].append(value);return value
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=rv01-'+mode);app_ready();until('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")')
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true');click('.scenarioPanel.active .srow[data-idx="6"] .scPresentStep');until('MuLERMoCScenario.present&&!!document.getElementById("scNumberingRight")');click('#scNumberingRight');a=snap('Right before Update');check(a['state']=='right' and a['right']=='true' and a['numbers']==[4,3,2,1],'Right choice starts consistent')
 ev('fScenarioUpdateStep(fScenarioPresent().id,6);true');snap('After Update before repaint');click('#zoomInBtn');b=snap('After actual zoom')
 if mode=='before':check(b['state']=='left' and b['right']=='true' and b['numbers']==[1,2,3,4],'RV01 reproduced in actual Firefox: left labels while right button stays pressed');screenshot(HERE/'before-mismatch.png')
 else:
  check(b['state']=='right' and b['right']=='true' and b['left']=='false' and b['numbers']==[4,3,2,1],'Update then zoom keeps selected direction and labels consistent')
  for width,height in [(390,760),(320,700),(1500,1000)]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
   if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
   until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===4');c=snap('Update then resize'+str(width));check(c['state']=='right' and c['right']=='true' and c['numbers']==[4,3,2,1],'Update then resize remains consistent '+str(width))
  screenshot(HERE/'after-consistent.png');click('#scNumberingLeft');ev('fScenarioUpdateStep(fScenarioPresent().id,6);true');click('#zoomOutBtn');d=snap('Left Update zoomout');check(d['state']=='left' and d['left']=='true' and d['right']=='false' and d['numbers']==[1,2,3,4],'Left choice also stays consistent after Update and zoom')
  click('#scNumberingRight');ev('fScenarioExitPresent();fScenarioSetAuthoring(true);true');click('.scenarioPanel.active .srow[data-idx="6"] .scPresentStep');until('!!document.getElementById("scNumberingLeft")&&document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===4');e=snap('Fresh step entry');check(e['state']=='left' and e['left']=='true' and e['numbers']==[1,2,3,4],'True step reentry retains required reset')
  ev('fScenarioExitPresent();true');check(ev('MuLERMoCScenario.numberingDirection===null&&!document.getElementById("scNumberingDirection")'),'Exit still clears transient state')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/(mode+'-failure.png'))
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/(mode+'-browser.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
