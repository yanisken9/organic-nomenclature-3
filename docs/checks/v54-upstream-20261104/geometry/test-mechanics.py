"""Independent numerical checks on serialized before/after output geometry."""
from pathlib import Path
import json,math,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
checks=[]
def check(ok,label,detail=None):
    checks.append({'ok':bool(ok),'label':label,'detail':detail})
    assert ok,(label,detail)
before=json.loads((HERE/'normalized-baseline-results.json').read_text());after=json.loads((HERE/'geometry-results.json').read_text())
old={(r['key'],r['mode']):r for r in before['rows']}
counts={'forms':0,'bondLengths':0,'unchangedAngles':0,'repairedPivots':0,'spTriple':0,'spDoubleDouble':0,'properOrientation':0,'contactPairs':0,'atomBondPairs':0,'bondCrossingPairs':0}
def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def point_line(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];ll=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/ll))if ll else 0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def cross(p,a,b,c):return (p[b][0]-p[a][0])*(p[c][1]-p[a][1])-(p[b][1]-p[a][1])*(p[c][0]-p[a][0])
def crossing(p,a,b,c,d):return cross(p,a,b,c)*cross(p,a,b,d)<-1e-8 and cross(p,c,d,a)*cross(p,c,d,b)<-1e-8
for row in after['rows']:
    if not row['generated']:continue
    key=(row['key'],row['mode']);base=old[key];counts['forms']+=1
    fixed={a['atom']for a in base['after']if a['error']>0.02}
    counts['repairedPivots']+=len(fixed)
    aa={(a['atom'],tuple(a['neighbors'])):a for a in base['localAngles']}
    for angle in row['localAngles']:
        if angle['atom']in fixed:continue
        prior=aa[(angle['atom'],tuple(angle['neighbors']))]
        assert abs(prior['angle']-angle['angle'])<0.02,(key,'other angle changed',prior,angle)
        counts['unchangedAngles']+=1
        if abs(prior['cross'])>0.001:
            assert prior['cross']*angle['cross']>0,(key,'local reflection',prior,angle)
            counts['properOrientation']+=1
    for a in row['after']:
        if 3 in a['orders']:counts['spTriple']+=1
        if a['orders']==[2,2]:counts['spDoubleDouble']+=1
    p=row['points'];q=base['points'];edges=[(a-1,b-1)for a,b in row['edges']];linked={tuple(sorted(e))for e in edges}
    for a,b in edges:
        assert abs(distance(p[a],p[b])-distance(q[a],q[b]))<0.00015,(key,'rotation changed generated bond length',a,b)
        counts['bondLengths']+=1
    for a in range(len(p)):
        for b in range(a):
            if (b,a)in linked:continue
            now=distance(p[a],p[b]);prior=distance(q[a],q[b]);counts['contactPairs']+=1
            assert not(now<1.17*0.45-0.0002 and now<prior-0.0002),(key,'new/worse nonbond contact',a,b,prior,now)
    for e,(a,b)in enumerate(edges):
        for i in range(len(p)):
            if i in (a,b):continue
            now=point_line(p[i],p[a],p[b]);prior=point_line(q[i],q[a],q[b]);counts['atomBondPairs']+=1
            assert not(now<1.17*0.12-0.0002 and now<prior-0.0002),(key,'new/worse atom-bond contact',i,a,b,prior,now)
        for c,d in edges[:e]:
            if len({a,b,c,d})!=4:continue
            counts['bondCrossingPairs']+=1
            assert not crossing(p,a,b,c,d)or crossing(q,a,b,c,d),(key,'new bond crossing',a,b,c,d)
check(counts['forms']==421,'All421 generated forms preserve mechanical invariants',counts)
protected=json.loads((HERE/'before.json').read_text())['protected']
changed=[p for p,h in protected.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
check(not changed,'Old52/data54 and all recorded MOL/SDF files unchanged',{'paths':len(protected),'changed':changed})
# Only this function changed relative to this subtask baseline; root numeric
# changes are already in before-core54.js and have not been reverted.
base=(HERE/'before-core54.js').read_text();current=(ROOT/'js/mulermoc-nom-core-54.js').read_text()
def outside(s):
    a=s.index('function fZigzagMol(');z=s.index('\n// ── fGuessName',a);return s[:a],s[z:]
root_numeric_change='sortedFunPositions.sort((a, b) => a - b)'
normalized=current.replace(root_numeric_change,'sortedFunPositions.sort()')
check(current.count(root_numeric_change)==3 and outside(base)==outside(normalized),'Outside owned fZigzagMol only root three authorized numeric sorts changed')
js=current+r'''
function mol(types,edges){return fWriteMolV2000([],types.map((el,i)=>({el,x:i,y:0})),edges)}
var probes=[
 ['ring',mol(['C','C','C'],[[1,2,1],[2,3,1],[3,1,1]]),[1,2,3]],
 ['disconnected',mol(['C','C','C'],[[1,2,1]]),[1,2]],
 ['duplicate parent',mol(['C','C'],[[1,2,1]]),[1,1]],
 ['nonbonded parent',mol(['C','C','C'],[[1,2,1],[2,3,1]]),[1,3]],
 ['invalid carbon valence',mol(['C','C','C'],[[1,2,3],[2,3,2]]),[1,2,3]]
];
return probes.map(([label,text,chain])=>({label,rejected:fZigzagMol(text,chain)===null}));
'''
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
p=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps('print(JSON.stringify((new Function('+json.dumps(js)+'))()));')+'\n',text=True,capture_output=True)
assert p.returncode==0,p.stdout+p.stderr
for r in json.loads(p.stdout):check(r['rejected'],'Unsafe/invalid fixture rejected: '+r['label'])
(HERE/'mechanics-results.json').write_text(json.dumps({'checks':checks,'counts':counts},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'counts':counts}))
