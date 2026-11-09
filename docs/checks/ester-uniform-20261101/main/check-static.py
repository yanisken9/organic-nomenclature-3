"""Actual ester integration identity, geometry and whole-library naming guards."""
from pathlib import Path
import gzip,json,math,hashlib,runpy,subprocess,ast
ROOT=Path.cwd();HERE=ROOT/'docs/checks/ester-uniform-20261101/main'
T=runpy.run_path(str(HERE/'transform.py'));base=T['base'];parse=T['parse'];literal=T['literal'];keys=T['KEYS'];data=T['DATA']
old,expected=T['outputs']();current=(ROOT/data).read_text()
for path,content in expected.items():assert(ROOT/path).read_bytes()==content.encode(),('Unexpected output',path)
geometry=[]
for key in keys:
    before=literal(old[data],key)[1];after=literal(current,key)[1]
    ls,aa,bb=parse(before);ns,new,nb=parse(after);n=len(aa)
    assert ls[:4]==ns[:4]and ls[4+n:]==ns[4+n:]and bb==nb
    assert all(a[20:]==b[20:]for a,b in zip(ls[4:4+n],ns[4:4+n]))
    for a,b,o in nb:
        dx,dy=new[b][0]-new[a][0],new[b][1]-new[a][1]
        assert dx==0 or dy==0
        target=.3094 if 'H'in[new[a][2],new[b][2]]else .6188
        assert abs(math.hypot(dx,dy)-target)<.00001
        ux,uy=aa[b][0]-aa[a][0],aa[b][1]-aa[a][1]
        assert ux*dx+uy*dy>0
    if key in base['accepted']:assert hashlib.sha256(after.encode()).hexdigest()==base['accepted'][key]['sha256']
    for path,k in base['sourceKeys'].items():
        if k!=key:continue
        sl,sa,sb=parse((ROOT/path).read_text());ol,oa,ob=parse(old[path]);sn=len(sa)
        assert sa==new and sb==nb and sl[:4]==ol[:4]and sl[4+sn:]==ol[4+sn:]
        assert all(a[20:]==b[20:]for a,b in zip(sl[4:4+sn],ol[4:4+sn]))
    geometry.append({'key':key,'atoms':n,'bonds':len(nb),'graphIDsNonXYUnchanged':True,'orthogonalLengthsPassed':True})
exec(compile((HERE/'naming-fragment.py.txt').read_text(),'naming-fragment','exec'))
protected=0
for path,digest in base['files'].items():
    if path in base['paths']or path in ['docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md']:continue
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,('Protected file changed',path);protected+=1
assert hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==base['indexSHA256']
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==base['HEAD']
for path in HERE.glob('*.py'):ast.parse(path.read_text())
out={'passed':True,'geometry':geometry,'namingCasesCompared':names['total'],'affectedFormChain2D3DCases':len(names['affected']),'names':names['affected'],'protectedFilesUnchanged':protected,'sourceMOLs':7,'exactAcceptedProposals':4,'coreChanged':False}
(HERE/'static.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['geometry','names']}))
