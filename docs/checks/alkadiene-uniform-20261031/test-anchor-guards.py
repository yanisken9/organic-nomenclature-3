"""Exercise new missing-center recognition on attached transient SVG clones.

No saved MOL is changed. Invalid native stroke pairs must leave the drawing
untouched; no partial label calibration may escape a failed validation.
"""
from pathlib import Path
import os,json,traceback
ROOT=Path(__file__).resolve().parents[3];TMP=Path('/tmp/namelecule-alkadiene-uniform-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8032/main/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
try:
 navigate('mulermoc-nom-52.html?audit=cumulene-guards');app_ready();until('window.JSmolReadyFlag===true')
 ev('selectedMol="propadiene";mode2D="expanded";fInitProps();fLoadMol2D();fClearHighlights();window.__prep=fPrepareFixedCCAlkanePrototype;fPrepareFixedCCAlkanePrototype=function(){window.__nativeSVG=molSvg.node.outerHTML;return __prep()};try{fUpdateSVG()}finally{fPrepareFixedCCAlkanePrototype=__prep};true')
 out['cases']=json.loads(ev('''JSON.stringify((()=>{
 const active=molSvg,activeBefore=active.node.outerHTML,host=document.createElement('div');
 host.style.cssText='position:absolute;left:-100000px;top:0;opacity:0;pointer-events:none';document.getElementById('jsmeNomeclatureSVG').appendChild(host);
 const cases=[];
 try {
  for(const kind of ['valid','unequal-length','shifted-pair','reversed-stroke']){
   host.innerHTML=__nativeSVG;const svg=host.querySelector('svg'),lines=svg.querySelectorAll('line');
   if(kind==='unequal-length')lines[0].setAttribute('x2',Number(lines[0].getAttribute('x2'))+20);
   if(kind==='shifted-pair')for(const l of [lines[0],lines[1]])for(const a of ['x1','x2'])l.setAttribute(a,Number(l.getAttribute(a))+20);
   if(kind==='reversed-stroke')for(const [a,b]of [['x1','x2'],['y1','y2']]){const x=lines[0].getAttribute(a);lines[0].setAttribute(a,lines[0].getAttribute(b));lines[0].setAttribute(b,x)}
   const before=svg.outerHTML;molSvg=MuSVG(svg);fPrepareFixedCCAlkanePrototype();
   cases.push({kind,calibrated:!!svg.dataset.alkaneFixedCCScale,unchanged:svg.outerHTML===before});
  }
 }finally{molSvg=active;host.remove()}
 return {cases,activeDrawingUnchanged:active.node.outerHTML===activeBefore};
})())'''))
 result=out['cases'];assert result['activeDrawingUnchanged'];assert result['cases'][0]['calibrated']
 assert all(not c['calibrated']and c['unchanged']for c in result['cases'][1:])
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(TMP/'anchor-guards.json').write_text(json.dumps(out,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps(out),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
