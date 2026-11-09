"""Owned GUI Workshop diagnosis; keep the single BiDi connection alive for handoff."""
from pathlib import Path
import os,json,hashlib,time,traceback,sys,base64
HERE=Path('docs/checks/firefox-workshop-freeze-20261109')
proc=json.loads((HERE/'process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
helper=Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(12)')
helper=helper.replace("call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})",'')
exec(compile(helper,'owned-gui-bidi','exec'))
windows=call('browser.getClientWindows',{})['clientWindows'];assert len(windows)==1;window=windows[0]['clientWindow']
proc.update({'context':ctx,'clientWindow':window,'connectionPolicy':'Single live Python driver/WebSocket; do not exit driver before handoff'})
(HERE/'process.json').write_text(json.dumps(proc,indent=2)+'\n')
report={'completed':False,'runs':[],'sourceSHA256':hashlib.sha256(Path('scenarios/alkanes-user-3.scenario.json').read_bytes()).hexdigest(),'scope':'Own fresh GUI; native fullscreen command, not actual physical green-button hover; actual trusted pointer Workshop interaction; author preview11; application source unchanged','limitations':['Same new profile, new page per run; browser resource cache can warm after first run','Instrumentation changes only owned page; promise wrappers and logging may affect scheduling','No existing Firefox493/55879 interaction; cannot establish what happened there']}
def save():
 report['javascriptErrors']=list(js_errors);(HERE/'matrix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def emit(v):print(json.dumps(v,ensure_ascii=False),flush=True)
def stage(run,label,extra=None):
 item={'stage':label,'seconds':round(time.monotonic()-run['_start'],3)}
 if extra is not None:item['detail']=extra
 run['stages'].append(item);emit({'run':run['label'],**item});save()
def wait(expr,seconds=15):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(expr):return
  time.sleep(.2)
 raise AssertionError('Timed out '+str(seconds)+'sec: '+expr)
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def status():
 return read('(()=>{const d=document.getElementById("nlQuizDialog"),im=document.querySelector("#nlQuizDialog .diagram-image");return{url:location.href,step:typeof fScenarioPresent==="function"?fScenarioPresent().index:null,dialogOpen:d?d.open:false,modal:d?d.matches(":modal"):false,active:document.activeElement?document.activeElement.id:null,visibility:document.visibilityState,focus:document.hasFocus(),viewport:{width:innerWidth,height:innerHeight},heart:window.__diag?{raf:__diag.raf,timers:__diag.timers,lastRAF:__diag.lastRAF,lastTimer:__diag.lastTimer}:null,image:im?{src:im.currentSrc,complete:im.complete,naturalWidth:im.naturalWidth,className:im.className}:null,progress:document.getElementById("nlQuizProgress")?.textContent,hostBusy:document.getElementById("nlQuizHost")?.getAttribute("aria-busy"),error:document.querySelector("#nlQuizDialog .nl-quiz-error")?.textContent,round:window.__mountedRound?{id:__mountedRound.id,kind:__mountedRound.kind}:null}})()')
def pointer(sel):
 ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center",inline:"nearest"});true')
 p=read('(()=>{const e=document.querySelector('+json.dumps(sel)+'),r=e.getBoundingClientRect(),x=Math.round(r.left+r.width/2),y=Math.round(r.top+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,hit:hit?.id,hitClass:hit?.className,enabled:!e.disabled,target:e.id,receives:e===hit||e.contains(hit)}})()')
 assert p['receives'] and p['enabled'],{'selector':sel,'hitTest':p}
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'workshop-diagnostic-mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
 return p
instrument=r'''(()=>{
 const d=window.__diag={started:performance.now(),events:[],raf:0,timers:0,lastRAF:0,lastTimer:0};
 const log=(kind,info)=>{if(d.events.length<2500)d.events.push({t:Math.round(performance.now()-d.started),kind,info})};window.__diagLog=log;
 function frame(t){d.raf++;d.lastRAF=t;requestAnimationFrame(frame)}requestAnimationFrame(frame);
 setInterval(()=>{d.timers++;d.lastTimer=performance.now()},100);
 for(const name of ['pointerdown','pointerup','click','focusin','focusout'])document.addEventListener(name,e=>log(name,{id:e.target.id,cls:typeof e.target.className==='string'?e.target.className:'',trusted:e.isTrusted,active:document.activeElement?.id}),true);
 for(const name of ['visibilitychange','fullscreenchange'])document.addEventListener(name,()=>log(name,{visibility:document.visibilityState,fullscreen:!!document.fullscreenElement}));
 addEventListener('error',e=>log('error',{message:e.message,src:e.filename,line:e.lineno}),true);addEventListener('unhandledrejection',e=>log('unhandledrejection',{message:String(e.reason)}));
 const modal=HTMLDialogElement.prototype.showModal;HTMLDialogElement.prototype.showModal=function(){log('showModal-before',{id:this.id,active:document.activeElement?.id});const r=modal.apply(this,arguments);log('showModal-after',{open:this.open,modal:this.matches(':modal'),active:document.activeElement?.id});return r};
 const original=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,opts){window.__mountedRound=JSON.parse(JSON.stringify(opts.round));log('mountRound',{id:opts.round.id,kind:opts.round.kind});return original.apply(this,arguments)};
 const client=NameleculeChemistryClient;window.NameleculeChemistryClient=Object.freeze({analyze:function(m,o){const t=performance.now();log('analyze-start',{id:m.id});return client.analyze(m,o).then(r=>{log('analyze-ok',{id:m.id,ms:Math.round(performance.now()-t)});return r},e=>{log('analyze-error',{id:m.id,message:String(e),code:e.code});throw e})},verifyEngine:function(h,o){const t=performance.now();log('verify-start',{hash:h});return client.verifyEngine(h,o).then(r=>{log('verify-ok',{ms:Math.round(performance.now()-t)});return r},e=>{log('verify-error',{message:String(e)});throw e})}});
 let queued=false,last='';new MutationObserver(()=>{if(queued)return;queued=true;setTimeout(()=>{queued=false;const host=document.getElementById('nlQuizHost'),dialog=document.getElementById('nlQuizDialog'),img=host?.querySelector('.diagram-image');const info={open:dialog?.open,busy:host?.getAttribute('aria-busy'),text:host?.textContent.slice(0,250),image:img?{complete:img.complete,width:img.naturalWidth,cls:img.className}:null};const v=JSON.stringify(info);if(v!==last){last=v;log('modal-mutation',info)}},40)}).observe(document.body,{subtree:true,childList:true,attributes:true,characterData:true});
 log('instrumented',{visibility:document.visibilityState,focus:document.hasFocus()});return true})()'''
def snapshot(run,name):
 run.setdefault('snapshots',{})[name]=status()
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(run['label']+'-'+name+'.png')).write_bytes(base64.b64decode(r['data']))
 save()
def set_state(state):
 call('browsingContext.activate',{'context':ctx});call('browser.setClientWindowState',{'clientWindow':window,'state':state});time.sleep(.4)
 actual=call('browser.getClientWindows',{})['clientWindows'];assert any(w['clientWindow']==window and w['state']==state for w in actual);return actual

def run_one(state,cycle):
 run={'label':state+'-'+str(cycle),'windowState':state,'cycle':cycle,'stages':[],'_start':time.monotonic(),'completed':False};report['runs'].append(run);save()
 try:
  set_state(state);stage(run,'native-window-state-confirmed')
  navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=workshop-freeze-'+run['label'])
  wait("typeof jsmeNomeclatureApplet!=='undefined'&&!!jsmeNomeclatureApplet&&!!nameExamples.methyl_3_butene_1.classification",45)
  wait('fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',30)
  ev(instrument);stage(run,'fresh-page-ready')
  ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true')
  ev('document.querySelector(\'.scenarioPanel.active .srow[data-idx="10"] .scPresentStep\').click();true');wait('MuLERMoCScenario.present&&fScenarioPresent().index===10',12);stage(run,'author-preview11-ready',status())
  stage(run,'open-pointer-hit',pointer('#nlQuizOpen'))
  wait('!!document.querySelector("#nlQuizDialog[open]")',6);stage(run,'dialog-open',status())
  wait('!!window.__mountedRound&&!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',50);stage(run,'generation-and-image-ready',status());snapshot(run,'opened')
  # Exercise a genuine answer; if first round is ordering, reach a replacement
  # by its normal successful continuation, with at most three actual repairs.
  for ri in range(3):
   r=read('__mountedRound');stage(run,'round-'+str(ri+1)+'-kind',{'kind':r['kind'],'id':r['id']})
   if r['kind']=='replace':
    p=pointer('[id$="-part-'+r['targetPartId']+'"]');stage(run,'part-pointer-hit',p)
    i=next(i for i,c in enumerate(r['choices']) if c['value']==r['correctValue']);stage(run,'choice-pointer-hit',pointer('[id$="-choice-'+str(i)+'"]'))
   else:
    stage(run,'order-part-pointer-hit',pointer('[id$="-part-'+r['correctOrder'][0]+'"]'));stage(run,'order-move-pointer-hit',pointer('[id$="-move-left"]'))
   stage(run,'check-pointer-hit',pointer('[id$="-check-button"]'));wait('!!document.querySelector("#nlQuizDialog .feedback.is-success")',6);stage(run,'success-feedback',status())
   if r['kind']=='replace':run['replacementUIVerified']=True;break
   if ri<2:pointer('#nlQuizDialog .round-next button');wait('!!document.querySelector("#nlQuizDialog .diagram-image.is-ready")&&__mountedRound.id!=='+json.dumps(r['id']),15)
  snapshot(run,'answered');before=read('({raf:__diag.raf,timers:__diag.timers})');time.sleep(.7);after=read('({raf:__diag.raf,timers:__diag.timers})')
  assert after['raf']>before['raf'] and after['timers']>before['timers'];stage(run,'raf-and-timer-live',{'before':before,'after':after})
  stage(run,'close-pointer-hit',pointer('#nlQuizBack'));wait('!document.getElementById("nlQuizDialog").open',5)
  stage(run,'reopen-pointer-hit',pointer('#nlQuizOpen'));wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',15);stage(run,'modal-reopened-ready',status());snapshot(run,'reopened')
  run['completed']=True
 except Exception:
  run['failure']=traceback.format_exc();emit({'run':run['label'],'failure':run['failure']})
  try:snapshot(run,'failure')
  except Exception as e:run['captureFailure']=str(e)
 finally:
  try:
   run['pageEvents']=read('__diag.events');run['resourceTimings']=read('performance.getEntriesByType("resource").filter(e=>/worker|chemistry|alkane|svg/.test(e.name)).map(e=>({name:e.name,duration:e.duration,transferSize:e.transferSize,decodedBodySize:e.decodedBodySize}))');run['finalStatus']=status()
  except Exception as e:run['traceCaptureError']=str(e)
  run['elapsedSeconds']=round(time.monotonic()-run.pop('_start'),3);save()
 return run

try:
 assert report['sourceSHA256']=='607a530a2d3ba151026517c61d6f7a31644e15abf82a687e778b7453d80089b7'
 for cycle in [1,2]:
  for state in ['normal','fullscreen']:
   run=run_one(state,cycle)
   if not run['completed']:raise RuntimeError('Bounded matrix stopped on first failed run')
 report['completed']=True;save();emit({'matrixCompleted':True,'runs':len(report['runs']),'pageJSErrors':len(js_errors)})
except Exception:
 report['failure']=traceback.format_exc();save();emit({'matrixCompleted':False,'failure':report['failure']})
# Keep the single live WebSocket and browser available for physical-user tests.
emit({'DRIVER_READY':True,'process':proc,'status':status(),'commands':['status','eval(expression)','pointer(selector)','window(state)','screenshot(name)','fresh-preview','close-dialog','quit']})
for line in sys.stdin:
 try:
  q=json.loads(line);op=q.get('op')
  if op=='status':answer={'status':status(),'windows':call('browser.getClientWindows',{})['clientWindows']}
  elif op=='eval':answer={'value':ev(q['expression'])}
  elif op=='pointer':answer=pointer(q['selector'])
  elif op=='window':answer={'windows':set_state(q['state'])}
  elif op=='screenshot':
   name=q.get('name','manual');assert name.replace('-','').replace('_','').isalnum();r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});path=HERE/(name+'.png');path.write_bytes(base64.b64decode(r['data']));answer={'path':str(path),'status':status()}
  elif op=='fresh-preview':
   navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=workshop-manual-'+str(int(time.time())));wait('typeof jsmeNomeclatureApplet!=="undefined"&&!!jsmeNomeclatureApplet&&fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")',45);ev(instrument);ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();document.querySelector(\'.scenarioPanel.active .srow[data-idx="10"] .scPresentStep\').click();true');wait('MuLERMoCScenario.present&&fScenarioPresent().index===10',12);answer={'status':status()}
  elif op=='close-dialog':ev('document.getElementById("nlQuizDialog")?.close();true');answer={'status':status()}
  elif op=='quit':
   save();call('session.end',{});emit({'driverClosed':True,'browserMayRemain':True});break
  else:raise ValueError('Unknown op')
  emit({'ok':True,'op':op,'answer':answer})
 except Exception:emit({'ok':False,'error':traceback.format_exc()})
# No implicit browser shutdown. Root owns subsequent physical test and cleanup.
