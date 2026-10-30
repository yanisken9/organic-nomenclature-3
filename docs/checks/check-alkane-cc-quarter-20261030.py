"""Check the approved25% C-C reduction against its immediate immutable baseline."""
from pathlib import Path
import ast,base64,difflib,gzip,hashlib,json,math,re,runpy,subprocess

BASE=Path('docs/checks/alkane-cc-quarter-before-20261030.json.gz')
snap=json.loads(gzip.decompress(BASE.read_bytes()))
old={p:base64.b64decode(v).decode()for p,v in snap['sources'].items()}
helper=runpy.run_path('docs/checks/harmonize-two-alkanes-20261030.py')
key=snap['key'];data_path='js/jsme-nick-nomeclature-moc2-data_52.js'
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def registry(code):
 script='var window={};'+code+';print(JSON.stringify({mols:window.MOL2D,examples:nameExamples}));'
 return json.loads(subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(script)+'\n',text=True,capture_output=True,check=True).stdout)
before=registry(old[data_path]);code=Path(data_path).read_text();after=registry(code)
assert before['examples']==after['examples']
assert set(before['mols'])==set(after['mols'])
assert all(before['mols'][k]==v for k,v in after['mols'].items()if k!=key)
assert all(before['mols'][key][f]==after['mols'][key][f]for f in ['condensed','skeletal'])
def masked(s):
 m=helper['literal_match'](s,key+'_2D_Expanded');assert m
 return s[:m.start(1)]+'PROTOTYPE_MOL'+s[m.end(1):]
assert masked(code)==masked(old[data_path])
def verify(a,b,label):
 al,aa,ae=helper['parse'](a);bl,ba,be=helper['parse'](b);n=len(aa)
 assert ae==be and len(ba)==n
 assert al[:4]==bl[:4]and al[4+n:]==bl[4+n:]
 lengths=[];cc=[]
 for i,(x,y)in enumerate(zip(aa,ba)):
  assert al[i+4][20:]==bl[i+4][20:]
  if x[2]!='H':
   assert max(abs(y[d]-x[d]*.6188/.825)for d in (0,1))<1e-8
   continue
  near=[v if u==i else u for u,v in ae if i in (u,v)];assert len(near)==1
  c=near[0];assert ba[c][2]=='C'
  ov=[x[d]-aa[c][d]for d in (0,1)];nv=[y[d]-ba[c][d]for d in (0,1)]
  assert max(abs(ov[d]-nv[d])for d in (0,1))<1e-8
  lengths.append(math.hypot(*nv));assert abs(lengths[-1]-.3094)<1e-8
 for u,v in be:
  if ba[u][2]==ba[v][2]=='C':cc.append(math.dist(ba[u][:2],ba[v][:2]))
 assert len(lengths)==14 and len(cc)==5 and all(abs(x-.6188)<1e-8 for x in cc)
 return {'source':label,'uniform14CH':.3094,'uniform5CC':.6188,'CHVectorsAndIndexedGraphAndOtherFieldsUnchanged':True,'carbonScale':.6188/.825}
rows=[verify(before['mols'][key]['expanded'],after['mols'][key]['expanded'],'embedded')]
for p in old:
 if p.endswith('.mol'):rows.append(verify(old[p],Path(p).read_text(),p))
assert after['mols'][key]['expanded']==Path('mols/new_molecules/'+key+'_2D_Expanded.mol').read_text()
viewer='js/mulermoc-nom-molview-52.js';v=Path(viewer).read_text();o=old[viewer]
assert v==o.replace("// Professor's original 2-methylpentane: C-C/font = 3.488636..., rounded.","// Original reference C-C/font 3.49, shortened by the approved 25%.").replace(' / 3.49;',' / 2.6175;')
html='mulermoc-nom-52.html';h=Path(html).read_text();oh=old[html]
assert h==oh.replace('v=alkane-fixed-cc-20261030','v=alkane-cc-quarter-20261030')
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=[p for p in snap['fileHashes']if p not in allowed]
changed=[p for p in protected if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=snap['fileHashes'][p]]
assert not changed,changed
for p in [data_path,viewer]:subprocess.run([JSC,'-e','new Function(JSON.parse(readline()));'],input=json.dumps(Path(p).read_text())+'\n',text=True,check=True,capture_output=True)
for p in ['docs/checks/check-alkane-cc-quarter-20261030.py','docs/checks/test-alkane-cc-quarter-20261030.py']:ast.parse(Path(p).read_text())
diff=''.join(''.join(difflib.unified_diff(a.splitlines(True),Path(p).read_text().splitlines(True),fromfile='before/'+p,tofile='after/'+p))for p,a in old.items())
Path('docs/checks/alkane-cc-quarter-source-20261030.diff').write_text(diff)
result={'passed':True,'moleculesChanged':1,'sources':rows,'otherMoleculeRecordsUnchanged':len(after['mols'])-1,'otherFormsMetadataAndCodeByteIdentical':True,'viewerOnlyPrototypeRatioAndCommentChanged':True,'htmlOnly2CacheKeys':True,'protectedExistingFilesUnchanged':len(protected),'core3DScenariosReactUnchanged':True,'syntax':'2JS and2Python PASS'}
Path('docs/checks/alkane-cc-quarter-static-20261030.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
