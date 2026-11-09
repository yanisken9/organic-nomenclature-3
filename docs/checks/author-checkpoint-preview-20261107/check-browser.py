from pathlib import Path
import os,json,copy,traceback
HERE=Path('docs/checks/author-checkpoint-preview-20261107')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text())
games={g['seed']:{s['id']:s for s in g['sets']} for g in fixtures}
reminders={
 'parent-length':'Η αποστολή αφορά το πλήθος των ατόμων C της κύριας αλυσίδας.',
 'bond-type':'Η αποστολή αφορά το είδος των δεσμών μεταξύ ατόμων C.',
 'branch-locants':'Η αποστολή αφορά τις θέσεις σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
 'branch-multiplier':'Η αποστολή αφορά το πλήθος των ίδιων διακλαδώσεων.'}
out={'completed':False,'checks':[],'rounds':[],'fixture_policy':'Owned profile only. Actual learner partial progress and temporary preview completions created through UI; no fabricated solved receipts. Title changed only in isolated browser; no source/desktop JSON writes.','limitations':['Headless isolated Firefox; no user-facing Firefox freeze diagnosis','No Safari, physical mobile, screen reader or full conference sequence audit','No new viewer/3D audit; existing JSmol issue remains outside scope']}
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS '+name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('''window.testReceiptInfo=function(){const s=fScenarioPresent();const content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16);return {key,content,record:JSON.parse(sessionStorage.getItem(key)||"null")}};window.testOriginalMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.testMounted=JSON.parse(JSON.stringify(options.round));return testOriginalMount(host,options)};true''')
def reload():
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def seed(index,value):
 ev('(()=>{const i=testReceiptInfo();const r=i.record||{version:1,content:i.content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(i.key,JSON.stringify(r));return true})()');reload()
def open_quiz():
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testMounted',seconds=45)
def mounted():return json.loads(ev('JSON.stringify(testMounted)'))
def state(index):return json.loads(ev('JSON.stringify(testReceiptInfo().record.states['+str(index)+'])'))
def stable_progress(value):
 result=copy.deepcopy(value)
 # Existing adapter intentionally resets unvisited later rounds; their random
 # choice order is not an answered/current selection or completion receipt.
 for i,s in enumerate(result['states']):
  if i>result['currentRound'] and s and not s['solved'] and s['attempts']==0 and s['selectedPartId'] is None:
   s['choiceOrder']=[]
 return result
def message():return ev('document.querySelector("#nlQuizDialog .part-selection-status").textContent')
def pointer(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});true')
 pos=json.loads(ev('JSON.stringify((()=>{const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})())'))
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'feedback-mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':pos['x'],'y':pos['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def solve(round):
 if round['kind']=='replace':
  click('[id$="-part-'+round['targetPartId']+'"]');i=next(i for i,c in enumerate(round['choices']) if c['value']==round['correctValue']);click('[id$="-choice-'+str(i)+'"]')
 else:
  click('[id$="-part-'+round['correctOrder'][0]+'"]');click('[id$="-move-left"]')
 click('[id$="-check-button"]');until('!!document.querySelector("#nlQuizDialog .feedback.is-success")')

def storage():
 return json.loads(ev('JSON.stringify(Object.fromEntries(Object.keys(sessionStorage).filter(k=>k.startsWith("namelecule:lesson-checkpoints:")).map(k=>[k,sessionStorage.getItem(k)])))'))
def editor():
 ev('fScenarioSetAuthoring(true);if(!document.querySelector(".scenarioPanel.active .scenarioDrawer.open"))document.querySelector(".scenarioPanel.active .scList").click();true')
def screen(index):
 click('.scenarioPanel.active .srow[data-idx="'+str(index)+'"] .scPresentStep')
 until('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation')
def native_key(key):
 call('browsingContext.activate',{'context':ctx})
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'author-preview-keyboard','actions':[{'type':'keyDown','value':key},{'type':'keyUp','value':key}]}]})

try:
 # A real saved learner answer supplies the isolation baseline.
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=author-step-preview-20261107-r1#step=4');ready()
 check(ev('fScenarioPresent().index===3&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&document.getElementById("scNext").disabled'),'Ordinary learner gate still blocks at step4')
 open_quiz();d=mounted();solve(d);click('#nlQuizDialog .round-next button')
 until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']))
 click('#nlQuizBack');learner_storage=storage()
 check(len(learner_storage)==1 and state(3)['currentRound']==1,'Real first learner repair is stored without unlocking the three-round gate')
 click('#scExit');until('!MuLERMoCScenario.present');editor()
 original_steps=ev('JSON.stringify(fScenarioActive().steps)')
 # The actual inline change handler represents the user's edited step.
 ev('const input=document.querySelector(".scenarioPanel.active .srow:nth-child(5) .scStepTitle");input.value+=" [έλεγχος συγγραφέα]";input.dispatchEvent(new Event("change",{bubbles:true}));true')
 edited_steps=ev('JSON.stringify(fScenarioActive().steps)')
 screen(4)
 check(ev('fScenarioPresent().index===4&&location.hash==="#step=5"&&NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Screen opens edited step5 directly despite unsolved step4')
 check(ev('document.getElementById("pageTitle").textContent.includes("[έλεγχος συγγραφέα]")&&document.getElementById("scPos").textContent.includes("Δοκιμή")'),'Edited title and explicit preview counter shown')
 check(ev('!document.getElementById("scNext").disabled&&document.getElementById("comp6").getAttribute("aria-disabled")==="true"&&!!document.getElementById("scChainNavigation")'),'Step5 keeps authored passive boxes and chain selector; preview Next enabled')
 screenshot(HERE/'preview-step5.png')
 click('#scNext');check(ev('fScenarioPresent().index===5'),'Preview Next advances directly to6')
 ev('window.testKeys=[];document.addEventListener("keydown",e=>testKeys.push({key:e.key,trusted:e.isTrusted,target:e.target.tagName}),true);document.getElementById("scNext").focus();true');native_key('\ue012')
 try:until('fScenarioPresent().index===4',seconds=3)
 except AssertionError:pass
 out['native_keyboard_probe']=json.loads(ev('JSON.stringify({events:testKeys,index:fScenarioPresent().index,focus:document.hasFocus(),active:document.activeElement.tagName,noteEditorOpen:fScenarioNoteEditorIsOpen()})'))
 if ev('fScenarioPresent().index!==4'):
  assert not out['native_keyboard_probe']['events'],out['native_keyboard_probe']
  out['limitations'].append('Native ArrowLeft unverified: headless endpoint delivered no keydown. Actual document handler exercised with synthetic KeyboardEvent.')
  ev('document.getElementById("scNext").dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowLeft",bubbles:true}));true')
 check(ev('fScenarioPresent().index===4'),'ArrowLeft document route returns preview to5')
 ev('location.hash="#step=12";true');until('fScenarioPresent().index===11')
 check(ev('NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Preview hash crosses both unsolved quiz gates')
 click('#scPrev');check(ev('fScenarioPresent().index===10&&!document.getElementById("scNext").disabled'),'Preview step11 quiz is optional for navigation')
 click('#scNext');check(ev('fScenarioPresent().index===11'),'Preview can continue beyond optional quiz11')
 for width in [390,320]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':844},'devicePixelRatio':1})
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  check(ev('(()=>{const b=document.getElementById("scPos").getBoundingClientRect();return b.left>=0&&b.right<=innerWidth})()'),'Preview counter fits '+str(width)+'px')
  screenshot(HERE/('preview-'+str(width)+'.png'))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 # Solve the preview set for real; its completion must never enter learner storage.
 ev('fScenarioGo(3);true');open_quiz()
 for ri in range(3):
  d=mounted();solve(d);click('#nlQuizDialog .round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Preview quiz can actually be completed in temporary state')
 check(storage()==learner_storage,'Full preview completion leaves every learner storage byte unchanged')
 check(ev('JSON.stringify(fScenarioPresent().steps)')==edited_steps,'Preview/navigation/quiz do not add state or flags to authored steps')
 click('#scExit');until('!MuLERMoCScenario.present')
 check(ev('MuLERMoCScenario.authoring&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&!document.getElementById("nlQuizDialog").open'),'Exit clears preview, closes quiz and returns to editor')
 screen(4);ev('fScenarioGo(3);true')
 check(ev('!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&!document.getElementById("scNext").disabled'),'Reopening preview starts fresh temporary progress')
 click('#scExit');until('!MuLERMoCScenario.present');editor()
 click('.scenarioPanel.active .scPresent');until('MuLERMoCScenario.present')
 check(ev('fScenarioPresent().index===0&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&!document.getElementById("scPos").textContent.includes("Δοκιμή")'),'Card Play uses learner mode at step1 after preview')
 ev('fScenarioGo(4);true');until('!MuLERMoCScenario.checkpointPreparation')
 check(ev('fScenarioPresent().index===3&&document.getElementById("scNext").disabled'),'Normal card Play cannot pass unsolved quiz4')
 check(storage()==learner_storage,'Preview/Exit/cardPlay never overwrite original learner receipt')
 click('#scExit');until('!MuLERMoCScenario.present');editor()
 # In-memory failure: no file edits, and restore the original function immediately.
 ev('window.testApply=fScenarioApply;fScenarioApply=()=>false;true');click('.scenarioPanel.active .srow[data-idx="4"] .scPresentStep')
 ev('fScenarioApply=testApply;true')
 check(ev('!MuLERMoCScenario.present&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Failed launch invalidates preview context and returns author mode')
 screen(4)
 ev('window.testOld=fScenarioPresent();window.testNew=fScenarioNew("isolated-preview-context-check",true);true')
 check(ev('!NameleculeQuizCheckpoints.isPreview(testOld)&&!NameleculeQuizCheckpoints.isPreview(testNew)'),'New/import card path invalidates old scenario preview')
 # Normal fresh library load must recover the original partial learner progress.
 navigate('design/theory-library.html?v=author-step-preview-20261107-r1');click('article[aria-labelledby=alkanes-title] a.action');ready()
 ev('location.hash="#step=5";true');until('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&document.getElementById("scNext").disabled'),'Library/manual hash still enforces normal first gate')
 normal_loaded=storage();raw_before=json.loads(next(iter(learner_storage.values())));raw_loaded=json.loads(next(iter(normal_loaded.values())))
 check(set(normal_loaded)==set(learner_storage) and raw_loaded['content']==raw_before['content'] and stable_progress(raw_loaded['states']['3'])==stable_progress(raw_before['states']['3']),'Normal receipt preparation preserves answers/counters/seed and content identity')
 out['normal_prepare_observation']={'before':raw_before,'after':raw_loaded,'exact_bytes':normal_loaded==learner_storage,'existing_policy':'Unchanged adapter resets unvisited future round choiceOrder during normal prepare/open; preview bytes checked strictly before normal restoration.'}
 open_quiz();restored=state(3);before_record=raw_before['states']['3']
 check(restored['currentRound']==1 and stable_progress(restored)==stable_progress(before_record),'Original learner answers/current selection/counters restore after rehearsal')
 out['normal_reopen_observation']={'before':before_record,'after':restored,'exact_storage_before_normal_restore':True,'future_unvisited_choice_order_policy':'Existing unchanged generated adapter recreates unvisited future choice orders on normal open; those are not answered progress.'}
 for ri in [1,2]:
  d=mounted();solve(d);click('#nlQuizDialog .round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
 ev('fScenarioGo(11);true');until('fScenarioPresent().index===10&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('document.getElementById("scNext").disabled&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Normal learner also stops at second unsolved gate11 after completing first set')
 click('#scExit');until('location.pathname.endsWith("/design/theory-library.html")')
 check(ev('!!document.querySelector("article[aria-labelledby=alkanes-title]")'),'Normal library Exit keeps existing return route')
 # Reloading an editor rehearsal drops its RAM context; URL flag alone is ignored.
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=author-step-preview-20261107-r1');ready();editor();screen(4)
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
 check(ev('!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&!MuLERMoCScenario.present'),'Reload carries no preview context or learner completion')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&preview=1#step=12');ready()
 check(ev('fScenarioPresent().index===10&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Invented preview URL cannot bypass remaining learner gate11')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=author-step-preview-20261107-r1');ready();editor()
 ev('window.testClicks=[];document.addEventListener("click",e=>{if(e.target.closest(".scPresentStep"))testClicks.push({trusted:e.isTrusted})},true);true')
 pointer('.scenarioPanel.active .srow[data-idx="4"] .scPresentStep');until('MuLERMoCScenario.present')
 check(ev('fScenarioPresent().index===4&&testClicks.some(e=>e.trusted)'),'Real pointer activates editor screen and opens step5 directly')
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
