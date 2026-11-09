from pathlib import Path
import os,json,copy,traceback
HERE=Path('docs/checks/alkane-step7-numbering-20261108')
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
 app_ready();until('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
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

import hashlib
out={'completed':False,'checks':[],'limitations':['Owned headless Firefox; no personal browser interaction or freeze diagnosis','Viewport emulation, not physical mobile/Safari/screen reader or conference sequence','No full 3D audit; direction support requires2D-only step','Export actual Blob captured and validated; no browser download picker; actual Desktop export verified separately']}
def labels():return json.loads(ev('JSON.stringify([...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].map(e=>({text:e.textContent,x:Number(e.getAttribute("x")),y:Number(e.getAttribute("y"))})).sort((a,b)=>a.x-b.x))'))
def sequence():return [int(n['text']) for n in labels()]
def wait_numbers(expected):until('JSON.stringify([...document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]")].sort((a,b)=>Number(a.getAttribute("x"))-Number(b.getAttribute("x"))).map(e=>Number(e.textContent)))==='+json.dumps(json.dumps(expected,separators=(',',':'))),seconds=12)
def invariant():return ev('JSON.stringify({mol:selectedMol,chain:mainChainAtomsList,index:mainChainPoolIdx,pool:mainChainPool.map(p=>p.chain),name:currentMolName,types:allAtomsTypeList,bonds:bondList,geometry:jsmeNomeclatureApplet.molFile().split("\\n").slice(3).join("\\n")})')
def buttons_fit(width):
 ev('document.getElementById("scNumberingRight").scrollIntoView({block:"center"});true')
 data=json.loads(ev('JSON.stringify(["scNumberingLeft","scNumberingRight"].map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();return{id,left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height,hit:e.contains(document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2)),pressed:e.getAttribute("aria-pressed"),border:getComputedStyle(e).borderTopWidth}}))'))
 out.setdefault('buttonBounds',[]).append({'width':width,'buttons':data})
 a,b=data;separate=max(a['left'],b['left'])>=min(a['right'],b['right']) or max(a['top'],b['top'])>=min(a['bottom'],b['bottom'])
 return separate and all(d['hit'] and d['left']>=0 and d['right']<=width and d['width']>=44 and d['height']>=44 and d['border']!='0px' for d in data)
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&v=step7-author-check');ready();ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();true');click('.scenarioPanel.active .srow[data-idx="6"] .scPresentStep');until('MuLERMoCScenario.present&&!!document.getElementById("scNumberingRight")');click('#scNumberingRight')
 check(ev('NameleculeQuizCheckpoints.isPreview(fScenarioPresent())&&fScenarioPresent().index===6'),'Author screen opens step7 directly with direction control')
 check(ev('new Promise(resolve=>setTimeout(()=>resolve(MuLERMoCScenario.numberingDirection.direction==="right"&&nameAnalysisMode==="compCarbonsCount"&&document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===4),2300))'),'Delayed initial highlight does not override a direction choice')
 ev('fScenarioUpdateStep(fScenarioPresent().id,6);true');check(ev('fScenarioPresent().steps[6].show.numberingDirection===true&&fScenarioPresent().steps[6].show.viewers["2D"]===true&&fScenarioPresent().steps[6].show.viewers["3D"]===false'),'Actual Update preserves optional flag and authored2D-only viewerpermissions')
 ev('window.testSaveBlob=fScenarioSaveBlob;fScenarioSaveBlob=(name,blob)=>{window.testExportBlob=blob;return true};fScenarioExport(fScenarioPresent().id);fScenarioSaveBlob=testSaveBlob;true')
 exported=json.loads(ev('testExportBlob.text()'));(HERE/'browser-export.json').write_text(json.dumps(exported,ensure_ascii=False,indent=2)+'\n')
 check(exported['steps'][6]['show']['numberingDirection'] is True and 'numberingDirection' not in exported['steps'][6] and 'direction' not in exported['steps'][6],'Actual export retains opt-in and omits transient selected direction')
 check(ev('fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+').ok'),'Actual exported Blob roundtrip validates')
 ev('fScenarioExitPresent();true');check(ev('!MuLERMoCScenario.present&&MuLERMoCScenario.numberingDirection===null&&!document.getElementById("scNumberingDirection")'),'Stop/Exit clears transient direction and control')
 click('.scenarioPanel.active .srow[data-idx="6"] .scPresentStep');until('MuLERMoCScenario.present&&!!document.getElementById("scNumberingLeft")');wait_numbers([1,2,3,4]);check(True,'Author reentry also starts left with no persisted direction')
 ev('fScenarioExitPresent();fScenarioDuplicateStep(fScenarioActive().id,6);true');check(ev('fScenarioActive().steps[7].show.numberingDirection===true&&fScenarioActive().steps[7]!==fScenarioActive().steps[6]'),'Actual Duplicate preserves optional flag without aliasing original step')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
 try:screenshot(HERE/'author-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'browser-author.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
