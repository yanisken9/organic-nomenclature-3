# Runs only after the direct-source checks, same frozen eight-source guard.
viewport(1280,800);navigate('design/theory-library.html?v=workshop-parity-regression');click('article[aria-labelledby=alkanes-title] a.action');ready();check(ev('location.pathname.endsWith("mulermoc-nom-55.html")&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Normal library entry Main55 learner mode')
for i in (1,2,3):click('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
ev('fScenarioGo(11);true');check(ev('fScenarioPresent().index===3&&document.getElementById("scNext").disabled'),'Main55 first gate rejects skip')
for step,setid,seedvalue in [(3,'alkanes-unbranched','4'),(10,'alkanes-branched','1')]:
 if step==10:
  for i in (5,6,7,8,9,10):click('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
  ev('fScenarioGo(11);true');check(ev('fScenarioPresent().index===10&&document.getElementById("scNext").disabled'),'Main55 second gate rejects skip');viewport(390,760)
 seed_lesson(step,seedvalue);open_lesson()
 for ri,f in enumerate(GAMES[seedvalue][setid]['rounds']):
  label='main55-s'+str(step+1)+'r'+str(ri+1)
  if ri==0:shown(label+'-entry',1280 if step==3 else 390)
  if f['moleculeId']=='ethyl_3_dimethyl_2_5_hexane':
   for w,h in [(1280,800),(390,760),(320,700)]:viewport(w,h);top();shown(label+'-entry',w)
   zoom(label,True);viewport(390,760)
  solve(f,label,ri,True,extensive=(step==3 and ri==0),tall=(step==10 and ri==2));check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),'+str(step)+')')==(ri==2)and ev('document.getElementById("scNext").disabled')==(ri<2),label+' required gate unlock only after third earned repair');next_round(label,ri,True,step)
check(ev('fScenarioPresent().index===11&&!document.getElementById("nlQuizDialog").open&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Main55 actual six repairs reach step12')
click('#scPrev');wait('fScenarioPresent().index===10');check(not ev('document.getElementById("scNext").disabled'),'Main55 completed gate replay stays unlocked');click('#scNext');wait('fScenarioPresent().index===11');click('#scExit');wait('location.pathname.endsWith("/design/theory-library.html")');check(True,'Main55 Exit returns library')
# Main54 same source compatibility is bounded: one actual generated round, not full gate replay.
viewport(1280,800);navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');ready()
for i in (1,2,3):click('#scNext');wait('fScenarioPresent().index==='+str(i)+'&&!MuLERMoCScenario.checkpointPreparation')
seed_lesson(3,'4');open_lesson();f=GAMES['4']['alkanes-unbranched']['rounds'][0];solve(f,'main54-s4r1',0,True);check(ev('document.getElementById("scNext").disabled&&!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Main54 same-source earned first round leaves required gate locked');click('#nlQuizBack');check(not ev('document.getElementById("nlQuizDialog").open'),'Main54 close returns to lesson')
OUT['embeddedCompleted']=True
