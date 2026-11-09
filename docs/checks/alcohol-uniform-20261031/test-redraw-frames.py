# -*- coding: utf-8 -*-
"""Measure the actual transforms of a recorded root-viewBox-only difference."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[3];TMP=Path('/tmp/namelecule-alcohol-uniform-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8032/main/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
try:
 navigate('mulermoc-nom-52.html?audit=alcohol-redraw-frames');app_ready();ev('document.fonts.ready.then(()=>true)')
 pair=json.load(gzip.open(TMP/'controls-16.json.gz','rt'))['idempotenceDifference']
 ev('window.__pair='+json.dumps(pair)+';true')
 out['recordedPair']=json.loads(ev('''JSON.stringify((()=>{
 const matrices=[],children=[];
 for(let i=0;i<2;i++){
  const div=document.createElement('div');div.style.cssText='position:fixed;left:'+(i*700)+'px;top:0;width:618px;height:287.16668701171875px;background:white';
  div.innerHTML=__pair[i?'second':'first'];document.body.append(div);
  const svg=div.querySelector('svg'),m=svg.getScreenCTM();
  matrices.push({a:m.a,b:m.b,c:m.c,d:m.d,e:m.e-i*700,f:m.f});children.push(svg.innerHTML);
 }
 const deltas=Object.keys(matrices[0]).map(k=>Math.abs(matrices[0][k]-matrices[1][k]));
 return {matrices,childrenIdentical:children[0]===children[1],maxEffectiveTransformDelta:Math.max(...deltas)};
})())'''))
 assert out['recordedPair']['childrenIdentical']and out['recordedPair']['maxEffectiveTransformDelta']<1e-7
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors;(TMP/'redraw-frame-comparison.json').write_text(json.dumps(out,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps(out),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
