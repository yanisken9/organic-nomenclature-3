from pathlib import Path
import json,os,time,traceback,base64,hashlib
HERE=Path('docs/checks/quiz-round-scroll-20261109/browser');proc=json.loads((HERE/'process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
helper=Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(15)');exec(compile(helper,'owned-headless-bidi','exec'))
out={'completed':False,'scope':'Approved scrollfix verification only. Normal learner library→gate4 desktop→gate11 mobile→12. Separate owned headless; GUI56371/driver21029 untouched. Unsolved seed fixtures only; six actual trusted UI repairs.','runs':[],'sourceSHA256':hashlib.sha256(Path('scenarios/alkanes-user-3.scenario.json').read_bytes()).hexdigest()}
def save():out['javascriptErrors']=js_errors;(HERE/'browser-after.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
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
out['checks']=[];out['rounds']=[];out['sameRoundScroll']=[];out['limitations']=['Owned headless, not user GUI/freeze diagnosis','Viewportemulation1280×650/DPR2,390×760/DPR1 and320×700/DPR1, not physical mobile/Safari','Only normal learner checkpoint flow; root separately covers private callback invalid/stale/same-index guards','Desktop uses actual unbranched set and mobile actual branched set; baseline original clipping used generated branched set. Shared dialog lifecycle is exercised in both.']
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());games={g['seed']:{s['id']:s for s in g['sets']} for g in fixtures}
def check(ok,label):
 assert ok,label
 out['checks'].append(label);save();print('PASS '+label,flush=True)
def ready():
 app_ready();wait('fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',40)
 ev('''window.testReceiptInfo=function(){const s=fScenarioPresent();const content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16);return{key,content,record:JSON.parse(sessionStorage.getItem(key)||"null"))}}'''.replace('JSON.parse(sessionStorage.getItem(key)||"null"))','JSON.parse(sessionStorage.getItem(key)||"null")'))
 ev('window.testNativeClicks=[];document.addEventListener("click",e=>testNativeClicks.push({id:e.target.id,cls:e.target.className,trusted:e.isTrusted,t:performance.now(),dialogScrollTop:document.getElementById("nlQuizDialog")?.scrollTop}),true);window.testOriginalMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,o){window.testMounted=JSON.parse(JSON.stringify(o.round));return testOriginalMount(host,o)};true')
def seed(index,value):
 ev('(()=>{const i=testReceiptInfo();const r=i.record||{version:1,content:i.content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(i.key,JSON.stringify(r));return true})()')
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def plain_pointer(selector,scroll=False):
 if scroll:ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});true')
 p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),x=Math.round(r.left+r.width/2),y=Math.round(r.top+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:e.disabled}})()');assert p['hit'] and not p['disabled'],(selector,p)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'learner-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def open_quiz():
 plain_pointer('#nlQuizOpen',True);wait('!!window.testMounted&&!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45)
def current_state(index,ri):return read('testReceiptInfo().record.states['+str(index)+'].states['+str(ri)+']')
def clean_entry(run,label):
 m=mark(run,label);obj=next(e for e in m['elements'] if e['selector']=='.round-heading p');h1=next(e for e in m['elements'] if e['selector']=='.round-heading h1');hb=m['header']['rect']['bottom']
 check(abs(m['dialog']['scrollTop'])<.01 and obj['rect']['top']>=hb and h1['rect']['top']>=hb and obj['headerOverlapPx']==0,label+' starts atdialogTop0 with h1/objective fully belowstickyheader')
 return m
def same_round_action(selector,label):
 pointer(selector);click=read('testNativeClicks[testNativeClicks.length-1]');after=ev('document.getElementById("nlQuizDialog").scrollTop');out['sameRoundScroll'].append({'label':label,'beforeClick':click,'afterScrollTop':after})
 check(click['trusted'] and click['dialogScrollTop']>0 and after>0,label+' actualsame-round action keeps manually scrolled position awayfromtop')
try:
 check(hashlib.sha256(Path('js/namelecule-quiz-checkpoints.js').read_bytes()).hexdigest()=='35fda6953f06356d498f1be40fe4c6123d0c81c3bdbf81a60fa3fda5ea211501','Exact approvedcontroller revision tested')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':650},'devicePixelRatio':2})
 navigate('design/theory-library.html?v=quiz-round-scroll-20261109');ev('document.querySelector("article[aria-labelledby=alkanes-title] a.action").click();true');ready()
 check(ev('MuLERMoCScenario.present&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&fScenarioPresent().steps.length===12'),'Real12step learner flow fromlibrary')
 out['loadedCheckpointScript']=ev('[...document.scripts].find(s=>s.src.includes("namelecule-quiz-checkpoints.js"))?.src')
 ev('fScenarioGo(9);true');wait('fScenarioPresent().index===3',12)
 check(ev('document.getElementById("scNext").disabled'),'Prior gate4 cannotbebypassed')
 for step_index,set_id,seed_value,width,height,dpr in [(3,'alkanes-unbranched','4',1280,650,2),(10,'alkanes-branched','1',390,760,1)]:
  if step_index==10:
   ev('fScenarioGo(9);true');wait('fScenarioPresent().index===9',12);plain_pointer('#scNext',False);wait('fScenarioPresent().index===10',12)
   check(ev('document.getElementById("scNext").disabled&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Actualgate4 completion allows10→11 while11stillblocks12')
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':dpr})
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  seed(step_index,seed_value);wait('fScenarioPresent().index==='+str(step_index),15)
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  run={'width':width,'height':height,'dpr':dpr,'step':step_index+1,'setId':set_id,'measurements':[]};out['runs'].append(run);open_quiz();clean_entry(run,'initial-open')
  for ri,fixture in enumerate(games[seed_value][set_id]['rounds']):
   r=read('testMounted');check(r['id']==fixture['id'] and ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ '+str(ri+1)+'/3','Step'+str(step_index+1)+' actualround'+str(ri+1)+' andcounter')
   if r['kind']=='replace':
    pointer('[id$="-part-'+r['targetPartId']+'"]');i=next(i for i,c in enumerate(r['choices']) if c['value']==r['correctValue']);same_round_action('[id$="-choice-'+str(i)+'"]','Step'+str(step_index+1)+' round'+str(ri+1)+' choice')
   else:
    pointer('[id$="-part-'+r['correctOrder'][0]+'"]');same_round_action('[id$="-move-left"]','Step'+str(step_index+1)+' round'+str(ri+1)+' ordering')
   if ri==0:
    answer=current_state(step_index,ri);plain_pointer('#nlQuizBack');check(ev('!document.getElementById("nlQuizDialog").open&&document.getElementById("scNext").disabled'),'Returntotheory beforeanswercheck keepsgateblocked')
    open_quiz();clean_entry(run,'reopened-selected-round1');check(current_state(step_index,ri)==answer and ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','Reopenpreservesselectedanswer andcounter')
    if width==390:
     call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':320,'height':700},'devicePixelRatio':1});clean_entry(run,'resize320-sameround-top');check(current_state(step_index,ri)==answer,'320resize preservesactualselectedanswer')
     call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':760},'devicePixelRatio':1})
   same_round_action('[id$="-check-button"]','Step'+str(step_index+1)+' round'+str(ri+1)+' check');wait('!!document.querySelector("#nlQuizDialog .feedback.is-success")',8)
   check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(step_index)+')')==(ri==2),'Step'+str(step_index+1)+' gatecomplete onlyafter'+str(ri+1)+' actualrepairs')
   check(ev('document.getElementById("scNext").disabled')==(ri<2),'Step'+str(step_index+1)+' Nextlock matchesactualcompletion'+str(ri+1))
   out['rounds'].append({'step':step_index+1,'round':ri+1,'id':r['id'],'actualSuccess':True});mark(run,'round'+str(ri+1)+'-solved-before-continue')
   pointer('#nlQuizDialog .round-next button')
   if ri<2:
    wait('!!document.querySelector("#nlQuizDialog .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(r['id']),15);clean_entry(run,'after-continue-to-round'+str(ri+2))
   else:wait('fScenarioPresent().index==='+str(step_index+1),15)
  run['nativeClicks']=read('testNativeClicks');run['completed']=True;save()
 check(ev('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Bothactual3repairgates complete; normallearner reaches12')
 ev('new Promise(resolve=>setTimeout(()=>resolve(true),1000))');screenshot_view('mobile-final-step12');plain_pointer('#scExit',True);wait('location.pathname.endsWith("/design/theory-library.html")',12);check(True,'NormalReturn/Exit reacheslibrary')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:screenshot_view('harness-failure');out['failureMeasurement']=measure()
 except Exception as e:out['captureFailure']=str(e)
finally:
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'actualRepairs':len(out['rounds']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']:raise SystemExit(1)
