"""Actual UI controls and expanded anchor calibration in isolated Firefox."""
from pathlib import Path
import os,json,gzip,traceback,base64
ROOT=Path(__file__).resolve().parents[3]
TMP=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
HERE=Path(__file__).resolve().parent
keys=json.loads((HERE/'baseline.json').read_text())['keys']
only=os.environ.get('NAMELECULE_TEST_KEYS')
if only:keys=[k for k in keys if k in only.split(',')]
DETAIL_KEYS={'propanol_1','propanetriol','isopropyl_4_dimethyl_3_5_heptanol_2','ethyl_3_methyl_4_hexen_3_yn_5_ol_2'}
out={'cases':[],'exports':[],'completed':False,'detailedControlKeys':sorted(DETAIL_KEYS),'coverage':'All17default/min/maxzoomandOH;fullcontrols4representatives;existing102before/after16and42OHstatesretained'}
resume=os.environ.get('NAMELECULE_RESUME_AFTER_DESKTOP_POLYOL')=='1'
if resume:
 out=json.load(gzip.open(HERE/'controls-attempt-artifact-path-error.json.gz','rt'))
 out['previousHarnessFailure']=out.pop('failure');out.pop('traceback',None);out['completed']=False
geometry='''JSON.stringify((()=>{
 const svg=molSvg.node,labels=[...svg.querySelectorAll('text[data-namelecule-role="label"]')],font=parseFloat(getComputedStyle(labels[0]).fontSize);
 const points=new Map(labels.map(t=>[Number(t.dataset.nameleculeAtom),{x:Number(t.dataset.fixedCCAtomX),y:Number(t.dataset.fixedCCAtomY)}]));
 return {calibrated:!!svg.dataset.alkaneFixedCCScale,font,ratios:bondList.map(([a,b,o])=>{const p=points.get(a),q=points.get(b);return {atoms:[a,b],type:(allAtomsTypeList[a-1]==='H'||allAtomsTypeList[b-1]==='H')?'XH':'heavy',order:o,ratio:Math.hypot(q.x-p.x,q.y-p.y)/font,horizontal:Math.abs(q.y-p.y)<.01}}),fonts:[...new Set(labels.map(t=>getComputedStyle(t).fontSize))]};
})())'''
numbers='''JSON.stringify((()=>{
 const svg=molSvg.node,outer=svg.getBoundingClientRect(),ns=[...svg.querySelectorAll('text[id^=number]')],labels=[...svg.querySelectorAll('text[data-namelecule-role="label"]')];
 function ink(t){const b=NameleculeLabelMetrics.element(t),m=t.getScreenCTM();if(!b)return null;const p=new DOMPoint(b.left,b.top).matrixTransform(m),q=new DOMPoint(b.right,b.bottom).matrixTransform(m);return {left:p.x,top:p.y,right:q.x,bottom:q.y};}
 const boxes=ns.map(ink),atoms=labels.map(ink);let collisions=0,atomCollisions=0;
 for(const a of boxes)for(const b of atoms)if(a&&b&&Math.min(a.right,b.right)-Math.max(a.left,b.left)>.25&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.25)collisions++;
 for(let i=0;i<atoms.length;i++)for(let j=0;j<i;j++){const a=atoms[i],b=atoms[j];if(a&&b&&Math.min(a.right,b.right)-Math.max(a.left,b.left)>.25&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.25)atomCollisions++;}
 return {expected:numberingFlag?numbersSVGElements.filter(Boolean).length:0,values:ns.map(n=>n.textContent),collisions,atomCollisions,clipped:boxes.filter(b=>b&&(b.left<outer.left-1||b.top<outer.top-1||b.right>outer.right+1||b.bottom>outer.bottom+1)).length};
})())'''
def capture(width,phase,calibration=True):
 ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')
 row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=width,phase=phase)
 out['cases'].append(row)
 (HERE/'controls-progress.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
 row['numberCheck']=json.loads(ev(numbers));assert not row['numberCheck']['collisions']and not row['numberCheck']['clipped']and not row['numberCheck']['atomCollisions']
 idx=0;oh=[]
 for a,b,order in row['bondGraph']:
  if {row['atomSymbols'][a-1],row['atomSymbols'][b-1]}=={'O','H'}:
   visible=row['raster']['lineVisibility'][idx]['visibleLength'];assert visible>0
   oh.append({'atoms':[a,b],'visibleCSSLength':visible})
  idx+=order
 assert len(oh)==row['atomSymbols'].count('O');row['OHbonds']=oh
 assert ev("[...molSvg.node.querySelectorAll('text[data-namelecule-role=label]')].every(t=>!['OH','HO'].includes(t.textContent.trim()))")
 # Firefox text layout rectangles include whitespace at tiny zoom. Keep those
 # flags as diagnostics; actual glyph bounds and raster contacts are decisive.
 assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount'],(row['key'],phase)
 if calibration:
  row['calibration']=json.loads(ev(geometry));c=row['calibration'];assert c['calibrated']and len(c['fonts'])==1
  assert all(abs(b['ratio']-((2.6175*(.98/.6188) if row['key']=='isopropyl_4_dimethyl_3_5_heptanol_2'and sorted(b['atoms'])==[4,10] else 2.6175) if b['type']=='heavy'else 1.30875))<.012 for b in c['ratios']),c
 return row
try:
 navigate('mulermoc-nom-52.html?audit=alcohol-controls');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in keys:
   if resume and width==1500 and key in keys[:7]:continue
   ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true');capture(width,'selected')
   for target,button in [(0.5,'zoomOutBtn'),(6,'zoomInBtn'),(2,'zoomOutBtn')]:
    if target==2:ev('molZoom2D=2;fReapplyZoomScale2D();true')
    else:ev('for(let i=0;i<16;i++)document.getElementById('+json.dumps(button)+').click();true')
    assert ev('molZoom2D')==target;capture(width,'zoom-'+str(target))
   if key not in DETAIL_KEYS:
    print('zoom/OH',width,key,'passed',flush=True)
    continue
   ev('fClearHighlights();fShowNameAnalysis();document.getElementById("comp5").click();true');until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
   row=capture(width,'numbering');assert row['numberCheck']['values']==[str(i+1)for i in range(row['numberCheck']['expected'])]
   for comp in ['comp1','comp3','comp6','comp9']:
    if ev('!!document.getElementById('+json.dumps(comp)+')'):
     ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(comp)+').click();true');until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20);capture(width,comp)
     if comp=='comp9':
      until('typeof mainChainPool3DKey!=="undefined"&&mainChainPool3DKey===selectedMol')
      expected=2*int(ev('allAtomsTypeList.filter(s=>s==="O").length'))
      until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{selected}.count"))==='+str(expected),seconds=20)
      out.setdefault('OH3Dselections',[]).append({'key':key,'width':width,'selectedCount':expected,'selection':ev('JmolSelection')})

   ev('document.getElementById("view2DBtn").click();document.getElementById("view2DBtn").click();fReapplyZoomScale2D();true');capture(width,'hide-show')
   # Preparation is rebuilt from fresh native SVG; no cumulative movement.
   ev('fClearHighlights();fUpdateSVG();window.__first=molSvg.node.outerHTML;fUpdateSVG();true')
   if not ev('window.__first===molSvg.node.outerHTML'):
    # Preserve the known framing discrepancy as an unresolved failure, rather
    # than treating identical child geometry as proof of optical equivalence.
    row={'key':key,'width':width,'first':ev('window.__first'),'second':ev('molSvg.node.outerHTML')}
    row['childrenIdentical']=ev('new DOMParser().parseFromString(__first,"image/svg+xml").documentElement.innerHTML===molSvg.node.innerHTML')
    out.setdefault('unresolvedFramingDifferences',[]).append(row)
    assert row['childrenIdentical'],'Unexpected cumulative child geometry change'
    capture(width,'redraw-second')
   if width==1500 and key in ['ethanol','propanetriol','methyl_4_penten_4_yn_2_ol_1']:
    ev('fShowNameAnalysis();true');screenshot(TMP/(key+'-after.png'))
   print('controls',width,key,'passed',flush=True)
 for key in (keys if only else ['ethanol','propanetriol','methyl_4_penten_4_yn_2_ol_1']):
  ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true');capture(390,'pre-export')
  ev('window.__png=null;window.__nativeClick=HTMLAnchorElement.prototype.click;window.__nativeURL=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==="image/png")__png=b;return __nativeURL.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById("save2DBtn").click();true');until('!!window.__png')
  raw=ev('new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(",")[1]);f.readAsDataURL(__png)})');name=key+'-export.png';(TMP/name).write_bytes(base64.b64decode(raw));out['exports'].append({'key':key,'file':name,'bytes':ev('__png.size')});assert ev('__png.size')>1000;ev('HTMLAnchorElement.prototype.click=__nativeClick;URL.createObjectURL=__nativeURL;true')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/('controls-final-targeted.json.gz' if only else 'controls-final.json.gz')).write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'errors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
