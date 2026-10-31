"""Stress future author-provided geometry without editing any production MOL."""
from pathlib import Path
import os,json,math,gzip,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
original=json.loads((repo/'docs/checks/svg-text-root-20261031/propene.json').read_text())['annotated']
fixtures=[]
for factor in [1,.375,.1]:
 for angle in [0,45,90]:
  lines=original.split('\n');n=int(lines[3][:3]);nb=int(lines[3][3:6]);xy=[list(map(float,s[:30].split()))for s in lines[4:4+n]]
  for line in lines[4+n:4+n+nb]:
   i,j=int(line[:3])-1,int(line[3:6])-1
   if lines[4+i][31:34].strip()=='H':i,j=j,i
   if lines[4+j][31:34].strip()=='H':xy[j]=[xy[i][d]+(xy[j][d]-xy[i][d])*factor for d in range(3)]
  a=math.radians(angle)
  for i,(x,y,z)in enumerate(xy):
   coords=[x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z];lines[4+i]=''.join(f'{v:10.4f}'for v in coords)+lines[4+i][30:]
  fixtures.append({'id':f'propene-synthetic-CHfactor{factor}-rotation{angle}','factor':factor,'angle':angle,'mol':'\n'.join(lines)})
(root/'future-fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n');out={'cases':[],'faultInjection':[],'completed':False}
try:
 for version in ['baseline','candidate']:
  navigate('native-'+version+'/index.html');until('window.loaded===true');ev('document.fonts.ready.then(()=>true)');ev((repo/'docs/checks/svg-text-prototype-20261031/measure.js').read_text());ev('a.setMolecularAreaLineWidth(.6);a.setMolecularAreaScale(2);true')
  for fixture in fixtures:
   for font in [9,16]:
    ev('a.setAtomMolecularAreaFontSize('+str(font)+');a.readMolFile('+json.dumps(fixture['mol'])+');document.getElementById("export").innerHTML=a.getMolecularAreaGraphicsString();true')
    row=json.loads(ev('prototypeMeasure(true).then(r=>JSON.stringify(r))'));row.update(version=version,font=font,fixture=fixture['id'],factor=fixture['factor'],angle=fixture['angle']);out['cases'].append(row)
  # Separate fault run: same-origin iframe and top Canvas prototypes. A new
  # font size avoids a previously populated metric-cache key.
  r=json.loads(ev('JSON.stringify((()=>{let patched=0;for(const w of [window,...Array.from({length:frames.length},(_,i)=>frames[i])]){try{const p=w.CanvasRenderingContext2D.prototype,orig=p.measureText;p.measureText=function(s){let m=orig.call(this,s);return {width:m.width,actualBoundingBoxAscent:NaN,actualBoundingBoxDescent:NaN,actualBoundingBoxLeft:NaN,actualBoundingBoxRight:NaN}};patched++}catch(e){}}try{a.setAtomMolecularAreaFontSize(13);a.readMolFile('+json.dumps(original)+');let svg=a.getMolecularAreaGraphicsString();return {patched,throws:false,hasSVG:svg.includes("<svg")}}catch(e){return {patched,throws:true,error:String(e)}}})())'))
  r['version']=version;out['faultInjection'].append(r);print(version,'futurecases',18,'fault',r,flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'future.json.gz').write_bytes(gzip.compress(json.dumps(out).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('future completed',out['completed'],'cases',len(out['cases']),flush=True)
