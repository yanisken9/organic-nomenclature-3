"""52 coordinate/identity guards and full-library naming-engine differential."""
from pathlib import Path
import gzip,json,math,subprocess,hashlib,runpy
ROOT=Path.cwd();HERE=ROOT/'docs/checks/carbonyl-acid-uniform-20261101'
T=runpy.run_path(str(HERE/'transform.py'));parse=T['parse'];literal=T['literal'];keys=T['KEYS']
base=json.loads((HERE/'baseline.json').read_text());old=json.load(gzip.open(HERE/'before-sources.json.gz','rt'))
expected=T['outputs']()[1];data=T['DATA']
for p,text in expected.items():assert(ROOT/p).read_bytes()==text.encode(),('Not frozen-source output',p)
updates=runpy.run_path(str(HERE/'update-viewer.py'))['outputs']()[1]
for p,text in updates.items():assert(ROOT/p).read_bytes()==text.encode(),('Not bounded viewer/cache output',p)
SPECIAL={'ethyl_4_isopropyl_3_methyl_2_hexanal':{frozenset([2,7]):.588,frozenset([3,8]):.9,frozenset([4,11]):.588},
         'isopropyl_2_buten_2_dial':{frozenset([2,5]):.588},
         'trimethyl_3_4_4_pentanone_2':{frozenset([4,8]):.98}}
def validate(before,after,key):
    ls,atoms,edges=parse(before);ns,new,nb=parse(after);n=len(atoms)
    assert ls[:4]==ns[:4]and ls[4+n:]==ns[4+n:]and edges==nb
    assert all(x[20:]==y[20:]for x,y in zip(ls[4:4+n],ns[4:4+n]))
    assert len(set(v[:2]for v in new))==n
    near=[[]for _ in new]
    for a,b,o in nb:
        near[a].append((b,o));near[b].append((a,o))
        dx,dy=new[b][0]-new[a][0],new[b][1]-new[a][1]
        assert dx==0 or dy==0,('Diagonal',key,a+1,b+1)
        target=.3094 if 'H'in[new[a][2],new[b][2]]else SPECIAL.get(key,{}).get(frozenset([a+1,b+1]),.6188)
        assert abs(math.hypot(dx,dy)-target)<.00001,(key,a+1,b+1,target)
        if key not in base['accepted']:
            ux,uy=atoms[b][0]-atoms[a][0],atoms[b][1]-atoms[a][1]
            assert ux*dx+uy*dy>0 and abs(ux*dy-uy*dx)<.0001
        for k,p in enumerate(new):
            if k in[a,b]:continue
            t=max(0,min(1,((p[0]-new[a][0])*dx+(p[1]-new[a][1])*dy)/(dx*dx+dy*dy)))
            assert math.dist(p[:2],(new[a][0]+t*dx,new[a][1]+t*dy))>.0001,(key,'Atom on unrelated bond',k+1,a+1,b+1)
    def cross(a,b,c):return(new[b][0]-new[a][0])*(new[c][1]-new[a][1])-(new[b][1]-new[a][1])*(new[c][0]-new[a][0])
    for bi,(a,b,o)in enumerate(nb):
        for c,d,p in nb[:bi]:
            if len({a,b,c,d})<4:continue
            assert not(cross(a,b,c)*cross(a,b,d)<-1e-12 and cross(c,d,a)*cross(c,d,b)<-1e-12)
            if abs(cross(a,b,c))<1e-9 and abs(cross(a,b,d))<1e-9:
                axis=0 if new[a][0]!=new[b][0]else 1
                assert min(max(new[a][axis],new[b][axis]),max(new[c][axis],new[d][axis]))-max(min(new[a][axis],new[b][axis]),min(new[c][axis],new[d][axis]))<1e-8
    groups=0
    for c,v in enumerate(new):
        if v[2]!='C':continue
        doubles=[i for i,o in near[c]if new[i][2]=='O'and o==2]
        hydroxyls=[i for i,o in near[c]if new[i][2]=='O'and o==1 and any(new[j][2]=='H'for j,p in near[i])]
        if not(doubles and hydroxyls):continue
        groups+=1;oxygen=doubles[0];oh=hydroxyls[0];hydrogen=next(i for i,o in near[oh]if new[i][2]=='H')
        assert new[c][0]==new[oxygen][0]and new[c][1]==new[oh][1]==new[hydrogen][1]
        assert(new[oh][0]-new[c][0])*(new[hydrogen][0]-new[oh][0])>0
    return {'key':key,'atoms':n,'graphIDsNonXYUnchanged':True,'allBondsOrthogonal':True,'carboxylGroups':groups}
current=(ROOT/data).read_text();geometry=[]
for key in keys:
    before=literal(old[data],key)[1];after=literal(current,key)[1]
    geometry.append(validate(before,after,key))
    if key in base['accepted']:
        assert hashlib.sha256(after.encode()).hexdigest()==base['accepted'][key]['sha256']
    for p,k in base['sourceKeys'].items():
        if k==key:assert(ROOT/p).read_text()==after
assert sum(r['carboxylGroups']for r in geometry)==26
print('Geometry and source/embed guards passed',len(geometry),flush=True)
exec(compile((HERE/'naming-fragment.py.txt').read_text(),'naming-fragment','exec'))
protected=0
for p,digest in base['files'].items():
    if p in base['paths']or p in ['docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md']:continue
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,('Protected file changed',p)
    protected+=1
assert hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==base['indexSHA256']
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==base['HEAD']
out={'passed':True,'geometry':geometry,'namingCasesCompared':names['total'],
     'affectedFormChain2D3DCases':len(names['affected']),'names':names['affected'],
     'protectedFilesUnchanged':protected,'coreUnchanged':True,'sourceMOLs':31,
     'exactAcceptedMOLs':8,'newAtomsOrBondIDs':False}
(HERE/'static.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in ['geometry','names']}),flush=True)
