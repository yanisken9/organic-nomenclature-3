from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
def current():return ev('document.getElementById("nlQuizDialog")?.open?document.getElementById("nlQuizDialog").scrollTop:scrollY')
def sample(ms=2000):ev('(()=>{window.__interruptTrace=[];let start=performance.now();function tick(){let d=document.getElementById("nlQuizDialog");__interruptTrace.push({ms:performance.now()-start,y:d?.open?d.scrollTop:scrollY});if(performance.now()-start<'+str(ms)+')requestAnimationFrame(tick)}requestAnimationFrame(tick);return true})()')
def safe(sel):return read('(()=>{let d=document.getElementById("nlQuizDialog"),r=document.querySelector('+json.dumps(sel)+').getBoundingClientRect(),dr=d?.open?d.getBoundingClientRect():null,h=d?.open?d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect().bottom:0;return{top:r.top,bottom:r.bottom,safeTop:h+12,safeBottom:(dr?dr.top+d.clientHeight+1:innerHeight)-12,y:d?.open?d.scrollTop:scrollY}})()')
try:
 source_guard();OUT['pageEvidence']='interruptions-r1-retained.json: native wheel/manual interruption and rapid latest selection pass; reveal implementation exact r1→r2.'
 # Unsolved dialog fixture only, close during actual reveal, reopen unchanged at top.
 viewport(390,760);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');app_ready();wait('!!fScenarioPresent()&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55)
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):click('#rotatePromptDismiss')
 for i in (1,2,3):click('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
 click('#nlQuizOpen');image_ready();target='[id$="part-component-6"]';p=prepare(target);sample(600);pointer(p);pause(45);during=current();click('#nlQuizBack',50);check(not ev('document.getElementById("nlQuizDialog").open'),'Dialog Back closes during pending reveal');click('#nlQuizOpen');image_ready();sample(1200);pause(1350);trace=read('__interruptTrace');OUT['dialogReopen']={'motionBeforeBack':during,'trace':trace};check(all(abs(v['y'])<1 for v in trace),'Dialog reopen stays at top without stale motion',OUT['dialogReopen']);check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','Dialog Back/reopen retains current-question position');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
