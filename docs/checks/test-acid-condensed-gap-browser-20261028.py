"""Real Firefox before/after acid mask checks; artifacts only under /tmp."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
import runpy,gzip
ns=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py');inv=ns['inventory']();acids=[k for k,f in inv.items()if f.get('expanded')and ns['parse'](f['expanded'])[-1]]
old=json.loads(gzip.decompress(Path('docs/checks/acid-condensed-gap-before-source-20261028.json.gz').read_bytes()));viewer=base64.b64decode(old['js/mulermoc-nom-molview-52.js']).decode();a=viewer.index('function fAddHydrogens2SVG()');b=viewer.index('function fGetCompactedAtomSkipSet',a);before=viewer[a:b].strip()
folder=Path('/tmp/namelecule-acid-condensed-gap-20261028');folder.mkdir(exist_ok=True);result={'completed':False,'cases':[],'interaction':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
# SVG comparisons ignore selection/numbering overlays. For non-acids and other
# forms the complete SVG markup must remain identical, not just matching names.
render="""function(fn){fAddHydrogens2SVG=fn;fInitNamingProps();fLoadMol2D();const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text:not([id^=number])')],boxes=labels.map(e=>e.getBoundingClientRect());const overlap=[];for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j];if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlap.push([i,j])}const lines=[...svg.querySelectorAll('line')].map(e=>e.outerHTML),texts=labels.map(e=>e.outerHTML),masks=[...svg.querySelectorAll('rect')].map(e=>e.outerHTML),gaps=[];if(mode2D==='condensed'){for(const label of labels){if(!/^CH[23]$/.test(label.textContent))continue;const c=label.firstElementChild;if(!c)continue;const cb=c.getBoundingClientRect(),x=Number(label.getAttribute('x'));const line=[...svg.querySelectorAll('line')].find(l=>Math.abs(Number(l.getAttribute('x1'))-Number(l.getAttribute('x2')))<.01&&Math.abs(Number(l.getAttribute('x1'))-x)<100&&l.getBoundingClientRect().bottom>cb.bottom+2&&l.getBoundingClientRect().top<cb.bottom);if(!line)continue;const candidates=[...svg.querySelectorAll('rect')].map(e=>({e,r:e.getBoundingClientRect()})).filter(m=>m.r.width<outer.width/2&&m.r.height<100&&m.r.left<cb.left+cb.width/2&&m.r.right>cb.left+cb.width/2&&m.r.top<cb.top+cb.height/2&&m.r.bottom>cb.top+cb.height/2).sort((a,b)=>a.r.width*a.r.height-b.r.width*b.r.height);if(candidates[0])gaps.push({label:label.id,text:label.textContent,pixels:candidates[0].r.bottom-cb.bottom})}}return {lines,texts,masks,gaps,overlap,clipped:labels.filter((e,i)=>{const b=boxes[i];return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),viewBox:svg.getAttribute('viewBox'),svg:svg.outerHTML}}"""
try:
 navigate('mulermoc-nom-52.html?v=acid-condensed-gap-check');app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)')
 ev('window.__gapBefore=('+before+');window.__gapAfter=fAddHydrogens2SVG;window.__gapRender=('+render+');window.__gapInspect=('+render.replace('function(fn){fAddHydrogens2SVG=fn;fInitNamingProps();fLoadMol2D();','function(){')+');true')
 # Non-acid guards with vertical branches and subscripts.
 guards=['methane','isopropyl_4_dimethyl_3_5_heptanol_2','ethyl_isopropyl_ether','methyl_2_propene_1','dimethyl_4_5_hexene_5_yne_1_one_3','dimethyl_2_3_butane']
 guards=[k for k in guards if k in inv];assert len(guards)>=3
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7)
  if width==390:ev("document.getElementById('rotatePromptDismiss').click();true")
  for key in acids+guards:
   for mode in ['condensed','expanded','skeletal']:
    if not inv[key].get(mode):continue
    row=data('(()=>{selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+";nameAnalysisMode='none';numberingFlag=false;const a=__gapRender(__gapBefore),b=__gapRender(__gapAfter);return {key:selectedMol,mode:mode2D,before:a,after:b}})()")
    x,y=row['before'],row['after'];assert x['lines']==y['lines']and x['texts']==y['texts']and x['viewBox']==y['viewBox'],(key,mode,'non-mask change')
    if key not in acids or mode!='condensed':assert x['svg']==y['svg'],(key,mode,'scope')
    assert not y['clipped']and y['overlap']==x['overlap'],(key,mode,'new overlap/clipping')
    for a,b in zip(x['gaps'],y['gaps']):
     assert a['label']==b['label']and b['pixels']<=a['pixels']+.03,(key,mode,a,b)
     if key in acids and mode=='condensed':assert .2<b['pixels']<2.5,(width,key,a,b)
    result['cases'].append(dict(width=width,key=key,mode=mode,changedMasks=x['masks']!=y['masks'],beforeGaps=x['gaps'],afterGaps=y['gaps']))
  print('PASS viewport',width,'acid/guard before-after forms',flush=True)
 key='ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid'
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7)
  ev('fAddHydrogens2SVG=__gapAfter;selectedMol='+json.dumps(key)+";mode2D='condensed';fSelectMol();true")
  until("mainChainPool3DKey==='"+key+"'")
  until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
  for box in ['comp5','acidPrefixSub3','comp1']:
   ev('document.getElementById('+json.dumps(box)+').click();true');time.sleep(.2)
   for zoom in ['default','in','restored']:
    if zoom=='in':ev("document.getElementById('zoomInBtn').click();true")
    if zoom=='restored':ev("document.getElementById('zoomOutBtn').click();true")
    r=data("(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg');return {mode:nameAnalysisMode,zoom:molZoom2D,labels:[...svg.querySelectorAll('text[id^=C]')].filter(e=>/^CH[23]$/.test(e.textContent)).length,selected:Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.atomno.all')}})()")
    assert r['labels']>0 and len(r['selected'])>0
    geometry=data('__gapInspect()');assert not geometry['overlap']and not geometry['clipped']and len(geometry['gaps'])==2,geometry
    assert all(.2<g['pixels']<2.5 for g in geometry['gaps']),geometry['gaps']
    r['gaps']=geometry['gaps'];r.update(width=width,box=box,phase=zoom);result['interaction'].append(r)
   if box=='acidPrefixSub3':screenshot(str(folder/('complex-selected-'+str(width)+'.png')))
 # Real colour controls and export preserve the existing flow.
 ev("document.getElementById('svgAtomColorCheck').click();document.getElementById('svgAtomColorCheck').click();true")
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
 until('!!window.__png && !!window.__exportSvg')
 assert ev("window.__png.size>1000 && !new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').querySelector('parsererror')")
 assert not js_errors,js_errors
 result['guards']=guards;result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'interaction':len(result['interaction']),'errors':len(js_errors)}),flush=True)
