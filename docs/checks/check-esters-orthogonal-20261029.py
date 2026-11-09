"""Validate the five approved expanded-only coordinate changes and all orthogonal bonds."""
from pathlib import Path
import argparse,hashlib,json,math,subprocess
parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
specs=json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())
def embedded(text):
 code='var window={};'+text+';print(JSON.stringify(window.MOL2D));'
 p=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',capture_output=True,text=True,check=True)
 return json.loads(p.stdout)
data='js/jsme-nick-nomeclature-moc2-data_52.js';old=embedded((args.baseline/data).read_text());new=embedded(Path(data).read_text())
assert set(old)==set(new)
keys={s['key']for s in specs}
for key in old:
 for mode in old[key]:
  if key not in keys or mode!='expanded':assert old[key][mode]==new[key][mode],(key,mode)
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def delta(a,b):return(a[0]-b[0],a[1]-b[1])
def intersection(a,b,c,d):
 u,v=delta(b,a),delta(d,c);den=cross(u,v)
 if abs(den)<1e-9:
  if abs(cross(delta(c,a),u))>1e-6:return False
  ll=sum(t*t for t in u);ts=[sum(x*y for x,y in zip(delta(p,a),u))/ll for p in[c,d]]
  return min(1,max(ts))-max(0,min(ts))>1e-5
 t=cross(delta(c,a),v)/den;q=cross(delta(c,a),u)/den
 return -1e-6<=t<=1+1e-6 and -1e-6<=q<=1+1e-6
rows=[];allowed={data,'mulermoc-nom-52.html','docs/checks/generate-esters-20261029.py'}
for spec in specs:
 path=Path('mols/new_molecules')/(spec['key']+'_2D_Expanded.mol');allowed.add(str(path))
 a=(args.baseline/path).read_text().splitlines();b=path.read_text().splitlines();n=int(b[3][:3]);nb=int(b[3][3:6])
 assert a[:4]==b[:4]and a[4+n:]==b[4+n:]and all(x[20:]==y[20:]for x,y in zip(a[4:4+n],b[4:4+n]))
 assert path.read_text()==new[spec['key']]['expanded']
 pts=[(float(s[:10]),float(s[10:20]))for s in b[4:4+n]];edges=[(int(s[:3])-1,int(s[3:6])-1)for s in b[4+n:4+n+nb]]
 for index,(i,j) in enumerate(edges):
  dx,dy=delta(pts[i],pts[j]);assert (abs(dx)<1e-6)!=(abs(dy)<1e-6),(path,i,j,dx,dy)
  for k,l in edges[:index]:
   if len({i,j,k,l})==4:assert not intersection(pts[i],pts[j],pts[k],pts[l]),(path,'crossing',i,j,k,l)
  u=delta(pts[j],pts[i]);length2=sum(t*t for t in u)
  for k in range(n):
   if k in [i,j]:continue
   t=sum(x*y for x,y in zip(delta(pts[k],pts[i]),u))/length2
   if .02<t<.98:assert math.dist(pts[k],(pts[i][0]+t*u[0],pts[i][1]+t*u[1]))>.15,(path,'atom on bond',k,i,j)
 nearest=min(math.dist(pts[i],pts[j])for i in range(n)for j in range(i)if(i,j)not in edges and(j,i)not in edges);assert nearest>1,(path,nearest)
 if spec['key']=='tert_butyl_methanoate':assert pts[7][0]<pts[0][0]and pts[7][1]==pts[0][1]
 rows.append({'key':spec['key'],'atoms':n,'orthogonalBonds':nb,'nearestNonbonded':nearest,'indexedGraphUnchanged':True})
hashes=json.loads((args.baseline.parent/'before-hashes.json').read_text());preserved={p:h for p,h in hashes.items()if p not in allowed}
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in preserved.items())
result={'passed':True,'rows':rows,'orthogonalBonds':sum(r['orthogonalBonds']for r in rows),'otherEmbeddedMoleculesUnchanged':len(new)-5,'nonExpandedFormsUnchanged':True,'preservedHashes':preserved}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS five expanded source/embedded graphs;',result['orthogonalBonds'],'orthogonal bonds; all other forms/old esters/core/viewer/3D unchanged')
