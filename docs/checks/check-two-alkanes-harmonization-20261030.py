"""Check the approved two-alkane coordinate changes against the saved baseline."""
from pathlib import Path
import argparse
import base64
import gzip
import hashlib
import itertools
import json
import math
import re
import runpy
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('--before', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
helper = runpy.run_path('docs/checks/harmonize-two-alkanes-20261030.py')
parse = helper['parse']
snapshot = json.loads(gzip.decompress(args.before.read_bytes()))
original = {path: base64.b64decode(value).decode() for path, value in snapshot['sources'].items()}
data_path = helper['DATA']
current_code = Path(data_path).read_text()
code = 'var window={};'+current_code+';print(JSON.stringify({mols:window.MOL2D,examples:nameExamples}));'
run = subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                      '-e', 'eval(JSON.parse(readline()))'], input=json.dumps(code)+'\n',
                     text=True, capture_output=True, check=True)
registry = json.loads(run.stdout)
old_run = subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                          '-e', 'eval(JSON.parse(readline()))'],
                         input=json.dumps('var window={};'+original[data_path]+';print(JSON.stringify({mols:window.MOL2D,examples:nameExamples}));')+'\n',
                         text=True,capture_output=True,check=True)
old_registry = json.loads(old_run.stdout)
assert registry['examples'] == old_registry['examples']
assert set(registry['mols']) == set(old_registry['mols'])
assert all(registry['mols'][key] == value for key, value in old_registry['mols'].items()
           if key not in helper['KEYS'])


def masked(code):
    for key in helper['KEYS']:
        for form in helper['FORMS']:
            match = helper['literal_match'](code, key+'_2D_'+form)
            assert match
            code = code[:match.start(1)] + 'MOL_COORDINATE_RECORD' + code[match.end(1):]
    return code


assert masked(current_code) == masked(original[data_path])


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def subtract(a, b):
    return (a[0]-b[0], a[1]-b[1])


def intersects(a, b, c, d):
    u, v = subtract(b,a), subtract(d,c)
    den = cross(u,v)
    if abs(den) < 1e-8:
        if abs(cross(subtract(c,a),u)) > 1e-6:
            return False
        length2 = sum(x*x for x in u)
        projection = [sum(x*y for x,y in zip(subtract(p,a),u))/length2 for p in (c,d)]
        return min(1,max(projection))-max(0,min(projection)) > 1e-5
    t = cross(subtract(c,a),v)/den
    q = cross(subtract(c,a),u)/den
    return -1e-6 <= t <= 1+1e-6 and -1e-6 <= q <= 1+1e-6


rows = []
for path, before in original.items():
    if not path.endswith('.mol'):
        continue
    after = Path(path).read_text()
    old_lines, old_atoms, old_edges = parse(before)
    lines, atoms, edges = parse(after)
    n = len(atoms)
    assert old_lines[:4] == lines[:4] and old_lines[4+n:] == lines[4+n:], path
    assert all(a[20:] == b[20:] for a,b in zip(old_lines[4:4+n], lines[4:4+n])), path
    assert edges == old_edges and len(atoms) == len(old_atoms)
    carbon_count = sum(a[2]=='C' for a in atoms)
    explicit_h = sum(a[2]=='H' for a in atoms)
    assert carbon_count in (6,10) and explicit_h in (0,2*carbon_count+2)
    degree = [sum(i in edge for edge in edges) for i in range(n)]
    assert all(degree[i] == (4 if a[2]=='C' else 1) for i,a in enumerate(atoms)) if explicit_h else all(d<=4 for d in degree)
    lengths = [math.dist(atoms[a][:2],atoms[b][:2]) for a,b in edges]
    cc = [v for v,(a,b) in zip(lengths,edges) if atoms[a][2]==atoms[b][2]=='C']
    assert all(abs(length-.825)<.0002 for length in cc), path
    if path.endswith(('_Condensed.mol','_Expanded.mol')):
        assert all(abs(atoms[a][0]-atoms[b][0])<.00001 or abs(atoms[a][1]-atoms[b][1])<.00001 for a,b in edges), path
    else:
        # A proper similarity transform preserves every local angle and the
        # orientation (cross-product sign), including branch junctions.
        for vertex in range(n):
            neighbors = [b if a==vertex else a for a,b in edges if vertex in (a,b)]
            for a,b in itertools.combinations(neighbors,2):
                def angle(points):
                    u=subtract(points[a][:2],points[vertex][:2]); v=subtract(points[b][:2],points[vertex][:2])
                    return math.degrees(math.atan2(cross(u,v),sum(x*y for x,y in zip(u,v))))
                assert abs(angle(atoms)-angle(old_atoms))<.03, (path,vertex,a,b)
    for i,(a,b) in enumerate(edges):
        for c,d in edges[:i]:
            if len({a,b,c,d})==4:
                assert not intersects(atoms[a][:2],atoms[b][:2],atoms[c][:2],atoms[d][:2]), (path,a,b,c,d)
    if 'new_molecules' in path:
        key=next(key for key in helper['KEYS'] if Path(path).name.startswith(key+'_2D_'))
        form=next(form for form in helper['FORMS'] if path.endswith('_'+form+'.mol'))
        assert registry['mols'][key][form.lower()] == after
    rows.append({'path':path,'atoms':n,'bonds':len(edges),'CC_range':[min(cc),max(cc)],
                 'indexedGraphAndNonCoordinateFieldsPreserved':True,'unrelatedBondCrossings':0})

allowed = set(original) | {'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
hashes = snapshot['fileHashes']
protected = [path for path in hashes if path not in allowed]
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==hashes[path] for path in protected)
result = {'passed':True,'sources':rows,'oldMoleculesUnchanged':len(registry['mols'])-2,
          'allNamingMetadataUnchanged':True,'otherDataCodeByteIdentical':True,
          'protectedExistingFilesUnchanged':len(protected),
          'protected3DFilesUnchanged':sum(path.endswith('.sdf') for path in protected),
          'protectedCoreSHA256':hashes['js/mulermoc-nom-core-52.js'],
          'sourceEmbeddedPairs':6}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(rows),'coordinate-only source MOLs; 6 source/embedded pairs;',len(protected),'protected files unchanged')
