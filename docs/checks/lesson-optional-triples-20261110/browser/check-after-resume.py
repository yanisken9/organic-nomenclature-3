from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
exec((H/'round-helpers.py').read_text(),globals())
def observe_rounds():
 ev('(()=>{if(NameleculeRepairGame.mountRound.__observed)return true;const original=NameleculeRepairGame.mountRound;let observed=function(host,options){window.__observedRound=JSON.parse(JSON.stringify(options.round));return original.apply(this,arguments)};observed.__observed=true;NameleculeRepairGame.mountRound=observed;return true})()')
def current_round():return read('__observedRound')
def storage():return read('JSON.parse(sessionStorage.getItem(Object.keys(sessionStorage).find(k=>k.startsWith("namelecule:lesson-checkpoints:v1:"))))')
def required(step):return storage()['states'][str(step)]
def practice(step):return storage()['practices'][str(step)]
def complete(step):return ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(step)+')&&!document.getElementById("scNext").disabled')
def reload_lesson(step):
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();dismiss_rotate();ev('fScenarioGo('+str(step)+');true');wait('fScenarioPresent().index==='+str(step)+'&&!MuLERMoCScenario.checkpointPreparation');
 if step in (3,10):wait('!document.getElementById("nlQuizOpen").disabled')
 observe_rounds()
def layout(label):
 g=read('(()=>{let d=document.getElementById("nlQuizDialog"),h=d.querySelector(".nl-quiz-dialog-header"),buttons=[...d.querySelectorAll(".nl-quiz-dialog-actions button:not([hidden]),.round-next button")].map(n=>({text:n.textContent,rect:n.getBoundingClientRect().toJSON(),disabled:n.disabled}));return{viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,dialog:d.getBoundingClientRect().toJSON(),header:h.getBoundingClientRect().toJSON(),buttons}})()');OUT['measurements'].append({'label':label,**g});check(g['pageWidth']<=g['viewport']and g['dialog']['left']>=0 and g['dialog']['right']<=g['viewport']+1,label+' viewport and whole dialog fit',g)
 buttons=g['buttons'];check(all(b['rect']['left']>=g['dialog']['left']-1 and b['rect']['right']<=g['dialog']['right']+1 for b in buttons),label+' buttons inside dialog width',buttons)
 for i,a in enumerate(buttons):
  for b in buttons[i+1:]:
   x,y=a['rect'],b['rect'];assert min(x['right'],y['right'])-max(x['left'],y['left'])<=1 or min(x['bottom'],y['bottom'])-max(x['top'],y['top'])<=1,(label,a,b)
 check(True,label+' controls do not overlap');shot(label)
def expect_optional(step,earned,label):
 check(complete(step)and required(step)==earned,label+' original earned receipt and unlock invariant');check(ev('document.getElementById("nlQuizDialogTitle").textContent==="Προαιρετική εξάσκηση"&&!document.getElementById("nlQuizPracticeContinue").hidden&&!document.getElementById("nlQuizPracticeContinue").disabled&&!document.getElementById("nlQuizPracticeNotice").hidden'),label+' optional title notice and always available continue')
def another(step,earned,label):
 old=practice(step)['seed'] if str(step)in storage().get('practices',{})else earned['seed'];click('.round-next .secondary');image_ready();top();now=practice(step)['seed'];check(old!=now and counter()=='Κουίζ 1/3',label+' fresh seed resets optional to1/3',{'previous':old,'new':now});expect_optional(step,earned,label);return now
