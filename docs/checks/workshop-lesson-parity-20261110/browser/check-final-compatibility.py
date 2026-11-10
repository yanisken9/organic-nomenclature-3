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

def ready():
 app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55);
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):click('#rotatePromptDismiss')
def seed_lesson(index,value):
 ev('(()=>{let s=fScenarioPresent(),content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps}),h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);let key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16),r=JSON.parse(sessionStorage.getItem(key)||"null")||{version:1,content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(key,JSON.stringify(r));return true})()');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def open_lesson():click('#nlQuizOpen');image_ready();check(abs(ev('document.getElementById("nlQuizDialog").scrollTop'))<1,'Lesson opens at top')

try:
 source_guard();viewport(1280,800);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library');ready()
 prior=json.loads((H/'root-embedded-r1-final-browser.json').read_text());receipt=next(r['receipt'] for r in reversed(prior['repairs']) if r['label']=='main55-s11r3');earned_storage={k:v for k,v in receipt.items() if k.startswith('namelecule:lesson-checkpoints:v1:')};assert earned_storage
 OUT['lineage']={'gates':'root-embedded-r1-final-browser.json, actual earned six across recorded continuations','exitFixture':'exact genuine full gate receipt restored; correct from=theory-library launch flag required by player; prior Exit correctly returned exploration without that flag.'}
 ev('Object.entries('+json.dumps(earned_storage,ensure_ascii=False)+').forEach(([k,v])=>sessionStorage.setItem(k,v));true');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();ev('fScenarioGo(11);true');wait('fScenarioPresent().index===11&&!MuLERMoCScenario.checkpointPreparation');click('#scExit');wait('location.pathname.endsWith("/design/theory-library.html")');check(True,'Main55 library-launched Exit returns library')
 viewport(1280,800);navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');ready()
 for i in (1,2,3):click('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
 seed_lesson(3,'4');open_lesson();f=GAMES['4']['alkanes-unbranched']['rounds'][0];solve(f,'main54-s4r1',0,True);check(ev('document.getElementById("scNext").disabled&&!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Main54 same-source earned first round leaves required gate locked');click('#nlQuizBack');check(not ev('document.getElementById("nlQuizDialog").open'),'Main54 close returns to lesson');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
