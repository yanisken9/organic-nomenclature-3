"""Real Firefox native-producer comparison. No Namelecule viewer/postprocessing."""
from pathlib import Path
import os,json,time,traceback,gzip,hashlib
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-prototype-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8025/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
fixtures=json.loads((here/'fixtures.json').read_text());result={'cases':[],'completed':False,'scope':'native Firefox permutation; no production application change'}
try:
 for version in ['baseline','candidate']:
  navigate(version+'/index.html');until('window.loaded===true',seconds=30);ev('document.fonts.ready.then(()=>true)');ev((here/'measure.js').read_text())
  ev('a.setMolecularAreaLineWidth(.6);a.setMolecularAreaScale(2);true')
  for fixture in fixtures:
   for font in [9,12,14,16]:
    t=time.monotonic();ev('a.setAtomMolecularAreaFontSize('+str(font)+');a.readMolFile('+json.dumps(fixture['mol'])+');document.getElementById("export").innerHTML=a.getMolecularAreaGraphicsString();true')
    draw_ms=(time.monotonic()-t)*1000
    row=json.loads(ev('prototypeMeasure(true).then(r=>JSON.stringify(r))'));row.update(version=version,fixture=fixture['id'],font=font,drawAndTransportMs=round(draw_ms,2));result['cases'].append(row)
   print(version,fixture['id'],'done',flush=True)
  if version=='candidate':
   ev('a.setAtomMolecularAreaFontSize(9);a.readMolFile('+json.dumps(fixtures[1]['mol'])+');document.getElementById("export").innerHTML=a.getMolecularAreaGraphicsString();true')
  screenshot(str(root/(version+'-tested.png')))
 result['completed']=True
except Exception as e:result['failure']=str(e);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors
 (root/'browser.json.gz').write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'errors':len(js_errors)}),flush=True)
if not result['completed']:raise SystemExit(1)
