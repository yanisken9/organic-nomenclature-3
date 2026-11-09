"""Transient before/after reproduction of the first extreme-zoom audit failure."""
from pathlib import Path
import runpy
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
T=runpy.run_path(str(HERE/'transform.py'));old=json.load(gzip.open(HERE/'before-sources.json.gz','rt'))
new_data=(ROOT/T['DATA']).read_text();old_view=old['js/mulermoc-nom-molview-52.js']
def calibration(code):
    a=code.index('function fPrepareFixedCCAlkanePrototype()');b=code.index('function fGetUniform2DLibraryFrame()',a)
    return code[a:b]
out={'cases':[],'completed':False,'transientOnly':True}
try:
    start('mulermoc-nom-52.html?audit=carbonyl-acid-zoom-diagnostic')
    for phase,data,viewer in [('before',old[T['DATA']],old_view),('after',new_data,(ROOT/'js/mulermoc-nom-molview-52.js').read_text())]:
        ev('fPrepareFixedCCAlkanePrototype=('+calibration(viewer)+');true')
        for key in KEYS:
            mol=T['literal'](data,key)[1]
            ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=window.MOL2D['+json.dumps(key)+'].expanded='+json.dumps(mol)+';true')
        ev('uniform2DLibraryFrame=null;true');select_ui('ethyl_2_methyl_3_pentanal')
        ev('document.getElementById("comp5").click();true')
        until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
        for target,button in [(.5,'zoomOutBtn'),(6,'zoomInBtn')]:
            ev('for(let i=0;i<16;i++)document.getElementById('+json.dumps(button)+').click();true')
            row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(phase=phase,zoom=target)
            row['inkMetrics']=json.loads(ev(json.loads((HERE/'control-probes.json').read_text())['ink_probe']))
            row['actualFontAndInk']=json.loads(ev('JSON.stringify((()=>{const t=molSvg.node.querySelector("text[data-namelecule-role=label]"),m=t.getScreenCTM(),b=NameleculeLabelMetrics.element(t);return{fontCSS:parseFloat(getComputedStyle(t).fontSize)*Math.hypot(m.a,m.b),inkWidthCSS:(b.right-b.left)*Math.hypot(m.a,m.b),DOMBoxWidth:t.getBoundingClientRect().width}})())'))
            out['cases'].append(row);screenshot(HERE/('zoom-'+phase+'-'+str(target)+'.png'))
            print(phase,target,'clipped',row['clipped'],'overlaps',row['overlaps'],'raster',row['raster'],flush=True)
    out['completed']=True
finally:save_result(out,'zoom-diagnostic.json.gz')
