from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/alkane-checkpoint-pilot-20261104/browser/test-pilot.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[]}
try:
 navigate(PILOT+'#step=10');lesson_ready();until('!!document.querySelector("#nlQuizOpen")')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':844,'height':390},'devicePixelRatio':1})
 open_quiz();check(ev('getComputedStyle(document.querySelector("#nlQuizDialog .round-heading h1")).display==="block"'),'Embedded mission title visible despite inherited Main landscape h1 rule')
 check(ev('(()=>{let d=document.querySelector("#nlQuizDialog");return d.scrollWidth<=d.clientWidth+1})()'),'Landscape dialog still fits after title reset')
 screenshot_here('pilot-mission-landscape.png')
 click('.diagram-tools button');key('\ue00c');until('!document.querySelector("#nlQuizDialog .zoom-dialog")');check(ev('document.querySelector("#nlQuizDialog").open'),'Final target still closes only zoom on Escape')
 click('#nlQuizBack');check(index()==9,'Final target returns to theory')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors
 (HERE/'landscape-heading-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
