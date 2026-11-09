"""Targeted Firefox follow-up: actual selected molecule, exports, chain changes, hosts."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
created=[ctx]
folder=Path('/tmp/namelecule-skeletal-layout-20261028');result={'completed':False,'hosts':[]}
target='ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid'
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
try:
 navigate('mulermoc-nom-52.html?v=skeletal-interactions');app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)');ev('window.skeletalLayoutReal=fApplySkeletalLayout;true')
 for k in [target,'butanenitrile']:
  ev('fApplySkeletalLayout=()=>{};document.getElementById('+json.dumps(k)+').click();true');until('mainChainPool3DKey==='+json.dumps(k))
  ev("document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();true");screenshot(str(folder/(k+'-before.png')))
  before=data('({name:currentMolName,chain:mainChainAtomsList,chain3:mainChainAtoms3D})')
  ev('fApplySkeletalLayout=skeletalLayoutReal;fUpdateSVG();true');after=data('({name:currentMolName,chain:mainChainAtomsList,chain3:mainChainAtoms3D})');assert before==after
  screenshot(str(folder/(k+'-after.png')))
 ev('document.getElementById('+json.dumps(target)+').click();true');until('mainChainPool3DKey==='+json.dumps(target));ev("document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();true")
 base=data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList,chain3:mainChainAtoms3D})')
 ev("document.getElementById('acidPrefixSub3').click();true");selection=ev('JmolSelection')
 for d in [1,-1,1,-1]:
  ev('fZoom2D('+str(d)+');true');time.sleep(.2)
  assert data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList,chain3:mainChainAtoms3D})')==base
  assert ev('JmolSelection')==selection
 result['zoomCycles']=4
 # Capture the real exporter canvas/blob; suppress the download only.
 ev("""window.skeletalNativeCreate=URL.createObjectURL;window.skeletalNativeClick=HTMLAnchorElement.prototype.click;window.skeletalNativeToBlob=HTMLCanvasElement.prototype.toBlob;window.skeletalPNGs={};window.skeletalPNG=null;URL.createObjectURL=function(blob){const url=skeletalNativeCreate.call(URL,blob);skeletalPNGs[url]=blob;return url};HTMLCanvasElement.prototype.toBlob=function(callback,type){const pixels=this.getContext('2d').getImageData(0,0,this.width,Math.max(1,this.height-90)).data;let ink=0;for(let i=0;i<pixels.length;i+=4){if(pixels[i]<240||pixels[i+1]<240||pixels[i+2]<240)ink++}window.skeletalCanvas={width:this.width,height:this.height,ink};return skeletalNativeToBlob.call(this,callback,type)};HTMLAnchorElement.prototype.click=function(){if(this.download.endsWith('_2D.png')){const blob=skeletalPNGs[this.href],reader=new FileReader();reader.onload=()=>{skeletalPNG={name:this.download,size:blob.size,type:blob.type,data:reader.result}};reader.readAsDataURL(blob)}else skeletalNativeClick.call(this)};fSave2DPng();true""")
 until('!!window.skeletalPNG');png=data('skeletalPNG');canvas=data('skeletalCanvas');assert png['size']>1000 and png['type']=='image/png' and canvas['width']==1200 and canvas['ink']>100
 (folder/'selected-acid-export.png').write_bytes(base64.b64decode(png['data'].split(',')[1]));result['png']=dict(name=png['name'],bytes=png['size'],**canvas)
 ev('URL.createObjectURL=skeletalNativeCreate;HTMLAnchorElement.prototype.click=skeletalNativeClick;HTMLCanvasElement.prototype.toBlob=skeletalNativeToBlob;true')
 # Alternative numbered-parent selection must rebuild from original coordinates.
 ev("document.getElementById('ethyl_3_dimethyl_4_5_hexadiene_1_4').click();true");until("mainChainPool3DKey==='ethyl_3_dimethyl_4_5_hexadiene_1_4'");ev("document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();true")
 idx=ev('mainChainPoolIdx');size=ev('mainChainPool.length');initial=data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList})')
 if size>1:
  direction=1 if idx<size-1 else -1;ev('fStepMainChain('+str(direction)+');true');other=data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList})');assert other['name']==initial['name']
  ev('fStepMainChain('+str(-direction)+');true');assert data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList})')==initial
  result['chainStepRoundtrip']=True
 else:result['chainStepRoundtrip']='No alternative in selected pool'
 # Both embedded pages load the same helper, retaining their original sizing flags.
 for path in ['react-preview/public/viewer-host.html','react-preview/public/lesson-host.html']:
  ctx=call('browsingContext.create',{'type':'tab'})['context'];created.append(ctx)
  call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
  navigate(path+'?v=skeletal-layout-check');app_ready();until('!!window.JSmolReadyFlag')
  ev("selectedMol='butanenitrile';mode2D='skeletal';nameAnalysisMode='none';numberingFlag=false;fInitNamingProps();fLoadMol2D();true")
  info=data("({helper:typeof fSkeletalLayoutMol,source:skeletalLayoutSource.key,applied:skeletalLayoutApplied,mol:myMol2D,font:document.documentElement.getAttribute('data-namelecule-2d-font-size')})")
  assert info['helper']=='function' and info['source']=='butanenitrile' and info['applied'] and info['font'] is None
  info.pop('mol');result['hosts'].append(dict(path=path,**info))
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'interactions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 for context in created:call('browsingContext.close',{'context':context})
 call('session.end',{})
 print(json.dumps({k:v for k,v in result.items() if k!='javascriptErrors'},ensure_ascii=False), 'JS errors:',len(js_errors),flush=True)
