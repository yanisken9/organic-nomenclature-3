"""Approved expanded ether drawing units, rebuilt from frozen original MOLs.

Only x/y fields change. Keep original directions (including slight departures
from the axes in the professor's isopropylmethyl ether), IDs and bond fields.
Import is pure; --apply refuses any unexpected source changes.
"""
from pathlib import Path
import argparse,gzip,json,math,runpy
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'))
parse=BASE['parse'];literal=BASE['literal'];DATA=BASE['DATA']
KEYS=['dimethylether','ethyl_methyl_ether','diethyl_ether','isopropyl_methyl_ether',
      'methyl_propyl_ether','ethyl_propyl_ether','ethyl_isopropyl_ether',
      'butyl_methyl_ether','ethyl_sec_butyl_ether','isobutyl_isopropyl_ether',
      'tert_butyl_isopropyl_ether']
def transform(mol):
    lines,atoms,bonds=parse(mol);n=len(atoms);near=[[]for _ in atoms]
    assert n and len(bonds)==n-1 and {a[2]for a in atoms}=={'C','H','O'}
    for a,b,order in bonds:
        assert order==1;near[a].append(b);near[b].append(a)
    for i,a in enumerate(atoms):assert len(near[i])=={'C':4,'O':2,'H':1}[a[2]]
    oxygen=[i for i,a in enumerate(atoms)if a[2]=='O'];assert len(oxygen)==1
    assert all(atoms[j][2]=='C'for j in near[oxygen[0]])
    heavy=[i for i,a in enumerate(atoms)if a[2]!='H']
    lengths=sorted(math.dist(atoms[a][:2],atoms[b][:2])for a,b,_ in bonds
                   if atoms[a][2]!='H'and atoms[b][2]!='H')
    scale=.6188/lengths[len(lengths)//2];root=heavy[0]
    xy={root:(atoms[root][0]*scale,atoms[root][1]*scale)};pending=[root]
    def add(a,b,length):
        dx=atoms[b][0]-atoms[a][0];dy=atoms[b][1]-atoms[a][1];r=math.hypot(dx,dy)
        assert r>0;xy[b]=(xy[a][0]+length*dx/r,xy[a][1]+length*dy/r)
    while pending:
        a=pending.pop()
        for b in near[a]:
            if atoms[b][2]=='H'or b in xy:continue
            add(a,b,.6188);pending.append(b)
    assert all(a in xy for a in heavy)
    for i,a in enumerate(atoms):
        if a[2]=='H':add(near[i][0],i,.3094)
    assert len(xy)==n
    xy={i:tuple(round(v,4)for v in point)for i,point in xy.items()}
    assert len(set(xy.values()))==n,'Coincident atoms; refuse transformation'
    for i in range(n):
        x,y=xy[i];lines[4+i]='%10.4f%10.4f'%(x if x else 0.,y if y else 0.)+lines[4+i][20:]
    return ''.join(lines)
def outputs():
    source=json.load(gzip.open(HERE/'before-sources.json.gz','rt'));code=source[DATA]
    for key in KEYS:
        m,mol=literal(code,key);code=code[:m.start(1)]+json.dumps(transform(mol))+code[m.end(1):]
    result={DATA:code}
    for p,mol in source.items():
        if p.endswith('.mol'):result[p]=transform(mol)
    return source,result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args()
    original,result=outputs()
    if args.apply:
        for path in result:assert(ROOT/path).read_bytes()==original[path].encode(),('Baseline changed',path)
        for path,content in result.items():(ROOT/path).write_text(content)
    print(json.dumps({'keys':len(KEYS),'changedDataAndMOLs':len(result),'applied':args.apply}))
