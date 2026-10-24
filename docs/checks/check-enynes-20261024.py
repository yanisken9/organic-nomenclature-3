"""Read-only RDKit/JSC batch validation for three compatible enynes."""
from pathlib import Path
import runpy,json,hashlib,math,itertools,subprocess
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,rdMolTransforms
ns=runpy.run_path('docs/checks/generate-enynes-20261024.py');SPECS=ns['SPECS']
for spec in SPECS:
 key=spec['key'];provenance=json.loads(Path('mols/new_molecules',key+'_3D.provenance.json').read_text())
 for form in ['Condensed','Expanded','Skeletal','3D']:
  path=Path('mols/new_molecules',key+('_3D.sdf' if form=='3D' else '_2D_'+form+'.mol'))
  m=Chem.MolFromMolFile(str(path),removeHs=False);assert m is not None,path
  assert rdMolDescriptors.CalcMolFormula(m)==spec['formula'],path
  assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(ns['graph'](spec)),path
  assert all(a.GetFormalCharge()==0 and a.GetTotalValence()==(4 if a.GetSymbol()=='C' else 1) for a in m.GetAtoms()),path
  h=sum(a.GetSymbol()=='H' for a in m.GetAtoms());assert h==(int(spec['formula'].split('H')[1]) if form in ['Expanded','3D'] else 0),path
  assert sum(b.GetBondTypeAsDouble()==2 for b in m.GetBonds())==1 and sum(b.GetBondTypeAsDouble()==3 for b in m.GetBonds())==1,path
  mapping=provenance['atomMapping2Dto3D'] if form=='3D' else {str(i):i for i in range(1,m.GetNumAtoms()+1)}
  for a,b,o in spec['edges']:assert m.GetBondBetweenAtoms(mapping[str(a)]-1,mapping[str(b)]-1).GetBondTypeAsDouble()==o,path
  conf=m.GetConformer();assert all(math.isfinite(v) for xyz in conf.GetPositions() for v in xyz),path
  for a,b in itertools.combinations(range(m.GetNumAtoms()),2):assert conf.GetAtomPosition(a).Distance(conf.GetAtomPosition(b))>.3,(path,a,b)
  if form=='3D':
   ns['validate_three'](m,spec)
   assert hashlib.sha256(path.read_bytes()).hexdigest()==provenance['sha256']
   assert Path('mols/nomeclature-moc2',path.name).read_bytes()==path.read_bytes()
   if provenance['source']=='PubChem':
    import io
    original=next(Chem.ForwardSDMolSupplier(io.BytesIO(path.read_bytes()),removeHs=False))
    assert original.GetProp('PUBCHEM_COMPOUND_CID')==str(provenance['cid'])
    assert original.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0','Generic requested record must not assert stereoisomer'
   assert provenance['mainChain3D']==[mapping[str(i)] for i in range(1,spec['parent']+1)]
  else:
   assert all(abs(xyz[2])<1e-5 for xyz in conf.GetPositions()),path
   assert conf.GetAtomPosition(0).x>conf.GetAtomPosition(spec['parent']-1).x,(path,'numbering must start at right')
   for bond in m.GetBonds():
    d=rdMolTransforms.GetBondLength(conf,bond.GetBeginAtomIdx(),bond.GetEndAtomIdx())
    assert abs(d-(.78 if 'H' in [bond.GetBeginAtom().GetSymbol(),bond.GetEndAtom().GetSymbol()] else 1.17))<.0002,(path,d)
   def cross(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
   for a,b in itertools.combinations(m.GetBonds(),2):
    ids=[a.GetBeginAtomIdx(),a.GetEndAtomIdx(),b.GetBeginAtomIdx(),b.GetEndAtomIdx()]
    if len(set(ids))<4:continue
    p,q,r,s=[conf.GetAtomPosition(i) for i in ids]
    assert not(cross(p,q,r)*cross(p,q,s)<-1e-8 and cross(r,s,p)*cross(r,s,q)<-1e-8),(path,ids)
   if form in ['Expanded','Skeletal']:
    for bond in m.GetBonds():
     if bond.GetBondTypeAsDouble()!=3:continue
     a,b=bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()
     for center,other in [(a,b),(b,a)]:
      for neighbor in m.GetAtomWithIdx(center).GetNeighbors():
       if neighbor.GetIdx()!=other:assert rdMolTransforms.GetAngleDeg(conf,neighbor.GetIdx(),center,other)>179,(path,center)
 print('PASS',key,spec['formula'],'four forms graph/H/valence/bonds/coordinates/3D/provenance')
# Reuse the existing production JS naming harness; run only the new18cases.
text=Path('docs/checks/test-dienes-naming-20261024.py').read_text();scope={};exec(text[:text.index("js='var run")],scope)
body=scope['body'];js='var run=new Function("key","mode","chainMode","sdf",'+json.dumps(body)+');var rows=[];'
for spec in SPECS:
 for mode in ['condensed','expanded','skeletal']:
  for chain in ['algorithmic','data']:
   args=[spec['key'],mode,chain,Path('mols/nomeclature-moc2',spec['key']+'_3D.sdf').read_text()]
   js+='rows.push('+json.dumps([spec['name'],spec['parent'],mode,chain])+'.concat([run('+','.join(json.dumps(x) for x in args)+')]));'
js+='print(JSON.stringify(rows));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e',js],capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
for name,n,mode,chain,result in json.loads(r.stdout):
 assert result['name']==name and result['series']=='enynes' and len(result['chain'])==n and len(result['chain3'])==n,result
 assert result['two']==result['three'],result
print('PASS18 production naming/2D3D parent and bond-order cases')
