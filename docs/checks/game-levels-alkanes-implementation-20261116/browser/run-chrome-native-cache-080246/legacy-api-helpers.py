"""Bounded genuine legacy migration and authoring contract checks; no startup."""
def fresh_tab():
 global ctx
 previous=ctx;ctx=call('browsingContext.create',{'type':'tab'})['context'];call('browsingContext.close',{'context':previous});viewport(1500,1000)

def comparable_progress(progress,game):
 result=json.loads(json.dumps(progress));removed=[]
 if game=='repair':
  for index,state in enumerate(result['states']):
   if index>result['currentRound'] and state.get('selectedPartId') is None and state.get('selectedValue') is None and not state.get('order') and not state.get('attempts') and not state.get('submitted') and not state.get('solved'):
    if 'choiceOrder' in state:removed.append(index);del state['choiceOrder']
 return result,removed

def learner_records():
 return read('Object.values(sessionStorage).map(v=>{try{return JSON.parse(v)}catch(_){return null}}).filter(v=>v&&typeof v.content==="string"&&v.states)')

def author_contract():
 fresh_tab();page('mulermoc-nom-57.html?scenario=scenarios/alkanes-user-3.scenario.json');ready()
 before=learner_records();check(not any(any(s.get('solved') or s.get('legacyEarned') or s.get('receipts') for s in r['states'].values()) for r in before),'fresh author profile has no earned learner receipts')
 click('#scenarioAuthorTab');wait('MuLERMoCScenario.authoring&&!MuLERMoCScenario.present')
 for index in [4,10]:
  # Explicitly authorized public authoring API, not a claimed screen click.
  ev('fScenarioAuthorPreviewBegin(fScenarioActive().id,'+str(index)+');true')
  wait('MuLERMoCScenario.present&&fScenarioPresent().index==='+str(index)+'&&fScenarioIsAuthorPreview(fScenarioPresent())')
  check(learner_records()==before,'author-preview API step'+str(index+1)+' bypasses learner gates without learner receipt writes')
  shot('author-preview-api-step'+str(index+1));click('#scExit');wait('!MuLERMoCScenario.present')
 payload=json.loads(ev('''(async()=>{const original=fScenarioSaveBlob;let result=null;try{fScenarioSaveBlob=async(name,blob)=>{result={name,type:blob.type,text:await blob.text()};return true};await fScenarioExport(fScenarioActive().id);return JSON.stringify(result)}finally{fScenarioSaveBlob=original}})()'''))
 exported=json.loads(payload['text'])
 check(exported['scenarioVersion']==2 and exported['steps'][3]['checkpoint']['round']['requiredLevels']==[1] and exported['steps'][10]['checkpoint']['round']['requiredLevels']==[1,2] and exported['steps'][10]['checkpoint']['round']['allowedLevels']==[1,2,3] and len(exported['steps'][11]['menuSubset'])==14,'actual Export API Blob preserves v2 recipes and14menu; no disk save')
 validated=read('fScenarioValidate('+json.dumps(exported)+')')
 check(validated['ok'] and len(validated['steps'][11]['menuSubset'])==14,'actual exported v2 payload revalidates through application API')
 prior_id=read('fScenarioActive().id')
 ev('fScenarioImportFile(new File(['+json.dumps(payload['text'])+'],"bounded-roundtrip.json",{type:"application/json"}));true')
 wait('fScenarioActive().id!=='+json.dumps(prior_id)+'&&fScenarioActive().steps.length===12&&fScenarioActive().steps[10].checkpoint.round.version===2')
 actual=read('({round4:fScenarioActive().steps[3].checkpoint.round,round11:fScenarioActive().steps[10].checkpoint.round,menu:fScenarioActive().steps[11].menuSubset})')
 check(actual['round4']==exported['steps'][3]['checkpoint']['round'] and actual['round11']==exported['steps'][10]['checkpoint']['round'] and actual['menu']==exported['steps'][11]['menuSubset'],'actual FileReader Import API roundtrip retains exact new contracts')
 check(learner_records()==before,'preview/Export/Import APIs add no learner receipt')
 OUT['authorContract']={'kind':'Actual author-preview/Export/FileReader Import APIs; author tab and Exit are trusted clicks. SaveBlob delivery intercepted only to inspect generated Blob in memory; no disk/download.','previewSteps':[5,11],'exportFilename':payload['name'],'exportSHA256':hashlib.sha256(payload['text'].encode()).hexdigest(),'contract':actual}

