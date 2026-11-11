from pathlib import Path
exec((Path(__file__).with_name('driver.py')).read_text())
OUT={'checks':[],'solved':[],'conditions':'Owned headless Firefox; actual production UI, native viewer and verified chemistry Worker. Read-only preload observes bridge loads for deterministic test inputs; trusted pointer input submits answers.'}
def check(ok,label,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError((label,detail))
def pause(sec=.3):time.sleep(sec)
def viewport(w,h=900):call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});pause()
def ready():
 app_ready();wait('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',60)
def lesson(index=3,version=55):
 open_page(f'mulermoc-nom-{version}.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library#step={index+1}');ready()
def rec():return read('(()=>{let c=JSON.stringify({version:1,title:String(fScenarioPresent().title||""),author:String(fScenarioPresent().author||"Unknown"),steps:fScenarioPresent().steps});return Object.values(sessionStorage).map(v=>{try{return JSON.parse(v)}catch(e){}}).find(v=>v?.content===c)})()')
def open_gate():wait('!!document.getElementById("nlQuizOpen")&&!document.getElementById("nlQuizOpen").disabled',60);click('#nlQuizOpen');wait('document.getElementById("nlQuizDialog").open')
def choose(game):
 if ev('!!document.querySelector(".nl-game-choice-switch")'):click('.nl-game-choice-switch')
 wait('!!document.querySelector(".nl-game-choice-card")');click('.nl-game-choice-card:nth-child('+('2'if game=='builder'else'1')+')')
 if game=='builder':builder_ready()
 else:wait('!!document.querySelector(".diagram-image.is-ready")',60)
B='document.querySelector(".nl-builder-frame").contentDocument'
def bel(sel):return B+'.querySelector('+json.dumps(sel)+')'
def bread(expr):return read('document.querySelector(".nl-builder-frame").contentWindow.eval('+json.dumps(expr)+')')
def builder_ready():
 wait('!!document.querySelector(".nl-builder-frame")');wait('!!document.querySelector(".nl-builder-frame").contentDocument?.querySelector("#bank-tiles button")||!!document.querySelector(".nl-builder-error")',65)
 check(not ev('!!document.querySelector(".nl-builder-error")'),'Builder verified/native ready',ev('document.querySelector(".nl-builder-error")?.textContent'))
