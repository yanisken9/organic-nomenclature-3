async function prototypeMeasure(raster) {
 const svg=document.querySelector('#export svg'), texts=[...svg.querySelectorAll('text')];
 const lines=[...svg.querySelectorAll('line')], pairs=texts.map(t=>({t,r:t.previousElementSibling})).filter(p=>p.r?.tagName==='rect');
 const attrs=e=>Object.fromEntries([...e.attributes].map(v=>[v.name,v.value]));
 const labels=pairs.map(({t,r})=>({text:t.textContent,rect:attrs(r),textAttrs:attrs(t),tspans:[...t.querySelectorAll('tspan')].map(v=>({text:v.textContent,attrs:attrs(v)}))}));
 const result={svg:svg.outerHTML,labels,lines:lines.map(attrs),resources:performance.getEntriesByType('resource').filter(v=>v.name.includes('.cache.js')).map(v=>v.name)};
 if(!raster)return result;
 let xmin=Infinity,ymin=Infinity,xmax=-Infinity,ymax=-Infinity;
 const point=(x,y)=>{xmin=Math.min(xmin,x);ymin=Math.min(ymin,y);xmax=Math.max(xmax,x);ymax=Math.max(ymax,y)};
 for(const t of texts){let b=t.getBBox();point(b.x,b.y);point(b.x+b.width,b.y+b.height)}
 for(const l of lines){point(+l.getAttribute('x1'),+l.getAttribute('y1'));point(+l.getAttribute('x2'),+l.getAttribute('y2'))}
 const font=+texts[0]?.getAttribute('font-size')?.replace('px','')||270, factor=64/font;
 const margin=font/2;xmin-=margin;ymin-=margin;xmax+=margin;ymax+=margin;
 const width=Math.ceil((xmax-xmin)*factor),height=Math.ceil((ymax-ymin)*factor);
 async function layer(kind){
  const node=svg.cloneNode(true);node.setAttribute('xmlns','http://www.w3.org/2000/svg');
  node.setAttribute('viewBox',[xmin,ymin,width/factor,height/factor].join(' '));node.setAttribute('width',width);node.setAttribute('height',height);
  for(const g of node.querySelectorAll('g'))g.removeAttribute('transform');
  for(const e of [...node.querySelectorAll('g>*')]){
   const tag=e.tagName,paired=tag==='rect'&&e.nextElementSibling?.tagName==='text';
   if(kind==='glyphs'){if(tag!=='text')e.remove();else e.setAttribute('fill','black')}
   if(kind==='masks'){if(!paired)e.remove();else {e.setAttribute('fill','black');e.setAttribute('stroke','none')}}
   if(kind==='bonds'){
    if(tag==='text'||tag==='polygon'||(tag==='rect'&&!paired))e.remove();
    else if(paired){e.setAttribute('fill','white');e.setAttribute('stroke','none')}
   }
  }
  const img=new Image();img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(node.outerHTML);await img.decode();
  const c=document.createElement('canvas');c.width=width;c.height=height;const context=c.getContext('2d',{willReadFrequently:true});context.drawImage(img,0,0);
  return context.getImageData(0,0,width,height).data;
 }
 const [glyphs,masks,bonds]=await Promise.all(['glyphs','masks','bonds'].map(layer));
 let ink=0,uncovered=0,nearBond=0;
 for(let y=2;y<height-2;y++)for(let x=2;x<width-2;x++){
  const i=(y*width+x)*4;if(glyphs[i+3]<128)continue;ink++;
  if(masks[i+3]<250)uncovered++;
  let contact=false;
  for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++){
   const j=((y+dy)*width+x+dx)*4;
   // Opaque white backplates are distinguished from remaining black bonds.
   if(bonds[j+3]>128&&bonds[j]<128)contact=true;
  }
  if(contact)nearBond++;
 }
 function masked(x,y){
  return pairs.some(({r})=>{
   const a=+r.getAttribute('x'),b=+r.getAttribute('y'),w=+r.getAttribute('width'),h=+r.getAttribute('height');
   if(x<a||x>a+w||y<b||y>b+h)return false;
   const rx=Math.min(+r.getAttribute('rx')||0,w/2),ry=Math.min(+r.getAttribute('ry')||0,h/2);
   const dx=Math.max(a+rx-x,0,x-(a+w-rx)),dy=Math.max(b+ry-y,0,y-(b+h-ry));
   return !dx||!dy||dx*dx/(rx*rx)+dy*dy/(ry*ry)<=1;
  });
 }
 const visibleLines=lines.map(l=>{
  const x=+l.getAttribute('x1'),y=+l.getAttribute('y1'),dx=+l.getAttribute('x2')-x,dy=+l.getAttribute('y2')-y,length=Math.hypot(dx,dy),steps=Math.ceil(length/2);
  let visible=0;for(let k=0;k<=steps;k++)if(!masked(x+dx*k/steps,y+dy*k/steps))visible++;
  return {length,visibleLength:length*visible/(steps+1)};
 });
 result.raster={width,height,inkPixels:ink,uncoveredInkPixels:uncovered,inkPixelsWithin2pxOfBond:nearBond,visibleLines,hiddenLines:visibleLines.filter(v=>v.visibleLength===0).length};
 return result;
}
