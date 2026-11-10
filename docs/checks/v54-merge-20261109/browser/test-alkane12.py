"""Actual normal12-step learner traversal: six earned repairs, declared seed fixtures."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());games={g['seed']:{s['id']:s for s in g['sets']} for g in fixtures}
out.update(rounds=[],geometry=[],models3D=[],lessonSteps=[],notes=['Seed4/seed1 unsolved start fixtures only; no solved receipts fabricated. All six repairs earned through native pointer actions.'])
def save():
 out['sourceHashesAtFinish']={p:hashlib.sha256((CR/p).read_bytes()).hexdigest() for p in SOURCE_PATHS};out['sourceChangedDuringRun']=[p for p in SOURCE_PATHS if out['sourceHashesAtFinish'][p]!=START_HASHES[p]];out['frozenTargetMatchesAtFinish']=out['sourceHashesAtFinish']==FROZEN['files'];out['completed']=out['completed'] and out['frozenTargetMatchesAtFinish'];out['javascriptErrors']=js_errors;(HERE/'alkane12-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def wait(expr,sec=20):
 end=time.monotonic()+sec
 while time.monotonic()<end:
  if ev(expr):return
  time.sleep(.1)
 raise AssertionError('Timeout '+expr)
def check(ok,label):
 assert ok,label
 out['checks'].append(label);save();print('PASS '+label,flush=True)
def shot(label):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(label+'.png')).write_bytes(base64.b64decode(r['data']))
def ready():
 app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',45)
def pause(ms=850):ev('new Promise(r=>setTimeout(()=>r(true),'+str(ms)+'))')
def pointer_at(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'prefix-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def pointer(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});true');pause(120)
 p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()');assert p['hit'] and not p['disabled'],(selector,p);pointer_at(p)
def wheel(delta):
 p=read('(()=>{const d=document.getElementById("nlQuizDialog").getBoundingClientRect(),h=document.querySelector("#nlQuizDialog .nl-quiz-dialog-header").getBoundingClientRect();return{x:Math.round(d.x+d.width*.65),y:Math.round(h.bottom+(d.bottom-h.bottom)*.6)}})()');call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'prefix-wheel','actions':[{'type':'scroll','x':p['x'],'y':p['y'],'deltaX':0,'deltaY':int(delta),'duration':100}]}]});pause(140)
def quiz_pointer(selector):
 for _ in range(24):
  p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),d=document.getElementById("nlQuizDialog").getBoundingClientRect(),h=document.querySelector("#nlQuizDialog .nl-quiz-dialog-header").getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,headerBottom:h.bottom,dialogBottom:d.bottom,hit:e===hit||e.contains(hit),disabled:e.disabled}})()')
  if p['top']>=p['headerBottom']+3 and p['bottom']<=p['dialogBottom']-3 and p['hit'] and not p['disabled']:pointer_at(p);return
  wheel(-220 if p['top']<p['headerBottom']+3 else 220)
 raise AssertionError('Cannot reach '+selector+' '+str(p))
def visible(id):return ev('(()=>{const e=document.getElementById('+json.dumps(id)+'),r=e?.getBoundingClientRect();return !!r&&r.width>0&&r.height>0&&getComputedStyle(e).visibility!=="hidden"})()')
def receipt():return read('(()=>{const s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16);return{key,content,record:JSON.parse(sessionStorage.getItem(key)||"null")}})()')
def seed(index,value):
 i=receipt();r=i['record'] or {'version':1,'content':i['content'],'states':{}};r['states'][str(index)]={'version':1,'seed':value,'currentRound':0,'states':[None,None,None],'solved':False}
 ev('sessionStorage.setItem('+json.dumps(i['key'])+','+json.dumps(json.dumps(r,ensure_ascii=False,separators=(',',':')))+');true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def dismiss_rotate():
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):ev('document.getElementById("rotatePromptDismiss").click();true')
def step(index):
 wait('fScenarioPresent().index==='+str(index)+'&&!MuLERMoCScenario.checkpointPreparation',25)
 out['lessonSteps'].append(read('({step:fScenarioPresent().index+1,title:document.getElementById("pageTitle").textContent.trim(),selectedMol,mode2D,nextDisabled:document.getElementById("scNext").disabled})'));save()
def next_step(index):pointer('#scNext');step(index)
def checkpoint(index,label):
 check(ev('document.getElementById("pageContainer").classList.contains("scContentOnly")') and all(not visible(x) for x in ['viewerCol','analysisCol','menuCol','jsmeNomeclatureSVG','nomeclature3D']),label+' hides molecular view/name/menu')
 wait('!!document.querySelector("#pageTitle img")&&document.querySelector("#pageTitle img").complete&&document.querySelector("#pageTitle img").naturalWidth>0',12)
 check(visible('nlQuizCheckpoint') and visible('scStepText') and ev('document.getElementById("scNext").disabled'),label+' shows loaded logo/instructions/card and blocks Next');shot(label)
def quiz_top(label):
 g=read('(()=>{const d=document.getElementById("nlQuizDialog"),h=d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),title=d.querySelector(".round-heading h1").getBoundingClientRect(),objective=d.querySelector(".round-heading p").getBoundingClientRect();return{scroll:d.scrollTop,headerBottom:h.bottom,titleTop:title.top,objectiveTop:objective.top,progress:document.getElementById("nlQuizProgress").textContent,dialog:d.getBoundingClientRect().toJSON(),width:innerWidth,documentWidth:document.documentElement.scrollWidth}})()');out.setdefault('quizGeometry',[]).append({'label':label,**g});check(abs(g['scroll'])<1 and g['titleTop']>=g['headerBottom'] and g['objectiveTop']>=g['headerBottom'],label+' new round starts at top below fixed header');check(g['dialog']['left']>=0 and g['dialog']['right']<=g['width'] and g['documentWidth']<=g['width'],label+' quiz stays within viewport');return g
def solve_gate(index,set_id,seed_value):
 seed(index,seed_value);dismiss_rotate();pointer('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45);quiz_top('s'+str(index+1)+' entry')
 for ri,f in enumerate(games[seed_value][set_id]['rounds']):
  tag='step'+str(index+1)+'-round'+str(ri+1);check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ '+str(ri+1)+'/3',tag+' actual counter')
  if f['kind']=='replace':
   quiz_pointer('[id$="-part-'+f['targetPartId']+'"]');pause();correct=next(i for i,c in enumerate(f['choices']) if c['value']==f['correctValue']);quiz_pointer('[id$="-choice-'+str(correct)+'"]');pause()
  else:
   quiz_pointer('[id$="-part-'+f['correctOrder'][0]+'"]');pause();quiz_pointer('[id$="-move-left"]');pause()
  quiz_pointer('[id$="-check-button"]');wait('!!document.querySelector("#nlQuizDialog .feedback.is-success")',10);pause()
  check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(index)+')')==(ri==2),tag+' completion requires third actual repair');check(ev('document.getElementById("scNext").disabled')==(ri<2),tag+' normal Next lock follows earned completion')
  rec=receipt()['record']['states'][str(index)];out['rounds'].append({'step':index+1,'round':ri+1,'id':f['id'],'receipt':rec});shot(tag+'-success');save();quiz_pointer('#nlQuizDialog .round-next button')
  if ri<2:wait('document.getElementById("nlQuizProgress").textContent==='+json.dumps('Κουίζ '+str(ri+2)+'/3')+'&&!!document.querySelector("#nlQuizDialog .diagram-image.is-ready")',20);quiz_top(tag+' Continue')
  else:step(index+1)
def numbers():return read('[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].sort((a,b)=>Number(a.getAttribute("x"))-Number(b.getAttribute("x"))).map(e=>Number(e.textContent))')
def geometry(key,mode,width):
 pause(180);g=read('(()=>{const host=document.getElementById("jsmeNomeclatureSVG"),hr=host.getBoundingClientRect(),svg=host.querySelector("svg"),els=[...host.querySelectorAll("svg text,svg path,svg line,svg polyline,svg polygon,svg circle")].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=="none"&&s.visibility!=="hidden"&&(r.width>0||r.height>0)}),rects=els.map(e=>e.getBoundingClientRect()),b=rects.length?{left:Math.min(...rects.map(r=>r.left)),top:Math.min(...rects.map(r=>r.top)),right:Math.max(...rects.map(r=>r.right)),bottom:Math.max(...rects.map(r=>r.bottom))}:null;return{key:selectedMol,mode:mode2D,width:innerWidth,pageWidth:document.documentElement.scrollWidth,host:hr.toJSON(),drawing:b,svg:!!svg,atoms:allAtomsTypeList.length,name:currentMolName}})()');out['geometry'].append(g);check(g['key']==key and g['mode']==mode and g['svg'] and g['drawing'] is not None,key+' '+mode+' rendered '+str(width));b=g['drawing'];h=g['host'];fits=b['left']>=h['left']-4 and b['right']<=h['right']+4 and b['top']>=h['top']-4 and b['bottom']<=h['bottom']+4 and g['pageWidth']<=width
 if not fits:out.setdefault('geometryExceptions',[]).append(g)
 save();return fits
try:
 cr=CR
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1});navigate('design/welcome-proposal.html?v=v55-browser');pointer('.card.one a.action');wait('location.pathname.endsWith("theory-library.html")');check(ev('document.querySelector("article[aria-labelledby=alkanes-title] a.action").href').startswith(proc['base_url']),'Copied library alkane link resolves inside nested prefix');pointer('article[aria-labelledby=alkanes-title] a.action');ready();step(0)
 out['environment']=read('({userAgent:navigator.userAgent,url:location.href,jsmolVersion:Jmol._version,jquery:$.fn.jquery})');check(ev('!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Normal learner presentation mode loaded from copied library')
 for i in [1,2,3]:next_step(i)
 checkpoint(3,'step4-desktop');ev('fScenarioGo(11);true');wait('fScenarioPresent().index===3');check(ev('document.getElementById("scNext").disabled'),'Unsolved gate4 rejects forward jump');solve_gate(3,'alkanes-unbranched','4');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();step(4);check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'), 'Actual refresh preserves first three earned repairs')
 wait('!!document.getElementById("scChainNavigation")');before=ev('mainChainPoolIdx');pointer('#chainNextBtn');check(ev('mainChainPoolIdx')!=before,'Step5 second equivalent chain selectable');pointer('#chainPrevBtn');check(ev('mainChainPoolIdx')==before,'Step5 original chain restored');shot('step5-chain')
 next_step(5);next_step(6);wait('!!document.getElementById("scNumberingRight")');wait('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===4');check(numbers()==[1,2,3,4],'Step7 initial numbering left to right');pointer('#scNumberingRight');check(numbers()==[4,3,2,1],'Step7 opposite direction labels rendered');pointer('#scNumberingLeft');check(numbers()==[1,2,3,4],'Step7 left direction restored');shot('step7-directions')
 for i in [7,8,9,10]:next_step(i)
 checkpoint(10,'step11-desktop');ev('fScenarioGo(11);true');wait('fScenarioPresent().index===10');check(ev('document.getElementById("scNext").disabled'),'Unsolved gate11 rejects final-step jump')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':760},'devicePixelRatio':1});dismiss_rotate();checkpoint(10,'step11-mobile390');check(ev('document.documentElement.scrollWidth<=innerWidth'),'Step11 mobile390 no horizontal overflow');solve_gate(10,'alkanes-branched','1')
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)&&!document.getElementById("nlQuizDialog").open'),'All6 actual repairs persisted; Continue enters final step12')
 check(visible('viewerCol') and visible('analysisCol') and visible('nomeclature3D') and not visible('nlQuizCheckpoint'),'Step12 restores molecular exploration and3D pane')
 keys=read('fScenarioPresent().steps[11].menuSubset');check(len(keys)==8 and all(ev('!!document.getElementById('+json.dumps(k)+')') for k in keys),'All8 final alkane menu controls present')
 for width,height in [(1280,800),(390,760)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});dismiss_rotate()
  for key in keys:
   pointer('#'+key);wait('selectedMol==='+json.dumps(key),15);wait('!!document.querySelector("#jsmeNomeclatureSVG svg")',15)
   modes=['condensed','expanded']+([] if key=='methane' else ['skeletal'])
   if key=='methane':check(ev('document.querySelectorAll("#radio2DMode .mode2DOption")[2].classList.contains("disabledRadio")&&!nameExamples.methane.structure2D_Skeletal'),'Methane has no skeletal representation '+str(width))
   for mode in modes:
    idx={'condensed':1,'expanded':2,'skeletal':3}[mode];pointer('#radio2DMode .mode2DOption:nth-child('+str(idx)+')');wait('mode2D==='+json.dumps(mode),12);geometry(key,mode,width)
   if width==1280:
    file=ev('nameExamples['+json.dumps(key)+'].file3D');expected=int((cr/file).read_text().splitlines()[3][:3])
    wait('(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length==='+str(expected)+'}catch(e){return false}})()',35)
    model=read('({key:selectedMol,file:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length})');model['expectedFromSourceSDF']=expected;out['models3D'].append(model);check(True,key+' prefixed3D model URL and sourceSDF atom count loaded')
  shot('step12-'+str(width))
 check(not out.get('geometryExceptions'),'All46 available2D representations bounded at desktop1280/mobile390')
 check(len(out['models3D'])==8,'All8 actual3D models loaded from copied prefix')
 pointer('#zoomInBtn');pointer('#zoomOutBtn');check(ev('selectedMol==="ethyl_3_dimethyl_2_5_hexane"&&mode2D==="skeletal"'),'Mobile final viewer zoom pair retains molecule/mode');pointer('#scPrev');step(10);check(not ev('document.getElementById("scNext").disabled'),'Completed workshop11 replay remains unlocked');pointer('#scNext');step(11);check(visible('viewerCol') and visible('nomeclature3D'),'Completed11→12 replay restores viewer panes')
 out['resources']=read('performance.getEntriesByType("resource").map(r=>({name:r.name,initiatorType:r.initiatorType,duration:r.duration,transferSize:r.transferSize,responseStatus:r.responseStatus}))');out['finalReceipt']=receipt();pointer('#scExit');wait('location.pathname==='+json.dumps('/organic-nomenclature-3/design/theory-library.html'),15);check(ev('!!document.querySelector("article[aria-labelledby=alkanes-title]")'),'Normal Exit returns to copied prefixed library');out['exitURL']=ev('location.href');shot('exit-library');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureURL']=ev('location.href');shot('failure');out['resourcesAtFailure']=read('performance.getEntriesByType("resource").map(r=>({name:r.name,initiatorType:r.initiatorType,duration:r.duration,transferSize:r.transferSize,responseStatus:r.responseStatus}))')
 except Exception as e:out['captureFailure']=str(e)
finally:
 try:save()
 finally:
  try:call('browsingContext.close',{'context':ctx})
  finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'rounds':len(out['rounds']),'forms':len(out['geometry']),'models3D':len(out['models3D']),'errors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
