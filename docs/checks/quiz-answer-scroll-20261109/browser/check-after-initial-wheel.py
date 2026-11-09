"""Read-only geometry around two actual quiz rounds; no app hooks or source edits."""
from pathlib import Path
import sys
MODE=sys.argv[1]
import os,json,time,traceback,hashlib,base64
HERE=Path('docs/checks/quiz-answer-scroll-20261109/browser');proc=json.loads((HERE/('process-'+MODE+'.json')).read_text());os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(15)'),'owned-headless-bidi','exec'))
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());fixture=next(s['rounds'][0] for g in fixtures if g['seed']=='4' for s in g['sets'] if s['id']=='alkanes-unbranched')
out={'completed':False,'date':'2026-11-09','role':'Developer preflight geometry evidence, not independent review','scope':'No production edits, hooks, extraUIlisteners or round API overrides. Separate owned headless, two actual rounds total; all answer actions use native pointer input and natural wheel to visible controls. Unsolved seed4 only.','runs':[],'sources':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['js/namelecule-game-repair.js','js/namelecule-quiz-checkpoints.js','css/namelecule-quiz-checkpoints.css','scenarios/alkanes-user-3.scenario.json']}}
def save():out['javascriptErrors']=js_errors;(HERE/(MODE+'-after.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
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
def geometry():return read('''(()=>{const d=document.getElementById('nlQuizDialog'),host=document.getElementById('nlQuizHost'),h=d?.querySelector('.nl-quiz-dialog-header'),hr=h?.getBoundingClientRect(),dr=d?.getBoundingClientRect(),top=hr?.bottom||0,bottom=Math.min(dr?.bottom||innerHeight,innerHeight),sels=['.round-heading h1','.round-heading p','.order-controls','.check-helper','.name-parts','.part-selection-status','.choice-fieldset','.choices','.candidate','.repair-actions','.feedback','.success-explanation','.round-next button'];return{time:new Date().toISOString(),step:fScenarioPresent().index,progress:document.getElementById('nlQuizProgress')?.textContent,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},active:{tag:document.activeElement?.tagName,id:document.activeElement?.id},dialog:d?{open:d.open,scrollTop:d.scrollTop,clientHeight:d.clientHeight,scrollHeight:d.scrollHeight,overflowY:getComputedStyle(d).overflowY,rect:dr.toJSON()}:null,host:host?{scrollTop:host.scrollTop,clientHeight:host.clientHeight,scrollHeight:host.scrollHeight,overflowY:getComputedStyle(host).overflowY}:null,documentScrollTop:document.scrollingElement.scrollTop,header:hr?.toJSON(),usable:{top,bottom,height:bottom-top},elements:sels.map(sel=>{const e=d?.querySelector(sel);if(!e)return{selector:sel,present:false};const r=e.getBoundingClientRect(),s=getComputedStyle(e),displayed=r.width>0&&r.height>0&&s.visibility!=='hidden',visible=displayed?Math.max(0,Math.min(r.bottom,bottom)-Math.max(r.top,top)):0;return{selector:sel,present:true,displayed,text:e.textContent,rect:r.toJSON(),visibleHeight:visible,fullyVisible:displayed&&r.top>=top&&r.bottom<=bottom,clippedTop:displayed?Math.max(0,top-r.top):0,clippedBottom:displayed?Math.max(0,r.bottom-bottom):0,display:s.display}})}})()''')
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
def prepare(sel):
 for _ in range(22):
  p=read('(()=>{const e=document.querySelector('+json.dumps(sel)+'),r=e.getBoundingClientRect(),d=document.getElementById("nlQuizDialog"),dr=d.getBoundingClientRect(),h=d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),hit=document.elementFromPoint(x,y);return{x,y,top:r.top,bottom:r.bottom,headerBottom:h.bottom,dialogBottom:dr.bottom,hit:e===hit||e.contains(hit),disabled:e.disabled}})()')
  if p['top']>=p['headerBottom']+3 and p['bottom']<=p['dialogBottom']-3 and p['hit'] and not p['disabled']:
   return p
  wheel(-220 if p['top']<p['headerBottom']+3 else 220)
 raise AssertionError('Cannot reach '+sel+' '+str(p))
out={'completed':False,'mode':MODE,'checks':[],'actions':[],'rounds':[],'notes':[],'limitations':['Ownedheadless, no personal/GUI browser interaction','Readonly DOM/rAF sampling only, no prototype hooks or fake solved receipts','Normal six-repair flow; separate reducedpref round and bounded standalone smoke']}
games={g['seed']:{s['id']:s for s in g['sets']} for g in fixtures}
def check(ok,label):
 assert ok,label
 out['checks'].append(label);save();print('PASS '+label,flush=True)
def seed(index,value):
 ev('(()=>{const s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16),r=JSON.parse(sessionStorage.getItem(key)||"null")||{version:1,content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(key,JSON.stringify(r));return true})()');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def open_quiz():
 plain_pointer('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45)
def top_entry(label):
 g=geometry();h=next(e for e in g['elements'] if e['selector']=='.round-heading h1');check(abs(g['dialog']['scrollTop'])<1 and h['rect']['top']>=g['header']['bottom'],label+' newround/reopen startsattop belowstickyheader')
def sample_start():
 ev('(()=>{window.__answerTrace=[];const start=performance.now();function tick(){const d=document.getElementById("nlQuizDialog"),a=document.activeElement;__answerTrace.push({ms:performance.now()-start,scroll:d?.open?d.scrollTop:document.scrollingElement.scrollTop,focus:{id:a?.id,tag:a?.tagName,text:a?.textContent?.slice(0,60)}});if(performance.now()-start<720)requestAnimationFrame(tick)}requestAnimationFrame(tick);return true})()')
def take_trace():
 ev('new Promise(r=>setTimeout(()=>r(true),760))');return read('__answerTrace')
def action(sel,label,start,end=None,keyboard=False,visible=False,short=False):
 p=prepare(sel);before=geometry()
 if keyboard:
  ev('document.querySelector('+json.dumps(sel)+').focus({preventScroll:true});true');call('browsingContext.activate',{'context':ctx})
 sample_start()
 if keyboard:call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'answer-keyboard','actions':[{'type':'keyDown','value':' '},{'type':'keyUp','value':' '}]}]})
 else:pointer_at(p)
 trace=take_trace();after=geometry();sels=[start,end or start];elements=[next(e for e in after['elements'] if e['selector']==s) for s in sels];assert all(e.get('displayed') for e in elements),(label,elements)
 safe_top=after['header']['bottom']+12;safe_bottom=after['dialog']['rect']['top']+after['dialog']['clientHeight']+1-12
 rt=min(e['rect']['top'] for e in elements);rb=max(e['rect']['bottom'] for e in elements);tall=rb-rt>safe_bottom-safe_top
 if tall:check(rt>=safe_top-2 and rt<safe_top+18,label+' tallrange beginsbelowstickyheader')
 else:check(rt>=safe_top-2 and rb<=safe_bottom+3,label+' settledrange fullyinsideheader-safe viewport')
 vals=[x['scroll'] for x in trace];unique=sorted(set(round(x,2) for x in vals));moved=abs(after['dialog']['scrollTop']-before['dialog']['scrollTop'])>1
 intermediate=any(min(vals[0],vals[-1])+.5<v<max(vals[0],vals[-1])-.5 for v in vals)
 if visible:check(not moved and max(vals)-min(vals)<1,label+' alreadyvisible hasnojump')
 if MODE=='reduced':check(not intermediate,label+' reducedpref hasnointermediate smoothpositions')
 elif moved:check(intermediate,label+' capturesnative smoothintermediatepositions')
 focus=[json.dumps(x['focus'],sort_keys=True) for x in trace if x['ms']>=100];check(len(set(focus))<=1,label+' focusdoesnotmove duringreveal')
 item={'label':label,'selector':sel,'semanticRange':sels,'before':before,'after':after,'trace':trace,'nativeSmoothIntermediate':intermediate,'tallRange':tall};out['actions'].append(item);save();r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(MODE+'-'+label+'.png')).write_bytes(base64.b64decode(r['data']));return item

