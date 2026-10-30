"""ACV2-R1: all8 at minimum zoom;3affected at intermediate/default, two widths."""
from pathlib import Path
source=Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text()
exec(compile(source.split('\ntry:\n navigate')[0],'clearance-test-setup','exec'))
result={'completed':False,'cases':[],'finding':'ACV2-R1'}
try:
 navigate('mulermoc-nom-52.html?v=targeted-zoom-review');app_ready();ev('document.fonts.ready.then(()=>true)');ev(install)
 keys=data('Object.keys(MOL2D).filter(k=>nameExamples[k]?.classification?.seriesKey==="alkanes")');assert len(keys)==8
 branched={'ethyl_3_dimethyl_2_5_hexane','methyl_2_pentane','dimethyl_2_3_butane'}
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in keys:
   ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();fClearHighlights();true')
   for zoom in ([0.5,1,2]if key in branched else[0.5]):
    ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
    row=json.loads(ev('(()=>{const z=molZoom2D,f=molSvg.node.dataset.uniformAtomFontPixels;return __endpointCheck().then(r=>JSON.stringify({...r,snapshotZoom:z,targetFontPixels:f}))})()'))
    row.update(key=key,width=width,absoluteZoom=zoom)
    assert row['snapshotZoom']==zoom and not row['clipped']and not row['overlaps'],row
    for b in row['checks']:
     assert b['visibleLength']>1 and all(e['gap']>.2 and e['rasterClear']for e in b['endpoints']),(key,width,zoom,b)
    assert ev('(()=>{fPadExpandedAlkaneLabels();const a=__read().svg;fPadExpandedAlkaneLabels();return a===__read().svg})()')
    result['cases'].append(row)
   print(key,width,'PASS',flush=True)
 assert not js_errors,js_errors
 result['completed']=True
except Exception as error:
 result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors
 (args.output/'targeted-zoom.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases'])}),flush=True)
if not result['completed']:raise SystemExit(1)
