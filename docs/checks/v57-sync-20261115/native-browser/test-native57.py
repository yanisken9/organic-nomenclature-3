"""Frozen57 real JSmol/native picking, ownership and isolated transport probes."""
from pathlib import Path
prefix=Path(__file__).with_name('test-first57.py').read_text().split('\ntry:\n')[0]
exec(compile(prefix,'native57-helpers','exec'))
F=json.loads((HERE.parent/'verification-target.json').read_text());C=Path(F['candidate'])
def frozen():return {p:hashlib.sha256((C/p).read_bytes()).hexdigest() for p in F['files']}==F['files']
def select(m,mode='expanded'):
    ev('selectedMol='+json.dumps(m)+';mode2D='+json.dumps(mode)+';fSelectMol();true');wait('fMuler3DModelReady()',40);pause(200)
def active():
    if not ev('fMulerSelectActive()'):click('#selectAtomsBtn')
    wait('fMulerSelectState().active&&fMuler3DModel.picking');pause(120)
def pick3(a):pointer_at(point3d(a));pause(250)
def pick2(a):
    ev('document.querySelector("#jsmeNomeclatureSVG").scrollIntoView({block:"center",behavior:"instant"});true');pause(100)
    p=read('(()=>{const a=fMulerSelectAnchors().find(p=>p.atom==='+str(a-1)+');if(!a)throw Error("no2Danchor");const g=document.querySelector("#jsmeNomeclatureSVG svg g"),p=new DOMPoint(a.x,a.y).matrixTransform(g.getScreenCTM());return{x:p.x,y:p.y}})()');pointer_at(p);pause(250)
def clear():
    ev('fMulerSelectClear();fMulerSelectRepaint();true');pause(150)
def bg():
    ev('document.querySelector("#nomeclature3D canvas").scrollIntoView({block:"center",behavior:"instant"});true');pause(100)
    return read('(()=>{const r=document.querySelector("#nomeclature3D canvas").getBoundingClientRect();return{x:r.x+15,y:r.y+15}})()')
