from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
HISTORY=ROOT/'docs/checks/lesson-optional-triples-20261110/browser/after-persistence-resume-browser.json'
def ready():
 app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55);dismiss_rotate()
def state():return read('(()=>{let b=document.getElementById("nlQuizBack"),c=document.getElementById("nlQuizPracticeContinue");return{backHidden:b.hidden,backDisplay:getComputedStyle(b).display,backRects:b.getClientRects().length,continueHidden:c.hidden,continueDisplay:getComputedStyle(c).display,index:fScenarioPresent().index,focus:document.activeElement.id}})()')
def saved():return read('JSON.parse(sessionStorage.getItem('+json.dumps(storage_key)+'))')
try:
 source_guard();viewport(1280,800);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step=4');ready()
 historical=json.loads(HISTORY.read_text());receipt=next(r['receipt']for r in historical['repairs']if r['label']=='required-s4r3');earned_storage={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};assert len(earned_storage)==1;storage_key=next(iter(earned_storage))
 OUT['receiptLineage']={'source':str(HISTORY.relative_to(ROOT))+' repairs[required-s4r3].receipt','sha256':hashlib.sha256(HISTORY.read_bytes()).hexdigest(),'exactImportedStorage':earned_storage,'claim':'Exact genuine previously earned receipt; no new prerequisite success claimed.'}
 ev('Object.entries('+json.dumps(earned_storage,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();wait('!document.getElementById("nlQuizOpen").disabled&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)',55);required=saved()['states'];click('#nlQuizOpen');image_ready();v=state();check(not v['backHidden']and v['backRects']>0 and v['continueHidden'],'Required header retains visible Return only',v);click('#nlQuizBack');check(ev('!document.getElementById("nlQuizDialog").open&&fScenarioPresent().index===3'),'Required Return closes to same checkpoint');click('#nlQuizPracticeOpen');image_ready();top();v=state()
 if STAGE=='before':check(not v['backHidden']and not v['continueHidden'],'Original optional header reproduces both ambiguous actions',v)
 else:check(v['backHidden']and v['backDisplay']=='none'and v['backRects']==0 and not v['continueHidden'],'Optional header shows Continue and removes Return from layout',v)
 for w,height in [(390,760),(320,700)]:
  viewport(w,height);top();v=read('(()=>{let d=document.getElementById("nlQuizDialog"),c=document.getElementById("nlQuizPracticeContinue"),r=c.getBoundingClientRect();return{width:innerWidth,pageWidth:document.documentElement.scrollWidth,dialogWidth:d.clientWidth,dialogScroll:d.scrollWidth,button:r.toJSON(),display:getComputedStyle(c).display}})()');check(v['pageWidth']<=w and v['dialogScroll']<=v['dialogWidth']and v['button']['width']>0,'Header fits narrow viewport '+str(w),v);shot('optional-'+str(w))
 ev('document.getElementById("nlQuizPracticeContinue").focus();true')
 # Use actual WebDriver Tab codepoint, not a JS event.
 key(chr(0xe004));focused=ev('document.activeElement.id');check((focused=='nlQuizBack')==(STAGE=='before'),'Native Tab includes Return only in required/before layout',focused)
 key(chr(0xe00c));check(ev('!document.getElementById("nlQuizDialog").open&&fScenarioPresent().index===3'),'Native Escape retains return-to-current-step behavior');check(saved()['states']==required,'Escape preserves original earned receipt');click('#nlQuizOpen');image_ready();v=state();check(not v['backHidden']and v['continueHidden'],'Reused dialog restores required Return',v);click('#nlQuizBack');click('#nlQuizPracticeOpen');image_ready();v=state();check(v['backHidden']==(STAGE=='after')and not v['continueHidden'],'Reused dialog restores correct optional header',v);ev('document.getElementById("nlQuizPracticeContinue").focus();true');key(chr(0xe007));wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');check(saved()['states']==required,'Native Enter on Continue advances while preserving earned receipt');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
