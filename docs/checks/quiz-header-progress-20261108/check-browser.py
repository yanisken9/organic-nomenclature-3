from pathlib import Path
import os,json,copy,traceback
HERE=Path('docs/checks/quiz-header-progress-20261108')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text())
games={g['seed']:{s['id']:s for s in g['sets']} for g in fixtures}
reminders={
 'parent-length':'Η αποστολή αφορά το πλήθος των ατόμων C της κύριας αλυσίδας.',
 'bond-type':'Η αποστολή αφορά το είδος των δεσμών μεταξύ ατόμων C.',
 'branch-locants':'Η αποστολή αφορά τις θέσεις σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
 'branch-multiplier':'Η αποστολή αφορά το πλήθος των ίδιων διακλαδώσεων.'}
out={'completed':False,'checks':[],'rounds':[],'fixture_policy':'Owned profile. Seed4 unbranched/seed1 branched only; all6 repairs solved through actual UI, no fabricated solved receipts. Actual frozen canonical fixtures and unchanged current9 lesson JSON.','limitations':['Headless isolated Firefox; no user-facing Firefox freeze diagnosis','No Safari, physical mobile, screen reader or full conference sequence audit','No new viewer/3D audit; existing JSmol issue remains outside scope']}
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS '+name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('MuLERMoCScenario.present&&!!fScenarioPresent()&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('''window.testReceiptInfo=function(){const s=fScenarioPresent();const content=JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key="namelecule:lesson-checkpoints:v1:"+(h>>>0).toString(16);return {key,content,record:JSON.parse(sessionStorage.getItem(key)||"null")}};window.testOriginalMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.testMounted=JSON.parse(JSON.stringify(options.round));return testOriginalMount(host,options)};true''')
def reload():
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
def seed(index,value):
 ev('(()=>{const i=testReceiptInfo();const r=i.record||{version:1,content:i.content,states:{}};r.states['+str(index)+']={version:1,seed:'+json.dumps(value)+',currentRound:0,states:[null,null,null],solved:false};sessionStorage.setItem(i.key,JSON.stringify(r));return true})()');reload()
def open_quiz():
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testMounted',seconds=45)
def mounted():return json.loads(ev('JSON.stringify(testMounted)'))
def state(index):return json.loads(ev('JSON.stringify(testReceiptInfo().record.states['+str(index)+'])'))
def stable_progress(value):
 result=copy.deepcopy(value)
 # Existing adapter intentionally resets unvisited later rounds; their random
 # choice order is not an answered/current selection or completion receipt.
 for i,s in enumerate(result['states']):
  if i>result['currentRound'] and s and not s['solved'] and s['attempts']==0 and s['selectedPartId'] is None:
   s['choiceOrder']=[]
 return result
