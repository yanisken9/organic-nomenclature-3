/* Read-only diagnostic of the final application SVG; writes only detached clones. */
window.auditFinalSvg=async function(raster=true){
 const replay=window.__auditReplaySource||null,svg=replay?document.querySelector('#snapshot svg'):document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text')];
 const visible=e=>{let s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)!==0&&e.getBoundingClientRect().width>0};
 const atoms=labels.filter(e=>!e.id.startsWith('number')&&visible(e));
 // Inspect the drawing itself, not the application's ordinal atom→rect map.
 // Compaction can remove the canvas background, making the first rect an atom.
 const rects=[...svg.querySelectorAll('rect')];
 const isCanvasBackground=r=>r===rects[0]&&!r.hasAttribute('rx')&&!r.hasAttribute('ry')&&+r.getAttribute('x')===0&&+r.getAttribute('y')===0;
 const backplates=new Set(rects.filter(r=>!isCanvasBackground(r)&&getComputedStyle(r).fill!=='none'));
 const num=v=>Number.isFinite(v)?Math.round(v*1e5)/1e5:null;
 const box=e=>{let b=e.getBoundingClientRect();return [b.left-outer.left,b.top-outer.top,b.right-outer.left,b.bottom-outer.top].map(num)};
 const atomData=atoms.map(t=>({text:t.textContent,box:box(t),font:getComputedStyle(t).fontSize}));
 const clipped=atomData.filter(t=>t.box[0]<-1||t.box[1]<-1||t.box[2]>outer.width+1||t.box[3]>outer.height+1);
 const overlaps=[];for(let i=0;i<atomData.length;i++)for(let j=0;j<i;j++){
  let a=atomData[i].box,b=atomData[j].box;
  if(Math.min(a[2],b[2])-Math.max(a[0],b[0])>1&&Math.min(a[3],b[3])-Math.max(a[1],b[1])>1)overlaps.push([i,j]);
 }
 const numberData=labels.filter(t=>t.id.startsWith('number')).map(t=>({text:t.textContent,box:box(t)}));
 const edges=[...svg.querySelectorAll('line')].filter(visible);
 const result={key:replay?replay.key:selectedMol,mode:replay?replay.mode:mode2D,name:replay?replay.name:currentMolName,atoms:atomData,clipped,overlaps,numbers:numberData,lines:edges.length,viewport:[outer.width,outer.height],viewBox:svg.getAttribute('viewBox'),atomSymbols:replay?replay.atomSymbols:allAtomsTypeList.slice(),bondGraph:replay?replay.bondGraph:bondList.map(b=>b.slice()),rawFinalSVG:svg.outerHTML};
 if(!raster)return result;
 // Render at 4x actual CSS size, preserving all transforms/viewBox. Canvas
 // TextMetrics is not used by this oracle. Copy computed text styles because
 // external application CSS is absent when an SVG is decoded as an image.
 const scale=4,width=Math.ceil(outer.width*scale),height=Math.ceil(outer.height*scale);
 if(!width||!height)throw Error('Empty final viewport');
 const original=[svg,...svg.querySelectorAll('*')],copy=svg.cloneNode(true),copied=[copy,...copy.querySelectorAll('*')];
 let sanitized=0;
 for(let k=0;k<copied.length;k++){
  const a=original[k],b=copied[k];
  for(const attr of [...b.attributes])if(!/^[a-zA-Z_][a-zA-Z0-9_.:-]*$/.test(attr.name)){b.removeAttribute(attr.name);sanitized++;}
  if(a.tagName==='text'){
   if(!atoms.includes(a))b.setAttribute('data-audit-ignore','1');
   const s=getComputedStyle(a);for(const p of ['font-family','font-size','font-weight','font-style','visibility','display'])b.style.setProperty(p,s.getPropertyValue(p));
  }
  if(backplates.has(a))b.setAttribute('data-audit-mask','1');
  if(a.tagName==='line'&&!edges.includes(a))b.setAttribute('data-audit-ignore','1');
 }
 async function draw(kind){
  const node=copy.cloneNode(true);node.setAttribute('xmlns','http://www.w3.org/2000/svg');node.setAttribute('width',width);node.setAttribute('height',height);node.style.width=width+'px';node.style.height=height+'px';
  if(!node.hasAttribute('viewBox'))node.setAttribute('viewBox',`0 0 ${outer.width} ${outer.height}`);
  for(const e of [...node.querySelectorAll('*')]){
   if(e.hasAttribute('data-audit-ignore')){e.remove();continue;}
   const tag=e.tagName,shape=['rect','line','polygon','path','circle','ellipse'].includes(tag),mask=e.hasAttribute('data-audit-mask');
   if(kind==='glyphs'){
    if(shape)e.remove();
    if(tag==='text'){e.style.fill='black';e.setAttribute('fill','black');}
   }else if(kind==='masks'){
    if(tag==='text'||(shape&&!mask))e.remove();
    if(mask){e.style.fill='black';e.setAttribute('fill','black');e.setAttribute('stroke','none');}
   }else{
    if(tag==='text'||(shape&&tag!=='line'&&!mask))e.remove();
    if(mask){e.style.fill='white';e.setAttribute('fill','white');e.setAttribute('stroke','none');}
    if(tag==='line'){e.style.stroke='black';e.setAttribute('stroke','black');}
   }
  }
  const img=new Image();img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(new XMLSerializer().serializeToString(node));await img.decode();
  const c=document.createElement('canvas');c.width=width;c.height=height;const ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(img,0,0);
  return ctx.getImageData(0,0,width,height).data;
 }
 // SVG images do not inherit the page's downloaded @font-face definitions.
 // Paint the glyphs with the page's actual fonts at SVG's actual character
 // positions. This uses pixels, never TextMetrics or producer mask dimensions.
 function paintGlyphs(){
  const c=document.createElement('canvas');c.width=width;c.height=height;const context=c.getContext('2d',{willReadFrequently:true});
  for(const text of atoms){
   const m=text.getScreenCTM();if(!m)continue;
   const walker=document.createTreeWalker(text,NodeFilter.SHOW_TEXT);let node,index=0;
   while(node=walker.nextNode()){
    const parent=node.parentElement,style=getComputedStyle(parent);
    for(const char of node.textContent){
     const pos=text.getStartPositionOfChar(index++);
     if(style.display==='none'||style.visibility==='hidden')continue;
     context.setTransform(scale*m.a,scale*m.b,scale*m.c,scale*m.d,scale*(m.e-outer.left),scale*(m.f-outer.top));
     context.font=style.fontStyle+' '+style.fontWeight+' '+style.fontSize+' '+style.fontFamily;
     context.textBaseline='alphabetic';context.fillStyle='black';context.fillText(char,pos.x,pos.y);
     if(style.stroke!=='none'){context.strokeStyle='black';context.lineWidth=parseFloat(style.strokeWidth)||0;context.strokeText(char,pos.x,pos.y);}
    }
   }
  }
  return context.getImageData(0,0,width,height).data;
 }
 // Sample actual screen-space line coverage by actual rounded backplates.
 const plates=[...backplates].filter(visible).map(r=>({r,inv:r.getScreenCTM()?.inverse()})).filter(v=>v.inv);
 const isMasked=(x,y)=>plates.some(({r,inv})=>{
  const p=new DOMPoint(x+outer.left,y+outer.top).matrixTransform(inv);
  const a=+r.getAttribute('x'),b=+r.getAttribute('y'),w=+r.getAttribute('width'),h=+r.getAttribute('height');if(p.x<a||p.x>a+w||p.y<b||p.y>b+h)return false;
  const rx=Math.min(+r.getAttribute('rx')||0,w/2),ry=Math.min(+r.getAttribute('ry')||0,h/2),dx=Math.max(a+rx-p.x,0,p.x-a-w+rx),dy=Math.max(b+ry-p.y,0,p.y-b-h+ry);
  return !dx||!dy||dx*dx/(rx*rx)+dy*dy/(ry*ry)<=1;
 });
 const lineVisibility=edges.map(l=>{
  const m=l.getScreenCTM(),p=new DOMPoint(+l.getAttribute('x1'),+l.getAttribute('y1')).matrixTransform(m),q=new DOMPoint(+l.getAttribute('x2'),+l.getAttribute('y2')).matrixTransform(m);
  const length=Math.hypot(q.x-p.x,q.y-p.y),steps=Math.max(2,Math.ceil(length*4));let n=0;
  for(let k=0;k<=steps;k++)if(!isMasked(p.x-outer.left+(q.x-p.x)*k/steps,p.y-outer.top+(q.y-p.y)*k/steps))n++;
  return {length:num(length),visibleLength:num(n*length/(steps+1))};
 });
 const [glyphs,masks,bonds]=await Promise.all([Promise.resolve(paintGlyphs()),draw('masks'),draw('bonds')]);
 let ink=0,uncovered=0,contact=0;const affected=new Set;
 // Restrict the pixel search to the visible text envelope, with 2 CSS px
 // clearance. This preserves the contact neighborhood and avoids empty canvas.
 const x0=Math.max(2,Math.floor(Math.min(...atomData.map(t=>t.box[0]))*scale)-2*scale),x1=Math.min(width-2,Math.ceil(Math.max(...atomData.map(t=>t.box[2]))*scale)+2*scale);
 const y0=Math.max(2,Math.floor(Math.min(...atomData.map(t=>t.box[1]))*scale)-2*scale),y1=Math.min(height-2,Math.ceil(Math.max(...atomData.map(t=>t.box[3]))*scale)+2*scale);
 for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){
  const i=(y*width+x)*4;if(glyphs[i+3]<128)continue;ink++;
  let bad=false;if(masks[i+3]<250){uncovered++;bad=true;}
  let near=false;for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++){
   const j=((y+dy)*width+x+dx)*4;if(bonds[j+3]>128&&bonds[j]<128)near=true;
  }
  if(near){contact++;bad=true;}
  if(bad)for(let k=0;k<atomData.length;k++){
   const b=atomData[k].box;if(x/scale>=b[0]-1&&x/scale<=b[2]+1&&y/scale>=b[1]-1&&y/scale<=b[3]+1)affected.add(k);
  }
 }
 result.raster={glyphMethod:"actual document fonts; SVG character positions; Canvas pixel paint",scale,width,height,inkPixels:ink,uncoveredInkPixels:uncovered,inkWithinHalfCssPixelOfBond:contact,affectedLabels:[...affected].map(i=>atomData[i].text),fullyHiddenLineCount:lineVisibility.filter(v=>v.visibleLength===0).length,lineVisibility,sanitizedCloneAttributes:sanitized};
 return result;
};