def cancel_back(target):
 p=prepare(target);before=geometry();sample_start();pointer_at(p);ev('new Promise(r=>setTimeout(()=>r(true),45))');during=geometry()
 d=read('(()=>{const r=document.getElementById("nlQuizBack").getBoundingClientRect();return{x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()');pointer_at(d);wait('!document.getElementById("nlQuizDialog").open',5);open_quiz();sample_start();trace=take_trace();after=geometry()
 out['cancelBack']={'before':before,'during':during,'after':after,'afterReopenTrace':trace};check(any(x['scroll']>before['dialog']['scrollTop'] for x in read('__answerTrace')) if False else during['dialog']['scrollTop']>before['dialog']['scrollTop'],'Back test observedmotion beforeclose');check(all(abs(x['scroll'])<1 for x in trace),'Back duringmotion thenreopen hasnostalemovement');check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','Back/reopen preservescounter');top_entry('AfterBackduringmotion')

def cancel_wheel(target):
 p=prepare(target);sample_start();pointer_at(p);ev('new Promise(r=>setTimeout(()=>r(true),45))');during=geometry();wheel(-120);trace=take_trace();after=geometry();out['cancelWheel']={'during':during,'after':after,'trace':trace};late=[x['scroll'] for x in trace if x['ms']>=350];check(bool(late) and max(late)-min(late)<1 and late[-1]<=during['dialog']['scrollTop']+1,'Trustedwheel duringmotion takescontrol withoutlaterautomaticreversal')

