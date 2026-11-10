"""One actual generated wrong replacement followed by earned correction."""
from pathlib import Path
import os,json,time,hashlib,base64,traceback
H=Path(__file__).resolve().parent;ROOT=Path.cwd();STAGE='wrong-answer';P=json.loads((H/'process.json').read_text());T=json.loads((H.parent.parent/'verification-target.json').read_text())['files']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(ROOT/p)==v for p,v in T.items());os.environ['NAMELECULE_BIDI_PORT']=str(P['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=P['base_url'];exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'owned-mini-bidi','exec'));call('script.addPreloadScript',{'functionDeclaration':'() => { window.MULER_QUIET_FETCH = true; }','contexts':[ctx]})
FIX=json.loads((ROOT/'docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());f=next(s['rounds'][0]for g in FIX if g['seed']=='4'for s in g['sets']if s['id']=='alkanes-unbranched')
out={'completed':False,'role':'Developer bounded Reviewer supplement','checks':[],'actions':[],'scope':'One actual generated embedded unsolved round: correct target, incorrect nonoriginal replacement, Check, locked gate and safe feedback, then correct replacement and earned repair. No full six-round rerun.','targetHashes':T,'canonicalFixtureRoundId':f['id'],'fixtureSeed':'4'}
def save():
 out['javascriptErrors']=js_errors;(H/(STAGE+'-browser.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')

def read(x):return json.loads(ev('JSON.stringify('+x+')'))

def wait(x,seconds=30):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.1)
 raise AssertionError('Timeout '+x)

def pause(ms=750):ev('new Promise(r=>setTimeout(()=>r(true),'+str(ms)+'))')

def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});save();print('PASS '+label,flush=True)

def shot(label):
 result=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(H/(STAGE+'-'+label+'.png')).write_bytes(base64.b64decode(result['data']))

def ready():app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',45)

def pointer_at(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'presentation-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})

def plain(sel):
 ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(120);p=read('(()=>{let n=document.querySelector('+json.dumps(sel)+'),r=n.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:n===h||n.contains(h),disabled:!!n.disabled}})()');assert p['hit']and not p['disabled'],(sel,p);pointer_at(p)

def wheel(delta):
 p=read('(()=>{let d=document.getElementById("nlQuizDialog").getBoundingClientRect(),h=document.querySelector("#nlQuizDialog .nl-quiz-dialog-header").getBoundingClientRect();return{x:Math.round(d.x+d.width*.65),y:Math.round(h.bottom+(d.bottom-h.bottom)*.6)}})()');call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'presentation-wheel','actions':[{'type':'scroll','x':p['x'],'y':p['y'],'deltaX':0,'deltaY':delta,'duration':100}]}]});pause(130)

def prepare(sel):
 for _ in range(30):
  p=read('(()=>{let n=document.querySelector('+json.dumps(sel)+'),r=n.getBoundingClientRect(),d=document.getElementById("nlQuizDialog").getBoundingClientRect(),h=document.querySelector("#nlQuizDialog .nl-quiz-dialog-header").getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,header:h.bottom,dialog:d.bottom,hit:n===hit||n.contains(hit),disabled:!!n.disabled}})()')
  if p['top']>=p['header']+3 and p['bottom']<=p['dialog']-3 and p['hit']and not p['disabled']:return p
  wheel(-220 if p['top']<p['header']+3 else 220)
 raise AssertionError('Cannot reach '+sel+' '+str(p))

def quiz(sel):pointer_at(prepare(sel));pause()

def safe_range(first,last=None):return read('(()=>{let d=document.getElementById("nlQuizDialog"),dr=d.getBoundingClientRect(),h=d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),a=d.querySelector('+json.dumps(first)+').getBoundingClientRect(),b=d.querySelector('+json.dumps(last or first)+').getBoundingClientRect();return{top:Math.min(a.top,b.top),bottom:Math.max(a.bottom,b.bottom),safeTop:h.bottom+12,safeBottom:dr.top+d.clientHeight+1-12,scroll:d.scrollTop}})()')

