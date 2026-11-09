from pathlib import Path
import json,time,traceback
support=Path('docs/checks/workshop-hub-20261104/browser/test-hub.py').read_text().split('\ntry:\n',1)[0]
exec(compile(support,'support','exec'))
out={'completed':False,'checks':[]}
try:
 navigate('games/name-repair.html?v=workshop-hub-header');hub_ready()
 check(ev('document.querySelector(".header-label").textContent')=='ΜΙΚΡΕΣ ΑΠΟΣΤΟΛΕΣ ΟΝΟΜΑΤΟΛΟΓΙΑΣ','Exact user-requested nomenclature header')
 for w in [1500,1000,920]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':1000},'devicePixelRatio':1})
  check(ev('(()=>{let a=document.querySelector(".brand").getBoundingClientRect(),b=document.querySelector(".header-label").getBoundingClientRect(),c=document.querySelector(".exit-link").getBoundingClientRect();return a.right<=b.left&&b.right<=c.left&&document.documentElement.scrollWidth<=innerWidth})()'),'Longer header fits '+str(w))
  if w==1500:ev('scrollTo(0,0);true');screenshot_here('hub-1500.png')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors
 (HERE/'header-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
