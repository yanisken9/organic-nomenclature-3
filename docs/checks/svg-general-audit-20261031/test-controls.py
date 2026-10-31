"""Bounded real controls/numbering/highlight/resize/export checks, before/after."""
from pathlib import Path
import os,json,gzip,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
out={'cases':[],'exports':[],'radiusDiagnostics':[],'completed':False}
choices=[('propene','expanded'),('dimethyl_2_3_butane','expanded'),('ethanenitrile','condensed'),('nitroethane','skeletal'),('ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid','expanded')]
def measure(version,width,phase):
 row=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'));row.update(version=version,width=width,phase=phase,analysisMode=ev('nameAnalysisMode'),expectedNumbers=ev('numberingFlag?numbersSVGElements.length:0'));out['cases'].append(row);return row
try:
 for version in ['baseline','candidate']:
  before=len(js_errors);navigate('app-'+version+'/mulermoc-nom-52.html?audit=controls');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((here/'final-svg-probe.js').read_text())
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
   for key,mode in choices:
    ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")['+str(['condensed','expanded','skeletal'].index(mode))+'].click();fShowNameAnalysis();true')
    until('selectedMol==='+json.dumps(key)+'&&mode2D==='+json.dumps(mode)+'&&mainChainPool3DKey==='+json.dumps(key),seconds=30)
    # Real zoom buttons move between default and neighboring settings.
    measure(version,width,'selected')
    for button in ['zoomInBtn','zoomOutBtn']:
     ev('document.getElementById('+json.dumps(button)+').click();true');measure(version,width,button)
    ev('document.getElementById("comp5").click();true');until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",seconds=20)
    measure(version,width,'numbering')
    # Click an available branch/group component, with the real event handler.
    comp=ev('Array.from(document.querySelectorAll(".nameCompBox")).find(e=>["comp1","comp6","comp9"].includes(e.id))?.id||null')
    if comp:
     ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(comp)+').click();true');measure(version,width,'highlight-'+comp)
    ev('document.getElementById("view2DBtn").click();document.getElementById("view2DBtn").click();fReapplyZoomScale2D();true');measure(version,width,'hide-show-2D')
    print(version,width,key,'controls done',flush=True)
  ev('fClearHighlights();fShowNameAnalysis();true')
  # Export interception prevents downloads; it does not replace the export code.
  ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;window.__anchorClick=HTMLAnchorElement.prototype.click;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
  until('!!window.__png&&!!window.__exportSvg',seconds=30)
  exp=json.loads(ev('JSON.stringify({bytes:__png.size,mime:__png.type,validSVG:!new DOMParser().parseFromString(__exportSvg,"image/svg+xml").querySelector("parsererror")})'));exp.update(version=version,javascriptErrorsSinceStart=len(js_errors)-before);out['exports'].append(exp)
  ev('HTMLAnchorElement.prototype.click=__anchorClick;URL.createObjectURL=__create;true')
  # Diagnostic only: whether native rounded corners contribute after the viewer
  # rewrites CHn. This changes a temporary DOM, never a source/fix recommendation.
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
  for key in ['ethanenitrile','ethanal']:
   ev('selectedMol='+json.dumps(key)+';mode2D="condensed";fInitProps();fLoadMol2D();true')
   a=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'))
   ev('for(const r of Object.values(fGetRenderedAtomRectMap(false,true))){r.attr({rx:0,ry:0})};true')
   b=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'));out['radiusDiagnostics'].append({'version':version,'key':key,'before':a,'squareDiagnostic':b})
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'controls.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('controls completed',out['completed'],'rows',len(out['cases']),'errors',len(js_errors),flush=True)
