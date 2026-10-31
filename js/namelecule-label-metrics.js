/* Shared glyph geometry for native JSME and final Namelecule labels.
 * Coordinates are local SVG user units, never a font line box or a prior mask.
 */
(function (root) {
  'use strict';
  const cache = new Map(), syntheticCache = new Map();
  const state = {version: '20261031-r1', epoch: 0, measured: 0, hits: 0,
    rasterFallbacks: 0, svgFallbacks: 0, nativeFallbacks: 0};
  let context;
  function finiteBox(b) {
    return b && [b.left,b.right,b.top,b.bottom].every(Number.isFinite) &&
      b.right >= b.left && b.bottom >= b.top;
  }
  function canvasContext() {
    if (!context) context = document.createElement('canvas').getContext('2d');
    return context;
  }
  function rasterGlyph(font, char, size, width) {
    // Independent fallback when a browser cannot supply actualBoundingBox*.
    const canvas = document.createElement('canvas');
    const side = Math.ceil(Math.max(size * 6, width * 2 + size * 4, 32));
    if (side > 4096) return null;
    canvas.width = canvas.height = side;
    const c = canvas.getContext('2d');
    if (!c) return null;
    const x = Math.ceil(size * 2), y = Math.ceil(size * 3);
    c.font = font; c.fillStyle = '#000'; c.fillText(char, x, y);
    const pixels = c.getImageData(0,0,side,side).data;
    let l=side,r=-1,t=side,b=-1;
    for (let yy=0; yy<side; yy++) for (let xx=0; xx<side; xx++) {
      if (pixels[(yy*side+xx)*4+3]) {l=Math.min(l,xx);r=Math.max(r,xx);t=Math.min(t,yy);b=Math.max(b,yy);}
    }
    if (r < l) return /\s/.test(char) ? {left:0,right:0,top:0,bottom:0} : null;
    state.rasterFallbacks++;
    return {left:l-x-1,right:r+2-x,top:t-y-1,bottom:b+2-y};
  }
  function glyph(style, char) {
    const size = parseFloat(style.fontSize);
    const font = `${style.fontStyle} ${style.fontWeight} ${size}px ${style.fontFamily}`;
    const key = state.epoch+'|'+font+'|'+char;
    if (cache.has(key)) {state.hits++;return cache.get(key);}
    const c = canvasContext();
    let box = null;
    if (c && size > 0) {
      c.font = font;
      const m = c.measureText(char);
      const b = {left:-m.actualBoundingBoxLeft,right:m.actualBoundingBoxRight,
        top:-m.actualBoundingBoxAscent,bottom:m.actualBoundingBoxDescent};
      box = finiteBox(b) ? b : rasterGlyph(font,char,size,m.width || size);
    }
    if (finiteBox(box)) {
      if (cache.size >= 4096) cache.clear();
      cache.set(key,box);state.measured++;
    }
    return box;
  }
  function element(text) {
    if (!text || !text.isConnected) return null;
    const chars=[];
    const walker=document.createTreeWalker(text,NodeFilter.SHOW_TEXT);
    for (let n; (n=walker.nextNode());) {
      const style=getComputedStyle(n.parentElement);
      for (const char of n.nodeValue) chars.push({char,style});
    }
    if (!chars.length) return null;
    let l=Infinity,r=-Infinity,t=Infinity,b=-Infinity;
    try {
      for (let i=0; i<chars.length; i++) {
        const p=text.getStartPositionOfChar(i), m=glyph(chars[i].style,chars[i].char);
        if (!finiteBox(m)) {
          // Conservative SVG fallback; final drawing validation also checks bonds.
          const e=text.getExtentOfChar(i);
          if (![e.x,e.y,e.width,e.height].every(Number.isFinite) || !e.height) return null;
          l=Math.min(l,e.x);r=Math.max(r,e.x+e.width);t=Math.min(t,e.y);b=Math.max(b,e.y+e.height);
          state.svgFallbacks++;
        } else {
          l=Math.min(l,p.x+m.left);r=Math.max(r,p.x+m.right);
          t=Math.min(t,p.y+m.top);b=Math.max(b,p.y+m.bottom);
        }
      }
    } catch (_) {return null;}
    const box={left:l,right:r,top:t,bottom:b};
    return finiteBox(box) && r>l && b>t ? box : null;
  }
  function synthetic(font, label) {
    const key=JSON.stringify([state.epoch,font.a,font.b,font.c,label.n,label.j,label.k]);
    if (syntheticCache.has(key)) return syntheticCache.get(key);
    const ns='http://www.w3.org/2000/svg', svg=document.createElementNS(ns,'svg');
    const text=document.createElementNS(ns,'text');
    svg.style.cssText='position:absolute;left:-100000px;top:0;opacity:0;pointer-events:none';
    svg.setAttribute('aria-hidden','true');svg.setAttribute('width','10000');svg.setAttribute('height','10000');
    text.setAttribute('x','0');text.setAttribute('y','0');text.setAttribute('font-family',font.a);
    text.setAttribute('font-size',Math.round(font.b*30)+'px');
    if (font.c&1) text.setAttribute('font-weight','bold');
    if (font.c&2) text.setAttribute('font-style','italic');
    let prior=99,span;
    for (let i=0;i<label.n.length;i++) {
      let shift=0;
      for (const [value,ranges] of [[-1,label.j],[1,label.k]]) {
        for (const range of ranges || []) if (i>=range[0] && i<range[0]+range[1]) shift=value;
      }
      if (shift!==prior) {
        span=document.createElementNS(ns,'tspan');
        if (shift) span.setAttribute('baseline-shift',shift<0?'sub':'super');
        text.appendChild(span);prior=shift;
      }
      span.appendChild(document.createTextNode(label.n[i]));
    }
    svg.appendChild(text);document.body.appendChild(svg);
    try {
      const box=element(text);
      if (box) {if (syntheticCache.size >= 4096) syntheticCache.clear();syntheticCache.set(key,box);}
      return box;
    } finally {svg.remove();}
  }
  function nativeCap(font, legacy) {
    try {
      const m=synthetic(font,{n:'H',j:null,k:null});
      if (m && -m.top-m.bottom>0) return (-m.top-m.bottom)/30;
    } catch (_) { /* Native UI may render before a document body exists. */ }
    state.nativeFallbacks++;return legacy;
  }
  function nativeLabel(label,font) {
    try {
      const m=synthetic(font,label);
      if (m) return {x:Math.floor(label.d*30+m.left-60)/30,
        y:Math.floor(label.e*30+m.top-60)/30,
        right:Math.ceil(label.d*30+m.right+60)/30,
        bottom:Math.ceil(label.e*30+m.bottom+60)/30};
    } catch (_) { /* Final viewer remeasures and handles unavailable geometry. */ }
    state.nativeFallbacks++;return null;
  }
  function invalidate() {cache.clear();syntheticCache.clear();state.epoch++;}
  root.NameleculeLabelMetrics={state,element,synthetic,nativeCap,nativeLabel,invalidate};
  if (document.fonts) {
    document.fonts.addEventListener('loadingdone',()=>{
      invalidate();
      root.dispatchEvent(new Event('namelecule-font-metrics-change'));
    });
    document.fonts.addEventListener('loadingerror',invalidate);
  }
})(window);
