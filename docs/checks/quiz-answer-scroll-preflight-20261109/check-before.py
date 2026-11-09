"""Read-only geometry around two actual quiz rounds; no app hooks or source edits."""
from pathlib import Path
import os,json,time,traceback,hashlib,base64
HERE=Path('docs/checks/quiz-answer-scroll-preflight-20261109');proc=json.loads((HERE/'process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(15)'),'owned-headless-bidi','exec'))
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());fixture=next(s['rounds'][0] for g in fixtures if g['seed']=='4' for s in g['sets'] if s['id']=='alkanes-unbranched')
out={'completed':False,'date':'2026-11-09','role':'Developer preflight geometry evidence, not independent review','scope':'No production edits, hooks, extraUIlisteners or round API overrides. Separate owned headless, two actual rounds total; all answer actions use native pointer input and natural wheel to visible controls. Unsolved seed4 only.','runs':[],'sources':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['js/namelecule-game-repair.js','js/namelecule-quiz-checkpoints.js','css/namelecule-quiz-checkpoints.css','scenarios/alkanes-user-3.scenario.json']}}
def save():out['javascriptErrors']=js_errors;(HERE/'before.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def wait(x,sec=20):
 end=time.monotonic()+sec
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.1)
 raise AssertionError('Timeout '+x)
def ready():
 app_ready();wait('fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',40)
def seed_unsolved():
 ev('(()=>{const s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16),r=JSON.parse(sessionStorage.getItem(key)||"null")||{version:1,content,states:{}};r.states[3]={version:1,seed:"4",currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(key,JSON.stringify(r));return true})()');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def geometry():return read('''(()=>{const d=document.getElementById('nlQuizDialog'),host=document.getElementById('nlQuizHost'),h=d?.querySelector('.nl-quiz-dialog-header'),hr=h?.getBoundingClientRect(),dr=d?.getBoundingClientRect(),top=hr?.bottom||0,bottom=Math.min(dr?.bottom||innerHeight,innerHeight),sels=['.round-heading p','.name-parts','.part-selection-status','.choice-fieldset','.choices','.candidate','.repair-actions','.feedback','.success-explanation','.round-next button'];return{time:new Date().toISOString(),step:fScenarioPresent().index,progress:document.getElementById('nlQuizProgress')?.textContent,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},active:{tag:document.activeElement?.tagName,id:document.activeElement?.id},dialog:d?{open:d.open,scrollTop:d.scrollTop,clientHeight:d.clientHeight,scrollHeight:d.scrollHeight,overflowY:getComputedStyle(d).overflowY,rect:dr.toJSON()}:null,host:host?{scrollTop:host.scrollTop,clientHeight:host.clientHeight,scrollHeight:host.scrollHeight,overflowY:getComputedStyle(host).overflowY}:null,documentScrollTop:document.scrollingElement.scrollTop,header:hr?.toJSON(),usable:{top,bottom,height:bottom-top},elements:sels.map(sel=>{const e=d?.querySelector(sel);if(!e)return{selector:sel,present:false};const r=e.getBoundingClientRect(),s=getComputedStyle(e),displayed=r.width>0&&r.height>0&&s.visibility!=='hidden',visible=displayed?Math.max(0,Math.min(r.bottom,bottom)-Math.max(r.top,top)):0;return{selector:sel,present:true,displayed,text:e.textContent,rect:r.toJSON(),visibleHeight:visible,fullyVisible:displayed&&r.top>=top&&r.bottom<=bottom,clippedTop:displayed?Math.max(0,top-r.top):0,clippedBottom:displayed?Math.max(0,r.bottom-bottom):0,display:s.display}})}})()''')
def record(run,label,before=None):
 time.sleep(.15);g=geometry();m={'label':label,'geometry':g}
 if before is not None:m['beforeActualClick']=before
 run['stages'].append(m);save();r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(str(run['width'])+'-'+label+'.png')).write_bytes(base64.b64decode(r['data']));print(json.dumps({'width':run['width'],'stage':label,'scrollTop':g['dialog']['scrollTop'],'elements':[{k:e.get(k) for k in ['selector','displayed','visibleHeight','fullyVisible','clippedBottom']} for e in g['elements'] if e['selector'] in ['.part-selection-status','.choices','.candidate','.feedback','.round-next button']]},ensure_ascii=False),flush=True)