def visible_level_panel():
 global INDEX
 for index in range(5,11):pause(.3);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index
 open_gate();click('.nl-game-choice-card:nth-child(4)');wait('document.querySelectorAll("#nlQuizDialog [data-level]").length===3')
 for width,height in [(1500,1000),(390,844)]:
  viewport(width,height)
  ev('(()=>{const d=document.getElementById("nlQuizDialog"),n=d.querySelector(".nl-game-choice-note");n.scrollIntoView({block:"start",behavior:"instant"});d.scrollBy({top:-d.querySelector(".nl-quiz-dialog-header").getBoundingClientRect().height-12,behavior:"instant"})})()');pause(.3)
  proof=read('({status:[...document.querySelectorAll("#nlQuizDialog .nl-game-choice-note")].map(e=>e.textContent),levels:[...document.querySelectorAll("#nlQuizDialog [data-level]")].map(e=>({level:e.dataset.level,text:e.textContent,top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom})),height:innerHeight})')
  check(all(('Υποχρεωτικό' if item['level'] in ['1','2'] else 'Προαιρετικό') in item['text'] for item in proof['levels']),'gate11 actual required1/2 optional3 labels '+str(width),proof)
  check(all(item['top']>=0 and item['bottom']<=height for item in proof['levels']),'gate11 three labelled levels actually within viewport '+str(width),proof)
  shot('gate11-visible-level-badges-'+str(width));OUT.setdefault('visibleLevelPanels',[]).append({'width':width,**proof})
 viewport(1500,1000)

def bank_layout_capture(game):
 viewport(390,844);game_ready(game,True)
 selector='#answer-zone' if game=='builder' else '#assembly-board'
 ev(window_expr(game,True)+'.document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"start",behavior:"instant"});true');pause(.3)
 proof=game_read(game,'(()=>{const a=document.querySelector('+json.dumps(selector)+').getBoundingClientRect(),b=document.querySelector('+json.dumps('#bank-zone' if game=='builder' else '#piece-bank')+').getBoundingClientRect();return{drop:a.toJSON(),bank:b.toJSON(),gap:b.top-a.bottom}})()',True)
 check(proof['gap']>=0 and proof['gap']<140,game+' narrow bank remains close below construction area',proof)
 shot('legacy-'+game+'-current-bank-droparea-390');OUT.setdefault('bankLayouts',[]).append({'game':game,**proof});viewport(1500,1000)

def legacy_migration():
 global INDEX
 OUT['legacyPartialMigrations']=[]
 for game in ['detective','builder','puzzle','repair']:
  fresh_tab();lesson(3,'__cache__/old/mulermoc-nom-57.html');open_gate();choose(game)
  SOLVERS[game]('old4 '+game+' genuine partial',True,True);pause(.3)
  old_gate=gate_state();before=old_gate['games'][game]
  check(old_gate['version']==1 and not old_gate['solved'],'actual old4 '+game+' partial remains locked')
  lesson(3);open_gate();game_ready(game,True)
  migrated=active_attempt(game,'legacy');after=migrated['progress']
  a,removed=comparable_progress(before,game);b,_=comparable_progress(after,game)
  check(a==b and migrated['context']['source']=='legacy' and migrated['context']['level'] is None and migrated['context']['seed']==before['seed'],'old4 '+game+' exact raw partial becomes explicit legacy8 wrapper',{'ignoredUntouchedFutureChoiceOrders':removed})
  check(not gate_state()['solved'],'migrated '+game+' partial does not unlock')
  current=after;context=migrated['context']
  lesson(3,'__cache__/old/mulermoc-nom-57.html');open_gate();game_ready(game,True)
  if game=='detective':frame_click(game,'#clear-selection')
  elif game=='builder':frame_click(game,'#bank-tiles button')
  elif game=='puzzle':frame_click(game,'[data-hydrogens="4"]')
  else:
   rnd=repair_oracle(True);selected=gate_state()['games'][game]['states'][gate_state()['games'][game]['currentRound']]['selectedPartId'];part=next(p for p in rnd['parts'] if p['id']!=selected);click('[id$="part-'+part['id']+'"]')
  pause(.3);check(gate_state()['games'][game]!=before,'actual later old4 '+game+' key changed through UI')
  lesson(3);open_gate();game_ready(game,True)
  actual=active_attempt(game,'legacy');a,_=comparable_progress(current,game);b,_=comparable_progress(actual['progress'],game)
  check(a==b and actual['context']==context,'present v2 '+game+' progress wins over later old-key mutation')
  OUT['legacyPartialMigrations'].append({'game':game,'before':before,'after':after,'context':context,'ignoredUntouchedFutureChoiceOrders':removed});shot('legacy-'+game+'-partial-current-wins')
  if game in ['builder','puzzle']:bank_layout_capture(game)
 fresh_tab();lesson(3,'__cache__/old/mulermoc-nom-57.html');open_gate();choose('repair')
 ids=[]
 for index in range(3):
  if index:next_round('repair',True)
  ids.append(solve_repair('actual old4 Repair earned '+str(index+1),True))
 check(len(set(ids))==3 and gate_state()['solved'],'actual old4 Repair genuine distinct earned triple')
 old=gate_state();lesson(3);open_gate();game_ready('repair',True);new=gate_state()
 check(new['solved'] and new['legacyEarned']['game']=='repair' and new['legacyEarned']['attempt']['context']['source']=='legacy' and not new['receipts'],'old4 Repair earned receipt grandfathered separately from new level receipts')
 a,_=comparable_progress(old['earned']['evidence'],'repair');b,_=comparable_progress(new['legacyEarned']['attempt']['progress'],'repair');check(a==b,'grandfathered Repair earned raw evidence remains exact')
 activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');INDEX=4
 check(True,'actual grandfathered Repair Continue reaches step5');OUT['legacyRepairEarned']={'ids':ids,'before':old,'after':new}
 visible_level_panel();author_contract()
