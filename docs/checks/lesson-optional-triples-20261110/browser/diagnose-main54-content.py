from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
exec((H/'round-helpers.py').read_text(),globals())
def diffs(a,b,path=''):
 if type(a)!=type(b):return[path]
 if isinstance(a,dict):return [p for k in a.keys()|b.keys()for p in ([path+'/'+str(k)]if k not in a or k not in b else diffs(a[k],b[k],path+'/'+str(k)))]
 if isinstance(a,list):return [path+'/length']if len(a)!=len(b)else [p for i,(x,y)in enumerate(zip(a,b))for p in diffs(x,y,path+'/'+str(i))]
 return []if a==b else [path]
try:
 source_guard();viewport(1280,800);navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');ready();dismiss_rotate();actual=read('(()=>{let s=fScenarioPresent();return{version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps}})()');priorpath=ROOT/'docs/checks/workshop-lesson-parity-20261110/browser/root-embedded-r1-final-browser.json';prior=json.loads(priorpath.read_text());receipt=next(r['receipt']for r in prior['repairs']if r['label']=='main55-s11r3');imported={k:v for k,v in receipt.items()if k.startswith('namelecule:lesson-checkpoints:v1:')};original=json.loads(next(iter(imported.values())));changes=diffs(json.loads(original['content']),actual);OUT['main54RuntimeContent']={'source':str(priorpath.relative_to(ROOT))+' repairs[main55-s11r3].receipt','differences':changes,'current':actual};check(bool(changes),'Main54 current scenario differs from exact historical Main55 content',changes);OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
finally:finish()
if not OUT['completed']:raise SystemExit(1)
