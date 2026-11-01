"""Bounded actual controls on transient acid candidates in a disposable tab."""
from pathlib import Path
import os,json,gzip,traceback,runpy
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
h=runpy.run_path(str(HERE/'prepare.py'))
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
probes=json.loads((HERE/'control-probes.json').read_text())
out={'cases':[],'models':[],'completed':False,'previewOnly':True}
def inspect(width,phase):
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
    row.update(width=width,phase=phase)
    assert not row['clipped']and not row['overlaps']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount']
    row['calibration']=json.loads(ev(probes['scale_probe']))
    assert row['calibration']['calibrated']and len(row['calibration']['fonts'])==1
    for r in row['calibration']['ratios']:
        assert abs(r['ratio']-(1.30875 if r['H']else 2.6175))<.013
    row['ink']=json.loads(ev(probes['ink_probe']))
    assert not row['ink']['contacts']and not row['ink']['clippedNumbers'],row['ink']
    if ev('numberingFlag'):
        assert row['ink']['numberTexts']==[str(i+1)for i in range(row['ink']['expected'])]
    out['cases'].append(row)
try:
    navigate('mulermoc-nom-52.html?audit=acid-preview-controls');app_ready();until('window.JSmolReadyFlag===true')
    ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
    ev('fPrepareFixedCCAlkanePrototype=('+ (HERE/'preview-calibration.js').read_text()+');true')
    for key in h['CAPTURE_KEYS']:
        mol=(HERE/(key+'-proposed.mol')).read_text()
        ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=window.MOL2D['+json.dumps(key)+'].expanded='+json.dumps(mol)+';true')
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        ev('document.getElementById("rotatePromptDismiss")?.click();true')
        for key in h['KEYS']+['methanoicacid','aminobutanoic_acid_3']:
            ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true')
            until('selectedMol==='+json.dumps(key)+'&&mode2D==="expanded"')
            until('mainChainPool3DKey==='+json.dumps(key))
            until('(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()')
            out['models'].append({'key':key,'width':width,'actualModelURLMatched':True})
            inspect(width,'selected')
            ev('document.getElementById("comp5").click();true')
            until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
            inspect(width,'chain-numbered')
            for button,phase in [('zoomInBtn','zoom-in'),('zoomOutBtn','zoom-restored')]:
                ev('document.getElementById('+json.dumps(button)+').click();true');inspect(width,phase)
            # The supported font-refresh entry point preserves numbering;
            # fUpdateSVG alone rebuilds only the molecular drawing.
            ev('fRefreshFontDrawing2D();true');inspect(width,'font-refresh')
            if width==1500 and key=='aminobutanoic_acid_3':screenshot(HERE/'amino-calibration.png')
            print('controls',width,key,'passed',flush=True)
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
    out['javascriptErrors']=js_errors
    (HERE/'controls.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'jsErrors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
