"""Supplement: zero-tolerance Expanded glyph bounds and real radio clicks.
Reuses the browser transport and ink-bound implementation of the main check.
Artifacts under /tmp only. Requires localhost8013/BiDi9237.
"""
import ast
from pathlib import Path
src=Path('docs/checks/test-ether-refinement-browser-20261026.py').read_text()
helper=next(n.args[0].value for n in ast.walk(ast.parse(src)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ev' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and n.args[0].value.startswith('window.__etherInkBox='))
exec(compile(src.split('specs=')[0],'browser-transport','exec'))
rows=[]
try:
 navigate('mulermoc-nom-51.html?v=refinement-strict-ink');app_ready();ev(helper)
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.5)
  ev("document.getElementById('rotatePromptDismiss')?.click()")
  for key in ['ethyl_isopropyl_ether','ethyl_sec_butyl_ether','tert_butyl_isopropyl_ether']:
   ev('document.getElementById('+json.dumps(key)+').click()')
   ev('document.querySelectorAll("#radio2DMode .mode2DOption")[1].click()')
   assert ev('mode2D')=='expanded'
   result=json.loads(ev("JSON.stringify((()=>{const a=[...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].map(window.__etherInkBox);return{pairs:a.flatMap((b,i)=>a.slice(i+1).filter(c=>Math.min(b.right,c.right)>Math.max(b.left,c.left)&&Math.min(b.bottom,c.bottom)>Math.max(b.top,c.top)).map(c=>[b,c]))}})())"))
   assert not result['pairs'],(width,key,result)
   rows.append(dict(width=width,molecule=key,noGlyphInkOverlap=True,actualExpandedRadioClick=True))
   screenshot('/tmp/ether-refinement-ink-'+str(width)+'-'+key+'.png')
 assert not js_errors,js_errors
 Path('/tmp/ether-refinement-strict-ink-20261026.json').write_text(json.dumps(dict(cases=rows,javascriptErrors=js_errors),indent=2));print('PASS6 actual Expanded radio /zero-tolerance glyph bounds checks')
finally:
 call('browsingContext.close',{'context':ctx});call('session.end',{})
