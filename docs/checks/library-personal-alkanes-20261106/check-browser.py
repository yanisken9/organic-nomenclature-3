from pathlib import Path
import os,json,traceback,hashlib
HERE=Path('docs/checks/library-personal-alkanes-20261106')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'limitations':['Isolated headless Firefox; DOM click activates actual navigation. Native pointer/keyboard, Safari, physical mobile and full conference flow not audited. No repeated full quiz/viewer/3D regression because their files/data are unchanged.']}
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS '+name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('MuLERMoCScenario.present&&!!fScenarioPresent()&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
try:
 navigate('design/theory-library.html?v=alkanes-personal-20261106-r1')
 check(ev('document.querySelectorAll("article[aria-labelledby=alkanes-title]").length===1'),'One existing Alkane card, no duplicate')
 expected='../mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&v=alkanes-personal-20261106-r1'
 check(ev('document.querySelector("article[aria-labelledby=alkanes-title] a.action").getAttribute("href")')==expected,'Alkane action targets current personal JSON with presentation and return flags')
 check(ev('document.querySelector("article[aria-labelledby=alkanes-title] .count").textContent')=='12 βήματα · 8 μόρια','Existing card count matches personal lesson')
 other=ev('document.querySelector("article[aria-labelledby=alkenes-title] a.action").getAttribute("href")')
 screenshot(HERE/'library.png')
 click('article[aria-labelledby=alkanes-title] a.action');ready()
 check(ev('new URLSearchParams(location.search).get("scenario")==="scenarios/alkanes-user-3.scenario.json"'),'Actual card click navigates to current scenario URL')
 check(ev('fScenarioPresent().title==="Αλκάνια"&&fScenarioPresent().steps.length===12&&fScenarioPresent().index===0'),'Current personal lesson loads its 12 steps from first step')
 check(ev('selectedMol==="ethane"&&document.getElementById("pageTitle").textContent.includes("Τι είναι τα αλκάνια")'),'First step displays the saved title and ethane')
 check(ev('fScenarioPresent().steps[4].styleName.disabled.join(",")==="comp6,comp9"&&fScenarioPresent().steps[4].show.chainNavigation===true'),'Loaded lesson includes reviewed step5 restrictions and two-chain selector')
 check(ev('MuLERMoCScenario.returnToTheoryLibrary===true'),'Library return flag is active')
 screenshot(HERE/'lesson-start.png')
 for index in [1,2,3]:
  click('#scNext');until('fScenarioPresent().index==='+str(index)+'&&!MuLERMoCScenario.checkpointPreparation',seconds=45)
  check(ev('fScenarioPresent().index')==index,'Forward navigation reaches step '+str(index+1))
 check(ev('!!document.getElementById("nlQuizOpen")&&document.getElementById("scNext").disabled'),'Workshop gate remains present and locked at step4')
 check(ev('!document.getElementById("viewerCol").getClientRects().length'),'Saved Workshop-only layout is loaded')
 click('#scExit');until('location.pathname.endsWith("/design/theory-library.html")&&!!document.querySelector("#alkanes-title")',seconds=30)
 check(ev('document.querySelector("article[aria-labelledby=alkanes-title] a.action").getAttribute("href")')==expected,'Exit returns to library with the updated Alkane action')
 check(ev('document.querySelector("article[aria-labelledby=alkenes-title] a.action").getAttribute("href")')==other,'Other lesson action is unchanged after return')
 out['final_url']=ev('location.href');out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
