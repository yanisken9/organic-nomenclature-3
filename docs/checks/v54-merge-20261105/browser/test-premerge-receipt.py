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
 call('browsingContext.navigate',{'context':ctx,'url':'http://127.0.0.1:8055/'+LESSON+'#step=4','wait':'complete'});ready_lesson();open_generated()
 data=round_data();check(data['correctName']==ORACLE[data['moleculeId']],'Pre-merge round agrees with oracle');candidate(data);activate(submit());until('!!document.querySelector(".feedback.is-success")');activate('.round-next button');until('testCurrentRound.id!=='+json.dumps(data['id']))
 next_data=round_data();candidate(next_data)
 saved=json.loads(ev("JSON.stringify(Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith('namelecule:lesson-checkpoints:v1:'))))"))
 check(bool(saved),'Pre-merge saved receipt exists')
 preload=call('script.addPreloadScript',{'functionDeclaration':'()=>{const saved='+json.dumps(saved)+';for(const [k,v]of Object.entries(saved))sessionStorage.setItem(k,v)}','contexts':[ctx]})['script']
 navigate(LESSON+'#step=4');ready_lesson();call('script.removePreloadScript',{'script':preload});preload=None;open_generated()
 check(round_data()==next_data,'Old receipt regenerates same second question on merged main')
 check(ev('document.querySelector(".candidate-name").textContent')==next_data['correctName'],'Unsubmitted old answer is restored')
 state_now=storage();gate=next(iter(state_now.values()))['states']['3']
 check(gate['currentRound']==1 and gate['states'][0]['solved'],'Earlier solved repair survives actual engine update')
 check(ev('document.querySelector("#scNext").disabled'),'Restored partial set remains correctly locked')
 check(ev('performance.getEntriesByType("resource").some(r=>r.name.includes("/chemistry-engines/3f9382b4"))'),'Merged lesson actually fetched immutable checked engine')
 activate(submit());until('!!document.querySelector(".feedback.is-success")');activate('.round-next button');until('testCurrentRound.id!=='+json.dumps(next_data['id']))
 third=round_data();candidate(third);activate(submit());until('!!document.querySelector(".feedback.is-success")');activate('.round-next button');until('fScenarioPresent().index===4')
 check(True,'Old saved partial set completes and unlocks Part B')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 if preload:
  try:call('script.removePreloadScript',{'script':preload})
  except Exception:pass
 out['javascriptErrors']=js_errors
 Path('docs/checks/v54-merge-20261105/browser/premerge-receipt-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
