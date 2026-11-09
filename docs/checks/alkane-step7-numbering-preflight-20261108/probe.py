from pathlib import Path
import json,os,traceback,subprocess,signal,time,hashlib
HERE=Path('docs/checks/alkane-step7-numbering-preflight-20261108');process=json.loads((HERE/'test-process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(process['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'scope':'Read-only preflight; actual author preview7, supported chain-navigation temporarily revealed for diagnosis only; no persisted scenario/settings/core edits','observations':{}}
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def snapshot():return json.loads(ev('JSON.stringify({step:fScenarioPresent().index+1,mol:selectedMol,mode:nameAnalysisMode,chain:mainChainAtomsList,poolIndex:mainChainPoolIdx,pool:mainChainPool.map(p=>p.chain),numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(e=>({text:e.textContent,x:e.getAttribute("x"),y:e.getAttribute("y")})),chainNavigation:!!document.getElementById("scChainNavigation"),name:currentMolName})'))
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=step7-numbering-preflight-20261108');app_ready();until('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true');click('.scenarioPanel.active .srow[data-idx="6"] .scPresentStep');until('MuLERMoCScenario.present&&fScenarioPresent().index===6')
 out['observations']['default']=snapshot();click('#comp5');out['observations']['stemSelected']=snapshot();screenshot(HERE/'current-step7.png')
 ev('fScenarioApplyChainNavigation(Object.assign({},fScenarioPresent().steps[6].show,{chainNavigation:true}));true')
 out['observations']['temporarilyRevealedNavigation']=snapshot()
 before=snapshot();rev=list(reversed(before['chain']));out['observations']['exactReverseInPool']=rev in before['pool'];out['observations']['sameAtomSetPoolPaths']=[p for p in before['pool'] if sorted(p)==sorted(before['chain'])]
 click('#chainNextBtn');out['observations']['nextPath']=snapshot();click('#chainPrevBtn');out['observations']['previousPath']=snapshot()
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'observations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 r=subprocess.run(['ps','-p',str(process['pid']),'-o','command='],capture_output=True,text=True)
 if r.returncode==0 and process['profile'] in r.stdout and '--headless' in r.stdout:
  os.kill(process['pid'],signal.SIGTERM)
  for _ in range(30):
   if subprocess.run(['ps','-p',str(process['pid']),'-o','pid='],capture_output=True).returncode!=0:break
   time.sleep(.1)
  closed=subprocess.run(['ps','-p',str(process['pid']),'-o','pid='],capture_output=True).returncode!=0
  (HERE/'cleanup.json').write_text(json.dumps({'pid':process['pid'],'profileVerified':True,'stopped':closed,'userBrowserAndServerUntouched':True},indent=2)+'\n')
 print(json.dumps({'completed':out['completed'],'errors':len(js_errors),'observations':out['observations'],'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