def clickel(expr):
 ev('('+expr+').scrollIntoView({block:"center",inline:"nearest",behavior:"instant"});true');pause(.12)
 p=read('(()=>{let e='+expr+',r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,w=e.ownerDocument.defaultView;while(w!==window){let q=w.frameElement.getBoundingClientRect();x+=q.x;y+=q.y;w=w.parent}return{x:Math.round(x),y:Math.round(y),disabled:!!e.disabled}})()')
 assert not p['disabled'],p
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'choice-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':p['x'],'y':p['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});pause(.14)
def bc(sel):clickel(bel(sel))
def footer(label,final=True):
 pause(.8);data=read('({buttons:[...document.querySelectorAll(".round-next button")].map(e=>e.textContent),headerHidden:document.getElementById("nlQuizReturn")?.hidden,header:[...document.querySelectorAll(".nl-quiz-dialog-header button")].map(e=>({text:e.textContent,hidden:e.hidden})),count:document.getElementById("nlQuizProgress").textContent})')
 check(len(data['buttons'])==(3 if final else 1),label+' footer action count',data)
 if final:check(all(e['hidden'] for e in data['header']),label+' no duplicate header action',data)
 return data
def bsolve(label,representation=False,partial_refresh=False):
 builder_ready();load=bread('__lessonLoad');round=load['round'];check(round['moleculeId']==load['moleculeId'],label+' load identity')
 tiles=bread('NameleculeNameBuilderEngine.createBank(__lessonLoad.round,{seed:__lessonLoad.bankSeed})');used=set();ids=[]
 for piece in round['pieces']:
  tile=next(t for t in tiles if t['id'] not in used and t['text']==piece['text'] and t['separatorBefore']==piece['separatorBefore']);ids.append(tile['id']);used.add(tile['id'])
 bc('#bank-tiles [data-tile-id='+json.dumps(ids[0])+']')
 check(bread('document.querySelector("#answer-tiles button").dataset.tileId')==ids[0],label+' actual clicked tile identity')
 if representation:
  before=bread('[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId)')
  for mode in ['expanded']+(['skeletal']if'skeletal'in round['representations']else[])+['3d','condensed']:
   selector='[data-representation='+json.dumps(mode)+']';bc(selector);wait(bel(selector)+'.getAttribute("aria-pressed")==="true"',55)
   check(bread('[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId)')==before,label+' '+mode+' preserves answer')
  bc('#zoom-in');bc('#zoom-out');check(bread('[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId)')==before,label+' zoom preserves answer')
  if round['moleculeId']=='methane':check(bread('document.querySelector("[data-representation=skeletal]").disabled'),label+' methane skeletal unavailable')
 if partial_refresh:
  before=rec();call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();builder_ready();check(bread('[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId)')==[ids[0]],label+' cold refresh partial preserved');check(bread('document.querySelector("#answer-tiles button").getAttribute("aria-pressed")')=='true',label+' selected answer retained')
 for tid in ids[1:]:bc('#bank-tiles [data-tile-id='+json.dumps(tid)+']')
 check(bread('document.getElementById("candidate-name").textContent')==round['correctName'],label+' composed name exact')
 bc('#check-answer');wait('!!document.querySelector(".round-next button")');check(bread('document.getElementById("feedback").classList.contains("success")'),label+' correct native check',bread('document.getElementById("feedback").className'))
 check(bool(bread('document.querySelector(".lesson-explanation")?.textContent')),label+' explanation supplied')
 OUT['solved'].append({'label':label,'game':'builder','moleculeId':round['moleculeId'],'name':round['correctName'],'load':load})
 print(label,round['moleculeId'],flush=True);return round['moleculeId']
def rround(index,practice=False):
 state=rec()['practices'if practice else'states'][str(index)]['games']['repair'];seed=state['seed']
 ev('(async()=>{window.__testCanonical=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput();return true})()')
 return read('NameleculeRepairGenerator.createGame(__testCanonical.catalog,__testCanonical.analyses,{seed:'+json.dumps(seed)+',difficulty:"basic"}).sets.find(e=>e.id==='+json.dumps('alkanes-unbranched'if index==3else'alkanes-branched')+').rounds['+str(state['currentRound'])+']')
def rsolve(label,index,practice=False):
 wait('!!document.querySelector(".diagram-image.is-ready")');r=rround(index,practice)
 if r['kind']=='replace':
  click('[id$="part-'+r['targetPartId']+'"]');good=next(i for i,c in enumerate(r['choices'])if c['value']==r['correctValue']);click('[id$="choice-'+str(good)+'"]')
 else:
  for dest,pid in enumerate(r['correctOrder']):
   order=read('[...document.querySelectorAll(".part-button")].map(e=>e.id.split("part-")[1])');pos=order.index(pid)
   if pos>dest:
    click('[id$="part-'+pid+'"]')
    for _ in range(pos-dest):click('[id$="move-left"]')
 click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")&&!!document.querySelector(".round-next button")')
 OUT['solved'].append({'label':label,'game':'repair','moleculeId':r['moleculeId'],'kind':r['kind']});print(label,r.get('moleculeId'),flush=True);return r
call('script.addPreloadScript',{'functionDeclaration':'''() => {addEventListener('message',e=>{if(e.data?.channel==='namelecule-builder-lesson-v1'&&e.data.command==='load')window.__lessonLoad=e.data;});}'''})
try:
 lesson(10);check(ev('fScenarioPresent().index')==3,'Direct step11 cannot bypass gate4');open_gate();choose('builder')
 bsolve('Mixed builder1');click('.round-next button');builder_ready();bsolve('Mixed builder2');check(not rec()['states']['3']['solved'],'Two Builder successes not enough')
 choose('repair');rsolve('Mixed repair1',3);check(not rec()['states']['3']['solved'],'Mixed2Builder+1Repair does not unlock')
 before=rec()['states']['3'];call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');check(rec()['states']['3']['games']['builder']['states'][:2]==before['games']['builder']['states'][:2],'Mixed pergame evidence survives cold refresh')
 choose('builder');builder_ready();check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 2/3' and ev('!!document.querySelector(".round-next button")'),'Returning to partial Builder resumes completed second');click('.round-next button');builder_ready();check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 3/3','Preserved Builder can continue to third');choose('repair');wait('!!document.querySelector(".diagram-image.is-ready")');click('.round-next button');wait('!!document.querySelector(".diagram-image.is-ready")')
 for i in [1,2]:
  rsolve('Required Repair unbranched'+str(i+1),3);footer('Repair unbranched'+str(i+1),i==2)
  if i<2:click('.round-next button');wait('!!document.querySelector(".diagram-image.is-ready")')
 check(rec()['states']['3']['earned']['game']=='repair','Repair independently earns unbranched gate');click('.round-next button');wait('fScenarioPresent().index===4');ev('location.hash="step=11";true');wait('fScenarioPresent().index===10');open_gate();choose('repair')
 for i in range(3):
  r=rsolve('Required Repair branched'+str(i+1),10);footer('Repair branched'+str(i+1),i==2)
  if i<2:click('.round-next button');wait('!!document.querySelector(".diagram-image.is-ready")')
 check(rec()['states']['10']['earned']['game']=='repair','Repair independently earns branched gate');shot('repair-branched-final.png');earned=rec()['states']['10']['earned']
 click('.round-next button:nth-child(3)');builder_ready();check(rec()['practices']['10']['selected']=='builder','Other game from Repair selects Builder');check(rec()['states']['10']['earned']==earned,'Required Repair receipt remains exact during Builder optional')
 # Layout across narrow widths; no source or receipt mutation.
 choose('repair');choose('builder');builder_ready()
 for w in [390,320]:
  viewport(w,760);check(ev('document.documentElement.scrollWidth<=innerWidth'),'No parent horizontal overflow '+str(w));check(bread('document.documentElement.scrollWidth<=innerWidth'),'No Builder page horizontal overflow '+str(w));shot('builder-'+str(w)+'.png');
  choose('repair');choose('builder');builder_ready()
 viewport(390,760);bsolve('Narrow optional Builder');footer('Narrow first',False);shot('builder-390-success.png')
 # Native depiction focus Escape returns to checkpoint without removing earned access.
 clickel(B+'.getElementById("molecule-viewer").contentDocument.querySelector("body")');call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'escape-key','actions':[{'type':'keyDown','value':'\ue00c'},{'type':'keyUp','value':'\ue00c'}]}]});wait('!document.getElementById("nlQuizDialog").open');check(rec()['states']['10']['earned']==earned,'Native-focused Escape preserves earned receipt')
 # Choice cards and logos fit a narrow modal, keyboard native buttons remain available.
 open_gate();choose('repair');click('.nl-game-choice-switch');viewport(320,760);shot('choice-320.png');check(ev('[...document.querySelectorAll(".nl-game-choice-card")].every(e=>e.scrollWidth<=e.clientWidth&&e.querySelector("img").naturalWidth>0)'),'Narrow choices both logos/text fit')
 # Save authentic earned evidence, then check compatible Main54 and final exploration.
 saved=read('Object.fromEntries(Object.entries(sessionStorage))');OUT['earnedStorage']=saved;viewport(1500,1000);lesson(10,54);check(ev('fScenarioPresent().index')==10,'Main54 reads shared verified progress');open_gate();wait('!!document.querySelector(".nl-game-choice-card")||!!document.querySelector(".diagram-image.is-ready")');check(not ev('!!document.querySelector(".nl-quiz-error")'),'Main54 new adapter available')
 # Older generated-only lesson keeps its previous game and does not open chooser.
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1#step=4');ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")',60);check(not ev('!!document.querySelector(".nl-game-choice-card")'),'Legacy lesson remains single Workshop')
 # Standalone Builder retains its own header/next and real success UI.
 open_page('games/name-builder.html?molecule=butane');wait('!!document.querySelector("#bank-tiles button")',60);check(ev('!document.documentElement.classList.contains("lesson-mode")&&getComputedStyle(document.querySelector(".site-header")).display!=="none"&&getComputedStyle(document.getElementById("next-molecule")).display!=="none"'),'Standalone Builder unchanged mode/header/next')
 # Standalone Workshop retains its dedicated landing flow.
 open_page('games/name-repair.html');wait('!!document.querySelector("#game-root")');check(not ev('!!document.querySelector(".nl-game-choice-card")'),'Standalone Workshop unaffected')
 OUT['passed']=True;OUT['jsExceptions']=js_errors
except Exception as e:
 OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('matrix-failure.png');raise
finally:
 (HERE/'matrix-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
