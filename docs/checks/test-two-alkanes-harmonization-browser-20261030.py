"""Actual Firefox/JSME checks; output stays under the supplied artifact folder.

Requires the existing localhost8013 and isolated Firefox BiDi9237 harness.
Width390 is responsive emulation, not a physical mobile-device test.
"""
from pathlib import Path
import argparse
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],
             'existing-firefox-bidi-harness', 'exec'))

specs = [('dimethyl_2_3_butane', '2,3-διμεθυλοβουτάνιο', 6, 14, 4),
         ('ethyl_3_dimethyl_2_5_hexane', '3-αιθυλο-2,5-διμεθυλοεξάνιο', 10, 22, 6)]
result = {'completed': False, 'forms': [], 'interactions': [], 'models': []}


def data(expression):
    return json.loads(ev('JSON.stringify(' + expression + ')'))


measure = r'''(()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
 const labels=[...svg.querySelectorAll('text')].filter(e=>e.textContent.trim()&&getComputedStyle(e).visibility!=='hidden'&&!(e.id||'').startsWith('number'));
 const overlaps=[];
 for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){
   const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();
   if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([labels[i].id,labels[i].textContent,labels[j].id,labels[j].textContent]);
 }
 const fonts=labels.map(e=>{const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b)});
 return {key:selectedMol,mode:mode2D,name:currentMolName,chain:mainChainAtomsList,overlaps,fonts,
  visibleH:labels.filter(e=>e.textContent==='H').length,
  clipped:labels.filter(e=>{const b=e.getBoundingClientRect();return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),
  viewport:[outer.width,outer.height],numbers:[...svg.querySelectorAll('text[id^=number]')].map(e=>+e.textContent)};
})()'''

try:
    navigate('mulermoc-nom-52.html?v=alkanes-harmonized-20261030')
    app_ready(); ev('document.fonts.ready.then(()=>true)')
    for width in [1500, 390]:
        call('browsingContext.setViewport', {'context':ctx, 'viewport':{'width':width,'height':1000}, 'devicePixelRatio':1})
        time.sleep(.3)
        for key, name, carbons, hydrogens, parent in specs + [('methyl_2_pentane','2-μεθυλοπεντάνιο',6,14,5)]:
            ev('document.getElementById('+json.dumps(key)+').click();true')
            for index, mode in enumerate(['condensed','expanded','skeletal']):
                ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
                row = data(measure); row['width'] = width
                assert row['name'] == name and len(row['chain']) == parent, row
                assert not row['overlaps'] and not row['clipped'], row
                if mode == 'expanded':
                    assert row['visibleH'] == hydrogens, row
                result['forms'].append(row)
                if width == 1500:
                    screenshot(str(args.output/(key+'-'+mode+'.png')))
        print('PASS forms width', width, flush=True)

    call('browsingContext.setViewport', {'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
    until('!!window.JSmolReadyFlag')
    ev("window.__colored=()=>Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').filter(a=>a.color.toLowerCase()==='[xd8eedc]').map(a=>a.atomno).sort((a,b)=>a-b);window.__withH=cs=>{const ids=new Set(cs);for(const[a,b]of bondList3D){if(ids.has(a)&&allAtomsTypeList3D[b-1]==='H')ids.add(b);if(ids.has(b)&&allAtomsTypeList3D[a-1]==='H')ids.add(a)}return [...ids].sort((a,b)=>a-b)};true")
    for key, name, carbons, hydrogens, parent in specs:
        ev('document.getElementById('+json.dumps(key)+').click();true')
        until('mainChainPool3DKey==='+json.dumps(key))
        until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
        model = data("({atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length,parsedAtoms:allAtomsTypeList3D.length})")
        assert model['atoms'] == model['parsedAtoms'] == carbons + hydrogens, model
        result['models'].append(dict(key=key, **model))
        for index, mode in enumerate(['condensed','expanded','skeletal']):
            ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
            for chain_mode in ['algorithmic', 'data']:
                ev('mainChainMode='+json.dumps(chain_mode)+';fLoadMol2D();fCalcMainChain3D();fShowNameAnalysis();true')
                assert ev('currentMolName') == name
                assert ev("fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)")
            ev("if(!document.querySelector('#highlightNumberingCheck').classList.contains('selectedCheck'))document.querySelector('#highlightNumberingCheck').click();fShowNameAnalysis();document.getElementById('comp5').click();true")
            until('JSON.stringify(__colored())===JSON.stringify(mainChainAtoms3D.slice().sort((a,b)=>a-b))', seconds=15)
            until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length==="+str(parent), seconds=15)
            row = data(measure)
            assert row['numbers'] == list(range(1,parent+1)), row
            assert not row['clipped'] and not row['overlaps'], row
            result['interactions'].append(dict(component='parent', **row))
            slots = [(1,'comp1')] if key == 'dimethyl_2_3_butane' else [(1,'comp1'),(2,'comp3')]
            for slot, component in slots:
                ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(component)+').click();true')
                until('JSON.stringify(__colored())===JSON.stringify(__withH(fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms))', seconds=15)
                groups = data('({a:fGetHydrocarbonBranchHighlight('+str(slot)+').atoms,b:fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms})')
                assert len(groups['a']) > 0 and len(groups['b']) > 0, groups
                result['interactions'].append(dict(key=key,mode=mode,component=component,groups=groups))
            for factor in [1.25,1]:
                ev('molZoom2D=MOL_ZOOM_DEFAULT*'+str(factor)+';fReapplyZoomScale2D();true')
                row=data(measure)
                assert not row['overlaps'] and not row['clipped'], row
            ev('fClearHighlights();fShowNameAnalysis();true')
        print('PASS models/highlights', key, flush=True)
    assert not js_errors, js_errors
    result['completed'] = True
except Exception as error:
    result['failure'] = str(error); result['traceback'] = traceback.format_exc()
    print(result['traceback'], flush=True)
finally:
    result['javascriptErrors'] = js_errors
    (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close', {'context':ctx}); call('session.end', {})
    print(json.dumps({'completed':result['completed'],'forms':len(result['forms']),'interactions':len(result['interactions']),'models':len(result['models']),'errors':len(js_errors)}),flush=True)
if not result['completed']:
    raise SystemExit(1)
