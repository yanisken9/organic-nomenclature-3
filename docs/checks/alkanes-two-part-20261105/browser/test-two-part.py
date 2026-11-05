"""Developer actual Firefox: complete generated lesson, restoration and gallery.
Only isolated owned tab. All canonical rounds come from actual chemistry Workers.
"""
from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/alkanes-two-part-20261105/browser/support.py').read_text(),'support','exec'))
LESSON='mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1'
ORACLE={'methane':'μεθάνιο','ethane':'αιθάνιο','propane':'προπάνιο','butane':'βουτάνιο','pentane':'πεντάνιο','methyl_2_pentane':'2-μεθυλοπεντάνιο','dimethyl_2_3_butane':'2,3-διμεθυλοβουτάνιο','ethyl_3_dimethyl_2_5_hexane':'3-αιθυλο-2,5-διμεθυλοεξάνιο'}
observed=[];preload=None

def ready_lesson():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===12');until('!document.documentElement.classList.contains("lesson-loading")&&!MuLERMoCScenario.checkpointPreparation');call('browsingContext.activate',{'context':ctx})

def refresh():
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready_lesson()

def install_capture():
 ev('''if(!window.testMountOriginal){window.testMountOriginal=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.testCurrentRound=JSON.parse(JSON.stringify(options.round));return testMountOriginal(host,options)}};true''')

def open_generated():
 install_capture();click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")');until('!!window.testCurrentRound')

def round_data():return json.loads(ev('JSON.stringify(testCurrentRound)'))
def storage():return json.loads(ev("JSON.stringify(Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith('namelecule:lesson-checkpoints:v1:')).map(([k,v])=>[k,JSON.parse(v)])))"))

def candidate(data):
 if data['kind']=='replace':
  activate(part(data['targetPartId']))
  good=next(i for i,c in enumerate(data['choices']) if c['value']==data['correctValue']);activate(choice(good))
 else:
  activate(part(data['correctOrder'][0]));activate('[id$="-move-left"]')
 check(ev('document.querySelector(".candidate-name").textContent')==data['correctName'],'Canonical candidate '+data['moleculeId'])

def solve_set(gate):
 open_generated();ids=[]
 for ri in range(3):
  data=round_data();ids.append(data['moleculeId']);observed.append({'gate':gate+1,'quiz':ri+1,'round':data})
  check(data['correctName']==ORACLE[data['moleculeId']],'Engine name agrees with independent oracle')
  check(index()==gate and ev('document.querySelector("#scNext").disabled'),'Unsolved set keeps theory locked, round '+str(ri+1))
  if ri==0:
   key('\ue014');key('\ue012');check(index()==gate,'Quiz keys do not navigate lesson')
   if data['kind']=='replace':
    activate(part(data['targetPartId']));bad=next(i for i,c in enumerate(data['choices']) if c['value']!=data['correctValue']);activate(choice(bad));activate(submit())
    check(not ev('!!document.querySelector(".feedback.is-success")') and ev('document.querySelector("#scNext").disabled'),'Wrong repair does not unlock')
    activate('.repair-actions .quiet')
  candidate(data)
  if ri==0:
   check(ev('document.querySelector("#scNext").disabled') and not ev('!!document.querySelector(".feedback.is-success")'),'Unsubmitted correct selection remains locked')
   frozen=storage();click('#nlQuizBack');refresh();open_generated()
   check(round_data()==data,'Refresh regenerates the exact canonical question',{'before':data,'after':round_data()});after=storage();before_gate=next(iter(frozen.values()))['states'][str(gate)];after_gate=next(iter(after.values()))['states'][str(gate)];check(before_gate['seed']==after_gate['seed'] and before_gate['currentRound']==after_gate['currentRound'] and before_gate['states'][ri]==after_gate['states'][ri],'Refresh preserves seed and active legal answer state',{'before':before_gate,'after':after_gate})
   check(ev('document.querySelector(".candidate-name").textContent')==data['correctName'],'Unsubmitted candidate restored')
   screenshot_here('gate-'+str(gate+1)+'-candidate.png')
  before=state();activate(submit());until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector(".success-explanation").textContent')==data['successText'],'Specific success explanation from canonical round')
  check(state()==before and index()==gate,'Answer does not reset live viewer or advance theory')
  check(ev('document.querySelector("#scNext").disabled')==(ri<2),'Only three solved rounds unlock gate')
  label='Επόμενο κουίζ' if ri<2 else 'Συνεχίζω τη θεωρία'
  check(ev('document.querySelector(".round-next button").textContent')==label,'Correct internal/theory continuation label')
  if ri==1:
   frozen=storage();click('#nlQuizBack');open_generated();check(round_data()==data and ev('!!document.querySelector(".feedback.is-success")'),'Close/reopen preserves second solved round and explanation')
  activate('.round-next button')
  if ri<2:
   until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")');until('testCurrentRound.id!=='+json.dumps(data['id']))
  else:until('fScenarioPresent().index==='+str(gate+1))
 check(len(set(ids))==3,'Three distinct molecules per set')
 check(not ev('!!document.querySelector("#nlQuizDialog[open]")'),'Set completion returns to theory')

