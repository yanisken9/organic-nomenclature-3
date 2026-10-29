"""Approved Expanded acid layout: chemical/ID/coordinate preservation and scoped source checks.
--read-only suppresses writing the result; no application/browser mutation.
"""
from pathlib import Path
import json,subprocess,gzip,base64,hashlib,math,runpy,sys
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
NODE='/tmp/namelecule-react-tools/node-v24.22.1-darwin-x64/bin/node'
old={p:base64.b64decode(v).decode()for p,v in json.loads(gzip.decompress(Path('docs/checks/acid-layout-before-source-20261028.json.gz').read_bytes())).items()}
def extract(source):
 js='const r=new Function('+json.dumps('var window={};'+source+';return {examples:nameExamples,mols:window.MOL2D};')+')();process.stdout.write(JSON.stringify(r));'
 return json.loads(subprocess.check_output([NODE,'-e',js],text=True))
datafile='js/jsme-nick-nomeclature-moc2-data_52.js';before=extract(old[datafile]);after=extract(Path(datafile).read_text())
assert before['examples']==after['examples'];assert len(after['examples'])==130
newkeys={s['key']for s in json.loads(Path('docs/checks/acids-specs-20261028.json').read_text())}
parse=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py')['parse'];rows=[];changed=[]
for key,forms in before['mols'].items():
 for mode,text in forms.items():
  new=after['mols'][key][mode]
  if mode!='expanded':
   assert new==text,(key,mode);continue
  if not parse(text)[-1]:
   assert new==text,key;continue
  ls,n,nb,aa,bb,tt,xyz,edges,groups=parse(text)
  assert groups,key
  _,nn,nnb,naa,nbb,ntt,nxyz,nedges,ngroups=parse(new)
  assert len(groups)==len(ngroups)
  assert (n,nb,tt,edges,bb)==(nn,nnb,ntt,nedges,nbb),(key,'atom IDs / bonds')
  moved=set(); main={i-1 for i in after['examples'][key]['mainChain_Expanded']}
  for c,o,hs in groups:
   od=next(b if a==c else a for a,b,q in edges if q==2 and ((a==c and tt[b]=='O')or(b==c and tt[a]=='O')))
   moved.update([o,od]+hs)
  methyls=[]
  for i,t in enumerate(tt):
   if t!='C' or i in main or key not in newkeys:continue
   es=[b if a==i else a for a,b,q in edges if a==i or b==i];cs=[b for b in es if tt[b]=='C'];hs=[b for b in es if tt[b]=='H']
   if len(cs)!=1 or cs[0]not in main or len(hs)!=3 or abs(xyz[i][0]-xyz[cs[0]][0])>.0001:continue
   moved.update([i]+hs);methyls.append(i)
   assert abs(math.dist(nxyz[i],nxyz[cs[0]])-1.755)<.00011,(key,'stem')
   for h in hs:
    assert all(abs((xyz[h][j]-xyz[i][j])-(nxyz[h][j]-nxyz[i][j]))<.00011 for j in range(3)),(key,'CH3 distorted')
  for i in range(n):
   assert aa[i][30:]==naa[i][30:],(key,'atom properties',i)
   if i not in moved:assert aa[i]==naa[i],(key,'unexpected move',i)
  a=Chem.MolFromMolBlock(text,removeHs=False);b=Chem.MolFromMolBlock(new,removeHs=False);assert a and b
  assert Chem.MolToSmiles(Chem.RemoveHs(a),isomericSmiles=False)==Chem.MolToSmiles(Chem.RemoveHs(b),isomericSmiles=False),(key,'graph')
  assert rdMolDescriptors.CalcMolFormula(a)==rdMolDescriptors.CalcMolFormula(b),(key,'formula')
  for c,o,hs in ngroups:
   od=next(j if i==c else i for i,j,q in nedges if q==2 and ((i==c and ntt[j]=='O')or(j==c and ntt[i]=='O')))
   assert len(hs)==1;h=hs[0]
   assert abs(nxyz[c][0]-nxyz[od][0])<.00011 and abs(nxyz[c][1]-nxyz[od][1])>.7,(key,'vertical C=O')
   assert abs(nxyz[c][1]-nxyz[o][1])<.00011 and abs(nxyz[o][1]-nxyz[h][1])<.00011,(key,'horizontal C-O-H')
   assert (nxyz[o][0]-nxyz[c][0])*(nxyz[h][0]-nxyz[o][0])>0,(key,'outward H')
   for x,y in [(c,od),(c,o),(o,h)]:assert abs(math.dist(xyz[x],xyz[y])-math.dist(nxyz[x],nxyz[y]))<.00015,(key,'COOH length')
   cs=[j if i==c else i for i,j,q in nedges if (i==c and ntt[j]=='C')or(j==c and ntt[i]=='C')]
   if cs:assert (sum(nxyz[j][0]-nxyz[c][0]for j in cs))*(nxyz[o][0]-nxyz[c][0])<0,(key,'COOH outward')
  sdf=Path('mols/nomeclature-moc2',key+'_3D.sdf').read_text();mol3=Chem.MolFromMolBlock(sdf,removeHs=False);assert mol3
  assert Chem.MolToSmiles(Chem.RemoveHs(b),isomericSmiles=False)==Chem.MolToSmiles(Chem.RemoveHs(mol3),isomericSmiles=False),(key,'3D graph')
  source=Path('mols/new_molecules',key+'_2D_Expanded.mol')
  if source.exists():assert source.read_text()==new
  rows.append(dict(key=key,carboxyls=len(groups),methylStems=len(methyls),formula=rdMolDescriptors.CalcMolFormula(b)));changed.append(key)
assert len(rows)==15 and sum(r['carboxyls']for r in rows)==17 and sum(r['methylStems']for r in rows)==6
base=json.loads(Path('docs/checks/acid-layout-before-20261028.json').read_text())['files']
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for p,h in base.items():
 if p in allowed:continue
 assert Path(p).is_file()and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('protected changed',p)
 protected+=1
# The four-acid generator must reproduce all twelve source 2D assets exactly.
g=runpy.run_path('docs/checks/generate-acids-20261028.py')
for s in g['SPECS']:
 for mode,mol in g['forms'](s).items():
  stem=s['key']+'_2D_'+mode;assert g['block'](mol,stem)==Path('mols/new_molecules',stem+'.mol').read_text(),('generator',s['key'],mode)
result={'passed':True,'molecules':rows,'carboxyls':17,'shortenedMethylStems':6,'protectedFiles':protected,'core52SHA256':hashlib.sha256(Path('js/mulermoc-nom-core-52.js').read_bytes()).hexdigest(),'unchangedOtherForms':True,'unchangedAllRecords':True}
if '--read-only'not in sys.argv:Path('docs/checks/acid-layout-assets-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS 15 Expanded molecules / 17 vertical C=O / collinear C–O–H / 6 shorter methyl stems;',protected,'protected files unchanged')
