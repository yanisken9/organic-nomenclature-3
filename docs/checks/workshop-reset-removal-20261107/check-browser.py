from pathlib import Path
import os,json,copy,traceback
HERE=Path('docs/checks/workshop-reset-removal-20261107')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
fixtures=json.loads(Path('docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json').read_text())
games={g['seed']:{s['id']:s for s in g['sets']} for g in fixtures}
reminders={
 'parent-length':'Η αποστολή αφορά το πλήθος των ατόμων C της κύριας αλυσίδας.',
 'bond-type':'Η αποστολή αφορά το είδος των δεσμών μεταξύ ατόμων C.',
 'branch-locants':'Η αποστολή αφορά τις θέσεις σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
 'branch-multiplier':'Η αποστολή αφορά το πλήθος των ίδιων διακλαδώσεων.'}
out={'completed':False,'checks':[],'rounds':[],'fixture_policy':'Isolated profile. Actual canonical fixtures from previous pinned-core run. Seed4 unbranched and seed1 branched; all six lesson rounds solved through UI, no solved receipts injected. Before/after shared mount comparison uses same canonical rounds. Static standalone uses original game data.','limitations':['Headless isolated Firefox; no user-facing Firefox freeze diagnosis','No Safari, physical mobile, screen reader or full conference sequence audit','No new viewer/3D audit; existing JSmol issue remains outside scope']}
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

def actions_only_check(scope=''):
 selector=scope+' .repair-actions' if scope else '.repair-actions'
 return ev('(()=>{const a=document.querySelector('+json.dumps(selector)+');return !!a&&a.children.length===1&&a.children[0].textContent==="Έλεγχος"&&!a.textContent.includes("null")&&!document.body.textContent.includes("Από την αρχή")})()')

