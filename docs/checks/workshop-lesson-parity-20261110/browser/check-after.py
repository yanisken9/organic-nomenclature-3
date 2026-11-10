from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
STATIC=json.loads((ROOT/'games/data/name-repair-alkanes.json').read_text())['sets']
FIX=json.loads((ROOT/'docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text());GAMES={g['seed']:{s['id']:s for s in g['sets']}for g in FIX}
OUT['repairs']=[];OUT['semanticActions']=[]
def counter():return ev('document.querySelector(".round-progress-counter")?.textContent||document.getElementById("nlQuizProgress")?.textContent')
def range_rect(first,last=None):return read('(()=>{let d=document.getElementById("nlQuizDialog"),dialog=!!d?.open,dr=dialog?d.getBoundingClientRect():null,h=dialog?d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect().bottom:0,a=document.querySelector('+json.dumps(first)+').getBoundingClientRect(),b=document.querySelector('+json.dumps(last or first)+').getBoundingClientRect();return{top:Math.min(a.top,b.top),bottom:Math.max(a.bottom,b.bottom),safeTop:h+12,safeBottom:(dialog?dr.top+d.clientHeight+1:innerHeight)-12,scroll:dialog?d.scrollTop:scrollY,dialog}})()')
def sample(ms=900):
 ev('(()=>{window.__parityTrace=[];let begin=performance.now();function tick(){let d=document.getElementById("nlQuizDialog");__parityTrace.push({ms:performance.now()-begin,y:d?.open?d.scrollTop:scrollY,focus:document.activeElement?.id});if(performance.now()-begin<'+str(ms)+')requestAnimationFrame(tick)}requestAnimationFrame(tick);return true})()')
def action(sel,label,first,last=None,visible=False):
 p=prepare(sel);pause(350);p=prepare(sel);before=range_rect(first,last) if ev('!!document.querySelector('+json.dumps(first)+')&&!!document.querySelector('+json.dumps(last or first)+')') else None;sample();pointer(p);pause(1050);g=range_rect(first,last);trace=read('__parityTrace');height=g['bottom']-g['top'];ok=g['top']>=g['safeTop']-2 and (g['bottom']<=g['safeBottom']+3 if height<=g['safeBottom']-g['safeTop'] else g['top']<g['safeTop']+20)
 OUT['semanticActions'].append({'label':label,'range':[first,last or first],'before':before,'after':g,'trace':trace});check(ok,label+' semantic response framed',g)
 if visible:check(max(t['y']for t in trace)-min(t['y']for t in trace)<1,label+' already visible no-op',trace)
 vals=[t['y']for t in trace];moved=abs(vals[-1]-vals[0])>1
 if moved:check(any(min(vals[0],vals[-1])+.5<y<max(vals[0],vals[-1])-.5 for y in vals),label+' native smooth intermediate positions')
 check(len(set(t['focus']for t in trace if t['ms']>250))<=1,label+' focus retained during reveal')
 return g

def shown(label,w):
 g=geometry(label,w);check('is-emphasized'in g['objective']['classes']and g['objective']['align']=='center'and int(g['objective']['weight'])>=700,label+' objective emphasized',g['objective']);check(g.get('scope')is None or'nl-repair-round'in g['scope'],label+' round style scope mounted')
 check(g['zoom']['aria']=='Μεγέθυνση σχεδίου'and not g['zoom']['text'].strip()and g['zoom']['rect']['width']>=44 and g['zoom']['rect']['height']>=44,label+' accessible compact magnifier',g['zoom']);return g

def zoom(label,largest=False):
 click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');z=read('(()=>{let a=document.querySelector(".diagram-image"),z=document.querySelector(".zoom-image");return{main:a.currentSrc,zoom:z.currentSrc,mainAlt:a.alt,zoomAlt:z.alt,focus:document.activeElement.className,label:document.querySelector(".diagram-tools span").textContent}})()');check(z['main']==z['zoom']and z['mainAlt']==z['zoomAlt'],label+' main and zoom same asset/alt',z)
 if largest:check('/condensed/'in z['main']and z['label']=='Συνεπτυγμένος συντακτικός τύπος'and'Συνεπτυγμένος'in z['mainAlt'],label+' condensed largest representation',z)
 shot(label+'-zoom');key('\ue00c');check(ev('document.activeElement===document.querySelector(".diagram-tools button")&&!document.querySelector(".zoom-dialog")'),label+' Escape closes zoom and restores focus')

def solve(f,label,ri,embedded=False,extensive=False,tall=False):
 prefix='[id$="part-';choice='[id$="choice-';checksel='[id$="check-button"]';expected='Κουίζ '+str(ri+1)+'/3';check(counter()==expected,label+' current-question position before check',counter())
 if f['kind']=='replace':
  wrong=next(p['id']for p in f['parts']if p['id']!=f['targetPartId']);target=prefix+f['targetPartId']+'"]'
  if extensive:
   action(prefix+wrong+'"]',label+' wrong-part','.part-selection-status');status=ev('document.querySelector(".part-selection-status").textContent');check(len(status)>len(f['feedback']['wrongPart']),label+' basic/authored reminder appended',status);shot(label+'-wrongpart')
  action(target,label+' target','.choice-fieldset')
  if extensive:action(target,label+' visible target','.choice-fieldset',visible=True)
  good=next(i for i,c in enumerate(f['choices'])if c['value']==f['correctValue'])
  if extensive:
   original=next(p['text']for p in f['parts']if p['id']==f['targetPartId']);bad=next(i for i,c in enumerate(f['choices'])if c['value']not in [original,f['correctValue']]);action(choice+str(bad)+'"]',label+' incorrect choice','.candidate','.check-helper');action(checksel,label+' incorrect check','.feedback');check(not ev('!!document.querySelector(".feedback.is-success")')and counter()==expected,label+' incorrect check stays on question',ev('document.querySelector(".feedback").textContent'));shot(label+'-incorrect')
  action(choice+str(good)+'"]',label+' correct choice','.candidate','.check-helper')
 else:
  action(prefix+f['correctOrder'][0]+'"]',label+' order-select','.part-selection-status','.order-controls');action('[id$="move-left"]',label+' order-move','.order-controls','.check-helper')
 if tall:viewport(390,320)
 action(checksel,label+' success','.feedback','.round-next button');check(ev('!!document.querySelector(".feedback.is-success")'),label+' actual earned repair');check(counter()==expected,label+' check preserves current position',counter());OUT['repairs'].append({'label':label,'canonicalId':f['id'],'kind':f['kind'],'position':ri+1,'receipt':read('Object.fromEntries(Object.entries(sessionStorage))')});shot(label+'-success')
 if tall:viewport(390,760)

def next_round(label,ri,embedded=False,index=None):
 click('.round-next button',700)
 if ri<2:wait('('+('document.getElementById("nlQuizProgress").textContent'if embedded else'document.querySelector(".round-progress-counter")?.textContent')+')==='+json.dumps('Κουίζ '+str(ri+2)+'/3')+'&&!!document.querySelector(".diagram-image.is-ready")');check(abs(ev('document.getElementById("nlQuizDialog")?.open?document.getElementById("nlQuizDialog").scrollTop:scrollY'))<1,label+' Next starts at top')
 elif embedded:wait('fScenarioPresent().index==='+str(index+1))
 else:
  wait('!!document.querySelector(".results")');check(ev('!document.getElementById("game-root").classList.contains("nl-repair-round")'),label+' results release round scope');shot(label+'-results')

def ready():app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55)
def seed_lesson(index,value):
 ev('(()=>{let s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps}),h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);let key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16),r=JSON.parse(sessionStorage.getItem(key)||"null")||{version:1,content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(key,JSON.stringify(r));return true})()');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def open_lesson():click('#nlQuizOpen');image_ready();check(abs(ev('document.getElementById("nlQuizDialog").scrollTop'))<1,'Lesson opens at top')
try:
 source_guard();viewport(1280,800)
 for si,sdata in enumerate(STATIC):
  direct(False,sdata['id'])
  for ri,f in enumerate(sdata['rounds']):
   label='authored-s'+str(si+1)+'r'+str(ri+1)
   if ri==0:
    for w,h in [(1280,800),(390,760),(320,700)]:viewport(w,h);top();shown(label+'-entry',w)
   viewport(390 if si else 1280,760 if si else 800);top()
   if f['moleculeId']=='ethyl_3_dimethyl_2_5_hexane':
    for w,h in [(1280,800),(390,760),(320,700)]:viewport(w,h);top();shown(label+'-entry',w)
    zoom(label,True)
   elif si==0 and ri==0:zoom(label)
   solve(f,label,ri,extensive=(ri==0),tall=(si==1 and ri==2));next_round(label,ri)
  click('.results-actions button');check(ev('!document.getElementById("game-root").classList.contains("nl-repair-round")&&!!document.getElementById("set-alkanes-unbranched-start")'),'Authored results return picker and release scope')
  click('#workshop-all-sets');check(ev('!!document.getElementById("set-alkanes-start")&&!document.getElementById("game-root").classList.contains("nl-repair-round")'),'Authored picker returns hub unscoped')
 # Generated basic full set: actual native state, saved refresh and results.
 ev('sessionStorage.clear();true');viewport(390,760);direct(True)
 for ri,f in enumerate(GAMES['4']['alkanes-unbranched']['rounds']):
  label='generated-basic-r'+str(ri+1)
  if ri==0:shown('generated-basic-entry',390)
  if ri==1:
   before=read('JSON.parse(sessionStorage.getItem("namelecule-repair-engine-pilot-v1"))');call('browsingContext.reload',{'context':ctx,'wait':'complete'});image_ready();after=read('JSON.parse(sessionStorage.getItem("namelecule-repair-engine-pilot-v1"))');check(before==after and counter()=='Κουίζ 2/3','Generated actual refresh preserves seed, current question and earned first state',{'before':before,'after':after});shot('generated-basic-refreshed')
  solve(f,label,ri,extensive=(ri==0));next_round(label,ri)
 # Challenge seed1 includes actual replacement and order; neutrality verified before earned action.
 ev('sessionStorage.clear();crypto.getRandomValues=(a)=>{a.fill(1);return a;};true');navigate('games/name-repair.html?source=engine');wait('!!document.getElementById("set-alkanes-start")',65);click('#set-alkanes-start');ev('document.getElementById("pilot-difficulty").value="challenge";document.getElementById("pilot-difficulty").dispatchEvent(new Event("change",{bubbles:true}));crypto.getRandomValues=(a)=>{a.fill(1);return a;};true');click('#set-alkanes-branched-start');image_ready();top()
 for ri,f in enumerate(GAMES['1']['alkanes-branched']['rounds']):
  label='generated-challenge-r'+str(ri+1);objective=ev('document.querySelector(".round-objective").textContent');check(objective=='Ένα μέρος του ονόματος δεν συμφωνεί με τη δομή. Εντόπισέ το και επισκεύασέ το.',label+' neutral challenge objective',objective)
  if f['kind']=='replace':
   wrong=next(p['id']for p in f['parts']if p['id']!=f['targetPartId']);action('[id$="part-'+wrong+'"]',label+' neutral wrong-part','.part-selection-status');check(ev('document.querySelector(".part-selection-status").textContent')==f['feedback']['wrongPart'],label+' challenge wrong-part remains neutral')
  if ri==0:shown('generated-challenge-entry',390)
  if f['kind']=='order':zoom(label,True)
  solve(f,label,ri);next_round(label,ri)
 OUT['directCompleted']=True;save()
 exec((H/'check-embedded.py').read_text(),globals());OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:
 OUT['frozenUnchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in OUT.get('target',{}).items());finish()
if not OUT['completed']:raise SystemExit(1)
