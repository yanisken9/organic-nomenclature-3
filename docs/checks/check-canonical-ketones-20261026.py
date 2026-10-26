"""Rigid geometry and full naming/old-data protection for skeletal rotations."""
from pathlib import Path
import json,math,hashlib,subprocess,runpy
from rdkit import Chem
base=Path('/tmp/namelecule-before-canonical-ketones-20261026')
datafile=Path('js/jsme-nick-nomeclature-moc2-data_51.js')
mod=runpy.run_path('docs/checks/align-other-ketones-skeletal-20261026.py')
before=mod['extract'](base/datafile);after=mod['extract'](datafile);rows=[]
for a,b in zip(before,after):
 assert a['key']==b['key'] and a['chain']==b['chain']
 key=a['key'];ls=a['mol'].splitlines();ls2=b['mol'].splitlines();n=int(ls[3][:3])
 assert ls[:4]==ls2[:4] and ls[4+n:]==ls2[4+n:]
 assert all(x[20:]==y[20:]for x,y in zip(ls[4:4+n],ls2[4:4+n]))
 p=[(float(l[:10]),float(l[10:20]))for l in ls[4:4+n]];q=[(float(l[:10]),float(l[10:20]))for l in ls2[4:4+n]]
 error=max(abs(math.dist(p[i],p[j])-math.dist(q[i],q[j]))for i in range(n)for j in range(i))
 assert error<.0002,(key,error)
 old=Chem.MolFromMolBlock(a['mol'],removeHs=False);new=Chem.MolFromMolBlock(b['mol'],removeHs=False);assert old and new
 assert Chem.MolToSmiles(old)==Chem.MolToSmiles(new)
 from rdkit.Chem import rdMolTransforms
 angles=[]
 for atom in old.GetAtoms():
  ns=[x.GetIdx()for x in atom.GetNeighbors()]
  for i,u in enumerate(ns):
   for v in ns[:i]:angles.append(abs(rdMolTransforms.GetAngleDeg(old.GetConformer(),u,atom.GetIdx(),v)-rdMolTransforms.GetAngleDeg(new.GetConformer(),u,atom.GetIdx(),v)))
 assert max(angles)<.03,(key,angles)
 offsets_before=mod['corrections'](ls);offsets_after=mod['corrections'](ls2)
 assert max(abs(t)for t in offsets_after)<.02,(key,offsets_after)
 if key in mod['TARGETS']:
  assert max(abs(t)for t in offsets_before)>.02
  assert mod['rotate'](a)[0]==b['mol'],key
 else:assert a['mol']==b['mol']
 # Keep legacy ChemDraw angles; six other drawings use the familiar +/-30 axes.
 tilts=[]
 for u,v in zip(a['chain'],a['chain'][1:]):
  dx,dy=q[v-1][0]-q[u-1][0],q[v-1][1]-q[u-1][1]
  tilt=(math.degrees(math.atan2(dy,dx))+90)%180-90
  tilts.append(tilt)
  if key=='pentyn_4_one_2':
   assert min(abs(abs(tilt)-15),abs(abs(tilt)-30))<.03,(key,tilt)
  else:assert abs(abs(tilt)-30)<.03,(key,tilt)
 # Idempotent: a second application does not move rounded coordinates.
 assert mod['rotate'](b)[0]is None,key
 f=Path('mols/new_molecules')/(key+'_2D_Skeletal.mol')
 if f.exists():assert f.read_text()==b['mol']
 rows.append(dict(key=key,carbonylCorrectionsBefore=offsets_before,carbonylCorrectionsAfter=offsets_after,parentBondTilts=tilts,maxPairDistanceDelta=error,maxAngleDelta=max(angles)))
# Exact records and every other molecular representation are protected semantically.
def obj(src):return 'var window={};'+src+';return {records:nameExamples,mols:window.MOL2D};'
js='var old=(new Function('+json.dumps(obj((base/datafile).read_text()))+'))(),cur=(new Function('+json.dumps(obj(datafile.read_text()))+'))();var targets='+json.dumps(mod['TARGETS'])+';for(var k of Object.keys(old.records)){if(JSON.stringify(old.records[k])!==JSON.stringify(cur.records[k]))throw Error(k+" record");for(var m of Object.keys(old.mols[k]))if(!(m==="skeletal"&&targets.includes(k))&&old.mols[k][m]!==cur.mols[k][m])throw Error(k+" "+m);}print(JSON.stringify({records:Object.keys(old.records).length}));'
def jsc(js):
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
 return json.loads(r.stdout)
assert jsc(js)['records']==126
# Reuse the real applet adapter and run every available form/chain-mode before/after.
ns={};exec(Path('docs/checks/test-other-ketones-naming-20261026.py').read_text().split('base=Path(')[0],ns)
tail=ns['tail'];tail=tail[:tail.index('if(!probe){fParseSDF3D')]
ret='return {name:currentMolName,parts:nameComponentsList,chain:mainChainAtomsList,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)};'
shared='\n'.join(Path(p).read_text()for p in ['js/mulermoc-nom-core-51.js','js/mulermoc-nom-molview-51.js'])
body=lambda data:ns['prefix']+data+'\n'+shared+tail+ret
js='var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body((base/datafile).read_text()))+'),after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body(datafile.read_text()))+');var obj=(new Function('+json.dumps(obj(datafile.read_text()))+'))(),n=0;for(var k of Object.keys(obj.records))for(var m of Object.keys(obj.mols[k]))if(obj.mols[k][m])for(var c of ["algorithmic","data"]){var a=[k,m,c,"",null],b=before.apply(null,a),d=after.apply(null,a);if(JSON.stringify(b)!==JSON.stringify(d))throw Error(JSON.stringify([a,b,d]));n++;}print(JSON.stringify({namingCases:n}));'
cases=jsc(js)['namingCases']
allowed={'js/jsme-nick-nomeclature-moc2-data_51.js','mulermoc-nom-51.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}|{'mols/new_molecules/'+k+'_2D_Skeletal.mol'for k in mod['TARGETS']}
protected=0
for p,h in json.loads((base/'hashes.json').read_text()).items():
 if p in allowed:continue
 assert Path(p).is_file()and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
 protected+=1
out=dict(geometry=rows,recordsUnchanged=126,namingCasesUnchanged=cases,protectedFiles=protected,checksPassed=True)
Path('docs/checks/canonical-ketones-static-20261026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS 7 skeleton geometries/126records;',cases,'naming cases;',protected,'protected files')
