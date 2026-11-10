"""Bounded native-input Firefox check; Developer evidence, not independent review."""
from pathlib import Path
import os,sys,json,time,base64,hashlib,urllib.request,traceback
H=Path(__file__).resolve().parent;ROOT=Path.cwd();STAGE=sys.argv[1];assert STAGE in ('before','after');P=json.loads((H/'process.json').read_text());BASE=json.loads((H.parent/'baseline.json').read_text());TARGET=BASE['sourceHashes'] if STAGE=='before' else json.loads((H/'frozen-target.json').read_text())['files']
os.environ['NAMELECULE_BIDI_PORT']=str(P['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=P[STAGE+'_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-bidi','exec'))
OUT={'stage':STAGE,'completed':False,'checks':[],'geometry':[],'nativeActions':[],'target':TARGET,'notes':['Developer-supplied browser evidence; no independent review claim.','Real Main55 lesson at step4 with deterministic unsolved seed4. Later direct step11 access, if used, is explicitly a navigation fixture, not proof of gate completion.','New owned isolated headless Firefox; no personal browser or GUI.','Before exact four-file overlay; runtime otherwise current.']}
def save():OUT['javascriptErrors']=js_errors;(H/(STAGE+'-browser.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def wait(x,seconds=35):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.1)
 raise AssertionError('Timeout '+x)
def pause(n=120):ev('new Promise(r=>setTimeout(()=>r(true),'+str(n)+'))')
def check(ok,label,data=None):
 assert ok,(label,data)
 OUT['checks'].append({'label':label,'evidence':data});save();print('PASS '+label,flush=True)
def shot(label):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(H/(STAGE+'-'+label+'.png')).write_bytes(base64.b64decode(r['data']))
def pointer(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'zoom-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def click(sel):
 ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center",behavior:"instant"});true');pause();p=read('(()=>{let n=document.querySelector('+json.dumps(sel)+'),r=n.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:n===h||n.contains(h),disabled:!!n.disabled}})()');assert p['hit']and not p['disabled'],(sel,p);pointer(p);OUT['nativeActions'].append({'click':sel,'point':p});pause()
def key(value):call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'zoom-keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]});OUT['nativeActions'].append({'key':value});pause()
def ready():app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',50)
def dismiss():
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):ev('document.getElementById("rotatePromptDismiss").click();true')
def viewport(w,h):call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});dismiss();pause()
def top():ev('document.getElementById("nlQuizDialog").scrollTo({top:0,behavior:"instant"});true');pause()
def seed(index,value):
 ev('(()=>{let s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps}),h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);let key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16),r=JSON.parse(sessionStorage.getItem(key)||"null")||{version:1,content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(key,JSON.stringify(r));return true})()');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def state():return read('({store:Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith("namelecule:lesson-checkpoints:v1:"))),progress:document.getElementById("nlQuizProgress").textContent,candidate:document.querySelector("#nlQuizDialog .candidate-name")?.textContent,selected:[...document.querySelectorAll("#nlQuizDialog input:checked")].map(n=>[n.id,n.value]),nextDisabled:document.getElementById("scNext").disabled})')
def geometry(label,w):
 g=read('(()=>{let d=document.getElementById("nlQuizDialog"),b=d.querySelector(".diagram-tools button"),l=d.querySelector(".diagram-tools span"),i=d.querySelector(".diagram-image"),card=d.querySelector(".diagram-card");return{width:innerWidth,docWidth:document.documentElement.scrollWidth,dialog:d.getBoundingClientRect().toJSON(),button:{rect:b.getBoundingClientRect().toJSON(),text:b.textContent,aria:b.getAttribute("aria-label"),title:b.title,disabled:b.disabled,classes:b.className},label:{rect:l.getBoundingClientRect().toJSON(),text:l.textContent,display:getComputedStyle(l).display},image:{rect:i.getBoundingClientRect().toJSON(),src:i.currentSrc,alt:i.alt,naturalWidth:i.naturalWidth},card:card?.getBoundingClientRect().toJSON()}})()');g['labelName']=label;OUT['geometry'].append(g);check(g['docWidth']<=w and g['dialog']['left']>=0 and g['dialog']['right']<=w,label+' no horizontal overflow',g);shot(label+'-'+str(w));save();return g

STAGE='image-supplement';OUT['stage']=STAGE;OUT['scope']='Corrected controlled loading/error fixture only; no learner replay.'
try:
 for p,h in TARGET.items():
  with urllib.request.urlopen(P['after_url']+p+'?guard='+str(time.time_ns()),timeout=15)as r:assert hashlib.sha256(r.read()).hexdigest()==h
 check(True,'frozen4 sources served')
 fixture='docs/checks/quiz-zoom-icon-20261110/browser/fixture.html';requestURL=P['after_url']+'docs/checks/quiz-zoom-icon-20261110/browser/held/assets/name-repair/propane.svg'
 call('session.subscribe',{'events':['network.beforeRequestSent'],'contexts':[ctx]})
 intercept=call('network.addIntercept',{'phases':['beforeRequestSent'],'urlPatterns':[{'type':'string','pattern':requestURL}],'contexts':[ctx]})['intercept']
 call('browsingContext.navigate',{'context':ctx,'url':P['after_url']+fixture+'?compact=1&held=1','wait':'interactive'});wait('!!document.querySelector(".diagram-zoom-button")');pause()
 held=[e['params'] for e in all_events if e.get('method')=='network.beforeRequestSent' and e['params']['request']['url']==requestURL and e['params'].get('isBlocked')];assert held,'No intercepted fixture image';request=held[-1]['request']['request']
 check(ev('document.querySelector(".diagram-zoom-button").disabled&&!document.querySelector(".diagram-image.is-ready")&&!document.querySelector(".zoom-dialog")'),'controlled real image request held: compact zoom disabled while loading')
 ev('document.querySelector(".diagram-card").scrollIntoView({block:"center"});true');pause();shot('controlled-loading-disabled')
 call('network.failRequest',{'request':request});wait('document.querySelector(".image-status").textContent.includes("δεν")')
 check(ev('document.querySelector(".diagram-zoom-button").disabled&&!document.querySelector(".zoom-dialog")&&document.querySelector(".image-status button").textContent==="Φόρτωσε ξανά τη δομή"'),'controlled real image request failed: zoom disabled with retry UI')
 OUT['fixture']={'requestURL':requestURL,'status':ev('document.querySelector(".image-status").textContent'),'uses':'Original canonical asset unchanged; test-only assetBase resolves to request intercepted by BiDi.'};shot('controlled-error-disabled');call('network.removeIntercept',{'intercept':intercept})
 check(all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in TARGET.items()),'frozen4 source unchanged')
 OUT['completed']=True;save()
except Exception:
 OUT['failure']=traceback.format_exc();save();raise
finally:
 save();call('browsingContext.close',{'context':ctx});call('session.end',{});s.close()
