"""Firefox/BiDi: before/after guards, all alkane stroke endpoints and raster gaps."""
from pathlib import Path
import argparse,base64,gzip,traceback
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
result={'completed':False,'comparisons':[],'interactions':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
snapshot=json.loads(gzip.decompress(Path('docs/checks/alkane-clearance-v2-before-20261030.json.gz').read_bytes()))
old=base64.b64decode(snapshot['sources']['js/mulermoc-nom-molview-52.js']).decode()
old=old[old.index('function fPadExpandedAlkaneBranchLabels()'):old.index('// ── fMolHasSpCarbon',old.index('function fPadExpandedAlkaneBranchLabels()'))]
install=r'''(()=>{
window.__padAfter=fPadExpandedAlkaneLabels;
window.__read=()=>{const svg=molSvg.node,labels=[...svg.querySelectorAll('text')].filter(e=>!(e.id||'').startsWith('number'));
return {svg:svg.outerHTML,lines:[...svg.querySelectorAll('line')].map(e=>e.outerHTML),texts:labels.map(e=>e.outerHTML),viewBox:svg.getAttribute('viewBox')};};
window.__render=fn=>{fPadExpandedAlkaneLabels=fn;fInitProps();numberingFlag=false;fLoadMol2D();return __read()};
window.__endpointCheck=async()=>{
 const svg=molSvg.node,outer=svg.getBoundingClientRect(),texts=fGetRenderedAtomTextMap(false,true),rects=fGetRenderedAtomRectMap(false,true);
 const bounds=r=>({left:r.left-outer.left,top:r.top-outer.top,right:r.right-outer.left,bottom:r.bottom-outer.top});
 const labels=Object.entries(texts).map(([i,t])=>({i:+i,symbol:allAtomsTypeList[i],box:bounds(t.node.getBoundingClientRect()),mask:bounds(rects[i].node.getBoundingClientRect()),fill:getComputedStyle(rects[i].node).fill.match(/[\d.]+/g).slice(0,3).map(Number)}));
 // Freeze geometry before awaiting image decode: JSmol callbacks may rebuild
 // the live SVG during await; detached nodes then have a different screen CTM.
 const bonds=bondList.map(b=>b.slice());
 const edges=[...svg.querySelectorAll('line')].map(line=>{
  const m=line.getScreenCTM(),pt=(x,y)=>{const p=svg.createSVGPoint();p.x=x;p.y=y;const q=p.matrixTransform(m);return{x:q.x-outer.left,y:q.y-outer.top}};
  return {ends:[pt(+line.getAttribute('x1'),+line.getAttribute('y1')),pt(+line.getAttribute('x2'),+line.getAttribute('y2'))],sw:parseFloat(line.getAttribute('stroke-width'))*Math.hypot(m.a,m.b)};
 });
 const canvas=document.createElement('canvas'),scale=8;canvas.width=Math.ceil(outer.width*scale);canvas.height=Math.ceil(outer.height*scale);
 const clone=svg.cloneNode(true);clone.setAttribute('width',outer.width);clone.setAttribute('height',outer.height);clone.style.width=outer.width+'px';clone.style.height=outer.height+'px';
 const sanitized=[];for(const el of clone.querySelectorAll('*'))for(const attr of [...el.attributes]){if(!/^[a-zA-Z_][a-zA-Z0-9_.:-]*$/.test(attr.name)){sanitized.push(attr.name);el.removeAttribute(attr.name);}}window.__lastRasterXML=new XMLSerializer().serializeToString(clone);const image=new Image(),url=URL.createObjectURL(new Blob([window.__lastRasterXML],{type:'image/svg+xml'}));
 try{await new Promise((ok,bad)=>{image.onload=ok;image.onerror=bad;image.src=url});const c=canvas.getContext('2d');c.fillStyle='white';c.fillRect(0,0,canvas.width,canvas.height);c.drawImage(image,0,0,outer.width*scale,outer.height*scale);
 const pixels=c.getImageData(0,0,canvas.width,canvas.height).data;
 // Independent ink bounds: rasterize the SVG text without any masks/bonds,
 // rather than reusing Canvas TextMetrics from the application helper.
 const glyphClone=clone.cloneNode(true);
 for(const e of glyphClone.querySelectorAll('line,rect,path,polygon,ellipse,circle,text[id^="number"]'))e.remove();
 const glyphURL=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(glyphClone)],{type:'image/svg+xml'}));
 const glyphImage=new Image();try{await new Promise((ok,bad)=>{glyphImage.onload=ok;glyphImage.onerror=bad;glyphImage.src=glyphURL});
 const gc=document.createElement('canvas');gc.width=canvas.width;gc.height=canvas.height;const g=gc.getContext('2d');g.fillStyle='white';g.fillRect(0,0,gc.width,gc.height);g.drawImage(glyphImage,0,0,outer.width*scale,outer.height*scale);
 const ink=g.getImageData(0,0,gc.width,gc.height).data;
 for(const l of labels){const box=l.box;let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity;
 for(let yy=Math.max(0,Math.floor(box.top*scale));yy<Math.min(gc.height,Math.ceil(box.bottom*scale));yy++)
 for(let xx=Math.max(0,Math.floor(box.left*scale));xx<Math.min(gc.width,Math.ceil(box.right*scale));xx++){
  const k=4*(yy*gc.width+xx);if(ink[k]<248||ink[k+1]<248||ink[k+2]<248){left=Math.min(left,xx);right=Math.max(right,xx+1);top=Math.min(top,yy);bottom=Math.max(bottom,yy+1);}}
 if(!Number.isFinite(left))throw Error('No rasterized glyph '+l.i);
 l.box={left:left/scale,top:top/scale,right:right/scale,bottom:bottom/scale};
 }
 }finally{URL.revokeObjectURL(glyphURL)}

 const clear=(x,y,fill)=>{const xx=Math.round(x*scale),yy=Math.round(y*scale);if(xx<0||yy<0||xx>=canvas.width||yy>=canvas.height)return false;const k=4*(yy*canvas.width+xx);const ok=fill.every((channel,i)=>Math.abs(pixels[k+i]-channel)<8);if(!ok)window.__failedPixel={x,y,fill,pixel:[...pixels.slice(k,k+4)],natural:[image.naturalWidth,image.naturalHeight],outer:[outer.width,outer.height]};return ok};
 const checks=[];for(let n=0;n<bonds.length;n++){
  const[a,b,order]=bonds[n],line=edges[n];if(!line||order!==1)throw Error('Missing single bond '+n);
  const ends=line.ends;
  const length=Math.hypot(ends[1].x-ends[0].x,ends[1].y-ends[0].y),ux=(ends[1].x-ends[0].x)/length,uy=(ends[1].y-ends[0].y)/length;
  const exit=(p,dx,dy,r)=>Math.min(dx>1e-8?(r.right-p.x)/dx:dx< -1e-8?(r.left-p.x)/dx:Infinity,dy>1e-8?(r.bottom-p.y)/dy:dy< -1e-8?(r.top-p.y)/dy:Infinity);
  const sw=line.sw,offsets=[-sw*.55,0,sw*.55];
  const record={a,b,type:labels.find(l=>l.i===a-1).symbol+'-'+labels.find(l=>l.i===b-1).symbol,length,endpoints:[]};
  for(const[k,atom]of[[0,a-1],[1,b-1]]){const l=labels.find(l=>l.i===atom),p=ends[k],dx=k?-ux:ux,dy=k?-uy:uy;
   const glyphExit=exit(p,dx,dy,l.box),maskExit=exit(p,dx,dy,l.mask),gap=maskExit-glyphExit;
   const sample=glyphExit+gap*.7;
   const clean=offsets.every(off=>clear(p.x+dx*sample-dy*off,p.y+dy*sample+dx*off,l.fill));
   record.endpoints.push({atom:atom+1,symbol:l.symbol,gap,rasterClear:clean,failedPixel:clean?null:window.__failedPixel,maskExit});
  }
  record.visibleLength=length-record.endpoints.reduce((sum,e)=>sum+e.maskExit,0);
  // A stroke remains visible between its two masks, and both end gaps are white.
  checks.push(record);
 }
 const overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){const a=labels[i].box,b=labels[j].box;if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([i,j]);}
 const clipped=labels.filter(l=>l.box.left< -1||l.box.top< -1||l.box.right>outer.width+1||l.box.bottom>outer.height+1).map(l=>l.i+1);
 return {checks,overlaps,clipped,sanitizedCloneAttributes:sanitized,atomCount:labels.length,viewport:[outer.width,outer.height]};
 }finally{URL.revokeObjectURL(url)}
};return true})()'''
try:
 navigate('mulermoc-nom-52.html?v=alkane-clearance-v2-test');app_ready();ev('document.fonts.ready.then(()=>true)');ev(install)
 ev('window.__padBefore=('+old+');true')
 keys=data('Object.keys(MOL2D)');alkanes=data('Object.keys(MOL2D).filter(k=>nameExamples[k]?.classification?.seriesKey==="alkanes")')
 assert len(alkanes)==8,alkanes
 for start in range(0,len(keys),20):
  batch=keys[start:start+20]
  rows=data('(()=>{const rows=[];for(const key of '+json.dumps(batch)+'){for(const mode of ["condensed","expanded","skeletal"]){if(!MOL2D[key][mode])continue;selectedMol=key;mode2D=mode;const a=__render(__padBefore),b=__render(__padAfter);rows.push({key,mode,sameSVG:a.svg===b.svg,sameLines:JSON.stringify(a.lines)===JSON.stringify(b.lines),sameText:JSON.stringify(a.texts)===JSON.stringify(b.texts),sameViewBox:a.viewBox===b.viewBox})}}return rows})()')
  for row in rows:
   assert row['sameLines']and row['sameText']and row['sameViewBox'],row
   assert row['sameSVG']==(row['mode']!='expanded'or row['key']not in alkanes),row
  result['comparisons']+=rows;print('Compared',min(start+20,len(keys)),'/',len(keys),flush=True)
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in alkanes:
   ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();fShowNameAnalysis();true')
   phases=[('plain',1),('plain',1.25),('plain',1)]
   if key in ['methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:phases += [('comp5',1),('comp1',1),('comp1',1.25)]
   for component,factor in phases:
    if component!='plain':
     ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(component)+').click();true')
     until("!numberingFlag||nameAnalysisMode!=='compCarbonsCount'||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",seconds=15)
    ev('molZoom2D=MOL_ZOOM_DEFAULT*'+str(factor)+';fReapplyZoomScale2D();true')
    row=json.loads(ev('__endpointCheck().then(r=>JSON.stringify(r))'));row.update(key=key,width=width,component=component,zoom=factor)
    assert not row['clipped']and not row['overlaps'],row
    for bond in row['checks']:
     assert bond['visibleLength']>1,bond
     assert all(e['gap']>.2 and e['rasterClear']for e in bond['endpoints']),(key,width,component,bond)
    result['interactions'].append(row)
   # Repeated mask application must not accumulate or move geometry. The
   # pre-existing fit oscillation is compared separately against the old helper.
   a=ev('fClearHighlights();fPadExpandedAlkaneLabels();__read().svg')
   b=ev('fPadExpandedAlkaneLabels();__read().svg');assert a==b,key
   if width==1500 and key in ['methane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:
    ev('molZoom2D=MOL_ZOOM_DEFAULT;fReapplyZoomScale2D();true');screenshot(str(args.output/(key+'-after.png')))
   print('Endpoint/raster checks',width,key,flush=True)
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
 until('!!window.__png&&!!window.__exportSvg');assert ev("__png.size>1000&&!new DOMParser().parseFromString(__exportSvg,'image/svg+xml').querySelector('parsererror')")
 result['export']='PNG blob >1000 bytes; valid SVG'
 assert not js_errors,js_errors
 result['completed']=True
except Exception as error:
 (args.output/'last-raster.svg').write_text(ev('window.__lastRasterXML') or '');result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors
 (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'comparisons':len(result['comparisons']),'interactions':len(result['interactions'])}),flush=True)
if not result['completed']:raise SystemExit(1)
