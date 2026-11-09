"""Bounded deployed root smoke only; no repeated repair/model suites."""
from pathlib import Path
import os,json,time,traceback,base64,hashlib
h=Path(__file__).resolve().parent;p=json.loads((h/'process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(p['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=p['base_url']
exec(compile(Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(20)'),'owned-live-bidi','exec'));call('session.subscribe',{'events':['network.responseCompleted','network.fetchError'],'contexts':[ctx]})
out={'completed':False,'role':'Developer LIVE browser smoke, not independent review','release':p['release'],'base_url':p['base_url'],'checks':[],'scope':'Cold owned headless Firefox profile; live welcome→library→current user3lesson→gate4 actual image/counter→Return/Exit. No six-repair repetition or model matrix.','limitations':['Bounded live smoke cannot guarantee uninterrupted operation or conference readiness','External JSmol/fonts/PubChem/tracking dependencies remain; no offline fallback certified','No personal GUI/browser/driver interaction, physical mobile/Safari/screen reader checks or prior freeze diagnosis']}
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def save():
 out['javascriptErrors']=js_errors;out['diagnosticEntries']=[x['params'] for x in all_events if x.get('method')=='log.entryAdded' and x.get('params',{}).get('level') in ['error','warn']];out['networkResponses']=[x['params'] for x in all_events if x.get('method')=='network.responseCompleted'];out['networkFetchErrors']=[x['params'] for x in all_events if x.get('method')=='network.fetchError'];(h/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def check(ok,label):
 assert ok,label
 out['checks'].append(label);save();print('PASS '+label,flush=True)
def wait(x,sec=30):
 end=time.monotonic()+sec
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.15)
 raise AssertionError('Timeout '+x)
def shot(name):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(h/(name+'.png')).write_bytes(base64.b64decode(r['data']))
def pointer(sel):
 ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center"});true');time.sleep(.1);pos=read('(()=>{const e=document.querySelector('+json.dumps(sel)+'),r=e.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,hit:e===hit||e.contains(hit),disabled:!!e.disabled}})()');assert pos['hit'] and not pos['disabled'],(sel,pos);call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'live-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':pos['x'],'y':pos['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1});navigate('design/welcome-proposal.html?v=release-20261109');check(ev('document.querySelectorAll(".card").length')==3,'LIVE welcome renders3primaryentries');out['environment']=read('({userAgent:navigator.userAgent,url:location.href,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio}})');shot('live-welcome');pointer('a.action[href^="theory-library.html"]');wait('!!document.querySelector("article[aria-labelledby=alkanes-title]")');check(ev('location.pathname')=='/organic-nomenclature-3/design/theory-library.html','LIVE welcome opens theorylibrary');pointer('article[aria-labelledby=alkanes-title] a.action');app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',50)
 check(ev('location.pathname')=='/organic-nomenclature-3/mulermoc-nom-54.html' and ev('new URL(location.href).searchParams.get("scenario")')=='scenarios/alkanes-user-3.scenario.json','LIVE library opens current user3lesson');check(ev('fScenarioPresent().index===0&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'LIVE12step lesson starts in normal learner step1');out['lesson']=read('({title:fScenarioPresent().title,steps:fScenarioPresent().steps.length,index:fScenarioPresent().index,scripts:[...document.scripts].map(s=>s.src).filter(Boolean),styles:[...document.styleSheets].map(s=>s.href).filter(Boolean),url:location.href})')
 for i in [1,2,3]:pointer('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation',30)
 check(ev('document.getElementById("scNext").disabled&&document.getElementById("pageContainer").classList.contains("scContentOnly")'),'LIVE gate4 actualNextblocks and contentonlylayout applies');wait('!!document.querySelector("#pageTitle img")&&document.querySelector("#pageTitle img").complete&&document.querySelector("#pageTitle img").naturalWidth>0',15);check(True,'LIVE workshop4logo loads');pointer('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45);check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','LIVE actual generated quiz opens with image/counter1of3');out['quiz']=read('(()=>{const d=document.getElementById("nlQuizDialog"),header=d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),title=d.querySelector(".round-heading h1").getBoundingClientRect(),obj=d.querySelector(".round-heading p").getBoundingClientRect(),img=d.querySelector(".diagram-image");return{imageURL:img.src,imageLoaded:img.complete&&img.naturalWidth>0,progress:document.getElementById("nlQuizProgress").textContent,scroll:d.scrollTop,headerBottom:header.bottom,titleTop:title.top,objectiveTop:obj.top}})()');check(out['quiz']['imageLoaded'] and out['quiz']['scroll']<1 and out['quiz']['titleTop']>=out['quiz']['headerBottom'] and out['quiz']['objectiveTop']>=out['quiz']['headerBottom'],'LIVE quiz image loaded and roundheading startsbelowstickyheader');shot('live-gate4-entry');pointer('#nlQuizBack');wait('!document.getElementById("nlQuizDialog").open');check(ev('fScenarioPresent().index===3&&document.getElementById("scNext").disabled'),'LIVE Return preserves unsolved gate4');pointer('#scExit');wait('location.pathname==="/organic-nomenclature-3/design/theory-library.html"');check(ev('!!document.querySelector("article[aria-labelledby=alkanes-title]")'),'LIVE Exit returns to theorylibrary');out['exitURL']=ev('location.href');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureURL']=ev('location.href');shot('live-failure')
 except Exception as e:out['captureFailure']=str(e)
finally:
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'pageJavascriptErrors':len(js_errors),'networkFetchErrors':len(out['networkFetchErrors']),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
