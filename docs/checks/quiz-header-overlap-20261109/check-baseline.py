from pathlib import Path
import json,os,time,traceback,base64,hashlib
HERE=Path('docs/checks/quiz-header-overlap-20261109');proc=json.loads((HERE/'process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
helper=Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(15)');exec(compile(helper,'owned-headless-bidi','exec'))
out={'completed':False,'scope':'Baseline reproduction only, no production/CSS prototype. Separate owned headless; GUI56371 and driver21029 untouched. Actual trusted repair/Continue/wheel controls; author preview11, no solved-receipt fabrication.','runs':[],'sourceSHA256':hashlib.sha256(Path('scenarios/alkanes-user-3.scenario.json').read_bytes()).hexdigest()}
def save():out['javascriptErrors']=js_errors;(HERE/'baseline.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def wait(x,sec=15):
 end=time.monotonic()+sec
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.1)
 raise AssertionError('Timeout '+x)
def screenshot_view(name):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(name+'.png')).write_bytes(base64.b64decode(r['data']))
def measure():return read('''(()=>{const d=document.getElementById('nlQuizDialog'),header=d?.querySelector('.nl-quiz-dialog-header'),h=header?.getBoundingClientRect(),elements=['.nl-quiz-host','.nl-quiz-set-progress','.round-topbar','.round-heading','.round-heading h1','.round-heading p','.compact-steps','.round-next button'].map(sel=>{const e=d?.querySelector(sel);if(!e)return{selector:sel,present:false};const r=e.getBoundingClientRect(),y=Math.max(r.top+(Math.min(r.height,18)/2),0),x=r.left+r.width/2,hit=document.elementFromPoint(x,y),s=getComputedStyle(e);return{selector:sel,present:true,text:e.textContent,rect:r.toJSON(),headerOverlapPx:h?Math.max(0,Math.min(r.bottom,h.bottom)-Math.max(r.top,h.top)):0,belowStickyHeader:h?r.top>=h.bottom:false,visibleBelowHeaderPx:h?Math.max(0,Math.min(r.bottom,d.getBoundingClientRect().bottom)-Math.max(r.top,h.bottom)):null,sampleHitId:hit?.id,sampleHitClass:typeof hit?.className==='string'?hit.className:null,sampleHitsSelf:e===hit||e.contains(hit),scrollTop:e.scrollTop,styles:{position:s.position,top:s.top,zIndex:s.zIndex,scrollMarginTop:s.scrollMarginTop}}});return{time:new Date().toISOString(),step:fScenarioPresent().index,round:window.testMounted?{id:testMounted.id,kind:testMounted.kind,objective:testMounted.objective}:null,progress:document.getElementById('nlQuizProgress')?.textContent,dialog:d?{open:d.open,scrollTop:d.scrollTop,clientHeight:d.clientHeight,scrollHeight:d.scrollHeight,rect:d.getBoundingClientRect().toJSON()}:null,header:header?{rect:h.toJSON(),style:{position:getComputedStyle(header).position,top:getComputedStyle(header).top,zIndex:getComputedStyle(header).zIndex}}:null,hostScrollTop:document.getElementById('nlQuizHost')?.scrollTop,active:{tag:document.activeElement?.tagName,id:document.activeElement?.id,text:document.activeElement?.textContent?.slice(0,140)},viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},elements}})()''')
def wheel(delta):
 p=read('(()=>{const d=document.getElementById("nlQuizDialog").getBoundingClientRect(),h=document.querySelector("#nlQuizDialog .nl-quiz-dialog-header").getBoundingClientRect();return{x:Math.round(d.left+d.width*.65),y:Math.round(h.bottom+(d.bottom-h.bottom)*.6)}})()')
 call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'diagnostic-wheel','actions':[{'type':'scroll','x':p['x'],'y':p['y'],'deltaX':0,'deltaY':int(delta),'duration':100}]}]});time.sleep(.12)
