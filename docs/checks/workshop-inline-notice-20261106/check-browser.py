from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/workshop-inline-notice-20261106')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'bounds':[]}
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS',name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def notice():return ev('!!document.querySelector("#scCheckpointNotice:not([hidden])")')
def attempt():ev('document.dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowRight",bubbles:true}));true')
def ready():
 app_ready();until('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")')
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=workshop-inline-notice-20261106-r1#step=4');ready()
 ev('window.initialFocus=document.activeElement;true');attempt()
 check(notice() and ev('fScenarioPresent().index===3'),'Right arrow produces lesson-local feedback without advancing')
 check(ev('document.querySelector("#scCheckpointNotice").parentNode===document.querySelector("#mainAppContainer>.mainApp3Columns")'),'Message belongs to former molecular space')
 check(ev('document.querySelector("#scCheckpointNotice").textContent')=='Λύσε το σύντομο κουίζ για να συνεχίσεις.','Original message preserved')
 check(ev('document.querySelector("#scCheckpointNotice").getAttribute("role")==="status"&&document.querySelector("#scCheckpointNotice").getAttribute("aria-live")==="polite"&&document.querySelector("#scCheckpointNotice").getAttribute("aria-atomic")==="true"'),'Accessible polite atomic status')
 check(ev('document.activeElement===initialFocus'),'Message does not move keyboard focus')
 check(ev('!document.querySelector("#scenarioToast").classList.contains("show")'),'No duplicate bottom toast')
 for width,height in [(1280,900),(390,844),(320,844),(1280,500)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});ev('new Promise(r=>setTimeout(r,150))')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  attempt()
  bounds=json.loads(ev('JSON.stringify((()=>{let n=document.getElementById("scCheckpointNotice").getBoundingClientRect(),r=document.querySelector("#mainAppContainer>.mainApp3Columns").getBoundingClientRect(),c=document.getElementById("creditsUs").getBoundingClientRect(),t=document.getElementById("scStepText").getBoundingClientRect();return{notice:{left:n.left,right:n.right,top:n.top,bottom:n.bottom},row:{top:r.top,bottom:r.bottom},note:{bottom:t.bottom},credits:{top:c.top},viewport:{width:innerWidth,height:innerHeight}}})())'))
  out['bounds'].append(bounds)
  n=bounds['notice'];check(0<=n['left']<n['right']<=width,'Message fits horizontal viewport '+str(width))
  check(n['top']>=43 and n['bottom']<=height,'Whole message is visible in viewport '+str(width)+'x'+str(height))
  check(n['top']>=bounds['note']['bottom'] and n['bottom']<=bounds['credits']['top'],'Message stays below instructions and above footer '+str(width))
  check(ev('!["viewerCol","analysisCol"].some(id=>document.getElementById(id).getClientRects().length)'),'Message does not restore molecular columns '+str(width))
  screenshot(HERE/('after-'+str(width)+'x'+str(height)+'.png'))
 # Keep original 2600ms lifetime; a repeated request owns a new timer.
 attempt();ev('new Promise(r=>setTimeout(r,1500))');attempt();ev('new Promise(r=>setTimeout(r,1500))')
 check(notice(),'Repeated attempt resets timer without early dismissal')
 ev('new Promise(r=>setTimeout(r,1250))')
 check(not notice() and ev('document.querySelector("#scCheckpointNotice").textContent===""'),'Expired status is hidden and emptied')
 attempt();ev('fScenarioToast("ordinary notice");true')
 check(not notice() and ev('document.querySelector("#scenarioToast").classList.contains("show")'),'Ordinary toast replaces inline notice cleanly')
 attempt();check(notice() and ev('!document.querySelector("#scenarioToast").classList.contains("show")'),'Inline notice replaces ordinary toast cleanly')
 ev('fScenarioGo(2);true');until('fScenarioPresent().index===2')
 check(not notice(),'Previous step clears inline message')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3');check(not notice(),'Returning to stop has no stale message')
 ev('location.hash="step=5";true');until('location.hash==="#step=4"')
 check(notice() and ev('fScenarioPresent().index===3'),'Blocked hash navigation uses the same local feedback')
 ev('fScenarioExitPresent();true')
 check(not notice() and ev('!MuLERMoCScenario.present'),'Exit clears inline feedback')
 ev('fScenarioPresentBegin(fScenarioActive().id,3);true');ready();check(not notice(),'Presentation reentry does not restore stale feedback')
 ev('fScenarioGo(4);true');check(notice(),'Direct blocked Go uses local feedback')
 ev('window.testTranslate=fMulerTByGr;fMulerTByGr=()=>"Translated notice";fScenarioGo(4);fMulerTByGr=testTranslate;true')
 check(ev('document.querySelector("#scCheckpointNotice").textContent')=='Translated notice','Existing translation mechanism retained')
 ev('window.testMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(h,o){window.testRound=JSON.parse(JSON.stringify(o.round));return testMount(h,o)};true')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testRound')
 for ri in range(3):
  d=json.loads(ev('JSON.stringify(testRound)'))
  if d['kind']=='replace':
   click('[id$="-part-'+d['targetPartId']+'"]');idx=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue']);click('[id$="-choice-'+str(idx)+'"]')
  else:click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]')
  if ri==2:ev('fScenarioGo(4);true');check(notice(),'Notice shown immediately before final answer')
  click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
  if ri==2:check(not notice() and not ev('document.querySelector("#scNext").disabled'),'Correct completion immediately clears notice and unlocks')
  click('.round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testRound.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
 check(not notice() and ev('document.getElementById("viewerCol").getClientRects().length>0'),'Step5 has no feedback leak and restores its molecule')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1#step=4');ready();attempt()
 check(not notice() and ev('document.getElementById("scenarioToast").classList.contains("show")'),'Legacy molecular checkpoint keeps ordinary toast')
 check(ev('getComputedStyle(document.getElementById("scenarioToast")).position==="fixed"&&getComputedStyle(document.getElementById("scenarioToast")).bottom==="16px"'),'Ordinary toast retains fixed bottom placement')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
