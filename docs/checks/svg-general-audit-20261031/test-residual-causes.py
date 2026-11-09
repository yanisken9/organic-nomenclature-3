"""Read-only-source causal diagnostics. DOM counterfactuals are not proposed fixes."""
from pathlib import Path
import os,json,gzip,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
out={'collector':[],'acidBounds':[],'dpr2':[],'completed':False}
measure=lambda:json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'))
try:
 for version in ['baseline','candidate']:
  navigate('app-'+version+'/mulermoc-nom-52.html?audit=residual-causes');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((here/'final-svg-probe.js').read_text())
  ev('window.__collectorOriginal=fCollectHighlightRectsNearText;window.__collectorTrace=[];window.__protectMask=false;fCollectHighlightRectsNearText=function(texts){const mask=fGetRenderedAtomRectMap(true,true)[8]?.node,rs=__collectorOriginal(texts);__collectorTrace.push({removedTexts:texts.map(t=>t.node.textContent),protectedCarbonIndex:9,protectedRect:mask?mask.outerHTML:null,collectorIncludesC9:rs.some(r=>r.node===mask)});return __protectMask?rs.filter(r=>r.node!==mask):rs};selectedMol="ethyl_4_isopropyl_3_methyl_2_hexanal";mode2D="condensed";fInitProps();fLoadMol2D();true')
  before=measure();ev('window.__protectMask=true;fInitProps();fLoadMol2D();true');after=measure()
  out['collector'].append({'version':version,'trace':json.loads(ev('JSON.stringify(__collectorTrace)')),'before':before,'diagnosticPreserveC9Mask':after})
  ev('fCollectHighlightRectsNearText=__collectorOriginal;selectedMol="pentanoic_acid";mode2D="condensed";fInitProps();fLoadMol2D();true')
  before=measure()
  details=json.loads(ev('JSON.stringify((()=>{const r=[...molSvg.node.querySelectorAll("rect")];if(r.length!==5)throw Error("Unexpected acid layout");const out=[],ctx=document.createElement("canvas").getContext("2d");for(const [id,i]of[["C4",3],["C5",4]]){const t=document.getElementById(id),walk=document.createTreeWalker(t,NodeFilter.SHOW_TEXT);let n,k=0,left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity;while(n=walk.nextNode()){let s=getComputedStyle(n.parentElement);ctx.font=s.fontStyle+" "+s.fontWeight+" "+s.fontSize+" "+s.fontFamily;for(const ch of n.textContent){let p=t.getStartPositionOfChar(k++),m=ctx.measureText(ch);left=Math.min(left,p.x-m.actualBoundingBoxLeft);right=Math.max(right,p.x+m.actualBoundingBoxRight);top=Math.min(top,p.y-m.actualBoundingBoxAscent);bottom=Math.max(bottom,p.y+m.actualBoundingBoxDescent);}}let old=r[i].outerHTML,pad=16.2;for(const [key,value]of Object.entries({x:left-pad,y:top-pad,width:right-left+2*pad,height:bottom-top+2*pad}))r[i].setAttribute(key,value);out.push({id,old,ink:{left,right,top,bottom},diagnostic:r[i].outerHTML});}return out})())'))
  after=measure();out['acidBounds'].append({'version':version,'before':before,'details':details,'diagnosticInkBounds':after})
  print(version,'collector contacts',out['collector'][-1]['before']['raster']['inkWithinHalfCssPixelOfBond'],'acid hidden',after['raster']['fullyHiddenLineCount'],flush=True)
 # Retina condition, targeted real final-app rendering; source unchanged.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':2})
 for key,mode in [('butene_1','expanded'),('dimethyl_2_3_butane','expanded'),('nitroethane','skeletal'),('ethanenitrile','condensed'),('ethyl_4_isopropyl_3_methyl_2_hexanal','condensed'),('pentanoic_acid','condensed')]:
  ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fInitProps();fLoadMol2D();true');row=measure();row['dpr']=ev('devicePixelRatio');out['dpr2'].append(row)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'residual-causes.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('causal diagnostics',out['completed'],'errors',len(js_errors),flush=True)