def pointer(selector):
 for _ in range(22):
  p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),d=document.getElementById("nlQuizDialog"),dr=d.getBoundingClientRect(),h=d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),x=Math.round(r.left+r.width/2),y=Math.round(r.top+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,headerBottom:h.bottom,dialogBottom:dr.bottom,hit:e===hit||e.contains(hit),disabled:e.disabled}})()')
  if p['top']>=p['headerBottom']+3 and p['bottom']<=p['dialogBottom']-3 and p['hit'] and not p['disabled']:
   call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'repair-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});return
  wheel(-220 if p['top']<p['headerBottom']+3 else 220)
 raise AssertionError('Could not wheel into view '+selector+' '+str(p))
def mark(run,label):
 m=measure();run['measurements'].append({'label':label,**m});save();print(json.dumps({'width':run['width'],'label':label,'round':m['progress'],'scroll':m['dialog']['scrollTop'],'headingTop':next((e['rect']['top'] for e in m['elements'] if e['selector']=='.round-heading' and e['present']),None),'objectiveTop':next((e['rect']['top'] for e in m['elements'] if e['selector']=='.round-heading p' and e['present']),None),'headerBottom':m['header']['rect']['bottom']},ensure_ascii=False),flush=True);screenshot_view(str(run['width'])+'-'+label)
 return m
try:
 for width,height,dpr in [(1280,650,2),(390,760,1)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':dpr})
  run={'width':width,'height':height,'dpr':dpr,'measurements':[],'repairs':[]};out['runs'].append(run);save()
  navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=header-overlap-baseline-'+str(width));app_ready();wait('fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',30)
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  ev('window.testNativeClicks=[];document.addEventListener("click",e=>testNativeClicks.push({id:e.target.id,cls:e.target.className,trusted:e.isTrusted,t:performance.now()}),true);window.testOriginalMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,o){window.testMounted=JSON.parse(JSON.stringify(o.round));return testOriginalMount(host,o)};fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();document.querySelector(\'.scenarioPanel.active .srow[data-idx="10"] .scPresentStep\').click();document.getElementById("nlQuizOpen").click();true')
  wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testMounted',45);mark(run,'initial-open')
  # Natural wheel can place any ordinary content behind a sticky header.
  for _ in range(5):
   current=measure();obj=next(e for e in current['elements'] if e['selector']=='.round-heading p');hb=current['header']['rect']['bottom'];delta=obj['rect']['top']-hb+8
   if abs(delta)<3:break
   wheel(delta)
  mark(run,'manual-scroll-objective-under-header')
  wheel(-2000);mark(run,'manual-scroll-return-top')
  for round_index in [1,2]:
   r=read('testMounted')
   if r['kind']=='replace':
    pointer('[id$="-part-'+r['targetPartId']+'"]');i=next(i for i,c in enumerate(r['choices']) if c['value']==r['correctValue']);pointer('[id$="-choice-'+str(i)+'"]')
   else:pointer('[id$="-part-'+r['correctOrder'][0]+'"]');pointer('[id$="-move-left"]')
   pointer('[id$="-check-button"]');wait('!!document.querySelector("#nlQuizDialog .feedback.is-success")',8);run['repairs'].append({'index':round_index,'id':r['id'],'kind':r['kind'],'actualSuccess':True});mark(run,'round'+str(round_index)+'-solved-before-continue')
   pointer('#nlQuizDialog .round-next button');wait('!!document.querySelector("#nlQuizDialog .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(r['id']),15);mark(run,'after-continue-to-round'+str(round_index+1))
   if round_index==1:
    # Reopen mid-set, without scrolling the dialog toward its top first.
    # The native Back control is sticky and visible, so direct trusted input
    # at its center preserves the inherited scroll position.
    p=read('(()=>{const r=document.getElementById("nlQuizBack").getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()');call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'repair-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
    wait('!document.getElementById("nlQuizDialog").open',5);ev('document.getElementById("nlQuizOpen").click();true');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',15);mark(run,'reopened-midset-round2')
  run['nativeClicks']=read('testNativeClicks');run['completed']=True;save()
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:screenshot_view('harness-failure');out['failureMeasurement']=measure()
 except Exception as e:out['captureFailure']=str(e)
finally:
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'diagnosticCompleted':out['completed'],'runs':len(out['runs']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']:raise SystemExit(1)
