"""Actual Main ester controls after approved integration."""
from pathlib import Path
import base64
HERE=Path(__file__).resolve().parent
exec(compile((HERE/'browser_support.py').read_text(),'support','exec'))
out={'cases':[],'models':[],'completed':False,'transientOverrides':False}
def inspect(width,phase):
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=audit(width,phase);assert ev('!!molSvg.node.dataset.alkaneFixedCCScale')
    out['cases'].append(row)
try:
    start('mulermoc-nom-52.html?audit=ester-main-controls')
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
            assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
            inspect(width,'numbered')
            step=ev('(["chainPrevBtn","chainNextBtn"].find(id=>{const b=document.getElementById(id);return b&&!b.disabled}))||""')
            if step:
                previous=ev('mainChainPoolIdx');ev('document.getElementById('+json.dumps(step)+').click();true')
                assert ev('mainChainPoolIdx')!=previous
                until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
                assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
                inspect(width,'alternate-chain')
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
            was3D=ev('document.getElementById("view3DBtn").classList.contains("active")')
            for expected in [not was3D,was3D]:
                ev('document.getElementById("view3DBtn").click();true')
                assert ev('document.getElementById("view3DBtn").classList.contains("active")')==expected
            screenshot(HERE/(key+'-controls-'+str(width)+'.png'))
            print('Controls passed',width,key,flush=True)
    for key in ['methyl_methanoate','isopropyl_2_3_dimethylbutanoate']:
        select_ui(key)
        ev('window.__png=null;window.__exportSvg=null;window.__nativeClick=HTMLAnchorElement.prototype.click;window.__nativeURL=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==="image/png")__png=b;if(b.type.startsWith("image/svg"))b.text().then(t=>__exportSvg=t);return __nativeURL.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById("save2DBtn").click();true')
        until('!!__png&&!!__exportSvg')
        assert ev('!new DOMParser().parseFromString(__exportSvg,"image/svg+xml").querySelector("parsererror")')
        raw=ev('new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(",")[1]);f.readAsDataURL(__png)})')
        (HERE/(key+'-export.png')).write_bytes(base64.b64decode(raw))
        out.setdefault('exports',[]).append({'key':key,'PNGBytes':ev('__png.size'),'exportSVGParses':True})
        assert out['exports'][-1]['PNGBytes']>1000
        ev('HTMLAnchorElement.prototype.click=__nativeClick;URL.createObjectURL=__nativeURL;true')
    for key in ['methane','propene','ethyne','butadiene_1_2','penten_3_yne_1',
                'isopropyl_4_dimethyl_3_5_heptanol_2','dimethylether','methanal','methanoicacid']:
        select_ui(key);out['cases'].append(audit(390,'unrelated-category'))
    out['completed']=True
except Exception as e:
    out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'controls.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
