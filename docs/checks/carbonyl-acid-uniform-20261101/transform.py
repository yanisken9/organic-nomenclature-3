"""Approved coordinate-only Main integration, rebuilt from frozen originals.

Eight visually accepted MOLs are used byte-for-byte; all other drawings retain
their original bond directions. No import-time writes or cumulative transforms.
"""
from pathlib import Path
import argparse,gzip,json,hashlib,math,runpy
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
base=json.loads((HERE/'baseline.json').read_text())
h=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'))
parse=h['parse'];literal=h['literal'];DATA=h['DATA'];KEYS=base['keys']
def uniform(mol):
    lines,atoms,bonds=parse(mol);near=[[]for _ in atoms]
    assert len(bonds)==len(atoms)-1
    for a,b,o in bonds:near[a].append(b);near[b].append(a)
    xy={0:(0.,0.)};pending=[0]
    while pending:
        a=pending.pop()
        for b in near[a]:
            if b in xy:continue
            dx,dy=atoms[b][0]-atoms[a][0],atoms[b][1]-atoms[a][1]
            r=math.hypot(dx,dy);assert r>0 and min(abs(dx),abs(dy))<r*.001
            target=.3094 if 'H'in[atoms[a][2],atoms[b][2]]else .6188
            xy[b]=(xy[a][0]+target*dx/r,xy[a][1]+target*dy/r);pending.append(b)
    assert len(xy)==len(atoms)
    points={i:tuple(round(v,4)for v in p)for i,p in xy.items()}
    assert len(set(points.values()))==len(atoms),'Coincident atoms; refuse normalization'
    for i in range(len(atoms)):
        x,y=points[i];lines[4+i]='%10.4f%10.4f'%(x or 0.,y or 0.)+lines[4+i][20:]
    return ''.join(lines)
def outputs():
    original=json.load(gzip.open(HERE/'before-sources.json.gz','rt'))
    code=original[DATA];mols={}
    for key in KEYS:
        m,mol=literal(code,key)
        if key in base['accepted']:
            ref=base['accepted'][key];p=ROOT/ref['path']
            assert hashlib.sha256(p.read_bytes()).hexdigest()==ref['sha256']
            candidate=p.read_text()
        else:candidate=uniform(mol)
        mols[key]=candidate
        code=code[:m.start(1)]+json.dumps(candidate)+code[m.end(1):]
    result={DATA:code}
    for p,key in base['sourceKeys'].items():result[p]=mols[key]
    return original,result
if __name__=='__main__':
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('--apply',action='store_true');opt=args.parse_args()
    original,result=outputs()
    if opt.apply:
        for p in result:assert(ROOT/p).read_bytes()==original[p].encode(),('Baseline changed',p)
        for p,content in result.items():(ROOT/p).write_text(content)
    print(json.dumps({'expanded':len(KEYS),'existingSourceMOLs':len(base['sourceKeys']),
                      'acceptedExactMOLs':len(base['accepted']),'applied':opt.apply}))
