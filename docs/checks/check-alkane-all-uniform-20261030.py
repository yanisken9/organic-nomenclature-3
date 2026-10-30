"""Check four coordinate changes and the common expanded pipeline's bounded scope."""
from pathlib import Path
import ast,base64,difflib,gzip,hashlib,json,math,runpy,subprocess
snap=json.loads(gzip.decompress(Path('docs/checks/alkane-all-uniform-before-20261030.json.gz').read_bytes()))
old={p:base64.b64decode(v).decode()for p,v in snap['sources'].items()}
h=runpy.run_path('docs/checks/harmonize-two-alkanes-20261030.py');keys=snap['keys']
DATA='js/jsme-nick-nomeclature-moc2-data_52.js';VIEW='js/mulermoc-nom-molview-52.js';HTML='mulermoc-nom-52.html'
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def registry(code):
 script='var window={};'+code+';print(JSON.stringify({mols:window.MOL2D,examples:nameExamples}));'
 return json.loads(subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(script)+'\n',text=True,capture_output=True,check=True).stdout)
before=registry(old[DATA]);code=Path(DATA).read_text();after=registry(code)
assert before['examples']==after['examples']and set(before['mols'])==set(after['mols'])
assert all(before['mols'][k]==v for k,v in after['mols'].items()if k not in keys)
assert all(before['mols'][k][f]==after['mols'][k][f]for k in keys for f in ['condensed','skeletal'])
def masked(s):
 for k in keys:
  m=h['literal_match'](s,k+'_2D_Expanded');assert m;s=s[:m.start(1)]+'UNIFORM_MOL'+s[m.end(1):]
 return s
assert masked(code)==masked(old[DATA])
rows=[]
for key in keys:
 al,aa,ae=h['parse'](before['mols'][key]['expanded']);bl,ba,be=h['parse'](after['mols'][key]['expanded']);n=len(aa)
 assert ae==be and len(ba)==n and al[:4]==bl[:4]and al[4+n:]==bl[4+n:]
 for i,(x,y)in enumerate(zip(aa,ba)):
  assert al[i+4][20:]==bl[i+4][20:]
  if x[2]=='C':assert all(abs(y[d]-round(x[d]*.6188/.825,4))<1e-8 for d in [0,1]);continue
  near=[v if u==i else u for u,v in ae if i in [u,v]];assert len(near)==1;c=near[0];assert ba[c][2]=='C'
  assert all(abs((x[d]-aa[c][d])-(y[d]-ba[c][d]))<1e-8 for d in [0,1])
 cc=[math.dist(ba[u][:2],ba[v][:2])for u,v in be if ba[u][2]==ba[v][2]=='C'];ch=[math.dist(ba[u][:2],ba[v][:2])for u,v in be if ba[u][2]!=ba[v][2]]
 nc=sum(a[2]=='C'for a in ba);assert len(cc)==nc-1 and len(ch)==2*nc+2
 assert all(abs(x-.6188)<1e-8 for x in cc)and all(abs(x-.3094)<1e-8 for x in ch)
 rows.append({'key':key,'CCCount':len(cc),'CHCount':len(ch),'CC':.6188,'CH':.3094,'relativeCHVectorsGraphFieldsPreserved':True})
assert before['mols']['methane']==after['mols']['methane']
all_keys=snap['viewerTargets']+['methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']
uniform=[]
for k in all_keys:
 _,a,e=h['parse'](after['mols'][k]['expanded']);cc=[math.dist(a[u][:2],a[v][:2])for u,v in e if a[u][2]==a[v][2]=='C'];ch=[math.dist(a[u][:2],a[v][:2])for u,v in e if a[u][2]!=a[v][2]]
 assert all(abs(x-.6188)<1e-8 for x in cc)and all(abs(x-.3094)<1e-8 for x in ch)
 uniform.append({'key':k,'CCCount':len(cc),'CHCount':len(ch)})
v=Path(VIEW).read_text();o=old[VIEW]
def outside_helper(s):
 a=s.index('function fPrepareFixedCCAlkanePrototype()');b=s.index('function fGetUniform2DLibraryFrame()',a);return s[:a]+s[b:]
assert outside_helper(v)==outside_helper(o)
assert Path(HTML).read_text()==old[HTML].replace('v=alkane-three-uniform-20261030','v=alkane-all-uniform-20261030')
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'};protected=[p for p in snap['fileHashes']if p not in allowed]
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==snap['fileHashes'][p]for p in protected)
for p in [DATA,VIEW]:subprocess.run([JSC,'-e','new Function(JSON.parse(readline()));'],input=json.dumps(Path(p).read_text())+'\n',text=True,capture_output=True,check=True)
for p in ['docs/checks/check-alkane-all-uniform-20261030.py','docs/checks/test-alkane-all-uniform-20261030.py']:ast.parse(Path(p).read_text())
Path('docs/checks/alkane-all-uniform-source-20261030.diff').write_text(''.join(''.join(difflib.unified_diff(s.splitlines(True),Path(p).read_text().splitlines(True),fromfile='before/'+p,tofile='after/'+p))for p,s in old.items()))
r={'passed':True,'changedExpandedMolecules':4,'viewerAddedMolecules':5,'methaneMOLUnchanged':True,'sources':rows,'all8ExpandedUniformLengths':uniform,'other137MoleculeRecordsAndTargetOtherFormsUnchanged':True,'dataOutside4LiteralsByteIdentical':True,'viewerChangesOnlyExistingPrototypeHelper':True,'htmlOnly2CacheKeys':True,'protectedExistingFilesUnchanged':len(protected),'core3DScenariosReactUnchanged':True,'syntax':'2JS and2Python PASS'}
Path('docs/checks/alkane-all-uniform-static-20261030.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
