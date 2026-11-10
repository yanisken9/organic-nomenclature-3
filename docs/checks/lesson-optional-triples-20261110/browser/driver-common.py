"""Owned isolated Firefox native-input helpers; Developer evidence only."""
from pathlib import Path
import os,sys,json,time,base64,hashlib,traceback,urllib.request
H=Path(__file__).resolve().parent;ROOT=Path.cwd();P=json.loads((H/os.environ.get('OPTIONAL_PROCESS_RECORD','process.json')).read_text());STAGE=sys.argv[1];REPORT=os.environ.get('OPTIONAL_REPORT',STAGE)
os.environ['NAMELECULE_BIDI_PORT']=str(P['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=P[STAGE+'_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-parity-bidi','exec'))
call('script.addPreloadScript',{'functionDeclaration':'() => {window.MULER_QUIET_FETCH=true; window.crypto.getRandomValues=(a)=>{a.fill(4);return a;}; }','contexts':[ctx]})
OUT={'completed':False,'stage':STAGE,'checks':[],'measurements':[],'actions':[],'role':'Developer browser evidence, not independent review','scope':['Exact seven-source before overlay, all other current runtime unchanged.','Deterministic unsolved seed via isolated crypto preload; every recorded success earned by learner pointer actions.','Owned headless isolated Firefox and ephemeral localhost only; personal GUI and 8013 untouched.']}
def save(name=None):
 OUT['javascriptErrors']=js_errors;(H/(name or REPORT+'-browser.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
def read(x):return json.loads(ev('JSON.stringify('+x+')'))
def pause(ms=180):time.sleep(ms/1000)
def wait(x,seconds=40):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(x):return
  time.sleep(.1)
 raise AssertionError('Timeout '+x)
def check(ok,label,detail=None):
 assert ok,(label,detail)
 OUT['checks'].append({'label':label,'detail':detail});save();print('PASS '+label,flush=True)
def shot(label):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(H/(REPORT+'-'+label+'.png')).write_bytes(base64.b64decode(r['data']))
def pointer(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'parity-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def key(value):call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'parity-keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]});pause()
def wheel(delta,dialog=False):
 p=read('(()=>{let d='+('document.getElementById("nlQuizDialog").getBoundingClientRect()'if dialog else '({x:0,y:0,width:innerWidth,height:innerHeight})')+';return{x:Math.round(d.x+d.width*.75),y:Math.round(d.y+d.height*.75)}})()');call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'parity-wheel','actions':[{'type':'scroll','x':p['x'],'y':p['y'],'deltaX':0,'deltaY':delta,'duration':100}]}]});pause(150)
def prepare(sel):
 for _ in range(35):
  p=read('(()=>{let n=document.querySelector('+json.dumps(sel)+');if(!n)return null;let r=n.getBoundingClientRect(),d=document.getElementById("nlQuizDialog"),dialog=!!d?.open,dr=dialog?d.getBoundingClientRect():{top:0,bottom:innerHeight},h=dialog?(n.closest(".nl-quiz-dialog-header")?dr.top:d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect().bottom):0,x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,safeTop:h+3,safeBottom:dr.bottom-3,hit:n===hit||n.contains(hit),disabled:!!n.disabled,dialog}})()')
  assert p is not None,sel
  if p['top']>=p['safeTop'] and p['bottom']<=p['safeBottom']and p['hit']and not p['disabled']:return p
  assert not p['disabled'],(sel,p)
  wheel(-220 if p['top']<p['safeTop']else 220,p['dialog'])
 raise AssertionError(('Unreachable',sel,p))
def click(sel,settle=230):
 p=prepare(sel);pause(350);p=prepare(sel);pointer(p);OUT['actions'].append({'click':sel,'point':p});pause(settle)
def viewport(w,h):
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1})
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):ev('document.getElementById("rotatePromptDismiss").click();true')
 pause()
def dismiss_rotate():
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):ev('document.getElementById("rotatePromptDismiss").click();true')
 pause()
def top():ev('(()=>{let d=document.getElementById("nlQuizDialog");(d?.open?d:window).scrollTo({top:0,behavior:"instant"});return true})()');pause()
def image_ready():wait('!!document.querySelector(".diagram-image.is-ready")',55)
def source_guard():
 t=json.loads((H.parent/'baseline.json').read_text())['sourceHashes'] if STAGE=='before'else json.loads((H/'frozen-target.json').read_text())['files'];OUT['target']=t
 for p,v in t.items():
  with urllib.request.urlopen(P[STAGE+'_url']+p+'?guard='+str(time.time_ns()),timeout=15)as r:b=r.read()
  assert hashlib.sha256(b).hexdigest()==v,p
 check(True,'Exact seven served source hashes',t)
def geometry(label,w):
 g=read('(()=>{let p=document.querySelector(".round-objective"),i=document.querySelector(".diagram-image"),b=document.querySelector(".diagram-tools button"),s=getComputedStyle(p),l=document.querySelector(".diagram-tools span"),counter=document.querySelector(".round-progress-counter");return{label:'+json.dumps(label)+',viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,scope:document.getElementById("game-root")?.className,objective:{text:p.textContent,classes:p.className,font:s.fontSize,weight:s.fontWeight,align:s.textAlign,rect:p.getBoundingClientRect().toJSON()},image:{src:i.currentSrc,alt:i.alt,width:i.naturalWidth,rect:i.getBoundingClientRect().toJSON()},representation:l.textContent,labelDisplay:getComputedStyle(l).display,zoom:{text:b.textContent,aria:b.getAttribute("aria-label"),rect:b.getBoundingClientRect().toJSON()},counter:counter?.textContent,body:document.body.className}})()');OUT['measurements'].append(g);check(g['pageWidth']<=w,label+' no horizontal overflow',g);shot(label+'-'+str(w));save();return g
def direct(engine=False,setid='alkanes-unbranched',difficulty='basic'):
 navigate('games/name-repair.html'+('?source=engine'if engine else ''));wait('!!document.getElementById("set-alkanes-start")',65);click('#set-alkanes-start');wait('!!document.getElementById("set-'+setid+'-start")')
 if engine and difficulty!='basic':ev('document.getElementById("pilot-difficulty").value='+json.dumps(difficulty)+';document.getElementById("pilot-difficulty").dispatchEvent(new Event("change",{bubbles:true}));true')
 click('#set-'+setid+'-start');image_ready();top()
def finish():
 save();call('browsingContext.close',{'context':ctx});call('session.end',{});s.close()
