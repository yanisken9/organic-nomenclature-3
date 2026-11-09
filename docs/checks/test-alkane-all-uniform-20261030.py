"""Remaining five expanded alkanes: reuse independent raster and numbering probes."""
from pathlib import Path
import subprocess
prior=Path('docs/checks/test-alkane-methylpentane-uniform-20261030.py').read_text()
exec(compile(prior.split('\nsnap=')[0],'existing-independent-raster-setup','exec'))
number_probe=prior.split('numbers=json.loads(ev("""',1)[1].split('"""))',1)[0]
snap=json.loads(gzip.decompress(Path('docs/checks/alkane-all-uniform-before-20261030.json.gz').read_bytes()))
oldviewer=base64.b64decode(snap['sources']['js/mulermoc-nom-molview-52.js']).decode()
oldprepare=oldviewer[oldviewer.index('function fPrepareFixedCCAlkanePrototype()'):oldviewer.index('function fGetUniform2DLibraryFrame()')]
code=base64.b64decode(snap['sources']['js/jsme-nick-nomeclature-moc2-data_52.js']).decode()
response=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps('var window={};'+code+';print(JSON.stringify(window.MOL2D));')+'\n',capture_output=True,text=True,check=True)
before={k:v['expanded']for k,v in json.loads(response.stdout).items()if k in snap['viewerTargets']}
counts={'methane':1,'ethane':2,'propane':3,'butane':4,'pentane':5}
result={'completed':False,'cases':[],'guards':[],'interactions':[]}
measurement=r'''(()=>{const meta={key:selectedMol,zoom:molZoom2D,prototype:molSvg.node.dataset.alkaneFixedCCScale||null,
 fonts:[...molSvg.node.querySelectorAll('text:not([id^="number"])')].map(t=>{const m=t.getScreenCTM();return parseFloat(getComputedStyle(t).fontSize)*Math.hypot(m.a,m.b)})};return __endpointCheck().then(r=>JSON.stringify({...r,...meta}))})()'''
def validate(row):
 assert row['prototype']and not row['overlaps']and not row['clipped'],row
 assert max(row['fonts'])-min(row['fonts'])<.01,row
 assert row['atomCount']==3*counts[row['key']]+2,row
 for bond in row['checks']:
  assert bond['visibleLength']>1 and all(e['gap']>.15 and e['rasterClear']for e in bond['endpoints']),bond
 cc=[b['length']for b in row['checks']if b['type']=='C-C'];ch=[b['length']for b in row['checks']if b['type']!='C-C']
 assert abs(sum(ch)/len(ch)/row['fonts'][0]-1.30875)<.01,row
 if cc:assert abs(sum(cc)/len(cc)/row['fonts'][0]-2.6175)<.01,row
 for cc_only in [False,True]:
  lengths=[b['visibleLength']for b in row['checks']if (b['type']=='C-C')==cc_only]
  if lengths:assert max(lengths)-min(lengths)<.15,lengths
try:
 navigate('mulermoc-nom-52.html?v=all-alkanes-uniform-test');app_ready();ev('document.fonts.ready.then(()=>true)');ev(install)
 ev('window.__newPrepare=fPrepareFixedCCAlkanePrototype;window.__oldPrepare=('+oldprepare+');window.__before='+json.dumps(before)+';window.__after=Object.fromEntries(Object.keys(__before).map(k=>[k,nameExamples[k].structure2D_Expanded]));window.__configure=old=>{fPrepareFixedCCAlkanePrototype=old?__oldPrepare:__newPrepare};true')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in counts:
   for phase in ['before','after']:
    for zoom in [0.5,2,2.5]:
     ev('__configure('+str(phase=='before').lower()+');selectedMol='+json.dumps(key)+';nameExamples[selectedMol].structure2D_Expanded=__'+phase+'[selectedMol];mode2D="expanded";numberingFlag=false;mainChainMode="algorithmic";fInitProps();fLoadMol2D();fShowNameAnalysis();molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
     row=json.loads(ev(measurement));row.update(width=width,phase=phase);result['cases'].append(row)
     if phase=='after':validate(row)
     if width==1500 and zoom==2 and key in ['methane','pentane']:screenshot(str(args.output/(key+'-'+phase+'.png')))
   print('Cases',width,key,'PASS',flush=True)
 # Other forms and all three previously reviewed expanded prototypes keep exact SVGs.
 guards=[(k,m)for k in counts for m in ['condensed','skeletal']]+[(k,'expanded')for k in ['methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']]
 for key,mode in guards:
  if not ev('!!window.MOL2D['+json.dumps(key)+']?.['+json.dumps(mode)+']'):continue
  pair=[ev('__configure('+str(old).lower()+');selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';numberingFlag=false;fInitProps();fLoadMol2D();molSvg.node.outerHTML')for old in [True,False]]
  assert pair[0]==pair[1],(key,mode)
  result['guards'].append({'key':key,'mode':mode,'identicalSVG':True})
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key,count in counts.items():
   ev('__configure(false);document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();molZoom2D=MOL_ZOOM_DEFAULT;fReapplyZoomScale2D();fClearHighlights();fShowNameAnalysis();document.getElementById("comp5").click();true')
   until("!numberingFlag||nameAnalysisMode!=='compCarbonsCount'||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",seconds=15)
   numbers=json.loads(ev(number_probe));assert numbers['count']==count and not numbers['clipped']and not numbers['overlap'],(key,numbers)
   row=json.loads(ev(measurement));row.update(width=width,numbering=numbers);validate(row);result['interactions'].append(row)
   assert ev('(()=>{fPrepareFixedCCAlkanePrototype();const a=molSvg.node.outerHTML;fPrepareFixedCCAlkanePrototype();return a===molSvg.node.outerHTML})()')
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
 until('!!window.__png&&!!window.__exportSvg');assert ev("__png.size>1000&&!new DOMParser().parseFromString(__exportSvg,'image/svg+xml').querySelector('parsererror')")
 result['export']='PNG >1000bytes and valid SVG';assert not js_errors,js_errors;result['completed']=True
except Exception as error:
 result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors;(args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'guards':len(result['guards']),'interactions':len(result['interactions'])}),flush=True)
if not result['completed']:raise SystemExit(1)
