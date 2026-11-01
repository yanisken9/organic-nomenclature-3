"""Check the approved spacing revision against the saved vertical preview."""
from pathlib import Path
import runpy,tarfile,math,json,hashlib
HERE=Path(__file__).resolve().parent
h=runpy.run_path(str(HERE/'prepare.py'));parse=h['parse']
baseline=json.loads((HERE/'spacing-baseline.json').read_text())
archive=HERE.parents[3]/baseline['snapshot']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==baseline['snapshotSHA256']
geometry=json.loads((HERE/'geometry.json').read_text());rows=[]
with tarfile.open(archive,'r:gz')as saved:
    for index,item in enumerate(geometry['molecules']):
        key=item['key'];old=saved.extractfile('comparison/'+key+'-proposed.mol').read().decode()
        new=(HERE/(key+'-proposed.mol')).read_text()
        ol,oa,ob=parse(old);nl,na,nb=parse(new)
        assert len(oa)==len(na)and ob==nb
        assert ol[:4]==nl[:4]and ol[4+len(oa):]==nl[4+len(na):]
        assert all(x[20:]==y[20:]for x,y in zip(ol[4:4+len(oa)],nl[4:4+len(na)]))
        near=[[]for _ in oa]
        for a,b,o in ob:near[a].append(b);near[b].append(a)
        allowed=set();stems={frozenset(i-1 for i in edge['atoms']):edge['proposed']for edge in item['stems']}
        if index==4:assert new==old
        else:
            target=.6188 if index in [0,2,5]else .588
            if index==1:
                assert stems=={frozenset((1,6)):.588,frozenset((2,7)):.9,frozenset((3,10)):.588}
            else:assert set(stems.values())=={target}
            for edge in item['stems']:
                parent,child=[i-1 for i in edge['atoms']];seen={parent};pending=[child]
                while pending:
                    i=pending.pop()
                    if i in seen:continue
                    seen.add(i);allowed.add(i);pending.extend(near[i])
        if index==3:
            allowed.update([10,11])
            assert na[11][:2]==(round(na[3][0]-.3094,4),na[3][1])
            assert na[10][:2]==(na[2][0],round(na[2][1]+.3094,4))
            assert na[6][0]==na[4][0]and na[6][1]<na[4][1]
            assert na[5][:2]==(round(na[4][0]+.6188,4),na[4][1])
            assert na[12][:2]==(round(na[4][0]-.3094,4),na[4][1])
        if index==1:
            assert na[25][:2]==(round(na[7][0]+.3094,4),na[7][1])
            assert na[8][:2]==(na[7][0],round(na[7][1]+.6188,4))
            assert na[9][:2]==(round(na[7][0]-.6188,4),na[7][1])
        changed={i for i in range(len(oa))if oa[i][:2]!=na[i][:2]};assert changed<=allowed
        for a,b,o in ob:
            expected=stems.get(frozenset((a,b)),math.dist(oa[a][:2],oa[b][:2]))
            assert abs(math.dist(na[a][:2],na[b][:2])-expected)<.00006,(key,a+1,b+1)
            if index in [0,2,5]and na[a][2]!='H'and na[b][2]!='H':
                assert abs(math.dist(na[a][:2],na[b][:2])-.6188)<1e-7
            assert na[a][0]==na[b][0]or na[a][1]==na[b][1],(key,a+1,b+1,'diagonal bond')
        bonded={frozenset((a,b))for a,b,o in ob}
        minimum=min(math.dist(na[a][:2],na[b][:2])for a in range(len(na))for b in range(a)if frozenset((a,b))not in bonded)
        assert minimum>.1547
        for c,atom in enumerate(na):
            for a,b,o in ob:
                if c in [a,b]:continue
                ax,ay=na[a][:2];bx,by=na[b][:2];cx,cy=atom[:2]
                dx,dy=bx-ax,by-ay;t=((cx-ax)*dx+(cy-ay)*dy)/(dx*dx+dy*dy)
                assert not(0<t<1 and math.hypot(cx-ax-t*dx,cy-ay-t*dy)<1e-7),(key,c+1,a+1,b+1)
        def cross(i,j,k):
            x,y=na[i][:2];u,v=na[j][:2];q,r=na[k][:2]
            return(u-x)*(r-y)-(v-y)*(q-x)
        for bi,(a,b,o)in enumerate(ob):
            for c,d,p in ob[:bi]:
                if len({a,b,c,d})<4:continue
                assert not(cross(a,b,c)*cross(a,b,d)<-1e-12 and cross(c,d,a)*cross(c,d,b)<-1e-12)
                if abs(cross(a,b,c))<1e-9 and abs(cross(a,b,d))<1e-9:
                    axis=0 if abs(na[a][0]-na[b][0])>abs(na[a][1]-na[b][1])else 1
                    lo=max(min(na[a][axis],na[b][axis]),min(na[c][axis],na[d][axis]))
                    hi=min(max(na[a][axis],na[b][axis]),max(na[c][axis],na[d][axis]))
                    assert hi-lo<1e-7
        assert (HERE/(key+'-before.mol')).read_bytes()==saved.extractfile('comparison/'+key+'-before.mol').read()
        rows.append({'key':key,'orangeLengths':list(stems.values()),'changedAtomIDs':sorted(i+1 for i in changed),
                     'minimumNonbondedDistance':minimum,'unchangedGraphIDsNonXY':True,
                     'unaffectedCoordinatesPreserved':True,'clearGeometry':True,'allBondsOrthogonal':True})
equal_baseline=json.loads((HERE/'fourth-right-baseline.json').read_text())
equal_archive=HERE.parents[3]/equal_baseline['snapshot']
assert hashlib.sha256(equal_archive.read_bytes()).hexdigest()==equal_baseline['snapshotSHA256']
with tarfile.open(equal_archive,'r:gz')as previous:
    for index in [0,1,2,4,5]:
        name=h['KEYS'][index]+'-proposed.mol'
        assert (HERE/name).read_bytes()==previous.extractfile('comparison/'+name).read()
out={'passed':True,'date':'2026-11-01','previewOnly':True,'molecules':rows,
     'equalCCMolecules':[1,3,6],'unchangedMolecules':[1,2,3,5,6],
     'fifthUnchanged':True,'MOLRoundingLengthTolerance':.00006}
(HERE/'spacing-geometry-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':True,'molecules':len(rows),'fifthUnchanged':True}))
