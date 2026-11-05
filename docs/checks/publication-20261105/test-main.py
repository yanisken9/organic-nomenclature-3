"""Bounded Developer post-install checks on primary; only owned Firefox9247 context."""
from pathlib import Path
import os,json,time,traceback
os.environ['NAMELECULE_BIDI_PORT']='9247'
os.environ.setdefault('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8057/organic-nomenclature-3/')
exec(compile(Path('tools/namelecule_bidi.py').read_text().replace("{'type':'tab'}","{'type':'window'}"),'bidi','exec'))
HERE=Path('docs/checks/publication-20261105')
out={'completed':False,'checks':[],'scope':'Developer final primary entry-flow checks; isolated owned Firefox9247 only. No authoring/network fixtures or changes to user window.'}
OLD='3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306'
NEW='8f3e5f76d96322faf7cf9251f4cae3eca204fe2f82bf5754fdce6ffc4cd5d5a9'
LESSON='mulermoc-nom-54.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1'
def check(v,label):
    assert v,label
    out['checks'].append(label);print('PASS',len(out['checks']),label,flush=True)
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def click(sel):
    ev('document.querySelector('+json.dumps(sel)+').scrollIntoView({block:"center",behavior:"instant"});new Promise(r=>setTimeout(r,80))')
    b=read('(()=>{const n=document.querySelector('+json.dumps(sel)+'),b=n.getBoundingClientRect();return{x:b.x+b.width/2,y:b.y+b.height/2,hit:n.contains(document.elementFromPoint(b.x+b.width/2,b.y+b.height/2)),enabled:!n.disabled}})()')
    assert b['hit'] and b['enabled'],(sel,b)
    call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(b['x']),'y':round(b['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def ready():
    app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===12');until('!document.documentElement.classList.contains("lesson-loading")&&!MuLERMoCScenario.checkpointPreparation')
def open_quiz():
    ev('if(!window.testMountOriginal){window.testMountOriginal=NameleculeRepairGame.mountRound;NameleculeRepairGame.mountRound=function(host,options){window.testCurrentRound=JSON.parse(JSON.stringify(options.round));return testMountOriginal(host,options)}};true')
    click('#nlQuizOpen');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&!!window.testCurrentRound')
def round_data():return read('testCurrentRound')
def candidate(data):
    if data['kind']=='replace':
        click('[id$="-part-'+data['targetPartId']+'"]')
        good=next(i for i,c in enumerate(data['choices']) if c['value']==data['correctValue'])
        click('[id$="-choice-'+str(good)+'"]')
    else:
        click('[id$="-part-'+data['correctOrder'][0]+'"]');click('[id$="-move-left"]')
def storage():return read('Object.fromEntries(Object.entries(sessionStorage).filter(([k])=>k.startsWith("namelecule:lesson-checkpoints:v1:")).map(([k,v])=>[k,JSON.parse(v)]))')
try:
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        navigate('docs/professor-20261105/update.html')
        check(ev('document.documentElement.scrollWidth<=innerWidth&&document.body.textContent.includes("5 Νοεμβρίου 2026")'),'Professor report readable at '+str(width))
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
    navigate('design/welcome-proposal.html?v=release-20261105')
    check(ev('!!document.querySelector("a[href*=mulermoc-nom-54]")'),'Welcome still opens current Main54')
    navigate('mulermoc-nom-54.html?v=post-install-20261105');app_ready();call('browsingContext.activate',{'context':ctx})
    until('window.JSmolReadyFlag===true')
    check(ev('Object.keys(nameExamples).length===141&&!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Primary main141molecules and initial2D ready')
    until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))===5',seconds=35)
    check(True,'Primary real methane3D contains5atoms')
    digest=ev('(async()=>{const u=[...document.scripts].find(s=>s.src.includes("mulermoc-nom-core-54.js")).src;return [...new Uint8Array(await crypto.subtle.digest("SHA-256",await(await fetch(u,{cache:"reload"})).arrayBuffer()))].map(n=>n.toString(16).padStart(2,"0")).join("")})()')
    check(digest==NEW,'Primary browser fetched exact independently reviewed new core')
    check(ev('document.querySelector("#autoLinearizeCheck").classList.contains("selectedCheck")&&[...document.scripts].some(s=>s.src.includes("merge54-20261105-r1"))'),'Primary automatic layout default and new cache references')
    navigate(LESSON+'#step=12');ready()
    check(ev('fScenarioPresent().index===3&&location.hash==="#step=4"&&document.querySelector("#scNext").disabled'),'Direct final-step request stops at unsolved required gate')
    open_quiz()
    check(ev('performance.getEntriesByType("resource").some(r=>r.name.includes("/chemistry-engines/3f9382b4"))'),'Primary embedded quiz fetched immutable verified old engine')
    check(ev('NameleculeChemistryClient.verifyEngine('+json.dumps(OLD)+')')==OLD,'Primary old quiz engine passes actual WebCrypto')
    check(ev('NameleculeChemistryClient.verifyEngine('+json.dumps(NEW)+')')==NEW,'Primary new engine passes verified404fallback')
    data=round_data();candidate(data);click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")')
    check(ev('document.querySelector("#scNext").disabled&&document.querySelector(".success-explanation").textContent==='+json.dumps(data['successText'])),'First solved repair explains answer but keeps required set locked')
    click('.round-next button');until('testCurrentRound.id!=='+json.dumps(data['id']));second=round_data();candidate(second)
    before=storage();click('#nlQuizBack');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_quiz()
    out['refreshEvidence']={'roundBefore':second,'roundAfter':round_data(),'storageBefore':before,'storageAfter':storage(),'candidateAfter':ev('document.querySelector(".candidate-name").textContent')}
    after=storage();receipt_key=next(iter(before));b=before[receipt_key];a=after[receipt_key];gb=b['states']['3'];ga=a['states']['3']
    check(set(before)==set(after) and b['version']==a['version'] and b['content']==a['content'] and all(gb[k]==ga[k] for k in ['version','seed','currentRound','solved']) and gb['states'][:2]==ga['states'][:2] and round_data()==second and ev('document.querySelector(".candidate-name").textContent')==second['correctName'],'Primary refresh preserves exact active question, earlier solved repair and unsubmitted repair')
    xb=gb['states'][2];xa=ga['states'][2]
    check({k:v for k,v in xb.items() if k!='choiceOrder'}=={k:v for k,v in xa.items() if k!='choiceOrder'} and all(st['selectedPartId'] is None and st['selectedValue'] is None and st['attempts']==0 and st['selectionMisses']==0 and not st['solved'] and not st['submitted'] and sorted(st['choiceOrder'])==list(range(len(st['choiceOrder']))) for st in [xb,xa]) and sorted(xb['choiceOrder'])==sorted(xa['choiceOrder']),'Future never-opened state remains pristine with same valid choice indices')
    check(ev('document.querySelector("#scNext").disabled'),'Restored partial set still locks theory')
    for i in range(2):
        data=round_data()
        if i:candidate(data)
        click('[id$="-check-button"]');until('!!document.querySelector(".feedback.is-success")');click('.round-next button')
        if i==0:until('testCurrentRound.id!=='+json.dumps(data['id']))
    until('fScenarioPresent().index===4');check(True,'Three solved primary repairs return to PartB')
    call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
    check(ev('fScenarioPresent().index===4&&location.hash==="#step=5"'),'Primary completed gate survives refresh')
    navigate('games/name-repair.html?source=engine');until('!!document.querySelector("#set-alkanes-start")')
    click('#set-alkanes-start');until('!!document.querySelector("#pilot-difficulty")');click('#set-alkanes-unbranched-start');until('!!document.querySelector(".diagram-image.is-ready")')
    check(ev('document.querySelector("#check-button").textContent.trim()==="Έλεγχος"&&performance.getEntriesByType("resource").some(r=>r.name.includes("/chemistry-engines/3f9382b4"))'),'Standalone generated Workshop loads checked engine and plain Check label')
    out['completed']=True
except Exception as e:
    out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
    out['javascriptErrors']=js_errors
    out['baseURL']=os.environ['NAMELECULE_TEST_BASE_URL']
    out['consoleEntries']=[e.get('params',{}) for e in all_events if e.get('method')=='log.entryAdded']
    (HERE/('main-'+os.environ.get('NAMELECULE_EVIDENCE_SUFFIX','prefix')+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
