"""Actual naming harness + all-library transient skeletal geometry and invariants."""
from pathlib import Path
import json,subprocess,gzip,base64,math,hashlib,sys
ns={};exec(Path('docs/checks/test-other-acids-naming-20261028.py').read_text().split("\njs='var run")[0],ns)
files=ns['files'];prefix=ns['prefix'];tail=ns['tail'];ret=ns['ret']
base={p:base64.b64decode(v).decode() for p,v in json.loads(gzip.decompress(Path('docs/checks/skeletal-layout-before-source-20261028.json.gz').read_bytes())).items()}
viewer=Path(files[2]).read_text();pure=viewer.split('// BEGIN SKELETAL GEOMETRY')[1].split('// END SKELETAL GEOMETRY')[0]
old=prefix+'\n'.join(base[p] if p in base else Path(p).read_text() for p in files)+tail+ret
new=prefix+'\n'.join(Path(p).read_text() for p in files)+tail+ret
extract='var window={};'+Path(files[0]).read_text()+';return window.MOL2D;'
js='var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(old)+'),after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(new)+');var inventory=(new Function('+json.dumps(extract)+'))();'+pure
sdfs={p.stem[:-3]:p.read_text() for p in Path('mols/nomeclature-moc2').glob('*_3D.sdf')}
js+='var sdfs='+json.dumps(sdfs)+';var names=0,rows=[];for(var key of Object.keys(inventory)){for(var mode of Object.keys(inventory[key])){if(!inventory[key][mode])continue;for(var chainMode of ["algorithmic","data"]){var args=[key,mode,chainMode,sdfs[key],null];var a=before.apply(null,args),b=after.apply(null,args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error("Naming changed:"+key+mode+chainMode);names++;if(mode==="skeletal"){var layout=fSkeletalLayoutMol(inventory[key][mode],b.chain);rows.push({key:key,chainMode:chainMode,chain:b.chain,source:inventory[key][mode],layout:layout});}}}}print(JSON.stringify({names:names,rows:rows}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
obj=json.loads(r.stdout);assert obj['names']==802 and len(obj['rows'])==266

def geometry(text):
 ls=text.splitlines();n=int(ls[3][:3]);nb=int(ls[3][3:6]);pts=[(float(l[:10]),float(l[10:20])) for l in ls[4:4+n]];bonds=[(int(l[:3])-1,int(l[3:6])-1,int(l[6:9]))for l in ls[4+n:4+n+nb]];adj=[[]for _ in pts]
 for a,b,o in bonds:adj[a].append(b);adj[b].append(a)
 return ls,n,pts,bonds,adj

def angle(p,c,a,b):
 u=(p[a][0]-p[c][0],p[a][1]-p[c][1]);v=(p[b][0]-p[c][0],p[b][1]-p[c][1]);den=math.hypot(*u)*math.hypot(*v)
 return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(u,v))/den)))) if den>1e-9 else None

repairs=[];sp_angles=[];improved=0
for row in obj['rows']:
 old,n,p,bonds,adj=geometry(row['source']);new,nn,q,_,_=geometry(row['layout']['mol']);assert n==nn
 assert old[:4]==new[:4] and old[4+n:]==new[4+n:]
 assert all(a[20:]==b[20:]for a,b in zip(old[4:4+n],new[4:4+n]))
 for a,b,_ in bonds:assert abs(math.dist(p[a],p[b])-math.dist(q[a],q[b]))<.0003,(row['key'],'length')
 fixed={x['atom']-1 for x in row['layout']['repairs']}
 for c,neighbors in enumerate(adj):
  for i,a in enumerate(neighbors):
   for b in neighbors[:i]:
    x=angle(p,c,a,b);y=angle(q,c,a,b)
    if c not in fixed and x is not None:assert abs(x-y)<.04,(row['key'],'angle',c,x,y)
 for a,b,o in bonds:
  if o==3:
   for c in [a,b]:
    if len(adj[c])==2:
     value=angle(q,c,*adj[c]);assert value is not None and value>179.94,(row['key'],'sp',c,value);sp_angles.append(value)
 chain=[i-1 for i in row['chain']]
 if len(chain)>=2:
  assert q[chain[-1]][0]>=q[chain[0]][0]-.0002,(row['key'],'direction')
  h0=max(p[i][1]for i in chain)-min(p[i][1]for i in chain);h1=max(q[i][1]for i in chain)-min(q[i][1]for i in chain)
  if not fixed:assert h1<=h0+.0003,(row['key'],'height',h0,h1)
  if h1<h0-.001:improved+=1
 assert not row['layout']['skipped'],(row['key'],'unsafe repair')
 repairs.extend(dict(key=row['key'],mode=row['chainMode'],**x)for x in row['layout']['repairs'])
basehash=json.loads(Path('docs/checks/skeletal-layout-before-20261028.json').read_text())
protected=[p for p in basehash if p.startswith(('mols/','scenarios/')) or p=='js/jsme-nick-nomeclature-moc2-data_52.js' or 'core-'in p]
for p in protected:assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==basehash[p],p
result=dict(namingCases=obj['names'],skeletalCases=len(obj['rows']),availableSkeletalForms=133,heightImprovedCases=improved,spAnglesChecked=len(sp_angles),minimumSpAngle=min(sp_angles),repairs=repairs,protectedFilesUnchanged=len(protected),allChecksPassed=True)
if '--read-only' not in sys.argv:
 Path('docs/checks/skeletal-layout-static-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 Path('/tmp/namelecule-skeletal-layout-20261028/transformed.json').write_text(json.dumps(obj,ensure_ascii=False))
print(json.dumps(result,ensure_ascii=False))
