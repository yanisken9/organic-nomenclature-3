"""Native-pointer normal learner replay, before overlay or frozen after target."""
from pathlib import Path
import os,json,time,traceback,hashlib,base64,sys,urllib.request
H=Path(__file__).resolve().parent;ROOT=Path.cwd();STAGE=sys.argv[1];assert STAGE in ['before','after'];P=json.loads((H/'process.json').read_text());BASE=json.loads((H.parent/'baseline.json').read_text());FOUR=['js/namelecule-generated-repair-checkpoint.js','js/namelecule-game-repair.js','css/namelecule-repair-round.css','mulermoc-nom-55.html'];protected={p:s for p,s in BASE['hashes'].items()if p not in FOUR}
# Guard molecular sources, generator, viewer, canonical JSON and existing assets.
for p in ['js/namelecule-repair-generator.js','js/mulermoc-nom-molview-55.js','js/jsme-nick-nomeclature-moc2-data_55.js','games/assets/name-repair/ethyl_3_dimethyl_2_5_hexane.svg']:
 protected[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if STAGE=='before':target={p:sha(H.parent/'before'/p)for p in FOUR};assert all(target[p]==BASE['hashes'][p]for p in FOUR)
else:
 frozen=json.loads((H.parent/'verification-target.json').read_text());target=frozen['files'];assert all(sha(ROOT/p)==v for p,v in target.items()),'After target mismatch before run'
assert all(sha(ROOT/p)==v for p,v in protected.items()),'Protected start mismatch'
os.environ['NAMELECULE_BIDI_PORT']=str(P['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=P[STAGE+'_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-bidi','exec'))
call('script.addPreloadScript',{'functionDeclaration':'() => { window.MULER_QUIET_FETCH = true; }','contexts':[ctx]})
FIX=json.loads((ROOT/'docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());games={g['seed']:{s['id']:s for s in g['sets']}for g in FIX}
out={'completed':False,'stage':STAGE,'role':'Developer browser evidence; not independent review','checks':[],'rounds':[],'geometry':[],'actions':[],'HTTP':{},'targetStart':target,'protectedStart':protected,'notes':['Seeds4/1 are unsolved deterministic fixtures only; all six repairs earned with native pointer actions.','Owned isolated headless Firefox desktop1280x800 and narrow390x760 (320px additionalcheck); no personal GUI control.','MULER_QUIET_FETCH supported setting suppresses irrelevant external naming requests; no service availability, offline or conference reliability claim.','Before uses exact four-file baseline overlay while other immutable runtime bytes are guarded.']}
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
def viewport(w,h):call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});dismiss();pause(150)
def top():ev('document.getElementById("nlQuizDialog").scrollTo({top:0,behavior:"instant"});true');pause(150)
def open_quiz():plain('#nlQuizOpen');wait('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',45);check(abs(ev('document.getElementById("nlQuizDialog").scrollTop'))<1,'Quiz opens at top')
def geometry(f,label,width):
 g=read('(()=>{let d=document.getElementById("nlQuizDialog"),p=d.querySelector(".round-heading p"),h=d.querySelector(".round-heading"),i=d.querySelector(".diagram-image"),r=p.getBoundingClientRect(),hr=h.getBoundingClientRect(),ir=i.getBoundingClientRect(),s=getComputedStyle(p);return{viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,dialog:d.getBoundingClientRect().toJSON(),objective:{text:p.textContent,font:s.fontSize,weight:s.fontWeight,align:s.textAlign,rect:r.toJSON(),heading:hr.toJSON()},image:{src:i.currentSrc,alt:i.alt,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,rect:ir.toJSON()},representation:d.querySelector(".diagram-tools span").textContent,representationDisplay:getComputedStyle(d.querySelector(".diagram-tools span")).display,progress:document.getElementById("nlQuizProgress").textContent}})()');g['roundId']=f['id'];g['label']=label;out['geometry'].append(g);check(g['documentWidth']<=width and g['dialog']['left']>=0 and g['dialog']['right']<=width,label+' no horizontal page/dialog overflow',g['dialog']);check(g['objective']['text']==f['objective'],label+' canonical objective unchanged')
 if STAGE=='after':
  check(g['objective']['align']=='center'and float(g['objective']['font'][:-2])>=(20 if width<=640 else 24) and int(g['objective']['weight'])>=700,label+' objective centered bold larger',g['objective'])
  large=f['moleculeId']=='ethyl_3_dimethyl_2_5_hexane';check(('/condensed/'in g['image']['src'])==large and g['representation']==('Συνεπτυγμένος συντακτικός τύπος'if large else 'Ανεπτυγμένος τύπος'),label+' representation/source agree',g['image'])
  if large:check(g['representationDisplay']!='none',label+' condensed representation label visible',g['representationDisplay'])
  check(f['correctName']not in g['image']['alt']and (('Συνεπτυγμένος'in g['image']['alt'])==large),label+' accurate nonanswer alt',g['image']['alt'])
 shot(label+'-'+str(width));save();return g

def solve_gate(index,setid,seedvalue):
 seed(index,seedvalue);dismiss();open_quiz()
 for ri,f in enumerate(games[seedvalue][setid]['rounds']):
  tag='s'+str(index+1)+'r'+str(ri+1);check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ '+str(ri+1)+'/3',tag+' exact round progress')
  if ri==0 or f['moleculeId']=='ethyl_3_dimethyl_2_5_hexane':
   for w,h in [(1280,800),(390,760)]:viewport(w,h);top();geometry(f,tag+'-entry',w)
   if f['moleculeId']=='ethyl_3_dimethyl_2_5_hexane':viewport(320,700);top();geometry(f,tag+'-entry',320)
   viewport(1280 if index==3 else 390,800 if index==3 else 760);top()
  if ri!=0 and f['moleculeId']!='ethyl_3_dimethyl_2_5_hexane':top();geometry(f,tag+'-entry',ev('innerWidth'))
  if f['moleculeId']=='ethyl_3_dimethyl_2_5_hexane':
   quiz('#nlQuizDialog .diagram-tools button');wait('!!document.querySelector("#nlQuizDialog .zoom-image")&&document.querySelector("#nlQuizDialog .zoom-image").naturalWidth>0');z=read('(()=>{let a=document.querySelector("#nlQuizDialog .diagram-image"),z=document.querySelector("#nlQuizDialog .zoom-image");return{main:a.currentSrc,zoom:z.currentSrc,alt:z.alt,mainAlt:a.alt}})()');check(z['main']==z['zoom']and z['alt']==z['mainAlt'],tag+' zoom uses identical asset and alt',z);shot(tag+'-zoom');quiz('#nlQuizDialog .zoom-heading button')
  if f['kind']=='replace':
   if ri==0:
    wrong=next(p['id']for p in f['parts']if p['id']!=f['targetPartId']);action('[id$="-part-'+wrong+'"]',tag+' wrong part','.part-selection-status');check(ev('document.querySelector("#nlQuizDialog .part-selection-status").textContent').startswith(f['feedback']['wrongPart']),tag+' wrongpart reminder preserved');check(ev('document.getElementById("scNext").disabled'),tag+' wrongpart keepsNextlocked')
   action('[id$="-part-'+f['targetPartId']+'"]',tag+' target','.choice-fieldset');good=next(i for i,c in enumerate(f['choices'])if c['value']==f['correctValue']);action('[id$="-choice-'+str(good)+'"]',tag+' correct choice','.candidate','.check-helper')
  else:action('[id$="-part-'+f['correctOrder'][0]+'"]',tag+' orderselect','.part-selection-status','.order-controls');action('[id$="-move-left"]',tag+' ordermove','.order-controls','.check-helper')
  if STAGE=='after'and index==3 and ri==1:
   before=storage();candidateBefore=ev('document.querySelector("#nlQuizDialog .candidate-name").textContent');plain('#nlQuizBack');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_quiz();after=storage();candidateAfter=ev('document.querySelector("#nlQuizDialog .candidate-name").textContent');out['progressRefresh']={'before':before,'after':after,'candidateBefore':candidateBefore,'candidateAfter':candidateAfter};save();key=next(iter(before));b=before[key];a=after[key];gb=b['states']['3'];ga=a['states']['3'];check(set(before)==set(after)and b['content']==a['content']and all(gb[k]==ga[k]for k in ['version','seed','currentRound','solved'])and gb['states'][:2]==ga['states'][:2]and candidateBefore==candidateAfter,tag+' realrefresh preserves earned first and unsubmitted second progress');check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 2/3'and ev('document.getElementById("scNext").disabled'),tag+' realrefresh roundcounter/Nextlock retained');shot(tag+'-refreshed')
  action('[id$="-check-button"]',tag+' success','.feedback','.round-next button');check(ev('!!document.querySelector("#nlQuizDialog .feedback.is-success")'),tag+' repair earned');check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(index)+')')==(ri==2)and ev('document.getElementById("scNext").disabled')==(ri<2),tag+' gate locks until third earned repair');out['rounds'].append({'step':index+1,'round':ri+1,'canonicalId':f['id'],'canonicalMoleculeId':f['moleculeId'],'receipt':storage()});shot(tag+'-success');quiz('#nlQuizDialog .round-next button')
  if ri<2:wait('document.getElementById("nlQuizProgress").textContent==='+json.dumps('Κουίζ '+str(ri+2)+'/3')+'&&!!document.querySelector("#nlQuizDialog .diagram-image.is-ready")');check(abs(ev('document.getElementById("nlQuizDialog").scrollTop'))<1,tag+' Continue next round starts at top')
  else:wait('fScenarioPresent().index==='+str(index+1));save()
try:
 for p,v in target.items():
  with urllib.request.urlopen(P[STAGE+'_url']+p+'?guard='+str(time.time_ns()),timeout=15)as r:b=r.read();out['HTTP'][p]={'status':r.status,'sha256':hashlib.sha256(b).hexdigest()}
  assert out['HTTP'][p]['sha256']==v,p
 check(True,STAGE+' exact HTTP target hashes')
 viewport(1280,800);navigate('design/theory-library.html?v=quiz-presentation-'+STAGE);plain('article[aria-labelledby=alkanes-title] a.action');ready();check(ev('!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Normal 12-step learner presentation')
 for i in [1,2,3]:plain('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
 ev('fScenarioGo(11);true');check(ev('fScenarioPresent().index===3&&document.getElementById("scNext").disabled'),'Required first gate rejects bypass');solve_gate(3,'alkanes-unbranched','4')
 for i in [5,6,7,8,9,10]:plain('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
 ev('fScenarioGo(11);true');check(ev('fScenarioPresent().index===10&&document.getElementById("scNext").disabled'),'Required second gate rejects bypass');solve_gate(10,'alkanes-branched','1');check(ev('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Six earned repairs reach step12');plain('#scPrev');wait('fScenarioPresent().index===10');check(not ev('document.getElementById("scNext").disabled'),'Completed gate replay remains unlocked');plain('#scNext');wait('fScenarioPresent().index===11');plain('#scExit');wait('location.pathname.endsWith("/design/theory-library.html")');check(True,'Lesson Exit returns to library')
 if STAGE=='after':
  viewport(1280,800);navigate('games/name-repair.html?v=quiz-presentation-default');wait('!!document.getElementById("set-alkanes-start")');plain('#set-alkanes-start');plain('#set-alkanes-unbranched-start');wait('!!document.querySelector(".diagram-image.is-ready")');g=read('(()=>{let p=document.querySelector(".round-heading p"),i=document.querySelector(".diagram-image"),s=getComputedStyle(p);return{font:s.fontSize,align:s.textAlign,classes:p.className,src:i.currentSrc,label:document.querySelector(".diagram-tools span").textContent}})()');check('is-emphasized'not in g['classes']and '/condensed/'not in g['src']and g['label']=='Ανεπτυγμένος τύπος','Standalone retains default presentation',g);shot('standalone-default')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure');out['failureURL']=ev('location.href')
 except Exception:pass
finally:
 out['protectedFinish']={p:sha(ROOT/p)for p in protected};out['protectedUnchanged']=out['protectedFinish']==protected
 out['targetFinish']={p:sha((H.parent/'before'/p)if STAGE=='before'else(ROOT/p))for p in target};out['targetUnchanged']=out['targetFinish']==target
 if not(out['protectedUnchanged']and out['targetUnchanged']):out['completed']=False;out['hashFailure']=True
 save();call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'stage':STAGE,'checks':len(out['checks']),'rounds':len(out['rounds']),'JSErrors':len(js_errors),'protectedUnchanged':out['protectedUnchanged'],'targetUnchanged':out['targetUnchanged'],'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
