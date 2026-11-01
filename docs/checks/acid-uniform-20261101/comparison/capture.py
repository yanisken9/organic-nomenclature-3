"""Capture preview-only MOLs with actual Main renderer in an isolated tab.

Transient MOL/function overrides exist only in this disposable browser context.
No Main source, scenario, SDF or core file is written.
"""
from pathlib import Path
import os,json,gzip,traceback,runpy
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
KEYS=runpy.run_path(str(HERE/'prepare.py'))['CAPTURE_KEYS']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'cases':[],'completed':False,'previewOnly':True}
measure=r'''JSON.stringify((()=>{
 const svg=molSvg.node,rootInverse=svg.getScreenCTM().inverse(),lines=[...svg.querySelectorAll('line')],anchors=new Map();
 function point(node,x,y){return new DOMPoint(x,y).matrixTransform(rootInverse.multiply(node.getScreenCTM()));}
 for(let i=0;i<bondList.length;i++){
  const[a,b,o]=bondList[i],ls=lines.slice(svgBondList[i]-1,svgBondList[i]-1+o);if(ls.length!==o)throw Error('Missing native strokes');
  if(o===3)continue;
  const p=ls.map(l=>point(l,Number(l.getAttribute('x1')),Number(l.getAttribute('y1')))),q=ls.map(l=>point(l,Number(l.getAttribute('x2')),Number(l.getAttribute('y2'))));
  for(const[id,ps]of[[a,p],[b,q]]){
   const c={x:ps.reduce((s,v)=>s+v.x,0)/ps.length,y:ps.reduce((s,v)=>s+v.y,0)/ps.length};
   if(o===1||!anchors.has(id))anchors.set(id,c);
  }
 }
 const first=anchors.get(mainChainAtomsList[0]),last=anchors.get(mainChainAtomsList.at(-1));if(!first||!last)throw Error('Parent endpoints unavailable');
 const cx=(first.x+last.x)/2,cy=(first.y+last.y)/2,label=svg.querySelector('text[data-namelecule-role="label"]'),lm=rootInverse.multiply(label.getScreenCTM());
 const fontRoot=parseFloat(getComputedStyle(label).fontSize)*Math.hypot(lm.a,lm.b);
 let left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity;
 for(const n of svg.querySelectorAll('line,text')){
  if(getComputedStyle(n).display==='none')continue;const b=n.getBBox();
  for(const[x,y]of[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]){
   const p=point(n,x,y);left=Math.min(left,(p.x-cx)/fontRoot);right=Math.max(right,(p.x-cx)/fontRoot);top=Math.min(top,(p.y-cy)/fontRoot);bottom=Math.max(bottom,(p.y-cy)/fontRoot);
  }
 }
 const clone=svg.cloneNode(true),nodes=[svg,...svg.querySelectorAll('*')],copies=[clone,...clone.querySelectorAll('*')];
 for(let i=0;i<nodes.length;i++){
  const style=getComputedStyle(nodes[i]);for(const p of ['font-family','font-size','font-weight','font-style','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity'])copies[i].style.setProperty(p,style.getPropertyValue(p));
 }
 return {rawSVG:clone.outerHTML,fontRoot,cx,cy,bounds:{left,right,top,bottom},name:currentMolName,chain:mainChainAtomsList.slice(),atomSymbols:allAtomsTypeList.slice(),bondGraph:bondList.map(b=>b.slice()),calibrated:!!svg.dataset.alkaneFixedCCScale};
})())'''
try:
 navigate('mulermoc-nom-52.html?audit=acid-isolated-preview');app_ready();until('window.JSmolReadyFlag===true')
 ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for molecule in KEYS:
   for variant in (['before','proposed']if width==1500 else ['proposed']):
    calibration=(HERE/('original-calibration.js'if variant=='before'else'preview-calibration.js')).read_text()
    ev('fPrepareFixedCCAlkanePrototype=('+calibration+');true')
    mol=(HERE/(molecule+'-'+variant+'.mol')).read_text()
    ev('nameExamples['+json.dumps(molecule)+'].structure2D_Expanded=window.MOL2D['+json.dumps(molecule)+'].expanded='+json.dumps(mol)+';selectedMol='+json.dumps(molecule)+';mode2D="expanded";nameAnalysisMode="none";fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),(molecule,variant)
    row=json.loads(ev(measure));row.update(key=molecule,variant=variant,width=width)
    if variant=='proposed':assert row['calibrated'],('Acid calibration guard rejected drawing',molecule)
    row['audit']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
    assert not row['audit']['clipped']and not row['audit']['raster']['inkWithinHalfCssPixelOfBond']and not row['audit']['raster']['fullyHiddenLineCount'],(molecule,variant,width)
    out['cases'].append(row);print('captured',molecule,variant,width,flush=True)
 for molecule in KEYS:
  rows=[c for c in out['cases']if c['key']==molecule]
  assert all(c['name']==rows[0]['name']and c['chain']==rows[0]['chain']and c['atomSymbols']==rows[0]['atomSymbols']and c['bondGraph']==rows[0]['bondGraph']for c in rows)
 out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/'browser.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'jsErrors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
