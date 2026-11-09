"""Compare existing PNG framing before/after without changing Main sources."""
from pathlib import Path
import runpy,base64
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
T=runpy.run_path(str(HERE/'transform.py'));old=json.load(gzip.open(HERE/'before-sources.json.gz','rt'))
current=(ROOT/T['DATA']).read_text();view=(ROOT/'js/mulermoc-nom-molview-52.js').read_text()
def calibration(code):
    a=code.index('function fPrepareFixedCCAlkanePrototype()');b=code.index('function fGetUniform2DLibraryFrame()',a);return code[a:b]
out={'cases':[],'completed':False,'appCodeChanged':False}
try:
    start('mulermoc-nom-52.html?audit=export-framing-diagnostic')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':1000},'devicePixelRatio':1})
    ev('document.getElementById("rotatePromptDismiss")?.click();true')
    for phase,data,viewer in [('before',old[T['DATA']],old['js/mulermoc-nom-molview-52.js']),('after',current,view)]:
        ev('fPrepareFixedCCAlkanePrototype=('+calibration(viewer)+');true')
        for key in KEYS:
            mol=T['literal'](data,key)[1]
            ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=window.MOL2D['+json.dumps(key)+'].expanded='+json.dumps(mol)+';true')
        ev('uniform2DLibraryFrame=null;true')
        key='ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid'
        select_ui(key);ev('for(let i=0;i<16;i++)document.getElementById("zoomInBtn").click();document.getElementById("comp5").click();true')
        until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
        row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(phase=phase,zoom=ev('molZoom2D'))
        row['nameBoxesTotalWidthAtExport']=ev('(()=>{const c=document.createElement("canvas").getContext("2d");c.font="bold 40px Arial, sans-serif";const b=fGetNameBoxes();return b.reduce((s,v)=>s+c.measureText(v.text).width+36,0)-2*(b.length-1)})()')
        screenshot(HERE/('export-'+phase+'-live.png'))
        ev('window.__png=null;window.__exportSvg=null;window.__nativeClick=HTMLAnchorElement.prototype.click;window.__nativeURL=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==="image/png")__png=b;if(b.type.startsWith("image/svg"))b.text().then(t=>__exportSvg=t);return __nativeURL.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById("save2DBtn").click();true')
        until('!!__png&&!!__exportSvg')
        raw=ev('new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(",")[1]);f.readAsDataURL(__png)})')
        (HERE/('export-'+phase+'-diagnostic.png')).write_bytes(base64.b64decode(raw))
        (HERE/('export-'+phase+'-diagnostic.svg')).write_text(ev('__exportSvg'))
        row['exportSVGParses']=ev('!new DOMParser().parseFromString(__exportSvg,"image/svg+xml").querySelector("parsererror")')
        out['cases'].append(row)
        ev('HTMLAnchorElement.prototype.click=__nativeClick;URL.createObjectURL=__nativeURL;true')
    out['completed']=True
finally:save_result(out,'export-framing-diagnostic.json.gz')