def solve_fixture(f,step,ri,extensive=False,tall=False):
 check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ '+str(ri+1)+'/3','Step'+str(step+1)+' counter'+str(ri+1))
 tag='s'+str(step+1)+'r'+str(ri+1)
 if f['kind']=='replace':
  target='[id$="-part-'+f['targetPartId']+'"]'
  if extensive:
   wrong=next(p['id'] for p in f['parts'] if p['id']!=f['targetPartId']);action('[id$="-part-'+wrong+'"]',tag+'-agreeing','.part-selection-status')
   if MODE=='normal':
    cancel_back(target);cancel_wheel(target)
  action(target,tag+'-target','.choice-fieldset',keyboard=(MODE=='normal' and step==3 and ri==1))
  if extensive:action(target,tag+'-target-alreadyvisible','.choice-fieldset',visible=True)
  original=next(p['text'] for p in f['parts'] if p['id']==f['targetPartId']);correct=next(i for i,c in enumerate(f['choices']) if c['value']==f['correctValue'])
  if extensive:
   for kind,val in [('unchanged',original),('incorrect',next(c['value'] for c in f['choices'] if c['value']!=f['correctValue'] and c['value']!=original))]:
    idx=next(i for i,c in enumerate(f['choices']) if c['value']==val);action('[id$="-choice-'+str(idx)+'"]',tag+'-'+kind+'-choice','.candidate','.check-helper');action('[id$="-check-button"]',tag+'-'+kind+'-check','.feedback');check(not ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(step)+')'),kind+' answerdoesnotunlockgate')
  action('[id$="-choice-'+str(correct)+'"]',tag+'-correct-choice','.candidate','.check-helper')
 else:
  action('[id$="-part-'+f['correctOrder'][0]+'"]',tag+'-order-select','.part-selection-status','.order-controls');action('[id$="-move-left"]',tag+'-order-move','.order-controls','.check-helper')
 if tall:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':320},'devicePixelRatio':1});out['notes'].append('Realfeedback shortviewport390×320 boundary, no textfixture/stub')
 action('[id$="-check-button"]',tag+'-success','.feedback','.round-next button');check(ev('!!document.querySelector("#nlQuizDialog .feedback.is-success")'),'Actualsuccess '+tag);out['rounds'].append({'step':step+1,'round':ri+1,'id':f['id']})
 if tall:call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':760},'devicePixelRatio':1})
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(step)+')')==(ri==2),'Gatecompletiononlyafteractualthird '+tag)
 if MODE=='normal':
  pointer_at(prepare('#nlQuizDialog .round-next button'))
  if ri<2:wait('document.getElementById("nlQuizProgress").textContent==='+json.dumps('Κουίζ '+str(ri+2)+'/3')+'&&!!document.querySelector("#nlQuizDialog .diagram-image.is-ready")',15);top_entry(tag+' Continue')
  else:wait('fScenarioPresent().index==='+str(step+1),15)

