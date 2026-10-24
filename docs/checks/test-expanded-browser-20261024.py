"""Extend the six-diene browser regression with display-only parallel bonds/PNG.
Uses the existing local Firefox BiDi test; writes only /tmp screenshots/artifacts.
"""
from pathlib import Path
source=Path('docs/checks/test-dienes-browser-20261024.py').read_text()
helper=r'''
window.__checkExpandedParallels=(svg=document.querySelector('#jsmeNomeclatureSVG svg'))=>{
 const lines=svg.querySelectorAll('line');
 return bondList.every((bond,b)=>{
  if(bond[2]!==2)return true;
  const pair=[lines[svgBondList[b]-1],lines[svgBondList[b]]];
  if(pair.some(l=>!l))return false;
  const ys=pair.map(l=>[Number(l.getAttribute('y1')),Number(l.getAttribute('y2'))]);
  return ys.every(y=>Math.abs(y[0]-y[1])<.001)&&Math.abs(ys[0][0]-ys[1][0])>.1;
 });
};
'''
needle=" assert ev('Object.keys(nameExamples).length===86')"
source=source.replace(needle," ev("+repr(helper)+")\n"+needle)
needle='    ev("[...document.querySelectorAll(\'.nameCompBox\')].forEach(e=>e.click())")'
assert source.count(needle)==1
source=source.replace(needle,needle+"\n    if mode=='expanded':assert ev('window.__checkExpandedParallels()'),(key,chain,'parallel SVG')")
png=r'''
 ev("mode2D='expanded';fLoadMol2D();fShowNameAnalysis();window.__png=null;window.__exportSvg=null;window.__download=null;window.__makeURL=URL.createObjectURL.bind(URL);URL.createObjectURL=function(blob){if(blob.type.startsWith('image/svg'))blob.text().then(s=>window.__exportSvg=s);if(blob.type==='image/png')window.__png=blob;return window.__makeURL(blob)};HTMLAnchorElement.prototype.click=function(){window.__download=this.download};fSave2DPng()")
 until("!!window.__png && !!window.__exportSvg && !!window.__download",20)
 assert ev("window.__png.size>1000&&window.__checkExpandedParallels(new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').documentElement)")
 print('PASS expanded parallel SVG after component clicks and actual PNG blob/exported SVG',flush=True)
'''
source=source.replace(' assert not js_errors,js_errors',png+' assert not js_errors,js_errors')
exec(compile(source,'expanded-browser-regression','exec'))
