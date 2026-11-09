from pathlib import Path
import os,json,traceback
HERE=Path('docs/checks/workshop-entry-label-20261106');meta=json.loads((HERE/'test-process.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(meta['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[]};label='πήγαινε στο συνεργείο'
def check(ok,name):
 assert ok,name
 out['checks'].append(name);print('PASS',name,flush=True)
def click(selector):ev('document.querySelector('+json.dumps(selector)+').click();true')
def ready():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent()&&!document.documentElement.classList.contains("lesson-loading")&&!MuLERMoCScenario.checkpointPreparation')
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=workshop-entry-label-20261106-r1#step=4');ready()
 check(ev('document.querySelector("#nlQuizOpen").textContent')==label,'Exact authored entry label at step4')
 check(ev('document.querySelector("#scNext").disabled'),'Step4 remains locked before solving')
 until('!!document.querySelector("#pageTitle .scStepHeadingVisual.is-loaded")')
 check(ev('document.querySelector("#pageTitle img").naturalWidth>0'),'Workshop heading logo retained')
 ev('window.testSave=fScenarioSaveBlob;window.testExport=null;fScenarioSaveBlob=(n,b)=>(window.testExport=b,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=testSave;true')
 exported=json.loads(ev('testExport.text()'))
 check([exported['steps'][i]['checkpoint']['openLabel'] for i in [3,10]]==[label,label],'Export preserves both authored labels')
 (HERE/'exported.json').write_text(json.dumps(exported,ensure_ascii=False,indent=2)+'\n')
 for width,height in [(1280,900),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  ev('new Promise(r=>setTimeout(r,100));')
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  check(ev('(()=>{let b=document.querySelector("#nlQuizOpen").getBoundingClientRect();return b.width>0&&b.x>=0&&b.right<=innerWidth&&b.height>=44})()'),'Button fits viewport '+str(width))
  screenshot(HERE/('button-'+str(width)+'.png'))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':900},'devicePixelRatio':1})
 ev('window.testMount=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(h,o){window.testRound=JSON.parse(JSON.stringify(o.round));return testMount(h,o)};true')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testRound')
 check(ev('fScenarioPresent().index===3'),'Custom step4 button opens real quiz in place')
 for ri in range(3):
  d=json.loads(ev('JSON.stringify(testRound)'))
  if d['kind']=='replace':
   click('[id$="-part-'+d['targetPartId']+'"]');idx=next(i for i,c in enumerate(d['choices']) if c['value']==d['correctValue']);click('[id$="-choice-'+str(idx)+'"]')
  else:click('[id$="-part-'+d['correctOrder'][0]+'"]');click('[id$="-move-left"]')
  click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
  check(ev('document.querySelector("#scNext").disabled')==(ri<2),'Required completion unchanged round'+str(ri+1))
  if ri==2:check(ev('document.querySelector("#nlQuizOpen").textContent')=='Δες ξανά την επισκευή','Completed checkpoint preserves revisit label')
  click('.round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testRound.id!=='+json.dumps(d['id']))
  else:until('fScenarioPresent().index===4')
 ev('fScenarioGo(10);true');until('fScenarioPresent().index===10&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('document.querySelector("#nlQuizOpen").textContent')==label,'Exact authored entry label at step11')
 click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")')
 check(ev('document.querySelector("#scNext").disabled'),'Step11 button opens real quiz with gate locked')
 click('#nlQuizBack');check(ev('fScenarioPresent().index===10&&document.querySelector("#nlQuizOpen").textContent')==label,'Closing quiz retains custom entry label')
 for bad in ['', '  ', False, {}, 'x'*101]:
  cp=json.loads(json.dumps(exported['steps'][3]['checkpoint']));cp['openLabel']=bad
  check(ev('!Object.prototype.hasOwnProperty.call(NameleculeQuizCheckpoints.validateCheckpoint('+json.dumps(cp,ensure_ascii=False)+'),"openLabel")'),'Invalid optional label falls back '+repr(bad)[:30])
 cp=json.loads(json.dumps(exported['steps'][3]['checkpoint']));cp['openLabel']='  '+label+'  '
 check(ev('NameleculeQuizCheckpoints.validateCheckpoint('+json.dumps(cp,ensure_ascii=False)+').openLabel')==label,'Authored label trimmed safely')
 ev('window.testCount=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File(['+json.dumps(json.dumps(exported,ensure_ascii=False))+'],"roundtrip.json",{type:"application/json"}));true')
 until('MuLERMoCScenario.scenarios.length===testCount+1')
 check(ev('fScenarioActive().steps[3].checkpoint.openLabel===fScenarioActive().steps[10].checkpoint.openLabel&&fScenarioActive().steps[3].checkpoint.openLabel==='+json.dumps(label)),'FileReader reimport preserves both labels')
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1#step=4');ready()
 check(ev('document.querySelector("#nlQuizOpen").textContent')=='Στο Συνεργείο ονομάτων','Unmodified lesson retains existing localized default')
 check(ev('fScenarioPresent().steps.filter(s=>s.checkpoint).every(s=>!Object.prototype.hasOwnProperty.call(s.checkpoint,"openLabel"))'),'Legacy checkpoints gain no label property')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx});call('session.end',{})
 except Exception:pass
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
