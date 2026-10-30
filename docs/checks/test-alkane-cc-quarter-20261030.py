"""Approved25% C-C reduction in the single-molecule prototype."""
from pathlib import Path
import subprocess
setup=Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text().split('\ntry:\n navigate')[0]
exec(compile(setup,'existing-raster-test-setup','exec'))
# Tag each detached glyph with a distinct color: small font line-boxes can
# overlap neighboring ink, so black-only scans would misattribute that ink.
install=install.replace("const glyphURL=", """const glyphTexts=[...glyphClone.querySelectorAll('text')];glyphTexts.forEach((t,i)=>{const color='rgb('+(i%5*50)+','+(Math.floor(i/5)*50)+',0)';for(const el of [t,...t.querySelectorAll('*')]){el.style.fill=color;if(el.hasAttribute('stroke')&&el.getAttribute('stroke')!=='none')el.style.stroke=color;}});const glyphURL=""")
install=install.replace("if(ink[k]<248||ink[k+1]<248||ink[k+2]<248){", "const alpha=(255-ink[k+2])/255;const red=(ink[k]-255*(1-alpha))/alpha,green=(ink[k+1]-255*(1-alpha))/alpha;if(alpha>.08&&Math.abs(red-l.i%5*50)<14&&Math.abs(green-Math.floor(l.i/5)*50)<14){")
snap=json.loads(gzip.decompress(Path('docs/checks/alkane-cc-quarter-before-20261030.json.gz').read_bytes()))
oldviewer=base64.b64decode(snap['sources']['js/mulermoc-nom-molview-52.js']).decode()
oldprepare=oldviewer[oldviewer.index('function fPrepareFixedCCAlkanePrototype()'):oldviewer.index('function fGetUniform2DLibraryFrame()')]
oldfit=oldviewer[oldviewer.index('function fFit2DSVG()'):oldviewer.index('// JSME labels collinear sp carbons',oldviewer.index('function fFit2DSVG()'))]
code=base64.b64decode(snap['sources']['js/jsme-nick-nomeclature-moc2-data_52.js']).decode()
response=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps('var window={};'+code+';print(JSON.stringify(window.MOL2D.dimethyl_2_3_butane.expanded));')+'\n',capture_output=True,text=True,check=True)
quarter=json.loads(response.stdout)
result={'completed':False,'cases':[],'guards':[],'interactions':[]}
measurement=r'''(()=>{const meta={key:selectedMol,zoom:molZoom2D,targetFont:molSvg.node.dataset.uniformAtomFontPixels,
 fonts:[...molSvg.node.querySelectorAll('text:not([id^="number"])')].map(t=>{const m=t.getScreenCTM();return parseFloat(getComputedStyle(t).fontSize)*Math.hypot(m.a,m.b)}),prototype:molSvg.node.dataset.alkaneFixedCCScale||null};return __endpointCheck().then(r=>JSON.stringify({...r,...meta}))})()'''