try:
 navigate(LESSON+'#step=12');ready_lesson()
 check(index()==3 and ev('location.hash')=='#step=4','Cold final deep link stops at first required set')
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)===false'),'No initial completion receipt')
 ev('fScenarioGo(0);true');until('fScenarioPresent().index===0')
 for i in range(3):
  check(index()==i,'Part A teaching step '+str(i+1));click('#scNext');until('fScenarioPresent().index==='+str(i+1))
 click('#zoomInBtn');initial=state();ev('window.testApplyCount=0;window.testApplyOriginal=fScenarioApply;fScenarioApply=function(){window.testApplyCount++;return testApplyOriginal.apply(this,arguments)};true')
 for command in ['fScenarioGo(11)','location.hash="step=12"']:
  ev(command+';true');until('location.hash==="#step=4"');check(index()==3 and state()==initial,'Blocked direct/hash navigation preserves viewer')
 check(ev('testApplyCount===0'),'Blocked jump never reapplies molecular snapshot')
 solve_set(3)
 check(index()==4,'Part B opens after first set');refresh();check(index()==4 and ev('location.hash')=='#step=5','Completed first set revalidated after refresh without losing target')
 # A genuinely unavailable Worker during receipt reconstruction must fail closed
 # with retry/Exit, then recover in the same page after removing the injected fault.
 preload=call('script.addPreloadScript',{'functionDeclaration':'()=>{window.testRealWorker=window.Worker;window.Worker=new Proxy(Worker,{construct(target,args){if(String(args[0]).includes("namelecule-chemistry-worker.js"))throw new Error("owned deliberate chemistry Worker unavailable");return Reflect.construct(target,args)}})}','contexts':[ctx]})['script']
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});app_ready();until('!!document.querySelector("#scCheckpointPreparation.is-error")')
 check(ev('document.querySelector("#scNext").disabled') and ev('location.hash')=='#step=5','Unavailable Worker retains requested target and locks continuation')
 screenshot_here('receipt-error-retry.png')
 ev('window.Worker=window.testRealWorker;true');call('script.removePreloadScript',{'script':preload});preload=None
 click('#scCheckpointPreparation button');until('!MuLERMoCScenario.checkpointPreparation&&fScenarioPresent().index===4');check(True,'Visible Retry recovers actual Worker reconstruction without reload')
 for i in range(4,10):
  check(index()==i,'Part B teaching step '+str(i+1))
  if i in (5,8,9):
   check(ev('fScenarioShowComponentRule(nameAnalysisMode)'),'Existing optional component rule available')
  click('#scNext');until('fScenarioPresent().index==='+str(i+1))
 check(index()==10 and ev('document.querySelector("#scNext").disabled'),'Second required set stops final gallery')
 solve_set(10);check(index()==11,'Final gallery unlocked after both sets')
 refresh();check(index()==11 and ev('location.hash')=='#step=12','Both saved sets revalidated and final destination restored')
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Both canonical set receipts complete')
 check(json.loads(ev('JSON.stringify(fScenarioPresent().steps[11].menuSubset)'))==list(ORACLE),'Final menu includes all eight alkanes')
 # Actual interactive menu/2D/3D paths; current model must be the selected file.
 gallery=[]
 for mol,name in ORACLE.items():
  click('.menuLi#'+mol);until('selectedMol==='+json.dumps(mol));until('currentMolName==='+json.dumps(name))
  sdf=ev('nameExamples[selectedMol].file3D');expected=int(Path(sdf).read_text().splitlines()[3][:3])
  until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(expected),seconds=30)
  until("(()=>{const m=fJSmolGetPropertyAsArray(jmolAppletNomeclature,'modelInfo');return m&&m.models&&m.models.length===1&&m.models[0].file.endsWith("+json.dumps('/'+sdf)+")})()",seconds=30)
  model=json.loads(ev("JSON.stringify(fJSmolGetPropertyAsArray(jmolAppletNomeclature,'modelInfo'))"))
  check(ev('fJSmolLive()&&!!document.querySelector("#nomeclature3D canvas")') and len(model['models'])==1 and model['models'][0]['file'].endswith('/'+sdf),'Actual3D model matches '+mol)
  for ri,mode in enumerate(['condensed','expanded','skeletal']):
   if mol=='methane' and mode=='skeletal':
    check(ev('document.querySelectorAll("#radio2DMode .mode2DOption")[2].classList.contains("disabledRadio")'),'Methane skeletal unavailable explicitly');continue
   click('#radio2DMode .mode2DOption:nth-of-type('+str(ri+1)+')');until('mode2D==='+json.dumps(mode))
   check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG").getAttribute("data-label-error")'),'Actual2D '+mol+' '+mode)
   gallery.append({'molecule':mol,'mode':mode,'name':ev('currentMolName'),'3DAtoms':expected})
  # Name interaction remains live in the final lesson, including numbering.
  click('#comp5');check(ev('nameAnalysisMode==="compCarbonsCount"'),'Gallery name click '+mol)
 screenshot_here('final-gallery-desktop.png')
 click('#zoomInBtn');check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Gallery zoom remains usable')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':844,'height':390},'devicePixelRatio':1});check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Gallery landscape resize retains drawing')
 screenshot_here('final-gallery-landscape.png')
 out['gallery']=gallery;out['observedRounds']=observed;out['finalStorage']=storage()
 out['completed']=True
except Exception as exc:
 out['failure']=str(exc);out['traceback']=traceback.format_exc()
 try:screenshot_here('two-part-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['consoleErrors']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')=='error']
 (HERE/'two-part-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 if preload:
  try:call('script.removePreloadScript',{'script':preload})
  except Exception:pass
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