def sel():return read('({a2:fMulerSelectState().atoms2D,a3:fMulerSelectState().atoms3D,b2:fMulerSelectState().bonds2D,b3:fMulerSelectState().bonds3D,target:window.MulerQuizTarget})')
try:
    assert frozen();out['frozenTarget']=F['files']
    call('script.addPreloadScript',{'functionDeclaration':'()=>{window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
    navigate('mulermoc-nom-57.html?libs=cdn&lang=en');app_ready();wait('window.JSmolReadyFlag===true',70)
    select('ethanol');active();check(True,'Cold57 model ownership gate and native selection entry ready',model_state())
    pick3(1);check(sel()['a2']==[3] and sel()['a3']==[1],'Genuine3D O maps to2D O',sel());pick3(1);check(not sel()['a2'] and not sel()['a3'],'Genuine3D O retoggle removes both')
    pick3(9);check(sel()['a2']==[9] and sel()['a3']==[9],'Free OH hydrogen stays individual in both viewers',sel());pick3(9)
    pick2(3);check(sel()['a3']==[1],'Genuine2D O maps to3D O');pick3(1);check(not sel()['a2'] and not sel()['a3'],'3D deselection removes2D-origin membership')
    p1=point3d(2);p2=point3d(3);pointer_at({'x':(p1['x']+p2['x'])/2,'y':(p1['y']+p2['y'])/2});pause(350)
    check(sel()['b3']==[3] and len(sel()['b2'])==1 and not sel()['a2'],'Genuine projected C-C bond midpoint uses actual bond callback',sel())
    bond2=sel()['b2'][0];p1=point3d(2);p2=point3d(3);pointer_at({'x':(p1['x']+p2['x'])/2,'y':(p1['y']+p2['y'])/2});pause(250);check(not sel()['b3'] and not sel()['b2'],'Genuine3D bond retoggle clears both')
    pick3(1);p=bg();pointer_at(p);pause(650);check(sel()['a3']==[1],'Single3D background click preserves selection')
    pointer_at(p);pause(70);pointer_at(p);pause(650);check(not sel()['a3'] and not sel()['a2'],'Double3D background tap clears both')
    click('#comp9');wait('window.MulerQuizTarget==="compSuffix"');check(read('fMulerQuizTargetSet().slice().sort((a,b)=>a-b)')==[3,9],'Native OH mission explicitly targets O and H')
    pick3(1);check(ev('window.MulerQuizTarget==="compSuffix"&&fMulerSelectState().atoms2D.includes(3)'),'Partial3D OH selection stays armed')
    pick3(9);check(ev('!window.MulerQuizTarget&&document.querySelector("#comp9").classList.contains("selected")'),'Genuine3D explicit OH H completes native functional-group reward')
    for molecule in ['hydroxypropanoic_acid_2','aminobutanoic_acid_3','Oxopropanoic_acid']:
        select(molecule);active()
        if not ev('window.MulerQuizTarget==="compSecondSub1"'):click('#comp1')
        wait('window.MulerQuizTarget==="compSecondSub1"')
        ids=read('fMulerQuizTargetSet().slice()');check(bool(ids),'Secondary hetero-prefix has exact target: '+molecule,read('fMulerQuizTargetSet().map(a=>({id:a,el:allAtomsTypeList[a-1]}))'))
        for a in ids:pick2(a)
        check(ev('!window.MulerQuizTarget&&document.querySelector("#comp1").classList.contains("selected")'),'Actual2D hetero-prefix picks earn native reward: '+molecule)
    select('ethane');active();click('#comp5');wait('window.MulerQuizTarget==="compCarbonsCount"')
    table=read('bondList3D.map((b,i)=>({id:i+1,b})).filter(x=>allAtomsTypeList3D[x.b[0]-1]==="H"||allAtomsTypeList3D[x.b[1]-1]==="H")');carbon=read('allAtomsTypeList3D.indexOf("C")+1')
    hs=[]
    for r in table:
        if carbon in r['b'][:2]:hs.append(r['b'][0] if r['b'][1]==carbon else r['b'][1])
    assert len(hs)>=2
    pick3(carbon);pick3(hs[0]);pick3(hs[1]);check(len(sel()['a2'])==1 and len(sel()['a3'])==3,'Multiple3D H/C contributors share correct parent membership',sel())
    pick3(hs[0]);check(len(sel()['a2'])==1 and len(sel()['a3'])==2,'Removing one H contributor keeps other parent contributors',sel())
    pick3(carbon);check(len(sel()['a2'])==1 and sel()['a3']==[hs[1]],'Removing C retains H-origin parent membership',sel())
    pick3(hs[1]);check(not sel()['a2'] and not sel()['a3'],'Removing last H clears parent without orphan')
    clear();ev('window.MulerQuizTarget=null;true');select('ethanol');active();pick3(1)
    ev('window.__oldPickName=fMuler3DModel.pickCallback;window.__oldPick=window[__oldPickName];window.__oldToken=fMuler3DModel.id;true')
    select('propane');check(not sel()['a2'] and not sel()['a3'],'Molecule change clears prior selection and contributions')
    before=sel();ev('window.__oldPick("jmolAppletNomeclature","O #1",0,{index:0});window.__muler3DLoadDone(window.__oldToken);true');check(sel()==before and ev('typeof window[__oldPickName]==="undefined"'),'Old actual callback closure and load token cannot affect new molecule')
    # Controlled page-parser delay while real JSmol finishes its real model load.
    ev('window.__savedParsed=fMuler3DParsedSource;window.__heldParsed=[];fMuler3DParsedSource=function(m,t){__heldParsed.push([m,t])};selectedMol="butane";mode2D="expanded";fSelectMol();true')
    wait('fMuler3DModel.completed&&window.__heldParsed.length>0',35)
    check(ev('!fMuler3DModelReady()&&!fMulerSelectFullMap()'),'Real completed JSmol model cannot arm before delayed current parser acknowledgement')
    ev('fMuler3DParsedSource=window.__savedParsed;for(const x of __heldParsed)fMuler3DParsedSource(...x);true');wait('fMuler3DModelReady()',15);check(True,'Releasing exact delayed source opens ownership gate')
    # Controlled loader submission hold: real model is old, current parse can finish first.
    ev('window.__savedScript=Jmol.script;window.__heldScripts=[];Jmol.script=function(a,c){if(/frank off;load /.test(c)){__heldScripts.push([a,c]);return null}return __savedScript.apply(this,arguments)};selectedMol="pentane";fSelectMol();true')
    wait('fMuler3DModel.parsed&&window.__heldScripts.length>0',20)
    check(ev('!fMuler3DModel.completed&&!fMuler3DModelReady()&&!fMulerSelectFullMap()'),'Current parsed SDF cannot arm against prior visible model before real load tail')
    ev('Jmol.script=window.__savedScript;for(const x of __heldScripts)Jmol.script(...x);true');wait('fMuler3DModelReady()',35);check(True,'Real released load completion restores ready picking')
    # Explicit model transport failure: recovery uses fresh owned load, not a false completion.
    ev('window.__orig3DFile=nameExamples.ethane.file3D;nameExamples.ethane.file3D="mols/not-present-v57-safety.sdf";selectedMol="ethane";fSelectMol();true');pause(1800)
    check(ev('!fMuler3DModelReady()&&!fMulerSelectFullMap()'),'Unavailable3D file fails closed while2D remains usable',model_state())
    check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Failed3D transport preserves actual2D drawing')
    ev('nameExamples.ethane.file3D=window.__orig3DFile;fSelectMol();true');wait('fMuler3DModelReady()',40);check(True,'Fresh correct source recovers after failed3D load')
    select('ethanol','condensed');active();check(True,'Condensed mode reload passes live-model guard');select('ethanol','skeletal');active();check(True,'Skeletal mode reload passes live-model guard')
    select('ethanol','expanded');active();pick3(1)
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(600)
    check(ev('fMuler3DModelReady()&&fMulerSelectState().atoms2D.includes(3)'),'390px resize preserves selection and source ownership');shot('native57-mobile')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});pause(300)
    click('#newMolBtn');wait('!!window.MulerDraft');check(ev('!fMulerSelectActive()&&!fMuler3DModelReady()'),'Draft entry prevents3D picking on transient draft');click('#molDraftCancelBtn');wait('!window.MulerDraft');wait('fMuler3DModelReady()',40);check(ev('!fMulerSelectActive()'),'DraftCancel restores model with inactive selection')
    navigate('mulermoc-nom-57.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library');wait('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&!document.documentElement.classList.contains("lesson-loading")',100)
    check(ev('!window.MulerQuizTarget&&!fMulerSelectActive()'),'Actual lesson Present does not arm native selection quiz');shot('native57-present')
    check(frozen(),'All17 frozen runtime hashes unchanged during native browser matrix')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
    try:out['modelAtFailure']=model_state();shot('native57-failure')
    except Exception as extra:out['failureDiagnostic']=str(extra)
finally:finish('native57')
if not out['completed']:raise SystemExit(1)
