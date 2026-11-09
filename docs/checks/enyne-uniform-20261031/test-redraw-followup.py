"""Bounded diagnostic for one unreproduced strict SVG-serialization mismatch."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[3];TMP=Path('/tmp/namelecule-enyne-uniform-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8032/main/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'pairs':0,'differences':[],'completed':False}
try:
 navigate('mulermoc-nom-52.html?audit=seventh-redraw-followup');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)')
 for round in range(3):
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
   ev('document.getElementById("penten_3_yne_1").click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true')
   for target in [.5,6,2]:
    ev('molZoom2D='+str(target)+';fReapplyZoomScale2D();fShowNameAnalysis();document.getElementById("comp5").click();true')
    until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
    ev('document.getElementById("view2DBtn").click();document.getElementById("view2DBtn").click();fClearHighlights();true')
    result=json.loads(ev('JSON.stringify((()=>{let n=0;for(let i=0;i<10;i++){fUpdateSVG();const first=molSvg.node.outerHTML;fUpdateSVG();const second=molSvg.node.outerHTML;n++;if(first!==second)return {n,first,second};}return {n};})())'))
    out['pairs']+=result['n']
    if 'first'in result:out['differences'].append({'round':round,'width':width,'zoom':target,**result})
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors;(TMP/'redraw-followup.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'pairs':out['pairs'],'differences':len(out['differences']),'errors':len(js_errors)}),flush=True)
if not out['completed']or out['differences']or js_errors:raise SystemExit(1)
