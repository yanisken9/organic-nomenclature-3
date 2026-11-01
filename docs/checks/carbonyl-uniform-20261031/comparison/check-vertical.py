"""Bounded regression checks against the retained pre-vertical preview."""
from pathlib import Path
import runpy,tarfile,math,json,hashlib
HERE=Path(__file__).resolve().parent
h=runpy.run_path(str(HERE/'prepare.py'));parse=h['parse'];rows=[]
baseline=json.loads((HERE/'vertical-baseline.json').read_text())
archive=HERE.parents[3]/baseline['snapshot']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==baseline['snapshotSHA256']
with tarfile.open(archive,'r:gz')as saved:
    for key in h['KEYS']:
        old=saved.extractfile('comparison/'+key+'-proposed.mol').read().decode()
        new=(HERE/(key+'-proposed.mol')).read_text()
        ol,oa,ob=parse(old);nl,na,nb=parse(new)
        assert len(oa)==len(na)and ob==nb
        assert ol[:4]==nl[:4]and ol[4+len(oa):]==nl[4+len(na):]
        assert all(x[20:]==y[20:]for x,y in zip(ol[4:4+len(oa)],nl[4:4+len(na)]))
        near=[[]for _ in oa]
        for a,b,o in ob:near[a].append(b);near[b].append(a)
        allowed=set()
        for parent,first,last in h['VERTICAL_ETHYLS'].get(key,[]):
            parent,first,last=parent-1,first-1,last-1
            allowed.add(last)
            allowed.update(i for i in near[last]+near[first]if oa[i][2]=='H')
            assert na[parent][0]==na[first][0]==na[last][0]
            assert (na[first][1]-na[parent][1])*(na[last][1]-na[first][1])>0
            assert abs(math.dist(na[first][:2],na[last][:2])-.6188)<1e-7
        changed={i for i in range(len(oa))if oa[i][:2]!=na[i][:2]}
        assert changed<=allowed,(key,changed-allowed)
        for a,b,o in ob:
            assert abs(math.dist(oa[a][:2],oa[b][:2])-math.dist(na[a][:2],na[b][:2]))<1e-7
        bonded={frozenset((a,b))for a,b,o in ob}
        minimum=min(math.dist(na[a][:2],na[b][:2])for a in range(len(na))for b in range(a)if frozenset((a,b))not in bonded)
        assert minimum>.1547
        for c,atom in enumerate(na):
            for a,b,o in ob:
                if c in [a,b]:continue
                ax,ay=na[a][:2];bx,by=na[b][:2];cx,cy=atom[:2]
                dx,dy=bx-ax,by-ay;t=((cx-ax)*dx+(cy-ay)*dy)/(dx*dx+dy*dy)
                assert not(0<t<1 and math.hypot(cx-ax-t*dx,cy-ay-t*dy)<1e-7),(key,c+1,a+1,b+1)
        for index,(a,b,o)in enumerate(ob):
            for c,d,p in ob[:index]:
                if len({a,b,c,d})<4:continue
                def cross(i,j,k):
                    x,y=na[i][:2];u,v=na[j][:2];q,r=na[k][:2]
                    return(u-x)*(r-y)-(v-y)*(q-x)
                assert not(cross(a,b,c)*cross(a,b,d)<-1e-12 and cross(c,d,a)*cross(c,d,b)<-1e-12)
        assert (HERE/(key+'-before.mol')).read_bytes()==saved.extractfile('comparison/'+key+'-before.mol').read()
        rows.append({'key':key,'verticalEthylCount':len(h['VERTICAL_ETHYLS'].get(key,[])),
                     'changedAtomIDs':sorted(i+1 for i in changed),'minimumNonbondedDistance':minimum,
                     'graphFieldsLengthsUnchanged':True,'noCrossingsOrAtomsOnUnrelatedBonds':True})
out={'passed':True,'previewOnly':True,'molecules':rows,'verticalEthylCount':sum(r['verticalEthylCount']for r in rows)}
(HERE/'vertical-geometry-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':True,'molecules':len(rows),'verticalEthylCount':out['verticalEthylCount']}))