try:
 OUT['harnessCorrection']='Captured mounted display rounds already contain mission reminder. Compare exact displayed feedback, not assume canonical shorter string. Initial harness failure retained.';source_guard();OUT['answerOracle']='Pass-through wrapper records actual mounted canonical options.round; source/engine unchanged, every new answer uses native input. Deterministic crypto only controls unsolved seed.'
 OUT=json.loads((H/'after-attempt2-visible-reflow-browser.json').read_text());OUT.pop('failure',None);OUT['completed']=False;OUT['resumeFrom']='after-attempt2-visible-reflow-browser.json repairs[required-s4r3].receipt; exact genuinely earned three mandatory repairs. No new prerequisite success claimed.';OUT['harnessCorrection2']='Smooth intermediates required only for offscreen response reveal. Removing previous feedback reflowed content and clamped scroll14.85px while response remained visible before/after; original trace retained.';source_guard()
 viewport(1280,800);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');ready();dismiss_rotate();receipt=next(x['receipt']for x in OUT['repairs']if x['label']=='required-s4r3');earnedstorage={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};ev('Object.entries('+json.dumps(earnedstorage,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');reload_lesson(3);open_lesson()
 earned=required(3);check(ev('document.querySelectorAll(".round-next button").length===2'),'Required third success retains continue and adds practice');OUT['earnedRequired']=earned
 for w,height in [(1280,800),(390,760),(320,700)]:viewport(w,height);prepare('.round-next .secondary');layout('required-third-success-'+str(w))
 seed=another(3,earned,'Gate4 first optional');viewport(390,760);top();layout('optional-entry-390');zoom('optional-gate4');
 for ri in range(3):
  f=current_round();solve(f,'optional-s4r'+str(ri+1),ri,True,extensive=ri==0);expect_optional(3,earned,'Gate4 optional answer'+str(ri+1))
  if ri<2:next_round('optional-s4r'+str(ri+1),ri,True,3)
 check(practice(3)['solved']and ev('document.querySelectorAll(".round-next button").length===2'),'Optional triple complete supports repeat and continue');viewport(320,700);prepare('.round-next .secondary');layout('optional-third-success-320');another(3,earned,'Gate4 repeat optional')
 f=current_round();click('[id$="check-button"]');check(not practice(3)['solved'],'Unanswered optional check remains unfinished');expect_optional(3,earned,'Unfinished optional')
 if f['kind']=='replace':
  click('[id$="part-'+f['targetPartId']+'"]');bad=next(i for i,c in enumerate(f['choices'])if c['value']!=f['correctValue']);click('[id$="choice-'+str(bad)+'"]');click('[id$="check-button"]');check(not ev('!!document.querySelector(".feedback.is-success")'),'Optional incorrect/unchanged answer does not earn success')
 before=practice(3);click('#nlQuizBack');check(ev('fScenarioPresent().index===3&&!document.getElementById("nlQuizDialog").open'),'Back returns same checkpoint');check(practice(3)==before and required(3)==earned and complete(3),'Back preserves unfinished optional and required mastery');click('#nlQuizPracticeOpen');image_ready();check(practice(3)==before,'Reopen preserves current optional attempt');click('#nlQuizBack');reload_lesson(3);click('#nlQuizPracticeOpen');image_ready();check(practice(3)==before and required(3)==earned and complete(3),'Same-tab refresh/reopen preserves exact partial optional and required receipt');top();layout('optional-resumed-320');click('#nlQuizPracticeContinue');wait('fScenarioPresent().index===4');check(ev('!document.getElementById("nlQuizDialog").open'),'Header continue exits unfinished optional to next theory step')
 # Explicit historical receipt import supplies prerequisite mastery for bounded branched verification.
 priorpath=ROOT/'docs/checks/workshop-lesson-parity-20261110/browser/root-embedded-r1-final-browser.json';prior=json.loads(priorpath.read_text());receipt=next(r['receipt']for r in prior['repairs']if r['label']=='main55-s11r3');imported={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};OUT['branchedReceiptLineage']={'source':str(priorpath.relative_to(ROOT))+' repairs[main55-s11r3].receipt','sourceSHA256':hashlib.sha256(priorpath.read_bytes()).hexdigest(),'role':'Exact genuine historical six repairs; no new prerequisite successes claimed.','exactStorage':imported};ev('Object.entries('+json.dumps(imported,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');reload_lesson(10);check(complete(10),'Gate11 historical required receipt independently regenerates/validates');earned11=required(10);click('#nlQuizPracticeOpen');image_ready();expect_optional(10,earned11,'Gate11 first optional');viewport(390,760)
 for ri in range(3):
  f=current_round();solve(f,'optional-s11r'+str(ri+1),ri,True,extensive=ri==0);expect_optional(10,earned11,'Gate11 optional answer'+str(ri+1))
  if ri<2:next_round('optional-s11r'+str(ri+1),ri,True,10)
 another(10,earned11,'Gate11 repeat optional');click('#nlQuizBack');before11=practice(10);reload_lesson(10);click('#nlQuizPracticeOpen');image_ready();check(practice(10)==before11 and required(10)==earned11 and complete(10),'Gate11 refresh preserves fresh unfinished optional and required receipt');click('#nlQuizPracticeContinue');wait('fScenarioPresent().index===11');check(ev('!document.getElementById("nlQuizDialog").open'),'Gate11 optional continue reaches final theory')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
