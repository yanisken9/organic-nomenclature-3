# -*- coding: utf-8 -*-
"""Render three preview-only MOLs in an isolated tab; never writes app sources."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
key='isopropyl_4_dimethyl_3_5_heptanol_2';out={'cases':[],'completed':False}
measure='''JSON.stringify((()=>{
 const svg=molSvg.node,inv=svg.getCTM().inverse(),lines=[...svg.querySelectorAll('line')],anchors=new Map();
 const g=svg.querySelector('g'),gm=g.transform.baseVal.consolidate().matrix;
 if(gm.b||gm.c||gm.e||gm.f||gm.a!==gm.d)throw Error('Unsupported native SVG transform');
 function rootPoint(node,x,y){return {x:x*gm.a,y:y*gm.d};}
 for(let i=0;i<bondList.length;i++){
  const [a,b,o]=bondList[i];if(o!==1)throw Error('Unexpected multiple bond');
  const l=lines[svgBondList[i]-1];
  anchors.set(a,rootPoint(l,Number(l.getAttribute('x1')),Number(l.getAttribute('y1'))));
  anchors.set(b,rootPoint(l,Number(l.getAttribute('x2')),Number(l.getAttribute('y2'))));
 }
 const label=svg.querySelector('text[data-namelecule-role=label]');
 const fontRoot=parseFloat(label.getAttribute('font-size'))*gm.a;
 const cx=(anchors.get(1).x+anchors.get(7).x)/2,cy=anchors.get(4).y;
 let left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity;
 for(const n of svg.querySelectorAll('line,text')){
  const b=n.getBBox();for(const [x,y]of[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]){
   const p=rootPoint(n,x,y);left=Math.min(left,(p.x-cx)/fontRoot);right=Math.max(right,(p.x-cx)/fontRoot);top=Math.min(top,(p.y-cy)/fontRoot);bottom=Math.max(bottom,(p.y-cy)/fontRoot);
  }
 }
 const stem=bondList.findIndex(([a,b])=>(a===4&&b===10)||(a===10&&b===4));
 lines[svgBondList[stem]-1].setAttribute('stroke','#a45f36');
 const point=anchors.get(20);
 return {rawSVG:svg.outerHTML,fontRoot,cx,cy,bounds:{left,right,top,bottom},collisionPoint:{x:(point.x-cx)/fontRoot,y:(point.y-cy)/fontRoot},nativeStemUnits:Math.hypot(anchors.get(4).x-anchors.get(10).x,anchors.get(4).y-anchors.get(10).y)/Math.hypot(anchors.get(1).x-anchors.get(2).x,anchors.get(1).y-anchors.get(2).y),nativeHSeparationUnits:Math.hypot(anchors.get(20).x-anchors.get(36).x,anchors.get(20).y-anchors.get(36).y)/Math.hypot(anchors.get(1).x-anchors.get(2).x,anchors.get(1).y-anchors.get(2).y),nativeAtomCount:allAtomsTypeList.length,name:currentMolName,calibrated:!!svg.dataset.alkaneFixedCCScale};
})())'''
try:
 navigate('mulermoc-nom-52.html?audit=alcohol-stem-preview');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
 for name in ['current','equal-invalid','proposed']:
  if name!='current':ev('fPrepareFixedCCAlkanePrototype=('+ (HERE/'preview-only-calibration.js').read_text()+');true')
  ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=window.MOL2D['+json.dumps(key)+'].expanded='+json.dumps((HERE/(name+'.mol')).read_text())+';selectedMol='+json.dumps(key)+';mode2D="expanded";fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
  assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),name
  row=json.loads(ev(measure));row['case']=name;assert row['nativeAtomCount']==39
  assert abs(row['nativeStemUnits']-({'current':2,'equal-invalid':1,'proposed':(.98/.6188)}[name]))<.003
  if name=='equal-invalid':assert row['nativeHSeparationUnits']<.001
  if name=='proposed':
   assert abs(row['nativeHSeparationUnits']-(.3612/.6188))<.003
   row['audit']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));assert not row['audit']['clipped']and not row['audit']['raster']['inkWithinHalfCssPixelOfBond']and not row['audit']['raster']['fullyHiddenLineCount']
  out['cases'].append(row);print('Captured',name,flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/'browser.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'errors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