def pointer_at(e):
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'answer-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':e['x'],'y':e['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def plain_pointer(sel):
 ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center"});true');p=read('(()=>{const e=document.querySelector('+json.dumps(sel)+'),r=e.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h)}})()');assert p['hit'];pointer_at(p)
def wheel(delta):
 p=read('(()=>{const d=document.getElementById("nlQuizDialog").getBoundingClientRect(),h=document.querySelector("#nlQuizDialog .nl-quiz-dialog-header").getBoundingClientRect();return{x:Math.round(d.x+d.width*.65),y:Math.round(h.bottom+(d.bottom-h.bottom)*.6)}})()');call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'answer-wheel','actions':[{'type':'scroll','x':p['x'],'y':p['y'],'deltaX':0,'deltaY':int(delta),'duration':100}]}]});time.sleep(.12)
def pointer(sel):
 for _ in range(22):
  p=read('(()=>{const e=document.querySelector('+json.dumps(sel)+'),r=e.getBoundingClientRect(),d=document.getElementById("nlQuizDialog"),dr=d.getBoundingClientRect(),h=d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,headerBottom:h.bottom,dialogBottom:dr.bottom,hit:e===hit||e.contains(hit),disabled:e.disabled}})()')
  if p['top']>=p['headerBottom']+3 and p['bottom']<=p['dialogBottom']-3 and p['hit'] and not p['disabled']:
   before=geometry();pointer_at(p);return before
  wheel(-220 if p['top']<p['headerBottom']+3 else 220)
 raise AssertionError('Cannot reach '+sel+' '+str(p))
try:
 for width,height,dpr in [(1280,650,2),(390,760,1)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':dpr});navigate('design/theory-library.html?v=answer-scroll-preflight-'+str(width));ev('document.querySelector("article[aria-labelledby=alkanes-title] a.action").click();true');ready();ev('fScenarioGo(3);true');wait('fScenarioPresent().index===3',12);seed_unsolved()
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  run={'width':width,'height':height,'dpr':dpr,'fixtureId':fixture['id'],'stages':[]};out['runs'].append(run);plain_pointer('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45)
  assert ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3'
  assert ev('document.querySelector("#nlQuizDialog .broken-name").textContent')==''.join(p['text'] for p in fixture['parts'])
  record(run,'initial-open')
  wrong=next(p['id'] for p in fixture['parts'] if p['id']!=fixture['targetPartId']);b=pointer('[id$="-part-'+wrong+'"]');record(run,'agreeing-component-feedback',b)
  b=pointer('[id$="-part-'+fixture['targetPartId']+'"]');record(run,'target-reveals-choices',b)
  original=next(p['text'] for p in fixture['parts'] if p['id']==fixture['targetPartId']);wrong_i=next(i for i,c in enumerate(fixture['choices']) if c['value']!=fixture['correctValue'] and c['value']!=original)
  b=pointer('[id$="-choice-'+str(wrong_i)+'"]');record(run,'incorrect-replacement-candidate',b)
  b=pointer('[id$="-check-button"]');wait('!!document.querySelector("#nlQuizDialog .feedback:not(.is-success)")&&document.querySelector("#nlQuizDialog .feedback").textContent.length>0',8);record(run,'incorrect-check-feedback',b)
  correct_i=next(i for i,c in enumerate(fixture['choices']) if c['value']==fixture['correctValue']);b=pointer('[id$="-choice-'+str(correct_i)+'"]');record(run,'correct-replacement-candidate',b)
  b=pointer('[id$="-check-button"]');wait('!!document.querySelector("#nlQuizDialog .feedback.is-success")',8);record(run,'correct-check-success-explanation-continue',b)
  assert not ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)')
  run['oneActualRepairSolved']=True;run['gateStillBlocked']=ev('document.getElementById("scNext").disabled');run['completed']=True;save()
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureGeometry']=geometry();r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/'harness-failure.png').write_bytes(base64.b64decode(r['data']))
 except Exception as e:out['captureFailure']=str(e)
finally:
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'rounds':len(out['runs']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']:raise SystemExit(1)
