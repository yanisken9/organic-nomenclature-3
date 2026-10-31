"""Actual missing-metric fallback, total-failure UI, cache and font invalidation."""
from pathlib import Path
import os,json,time,traceback,gzip
r=Path('/tmp/namelecule-svg-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
out={'checks':[],'completed':False}
try:
 navigate('main/mulermoc-nom-52.html?audit=metric-recovery');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((r/'final-svg-probe.js').read_text())
 ev('document.getElementById("propene").click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true')
 out['before']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
 ev('window.__measure=CanvasRenderingContext2D.prototype.measureText;CanvasRenderingContext2D.prototype.measureText=function(s){const m=__measure.call(this,s);return {width:m.width}};NameleculeLabelMetrics.invalidate();fReapplyZoomScale2D();true')
 assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')
 out['missingActualBounds']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));out['fallbackState']=json.loads(ev('JSON.stringify(NameleculeLabelMetrics.state)'));assert out['fallbackState']['rasterFallbacks']>0
 ev('CanvasRenderingContext2D.prototype.measureText=__measure;NameleculeLabelMetrics.invalidate();fReapplyZoomScale2D();true');out['restored']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
 # Force every glyph measurement unavailable, including SVG extent access.
 ev('window.__extent=SVGTextContentElement.prototype.getExtentOfChar;CanvasRenderingContext2D.prototype.measureText=function(){throw Error("injected unavailable measurement")};SVGTextContentElement.prototype.getExtentOfChar=function(){throw Error("injected unavailable SVG extent")};NameleculeLabelMetrics.invalidate();fReapplyZoomScale2D();true')
 out['totalFailure']=json.loads(ev('JSON.stringify({svg:!!document.querySelector("#jsmeNomeclatureSVG svg"),status:document.querySelector("#jsmeNomeclatureSVG [role=status]")?.textContent,key:selectedMol,name:currentMolName})'));assert not out['totalFailure']['svg'] and out['totalFailure']['status']
 # Export cannot emit a detached/obsolete drawing while the failure is displayed.
 ev('window.__downloaded=false;window.__click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){__downloaded=true};document.getElementById("save2DBtn").click();true');assert not ev('__downloaded')
 ev('CanvasRenderingContext2D.prototype.measureText=__measure;SVGTextContentElement.prototype.getExtentOfChar=__extent;HTMLAnchorElement.prototype.click=__click;NameleculeLabelMetrics.invalidate();fReapplyZoomScale2D();true');assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG [role=status]")')
 out['recovered']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
 # Explicit late font readiness signal must redraw the CURRENT molecule, not the old one.
 ev('document.getElementById("ethanol").click();window.__epoch=NameleculeLabelMetrics.state.epoch;document.fonts.dispatchEvent(new Event("loadingdone"));document.getElementById("pentanoic_acid").click();true');time.sleep(.4)
 assert ev('selectedMol==="pentanoic_acid"&&NameleculeLabelMetrics.state.epoch>__epoch&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
 out['fontRaceCurrent']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
 for k in ['before','restored','recovered','fontRaceCurrent']:
  assert out[k]['raster']['inkWithinHalfCssPixelOfBond']==0 and out[k]['raster']['fullyHiddenLineCount']==0 and not out[k]['clipped'],k
 # A missing service asset must not crash the native JSME producer either.
 ev('window.__service=NameleculeLabelMetrics;window.NameleculeLabelMetrics=undefined;fReapplyZoomScale2D();true');assert ev('!document.querySelector("#jsmeNomeclatureSVG svg")&&!!document.querySelector("#jsmeNomeclatureSVG [role=status]")')
 ev('window.NameleculeLabelMetrics=__service;NameleculeLabelMetrics.invalidate();fReapplyZoomScale2D();true');assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')
 out['checks']=['missing actualBoundingBox uses raster fallback without exception','all metrics unavailable clears drawing and provides status, no stale PNG','restoration redraws current model','font epoch invalidation/current-molecule redraw'];out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'recovery.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('recovery',out['completed'],'errors',len(js_errors),flush=True)
