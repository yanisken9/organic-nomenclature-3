"""Check only affected existing alkane-lesson steps; never edits the lesson."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],
             'existing-firefox-bidi-harness', 'exec'))
source = json.loads(Path('scenarios/alkanes-nomenclature-branches.scenario.json').read_text())
targets = {'dimethyl_2_3_butane': ('2,3-διμεθυλοβουτάνιο',4),
           'ethyl_3_dimethyl_2_5_hexane': ('3-αιθυλο-2,5-διμεθυλοεξάνιο',6)}
result = {'completed':False,'steps':[]}
try:
    navigate('mulermoc-nom-52.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=alkane-mol-20261030')
    until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')")
    app_ready(); until('!!window.JSmolReadyFlag')
    for i,step in enumerate(source['steps']):
        if step['selectedMol'] not in targets:
            continue
        ev('fScenarioGo('+str(i)+');true')
        until('selectedMol==='+json.dumps(step['selectedMol'])+'&&nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']))
        until('mainChainPool3DKey==='+json.dumps(step['selectedMol']))
        row = json.loads(ev(r'''JSON.stringify((()=>{
          const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
          const lines=jsmeNomeclatureApplet.molFile().split('\n'),pts=lines.slice(4,4+atomsCount).map(l=>[+l.slice(0,10),+l.slice(10,20)]);
          const ys=mainChainAtomsList.map(i=>pts[i-1][1]);
          return {key:selectedMol,mode:mode2D,name:currentMolName,chain:mainChainAtomsList,
            horizontal:Math.max(...ys)-Math.min(...ys)<.001,
            mapping:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D),
            clipped:[...svg.querySelectorAll('text:not([id^=number])')].filter(e=>{const b=e.getBoundingClientRect();return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent)};
        })())'''))
        expected,parent = targets[step['selectedMol']]
        assert row['name']==expected and len(row['chain'])==parent and row['horizontal'] and row['mapping'] and not row['clipped'],(i+1,row)
        result['steps'].append(dict(step=i+1,**row))
    assert not js_errors,js_errors
    result['completed']=True
finally:
    result['javascriptErrors']=js_errors
    (args.output/'lesson.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':result['completed'],'affectedSteps':len(result['steps']),'errors':len(js_errors)}),flush=True)
