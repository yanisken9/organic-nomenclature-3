from pathlib import Path
exec(compile((Path(__file__).with_name('support.py')).read_text(), 'detective-support', 'exec'))

EXPECT = {
 'ethane': {'parent-chain': [[1,2]], 'single-bonds': [[1]]},
 'butane': {'parent-chain': [[2,3,4,5]], 'single-bonds': [[2,3,4]]},
 'methyl_2_pentane': {'parent-chain': [[1,2,3,4,6],[2,3,4,5,6]], 'branches': [[1],[5]], 'single-bonds': [[1,2,3,4,5]]},
 'dimethyl_2_3_butane': {'parent-chain': [[1,2,3,4],[1,2,3,6],[2,3,4,5],[2,3,5,6]], 'branches': [[1,4],[1,6],[4,5],[5,6]], 'single-bonds': [[1,2,3,4,5]]},
 'ethene': {'parent-chain': [[1,2]], 'double-bonds': [[1]]},
 'butene_1': {'parent-chain': [[1,2,3,4]], 'double-bonds': [[3]]},
 'butene_2': {'parent-chain': [[1,2,3,4]], 'double-bonds': [[2]]},
 'butyne_1': {'parent-chain': [[1,2,3,4]], 'triple-bonds': [[3]]},
 'butyne_2': {'parent-chain': [[1,2,3,4]], 'triple-bonds': [[2]]},
 'butadiene_1_2': {'parent-chain': [[1,2,3,4]], 'double-bonds': [[1,2]]},
 'butadiene_1_3': {'parent-chain': [[1,2,3,4]], 'double-bonds': [[1,3]]},
 'ethanol': {'parent-chain': [[1,2]], 'single-bonds': [[1]], 'hydroxyl': [[3,9]]},
 'butanol_2': {'parent-chain': [[1,2,3,4]], 'single-bonds': [[1,2,3]], 'hydroxyl': [[5,15]]},
 'propanal': {'parent-chain': [[1,2,3]], 'single-bonds': [[1,2]], 'aldehyde': [[3,4,10]]},
 'propanone': {'parent-chain': [[1,2,3]], 'single-bonds': [[1,2]], 'carbonyl': [[2,10]]},
 'pentanone_3': {'parent-chain': [[1,2,3,4,5]], 'single-bonds': [[1,2,3,4]], 'carbonyl': [[3,6]]},
 'methanoicacid': {'parent-chain': [[1]], 'carboxyl': [[1,2,4,5]]}
}
paths = json.loads((ROOT/'docs/checks/molecular-detective-plan-20261115/plan.json').read_text())['newImplementationFiles']
hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
out['runtimeAtStart'] = hashes
out['controlMethod'] = 'Molecule/mission select value + change event; molecule answers use genuine WebDriver pointer actions at visible SVG anchors/bond interiors. No direct selection setter or fabricated target.'
W = 'document.querySelector("#molecule-viewer").contentWindow'
S = 'NameleculeMolecularDetective.snapshot()'
def ready(): wait(S+'.phase==="active"', 40)
def snapshot(): return read(S)
def change_molecule(id):
    ev('(()=>{const e=document.querySelector("#molecule-select");e.value='+json.dumps(id)+';e.dispatchEvent(new Event("change",{bubbles:true}));return true})()')
    wait(S+'.moleculeId==='+json.dumps(id)+'&&'+S+'.phase==="active"')
def mission_list(): return read('NameleculeMolecularDetectiveEngine.missions('+W+'.NameleculeMolecularDetectiveHost.getSnapshot())')
def choose_family(family):
    missions = mission_list()
    index = next(i for i,m in enumerate(missions) if m['family']==family)
    previous = snapshot()['bridgeMissionId']
    ev('(()=>{const e=document.querySelector("#mission-select");e.value='+str(index)+';e.dispatchEvent(new Event("change",{bubbles:true}));return true})()')
    wait(S+'.phase==="active"&&'+S+'.bridgeMissionId!=='+json.dumps(previous))
    return missions[index]
def clear():
    if snapshot()['atoms'] or snapshot()['bonds']:
        click('#clear-selection')
        wait(S+'.atoms.length===0&&'+S+'.bonds.length===0')
