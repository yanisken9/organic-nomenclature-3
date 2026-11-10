from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
HISTORY=ROOT/'docs/checks/lesson-optional-triples-20261110/browser/after-persistence-resume-browser.json'
def ready():
 app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55);dismiss_rotate()
def state():return read('(()=>{let b=document.getElementById("nlQuizBack");return{backHidden:b.hidden,backDisplay:getComputedStyle(b).display,backRects:b.getClientRects().length,lower:[...document.querySelectorAll(".round-next button")].map(n=>({text:n.textContent,display:getComputedStyle(n).display,disabled:n.disabled})),counter:document.getElementById("nlQuizProgress").textContent,success:!!document.querySelector(".feedback.is-success"),index:fScenarioPresent().index}})()')
try:
 source_guard();viewport(1280,800);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step=4');ready()
 historical=json.loads(HISTORY.read_text());receipt=next(r['receipt']for r in historical['repairs']if r['label']=='required-s4r3');earned={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};assert len(earned)==1
 OUT['receiptLineage']={'source':str(HISTORY.relative_to(ROOT))+' repairs[required-s4r3].receipt','sha256':hashlib.sha256(HISTORY.read_bytes()).hexdigest(),'exactImportedStorage':earned,'claim':'Exact genuine previously earned three repairs; no new success claimed.'}
 ev('Object.entries('+json.dumps(earned,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();wait('!document.getElementById("nlQuizOpen").disabled&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)',55);click('#nlQuizOpen');image_ready();v=state();check(not v['backHidden'] and v['backRects']>0 and len(v['lower'])==2 and v['counter']=='Κουίζ 3/3' and v['success'],'Before original completed required header has Return plus both lower actions',v);top();shot('required-complete-header-1280');prepare('.round-next .secondary');shot('required-complete-actions-1280');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
