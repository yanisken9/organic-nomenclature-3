"""Bounded exact-candidate/public release smoke. Developer evidence only."""
from pathlib import Path
import os,sys,json,time,traceback,base64,hashlib,urllib.request
H=Path(__file__).resolve().parent;ROOT=Path.cwd();P=json.loads((H/'process.json').read_text());TARGET=json.loads((H.parent.parent/'runtime-target.json').read_text());STAGE=sys.argv[1]if len(sys.argv)>1 else 'local';BASE=P['base_url']if STAGE=='local'else'https://yanisken9.github.io/organic-nomenclature-3/'
os.environ['NAMELECULE_BIDI_PORT']=str(P['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=BASE
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-release-bidi','exec'))
call('session.subscribe',{'events':['network.responseCompleted','network.fetchError'],'contexts':[ctx]})
call('script.addPreloadScript',{'functionDeclaration':'() => {window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
OUT={'completed':False,'stage':STAGE,'role':'Developer release smoke; not independent review','base_url':BASE,'checks':[],'repairs':[],'HTTP':{},'limitations':['Owned isolated headlessFirefox desktop1280x800 only; no personalFirefox or intended conference machine tested.','Supported MULER_QUIET_FETCH suppresses irrelevant naming fetches; external naming availability and Internet-independent operation untested.','Bounded release replay; no full molecule/mode/lesson matrix or new chemistry certification.','Live smoke opens firstrequiredquiz and directauthoredWorkshop; localphase earned required/optional sets. Professorreport deliberately skipped pendingpublication.']}
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def save():
 OUT['javascriptErrors']=js_errors;(H/(STAGE+'-browser.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
def pause(ms=220):time.sleep(ms/1000)
def wait(x,seconds=40):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.12)
 raise AssertionError('Timeout '+x)
def check(ok,label,detail=None):
 assert ok,(label,detail)
 OUT['checks'].append({'label':label,'detail':detail});save();print('PASS '+label,flush=True)
def shot(label):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(H/(STAGE+'-'+label+'.png')).write_bytes(base64.b64decode(r['data']))
def pointer(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'release-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def key(value):call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'release-keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]});pause()
def wheel(delta,dialog):
 p=read('(()=>{let d='+('document.getElementById("nlQuizDialog").getBoundingClientRect()'if dialog else'({x:0,y:0,width:innerWidth,height:innerHeight})')+';return{x:Math.round(d.x+d.width*.75),y:Math.round(d.y+d.height*.75)}})()');call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'release-wheel','actions':[{'type':'scroll','x':p['x'],'y':p['y'],'deltaX':0,'deltaY':delta,'duration':100}]}]});pause(150)
def prepare(sel):
 if not ev('!!document.getElementById("nlQuizDialog")?.open'):
  ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(120)
 for _ in range(35):
  p=read('(()=>{let n=document.querySelector('+json.dumps(sel)+');if(!n)return null;let r=n.getBoundingClientRect(),d=document.getElementById("nlQuizDialog"),dialog=!!d?.open,dr=dialog?d.getBoundingClientRect():{top:0,bottom:innerHeight},h=dialog?(n.closest(".nl-quiz-dialog-header")?dr.top:d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect().bottom):0,x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,safeTop:h+3,safeBottom:dr.bottom-3,hit:n===hit||n.contains(hit),disabled:!!n.disabled,dialog}})()')
  assert p is not None,sel
  if p['top']>=p['safeTop']and p['bottom']<=p['safeBottom']and p['hit']and not p['disabled']:return p
  assert not p['disabled'],(sel,p)
  wheel(-220 if p['top']<p['safeTop']else 220,p['dialog'])
 raise AssertionError(('Unreachable',sel,p))
def click(sel,settle=260):
 p=prepare(sel);pause(300);p=prepare(sel);pointer(p);pause(settle)