def action(sel,label,first,last=None):
 p=prepare(sel);before=ev('document.getElementById("nlQuizDialog").scrollTop');pointer_at(p);pause(850);g=safe_range(first,last);height=g['bottom']-g['top'];fits=height<=g['safeBottom']-g['safeTop'];ok=g['top']>=g['safeTop']-2 and (g['bottom']<=g['safeBottom']+3 if fits else g['top']<g['safeTop']+20);out['actions'].append({'label':label,'beforeScroll':before,'settled':g});check(ok,label+' response within sticky-header safe viewport',g)

def storage():return read('Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith("namelecule:lesson-checkpoints:v1:")).map(([k,v])=>[k,JSON.parse(v)]))')

def seed(index,value):
 ev('(()=>{let s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps}),h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);let key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16),r=JSON.parse(sessionStorage.getItem(key)||"null")||{version:1,content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(key,JSON.stringify(r));return true})()');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()

def dismiss():
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):ev('document.getElementById("rotatePromptDismiss").click();true')

def open_quiz():plain('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45);check(abs(ev('document.getElementById("nlQuizDialog").scrollTop'))<1,'Quiz opens at top')

try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':760},'devicePixelRatio':1});navigate('design/theory-library.html?v=review-wrong-answer-supplement');plain('article[aria-labelledby=alkanes-title] a.action');ready();ev('fScenarioGo(3);true');wait('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation');seed(3,'4');dismiss();open_quiz();check(ev('document.querySelector("#nlQuizDialog .round-objective").textContent')==f['objective'],'Expected seeded canonical objective')
 action('[id$="-part-'+f['targetPartId']+'"]','Correct target','.choice-fieldset');original=next(p['text']for p in f['parts']if p['id']==f['targetPartId']);wrongIndex=next(i for i,c in enumerate(f['choices'])if c['value']not in [original,f['correctValue']]);wrong=f['choices'][wrongIndex];out['wrongChoice']={'original':original,'incorrect':wrong['value'],'correct':f['correctValue'],'expectedFeedback':wrong.get('feedback')or f['feedback']['incorrect']};action('[id$="-choice-'+str(wrongIndex)+'"]','Incorrect replacement','.candidate','.check-helper');action('[id$="-check-button"]','Incorrect Check','.feedback');out['incorrectFeedback']=ev('document.querySelector("#nlQuizDialog .feedback").textContent');out['receiptAfterIncorrect']=storage();check(out['wrongChoice']['expectedFeedback']in out['incorrectFeedback'],'Actual targeted incorrect feedback');check(ev('!document.querySelector("#nlQuizDialog .feedback.is-success")&&!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&document.getElementById("scNext").disabled&&document.getElementById("nlQuizProgress").textContent==="Κουίζ 1/3"'),'Wrong replacement keeps first round and required gate locked');shot('incorrect-feedback')
 correct=next(i for i,c in enumerate(f['choices'])if c['value']==f['correctValue']);action('[id$="-choice-'+str(correct)+'"]','Corrected replacement','.candidate','.check-helper');action('[id$="-check-button"]','Corrected Check','.feedback','.round-next button');out['receiptAfterCorrect']=storage();check(ev('!!document.querySelector("#nlQuizDialog .feedback.is-success")&&document.getElementById("scNext").disabled&&!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Correction earns one repair and leaves remaining two required');key=next(iter(out['receiptAfterCorrect']));before=out['receiptAfterIncorrect'][key]['states']['3']['states'][0];after=out['receiptAfterCorrect'][key]['states']['3']['states'][0];check(before['attempts']==1 and not before['solved']and after['attempts']==2 and after['solved'],'Receipt records one incorrect then one correct submitted attempt');shot('corrected-success');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:
 out['targetUnchanged']=all(sha(ROOT/p)==v for p,v in T.items());out['completed']=out['completed']and out['targetUnchanged'];save();call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'JavaScriptErrors':len(js_errors),'targetUnchanged':out['targetUnchanged'],'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
