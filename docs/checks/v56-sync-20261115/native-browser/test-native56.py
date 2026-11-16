"""Real native v56 picking/replay smoke in an owned Firefox; no answer receipts."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned56-support','exec'))

def select(molecule, representation='condensed'):
    ev('selectedMol='+json.dumps(molecule)+';mode2D='+json.dumps(representation)+';fSelectMol();true')
    wait('selectedMol==='+json.dumps(molecule)+'&&mode2D==='+json.dumps(representation)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
    pause(350)

def click_atom(atom):
    point=read('(()=>{const geom=fMulerSelectGeom(),a=geom.anchors.find(a=>a.atom==='+str(atom-1)+')||geom.verts.find(a=>{const pick=fMulerSelectPick(a.x,a.y);return pick&&pick.kind==="atom"&&pick.atom==='+str(atom)+'});if(!a)throw Error("Missing atom anchor");const g=document.querySelector("#jsmeNomeclatureSVG svg g"),p=new DOMPoint(a.x,a.y).matrixTransform(g.getScreenCTM());return{x:p.x,y:p.y,hit:document.elementFromPoint(p.x,p.y)?.closest("#jsmeNomeclatureSVG")!==null}})()')
    check(point['hit'],'native atom coordinate lies on actual viewer',{'atom':atom,'point':point})
    pointer_at(point);pause(280)

def arm_root():
    if not ev('fMulerSelectActive()'):
        pointer('#selectAtomsBtn');pause(200)
        check(ev('fMulerSelectActive()'),'trusted selection entry actually arms native mode',read('window.__toggleTrace||[]'))
    pointer('#comp5');wait('window.MulerQuizTarget==="compCarbonsCount"')

try:
    navigate('mulermoc-nom-56.html?lang=en&mol=ethane&v=native56-'+str(time.time_ns()))
    app_ready();wait('typeof fMulerSelectAnchors==="function"&&!!document.querySelector("#selectAtomsBtn")&&!!document.querySelector("#jsmeNomeclatureSVG svg")',60)
    out['focusBeforeActivation']=ev('document.hasFocus()');call('browsingContext.activate',{'context':ctx});out['focusAfterActivation']=ev('document.hasFocus()')
    check(read('Object.keys(nameExamples).length')==141,'new56 retains all141 molecules')
    check(visible('#selectAtomsBtn'),'selection entry visible in normal exploration')
    ev('window.__toggleTrace=[];window.__nativeToggle=fToggleAtomSelect;fToggleAtomSelect=function(){__toggleTrace.push({phase:"before",active:fMulerSelectActive(),present:fMulerSelectPresenting(),draft:!!window.MulerDraft,stack:new Error().stack});const r=__nativeToggle.apply(this,arguments);__toggleTrace.push({phase:"after",active:fMulerSelectActive()});return r};true')
    arm_root();chain=read('fMulerMainChainResolved().slice()');check(len(chain)==2,'ethane native root mission has two C atoms')
    click_atom(chain[0]);check(ev('MulerUserSelection.atoms2D.length===1&&MulerQuizTarget==="compCarbonsCount"'),'partial native selection remains armed')
    check(visible('#mulerQuizVerdict'),'partial native selection shows teacher live hint')
    click_atom(chain[1]);check(ev('!window.MulerQuizTarget&&document.querySelector("#comp5").classList.contains("selected")'),'exact native chain produces green component reward')
    check('Correct' in read('document.querySelector("#mulerQuizVerdict").textContent'),'exact native verdict is successful')
    shot('native56-ethane-success')
    if ev('fMulerSelectActive()'):pointer('#selectAtomsBtn')
    if not ev('nameAnalysisMode==="compCarbonsCount"'):pointer('#comp5')
    check(ev('nameAnalysisMode==="compCarbonsCount"'),'normal component remains selected outside picking after reward')
    select('butane');check(ev('nameAnalysisMode==="compCarbonsCount"&&document.querySelector("#comp5").classList.contains("selected")'),'native sticky component survives plain molecule change')
    pointer('#nameExplainAllBtn');check(ev('window.nameExplainAll&&!!document.querySelector("#nameAnalysisExplain .explainRow")'),'overview table opens')
    pointer('#nameExplainAllBtn');check(ev('!window.nameExplainAll'),'overview returns to individual explanation')
    select('penten_3_yne_1','expanded')
    out['actualLiteralHydrogen']=read('({atom:jsmeNomeclatureApplet.getAtom(0,6).label,rawContains:MOL2D.penten_3_yne_1.expanded.includes("[H]"),name:currentMolName,types:allAtomsTypeList.slice()})')
    check(out['actualLiteralHydrogen']['rawContains'] and out['actualLiteralHydrogen']['atom']=='H','real JSME normalizes preserved literal[H] source to H',out['actualLiteralHydrogen'])
    check(bool(out['actualLiteralHydrogen']['name']) and 'unsupported' not in out['actualLiteralHydrogen']['name'].lower(),'real normalized literalH molecule remains named')
    select('ethane','expanded');arm_root();chain=read('fMulerMainChainResolved().slice()')
    hyd=read('(()=>{for(const b of bondList){if(b[0]===fMulerMainChainResolved()[0]&&allAtomsTypeList[b[1]-1]==="H")return b[1];if(b[1]===fMulerMainChainResolved()[0]&&allAtomsTypeList[b[0]-1]==="H")return b[0]}return null})()')
    click_atom(hyd);check(ev('MulerUserSelection.atoms2D.length===1&&allAtomsTypeList[MulerUserSelection.atoms2D[0]-1]==="C"'),'teacher armed-quiz H-to-parent policy preserved explicitly')
    click_atom(chain[1]);check(ev('!window.MulerQuizTarget'),'expanded H-to-parent/native chain completes as teacher56')
    if ev('fMulerSelectActive()'):pointer('#selectAtomsBtn')
    select('methyl_2_pentane','skeletal');pointer('#selectAtomsBtn');arm_root()
    pool=read('fMulerQuizMainChainPool().map(x=>x.chain)');check(len(pool)>1,'branched native mission retains equivalent parent candidates',pool)
    for atom in pool[-1]:click_atom(atom)
    check(ev('!window.MulerQuizTarget'),'alternative valid native parent is accepted')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(500)
    check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'native successful drawing survives390px resize');shot('native56-mobile')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});pause(300)
    navigate('mulermoc-nom-56.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&v=native-present56-'+str(time.time_ns()))
    wait('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&!document.documentElement.classList.contains("lesson-loading")',100)
    check(not visible('#selectAtomsBtn'),'selection entry remains hidden in actual lesson presentation')
    check(ev('!window.MulerQuizTarget'),'scenario replay does not arm native quiz')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
    try:shot('native56-failure');out['failureState']=read('({mol:selectedMol,mode:mode2D,target:window.MulerQuizTarget,selection:window.MulerUserSelection,toggleTrace:window.__toggleTrace,ready:window.JSmolReadyFlag,name:currentMolName,explain:document.querySelector("#nameAnalysisExplain")?.textContent})')
    except Exception:pass
finally:finish('native56-browser')
if not out['completed']:raise SystemExit(1)
