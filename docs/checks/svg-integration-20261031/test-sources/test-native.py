from pathlib import Path
import os,json,gzip,traceback
r=Path('/tmp/namelecule-svg-integration-20261031');repo=Path.cwd();os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
fixtures=json.loads((repo/'docs/checks/svg-text-prototype-20261031/fixtures.json').read_text());prior=json.loads(gzip.decompress((repo/'docs/checks/svg-text-prototype-20261031/invariants.json.gz').read_bytes()));old={(c['fixture'],c['font']):c for c in prior['cases']if c['version']=='baseline'}
out={'cases':[],'completed':False,'reference':'earlier pinned original-module native invariants; same fixtures/fonts/viewport'}
snapshot=r'''(()=>{const m=a.g.b.r,base=m.b[1];return {atoms:Array.from({length:m.q},(_,i)=>{let v=m.b[i+1];return {index:i+1,x:v.s-base.s,y:v.u-base.u,element:v.c,label:v.i||null,charge:v.p||0,isotope:v.f||0}}),bonds:Array.from({length:m.r},(_,i)=>{let v=m.c[i+1];return [v.j,v.k,v.d]}),mol:a.molFile()}})()'''
try:
 navigate('native-main/index.html');until('window.loaded===true');ev('document.fonts.ready.then(()=>true)');ev((repo/'docs/checks/svg-text-prototype-20261031/measure.js').read_text());ev('a.setMolecularAreaLineWidth(.6);a.setMolecularAreaScale(2);true')
 for f in fixtures:
  for font in [9,12,14,16]:
   ev('a.setAtomMolecularAreaFontSize('+str(font)+');a.readMolFile('+json.dumps(f['mol'])+');document.getElementById("export").innerHTML=a.getMolecularAreaGraphicsString();true')
   state=json.loads(ev('JSON.stringify('+snapshot+')'));row=json.loads(ev('prototypeMeasure(true).then(v=>JSON.stringify(v))'));row.update(fixture=f['id'],font=font,state=state)
   b=old[f['id'],font];assert state['bonds']==b['bonds'] and len(state['atoms'])==len(b['atoms'])
   for x,y in zip(state['atoms'],b['atoms']):
    assert all(x[k]==y[k]for k in ['index','element','label','charge','isotope']);assert abs(x['x']-y['x'])<1e-8 and abs(x['y']-y['y'])<1e-8
   assert '\n'.join(state['mol'].split('\n')[3:])=='\n'.join(b['mol'].split('\n')[3:])
   row['chemicalAndCoordinateInvariants']=True;out['cases'].append(row);assert not row['raster']['uncoveredInkPixels']and not row['raster']['inkPixelsWithin2pxOfBond']and not row['raster']['hiddenLines'],(f['id'],font,row['raster'])
  print('native',f['id'],'passed',flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'native.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('native',out['completed'],'cases',len(out['cases']),'errors',len(js_errors),flush=True)
