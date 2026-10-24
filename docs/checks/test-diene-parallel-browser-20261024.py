"""Six-diene regression plus arbitrary-angle SVG parallelism and PNG checks."""
from pathlib import Path
source=Path('docs/checks/test-dienes-browser-20261024.py').read_text()
helper=r'''
window.__checkDieneParallels=(svg=document.querySelector('#jsmeNomeclatureSVG svg'))=>{
 const lines=svg.querySelectorAll('line');
 return bondList.every((bond,b)=>{
  if(bond[2]!==2)return true;
  const pair=[lines[svgBondList[b]-1],lines[svgBondList[b]]];if(pair.some(l=>!l))return false;
  const p=pair.map(l=>['x1','y1','x2','y2'].map(k=>Number(l.getAttribute(k))));
  const u=[p[0][2]-p[0][0],p[0][3]-p[0][1]],v=[p[1][2]-p[1][0],p[1][3]-p[1][1]];
  const n=Math.hypot(...u)*Math.hypot(...v);if(n<1)return false;
  return Math.abs(u[0]*v[1]-u[1]*v[0])/n<.002 &&
   Math.abs(u[0]*(p[1][1]-p[0][1])-u[1]*(p[1][0]-p[0][0]))/Math.hypot(...u)>.1;
 });
};
'''
needle=" assert ev('Object.keys(nameExamples).length===86')";source=source.replace(needle,' ev('+repr(helper)+')\n'+needle)
needle='    ev("[...document.querySelectorAll(\'.nameCompBox\')].forEach(e=>e.click())")';assert source.count(needle)==1
source=source.replace(needle,needle+"\n    assert ev('window.__checkDieneParallels()'),(key,mode,chain,'parallel double SVG')")
extra=r'''
 ev("document.getElementById('dimethyl_2_3_pentadiene_1_3').click()")
 until("mainChainPool3DKey==='dimethyl_2_3_pentadiene_1_3'")
 ev("window.__makeURL=URL.createObjectURL.bind(URL);URL.createObjectURL=function(blob){if(blob.type.startsWith('image/svg'))blob.text().then(s=>window.__exportSvg=s);if(blob.type==='image/png')window.__png=blob;return window.__makeURL(blob)};HTMLAnchorElement.prototype.click=function(){window.__download=this.download}")
 for mode in ['condensed','skeletal','expanded']:
  ev("mode2D="+json.dumps(mode)+";fLoadMol2D();fShowNameAnalysis();window.__png=null;window.__exportSvg=null;window.__download=null;fSave2DPng()")
  until('!!window.__png&&!!window.__exportSvg&&!!window.__download',20)
  assert ev("window.__png.size>1000&&window.__checkDieneParallels(new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').documentElement)")
  screenshot('/tmp/diene-parallel-final-'+mode+'.png')
  print('PASS '+mode+' parallel PNG Blob/export SVG',flush=True)
'''
source=source.replace(' assert not js_errors,js_errors',extra+' assert not js_errors,js_errors')
exec(compile(source,'diene-parallel-browser','exec'))
