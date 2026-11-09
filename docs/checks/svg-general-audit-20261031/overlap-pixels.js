window.auditOverlapPixels=async function(pairs){
 const svg=molSvg.node,box=svg.getBoundingClientRect(),all=[svg,...svg.querySelectorAll('*')],texts=[...svg.querySelectorAll('text')].filter(t=>{let s=getComputedStyle(t);return !t.id.startsWith('number')&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)!==0&&t.getBoundingClientRect().width>0});
 const scale=4,width=Math.ceil(box.width*scale),height=Math.ceil(box.height*scale),cache=new Map;
 async function ink(index){
  if(cache.has(index))return cache.get(index);
  const copy=svg.cloneNode(true),nodes=[copy,...copy.querySelectorAll('*')],target=nodes[all.indexOf(texts[index])];
  for(let k=0;k<nodes.length;k++){
   let e=nodes[k];for(const a of [...e.attributes])if(!/^[a-zA-Z_][a-zA-Z0-9_.:-]*$/.test(a.name))e.removeAttribute(a.name);
   if(e.tagName==='text'){
    if(e!==target)e.remove();else{let s=getComputedStyle(all[k]);for(const p of ['font-family','font-size','font-weight','font-style'])e.style.setProperty(p,s.getPropertyValue(p));e.style.fill='black';}
   }
   if(['rect','line','path','circle','ellipse','polygon'].includes(e.tagName))e.remove();
  }
  copy.setAttribute('xmlns','http://www.w3.org/2000/svg');copy.setAttribute('width',width);copy.setAttribute('height',height);copy.style.width=width+'px';copy.style.height=height+'px';
  let img=new Image;img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(new XMLSerializer().serializeToString(copy));await img.decode();
  const c=document.createElement('canvas');c.width=width;c.height=height;let ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(img,0,0);let data=ctx.getImageData(0,0,width,height).data;cache.set(index,data);return data;
 }
 const result=[];for(const [a,b]of pairs){const [x,y]=await Promise.all([ink(a),ink(b)]);let n=0;for(let k=3;k<x.length;k+=4)if(x[k]>=128&&y[k]>=128)n++;result.push({a,b,textA:texts[a].textContent,textB:texts[b].textContent,overlappingInkPixels:n});}return result;
};
