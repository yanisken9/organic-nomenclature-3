"""Targeted atom/bond invariants and deterministic rebuild, native producer only."""
from pathlib import Path
import os,json,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-prototype-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8025/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
fixtures=json.loads((here/'fixtures.json').read_text());out={'cases':[],'rebuild':[],'completed':False}
snapshot=r'''(()=>{const m=a.g.b.r,base=m.b[1];return {atoms:Array.from({length:m.q},(_,i)=>{let v=m.b[i+1];return {index:i+1,x:v.s-base.s,y:v.u-base.u,element:v.c,label:v.i||null,charge:v.p||0,isotope:v.f||0}}),bonds:Array.from({length:m.r},(_,i)=>{let v=m.c[i+1];return [v.j,v.k,v.d]}),mol:a.molFile()}})()'''
try:
 for version in ['baseline','candidate']:
  navigate(version+'/index.html');until('window.loaded===true');ev('document.fonts.ready.then(()=>true)');ev('a.setMolecularAreaLineWidth(.6);a.setMolecularAreaScale(2);true')
  for fixture in fixtures:
   for font in [9,12,14,16]:
    ev('a.setAtomMolecularAreaFontSize('+str(font)+');a.readMolFile('+json.dumps(fixture['mol'])+');document.getElementById("export").innerHTML=a.getMolecularAreaGraphicsString();true')
    item=json.loads(ev('JSON.stringify('+snapshot+')'));item.update(version=version,fixture=fixture['id'],font=font);out['cases'].append(item)
  # Rebuild same molecule after switching away, font and viewport changes.
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
   ev('a.setSize("'+str(min(width-30,600))+'px","400px");a.setAtomMolecularAreaFontSize(9);a.readMolFile('+json.dumps(fixtures[1]['mol'])+');true')
   first=ev('a.getMolecularAreaGraphicsString()')
   ev('a.readMolFile('+json.dumps(fixtures[-1]['mol'])+');a.setAtomMolecularAreaFontSize(16);a.setAtomMolecularAreaFontSize(9);a.readMolFile('+json.dumps(fixtures[1]['mol'])+');true')
   out['rebuild'].append({'version':version,'width':width,'sameSVG':first==ev('a.getMolecularAreaGraphicsString()')})
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'])
finally:
 out['javascriptErrors']=js_errors;(root/'invariants.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'rebuild':out['rebuild'],'errors':len(js_errors)}))
if not out['completed']:raise SystemExit(1)