try:
 # Reproduce the old UI using its saved source and compare the same live mount.
 navigate('games/name-repair.html?v=workshop-reset-removal-20261107-r1')
 until('!!document.querySelector("#set-alkanes-start")')
 ev('document.getElementById("game-root").removeAttribute("id");document.body.replaceChildren(Object.assign(document.createElement("main"),{id:"test-host",className:"game-root"}));true')
 examples=[games['4']['alkanes-unbranched']['rounds'][0],games['1']['alkanes-branched']['rounds'][1]]
 observed={}
 for phase,path in [('before','docs/checks/workshop-reset-removal-20261107/before/js/namelecule-game-repair.js'),('after','js/namelecule-game-repair.js')]:
  ev('(async()=>{(0,eval)(await(await fetch("/'+path+'",{cache:"reload"})).text());return true})()')
  for d in examples:
   ev('window.testApi=NameleculeRepairGame.mountRound(document.getElementById("test-host"),{round:'+json.dumps(d,ensure_ascii=False)+',assetBase:location.origin+"/games/"});true')
   until('!!document.querySelector(".diagram-image.is-ready")')
   count=ev('[...document.querySelectorAll(".repair-actions button")].filter(x=>x.textContent==="Από την αρχή").length')
   check(count==(1 if phase=='before' else 0),phase+' shared '+d['kind']+' reset presence matches requirement')
   st=json.loads(ev('JSON.stringify(testApi.getState())'));st.pop('choiceOrder',None)
   if phase=='before':observed[d['kind']]=st
   else:check(st==observed[d['kind']] and actions_only_check(),'Same initial '+d['kind']+' state; Check is sole repair action without null artifact')
   if d['kind']=='replace':screenshot(HERE/(phase+'-replacement.png'))
   ev('testApi.destroy();true')
 navigate('design/theory-library.html?v=workshop-reset-removal-20261107-r1');click('article[aria-labelledby=alkanes-title] a.action');ready()
 check(ev('[...document.scripts].some(s=>s.src.includes("namelecule-game-repair.js?v=workshop-reset-removal-20261107-r1"))'),'Main loads updated shared game cache URL')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 for set_id,index,destination,seed_value in [('alkanes-unbranched',3,4,'4'),('alkanes-branched',10,11,'1')]:
  if index==10:ev('fScenarioGo(10);true');until('fScenarioPresent().index===10')
  seed(index,seed_value);open_quiz()
  for ri,d in enumerate(games[seed_value][set_id]['rounds']):
   check(mounted()['id']==d['id'] and actions_only_check('#nlQuizDialog'),'Embedded '+set_id+' round '+str(ri)+' has only Check action')
   if ri==0 and index==3:
    wrong=next(p for p in d['parts'] if p['id']!=d['targetPartId'])
    pointer('[id$="-part-'+wrong['id']+'"]')
    check(message().startswith(d['feedback']['wrongPart']) and ev('document.querySelector("[id$=-check-button]").disabled'),'Wrong component still gives reminder and leaves Check disabled')
    click('[id$="-part-'+d['targetPartId']+'"]')
    original=next(p['text'] for p in d['parts'] if p['id']==d['targetPartId'])
    bad=next(i for i,c in enumerate(d['choices']) if c['value'] not in [d['correctValue'],original])
    click('[id$="-choice-'+str(bad)+'"]')
    call('browsingContext.activate',{'context':ctx});ev('window.testKeys=[];document.addEventListener("keydown",e=>testKeys.push({key:e.key,trusted:e.isTrusted}),true);document.querySelector("[id$=-check-button]").focus();true')
    call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'reset-removal-key','actions':[{'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]})
    check(state(index)['states'][ri]['attempts']==1 and ev('testKeys.some(k=>k.key==="Enter"&&k.trusted)'),'Native Enter submits wrong choice and increments attempts')
    good=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue'])
    click('[id$="-choice-'+str(good)+'"]')
    check(ev('document.querySelector(".candidate-name").textContent')==d['correctName'] and state(index)['states'][ri]['attempts']==1,'Replacement can change directly after wrong Check without resetting attempts')
    click('[id$="-part-'+wrong['id']+'"]');click('[id$="-part-'+d['targetPartId']+'"]')
    check(state(index)['states'][ri]['selectedValue'] is None and state(index)['states'][ri]['attempts']==1,'Component can change directly after wrong Check')
    click('[id$="-choice-'+str(good)+'"]');saved=state(index)
    click('#nlQuizBack');open_quiz()
    check(stable_progress(state(index))==stable_progress(saved) and actions_only_check('#nlQuizDialog'),'Reopen preserves active selection/counters without reset')
    reload();open_quiz()
    check(stable_progress(state(index))==stable_progress(saved) and actions_only_check('#nlQuizDialog'),'Refresh restores active selection/counters without reset')
    for width in [390,320]:
     call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':844},'devicePixelRatio':1})
     if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
     ev('document.querySelector(".repair-actions").scrollIntoView({block:"center"});true')
     check(ev('(()=>{const b=document.querySelector(".repair-actions button").getBoundingClientRect();return b.left>=0&&b.right<=innerWidth&&b.top>=0&&b.bottom<=innerHeight})()') and actions_only_check('#nlQuizDialog'),'Sole Check button fits '+str(width)+'px')
     screenshot(HERE/('lesson-'+str(width)+'.png'))
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
   if d['kind']=='order':
    click('[id$="-check-button"]');check(state(index)['states'][ri]['attempts']==1 and not state(index)['states'][ri]['solved'],'Original ordering can be checked and retried')
    click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]')
    check(ev('document.querySelector(".candidate-name").textContent')==d['correctName'],'Ordering can be corrected directly after wrong Check')
    click('[id$="-move-right"]');check(state(index)['states'][ri]['order']!=d['correctOrder'],'Ordering can be reversed with movement controls')
    saved=state(index);reload();open_quiz()
    check(stable_progress(state(index))==stable_progress(saved) and actions_only_check('#nlQuizDialog'),'Ordering selection/attempt/order restore without reset')
   solve(d)
   check(ev('document.getElementById("scNext").disabled')==(ri<2),'Embedded gate requires three solved rounds '+set_id+' '+str(ri+1))
   click('#nlQuizDialog .round-next button')
   if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']))
   else:until('fScenarioPresent().index==='+str(destination))
  check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(index)+')'),'Completed '+set_id+' gate unlocks theory')
 saved=json.loads(ev('JSON.stringify(testReceiptInfo().record)'));reload()
 check(ev('fScenarioPresent().index===11&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)') and json.loads(ev('JSON.stringify(testReceiptInfo().record)'))==saved,'Both completed receipts restore exactly after refresh')
 # Real standalone branch set exercises its existing separate progression UI.
 navigate('games/name-repair.html?v=workshop-reset-removal-20261107-r1');until('!!document.querySelector("#set-alkanes-start")')
 check(ev('[...document.scripts].some(s=>s.src.includes("namelecule-game-repair.js?v=workshop-reset-removal-20261107-r1"))'),'Standalone loads updated shared game cache URL')
 click('#set-alkanes-start');click('#set-alkanes-branched-start')
 static=json.loads(Path('games/data/name-repair-alkanes.json').read_text());rounds=next(s['rounds'] for s in static['sets'] if s['id']=='alkanes-branched')
 for ri,d in enumerate(rounds):
  until('!!document.querySelector(".diagram-image.is-ready")')
  check(actions_only_check(),'Standalone '+d['kind']+' round '+str(ri)+' has only Check')
  if d['kind']=='replace':
   click('#part-'+d['targetPartId']);bad=next(i for i,c in enumerate(d['choices']) if c['value']!=d['correctValue'] and c['value']!=next(p['text'] for p in d['parts'] if p['id']==d['targetPartId']))
   click('#choice-'+str(bad));click('#check-button');check(not ev('!!document.querySelector(".feedback.is-success")'),'Standalone wrong replacement remains editable')
   good=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue']);click('#choice-'+str(good))
  else:
   click('#check-button');click('#part-'+d['correctOrder'][0]);click('#move-left');click('#move-right');click('#move-left')
   check(ev('document.querySelector(".candidate-name").textContent')==d['correctName'],'Standalone ordering can move both directions after wrong Check')
   screenshot(HERE/'standalone-order.png')
  click('#check-button');until('!!document.querySelector(".feedback.is-success")');click('.round-next button')
  if ri<2:until('!!document.querySelector(".diagram-image.is-ready")&&document.querySelector(".broken-name").textContent!=='+json.dumps(''.join(p['text'] for p in d['parts'])))
 check(ev('!!document.querySelector(".results")&&document.querySelectorAll(".result-item").length===3'),'Standalone three-round results and Continue remain functional')
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
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
