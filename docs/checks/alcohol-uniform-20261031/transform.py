# -*- coding: utf-8 -*-
"""Expanded alcohol geometry/explicit O-H transformation from frozen source.

Pure functions on import. Existing atom and bond indices/fields are preserved;
missing O-bound hydrogens are appended. Heavy-bond drawing ratios are retained
(including the existing branch stem, with a separately approved target length).
"""
from pathlib import Path
import json,math,runpy,argparse
ROOT=Path(__file__).resolve().parents[3]
BASE=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'))
literal=BASE['literal'];parse=BASE['parse'];direction=BASE['direction'];DATA=BASE['DATA']
KEYS=['propanol_1','penten_4_ol_2','butanol_1','butene_3_ol_2','penten_2_ol_1','propanediol_1_2','propanetriol','ethanol','butanol_2','methyl_4_pentanol_2','dimethyl_2_2_pentanol_3','isopropyl_4_dimethyl_3_5_heptanol_2','methyl_2_propanediol_1_2','methyl_3_buten_3_ol_2','methyl_3_pentyn_4_ol_2','methyl_4_penten_4_yn_2_ol_1','ethyl_3_methyl_4_hexen_3_yn_5_ol_2']

def transform(mol,allow_long_stem=False,long_stem_length=None):
 if long_stem_length is not None:
  assert allow_long_stem and math.isfinite(long_stem_length) and long_stem_length>.6188
 lines,atoms,bonds=parse(mol);n=len(atoms);nb=len(bonds)
 assert set(a[2]for a in atoms)<={'C','H','O'}
 near=[[]for a in atoms]
 for a,b,o in bonds:near[a].append((b,o));near[b].append((a,o))
 oxygen=[i for i,a in enumerate(atoms)if a[2]=='O']
 assert oxygen and all(sum(atoms[j][2]=='C'for j,o in near[i])==1 and all(o==1 for j,o in near[i])for i in oxygen)
 heavy=[i for i,a in enumerate(atoms)if a[2]!='H'];edges=[(a,b,o)for a,b,o in bonds if atoms[a][2]!='H'and atoms[b][2]!='H'];assert len(edges)==len(heavy)-1
 lengths=sorted(math.dist(atoms[a][:2],atoms[b][:2])for a,b,o in edges);unit=lengths[len(lengths)//2];ratio={}
 for a,b,o in edges:
  value=math.dist(atoms[a][:2],atoms[b][:2])/unit;units=round(value)
  assert units in [1,2] and abs(value-units)<.001
  if units!=1 and not allow_long_stem:raise ValueError('Existing long stem requires explicit approval')
  ratio[frozenset([a,b])]=units
 scale=.6188/unit;root=heavy[0];xy={root:(round(atoms[root][0]*scale,4),round(atoms[root][1]*scale,4))};pending=[root]
 while pending:
  a=pending.pop()
  for b,o in near[a]:
   if atoms[b][2]=='H'or b in xy:continue
   dx,dy=direction(atoms[a],atoms[b]);units=ratio[frozenset([a,b])]
   length=long_stem_length if units!=1 and long_stem_length is not None else .6188*units
   xy[b]=(round(xy[a][0]+dx*length,4),round(xy[a][1]+dy*length,4));pending.append(b)
 assert all(i in xy for i in heavy)
 for i,a in enumerate(atoms):
  if a[2]!='H':continue
  assert len(near[i])==1
  parent=near[i][0][0];dx,dy=direction(atoms[parent],a)
  xy[i]=(round(xy[parent][0]+dx*.3094,4),round(xy[parent][1]+dy*.3094,4))
 added=[]
 for i in oxygen:
  hs=[j for j,o in near[i]if atoms[j][2]=='H'];assert len(hs)<=1
  if hs:continue
  assert len(near[i])==1
  parent=near[i][0][0];dx,dy=direction(atoms[parent],atoms[i])
  # Continue the existing C-O direction, using an explicit atom and bond.
  point=(round(xy[i][0]+dx*.3094,4),round(xy[i][1]+dy*.3094,4))
  assert point not in xy.values(),('New OH hydrogen collision',i+1)
  idx=n+len(added);xy[idx]=point;added.append((i,idx))
 assert len(set(xy.values()))==len(xy),'Coincident atoms; refuse geometry'
 for i in range(n):
  x,y=xy[i];lines[4+i]='%10.4f%10.4f'%(0.0 if not x else x,0.0 if not y else y)+lines[4+i][20:]
 new_atoms=[];new_bonds=[]
 for oxygen,idx in added:
  x,y=xy[idx]
  new_atoms.append('%10.4f%10.4f%10.4f H   0  0  0  0  0  0  0  0  0  0  0  0\n'%(x,y,0.0))
  new_bonds.append('%3d%3d%3d%3d  0  0  0\n'%(oxygen+1,idx+1,1,0))
 lines[3]='%3d%3d'%(n+len(added),nb+len(added))+lines[3][6:]
 return ''.join(lines[:4+n]+new_atoms+lines[4+n:4+n+nb]+new_bonds+lines[4+n+nb:])

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--apply',action='store_true');p.add_argument('--allow-long-stem',action='store_true');p.add_argument('--long-stem-length',type=float);p.add_argument('--exclude-pending-large',action='store_true');args=p.parse_args();source=args.original;code=(source/DATA).read_text();results={}
 for key in KEYS:
  if args.exclude_pending_large and key=='isopropyl_4_dimethyl_3_5_heptanol_2':continue
  m,mol=literal(code,key);code=code[:m.start(1)]+json.dumps(transform(mol,args.allow_long_stem,args.long_stem_length))+code[m.end(1):]
 results[DATA]=code
 for path in (source/'mols').rglob('*.mol'):
  if args.exclude_pending_large and path.name=='isopropyl_4_dimethyl_3_5_heptanol_2_2D_Expanded.mol':continue
  results[str(path.relative_to(source))]=transform(path.read_text(),args.allow_long_stem,args.long_stem_length)
 if args.apply:
  for name in results:assert Path(name).read_bytes()==(source/name).read_bytes(),('Baseline changed',name)
  for name,content in results.items():Path(name).write_text(content)
 print(json.dumps({'sources':len(results),'applied':args.apply}))
