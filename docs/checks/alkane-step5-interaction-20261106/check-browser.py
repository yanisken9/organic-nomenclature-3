from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/alkane-step5-interaction-20261106')
os.environ['NAMELECULE_BIDI_PORT']=str(json.loads((HERE/'test-process.json').read_text())['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[],'chain_states':[]}
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS',name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")')
def snapshot():
 return ev('JSON.stringify({mode:nameAnalysisMode,chain:mainChainAtomsList,selected:[...document.querySelectorAll(".nameCompBox.selected")].map(e=>e.id),explain:document.getElementById("nameAnalysisExplain").textContent,ruleHidden:getComputedStyle(document.getElementById("ruleTheoryContainer")).display==="none",numbers:[...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(n=>[n.id,n.textContent,n.getAttribute("x"),n.getAttribute("y")])})')
def number_ready():until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===5')
def chain_state():
 number_ready()
 return json.loads(ev('JSON.stringify({mode:mode2D,chain:mainChainAtomsList.slice(),highAtoms:highAtoms.slice(),name:currentMolName,analysis:nameAnalysisMode,label:document.getElementById("chainStepLabel").textContent,number0:[document.getElementById("number0").getAttribute("x"),document.getElementById("number0").getAttribute("y")],disabled:["comp6","comp9"].every(id=>document.getElementById(id).classList.contains("scNameCompDisabled"))})'))
def solve_gate():
 ev('window.testMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(h,o){window.testRound=JSON.parse(JSON.stringify(o.round));return testMount(h,o)};true')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testRound')
 for ri in range(3):
  d=json.loads(ev('JSON.stringify(testRound)'))
  if d['kind']=='replace':
   click('[id$="-part-'+d['targetPartId']+'"]');idx=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue']);click('[id$="-choice-'+str(idx)+'"]')
  else:click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]')
  click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector("#scNext").disabled')==(ri<2),'Existing gate requires three repairs '+str(ri+1))
  click('.round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testRound.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=alkane-step5-interaction-20261106-r1#step=5');ready()
 check(ev('fScenarioPresent().index===3'),'Direct step5 URL still respects first Workshop gate')
 solve_gate();number_ready()
 check(ev('nameAnalysisMode==="compCarbonsCount"&&document.querySelector("#comp5").classList.contains("selected")'),'Parent stem remains preselected and active')
 check(ev('document.querySelector("#comp6").textContent.trim()==="άν"&&document.querySelector("#comp9").textContent.trim()==="ιο"'),'Passive syllables retain their exact text')
 check(ev('["comp6","comp9"].every(id=>{let e=document.getElementById(id);return e.classList.contains("scNameCompDisabled")&&e.getAttribute("aria-disabled")==="true"&&getComputedStyle(e).pointerEvents==="none"&&!e.hasAttribute("inert")})'),'Passive boxes are noninteractive but remain readable')
 check(ev('["comp0","comp1"].every(id=>document.getElementById(id).classList.contains("comp-hidden"))'),'Locant and branch boxes remain hidden')
 for id in ['comp6','comp9']:
  before=snapshot();click('#'+id);check(snapshot()==before,'DOM click on '+id+' changes no analysis or drawing')
  ev('$("#'+id+'").trigger("click");true');check(snapshot()==before,'Synthetic click on '+id+' is also inert')
  ev('document.getElementById("'+id+'").dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",bubbles:true}));document.getElementById("'+id+'").dispatchEvent(new KeyboardEvent("keydown",{key:" ",bubbles:true}));true');check(snapshot()==before,'Enter/Space do not activate '+id)
  ev('document.getElementById("'+id+'").scrollIntoView({block:"nearest"});true')
  pos=json.loads(ev('JSON.stringify((()=>{let r=document.getElementById("'+id+'").getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})())'))
  call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':pos['x'],'y':pos['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
  check(ev('!document.querySelector("#'+id+':hover")') and snapshot()==before,'Actual pointer hover/click on '+id+' has no effect')
 check(ev('document.querySelectorAll("#chainStepperBox").length===1&&document.getElementById("chainStepperBox").parentNode.id==="scChainNavigation"'),'One existing chain stepper is exposed outside hidden settings')
 check(ev('!document.getElementById("nameSettingsPanel").classList.contains("open")&&getComputedStyle(document.getElementById("nameSettingsBtnDiv")).display==="none"'),'Other naming controls stay hidden')
 check(ev('document.getElementById("chainNextBtn").getAttribute("aria-label").length>0&&document.getElementById("scChainNavigation").getAttribute("role")==="group"'),'Chain selector has accessible native controls')
 expected={'condensed':[[1,2,3,4,6],[5,2,3,4,6]],'expanded':[[1,2,3,4,6],[5,2,3,4,6]],'skeletal':[[1,2,4,5,6],[3,2,4,5,6]]}
 for mi,mode in enumerate(['condensed','expanded','skeletal']):
  if mi:ev('document.querySelectorAll("#radio2DMode .radioCheckContainer")['+str(mi)+'].click();true');until('mode2D==='+json.dumps(mode))
  if ev('mainChainPoolIdx>0'):click('#chainPrevBtn')
  first=chain_state();click('#chainNextBtn');second=chain_state();click('#chainPrevBtn');again=chain_state()
  out['chain_states'].append({'mode':mode,'first':first,'second':second,'again':again})
  check([first['chain'],second['chain']]==expected[mode] and again['chain']==first['chain'],'Both chemically verified paths and return in '+mode)
  check(all(s['name']=='2-μεθυλοπεντάνιο' and s['analysis']=='compCarbonsCount' and len(s['highAtoms'])==5 and s['disabled'] for s in [first,second,again]),'Name, five-atom scope and restrictions persist in '+mode)
  check(first['number0']!=second['number0'] and first['number0']==again['number0'],'Displayed first locant follows selected terminal atom in '+mode)
  check(ev('getComputedStyle(document.getElementById("ruleTheoryContainer")).display==="none"'),'Chain swaps preserve authored hidden rule in '+mode)
  check(ev('document.getElementById("chainPrevBtn").disabled&&!document.getElementById("chainNextBtn").disabled'),'Chain endpoint buttons track selection in '+mode)
  screenshot(HERE/('chain-'+mode+'.png'))
 ev('document.querySelectorAll("#radio2DMode .radioCheckContainer")[0].click();true');until('mode2D==="condensed"');number_ready()
 for width,height in [(390,844),(320,844),(1280,900)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});ev('new Promise(r=>setTimeout(r,200))')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  ev('document.getElementById("scChainNavigation").scrollIntoView({block:"nearest"});true')
  check(ev('(()=>{let r=document.getElementById("scChainNavigation").getBoundingClientRect();return r.width>0&&r.left>=0&&r.right<=innerWidth&&document.querySelectorAll("#chainStepperBox").length===1})()'),'Chain selector fits and is unique at '+str(width))
  check(ev('["comp6","comp9"].every(id=>document.getElementById(id).classList.contains("scNameCompDisabled"))'),'Resize retains passive syllables at '+str(width))
  screenshot(HERE/('responsive-'+str(width)+'.png'))
 click('#comp5');check(ev('nameAnalysisMode==="none"'),'Parent stem still toggles normally')
 click('#comp5');number_ready();check(ev('nameAnalysisMode==="compCarbonsCount"'),'Parent stem reselects normally')
 check(ev('getComputedStyle(document.getElementById("ruleTheoryContainer")).display==="none"'),'Parent click preserves the authored rule permission')
 ev('fScenarioGo(5);true');until('fScenarioPresent().index===5')
 check(ev('!document.querySelector("#scChainNavigation")&&!["comp6","comp9"].some(id=>document.getElementById(id).classList.contains("scNameCompDisabled"))'),'Step6 restores normal components and removes standalone chain selector')
 click('#comp6');check(ev('nameAnalysisMode==="compBondType"'),'Step6 syllable interaction remains active')
 ev('fScenarioGo(4);true');until('fScenarioPresent().index===4');number_ready()
 check(ev('nameAnalysisMode==="compCarbonsCount"&&["comp6","comp9"].every(id=>fScenarioNameCompDisabled(id))&&!!document.querySelector("#scChainNavigation")'),'Return6→5 restores the exact per-step permissions')
 ev('fScenarioGo(3);true');until('fScenarioPresent().index===3')
 check(ev('!document.querySelector("#scChainNavigation")&&!document.getElementById("viewerCol").getClientRects().length'),'Step4 remains Workshop-only')
 ev('fScenarioGo(4);true');until('fScenarioPresent().index===4');number_ready()
 ev('window.saveBlob=fScenarioSaveBlob;window.exportedBlob=null;fScenarioSaveBlob=(n,b)=>(exportedBlob=b,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=saveBlob;true')
 exported=json.loads(ev('exportedBlob.text()'));source=json.loads(Path('scenarios/alkanes-user-3.scenario.json').read_text())
 check(exported['steps']==source['steps'],'Presentation export preserves all authored steps exactly')
 ev('fScenarioExitPresent();true')
 check(ev('!document.querySelector("#scChainNavigation")&&!["comp6","comp9"].some(id=>document.getElementById(id).hasAttribute("aria-disabled"))'),'Exit removes presentation-only restrictions and standalone controls')
 click('#comp6');check(ev('nameAnalysisMode==="compBondType"'),'Ordinary explorer interaction is restored after Exit')
 ev('fScenarioSetAuthoring(true);fScenarioGo(4);fScenarioUpdateStep(fScenarioActive().id,4);true')
 check(ev('JSON.stringify(fScenarioActive().steps[4].styleName.disabled)==="[\\"comp6\\",\\"comp9\\"]"&&fScenarioActive().steps[4].show.chainNavigation===true'),'Author Update preserves both optional authored permissions')
 ev('window.owner=fScenarioActive();fScenarioDuplicateStep(owner.id,4);true')
 check(ev('owner.steps.length===13&&JSON.stringify(owner.steps[5].styleName.disabled)===JSON.stringify(owner.steps[4].styleName.disabled)&&owner.steps[5].show.chainNavigation===true&&owner.steps[5].styleName.disabled!==owner.steps[4].styleName.disabled'),'Duplicate preserves independent restriction list and chain opt-in')
 ev('owner.steps.splice(5,1);owner.steps.forEach((s,i)=>s.n=i+1);window.beforeCount=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File(['+json.dumps(json.dumps(exported,ensure_ascii=False))+'],"roundtrip.json",{type:"application/json"}));true')
 until('MuLERMoCScenario.scenarios.length===beforeCount+1')
 check(ev('fScenarioActive().steps[4].show.chainNavigation===true&&fScenarioActive().steps[4].styleName.disabled.join(",")==="comp6,comp9"'),'FileReader import retains both optional fields')
 normalized=ev('JSON.stringify(fScenarioValidDisabledNameComps(["comp6","comp6","bad","comp9",5,{},"<b>"]))')
 check(normalized=='["comp6","comp9"]','Invalid/duplicate disabled IDs normalize without changing valid IDs')
 legacy=json.loads(Path('scenarios/alkanes-two-part-workshop.scenario.json').read_text())
 check(ev('(()=>{let r=fScenarioValidate('+json.dumps(legacy,ensure_ascii=False)+');return r.ok&&r.steps.every(s=>!Object.prototype.hasOwnProperty.call(s.styleName,"disabled")&&!Object.prototype.hasOwnProperty.call(s.show,"chainNavigation"))})()'),'Legacy scenario validation adds neither optional field')
 # Relevant default-rule cases remain available; the new chrome cap only hides
 # a reference when the presented step has not requested any effective rule.
 fixture=json.loads(json.dumps(source['steps'][4]));fixture['n']=1
 fixture['styleName'].pop('disabled');fixture['show'].pop('chainNavigation')
 for title,explicit,nav,analysis in [('Αλκάνια-Ονοματολογία και διακλαδώσεις',False,False,'compCarbonsCount'),('Explicit rule fixture',True,False,'compCarbonsCount'),('Αλκάνια-Ονοματολογία και διακλαδώσεις',False,False,'none'),('Legacy arbitrary title',False,False,'none'),('Αλκάνια-Ονοματολογία και διακλαδώσεις',False,True,'none')]:
  fixture['show']['rule']=explicit
  fixture['nameAnalysisMode']=analysis
  if nav:fixture['show']['chainNavigation']=True
  else:fixture['show'].pop('chainNavigation',None)
  ev('fScenarioExitPresent();window.ruleSc=fScenarioNew('+json.dumps(title,ensure_ascii=False)+',true);ruleSc.steps=['+json.dumps(fixture,ensure_ascii=False)+'];fScenarioPresentBegin(ruleSc.id,0);true');until('MuLERMoCScenario.present&&selectedMol==="methyl_2_pentane"')
  if analysis=='none':
   check(ev('getComputedStyle(document.getElementById("ruleTheoryContainer")).display==="none"'),'No unselected rule is forced open '+title+str(nav));click('#comp5')
  else:
   check(ev('getComputedStyle(document.getElementById("ruleTheoryContainer")).display!=="none"'),'Existing requested rule remains visible '+str(explicit));click('#comp5');click('#comp5')
  check(ev('getComputedStyle(document.getElementById("ruleTheoryContainer")).display!=="none"'),'Active parent click preserves requested or legacy rule '+title+str(nav))
 fixture['styleName']['disabled']=['comp6','comp9'];fixture['nameAnalysisMode']='compBondType';fixture['show']['rule']=False
 ev('fScenarioExitPresent();window.passiveSc=fScenarioNew("Disabled replay fixture",true);passiveSc.steps=['+json.dumps(fixture,ensure_ascii=False)+'];fScenarioPresentBegin(passiveSc.id,0);true');until('MuLERMoCScenario.present')
 check(ev('nameAnalysisMode==="none"&&!document.getElementById("comp6").classList.contains("selected")'),'Disabled stored component cannot replay or restore a selection')
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
