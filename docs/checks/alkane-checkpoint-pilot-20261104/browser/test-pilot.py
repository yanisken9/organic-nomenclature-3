"""Developer: actual Firefox isolated-tab checkpoint journey, not a unit DOM double."""
from pathlib import Path
import os,json,time,traceback
os.environ['NAMELECULE_BIDI_PORT']='9244'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
HERE=Path('docs/checks/alkane-checkpoint-pilot-20261104/browser')
PILOT='mulermoc-nom-54.html?scenario=scenarios/alkanes-name-repair-pilot.scenario.json&present=1'
ROUND=next(r for r in json.loads(Path('games/data/name-repair-alkanes.json').read_text())['rounds'] if r['id']=='parent-not-total')
out={'completed':False,'checks':[]}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS',len(out['checks']),label,flush=True)
def click(selector,touch=False):
 for _ in range(12):
  ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});new Promise(r=>setTimeout(r,100))')
  p=json.loads(ev('JSON.stringify((()=>{let n=document.querySelector('+json.dumps(selector)+'),b=n.getBoundingClientRect(),h=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return{x:b.x+b.width/2,y:b.y+b.height/2,hit:n.contains(h),disabled:n.disabled,at:h&&h.outerHTML.slice(0,140)}})())'))
  if p['hit']:break
 assert p['hit'] and not p['disabled'],(selector,p)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'touch'if touch else'mouse','parameters':{'pointerType':'touch'if touch else'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def key(value):
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
def activate(selector):
 ev('document.querySelector('+json.dumps(selector)+').focus();true');key('\ue007')
def lesson_ready():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===21');until('!document.documentElement.classList.contains("lesson-loading")');call('browsingContext.activate',{'context':ctx})
def open_quiz(touch=False):
 click('#nlQuizOpen',touch);until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")')
def part(id):return '[id$="-part-'+id+'"]'
def choice(i):return '[id$="-choice-'+str(i)+'"]'
def submit():return '[id$="-check-button"]'
def index():return ev('fScenarioPresent().index')
def state():return ev('JSON.stringify({mol:selectedMol,zoom:molZoom2D,numbering:numberingFlag,token:MuLERMoCScenario.applyToken,forms:document.querySelector("input[name=mol2d]:checked")?.id})')
def reload():
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});lesson_ready()
def screenshot_here(name):screenshot(HERE/name)
try:
 # Fresh tab, no receipt. A deep link past the gate must land at step10.
 navigate(PILOT+'#step=21');lesson_ready();until('!!document.querySelector("#nlQuizOpen")')
 check(index()==9 and ev('location.hash')=='#step=10','Cold URL clamps step21 to unsolved step10')
 check(ev('document.querySelector("#scNext").disabled'),'Next visibly disabled before solution')
 screenshot_here('pilot-gate-desktop.png')
 ev('window.__applyCount=0;window.__applyOriginal=fScenarioApply;fScenarioApply=function(){window.__applyCount++;return window.__applyOriginal.apply(this,arguments)};true')
 click('#zoomInBtn');initial=state()
 for action in ['fScenarioGo(20)','location.hash="step=21"']:
  ev(action+';true');until('location.hash==="#step=10"');check(index()==9 and state()==initial,'Blocked navigation preserves actual viewer '+action)
 key('\ue014');check(index()==9 and state()==initial,'Actual ArrowRight cannot bypass checkpoint')
 check(ev('__applyCount===0'),'Blocked navigation does not apply molecular snapshot')
 # Prior theory is available; returning must recreate the gate.
 click('#scPrev');until('fScenarioPresent().index===8');check(not ev('!!document.querySelector("#nlQuizOpen")'),'Previous theory accessible')
 click('#scNext');until('fScenarioPresent().index===9');initial=state();ev('window.__applyCount=0;true')
 open_quiz();screenshot_here('pilot-mission-desktop.png')
 check(ev('document.querySelectorAll("dialog[open]").length===1'),'Quiz is inside one native lesson dialog')
 check(not ev('document.querySelector("#nlQuizDialog").textContent.includes("Χρειάζεσαι μια ιδέα;")'),'No removed hint card')
 key('\ue014');key('\ue012');check(index()==9,'Dialog arrows do not navigate theory')
 click(part('ending'));check(ev('document.querySelector(".part-selection-status").textContent')=='Αυτό το συνθετικό συμφωνεί με τη δομή.','Agreeing fragment receives only accepted minimal feedback')
 click(part('root'));click(choice(0));click(submit())
 check(ev('document.querySelector(".feedback").textContent')==ROUND['choices'][0]['feedback'],'Wrong repair displays authored explanation')
 check(ev('document.querySelector("#scNext").disabled'),'Wrong submitted repair remains gated')
 click('.repair-actions .quiet');check(ev('document.querySelector(".session-row").textContent').strip().endswith('1'),'Retry retains attempt count')
 click(part('root'));click(choice(1))
 check(ev('document.querySelector(".candidate-name").textContent')==ROUND['correctName'],'Correct candidate can be prepared')
 check(ev('document.querySelector("#scNext").disabled') and not ev('!!document.querySelector(".is-success")'),'Correct selection without submitted check cannot unlock')
 check(state()==initial and ev('__applyCount===0'),'All quiz selections and retries preserve viewer snapshot')
 key('\ue00c');until('!document.querySelector("#nlQuizDialog[open]")')
 check(index()==9 and ev('document.activeElement.id')=='nlQuizOpen','Escape returns to current theory and restores button focus')
 reload();check(index()==9 and ev('document.querySelector("#scNext").disabled'),'Refresh retains unsolved gate')
 open_quiz();check(ev('document.querySelector(".candidate-name").textContent')==ROUND['correctName'],'Refresh restores candidate and choices')
 check(not ev('!!document.querySelector(".is-success")'),'Restored unsubmitted correct answer remains unsolved')
 click('#nlQuizBack');until('!document.querySelector("#nlQuizDialog[open]")');check(index()==9,'Explicit return to theory preserves checkpoint')
 open_quiz();initial=state();activate(submit());until('!!document.querySelector(".feedback.is-success")')
 check(ev('document.querySelector(".success-explanation").textContent')==ROUND['successText'],'Correct checked repair shows full existing explanation')
 check(ev('document.querySelector(".round-next button").textContent')=='Συνεχίζω τη θεωρία','Explicit theory Continue follows explanation')
 check(index()==9 and state()==initial,'Correct answer unlocks without advancing or resetting viewer')
 check(not ev('document.querySelector("#scNext").disabled'),'Correct check unlocks navigation')
 screenshot_here('pilot-success-desktop.png')
 activate('.round-next button');until('fScenarioPresent().index===10')
 check(not ev('!!document.querySelector("#nlQuizDialog[open]")') and not ev('!!document.querySelector("#nlQuizCheckpoint")'),'Continue closes exercise and applies next theory step')
 reload();check(index()==10,'Refresh preserves completed progress beyond checkpoint')
 ev('location.hash="step=21";true');until('fScenarioPresent().index===20');check(True,'Completed receipt permits later URL/hash destination')
 ev('fScenarioGo(9);true');until('!!document.querySelector("#nlQuizOpen")');open_quiz()
 check(ev('!!document.querySelector(".feedback.is-success")') and not ev('document.querySelector(".round-next button").disabled'),'Revisit restores completed explanation and image-gated Continue')
 # Main has a pre-existing portrait rotate prompt: test supported landscape. Mobile real controls; completed receipt is reset intentionally in isolated tab.
 click('#nlQuizBack');ev('NameleculeQuizCheckpoints.reset(fScenarioPresent());true')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':844,'height':390},'devicePixelRatio':1})
 open_quiz(True)
 check(ev('(()=>{const d=document.querySelector("#nlQuizDialog"),r=d.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&d.scrollWidth<=d.clientWidth+1})()'),'844×390 landscape dialog fits viewport without horizontal overflow')
 screenshot_here('pilot-mission-landscape.png')
 click('.diagram-tools button',True);until('!!document.querySelector("#nlQuizDialog .zoom-dialog")')
 check(ev('document.querySelectorAll("dialog[open]").length===1'),'Embedded zoom stays within quiz without nested modal')
 key('\ue00c');until('!document.querySelector("#nlQuizDialog .zoom-dialog")')
 check(ev('document.querySelector("#nlQuizDialog").open'),'First Escape closes zoom and keeps exercise')
 click(part('root'),True);click(choice(1),True);click(submit(),True);until('!!document.querySelector(".feedback.is-success")')
 screenshot_here('pilot-success-landscape.png');click('.round-next button',True);until('fScenarioPresent().index===10')
 check(True,'844×390 landscape simulated-touch solution and Continue work')
 # Missing SVG must prevent submission and permit retry or return.
 ev('fScenarioGo(9);NameleculeQuizCheckpoints.reset(fScenarioPresent());window.__failDiagram=true;const ds=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,"src");Object.defineProperty(HTMLImageElement.prototype,"src",{...ds,set(value){ds.set.call(this,window.__failDiagram&&String(value).endsWith("methyl_2_pentane.svg")?"games/assets/name-repair/deliberate-missing.svg":value)}});true')
 click('#nlQuizOpen');until('document.querySelector(".image-status")?.textContent.includes("δεν εμφανίστηκε")')
 check(ev('document.querySelectorAll(".part-button:disabled").length===5&&document.querySelector("#scNext").disabled'),'Missing molecule image disables assessment and retains gate')
 check(not ev('document.querySelector("#nlQuizRetry").hidden'),'Image failure exposes mission retry')
 screenshot_here('pilot-image-failure-mobile.png')
 click('#nlQuizBack');check(index()==9,'Load failure does not trap return to theory')
 ev('window.__failDiagram=false;true');open_quiz();check(ev('document.querySelectorAll(".part-button:disabled").length===0'),'Reopen retries and recovers actual diagram')
 click('#nlQuizBack')
 # Fail-closed runtime: unavailable controller and unknown question type.
 ev('window.__checkpointApi=NameleculeQuizCheckpoints;window.NameleculeQuizCheckpoints=null;fScenarioGo(20);true');check(index()==9,'Missing controller never bypasses required checkpoint')
 ev('window.NameleculeQuizCheckpoints=window.__checkpointApi;fScenarioPlayUi();true')
 ev('window.__checkpointSpec=fScenarioPresent().steps[9].checkpoint;fScenarioPresent().steps[9].checkpoint={...window.__checkpointSpec,type:"unknown-quiz"};fScenarioGo(20);true');check(index()==9,'Unknown quiz type never bypasses required checkpoint')
 ev('fScenarioPresent().steps[9].checkpoint=window.__checkpointSpec;fScenarioPlayUi();true')
 # PresentBegin gates too; authoring-preview Go can inspect later steps.
 ev('const id=fScenarioPresent().id;fScenarioExitPresent();window.__pilotId=id;fScenarioGo(20);true');check(index()==20 and not ev('MuLERMoCScenario.present'),'Author preview remains ungated')
 ev('fScenarioPresentBegin(window.__pilotId,20);true');until('MuLERMoCScenario.present');check(index()==9,'Starting presentation at later selected step honors gate')
 # History navigation into later hash is gated through hash handler.
 ev('location.hash="step=9";true');until('fScenarioPresent().index===8')
 ev('location.hash="step=21";true');until('fScenarioPresent().index===9')
 call('browsingContext.traverseHistory',{'context':ctx,'delta':-1});until('fScenarioPresent().index===8')
 call('browsingContext.traverseHistory',{'context':ctx,'delta':1});until('fScenarioPresent().index===9')
 check(ev('location.hash==="#step=10"'),'Actual browser Back/Forward cannot bypass unsolved gate')
 # Runtime schema boundaries against known library IDs.
 schema=json.loads(ev('JSON.stringify((()=>{const s=fScenarioPresent(),o={scenarioVersion:2,title:s.title,author:s.author,steps:s.steps};const good=fScenarioValidate(o).ok;o.scenarioVersion=1;const old=!fScenarioValidate(o).ok;o.scenarioVersion=2;o.steps=JSON.parse(JSON.stringify(o.steps));o.steps[9].selectedMol="unknown-molecule";const skipped=!fScenarioValidate(o).ok;return {good,old,skipped}})())'))
 check(all(schema.values()),'Real schema accepts pilot2, rejects v1 mandatory metadata and skipped question',schema)
 # Exit is always accessible via actual Escape after dialog closes.
 call('browsingContext.activate',{'context':ctx});ev('document.querySelector("#scExit").focus();true');key('\ue00c');until('!MuLERMoCScenario.present');check(not ev('!!document.querySelector("#nlQuizCheckpoint")'),'Escape exits presentation and removes checkpoint UI')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('pilot-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['diagnostics']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level') in ['warn','error']]
 (HERE/'pilot-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
