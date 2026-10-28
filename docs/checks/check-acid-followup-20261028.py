"""Approved acid follow-up: chemical/ID/coordinate preservation and scoped source checks.
--read-only suppresses writing the result; no application/browser mutation.
"""
from pathlib import Path
import json,subprocess,gzip,base64,hashlib,math,runpy,sys
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
NODE='/tmp/namelecule-react-tools/node-v24.22.1-darwin-x64/bin/node'
old={p:base64.b64decode(v).decode()for p,v in json.loads(gzip.decompress(Path('docs/checks/acid-followup-before-source-20261028.json.gz').read_bytes())).items()}
def extract(source):
 js='const r=new Function('+json.dumps('var window={};'+source+';return {examples:nameExamples,mols:window.MOL2D};')+')();process.stdout.write(JSON.stringify(r));'
 return json.loads(subprocess.check_output([NODE,'-e',js],text=True))
datafile='js/jsme-nick-nomeclature-moc2-data_52.js';before=extract(old[datafile]);after=extract(Path(datafile).read_text())
assert before['examples']==after['examples'];assert len(after['examples'])==130
parse=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py')['parse'];rows=[];changed=[]
for key,forms in before['mols'].items():
 for mode,text in forms.items():
  new=after['mols'][key][mode]
  if new==text:continue
  assert mode=='expanded',key
  ls,n,nb,aa,bb,tt,xyz,edges,groups=parse(text)
  assert groups,key
  _,nn,nnb,naa,nbb,ntt,nxyz,nedges,ngroups=parse(new)
  assert len(groups)==len(ngroups)
  moved={h for c,o,hs in groups for h in hs}
  for i in range(n):
   assert aa[i][30:]==naa[i][30:],(key,'existing atom properties',i)
   if i not in moved:assert aa[i]==naa[i],(key,'existing atom moved',i)
  assert nbb[:nb]==bb and all(t=='H'for t in ntt[n:]),key
  a=Chem.MolFromMolBlock(text,removeHs=False);b=Chem.MolFromMolBlock(new,removeHs=False);assert a and b
  assert Chem.MolToSmiles(Chem.RemoveHs(a),isomericSmiles=False)==Chem.MolToSmiles(Chem.RemoveHs(b),isomericSmiles=False),(key,'graph')
  assert rdMolDescriptors.CalcMolFormula(a)==rdMolDescriptors.CalcMolFormula(b),(key,'formula')
  for c,o,hs in ngroups:
   assert len(hs)==1,(key,'OH H missing');h=hs[0];v=tuple(nxyz[h][i]-nxyz[o][i]for i in range(3))
   assert abs(v[1])<.00011 and abs(v[2])<.00011 and .7799<=abs(v[0])<=.8251,(key,'nonhorizontal OH',v)
   assert (o,h,1)in nedges or(h,o,1)in nedges
   near=min(math.dist(nxyz[h],p)for i,p in enumerate(nxyz)if i not in [h,o]);assert near>.5,(key,'OH H collision',near)
  sdf=Path('mols/nomeclature-moc2',key+'_3D.sdf').read_text();mol3=Chem.MolFromMolBlock(sdf,removeHs=False);assert mol3
  assert Chem.MolToSmiles(Chem.RemoveHs(b),isomericSmiles=False)==Chem.MolToSmiles(Chem.RemoveHs(mol3),isomericSmiles=False),(key,'3D graph')
  source=Path('mols/new_molecules',key+'_2D_Expanded.mol')
  if source.exists():assert source.read_text()==new
  rows.append(dict(key=key,carboxyls=len(groups),oldAtoms=n,newAtoms=nn,addedH=nn-n,formula=rdMolDescriptors.CalcMolFormula(b)));changed.append(key)
assert len(rows)==15 and sum(r['carboxyls']for r in rows)==17 and sum(r['addedH']for r in rows)==13
base=json.loads(Path('docs/checks/acid-followup-before-20261028.json').read_text())['files']
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for p,h in base.items():
 if p in allowed:continue
 assert Path(p).is_file()and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('protected changed',p)
 protected+=1
# The four-acid generator must reproduce its current Expanded assets exactly.
g=runpy.run_path('docs/checks/generate-acids-20261028.py')
for s in g['SPECS']:
 stem=s['key']+'_2D_Expanded';assert g['block'](g['forms'](s)['Expanded'],stem)==Path('mols/new_molecules',stem+'.mol').read_text(),('generator',s['key'])
result={'passed':True,'molecules':rows,'carboxyls':17,'addedHydrogens':13,'protectedFiles':protected,'core52SHA256':hashlib.sha256(Path('js/mulermoc-nom-core-52.js').read_bytes()).hexdigest(),'unchangedOtherForms':True,'unchangedAllRecords':True}
if '--read-only'not in sys.argv:Path('docs/checks/acid-followup-assets-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS 15 Expanded molecules / 17 horizontal explicit O–H / 13 appended H;',protected,'protected files unchanged')
