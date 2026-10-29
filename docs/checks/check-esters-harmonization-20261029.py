"""Verify coordinate-only ester harmonization against its exact approved baseline."""
from pathlib import Path
import argparse, hashlib, json, math, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--before', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
specs = json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())
datafile = Path('js/jsme-nick-nomeclature-moc2-data_52.js')
code = 'var window={};'+datafile.read_text()+';print(JSON.stringify(window.MOL2D));'
raw = subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                      '-e', 'eval(JSON.parse(readline()))'], input=json.dumps(code)+'\n',
                     capture_output=True, text=True, check=True)
embedded = json.loads(raw.stdout)
old = json.loads((args.before.parent/'embedded-before.json').read_text())
new_keys = {s['key'] for s in specs}
assert set(embedded) == set(old)
assert all(embedded[k] == old[k] for k in old if k not in new_keys)

def cross(u,v): return u[0]*v[1]-u[1]*v[0]
def delta(a,b): return (a[0]-b[0],a[1]-b[1])
def intersect(a,b,c,d):
    u,v = delta(b,a),delta(d,c)
    den = cross(u,v)
    if abs(den) < 1e-8:
        if abs(cross(delta(c,a),u)) > 1e-6: return False
        ll = sum(t*t for t in u)
        ts = [sum(x*y for x,y in zip(delta(p,a),u))/ll for p in [c,d]]
        return min(1,max(ts))-max(0,min(ts)) > 1e-5
    t = cross(delta(c,a),v)/den
    q = cross(delta(c,a),u)/den
    return -1e-6 <= t <= 1+1e-6 and -1e-6 <= q <= 1+1e-6

rows=[]
for spec in specs:
    for form in ['Condensed','Expanded','Skeletal']:
        path=Path('mols/new_molecules')/(spec['key']+'_2D_'+form+'.mol')
        before=(args.before/path).read_text().splitlines()
        after=path.read_text().splitlines()
        n=int(after[3][:3]); nb=int(after[3][3:6])
        assert before[:4] == after[:4]
        assert before[4+n:] == after[4+n:]
        assert all(a[20:] == b[20:] for a,b in zip(before[4:4+n],after[4:4+n]))
        assert embedded[spec['key']][form.lower()] == path.read_text()
        xy=[(float(l[:10]),float(l[10:20])) for l in after[4:4+n]]
        edges=[(int(l[:3])-1,int(l[3:6])-1) for l in after[4+n:4+n+nb]]
        for i,(a,b) in enumerate(edges):
            for c,d in edges[:i]:
                if len({a,b,c,d}) < 4: continue
                assert not intersect(xy[a],xy[b],xy[c],xy[d]), (path,'crossing',a,b,c,d)
        acid=range(spec['acidCarbons']); alcohol=range(spec['acidCarbons'],spec['carbons'])
        assert sum(xy[i][0] for i in acid)/len(acid) < sum(xy[i][0] for i in alcohol)/len(alcohol)
        lengths=[math.dist(xy[a],xy[b]) for a,b in edges]
        if form == 'Skeletal': assert max(abs(v-.825) for v in lengths) < .0002
        rows.append({'key':spec['key'],'form':form,'atoms':n,'bonds':nb,
                     'lengthRange':[min(lengths),max(lengths)],'indexedAtomsAndBondsUnchanged':True,
                     'unrelatedBondIntersections':0,'embeddedMatchesSource':True})
unchanged=[]
for path,digest in json.loads((args.before.parent/'before-hashes.json').read_text()).items():
    if path.endswith(('.sdf','.provenance.json')) or path in ['js/mulermoc-nom-core-52.js','js/mulermoc-nom-molview-52.js']:
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest,path
        unchanged.append(path)
result={'passed':True,'forms':rows,'oldEmbeddedMoleculesUnchanged':len(old)-5,
        'byteIdentical3DProvenanceAndCoreViewer':unchanged}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS coordinate-only indexed graph preservation / 15 source-embedded pairs / 136 old records / 3D, core and viewer unchanged')
