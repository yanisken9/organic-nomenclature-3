from pathlib import Path
import json,time,traceback
prefix=Path('docs/checks/v54-sync-20261104/test-features.py').read_text().split('\ntry:\n',1)[0]
exec(compile(prefix,'feature-support','exec'))
out={'completed':False,'checks':[]}
def check(value,label):
 assert value,label
 out['checks'].append(label)
try:
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  navigate('design/welcome-proposal.html?v=v54-active-'+str(time.time_ns()))
  check(ev('document.querySelector(".explore-entry a").href.includes("mulermoc-nom-54.html")'),'Explore54 '+str(width))
  click('.explore-entry a');app_ready()
  check(ev('location.pathname.endsWith("mulermoc-nom-54.html")&&Object.keys(nameExamples).length===141'),'Actual54 boot '+str(width))
  
  if width==390:
   check(ev('getComputedStyle(document.querySelector("#rotatePrompt")).display!=="none"'),'Existing portrait rotationprompt')
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1000,'height':390},'devicePixelRatio':1})
  click('a[href*="welcome-proposal"]')
  until('location.pathname.endsWith("/design/welcome-proposal.html")')
  check(True,'Explore returnwelcome '+str(width))
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  click('.card.one a.action');until('location.pathname.endsWith("/design/theory-library.html")')
  links=json.loads(ev('JSON.stringify([...document.querySelectorAll("a[href*=scenario]")].map(a=>a.href))'))
  check(len(links)==14 and all('mulermoc-nom-54.html?'in x for x in links),'All14 lessons54 '+str(width))
  click('a[href*="alkanes-nomenclature-branches"]');app_ready()
  until('!!window.MuLERMoCScenario&&MuLERMoCScenario.ready&&MuLERMoCScenario.present&&MuLERMoCScenario.steps.length>0&&!document.documentElement.classList.contains("lesson-loading")&&!!document.querySelector("#scExit")')
  check(ev('new URLSearchParams(location.search).get("from")==="theory-library"&&MuLERMoCScenario.steps.length>0'),'Lessonpresentfromlibrary '+str(width))
  if width==390:call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1000,'height':390},'devicePixelRatio':1})
  click('#scExit');until('location.pathname.endsWith("/design/theory-library.html")')
  check(True,'LessonExitlibrary '+str(width))
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  click('a[href*="welcome-proposal"]');until('location.pathname.endsWith("/design/welcome-proposal.html")')
  click('.card.two a.action');until('location.pathname.endsWith("/games/name-repair.html")&&!!document.querySelector(".intro-start")')
  check(True,'Workshop directentry '+str(width))
  click('a.brand');until('location.pathname.endsWith("/design/welcome-proposal.html")')
  check(True,'Workshopreturn '+str(width))
  click('[data-panel="teacher"]');until('document.querySelector("#details").open')
  check(ev('document.querySelector("#dialog-link").href.includes("mulermoc-nom-54.html")'),'Teacher54 '+str(width))
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'activation-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'activation-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
