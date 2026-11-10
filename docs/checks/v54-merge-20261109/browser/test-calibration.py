"""Compare existing54/new55 actual expanded SVG calibration at matched viewport."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
METRIC=r'''(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),labels=[...svg.querySelectorAll('text[data-namelecule-atom]')],map=new Map(labels.map(t=>[+t.dataset.nameleculeAtom,t])),samples={CC:[],CH:[],font:[]};for(const t of labels){const m=t.getScreenCTM(),font=parseFloat(getComputedStyle(t).fontSize)*Math.hypot(m.a,m.b);samples.font.push(font)}for(const[a,b,o]of bondList){const ta=map.get(a),tb=map.get(b);if(!ta||!tb||!ta.hasAttribute('data-fixed-c-c-atom-x')||!tb.hasAttribute('data-fixed-c-c-atom-x'))continue;const pa=new DOMPoint(+ta.dataset.fixedCCAtomX,+ta.dataset.fixedCCAtomY).matrixTransform(ta.getScreenCTM()),pb=new DOMPoint(+tb.dataset.fixedCCAtomX,+tb.dataset.fixedCCAtomY).matrixTransform(tb.getScreenCTM()),syms=[allAtomsTypeList[a-1],allAtomsTypeList[b-1]].sort().join('');if(syms==='CC'||syms==='CH')samples[syms].push(Math.hypot(pa.x-pb.x,pa.y-pb.y))}const median=a=>a.length?a.slice().sort((a,b)=>a-b)[Math.floor(a.length/2)]:null;const c=median(samples.CC),h=median(samples.CH),f=median(samples.font);return{key:selectedMol,mode:mode2D,width:innerWidth,fontPx:f,CCPx:c,CHPx:h,CCperFont:c/f,CHperFont:h/f,CHperCC:h/c,samples,svgMetadata:{...svg.dataset},labels:labels.length,host:document.getElementById('jsmeNomeclatureSVG').getBoundingClientRect().toJSON()}})()'''
try:
 out['measurements']=[];out['oracleSweepPolicy']='Supported MULER_QUIET_FETCH preload; all calibration is real SVG rendering.'
 for version in [54,55]:
  navigate('mulermoc-nom-'+str(version)+'.html?v=calibration55-'+str(time.time_ns()));app_ready();ev('document.fonts.ready.then(()=>true)')
  for width,height in [(1500,1000),(390,760)]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
   for mol in ['dimethyl_2_3_butane','isopropyl_4_dimethyl_3_5_heptanol_2','ethyl_isopropyl_ether','isopropyl_ethanoate']:
    ev('selectedMol='+json.dumps(mol)+';mode2D="expanded";fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)');pause(150);r=read(METRIC);r['version']=version;out['measurements'].append(r)
    check(r['CCPx'] and r['CHPx'] and r['fontPx'],'Actual54/55 C-C/C-H/fontmetric available '+str(version)+' '+mol+' '+str(width),r)
    shot('calibration-v'+str(version)+'-'+mol+'-'+str(width))
 pairs=[]
 for b in out['measurements']:
  if b['version']!=55:continue
  a=next(a for a in out['measurements']if a['version']==54 and a['key']==b['key']and a['width']==b['width']);p={'key':b['key'],'width':b['width'],'fontRatio55vs54':b['fontPx']/a['fontPx'],'CCperFont54':a['CCperFont'],'CCperFont55':b['CCperFont'],'CHperCC54':a['CHperCC'],'CHperCC55':b['CHperCC']};pairs.append(p)
  check(abs(b['CCperFont']-a['CCperFont'])<.02 and abs(b['CHperCC']-a['CHperCC'])<.02,'No doublecompensation calibration ratios preserved '+b['key']+' '+str(b['width']),p)
 out['comparison']=pairs;out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('calibration-failure')
 except Exception:pass
finally:finish('calibration-browser')
if not out['completed']:raise SystemExit(1)