def pick(kind, id, touch=False):
    ev('document.querySelector("#molecule-viewer").scrollIntoView({block:"center",behavior:"instant"});true')
    pause(60)
    script = '''(()=>{const f=document.querySelector('#molecule-viewer'),w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg');let x,y;
      if(KIND==='atoms'){const a=g.anchors.find(a=>a.atom+1===ID);if(!a)throw Error('Missing anchor '+ID);x=a.x;y=a.y;}
      else {const group=g.groups.find(a=>a.bond+1===ID);if(!group)throw Error('Missing bond '+ID);const line=group.rep;let found=false;
        for(const t of [.5,.6,.4,.7,.3,.8,.2]){const xx=line.x1+(line.x2-line.x1)*t,yy=line.y1+(line.y2-line.y1)*t;
          if(!g.anchors.some(a=>a.w>0&&a.h>0&&xx>=a.x-a.w/2&&xx<=a.x+a.w/2&&yy>=a.y-a.h/2&&yy<=a.y+a.h/2)){x=xx;y=yy;found=true;break;}}
        if(!found)throw Error('No visible bond interior '+ID);}
      const p=svg.createSVGPoint();p.x=x;p.y=y;const screen=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM()),r=f.getBoundingClientRect();
      return{x:r.x+screen.x,y:r.y+screen.y,world:{x,y},expected:ID,kind:KIND};})()'''.replace('KIND',json.dumps(kind)).replace('ID',str(id))
    point = read(script)
    before = snapshot()
    pointer_at(point['x'], point['y'], touch)
    wait(S+'.selectionRevision>'+str(before['selectionRevision']), 5)
    return point
def selected(kind): return snapshot()[kind]
def check_result(correct):
    click('#check-answer')
    wait('!document.querySelector("#feedback").hidden')
    check(snapshot()['correct'] is correct, 'Genuine UI check '+('correct' if correct else 'incorrect'), snapshot())
