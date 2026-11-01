"""Coordinate/identity/protected-file checks for the isolated acid preview."""
from pathlib import Path
import json,math,gzip,hashlib,runpy,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
h=runpy.run_path(str(HERE/'prepare.py'));parse=h['parse']
source=json.load(gzip.open(HERE/'originals.json.gz','rt'));rows=[]
for key in h['CAPTURE_KEYS']:
    before=(HERE/(key+'-before.mol')).read_text()
    after=(HERE/(key+'-proposed.mol')).read_text()
    assert before==source[key]
    assert after==h['proposal'](before,key)[0],'Non-reproducible generator'
    ol,oa,ob=parse(before);nl,na,nb=parse(after);n=len(oa)
    assert ob==nb and ol[:4]==nl[:4] and ol[4+n:]==nl[4+n:]
    assert all(x[20:]==y[20:]for x,y in zip(ol[4:4+n],nl[4:4+n]))
    assert len(set(v[:2]for v in na))==n
    near=[[]for _ in na]
    for a,b,o in nb:
        near[a].append((b,o));near[b].append((a,o))
        expected=.3094 if 'H'in[na[a][2],na[b][2]]else .6188
        assert abs(math.dist(na[a][:2],na[b][:2])-expected)<.00001
        assert na[a][0]==na[b][0]or na[a][1]==na[b][1]
        for k,p in enumerate(na):
            if k in[a,b]:continue
            x,y=na[a][:2];dx,dy=na[b][0]-x,na[b][1]-y
            t=max(0,min(1,((p[0]-x)*dx+(p[1]-y)*dy)/(dx*dx+dy*dy)))
            assert math.dist(p[:2],(x+t*dx,y+t*dy))>.1547,('Atom too close to unrelated bond',key,k+1,a+1,b+1)
    def cross(a,b,c):return(na[b][0]-na[a][0])*(na[c][1]-na[a][1])-(na[b][1]-na[a][1])*(na[c][0]-na[a][0])
    for bi,(a,b,o)in enumerate(nb):
        for c,d,p in nb[:bi]:
            if len({a,b,c,d})<4:continue
            assert not(cross(a,b,c)*cross(a,b,d)<-1e-12 and cross(c,d,a)*cross(c,d,b)<-1e-12)
            if abs(cross(a,b,c))<1e-9 and abs(cross(a,b,d))<1e-9:
                axis=0 if na[a][0]!=na[b][0]else 1
                assert min(max(na[a][axis],na[b][axis]),max(na[c][axis],na[d][axis]))-max(min(na[a][axis],na[b][axis]),min(na[c][axis],na[d][axis]))<1e-8
    groups=0
    for c,v in enumerate(na):
        if v[2]!='C':continue
        doubles=[i for i,o in near[c]if na[i][2]=='O'and o==2]
        hydroxyls=[i for i,o in near[c]if na[i][2]=='O'and o==1 and any(na[j][2]=='H'for j,p in near[i])]
        if not(doubles and hydroxyls):continue
        groups+=1;oxygen=doubles[0];oh=hydroxyls[0]
        hydrogen=next(i for i,o in near[oh]if na[i][2]=='H')
        assert na[c][0]==na[oxygen][0]
        assert na[c][1]==na[oh][1]==na[hydrogen][1]
        assert(na[oh][0]-na[c][0])*(na[hydrogen][0]-na[oh][0])>0
    if key in h['KEYS']:
        assert na[8][0]==na[6][0] and na[8][1]<na[6][1]
        assert na[7][1]==na[6][1] and na[7][0]>na[6][0]
        assert na[10][0]==na[9][0] and na[10][1]>na[9][1]
    rows.append({'key':key,'atoms':n,'carboxylGroups':groups,'allBondsOrthogonal':True,
                 'graphIDsNonXYUnchanged':True,'coordinateClearancePassed':True})
base=json.loads((HERE/'application-baseline.json').read_text());protected=0
for name,digest in base['files'].items():
    if name in ['docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md']:continue
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('Protected file changed',name)
    protected+=1
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==base['HEAD']
assert hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==base['indexSHA256']
out={'passed':True,'previewOnly':True,'molecules':rows,'protectedFilesUnchanged':protected,
     'MainChanged':False,'coreChanged':False,'limitations':'Coordinate checks do not establish rendered-label readability.'}
(HERE/'geometry-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':True,'molecules':len(rows),'protectedFilesUnchanged':protected}))
