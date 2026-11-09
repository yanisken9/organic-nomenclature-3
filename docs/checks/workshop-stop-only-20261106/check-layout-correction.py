from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/workshop-stop-only-20261106')
OUT=HERE/'revision2';OUT.mkdir(exist_ok=True)
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'bounds':[]}
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS',name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def visible(id):return ev('document.getElementById('+json.dumps(id)+').getClientRects().length>0')
def clean():return ev('document.querySelector("#pageContainer").classList.contains("scContentOnly")&&["viewerCol","analysisCol","jsmeNomeclatureSVG","nomeclature3D"].every(id=>!document.getElementById(id).getClientRects().length)')
def ready():
 app_ready();until('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")')
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=workshop-stop-only-20261106-r2#step=4');ready()
 until('!!document.querySelector("#pageTitle .scStepHeadingVisual.is-loaded")')
 check(clean(),'Workshop-only presentation uses content layout')
 for width,height in [(320,844),(390,844),(1280,900)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});ev('new Promise(r=>setTimeout(r,200))')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  bounds=json.loads(ev('JSON.stringify(Object.fromEntries(["authorLayout","scStepText","nlQuizCheckpoint","nlQuizOpen"].map(id=>{let e=document.getElementById(id),r=e.getBoundingClientRect();return[id,{left:r.left,right:r.right,width:r.width,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth}]})))'))
  out['bounds'].append({'viewport':width,'boxes':bounds})
  check(all(0<=v['left']<v['right']<=width for v in bounds.values()),'Entire host, instructions, card and button fit '+str(width))
  check(bounds['scStepText']['scrollWidth']<=bounds['scStepText']['clientWidth'],'No horizontal text overflow '+str(width))
  check(clean(),'Resize preserves Workshop-only columns '+str(width))
  screenshot(OUT/('after-'+str(width)+'.png'))
 ev('fScenarioGo(2);true');until('fScenarioPresent().index===2')
 check(ev('!document.querySelector("#pageContainer").classList.contains("scContentOnly")') and visible('viewerCol') and visible('analysisCol'),'Step3 restores normal column layout')
 check(ev('!!document.querySelector("#scStepText").style.getPropertyValue("--scStepTextFitWidth")'),'Step3 retains measured text width')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 check(clean(),'Step3→4 restores content-only layout')
 ev('window.probeStep=fScenarioPresent().steps[3];probeStep.show.rule=true;fScenarioChrome(probeStep.show);true')
 check(visible('analysisCol') and ev('!document.querySelector("#pageContainer").classList.contains("scContentOnly")'),'Effective content restores normal sizing')
 ev('probeStep.show.rule=false;fScenarioChrome(probeStep.show);true')
 check(clean(),'Removing temporary rule restores correct host sizing')
 ev('fScenarioExitPresent();true')
 check(ev('!MuLERMoCScenario.present&&!document.querySelector("#pageContainer").classList.contains("scContentOnly")') and visible('viewerCol') and visible('analysisCol'),'Exit removes content layout and restores authoring columns')
 ev('fScenarioPresentBegin(fScenarioActive().id,3);true');ready()
 check(clean(),'Reentry restores Workshop-only layout')
 ev('window.testMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(h,o){window.testRound=JSON.parse(JSON.stringify(o.round));return testMount(h,o)};true')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testRound')
 check(ev('document.querySelector("#scNext").disabled'),'Quiz opens and remains locked')
 for ri in range(3):
  d=json.loads(ev('JSON.stringify(testRound)'))
  if d['kind']=='replace':
   click('[id$="-part-'+d['targetPartId']+'"]');idx=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue']);click('[id$="-choice-'+str(idx)+'"]')
  else:click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]')
  click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector("#scNext").disabled')==(ri<2),'Gate after repair '+str(ri+1))
  click('.round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testRound.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
 check(ev('!document.querySelector("#pageContainer").classList.contains("scContentOnly")') and visible('viewerCol') and visible('analysisCol'),'Step5 after real quiz restores molecular layout')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 check(clean() and not ev('document.querySelector("#scNext").disabled'),'Completed stop stays clean and unlocked')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1#step=4');ready()
 check(ev('!document.querySelector("#pageContainer").classList.contains("scContentOnly")') and visible('viewerCol') and visible('analysisCol'),'Canonical lesson does not acquire content-only layout')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(OUT/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (OUT/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
