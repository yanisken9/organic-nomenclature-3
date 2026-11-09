from pathlib import Path
import os,json,hashlib,traceback,urllib.request,difflib
HERE=Path('docs/checks/alkanes-json9-library-20261108');baseline=json.loads((HERE/'baseline.json').read_text());source=Path(baseline['source']);target=Path(baseline['target']);candidate=json.loads(source.read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'scope':'User-supplied JSON import as-is at existing active library path; no application code edits','limitations':['Owned headless Firefox; no user browser/unsaved edits accessed','All12 steps replayed in author rehearsal; unchanged quiz recipes validated/opened, not all six repairs solved anew','No new full3D/Safari/physicalmobile/screenreader/conference audit']}
def check(ok,label):
 assert ok,label
 out['checks'].append(label);print('PASS '+label,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=json9-preflight-20261108');ready()
 res=json.loads(ev('JSON.stringify(fScenarioValidate('+json.dumps(candidate,ensure_ascii=False)+'))'));out['validation']={'ok':res['ok'],'warnings':res.get('warnings',[]),'steps':len(res.get('steps',[]))}
 check(res['ok'] and len(res.get('steps',[]))==12 and not res.get('warnings'),'Actual player accepts source9 JSON with12steps and no warnings')
 check(hashlib.sha256(source.read_bytes()).hexdigest()==baseline['inputSHA256'],'Desktop source9 unchanged since preflight')
 check(hashlib.sha256(target.read_bytes()).hexdigest()==baseline['oldSHA256'],'Recorded existing lesson still matches recovery snapshot')
 target.write_bytes(source.read_bytes())
 check(target.read_bytes()==source.read_bytes(),'Installed lesson is byte-identical to Desktop9JSON')
 (HERE/'alkanes-user-3.scenario.json.diff').write_text(''.join(difflib.unified_diff((HERE/'before/scenarios/alkanes-user-3.scenario.json').read_text().splitlines(True),target.read_text().splitlines(True),fromfile='before/alkanes-user-3.scenario.json',tofile='active/alkanes-user-3.scenario.json')))
 with urllib.request.urlopen('http://127.0.0.1:8013/scenarios/alkanes-user-3.scenario.json',timeout=10) as r:
  data=r.read();check(r.status==200 and data==source.read_bytes(),'Local HTTP serves exact9JSON bytes through stable lesson URL')
 navigate('design/theory-library.html?v=alkanes-json9-20261108');click('article[aria-labelledby=alkanes-title] a.action');ready()
 check(ev('MuLERMoCScenario.present&&fScenarioPresent().index===0&&fScenarioPresent().title==="Αλκάνια"'),'Existing library card opens updated12step lesson normally')
 ev('location.hash="#step=5";true');until('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('document.getElementById("scNext").disabled&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Normal learner step5 request remains locked by quiz4')
 check(ev('fScenarioPresent().steps[3].note.includes("Χωρίς διακλαδώσεις")'),'Revised workshop text loaded from9JSON')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',seconds=45)
 check(ev('document.querySelector("#nlQuizDialog .repair-actions").children.length===1&&document.querySelector("#nlQuizDialog .repair-actions button").textContent==="Έλεγχος"'),'Unchanged generated quiz opens with current shared UI')
 click('#nlQuizBack');click('#scExit');until('location.pathname.endsWith("/design/theory-library.html")')
 check(ev('!!document.querySelector("article[aria-labelledby=alkanes-title]")'),'Normal lesson Exit returns to library')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=alkanes-json9-20261108');ready();ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true')
 click('.scenarioPanel.active .srow[data-idx="4"] .scPresentStep');until('MuLERMoCScenario.present')
 check(ev('fScenarioPresent().index===4&&NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Author screen opens revised step5 directly')
 check(ev('document.getElementById("pageTitle").textContent.trim()==="Κύρια αλυσίδα και συνολικά άτομα C"&&document.getElementById("scStepText").textContent.includes("ισοδύναμες κύριες αλυσίδες")'),'New step5 title and revised main-chain instruction rendered')
 check(ev('document.getElementById("comp6").getAttribute("aria-disabled")==="true"&&document.getElementById("comp9").getAttribute("aria-disabled")==="true"'),'Step5 passive name parts preserved')
 out['chainSelectors']=json.loads(ev('JSON.stringify([...document.querySelectorAll("#scChainNavigation button")].map(e=>({id:e.id,text:e.textContent,label:e.getAttribute("aria-label")})))'))
 check(ev('!!document.getElementById("scChainNavigation")&&document.querySelectorAll("#scChainNavigation button").length===2'),'Both existing main-chain navigation arrows remain available')
 before_chain=ev('mainChainPoolIdx');buttons='#scChainNavigation button';click(buttons+':last-of-type');check(ev('mainChainPoolIdx')!=before_chain,'Step5 can display second equivalent parent chain');click(buttons+':first-of-type');check(ev('mainChainPoolIdx')==before_chain,'Step5 switches back to first equivalent chain')
 screenshot(HERE/'updated-step5.png')
 for i in range(12):
  ev('fScenarioGo('+str(i)+');true');until('fScenarioPresent().index==='+str(i))
  expected=res['steps'][i]['title']
  check(ev('document.getElementById("pageTitle").textContent.trim()')==expected.strip(),'Rehearsal step '+str(i+1)+' applies correct title')
  if i in [5,6,7,9]:
   check(ev('!!document.getElementById("scStepText").querySelector("b")'),'Revised rich text renders correctly step'+str(i+1))
 check(ev('fScenarioPresent().steps[11].menuSubset.length===8&&fScenarioPresent().steps[11].show.viewers["2D"]&&fScenarioPresent().steps[11].show.viewers["3D"]'),'Final8molecule2D3D configuration retained')
 for p,h in baseline['protected'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
 check(True,'All45 protected app/core/library/other-scenario files unchanged')
 check(hashlib.sha256(target.read_bytes()).hexdigest()==baseline['inputSHA256'] and target.read_bytes()==source.read_bytes(),'Final active/Desktop9 exact byte andSHA match')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