def image_ready():wait('!!document.querySelector(".diagram-image.is-ready")',55)
def ready():
 app_ready();wait('MuLERMoCScenario.ready===true&&window.JSmolReadyFlag===true&&document.readyState==="complete"',60)
def lesson_ready():
 app_ready();wait('MuLERMoCScenario.ready===true&&MuLERMoCScenario.present&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55)
def model(key):
 file=ev('nameExamples['+json.dumps(key)+'].file3D');count=int((Path(P['candidateRoot'])/file).read_text().splitlines()[3][:3]);wait('(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length==='+str(count)+'}catch(e){return false}})()',45);return read('({key:selectedMol,file:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length})')
def observe():ev('(()=>{const original=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.__releaseRound=JSON.parse(JSON.stringify(options.round));return original.apply(this,arguments)};return true})()')
def storage():return read('Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith("namelecule:lesson-checkpoints:v1:")))')
def state():return read('({counter:document.getElementById("nlQuizProgress").textContent,backHidden:document.getElementById("nlQuizBack").hidden,continueHidden:document.getElementById("nlQuizPracticeContinue").hidden,lower:[...document.querySelectorAll(".round-next button")].map(n=>({text:n.textContent,disabled:n.disabled})),complete:NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3),image:!!document.querySelector(".diagram-image.is-ready")})')
def solve(label):
 r=read('__releaseRound');OUT['repairs'].append({'label':label,'round':r});save()
 if r['kind']=='replace':
  click('[id$="-part-'+r['targetPartId']+'"]');good=next(i for i,c in enumerate(r['choices'])if c['value']==r['correctValue']);click('[id$="-choice-'+str(good)+'"]')
 else:
  for index,pid in enumerate(r['correctOrder']):
   click('[id$="-part-'+pid+'"]')
   for _ in range(len(r['correctOrder'])):
    if ev('document.querySelector("[id$=\\"-move-left\\"]").disabled'):break
    click('[id$="-move-left"]')
   for _ in range(index):click('[id$="-move-right"]')
 click('[id$="-check-button"]',650);wait('!!document.querySelector(".feedback.is-success")');check(True,label+' earned through actual learner pointer inputs',state());OUT['repairs'][-1]['receipt']=storage();save()
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1})
 if STAGE=='local':
  for p,digest in TARGET['runtime'].items():
   with urllib.request.urlopen(BASE+p+'?releasehash='+str(time.time_ns()),timeout=15)as r:b=r.read();status=r.status
   OUT['HTTP'][p]={'status':status,'sha256':hashlib.sha256(b).hexdigest()};assert status==200 and OUT['HTTP'][p]['sha256']==digest,p
  check(True,'All26 exact served candidate runtime/provenance hashes match frozen release target')
 navigate('design/welcome-proposal.html?v=release-20261110-'+STAGE);check(ev('document.title.startsWith("Namelecule")&&document.querySelectorAll(".card").length===3'),'Welcome renders three entries');click('.explore-entry a');ready();check(ev('location.pathname.endsWith("mulermoc-nom-55.html")&&Object.keys(nameExamples).length===141&&Object.values(MOL2D).reduce((n,v)=>n+Object.values(v).filter(s=>typeof s==="string"&&!!s.trim()).length,0)===422'),'Actual welcome Explore opens Main55 with141molecules/422forms');OUT['models']=[model('methane')];check(True,'Initial methane real3D matches source file and5atoms')
 if STAGE=='local':
  click('#dimethyl_2_3_butane');wait('selectedMol==="dimethyl_2_3_butane"');OUT['models'].append(model('dimethyl_2_3_butane'));check(True,'Actual molecule switch loads matching dimethylbutane3D source')
  for mode,index in [('expanded',2),('skeletal',3),('condensed',1)]:
   click('#radio2DMode .mode2DOption:nth-child('+str(index)+')');wait('mode2D==='+json.dumps(mode)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")');check(ev('!document.querySelector("#jsmeNomeclatureSVG").getAttribute("data-label-error")&&document.querySelector("#radio2DMode .mode2DOption:nth-child('+str(index)+')").classList.contains("selectedRadio")'),'Actual '+mode+' radio and2D rendering agree')
  click('#zoomInBtn');click('#zoomOutBtn');check(ev('selectedMol==="dimethyl_2_3_butane"&&mode2D==="condensed"&&!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Main zoom pair preserves molecule and mode');shot('main55')
 navigate('design/welcome-proposal.html?v=release-20261110-theory-'+STAGE);click('.card.one a.action');wait('location.pathname.endsWith("theory-library.html")');check(ev('document.querySelectorAll("a[href*=scenario]").length===14'),'Actual welcome Theory reaches14lesson library');click('article[aria-labelledby=alkanes-title] a.action');lesson_ready();check(ev('location.pathname.endsWith("mulermoc-nom-55.html")&&fScenarioPresent().index===0&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Library alkane link opens normal12step Main55 lesson')
 for index in [1,2,3]:click('#scNext');wait('fScenarioPresent().index==='+str(index)+'&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('document.getElementById("scNext").disabled&&document.getElementById("pageContainer").classList.contains("scContentOnly")'),'Required gate4 blocks Next and hides viewer');observe();click('#nlQuizOpen');image_ready();check(state()['counter']=='Κουίζ 1/3'and not state()['backHidden'],'Actual first required quiz is ready with counter1/3 and Return');shot('required-first')
 if STAGE=='local':
  for ri in range(3):
   solve('required'+str(ri+1))
   if ri<2:
    check(ev('document.getElementById("scNext").disabled'),'Partial required set keeps gate locked');click('.round-next button',650);wait('document.getElementById("nlQuizProgress").textContent==='+json.dumps('Κουίζ '+str(ri+2)+'/3'));image_ready()
  v=state();check(v['complete']and v['backHidden']and v['continueHidden']and v['counter']=='Κουίζ 3/3'and len(v['lower'])==2 and all(not b['disabled']for b in v['lower']),'Completed required third exposes only lower Continue/Another triple pair',v);shot('required-completed');required=storage();click('.round-next .secondary',650);image_ready();v=state();check(v['backHidden']and not v['continueHidden']and v['counter']=='Κουίζ 1/3','Additional optional triple resets counter1/3 and restores upperContinue',v)
  for ri in range(3):
   solve('optional'+str(ri+1))
   if ri<2:click('.round-next button',650);wait('document.getElementById("nlQuizProgress").textContent==='+json.dumps('Κουίζ '+str(ri+2)+'/3'));image_ready()
  v=state();check(v['complete']and v['backHidden']and v['continueHidden']and v['counter']=='Κουίζ 3/3'and len(v['lower'])==2 and all(not b['disabled']for b in v['lower']),'Completed optional third hides upperContinue leaving only lower pair',v);OUT['earnedReceipt']=storage();shot('optional-completed');click('.round-next .secondary',650);image_ready();v=state();check(not v['continueHidden']and v['counter']=='Κουίζ 1/3'and v['complete'],'Another optional triple restores upperContinue preserving required mastery',v);click('#nlQuizPracticeContinue');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');check(True,'Actual upperContinue returns to next theory step');click('#scExit');wait('location.pathname.endsWith("theory-library.html")');check(True,'Actual lesson Exit returns to library')
  navigate('games/name-repair.html');wait('!!document.getElementById("set-alkanes-start")');click('#set-alkanes-start');wait('!!document.getElementById("set-alkanes-unbranched-start")');click('#set-alkanes-unbranched-start');image_ready();g=read('(()=>{let p=document.querySelector(".round-objective"),b=document.querySelector(".diagram-tools button"),s=getComputedStyle(p);return{text:p.textContent,emphasized:p.classList.contains("is-emphasized"),align:s.textAlign,weight:s.fontWeight,zoomText:b.textContent,zoomLabel:b.getAttribute("aria-label"),zoomRect:b.getBoundingClientRect().toJSON()}})()');check(g['emphasized']and g['align']=='center'and int(g['weight'])>=700 and not g['zoomText'].strip()and g['zoomLabel']=='Μεγέθυνση σχεδίου'and g['zoomRect']['width']>=44 and g['zoomRect']['height']>=44,'Direct Workshop objective is emphasized and magnifier accessible',g);click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');check(ev('document.querySelector(".diagram-image").currentSrc===document.querySelector(".zoom-image").currentSrc'),'Workshop zoom displays same actual asset');shot('workshop-zoom');key(chr(0xe00c));check(ev('!document.querySelector(".zoom-dialog")&&document.activeElement===document.querySelector(".diagram-tools button")'),'Workshop zoom Escape closes and restores magnifier focus')
 else:
  click('#nlQuizBack');check(ev('!document.getElementById("nlQuizDialog").open&&document.getElementById("scNext").disabled'),'Live quiz Return closes without bypassing required gate');click('#scExit');wait('location.pathname.endsWith("theory-library.html")');check(True,'Actual live lessonExit returns to library');navigate('games/name-repair.html');wait('!!document.getElementById("set-alkanes-start")');click('#set-alkanes-start');wait('!!document.getElementById("set-alkanes-unbranched-start")');click('#set-alkanes-unbranched-start');image_ready();g=read('(()=>{let p=document.querySelector(".round-objective"),b=document.querySelector(".diagram-tools button"),s=getComputedStyle(p);return{text:p.textContent,emphasized:p.classList.contains("is-emphasized"),align:s.textAlign,weight:s.fontWeight,zoomLabel:b.getAttribute("aria-label"),zoomRect:b.getBoundingClientRect().toJSON()}})()');check(g['emphasized']and g['align']=='center'and int(g['weight'])>=700 and g['zoomLabel']=='Μεγέθυνση σχεδίου'and g['zoomRect']['width']>=44 and g['zoomRect']['height']>=44,'Live direct Workshop objective and accessiblemagnifier',g);click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');check(ev('document.querySelector(".diagram-image").currentSrc===document.querySelector(".zoom-image").currentSrc'),'Live Workshopzoom same actualasset');shot('workshop-zoom');key(chr(0xe00c));check(ev('!document.querySelector(".zoom-dialog")&&document.activeElement===document.querySelector(".diagram-tools button")'),'Live Workshopzoom closes and restoresfocus')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure');OUT['failureURL']=ev('location.href');OUT['failureBody']=ev('document.body.innerText.slice(-7000)')
 except Exception:pass
finally:
 OUT['networkFailures']=[e['params']for e in all_events if e.get('method')=='network.fetchError' or(e.get('method')=='network.responseCompleted'and e.get('params',{}).get('response',{}).get('status',0)>=400)];OUT['externalResponses']=[{'url':e['params'].get('request',{}).get('url'), 'status':e['params'].get('response',{}).get('status')}for e in all_events if e.get('method')=='network.responseCompleted'and not e['params'].get('request',{}).get('url','').startswith(BASE)];OUT['networkResponseCount']=sum(e.get('method')=='network.responseCompleted'for e in all_events);OUT['javascriptErrors']=js_errors;OUT['diagnosticEntries']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in['error','warn']]
 if STAGE=='local':OUT['runtimeUnchangedAfter']=all(hashlib.sha256((Path(P['candidateRoot'])/p).read_bytes()).hexdigest()==digest for p,digest in TARGET['runtime'].items())
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{});s.close()
 print(json.dumps({'completed':OUT['completed'],'stage':STAGE,'checks':len(OUT['checks']),'repairs':len(OUT['repairs']),'JSErrors':len(js_errors),'failure':OUT.get('failure')},ensure_ascii=False),flush=True)
if not OUT['completed']:raise SystemExit(1)