def message():return ev('document.querySelector("#nlQuizDialog .part-selection-status").textContent')
def pointer(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center"});true')
 pos=json.loads(ev('JSON.stringify((()=>{const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})())'))
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'feedback-mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':pos['x'],'y':pos['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def solve(round):
 if round['kind']=='replace':
  click('[id$="-part-'+round['targetPartId']+'"]');i=next(i for i,c in enumerate(round['choices']) if c['value']==round['correctValue']);click('[id$="-choice-'+str(i)+'"]')
 else:
  click('[id$="-part-'+round['correctOrder'][0]+'"]');click('[id$="-move-left"]')
 click('[id$="-check-button"]');until('!!document.querySelector("#nlQuizDialog .feedback.is-success")')

def counter():return ev('document.getElementById("nlQuizProgress").textContent')
def header_layout(width):
 result=json.loads(ev('JSON.stringify((()=>{const ids=["nlQuizDialogTitle","nlQuizProgress","nlQuizBack"];return Object.fromEntries(ids.map(id=>{const e=document.getElementById(id),b=e.getBoundingClientRect();return[id,{left:b.left,right:b.right,top:b.top,bottom:b.bottom,hit:e.contains(document.elementFromPoint((b.left+b.right)/2,(b.top+b.bottom)/2))}]}))})())'))
 out.setdefault('headerBounds',[]).append({'width':width,'elements':result})
 separated=all(max(a['left'],b['left'])>=min(a['right'],b['right']) or max(a['top'],b['top'])>=min(a['bottom'],b['bottom']) for i,a in enumerate(result.values()) for b in list(result.values())[i+1:])
 return separated and all(r['left']>=0 and r['right']<=width and r['hit'] for r in result.values())

try:
 navigate('design/theory-library.html?v=quiz-header-progress-20261108-r1');click('article[aria-labelledby=alkanes-title] a.action');ready()
 check(ev('[...document.scripts].some(s=>s.src.includes("namelecule-generated-repair-checkpoint.js?v=quiz-header-progress-20261108-r1"))&&[...document.styleSheets].some(s=>(s.href||"").includes("namelecule-quiz-checkpoints.css?v=quiz-header-progress-20261108-r1"))'),'Updated adapter and CSS cache URLs loaded')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 for set_id,index,destination,seed_value in [('alkanes-unbranched',3,4,'4'),('alkanes-branched',10,11,'1')]:
  if index==10:ev('fScenarioGo(10);true');until('fScenarioPresent().index===10')
  seed(index,seed_value);open_quiz()
  for ri,d in enumerate(games[seed_value][set_id]['rounds']):
   expected='Κουίζ '+str(ri+1)+'/3'
   check(mounted()['id']==d['id'] and counter()==expected,'Header shows actual '+set_id+' round '+str(ri+1)+'/3')
   check(ev('document.querySelector(".nl-quiz-dialog-header").contains(document.getElementById("nlQuizProgress"))&&!document.getElementById("nlQuizProgress").hidden&&document.getElementById("nlQuizProgress").getAttribute("aria-live")==="polite"&&document.getElementById("nlQuizProgress").getAttribute("aria-atomic")==="true"'),'Progress lives in stable polite header slot '+set_id+' '+str(ri))
   check(ev('document.querySelector(".nl-quiz-set-progress").getAttribute("role")===null&&!document.querySelector(".nl-quiz-set-progress").textContent.includes("Κουίζ")'),'Old content keeps set title without duplicate counter announcement '+set_id+' '+str(ri))
   if index==3 and ri==0:
    screenshot(HERE/'counter-1-desktop.png')
    click('[id$="-part-'+d['targetPartId']+'"]');original=next(p['text'] for p in d['parts'] if p['id']==d['targetPartId']);bad=next(i for i,c in enumerate(d['choices']) if c['value'] not in [d['correctValue'],original]);click('[id$="-choice-'+str(bad)+'"]');click('[id$="-check-button"]')
    check(counter()==expected and state(index)['states'][ri]['attempts']==1,'Incorrect Check increments attempts but counter stays1/3')
   if index==3 and ri==1:
    saved=state(index);click('#nlQuizBack')
    check(ev('document.getElementById("nlQuizProgress").hidden&&document.getElementById("nlQuizProgress").textContent===""'),'Closing clears header progress')
    open_quiz();check(counter()==expected and stable_progress(state(index))==stable_progress(saved),'Reopen restores actual2/3 and saved progress')
    reload();open_quiz();check(counter()==expected and stable_progress(state(index))==stable_progress(saved),'Refresh restores actual2/3 and saved progress')
    for width,height in [(1500,600),(390,700),(320,640)]:
     call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
     if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
     until('document.getElementById("nlQuizDialog").scrollHeight>document.getElementById("nlQuizDialog").clientHeight')
     ev('document.getElementById("nlQuizDialog").scrollTop=0;true')
     check(header_layout(width),'Counter/title/Back separated and hittable before scroll '+str(width))
     initial_top=ev('document.getElementById("nlQuizProgress").getBoundingClientRect().top')
     ev('(()=>{const q=document.getElementById("nlQuizDialog");q.scrollTop=q.scrollHeight;return true})()')
     check(ev('document.getElementById("nlQuizDialog").scrollTop>0') and abs(ev('document.getElementById("nlQuizProgress").getBoundingClientRect().top')-initial_top)<1 and header_layout(width),'Counter stays visible while scrolling '+str(width))
     screenshot(HERE/('counter-scrolled-'+str(width)+'.png'))
    # A real click on the sticky Back must stay available at320px.
    pointer('#nlQuizBack');check(ev('!document.getElementById("nlQuizDialog").open'),'Real sticky Back pointer closes at320px')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});open_quiz();check(counter()==expected,'Counter remains2/3 after responsive Back/reopen')
   if d['kind']=='order':
    click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]');click('[id$="-move-right"]');click('[id$="-check-button"]')
    check(counter()==expected and not state(index)['states'][ri]['solved'],'Ordering movement/incorrect Check do not advance2/3')
   solve(d)
   check(counter()==expected,'Correct Check alone keeps current round '+set_id+' '+str(ri+1))
   check(ev('document.getElementById("scNext").disabled')==(ri<2),'Learner gate requires all3solved repairs '+set_id+' '+str(ri+1))
   if ri==2:screenshot(HERE/('counter-3-'+set_id+'.png'))
   click('#nlQuizDialog .round-next button')
   if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']))
   else:until('fScenarioPresent().index==='+str(destination))
  check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(index)+')&&document.getElementById("nlQuizProgress").hidden'),'Continue completes set and clears closed header '+set_id)
 # Revisit solved set: actual stored final round should show3/3.
 ev('fScenarioGo(3);true');open_quiz();check(counter()=='Κουίζ 3/3','Revisited completed first set restores3/3')
 click('#nlQuizBack')
 # Existing authored single-question checkpoint must not inherit a set counter.
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-name-repair-pilot.scenario.json&present=1#step=10');ready();click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',seconds=45)
 check(ev('document.getElementById("nlQuizProgress").hidden&&document.getElementById("nlQuizProgress").textContent===""'),'Legacy single-question checkpoint has no stale set counter')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
