"""Read-only runtime tracing, with baseline data/functions in an isolated tab."""
from pathlib import Path
import os,json,runpy,traceback
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
mod=runpy.run_path(str(HERE/'transform.py'));source=ROOT/'communication/checkpoints/alcohol-uniform-20261031/original'
before=(source/'js/mulermoc-nom-molview-52.js').read_text();after=(ROOT/'js/mulermoc-nom-molview-52.js').read_text()
def section(code,start,end):return code[code.index(start):code.index(end,code.index(start))].strip()
prep=section(before,'function fPrepareFixedCCAlkanePrototype()', 'function fGetUniform2DLibraryFrame()')
fitStart='function fFit2DSVG()';fitEnd='// JSME labels collinear sp carbons'
assert section(before,fitStart,fitEnd)==section(after,fitStart,fitEnd)
oldCode=(source/mod['DATA']).read_text();originals={k:mod['literal'](oldCode,k)[1]for k in mod['KEYS']}
out={'completed':False,'fitFunctionByteIdenticalBeforeAfter':True,'cases':[]}
try:
 for version in ['before-alcohols','after-alcohols']:
  navigate('mulermoc-nom-52.html?audit=fit-baseline-'+version);app_ready();ev('document.fonts.ready.then(()=>true)')
  if version=='before-alcohols':
   ev('fPrepareFixedCCAlkanePrototype=('+prep+');window.__oldMols='+json.dumps(originals)+';for(const[k,m]of Object.entries(__oldMols)){nameExamples[k].structure2D_Expanded=window.MOL2D[k].expanded=m;}uniform2DLibraryFrame=null;true')
  ev("window.__fits=[];window.__nativeFit=fFit2DSVG;\nfunction measureFit(){const s=document.querySelector('#jsmeNomeclatureSVG svg'),p=s.parentNode.getBoundingClientRect(),m=s.getCTM();return {parent:[p.width,p.height],styles:[s.style.width,s.style.height],viewBox:s.getAttribute('viewBox'),matrix:[m.a,m.d,m.e,m.f],svgSize:[s.getBoundingClientRect().width,s.getBoundingClientRect().height]};}\nfFit2DSVG=function(){const b=measureFit();__nativeFit();__fits.push({before:b,after:measureFit()});};true")
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
   ev('selectedMol="propanol_1";mode2D="expanded";fInitProps();fLoadMol2D();fShowNameAnalysis();true')
   states=[]
   for i in range(4):
    ev('window.__fits=[];fClearHighlights();fUpdateSVG();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    states.append(json.loads(ev('JSON.stringify({fits:__fits,settled:measureFit(),children:molSvg.node.innerHTML})')))
   out['cases'].append({'version':version,'width':width,'redraws':states})
 out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc())
finally:
 out['javascriptErrors']=js_errors;(HERE/'fit-baseline-trace.json').write_text(json.dumps(out,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'errors':len(js_errors)}))
if not out['completed']or js_errors:raise SystemExit(1)
