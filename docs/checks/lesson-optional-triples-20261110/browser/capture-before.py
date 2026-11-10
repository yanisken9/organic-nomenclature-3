from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
exec((H/'round-helpers.py').read_text(),globals())
try:
 OUT['harnessCorrection']='Cold old adapter imports are revalidated only on opening the required mount; initial cold-card isComplete assertion was premature. Earlier failure retained, no product source change.';source_guard();viewport(1280,800);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');ready();dismiss_rotate()
 priorpath=ROOT/'docs/checks/workshop-lesson-parity-20261110/browser/root-embedded-r1-final-browser.json';prior=json.loads(priorpath.read_text());receipt=next(r['receipt']for r in prior['repairs']if r['label']=='main55-s11r3');earned={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};assert earned
 OUT['receiptLineage']={'source':str(priorpath.relative_to(ROOT))+' repairs[main55-s11r3].receipt','sourceSHA256':hashlib.sha256(priorpath.read_bytes()).hexdigest(),'role':'Exact genuine historical six earned repairs; no new prerequisite success claimed.','exactStorage':earned}
 ev('Object.entries('+json.dumps(earned,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();dismiss_rotate()
 for step in (3,10):
  ev('fScenarioGo('+str(step)+');true');wait('fScenarioPresent().index==='+str(step)+'&&!MuLERMoCScenario.checkpointPreparation');wait('!document.getElementById("nlQuizOpen").disabled');dismiss_rotate();shot('s'+str(step+1)+'-card');check(ev('!document.getElementById("nlQuizPracticeOpen")'),'Baseline lacks optional card action '+str(step+1));open_lesson();check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(step)+')'),'Historical earned gate verified after normal required mount '+str(step+1));check(ev('document.getElementById("nlQuizProgress").textContent==="Κουίζ 3/3"'),'Baseline genuine third success review '+str(step+1));check(ev('document.querySelectorAll(".round-next button").length===1&&!document.getElementById("nlQuizPracticeContinue")'),'Baseline only theory continue at success '+str(step+1));top();shot('s'+str(step+1)+'-success-top');prepare('.round-next button');shot('s'+str(step+1)+'-success-actions');click('#nlQuizBack')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
