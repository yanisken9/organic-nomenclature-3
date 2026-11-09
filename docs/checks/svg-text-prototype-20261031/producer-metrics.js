/* ISOLATED EXPERIMENT ONLY. Called inside JSME EQ, before native rendering.
   Pin to the reviewed Firefox permutation; not a production vendor update. */
var nProtoMetrics = {cache:Object.create(null), measures:0, hits:0};
function nProtoMeasure(font, label) {
  var scale=30, size=Math.round(font.b*scale), key=JSON.stringify([font.a,font.c,size,label.n,label.j,label.k]);
  if(nProtoMetrics.cache[key]) {nProtoMetrics.hits++;return nProtoMetrics.cache[key];}
  var ns='http://www.w3.org/2000/svg', svg=document.createElementNS(ns,'svg'), text=document.createElementNS(ns,'text');
  svg.style.cssText='position:absolute;left:-100000px;top:0;opacity:0;pointer-events:none';
  svg.setAttribute('width','10000');svg.setAttribute('height','10000');
  text.setAttribute('x','0');text.setAttribute('y','0');text.setAttribute('font-family',font.a);
  text.setAttribute('font-size',size+'px');
  if(font.c&1)text.setAttribute('font-weight','bold');
  if(font.c&2)text.setAttribute('font-style','italic');
  var str=label.n, ranges=[[-1,label.j],[1,label.k]], prev=99, span;
  for(var i=0;i<str.length;i++) {
    var shift=0;
    for(var r=0;r<ranges.length;r++) for(var j=0;j<(ranges[r][1]||[]).length;j++) {
      var range=ranges[r][1][j];if(i>=range[0]&&i<range[0]+range[1])shift=ranges[r][0];
    }
    if(shift!==prev){span=document.createElementNS(ns,'tspan');if(shift)span.setAttribute('baseline-shift',shift<0?'sub':'super');text.appendChild(span);prev=shift;}
    span.appendChild(document.createTextNode(str[i]));
  }
  svg.appendChild(text);document.body.appendChild(svg);
  try {
    var canvas=nProtoMetrics.canvas||(nProtoMetrics.canvas=document.createElement('canvas').getContext('2d'));
    var css=getComputedStyle(text);canvas.font=css.fontStyle+' '+css.fontWeight+' '+size+'px '+css.fontFamily;
    var left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity;
    for(var k=0;k<str.length;k++) {
      var p=text.getStartPositionOfChar(k), m=canvas.measureText(str[k]);
      if(!Number.isFinite(m.actualBoundingBoxAscent)||!Number.isFinite(m.actualBoundingBoxLeft))throw Error('Missing actual glyph bounds');
      left=Math.min(left,p.x-m.actualBoundingBoxLeft);right=Math.max(right,p.x+m.actualBoundingBoxRight);
      top=Math.min(top,p.y-m.actualBoundingBoxAscent);bottom=Math.max(bottom,p.y+m.actualBoundingBoxDescent);
    }
    var cap=canvas.measureText('H');
    var out={left:left/scale,right:right/scale,top:top/scale,bottom:bottom/scale,cap:(cap.actualBoundingBoxAscent-cap.actualBoundingBoxDescent)/scale};
    if(!Number.isFinite(out.cap)||out.cap<=0)throw Error('Invalid font metrics');
    nProtoMetrics.measures++;return nProtoMetrics.cache[key]=out;
  } finally {svg.remove();}
}
function nProtoCap(font){return nProtoMeasure(font,{n:'H',j:null,k:null}).cap;}
function nProtoLabel(label,font){
  var m=nProtoMeasure(font,label), pad=2;
  // Same native label coordinates feed the painter and molecular framing.
  // Outward rounding accounts for JSME integer SVG coordinate serialization.
  var x=Math.floor((label.d+m.left-pad)*30)/30;
  var y=Math.floor((label.e+m.top-pad)*30)/30;
  var right=Math.ceil((label.d+m.right+pad)*30)/30;
  var bottom=Math.ceil((label.e+m.bottom+pad)*30)/30;
  label.a=new hR(x,y,right-x,bottom-y);
}
