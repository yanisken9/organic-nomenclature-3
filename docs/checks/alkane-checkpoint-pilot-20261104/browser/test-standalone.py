from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/alkane-checkpoint-pilot-20261104/browser/test-pilot.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[]}
game=json.loads(Path('games/data/name-repair-alkanes.json').read_text())
try:
 navigate('games/name-repair.html?v=checkpoint-regression');until('!!document.querySelector(".intro-start")');call('browsingContext.activate',{'context':ctx})
 until('document.querySelector(".workshop-logo").naturalWidth>0');check(ev('document.querySelector(".workshop-logo").complete&&document.querySelector(".workshop-logo").naturalWidth>0'),'Existing 3D logo decodes in introduction')
 activate('.intro-start')
 for r in game['rounds']:
  until('!!document.querySelector(".diagram-image.is-ready")')
  check(ev('document.querySelector(".round-heading h1").textContent')==r['title'],'Same round title '+r['id'])
  if r['kind']=='replace':
   activate('#part-'+r['targetPartId']);i=next(i for i,c in enumerate(r['choices']) if c['value']==r['correctValue']);activate('#choice-'+str(i))
  else:
   activate('#part-ethylGroup');activate('#move-left')
  activate('#check-button');until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector(".success-name").textContent')==r['correctName'],'Correct same candidate '+r['id'])
  check(ev('document.querySelector(".success-explanation").textContent')==r['successText'],'Same success explanation '+r['id'])
  check(ev('document.activeElement===document.querySelector(".round-next button")'),'Keyboard success focus '+r['id'])
  check(not ev('document.querySelector(".round-screen").textContent.includes("Χρειάζεσαι μια ιδέα;")'),'Hint card stays absent '+r['id'])
  activate('.round-next button')
 until('!!document.querySelector(".results")')
 check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".stat-number")].map(n=>Number(n.textContent)))'))==[4,4],'Existing five rounds score 4/4 excluding guided example')
 screenshot_here('standalone-results.png')
 activate('.results-actions button');until('!!document.querySelector(".intro-start")')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 check(ev('document.documentElement.scrollWidth<=innerWidth'),'390px standalone intro fits')
 click('.intro-start',True);until('!!document.querySelector(".diagram-image.is-ready")')
 check(ev('document.documentElement.scrollWidth<=innerWidth'),'390px standalone mission fits')
 screenshot_here('standalone-mobile.png')
 click('#part-root',True);i=next(i for i,c in enumerate(game['rounds'][0]['choices']) if c['value']==game['rounds'][0]['correctValue']);click('#choice-'+str(i),True);click('#check-button',True);until('!!document.querySelector(".feedback.is-success")')
 check(ev('document.querySelector(".success-name").textContent')==game['rounds'][0]['correctName'],'Mobile guided repair accepts actual touch')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('standalone-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'standalone-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
