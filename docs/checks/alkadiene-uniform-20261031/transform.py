"""Approved coordinate-only transformation from immutable original MOLs.

Uses the original professor propadiene/pentadiene orthogonal drawing convention;
the final .6188/.3094 units are the reviewed alkane settings. Atom order,
directions, graph, bond orders, headers and non-x/y fields stay unchanged.
This module has no import-time writes. CLI only writes with --apply.
"""
from pathlib import Path
import argparse, json, math, re

KEYS = ['propadiene', 'pentadiene_1_3', 'butadiene_1_3', 'butadiene_1_2', 'pentadiene_1_4', 'methyl_3_pentadiene_1_3', 'dimethyl_2_3_pentadiene_1_3', 'ethyl_3_dimethyl_4_5_hexadiene_1_4']
DATA = 'js/jsme-nick-nomeclature-moc2-data_52.js'
LITERAL = r'"(?:\\.|[^"\\])*"'

def literal(code, key):
    m = re.search(r'\b(?:let|const|var)\s+' + re.escape(key + '_2D_Expanded') +
                  r'\s*=\s*((?:' + LITERAL + r'\s*\+\s*)*' + LITERAL + r')\s*;', code)
    if not m: raise ValueError('Missing MOL literal: ' + key)
    return m, ''.join(json.loads(s) for s in re.findall(LITERAL, m[1]))

def parse(mol):
    lines = mol.splitlines(keepends=True)
    n, nb = int(lines[3][:3]), int(lines[3][3:6])
    atoms = [(float(s[:10]), float(s[10:20]), s[31:34].strip()) for s in lines[4:4+n]]
    bonds = [(int(s[:3])-1, int(s[3:6])-1, int(s[6:9])) for s in lines[4+n:4+n+nb]]
    return lines, atoms, bonds

def direction(a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    # The original drawings are orthogonal; tolerate only MOL rounding noise.
    length = math.hypot(dx, dy)
    if not length or min(abs(dx), abs(dy)) > .001*length:
        raise ValueError('Non-orthogonal/zero bond; no implicit layout rewrite')
    return (math.copysign(1, dx), 0) if abs(dx)>abs(dy) else (0, math.copysign(1, dy))

def transform(mol):
    lines, atoms, bonds = parse(mol)
    assert set(a[2] for a in atoms) == {'C', 'H'}
    assert sum(order == 2 for a,b,order in bonds) == 2
    assert all(order in [1,2] for a,b,order in bonds)
    carbons = [i for i,a in enumerate(atoms) if a[2] == 'C']
    neighbors = [[] for a in atoms]
    for a,b,order in bonds: neighbors[a].append(b); neighbors[b].append(a)
    cc = [math.dist(atoms[a][:2],atoms[b][:2]) for a,b,o in bonds if atoms[a][2]==atoms[b][2]=='C']
    assert len(cc) == len(carbons)-1
    scale = .6188 / sorted(cc)[len(cc)//2]
    root = carbons[0]
    xy = {root: (round(atoms[root][0]*scale,4), round(atoms[root][1]*scale,4))}
    pending = [root]
    while pending:
        a = pending.pop()
        for b in neighbors[a]:
            if atoms[b][2]!='C' or b in xy: continue
            dx,dy = direction(atoms[a],atoms[b])
            xy[b] = (round(xy[a][0]+dx*.6188,4), round(xy[a][1]+dy*.6188,4))
            pending.append(b)
    assert all(c in xy for c in carbons)
    for i,a in enumerate(atoms):
        if a[2]!='H': continue
        assert len(neighbors[i])==1 and atoms[neighbors[i][0]][2]=='C'
        c = neighbors[i][0]; dx,dy = direction(atoms[c],a)
        xy[i] = (round(xy[c][0]+dx*.3094,4), round(xy[c][1]+dy*.3094,4))
    for i in range(len(atoms)):
        x,y = xy[i]
        lines[4+i] = '%10.4f%10.4f' % (0.0 if not x else x, 0.0 if not y else y) + lines[4+i][20:]
    return ''.join(lines)

def changed_sources(original):
    data = (original/DATA).read_text()
    for key in KEYS:
        m,mol = literal(data,key)
        data = data[:m.start(1)] + json.dumps(transform(mol)) + data[m.end(1):]
    result = {DATA:data}
    for p in (original/'mols').rglob('*.mol'):
        result[str(p.relative_to(original))] = transform(p.read_text())
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original',type=Path,required=True);p.add_argument('--apply',action='store_true')
    args=p.parse_args();result=changed_sources(args.original)
    if args.apply:
        for name,content in result.items():
            if Path(name).read_bytes()!=(args.original/name).read_bytes():
                raise ValueError('Target differs from baseline: '+name)
        for name,content in result.items(): Path(name).write_text(content)
    print(json.dumps({'sources':list(result),'applied':args.apply}))
