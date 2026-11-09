"""Coordinate/graph guards and actual naming-engine before/after comparison."""
from pathlib import Path
import gzip,json,math,subprocess,hashlib,runpy
ROOT=Path.cwd();HERE=ROOT/'docs/checks/ether-uniform-20261031'
T=runpy.run_path(str(HERE/'transform.py'));parse=T['parse'];literal=T['literal'];keys=T['KEYS']
base=json.loads((HERE/'baseline.json').read_text());old=json.load(gzip.open(HERE/'before-sources.json.gz','rt'))
expected=T['outputs']()[1];data='js/jsme-nick-nomeclature-moc2-data_52.js'
for p,text in expected.items():assert(ROOT/p).read_bytes()==text.encode(),('Not frozen-source output',p)
def validate(a,b):
    ls,atoms,edges=parse(a);ns,new,nb=parse(b);n=len(atoms)
    assert ls[:4]==ns[:4]and ls[4+n:]==ns[4+n:]
    assert all(x[20:]==y[20:]for x,y in zip(ls[4:4+n],ns[4:4+n]))
    assert atoms!=new and edges==nb and len(set((v[0],v[1])for v in new))==n
    length=[];directions=[]
    for i,j,o in edges:
        dx,dy=atoms[j][0]-atoms[i][0],atoms[j][1]-atoms[i][1]
        ex,ey=new[j][0]-new[i][0],new[j][1]-new[i][1]
        before=math.hypot(dx,dy);after=math.hypot(ex,ey);target=.3094 if 'H'in[new[i][2],new[j][2]]else .6188
        assert abs(after-target)<.00015,(i,j,after,target)
        assert dx*ex+dy*ey>0
        difference=abs(dx*ey-dy*ex)/(before*after);assert difference<.0005,(i,j,'direction changed')
        length.append(after);directions.append(difference)
        for k,p in enumerate(new):
            if k in [i,j]:continue
            t=max(0,min(1,((p[0]-new[i][0])*ex+(p[1]-new[i][1])*ey)/(after*after)))
            assert math.dist(p[:2],(new[i][0]+t*ex,new[i][1]+t*ey))>.0001,('Atom on unrelated bond',k,i,j)
    def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    for i,j,o in edges:
        for k,l,_ in edges:
            if {i,j}&{k,l}:continue
            assert not(cross(new[i],new[j],new[k])*cross(new[i],new[j],new[l]) < -1e-10 and cross(new[k],new[l],new[i])*cross(new[k],new[l],new[j]) < -1e-10)
    near=[[]for _ in new]
    for i,j,_ in edges:near[i].append(j);near[j].append(i)
    assert all(len(near[i])=={'C':4,'H':1,'O':2}[v[2]]for i,v in enumerate(new))
    counts={s:sum(a[2]==s for a in new)for s in ['C','H','O']};assert counts['O']==1 and counts['H']==2*counts['C']+2
    return {'atoms':n,'formula':counts,'maxDirectionSineChange':max(directions),'minBond':min(length),'maxBond':max(length)}
geometry=[];current=(ROOT/data).read_text()
for k in keys:
    before=literal(old[data],k)[1];after=literal(current,k)[1];row=validate(before,after);row['key']=k
    for p in base['paths']:
        if p.endswith('/'+k+'_2D_Expanded.mol'):
            source=(ROOT/p).read_text();validate(old[p],source)
            assert after==source if before==old[p]else after==source+'\n'
    geometry.append(row)
print('Geometry and source/embed guards passed',len(geometry),flush=True)
prefix='var window={addEventListener(){}},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
core=(ROOT/'js/mulermoc-nom-core-52.js').read_text();viewer=(ROOT/'js/mulermoc-nom-molview-52.js').read_text()
tail=r'''
var MOL2D=window.MOL2D;selectedMol=key;mode2D=mode;mainChainMode=chainMode;
var text=MOL2D[key][mode],ls=text.split('\n'),na=Number(ls[3].slice(0,3)),nb=Number(ls[3].slice(3,6));
var aa=ls.slice(4,4+na).map(l=>({label:l.slice(31,34).trim()})),bb=ls.slice(4+na,4+na+nb).map(l=>({atoms:[Number(l.slice(0,3)),Number(l.slice(3,6))],order:Number(l.slice(6,9))}));
jsmeNomeclatureApplet={totalNumberOfAtoms:()=>na,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1],molFile:()=>text};
fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
nameExamples[key].classification=fGetMoleculeClassification();
var out={name:currentMolName,common:currentMolCommonName,parts:nameComponentsList,chain:mainChainAtomsList,classification:nameExamples[key].classification};
if(sdf){fParseSDF3D(sdf);fDetectMolType3D();fCalcMainChain3D();out.chain3D=mainChainAtoms3D;out.commonParts=fGetEtherCommonParts();out.prefixes=fEtherPrefixGroups();out.signature=fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList);out.signature3D=fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D);}
return out;
'''
js='var before=new Function("key","mode","chainMode","sdf",'+json.dumps(prefix+old[data]+core+old['js/mulermoc-nom-molview-52.js']+tail)+'),after=new Function("key","mode","chainMode","sdf",'+json.dumps(prefix+current+core+viewer+tail)+');'
js+='var registry=(new Function("var window={};"+'+json.dumps(current)+'+";return {metadata:nameExamples,mols:window.MOL2D};"))();var total=0,ether=[];'
sdfs={k:(ROOT/'mols/nomeclature-moc2'/(k+'_3D.sdf')).read_text()for k in keys}
js+='var sdfs='+json.dumps(sdfs)+';'
js+='''for(var[k,forms]of Object.entries(registry.mols))for(var[mode,text]of Object.entries(forms))if(text)for(var chain of ['algorithmic','data']){
var args=[k,mode,chain,sdfs[k]||''],a=before(...args),b=after(...args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify([k,mode,chain,a,b]));total++;
if(sdfs[k]){if(b.signature!==b.signature3D)throw Error('2D3D parent '+k);ether.push({key:k,mode,chain,result:b});}}
print(JSON.stringify({total,ether}));'''
jsc='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
r=subprocess.run([jsc,'-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout[:2500],r.stderr)
names=json.loads(r.stdout);assert len(names['ether'])==66
protected=0
for p,h in base['files'].items():
    if p in base['paths']or p in ['docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md']:continue
    assert(ROOT/p).is_file()and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,('Protected file changed',p)
    protected+=1
assert hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==base['indexSHA256']
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==base['HEAD']
out={'passed':True,'geometry':geometry,'namingCasesCompared':names['total'],'etherFormChain2D3DCases':66,'names':names['ether'],'protectedFilesUnchanged':protected,'coreUnchanged':True,'newAtomOrBondIDs':False}
(HERE/'static.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['geometry','names']}),flush=True)
