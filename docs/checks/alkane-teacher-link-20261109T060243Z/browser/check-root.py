"""Bounded root publication preflight using approved copied runtime and preserved public React."""
from pathlib import Path
import os,json,time,traceback,hashlib,base64,urllib.request
HERE=Path(__file__).resolve().parent;proc=json.loads((HERE/'process.json').read_text());plan=json.loads((HERE.parent/'root-publication-plan.json').read_text());root=Path(plan['publicClone']);os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=f'http://127.0.0.1:{proc["http_port"]}/organic-nomenclature-3/'
exec(compile(Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(20)'),'owned-root-bidi','exec'))
out={'completed':False,'role':'Developer root publication preflight; not independent review','checks':[],'rootFiles':{},'base_url':os.environ['NAMELECULE_TEST_BASE_URL'],'limitations':['Bounded localhost GitHub Pages prefix emulation; public-deployment HTTP/browser checks remain separate','Same approved runtime bytes as prefixed actual6repair replay; no duplicate repair suite','Only preserved public React dist tested; no React WIP/source interaction or rebuild','Owned headless Firefox only; no personal browser or prior freeze diagnosis; not conference certification']}
def save():
 out['javascriptErrors']=js_errors;out['allDiagnosticEntries']=[e['params'] for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level') in ['error','warn']];(HERE/'root-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def check(ok,label):
 assert ok,label
 out['checks'].append(label);save();print('PASS '+label,flush=True)
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def wait(expr,seconds=30):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(expr):return
  time.sleep(.15)
 raise AssertionError('Timeout '+expr)
def pointer(sel):
 ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center"});true');time.sleep(.1);p=read('(()=>{const e=document.querySelector('+json.dumps(sel)+'),r=e.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()');assert p['hit'] and not p['disabled'],(sel,p);call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'root-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def shot(name):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(name+'.png')).write_bytes(base64.b64decode(r['data']))
def inner(expr):return ev('document.querySelector("iframe").contentWindow.eval('+json.dumps(expr)+')')
try:
 check(all(hashlib.sha256((root/p).read_bytes()).hexdigest()==sha for p,sha in plan['rootFiles'].items()),'All12 root overlay files match approved current source hashes')
 check(all(hashlib.sha256((root/p).read_bytes()).hexdigest()==sha for p,sha in plan['protectedFiles'].items()),'All49 protected publishedReact/v52 files unchanged')
 for p,sha in plan['rootFiles'].items():
  with urllib.request.urlopen(os.environ['NAMELECULE_TEST_BASE_URL']+p,timeout=15) as r:data=r.read();out['rootFiles'][p]={'status':r.status,'SHA256':hashlib.sha256(data).hexdigest()};assert r.status==200 and out['rootFiles'][p]['SHA256']==sha,p
 check(True,'All12 actual root HTTP responses match frozen overlay bytes')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1});navigate('design/welcome-proposal.html?v=release-20261109');check(ev('document.title').startswith('Namelecule') and ev('document.querySelectorAll(".card").length')==3,'Root welcome renders three primary entries');shot('root-welcome');pointer('a.action[href^="theory-library.html"]');wait('!!document.querySelector("article[aria-labelledby=alkanes-title]")');check(ev('location.pathname')=='/organic-nomenclature-3/design/theory-library.html','Welcome theory link reaches root library');pointer('article[aria-labelledby=alkanes-title] a.action');app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',45)
 check(ev('location.pathname')=='/organic-nomenclature-3/mulermoc-nom-54.html' and ev('new URL(location.href).searchParams.get("scenario")')=='scenarios/alkanes-user-3.scenario.json','Root library opens current12step alkane lesson');check(ev('!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&fScenarioPresent().index===0'),'Root lesson begins normal learner mode step1')
 ev('fScenarioGo(11);true');wait('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation',30);check(ev('document.getElementById("scNext").disabled&&document.getElementById("pageContainer").classList.contains("scContentOnly")'),'Root actual gate4 blocks premature final-step navigation');pointer('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45);check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','Root real generated quiz image/counter renders');out['rootQuiz']=read('({progress:document.getElementById("nlQuizProgress").textContent,diagram:document.querySelector("#nlQuizDialog .diagram-image").src,dialogScroll:document.getElementById("nlQuizDialog").scrollTop})');shot('root-gate4-entry');pointer('#nlQuizBack');pointer('#scExit');wait('location.pathname==="/organic-nomenclature-3/design/theory-library.html"');check(True,'Root checkpoint Return and lesson Exit reach root library')
 out['rootErrorsBeforeReact']=len(js_errors);navigate('react-preview/dist/#/viewer');wait('!!document.querySelector(".molecule-stage iframe:not([hidden])")&&!document.getElementById("molecule-select").disabled&&document.querySelector(".molecule-stage").getAttribute("aria-busy")==="false"',60);wait('document.querySelector("iframe").contentWindow.eval("selectedMol")==="ethanol"',30);check(ev('document.getElementById("molecule-results").textContent.includes("126")'),'Preserved public React catalog has126molecules')
 check(inner('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG[data-label-error]")'),'Preserved public React ethanol2D model renders');scripts=json.loads(inner('JSON.stringify([...document.scripts].map(s=>s.src).filter(s=>s.includes("preserved-main-20261030")))'));check(len(scripts)==2,'React loads its two preserved52runtime scripts');out['reactPinnedScripts']=scripts
 wait('Number(document.querySelector("iframe").contentWindow.eval(\'Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count")\'))===9',35);check(True,'Preserved public React ethanol3D loads9atoms');pointer('input[name=mode][value=expanded]');wait('document.querySelector("iframe").contentWindow.eval("mode2D")==="expanded"',20);check(True,'Preserved React mode switch uses expanded2D');shot('root-react-preserved');out['reactURL']=ev('location.href')
 out['resources']=read('performance.getEntriesByType("resource").map(r=>({name:r.name,initiatorType:r.initiatorType,responseStatus:r.responseStatus,duration:r.duration}))');check(all(hashlib.sha256((root/p).read_bytes()).hexdigest()==sha for p,sha in plan['rootFiles'].items()),'All12 root overlay files remain frozen after test');check(all(hashlib.sha256((root/p).read_bytes()).hexdigest()==sha for p,sha in plan['protectedFiles'].items()),'All49 protected publishedReact/v52 files remain unchanged after test');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureURL']=ev('location.href');shot('root-failure')
 except Exception as e:out['captureFailure']=str(e)
finally:
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'pageErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
