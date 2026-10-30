"""Bounded comparison of a pre-existing repeated-fit oscillation, old/new masks."""
from pathlib import Path
source=Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text()
exec(compile(source.split('\ntry:\n navigate')[0],'clearance-test-setup','exec'))
result={'completed':False,'traces':{}}
try:
 navigate('mulermoc-nom-52.html?v=fit-comparison');app_ready();ev('document.fonts.ready.then(()=>true)');ev(install);ev('window.__padBefore=('+old+');true')
 for fn in ['__padBefore','__padAfter']:
  ev("selectedMol='ethyl_3_dimethyl_2_5_hexane';mode2D='expanded';__render("+fn+");fShowNameAnalysis();document.getElementById('comp1').click();molZoom2D=MOL_ZOOM_DEFAULT*1.25;fReapplyZoomScale2D();fClearHighlights();true")
  result['traces'][fn]=[ev("fFit2DSVG();molSvg.node.getAttribute('viewBox')")for _ in range(5)]
 assert result['traces']['__padBefore']==result['traces']['__padAfter'],result
 result['completed']=True
 result['interpretation']='Repeated full-fit oscillation is pre-existing and identical; glyph masks do not cause it. Not fixed by this scoped task.'
finally:
 result['javascriptErrors']=js_errors
 (args.output/'fit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps(result),flush=True)
if not result['completed']:raise SystemExit(1)
