from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
exec((H/'round-helpers.py').read_text(),globals())
def diffs(a,b,path=''):
 if type(a)!=type(b):return[path]
 if isinstance(a,dict):return [p for k in a.keys()|b.keys()for p in ([path+'/'+str(k)]if k not in a or k not in b else diffs(a[k],b[k],path+'/'+str(k)))]
 if isinstance(a,list):return [path+'/length']if len(a)!=len(b)else [p for i,(x,y)in enumerate(zip(a,b))for p in diffs(x,y,path+'/'+str(i))]
 return []if a==b else [path]
try:
 source_guard();viewport(320,700);navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');ready();dismiss_rotate();priorpath=ROOT/'docs/checks/workshop-lesson-parity-20261110/browser/root-embedded-r1-final-browser.json';prior=json.loads(priorpath.read_text());receipt=next(r['receipt']for r in prior['repairs']if r['label']=='main55-s11r3');imported={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};ev('Object.entries('+json.dumps(imported,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();dismiss_rotate();ev('fScenarioGo(3);true');wait('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation');wait('!document.getElementById("nlQuizOpen").disabled');records=read('Object.entries(sessionStorage).filter(([k])=>k.startsWith("namelecule:lesson-checkpoints:v1:")).map(([key,value])=>({key,record:JSON.parse(value)}))');OUT['main54ImportDiagnostic']={'records':records,'source':str(priorpath.relative_to(ROOT))+' repairs[main55-s11r3].receipt'}
 original=json.loads(next(iter(imported.values())))
 for row in records:
  if row['key']not in imported:OUT['main54ImportDiagnostic']['contentDifferences']=diffs(json.loads(original['content']),json.loads(row['record']['content']))
 check(ev('!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&document.getElementById("nlQuizPracticeOpen").hidden'),'Main54 distinct scenario fingerprint cannot borrow Main55 mastery');open_lesson();check(counter()=='Κουίζ 1/3'and ev('document.getElementById("nlQuizPracticeContinue").hidden'),'Main54 ordinary required dialog counter/header mounts at320');zoom('main54-required');click('#nlQuizBack');check(ev('fScenarioPresent().index===3&&document.getElementById("scNext").disabled&&!document.getElementById("nlQuizDialog").open'),'Main54 bounded required-close keeps unsolved gate locked');shot('main54-required-card-320')
 viewport(390,760);direct();check(ev('!document.querySelector(".has-practice-action")&&!document.querySelector(".nl-quiz-practice-continue")'),'Standalone default has no optional lesson controls');zoom('standalone-default');shot('standalone-default');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
