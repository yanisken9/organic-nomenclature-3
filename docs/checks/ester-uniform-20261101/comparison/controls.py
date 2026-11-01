"""Isolated proposed ester calibration/controls; Main source stays unchanged."""
from pathlib import Path
import base64
HERE=Path(__file__).resolve().parent
exec(compile((HERE/'browser_support.py').read_text(),'support','exec'))
out={'cases':[],'models':[],'completed':False,'previewOnly':True}
def inspect(width,phase):
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=audit(width,phase);assert ev('!!molSvg.node.dataset.alkaneFixedCCScale')
    out['cases'].append(row)
try:
    start('mulermoc-nom-52.html?audit=ester-preview-controls')
    ev('fPrepareFixedCCAlkanePrototype=('+ (HERE/'preview-calibration.js').read_text()+');true')
    for key in KEYS:
        mol=(HERE/(key+'-proposed.mol')).read_text()
        ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=window.MOL2D['+json.dumps(key)+'].expanded='+json.dumps(mol)+';true')
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        ev('document.getElementById("rotatePromptDismiss")?.click();true')
        for key in KEYS:
            select_ui(key)
            until('mainChainPool3DKey==='+json.dumps(key))
            until('(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()')
            out['models'].append({'key':key,'width':width,'actualModelURLMatched':True})
            inspect(width,'selected')
            ev('document.getElementById("comp5").click();true')
            until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
            inspect(width,'numbered')
            for target,button in [(.5,'zoomOutBtn'),(6,'zoomInBtn')]:
                ev('for(let i=0;i<16;i++)document.getElementById('+json.dumps(button)+').click();true')
                assert ev('molZoom2D')==target;inspect(width,'zoom-'+str(target))
            ev('fRefreshFontDrawing2D();true');inspect(width,'font-refresh')
            for part in ['comp10','comp11']:
                assert ev('!!document.getElementById('+json.dumps(part)+')')
                ev('document.getElementById('+json.dumps(part)+').click();true')
                inspect(width,part+'-highlight')
            for mode in ['condensed','skeletal','expanded']:
                index=['condensed','expanded','skeletal'].index(mode)
                ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
                assert ev('mode2D')==mode
            inspect(width,'mode-return')
            screenshot(HERE/(key+'-controls-'+str(width)+'.png'))
            print('Controls passed',width,key,flush=True)
    out['completed']=True
except Exception as e:
    out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'controls.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
