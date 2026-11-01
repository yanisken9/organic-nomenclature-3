"""Actual Main controls: accepted layouts, no-C-C cases and compound labels."""
from pathlib import Path
import base64,runpy
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
T=runpy.run_path(str(HERE/'transform.py'));base=T['base'];probes=json.loads((HERE/'control-probes.json').read_text())
CONTROL_KEYS=list(base['accepted'])+['methanal','methanoicacid','hydroxypropanoic_acid_2',
                                      'aminobutanoic_acid_3','dihydroxybutanedioic_acid_2_3']
out={'cases':[],'models':[],'exports':[],'completed':False,'transientOverrides':False}
def inspect(width,phase):
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=audit(width,phase);row['calibration']=json.loads(ev(probes['scale_probe']))
    c=row['calibration'];assert c['calibrated']and len(c['fonts'])==1
    # Compare displayed ratios with authored drawing units, independently of
    # any native coordinate normalization in JSME's MOL exporter.
    mol=ev('window.MOL2D[selectedMol].expanded');_,aa,bb=T['parse'](mol)
    assert len(c['ratios'])==len(bb)
    for r,(a,b,o)in zip(c['ratios'],bb):
        expected=((aa[b][0]-aa[a][0])**2+(aa[b][1]-aa[a][1])**2)**.5/.6188*2.6175
        assert abs(r['ratio']-expected)<.013,(row['key'],a+1,b+1,r['ratio'],expected)
    row['ink']=json.loads(ev(probes['ink_probe']))
    assert not row['ink']['contacts']and not row['ink']['clippedNumbers'],row['ink']
    assert row['ink']['numberTexts']==[str(i+1)for i in range(row['ink']['expected'])]
    if row['key']=='aminobutanoic_acid_3':
        ratio=ev('(()=>{const t=fGetRenderedAtomTextMap(false,true)[allAtomsTypeList.indexOf("N")].node;return Number(t.querySelector("tspan[dy]").getAttribute("dy"))/parseFloat(t.getAttribute("font-size"))})()')
        assert abs(ratio-70/270)<.00001
        row['subscriptDyPerFont']=ratio
    out['cases'].append(row)
try:
    start('mulermoc-nom-52.html?audit=carbonyl-acid-controls')
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        ev('document.getElementById("rotatePromptDismiss")?.click();true')
        for key in CONTROL_KEYS:
            select_ui(key)
            until('mainChainPool3DKey==='+json.dumps(key))
            until('(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()')
            out['models'].append({'key':key,'width':width,'actualModelURLMatched':True})
            inspect(width,'selected')
            ev('document.getElementById("comp5").click();true')
            until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
            inspect(width,'chain-numbered')
            step_button=ev('(["chainPrevBtn","chainNextBtn"].find(id=>{const b=document.getElementById(id);return b&&!b.disabled}))||""')
            if step_button:
                previous=ev('mainChainPoolIdx')
                ev('document.getElementById('+json.dumps(step_button)+').click();true')
                assert ev('mainChainPoolIdx')!=previous
                until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
                assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
                inspect(width,'alternate-chain')
            for target,button in [(.5,'zoomOutBtn'),(6,'zoomInBtn')]:
                ev('for(let i=0;i<16;i++)document.getElementById('+json.dumps(button)+').click();true')
                assert ev('molZoom2D')==target;inspect(width,'zoom-'+str(target))
            ev('fRefreshFontDrawing2D();true');inspect(width,'font-refresh')
            if ev('!!document.getElementById("comp1")'):
                ev('document.getElementById("comp1").click();true')
                until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
                inspect(width,'prefix-highlight')
            for mode in ['condensed','skeletal','expanded']:
                index=['condensed','expanded','skeletal'].index(mode)
                ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
                assert ev('mode2D')==mode
                if mode=='expanded':
                    until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
                    inspect(width,'mode-return')
            if width==1500 and key in ['methanal','aminobutanoic_acid_3']:
                screenshot(HERE/(key+'-controls.png'))
            print('controls',width,key,'passed',flush=True)
    for key in ['ethyl_4_isopropyl_3_methyl_2_hexanal',
                'ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid','aminobutanoic_acid_3']:
        select_ui(key);ev('document.getElementById("comp5").click();true')
        until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
        ev('window.__png=null;window.__exportSvg=null;window.__nativeClick=HTMLAnchorElement.prototype.click;window.__nativeURL=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==="image/png")__png=b;if(b.type.startsWith("image/svg"))b.text().then(t=>__exportSvg=t);return __nativeURL.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById("save2DBtn").click();true')
        until('!!__png&&!!__exportSvg')
        assert ev('!new DOMParser().parseFromString(__exportSvg,"image/svg+xml").querySelector("parsererror")')
        raw=ev('new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(",")[1]);f.readAsDataURL(__png)})')
        (HERE/(key+'-export.png')).write_bytes(base64.b64decode(raw))
        out['exports'].append({'key':key,'PNGBytes':ev('__png.size'),'exportSVGParses':True})
        assert out['exports'][-1]['PNGBytes']>1000
        ev('HTMLAnchorElement.prototype.click=__nativeClick;URL.createObjectURL=__nativeURL;true')
    before=ev('document.getElementById("view3DBtn").classList.contains("active")')
    for expected in [not before,before]:
        ev('document.getElementById("view3DBtn").click();true')
        assert ev('document.getElementById("view3DBtn").classList.contains("active")')==expected
    for key in ['methane','propene','ethyne','butadiene_1_2','penten_3_yne_1',
                'isopropyl_4_dimethyl_3_5_heptanol_2','dimethylether','tert_butyl_isopropyl_ether']:
        select_ui(key);row=audit(390,'unchanged-category');out['cases'].append(row)
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'controls.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