try:
 expected={'js/namelecule-game-repair.js':'7d0a0939841f0423377d0ccca66ee9554b70f8a61a7ff020cf833aa0755b5ac7','js/namelecule-generated-repair-checkpoint.js':'d99aaa972afa2a437bedf1e4eca3c835126f237e5333e33ac1d9d10d5b684d27','js/namelecule-quiz-checkpoints.js':'7bf5441b52b9b519db79f3e56adec97979668de172b8292c0a714355add35bb7','mulermoc-nom-54.html':'34ade6e22d3e9afaf8cfeb49d7a75fabada1a915b6d1550f58b83b323d68fb27'}
 check(all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in expected.items()),'ExactROOT READYsourcehashes')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':650},'devicePixelRatio':2});navigate('design/theory-library.html?v=answer-reveal-'+MODE);ev('document.querySelector("article[aria-labelledby=alkanes-title] a.action").click();true');ready();out['reducedMotion']=ev('matchMedia("(prefers-reduced-motion: reduce)").matches');check(out['reducedMotion']==(MODE=='reduced'),'Realprefersreducedmotion matchesownedprofile')
 ev('fScenarioGo(9);true');wait('fScenarioPresent().index===3',15);check(ev('document.getElementById("scNext").disabled'),'Normalgate4blocksjump');seed(3,'4');open_quiz();top_entry('Initialgate4')
 if MODE=='reduced':solve_fixture(games['4']['alkanes-unbranched']['rounds'][0],3,0,extensive=True)
 else:
  for ri,f in enumerate(games['4']['alkanes-unbranched']['rounds']):solve_fixture(f,3,ri,extensive=(ri==0))
  ev('fScenarioGo(10);true');wait('fScenarioPresent().index===10',15);check(ev('document.getElementById("scNext").disabled&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Gate4actualcomplete;11blocks12')
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':760},'devicePixelRatio':1});seed(10,'1')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':ev('document.getElementById("rotatePromptDismiss").click();true')
  open_quiz();top_entry('Initialgate11')
  for ri,f in enumerate(games['1']['alkanes-branched']['rounds']):
   if ri==0:
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':320,'height':700},'devicePixelRatio':1});top_entry('320pxsameentry');call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':760},'devicePixelRatio':1})
   solve_fixture(f,10,ri,tall=(ri==2))
  check(ev('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open'),'Actual6repairsreach12');ev('document.getElementById("scExit").click();true');wait('location.pathname.endsWith("/design/theory-library.html")',12)
  # Bounded actual standalone case: existing document scrolling semantics.
  navigate('games/name-repair.html?v=answer-reveal-smoke');wait('!!document.getElementById("set-alkanes-start")',20);plain_pointer('#set-alkanes-start');plain_pointer('#set-alkanes-unbranched-start');wait('!!document.querySelector(".diagram-image.is-ready")',15)
  for sel in ['#part-root','#choice-1','#check-button']:
   ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center"});true');p=read('(()=>{const r=document.querySelector('+json.dumps(sel)+').getBoundingClientRect();return{x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()');before_scroll=ev('scrollY');sample_start();pointer_at(p);trace=take_trace();check(max(x['scroll'] for x in trace)-min(x['scroll'] for x in trace)<1,'Standalone'+sel+' hasnoaddedscrollmotion')
  check(ev('!!document.querySelector(".feedback.is-success")'),'Standaloneactualrepairsuccess');out['standalone']=True
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureGeometry']=geometry();r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(MODE+'-failure.png')).write_bytes(base64.b64decode(r['data']))
 except Exception as e:out['captureFailure']=str(e)
finally:
 save()
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'mode':MODE,'completed':out['completed'],'checks':len(out['checks']),'actions':len(out['actions']),'actualRepairs':len(out['rounds']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']:raise SystemExit(1)