def sets(a): return sorted([sorted(x) for x in a])
try:
    call('script.addPreloadScript',{'functionDeclaration':'() => { window.__detectiveMessages=[]; window.addEventListener("message",e=>{if(e.data?.channel==="namelecule-molecular-detective-v1") window.__detectiveMessages.push(e.data)}); }','contexts':[ctx]})
    navigate('games/molecular-detective.html')
    ready()
    check(len(read('Array.from(document.querySelector("#molecule-select").options)'))==17, '17 available molecule controls')
    ev('localStorage.setItem("namelecule:lesson-checkpoints:v1:2feede3e","detective-preservation-sentinel");true')
    check_result(False)
    check('first' not in read('document.querySelector("#feedback").textContent').lower(), 'Empty attempt handled without solution')
    # Raw H stays H, wrong kind retains the attempt, and click toggles.
    pick('atoms',3)
    check(selected('atoms')==[3], 'Hydrogen stays raw H, never redirected to C')
    pick('bonds',1)
    check(selected('atoms')==[3] and not selected('bonds'), 'Wrong-kind bond click retains atom attempt')
    check_result(False)
    check(selected('atoms')==[3], 'Incorrect attempt stays editable')
    pick('atoms',3)
    check(not selected('atoms'), 'Click toggles selection off')
    pick('atoms',2)
    before=selected('atoms')
    click('#zoom-in');pause();click('#zoom-out');pause()
    check(selected('atoms')==before, 'Zoom in/out preserves current attempt')
    pick('atoms',1) # Focus the child before testing its native Escape handler.
    key('\ue00c'); wait(S+'.atoms.length===0')
    check(True, 'Native Escape clears with parent notification')
    # Independent expanded-MOL table oracles; every accepted alternative is earned by actual clicks.
    actual_answers=0;graph_rows=[]
    for molecule, families in EXPECT.items():
        change_molecule(molecule)
        graph=read(W+'.NameleculeMolecularDetectiveHost.getSnapshot()')
        missions=mission_list()
        check(set(m['family'] for m in missions)==set(families), molecule+' actual native mission families')
        check(read('document.querySelector("#mission-name").textContent')==graph['correctName'], molecule+' actual name serialized exactly')
        check(ev(W+'.MulerQuizTarget===null&&'+W+'.eval("nameAnalysisMode")==="none"&&!'+W+'.document.querySelector("#jsmeNomeclatureSVG text[id^=number]")'), molecule+' no automatic answer cues/numbering')
        graph_rows.append({'id':molecule,'name':graph['correctName'],'families':[m['family'] for m in missions]})
        for family,alternatives in families.items():
            mission=choose_family(family)
            check(sets(mission['accepted'])==sets(alternatives),molecule+'/'+family+' actual DOM/graph targets match independent oracle')
            for answer in alternatives:
                clear()
                for id in reversed(answer):pick(mission['kind'],id)
                check(selected(mission['kind'])==sorted(answer), molecule+'/'+family+' actual selected IDs',answer)
                check_result(True);actual_answers+=1
                check(not ev('document.querySelector("#next-mission").hidden'), 'Success exposes explicit next mission')
    out['actualCorrectAnswers']=actual_answers;out['nativeGraphs']=graph_rows
    # Exact edge-identity regression; adding the middle single bond must fail.
    change_molecule('butadiene_1_3');choose_family('double-bonds')
    for id in [1,2,3]:pick('bonds',id)
    check_result(False)
    check(selected('bonds')==[1,2,3], 'Diene endpoint-union false positive rejected without erasing choice')
    pick('bonds',2);check_result(True)
    # Next actually advances and clears the previous result.
    old=snapshot()['bridgeMissionId'];click('#next-mission');ready()
    check(snapshot()['bridgeMissionId']!=old and not snapshot()['atoms'] and not snapshot()['bonds'] and ev('document.querySelector("#feedback").hidden'), 'Next mission clears prior answer/result')
    # Carbonyl literal region and acid formyl-H exclusion through actual picks.
    change_molecule('propanone');choose_family('carbonyl')
    for id in [1,2,3,10]:pick('atoms',id)
    check_result(False)
    pick('atoms',1);pick('atoms',3);check_result(True)
    change_molecule('methanoicacid');choose_family('carboxyl')
    for id in [1,2,3,4,5]:pick('atoms',id)
    check_result(False)
    pick('atoms',3);check_result(True)
    # Retain actual old receipt, then replay from its legitimate child source.
    old_receipt=read('window.__detectiveMessages.filter(m=>m.type==="selection").at(-1)')
    change_molecule('ethane');pick('atoms',1)
    before=snapshot()
    ev(W+'.parent.postMessage('+json.dumps(old_receipt)+',location.origin);true');pause()
    check(snapshot()==before, 'Stale real selection receipt from old round ignored')
    ev('window.postMessage('+json.dumps(old_receipt)+',location.origin);true');pause()
    check(snapshot()==before, 'Wrong-source message ignored')
    ev('(()=>{const e=document.querySelector("#molecule-select");for(const id of ["butane","ethanol","butyne_2"]){e.value=id;e.dispatchEvent(new Event("change",{bubbles:true}));}return true})()')
    wait(S+'.phase==="active"&&'+S+'.moleculeId==="butyne_2"')
    check(read(W+'.NameleculeMolecularDetectiveHost.getSnapshot().moleculeId')=='butyne_2', 'Rapid molecule changes settle only latest native round')
    # Typography contract and viewport-emulated touch.
    ev('document.fonts.ready.then(()=>true)')
    font=read('(()=>{const s=getComputedStyle(document.querySelector("h1"));return{family:s.fontFamily,size:s.fontSize,weight:s.fontWeight,line:s.lineHeight,spacing:s.letterSpacing,body:getComputedStyle(document.body).fontFamily}})()')
    out['detectiveFont']=font
    check(font['family'].replace('"','')=='Roboto Condensed, sans-serif' and font['size']=='40px' and font['weight']=='700','Detective title matches approved font contract',font)
    change_molecule('methyl_2_pentane');choose_family('parent-chain')
    ev('window.scrollTo(0,0);true');shot('desktop-game')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(250)
    check(ev('document.documentElement.scrollWidth<=innerWidth+1'), '390px page has no horizontal overflow')
    pick('atoms',2,touch=True)
    check(selected('atoms')==[2], '390px genuine touch selects atom')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':320,'height':740},'devicePixelRatio':1});pause(200)
    check(selected('atoms')==[2] and ev('document.documentElement.scrollWidth<=innerWidth+1'), '320px resize preserves selection without horizontal overflow')
    click('#clear-selection');wait(S+'.atoms.length===0');shot('mobile-controls')
    check(ev('localStorage.getItem("namelecule:lesson-checkpoints:v1:2feede3e")==="detective-preservation-sentinel"'),'Existing lesson progress storage left unchanged')
    call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready()
    check(snapshot()['moleculeId']=='ethane' and not snapshot()['atoms'],'Actual reload returns working fresh mission')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
    navigate('games/molecular-puzzle.html');wait('!!document.querySelector(".puzzle-title h1")');ev('document.fonts.ready.then(()=>true)')
    puzzle_font=read('(()=>{const s=getComputedStyle(document.querySelector("h1"));return{family:s.fontFamily,size:s.fontSize,weight:s.fontWeight,line:s.lineHeight,spacing:s.letterSpacing,body:getComputedStyle(document.body).fontFamily}})()')
    check(font==puzzle_font,'Actual Puzzle and Detective typography matches',{'detective':font,'puzzle':puzzle_font})
    navigate('design/molecular-detective-preview.html')
    wait('document.querySelector(".preview-frame").contentWindow.NameleculeMolecularDetective?.snapshot().phase==="active"')
    check(ev('document.querySelector(".preview-frame").contentDocument.body.classList.contains("detective-embedded")'),'Lesson-look preview opens functioning embedded game')
    check(ev('document.querySelector(".preview-frame").contentDocument.documentElement.scrollHeight>document.querySelector(".preview-frame").clientHeight'),'Lesson-look preview can scroll its content')
    shot('lesson-look')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(200)
    check(ev('document.documentElement.scrollWidth<=innerWidth+1&&document.querySelector(".preview-frame").contentDocument.documentElement.scrollWidth<=document.querySelector(".preview-frame").clientWidth+1'),'390px lesson-look framing fits width')
    check(not js_errors,'No captured JavaScript exceptions',js_errors)
    out['runtimeAtFinish']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    check(out['runtimeAtFinish']==hashes,'All eight runtime files unchanged during acceptance')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc()
    try:
        out['stateAtFailure']=snapshot();shot('failure')
    except Exception:pass
finally: finish('acceptance')
if not out['completed']: raise SystemExit(1)
