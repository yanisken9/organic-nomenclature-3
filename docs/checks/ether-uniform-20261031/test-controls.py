"""Expanded scale/clearance, actual naming/numbering/highlights, resize and PNG."""
from pathlib import Path
import base64
exec(compile(Path('docs/checks/ether-uniform-20261031/browser_support.py').read_text(),'support','exec'))
out={'cases':[],'exports':[],'models':[],'completed':False}
scale_probe='''JSON.stringify((()=>{
const svg=molSvg.node,ts=[...svg.querySelectorAll('text[data-namelecule-role="label"]')],font=parseFloat(getComputedStyle(ts[0]).fontSize);
const points=new Map(ts.map(t=>[Number(t.dataset.nameleculeAtom),{x:Number(t.dataset.fixedCCAtomX),y:Number(t.dataset.fixedCCAtomY)}]));
return {calibrated:!!svg.dataset.alkaneFixedCCScale,fonts:[...new Set(ts.map(t=>getComputedStyle(t).fontSize))],ratios:bondList.map(([a,b])=>({H:allAtomsTypeList[a-1]==='H'||allAtomsTypeList[b-1]==='H',ratio:Math.hypot(points.get(b).x-points.get(a).x,points.get(b).y-points.get(a).y)/font}))};
})())'''
ink_probe='''JSON.stringify((()=>{
const svg=molSvg.node,view=svg.getBoundingClientRect();
function ink(t){let b=NameleculeLabelMetrics.element(t),m=t.getScreenCTM();if(!b)return null;const p=new DOMPoint(b.left,b.top).matrixTransform(m),q=new DOMPoint(b.right,b.bottom).matrixTransform(m);return {l:p.x,t:p.y,r:q.x,b:q.y};}
let atoms=[...svg.querySelectorAll('text[data-namelecule-role="label"]')].map(ink),numbers=[...svg.querySelectorAll('text[id^=number]')],boxes=numbers.map(ink),contacts=0;
const overlaps=(a,b)=>a&&b&&Math.min(a.r,b.r)-Math.max(a.l,b.l)>.25&&Math.min(a.b,b.b)-Math.max(a.t,b.t)>.25;
for(let i=0;i<atoms.length;i++)for(let j=0;j<i;j++)if(overlaps(atoms[i],atoms[j]))contacts++;
for(const a of boxes)for(const b of atoms)if(overlaps(a,b))contacts++;
return {contacts,numberTexts:numbers.map(t=>t.textContent),expected:numberingFlag?numbersSVGElements.filter(Boolean).length:0,clippedNumbers:boxes.filter(b=>b&&(b.l<view.left-1||b.t<view.top-1||b.r>view.right+1||b.b>view.bottom+1)).length};
})())'''
def capture(width,phase):
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=audit(width,phase);row['calibration']=json.loads(ev(scale_probe));c=row['calibration']
    assert c['calibrated']and len(c['fonts'])==1
    assert all(abs(r['ratio']-(1.30875 if r['H']else 2.6175))<.013 for r in c['ratios']),c
    row['ink']=json.loads(ev(ink_probe));assert not row['ink']['contacts']and not row['ink']['clippedNumbers'],row['ink']
    out['cases'].append(row);return row
def click_component(comp,width):
    if not ev('!!document.getElementById('+json.dumps(comp)+')'):return
    ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(comp)+').click();true')
    until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
    row=capture(width,comp);assert row['ink']['numberTexts']==[str(i+1)for i in range(row['ink']['expected'])]
try:
    start('mulermoc-nom-52.html?audit=ether-controls')
    ev("window.__coloredEtherAtoms=()=>Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').filter(a=>a.color.toLowerCase()==='[xd8eedc]').map(a=>a.atomno).sort((a,b)=>a-b);window.__etherWithH=(cs)=>{const atoms=new Set(cs);for(const b of bondList3D){if(atoms.has(b[0])&&allAtomsTypeList3D[b[1]-1]==='H')atoms.add(b[1]);if(atoms.has(b[1])&&allAtomsTypeList3D[b[0]-1]==='H')atoms.add(b[0]);}return [...atoms].sort((a,b)=>a-b)}")
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        for key in KEYS:
            select_ui(key);until('mainChainPool3DKey==='+json.dumps(key))
            expected=ev('allAtomsTypeList.length');until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))==='+str(expected));out['models'].append({'key':key,'width':width,'atoms':expected})
            assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
            capture(width,'selected')
            for target,button in [(.5,'zoomOutBtn'),(6,'zoomInBtn')]:
                ev('for(let i=0;i<16;i++)document.getElementById('+json.dumps(button)+').click();true');assert ev('molZoom2D')==target;capture(width,'zoom-'+str(target))
            ev('for(let i=0;i<4;i++)document.getElementById("zoomOutBtn").click();true')
            # Use actual radio clicks; the name panel is rebuilt on each toggle.
            ev('document.querySelector("#radioEtherNaming [data-naming-mode=iupac]").click();true');assert ev('etherNamingMode')=='iupac'
            click_component('comp5',width);click_component('comp1',width)
            until("JSON.stringify(__coloredEtherAtoms())===JSON.stringify(__etherWithH([functionalGroupObj3D.ether.O[0]+1].concat(fGetEtherAlkoxyChain3D())))")
            ev('document.querySelector("#radioEtherNaming [data-naming-mode=common]").click();true');assert ev('etherNamingMode')=='common';capture(width,'common')
            parts=json.loads(ev('JSON.stringify(fGetEtherCommonParts().parts)'))
            for i,part in enumerate(parts):
                if part['kind']!='alkyl':continue
                click_component('comp'+str(10+i),width)
                until('JSON.stringify(__coloredEtherAtoms())===JSON.stringify(__etherWithH('+json.dumps(part['chain3D'])+'))')
            # A second redraw must keep the same molecule/graph and safe drawing.
            ev('fClearHighlights();fShowNameAnalysis();fUpdateSVG();true');capture(width,'redraw')
            if width==1500 and key in ['dimethylether','isopropyl_methyl_ether','tert_butyl_isopropyl_ether']:
                screenshot(HERE/(key+'-controls.png'))
            print('controls',width,key,'passed',flush=True)
    for key in ['dimethylether','isopropyl_methyl_ether','tert_butyl_isopropyl_ether']:
        select_ui(key);ev('window.__png=null;window.__nativeClick=HTMLAnchorElement.prototype.click;window.__nativeURL=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==="image/png")__png=b;return __nativeURL.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById("save2DBtn").click();true');until('!!__png')
        raw=ev('new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(",")[1]);f.readAsDataURL(__png)})');(HERE/(key+'-export.png')).write_bytes(base64.b64decode(raw));out['exports'].append({'key':key,'bytes':ev('__png.size')});assert out['exports'][-1]['bytes']>1000
        ev('HTMLAnchorElement.prototype.click=__nativeClick;URL.createObjectURL=__nativeURL;true')
    before=ev('document.getElementById("view3DBtn").classList.contains("active")');ev('document.getElementById("view3DBtn").click();true');assert ev('document.getElementById("view3DBtn").classList.contains("active")')!=before
    ev('document.getElementById("view3DBtn").click();true');assert ev('document.getElementById("view3DBtn").classList.contains("active")')==before
    # Existing classes still use their existing calibration and readable drawing.
    for key in ['methane','propene','ethyne','butadiene_1_2','penten_3_yne_1','isopropyl_4_dimethyl_3_5_heptanol_2']:
        select_ui(key);row=audit(390,'unrelated-category');out['cases'].append(row)
    out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'controls.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
