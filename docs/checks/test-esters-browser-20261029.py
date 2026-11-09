"""Firefox 2D/3D ester checks through programmatic menu/radio activation.

Uses the existing localhost8013/BiDi9237 harness. Width390 is layout emulation,
not a physical mobile interaction test. All artifacts go to --output.
"""
from pathlib import Path
import argparse, traceback

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
folder = parser.parse_args().output
folder.mkdir(parents=True, exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],
             'existing-firefox-bidi-harness', 'exec'))
specs = json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())
result = {'completed': False, 'forms': [], 'models': [], 'highlights': [], 'layout': []}


def data(expr):
    return json.loads(ev('JSON.stringify('+expr+')'))


def geometry():
    return data(r'''(()=>{
      const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
      const els=[...svg.querySelectorAll('text,line,path')].filter(e=>!e.closest('defs')&&!(e.id||'').startsWith('number'));
      const labels=els.filter(e=>e.tagName==='text'&&e.textContent.trim()),overlaps=[];
      for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){
        const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();
        if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([labels[i].textContent,labels[j].textContent]);
      }
      return {key:selectedMol,mode:mode2D,chainMode:mainChainMode,name:currentMolName,chain:mainChainAtomsList,
        clipped:els.filter(e=>{const r=e.getBoundingClientRect();return r.left<outer.left-1||r.right>outer.right+1||r.top<outer.top-1||r.bottom>outer.bottom+1}).map(e=>e.textContent||e.tagName),
        overlaps,texts:labels.map(e=>e.textContent),viewport:[outer.width,outer.height],
        acidLeft:(()=>{if(!fIsSingleEster())return null;const lines=jsmeNomeclatureApplet.molFile().split('\n'),xs=lines.slice(4,4+atomsCount).map(l=>+l.slice(0,10));const mean=ids=>ids.reduce((n,i)=>n+xs[i],0)/ids.length;return mean(esterInfo.acidFrag)<mean(esterInfo.alcoholFrag);})()};
    })()''')


try:
    navigate('mulermoc-nom-52.html?v=esters-browser-20261029')
    app_ready(); until('!!window.JSmolReadyFlag'); ev('document.fonts.ready.then(()=>true)')
    assert ev('Object.keys(nameExamples).length') == 141
    ev("window.__colored=()=>Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').filter(a=>a.color.toLowerCase()==='[xd8eedc]').map(a=>a.atomno).sort((a,b)=>a-b);window.__withH=cs=>{const ids=new Set(cs);for(const [a,b]of bondList3D){if(ids.has(a)&&allAtomsTypeList3D[b-1]==='H')ids.add(b);if(ids.has(b)&&allAtomsTypeList3D[a-1]==='H')ids.add(a);}return [...ids].sort((a,b)=>a-b)};true")
    for spec in specs:
        key = spec['key']; print('CHECK', key, flush=True)
        ev('document.getElementById('+json.dumps(key)+').click();true')
        until('mainChainPool3DKey==='+json.dumps(key))
        until("(()=>{const a=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return a&&a.length===1&&a[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
        model = data("({atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length,parsedAtoms:allAtomsTypeList3D.length,chain:mainChainAtoms3D})")
        assert model['atoms'] == model['parsedAtoms'] == 3*spec['carbons']+2
        result['models'].append(dict(key=key, **model))
        for mode_index, mode in enumerate(['condensed', 'expanded', 'skeletal']):
            ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(mode_index)+'].click();true')
            for cm_index, cm in [(1, 'algorithmic'), (0, 'data')]:
                ev('document.querySelectorAll("#radioChainMode .radioCheckContainer")['+str(cm_index)+'].click();true')
                assert ev('mode2D') == mode and ev('mainChainMode') == cm
                row = geometry()
                assert row['name'] == spec['name'] and len(row['chain']) == spec['parent'], row
                assert row['acidLeft'] and not row['overlaps'] and not row['clipped'], row
                if mode == 'expanded':
                    assert row['texts'].count('H') == 2*spec['carbons'], row
                result['forms'].append(row)
            screenshot(str(folder/(key+'-'+mode+'.png')))
        # Parent stem, acid branches and alcohol group must address different
        # carbon sets. Check actual rendered JSmol colors, not only descriptors.
        ev("document.querySelectorAll('#radioChainMode .radioCheckContainer')[1].click();document.querySelectorAll('#radio2DMode .mode2DOption')[1].click();true")
        ev("if(!document.querySelector('#highlightNumberingCheck').classList.contains('selectedCheck'))document.querySelector('#highlightNumberingCheck').click();true")
        components = [('comp5', 'fGetEsterAcidParentChain()', 'fGetEsterAcidParentChain3D()', spec['parent']),
                      ('comp10', 'fGetEsterAlcoholChain()', 'fGetEsterAlcoholChain3D()', spec['carbons']-spec['acidCarbons'])]
        if spec['acidCarbons'] != spec['parent']:
            components.append(('comp1', 'fGetHydrocarbonBranchHighlight(1).atoms.filter(n=>allAtomsTypeList[n-1]===\'C\')',
                               'fGetHydrocarbonBranchHighlight3D(1).atoms', spec['acidCarbons']-spec['parent']))
        for comp, atoms2, atoms3, count in components:
            ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(comp)+').click();true')
            sets = data('({a:'+atoms2+',b:'+atoms3+',mode:nameAnalysisMode,selection:JmolSelection})')
            assert len(sets['a']) == len(sets['b']) == count, (key, comp, sets)
            expected3 = '('+atoms3+').slice().sort((a,b)=>a-b)' if comp == 'comp5' else '__withH('+atoms3+')'
            until('JSON.stringify(__colored())===JSON.stringify('+expected3+')', seconds=15)
            sets['colored3D'] = data('__colored()')
            sets['component'] = comp; sets['key'] = key
            result['highlights'].append(sets)
            if comp == 'comp5':
                numbers = data("[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>+e.textContent)")
                assert numbers == list(range(1, spec['parent']+1)), (key, numbers)
        ev('fClearHighlights();fShowNameAnalysis();true')
        for width in [390,1500]:
            call('browsingContext.setViewport', {'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
            time.sleep(.3)
            for i in range(3):
                ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click();true')
                row = geometry()
                assert row['acidLeft'] and not row['clipped'] and not row['overlaps'], (width,row)
                result['layout'].append(dict(width=width,**row))
    assert not js_errors, js_errors
    result['completed'] = True
except Exception as e:
    result['failure'] = str(e); result['traceback'] = traceback.format_exc()
    print(result['traceback'], flush=True)
finally:
    result['javascriptErrors'] = js_errors
    (folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close', {'context':ctx}); call('session.end', {})
    print(json.dumps({'completed':result['completed'],'forms':len(result['forms']),'models':len(result['models']),
                      'highlights':len(result['highlights']),'layout':len(result['layout']),'errors':len(js_errors)}),flush=True)

if not result["completed"]:
    raise SystemExit(1)