try:
 navigate('mulermoc-nom-52.html?v=cc-quarter-test');app_ready();ev('document.fonts.ready.then(()=>true)');ev(install)
 ev('window.__oldFit=('+oldfit+');window.__newFit=fFit2DSVG;window.__prepare=fPrepareFixedCCAlkanePrototype;window.__oldPrepare=('+oldprepare+');window.__quarter='+json.dumps(quarter)+';window.__half=nameExamples.dimethyl_2_3_butane.structure2D_Expanded;window.__configure=(old)=>{fFit2DSVG=old?__oldFit:__newFit;fPrepareFixedCCAlkanePrototype=old?__oldPrepare:__prepare};true')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for phase in (['after']if os.environ.get('NAMELECULE_FIXED_CC_FOCUS')else['before','after']):
   for zoom in ([2,0.5]if os.environ.get('NAMELECULE_FIXED_CC_FOCUS')else[0.5,2,2.5]):
    ev('__configure('+str(phase=='before').lower()+');selectedMol="dimethyl_2_3_butane";nameExamples[selectedMol].structure2D_Expanded='+('__half'if phase=='after'else'__quarter')+';mode2D="expanded";numberingFlag=false;mainChainMode="algorithmic";fInitProps();fLoadMol2D();fShowNameAnalysis();molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
    row=json.loads(ev(measurement));row.update(width=width,phase=phase)
    row['readabilityFailures']=[b for b in row['checks']if b['visibleLength']<=1 or any(e['gap']<=.15 or not e['rasterClear']for e in b['endpoints'])]
    if phase=='after':
     assert row['prototype'] and not row['overlaps']and not row['clipped']and not row['readabilityFailures'],row
     ratio=sum(b['length']for b in row['checks']if b['type']=='C-C')/sum(b['type']=='C-C'for b in row['checks'])/row['fonts'][0]
     assert abs(ratio-2.6175)<.01,(ratio,row)
    result['cases'].append(row)
    if width==1500 and zoom==2 and phase in ['before','after']:screenshot(str(args.output/(phase+'.png')))
  print('Cases',width,'PASS',flush=True)
 ev('nameExamples.dimethyl_2_3_butane.structure2D_Expanded=__half;true')
 for key,mode in [('dimethyl_2_3_butane','condensed'),('dimethyl_2_3_butane','skeletal'),('methyl_2_pentane','expanded'),('ethyl_3_dimethyl_2_5_hexane','expanded'),('methane','expanded'),('methanol','expanded')]:
  # Only test keys actually available in this library.
  if not ev('!!nameExamples['+json.dumps(key)+']'):continue
  pair=[]
  for old in [True,False]:
   pair.append(ev('__configure('+str(old).lower()+');selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';numberingFlag=false;fInitProps();fLoadMol2D();molSvg.node.outerHTML'))
  assert pair[0]==pair[1],(key,mode)
  result['guards'].append({'key':key,'mode':mode,'identicalSVG':True})
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  ev('__configure(false);document.getElementById("dimethyl_2_3_butane").click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();molZoom2D=MOL_ZOOM_DEFAULT;fReapplyZoomScale2D();fShowNameAnalysis();true')
  for component in ['comp5','comp1']:
   ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(component)+').click();true')
   until("!numberingFlag||nameAnalysisMode!=='compCarbonsCount'||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",seconds=15)
   # SVG typographic line boxes include unused descent/side bearing. Test
   # actual ink plus painted stroke for number-vs-atom collisions instead.
   numbers=json.loads(ev("""JSON.stringify((()=>{const root=molSvg.node,view=root.getBoundingClientRect(),ctx=document.createElement('canvas').getContext('2d');const box=t=>{const m=t.getScreenCTM(),s=getComputedStyle(t),k=Math.hypot(m.a,m.b);ctx.font=s.fontStyle+' '+s.fontWeight+' '+parseFloat(s.fontSize)*k+'px '+s.fontFamily;const ink=ctx.measureText(t.textContent),p=new DOMPoint(+t.getAttribute('x'),+t.getAttribute('y')).matrixTransform(m),sw=s.stroke==='none'?0:parseFloat(s.strokeWidth)*k/2;return {left:p.x-ink.actualBoundingBoxLeft-sw,right:p.x+ink.actualBoundingBoxRight+sw,top:p.y-ink.actualBoundingBoxAscent-sw,bottom:p.y+ink.actualBoundingBoxDescent+sw}};const atoms=[...root.querySelectorAll('text:not([id^=number])')].map(box),nums=[...root.querySelectorAll('text[id^=number]')].map(box);return {count:nums.length,clipped:nums.some(b=>b.left<view.left||b.top<view.top||b.right>view.right||b.bottom>view.bottom),overlap:nums.some(b=>atoms.some(a=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1))}})())"""))
   assert not numbers['clipped']and not numbers['overlap'],numbers
   if component=='comp5':assert numbers['count']==4,numbers
   row=json.loads(ev(measurement));row.update(width=width,component=component,numbering=numbers)
   assert not row['overlaps']and not row['clipped'],row
   assert all(b['visibleLength']>1 and all(e['gap']>.15 and e['rasterClear']for e in b['endpoints'])for b in row['checks']),row
   result['interactions'].append(row)
  assert ev('(()=>{fPrepareFixedCCAlkanePrototype();const a=molSvg.node.outerHTML;fPrepareFixedCCAlkanePrototype();return a===molSvg.node.outerHTML})()')
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
 until('!!window.__png&&!!window.__exportSvg');assert ev("__png.size>1000&&!new DOMParser().parseFromString(__exportSvg,'image/svg+xml').querySelector('parsererror')")
 result['export']='PNG >1000bytes and valid SVG'
 desktop=[x for x in result['cases']if x['width']==1500 and x['zoom']==2]
 if len(desktop)==2:
  stats={x['phase']:{'CC':sum(b['length']for b in x['checks']if b['type']=='C-C')/5,'CH':sum(b['length']for b in x['checks']if b['type']!='C-C')/14}for x in desktop}
  result['desktopComparison']={t:stats['after'][t]/stats['before'][t]for t in ['CC','CH']}
  assert abs(result['desktopComparison']['CC']-.75)<.001 and abs(result['desktopComparison']['CH']-1)<.003,stats
 for x in result['cases']:
  if x['phase']=='after':
   for kind in ['C-C','C-H']:
    lengths=[b['visibleLength']for b in x['checks']if b['type']==kind]
    assert max(lengths)-min(lengths)<.15,(kind,lengths)

 assert not js_errors,js_errors
 result['completed']=True
except Exception as error:
 result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors
 (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'guards':len(result['guards']),'interactions':len(result['interactions'])}),flush=True)
if not result['completed']:raise SystemExit(1)
