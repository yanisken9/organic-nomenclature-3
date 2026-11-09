"""Affected8 only: raw-data before/after at normal/min zoom and two widths."""
from pathlib import Path
import subprocess
setup=Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text().split('\ntry:\n navigate')[0]
exec(compile(setup,'existing-raster-test-setup','exec'))
snapshot=json.loads(gzip.decompress(Path('docs/checks/alkane-ch-quarter-before-20261030.json.gz').read_bytes()))
code=base64.b64decode(snapshot['sources']['js/jsme-nick-nomeclature-moc2-data_52.js']).decode()
response=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps('var window={};'+code+';print(JSON.stringify(window.MOL2D));')+'\n',capture_output=True,text=True,check=True)
before={k:v['expanded']for k,v in json.loads(response.stdout).items()if k in snapshot['keys']}
result={'completed':False,'cases':[],'highlights':[]}
measurement=r'''(()=>{const meta={key:selectedMol,name:currentMolName,zoom:molZoom2D,targetFontPixels:molSvg.node.dataset.uniformAtomFontPixels};return __endpointCheck().then(r=>JSON.stringify({...r,...meta}))})()'''
try:
 navigate('mulermoc-nom-52.html?v=alkane-ch-quarter');app_ready();ev('document.fonts.ready.then(()=>true)');ev(install)
 ev('window.__beforeCH='+json.dumps(before)+';window.__afterCH=Object.fromEntries(Object.keys(__beforeCH).map(k=>[k,nameExamples[k].structure2D_Expanded]));true')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in snapshot['keys']:
   for phase in ['before','after']:
    for zoom in [2,0.5]:
     ev('selectedMol='+json.dumps(key)+';nameExamples[selectedMol].structure2D_Expanded=__'+phase+'CH[selectedMol];mode2D="expanded";mainChainMode="algorithmic";numberingFlag=false;fInitProps();fLoadMol2D();fShowNameAnalysis();molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
     row=json.loads(ev(measurement));row.update(width=width,phase=phase)
     row['readabilityFailures']=[b for b in row['checks']if b['visibleLength']<=1 or any(e['gap']<=.2 or not e['rasterClear']for e in b['endpoints'])]
     assert row['zoom']==zoom and row['checks'] and not row['clipped']and not row['overlaps'],row
     result['cases'].append(row)
     if width==1500 and zoom==2 and phase=='after'and key in ['methane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:
      screenshot(str(args.output/(key+'-after.png')))
   ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=__afterCH['+json.dumps(key)+'];true')
   print('Before/after',width,key,flush=True)
 for key in ['methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
  ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();molZoom2D=MOL_ZOOM_DEFAULT;fReapplyZoomScale2D();fShowNameAnalysis();document.getElementById("comp1").click();true')
  row=json.loads(ev(measurement));assert not row['overlaps']and not row['clipped'],row
  result['highlights'].append(row)
 assert not js_errors,js_errors
 result['completed']=True
 result['readabilityPassed']=not any(c['readabilityFailures']for c in result['cases']if c['phase']=='after')
except Exception as error:
 result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors
 (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'readabilityPassed':result.get('readabilityPassed'),'highlights':len(result['highlights'])}),flush=True)
if not result['completed']:raise SystemExit(1)
