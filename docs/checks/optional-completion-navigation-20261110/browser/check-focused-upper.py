from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
HISTORY=ROOT/'docs/checks/lesson-optional-triples-20261110/browser/after-persistence-resume-browser.json'
def ready():
 app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55);dismiss_rotate();wait('!document.getElementById("nlQuizOpen").disabled',55)
def state():return read('(()=>{let b=document.getElementById("nlQuizBack"),c=document.getElementById("nlQuizPracticeContinue"),i=document.querySelector(".diagram-image");return{backHidden:b.hidden,backRects:b.getClientRects().length,continueHidden:c.hidden,continueRects:c.getClientRects().length,counter:document.getElementById("nlQuizProgress").textContent,title:document.getElementById("nlQuizDialogTitle").textContent,image:{ready:i?.classList.contains("is-ready"),src:i?.src},status:document.querySelector(".image-status")?.textContent,lower:[...document.querySelectorAll(".round-next button")].map(n=>({text:n.textContent,disabled:n.disabled})),requiredComplete:NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3),index:fScenarioPresent().index,focus:document.activeElement.tagName}})()')
def receipt():return read('Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith("namelecule:lesson-checkpoints:v1:")))')
def stored():return json.loads(next(iter(receipt().values())))
def fault(mode):
 p=json.loads((H/'fault-control.json').read_text());p['mode']=mode;(H/'fault-control.json').write_text(json.dumps(p)+'\n')
def observe():ev('(()=>{const original=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.__observedRound=JSON.parse(JSON.stringify(options.round));return original.apply(this,arguments)};return true})()')
def reload():
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();observe()
def upper_available(label):
 v=state();check(v['backHidden'] and not v['continueHidden'] and v['continueRects']>0 and ev('!document.getElementById("nlQuizPracticeContinue").disabled'),label,v)
def optional_done(label):
 v=state();check(v['backHidden'] and v['continueHidden'] and v['continueRects']==0 and v['counter']=='Κουίζ 3/3' and len(v['lower'])==2 and all(not b['disabled']for b in v['lower']) and v['image']['ready'] and stored()['practices']['3']['solved'],label,v)
def optional_pending(label):
 upper_available(label+' upperContinue remains available');v=state();check(v['counter']=='Κουίζ 3/3' and len(v['lower'])==2 and all(b['disabled']for b in v['lower']) and not v['image']['ready'],label+' lowerPair disabled pending actual image',v)
def fit(label,w):
 g=read('(()=>{let d=document.getElementById("nlQuizDialog"),buttons=[...d.querySelectorAll(".nl-quiz-dialog-actions button:not([hidden]),.round-next button")].map(n=>({text:n.textContent,rect:n.getBoundingClientRect().toJSON(),disabled:n.disabled}));return{viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,dialog:d.getBoundingClientRect().toJSON(),clientWidth:d.clientWidth,scrollWidth:d.scrollWidth,buttons}})()');OUT['measurements'].append({'label':label,**g});check(g['pageWidth']<=w and g['scrollWidth']<=g['clientWidth'] and g['dialog']['left']>=0 and g['dialog']['right']<=w+1,label+' viewport and dialog fit',g);check(all(b['rect']['left']>=g['dialog']['left']-1 and b['rect']['right']<=g['dialog']['right']+1 for b in g['buttons']),label+' controls fit width')
 for i,a in enumerate(g['buttons']):
  for b in g['buttons'][i+1:]:
   x,y=a['rect'],b['rect'];assert min(x['right'],y['right'])-max(x['left'],y['left'])<=1 or min(x['bottom'],y['bottom'])-max(x['top'],y['top'])<=1,(label,a,b)
 shot(label);save()
def scripts(label):
 d=read('(()=>{let s=[...document.scripts].map(n=>n.src);return{controller:s.find(x=>x.includes("namelecule-quiz-checkpoints.js")),renderer:s.find(x=>x.includes("namelecule-game-repair.js")),adapter:s.find(x=>x.includes("namelecule-generated-repair-checkpoint.js"))}})()');check(d['controller'].endswith('?v=optional-completion-navigation-20261110-r1') and d['renderer'].endswith('?v=required-completion-navigation-20261110-r2') and d['adapter'].endswith('?v=required-completion-navigation-20261110-r2'),label+' updated controller cache URL and preserved shared script URLs',d)
def focus_snapshot():return read('(()=>{let n=document.activeElement,d=document.getElementById("nlQuizDialog"),b=document.getElementById("nlQuizPracticeContinue");return{tag:n?.tagName,id:n?.id,hidden:n?.hidden,rects:n?.getClientRects().length,inside:d?.contains(n),dialogOpen:d?.open,hasFocus:document.hasFocus(),upperHidden:b?.hidden,upperRects:b?.getClientRects().length,index:typeof fScenarioPresent==="function"?fScenarioPresent()?.index:null,url:location.href}})()')
try:
 source_guard();viewport(390,760);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step=4');ready();rpath=H/'after-browser.json';prior=json.loads(rpath.read_text());earned=prior['newEarnedReceipt'];OUT['receiptLineage']={'source':'after-browser.json newEarnedReceipt','sha256':hashlib.sha256(rpath.read_bytes()).hexdigest(),'exactImportedStorage':earned,'claim':'Exact genuinely earned completed optional receipt from immediately preceding native run.'};ev('sessionStorage.clear();Object.entries('+json.dumps(earned,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');reload();fault('delay');click('#nlQuizPracticeOpen');wait('document.querySelectorAll(".round-next button").length===2');optional_pending('Focus probe pending completed optional');OUT['naturalLoadingFocus']=focus_snapshot();ev('document.getElementById("nlQuizPracticeContinue").focus();true');OUT['explicitUpperFocusBeforeRelease']=focus_snapshot();check(OUT['explicitUpperFocusBeforeRelease']['id']=='nlQuizPracticeContinue','Labelled explicit focus probe targets visible upperContinue');fault('normal');image_ready();optional_done('Focus probe actual image-ready callback hides upperContinue');pause(300);OUT['focusAfterImageReady']=focus_snapshot();shot('after-image-ready');OUT['focusObservationOnly']='Explicit focus setup probes newly hidden focusedcontrol; no key or handler/state injection. Data reports containment without presuming pass.';OUT['completed']=True;print(json.dumps({k:OUT[k]for k in ['naturalLoadingFocus','explicitUpperFocusBeforeRelease','focusAfterImageReady']},ensure_ascii=False),flush=True)
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
finally:
 fault('normal');finish()
