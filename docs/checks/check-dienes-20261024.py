"""Read-only chemical/coordinate checks; run from repo root with RDKit."""
from pathlib import Path
import runpy, math, itertools, json, hashlib
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, rdMolTransforms
SPECS=runpy.run_path('docs/checks/generate-dienes-20261024.py')['SPECS']
for spec in SPECS:
 key=spec['key'];expected=Chem.MolToSmiles(Chem.MolFromSmiles(spec['smiles']),isomericSmiles=False)
 for form in ['Condensed','Expanded','Skeletal','3D']:
  p=Path('mols/new_molecules')/(key+('_3D.sdf' if form=='3D' else '_2D_'+form+'.mol'))
  m=Chem.MolFromMolFile(str(p),removeHs=False);assert m is not None,p
  assert rdMolDescriptors.CalcMolFormula(m)==spec['formula'],p
  assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==expected,p
  assert all(a.GetFormalCharge()==0 and a.GetTotalValence()==(4 if a.GetSymbol()=='C' else 1) for a in m.GetAtoms()),p
  assert sum(b.GetBondTypeAsDouble()==2 for b in m.GetBonds())==2,p
  explicit=form in ['Expanded','3D'];h=sum(a.GetSymbol()=='H' for a in m.GetAtoms())
  assert h==(int(spec['formula'].split('H')[1]) if explicit else 0),p
  mapping=list(range(m.GetNumAtoms()))
  if form=='3D':
   provenance=json.loads(p.with_suffix('.provenance.json').read_text())
   assert hashlib.sha256(p.read_bytes()).hexdigest()==provenance['sha256'],p
   if provenance['source']=='PubChem':
    mapping=[provenance['atomMapping2Dto3D'][str(i+1)]-1 for i in range(max(max(a,b) for a,b,o in spec['edges']))]
    assert len(set(mapping))==max(max(a,b) for a,b,o in spec['edges']),p
    assert provenance['mainChain3D']==[mapping[i]+1 for i in range(spec['parent'])],p
  for a,b,o in spec['edges']:assert m.GetBondBetweenAtoms(mapping[a-1],mapping[b-1]).GetBondTypeAsDouble()==o,p
  conf=m.GetConformer();assert all(math.isfinite(v) for xyz in conf.GetPositions() for v in xyz),p
  for a,b in itertools.combinations(range(m.GetNumAtoms()),2):
   d=conf.GetAtomPosition(a).Distance(conf.GetAtomPosition(b));assert d>.3,(p,a,b,d)
  if form!='3D':
   assert all(abs(x[2])<1e-5 for x in conf.GetPositions()),p
   # Reject proper crossings of nonadjacent bonds (touches/collinearity handled
   # separately by atom clearance; rendered label clearance needs browser review).
   def cross(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
   for b1,b2 in itertools.combinations(m.GetBonds(),2):
    ids=[b1.GetBeginAtomIdx(),b1.GetEndAtomIdx(),b2.GetBeginAtomIdx(),b2.GetEndAtomIdx()]
    if len(set(ids))<4:continue
    a,b,c,d=[conf.GetAtomPosition(i) for i in ids]
    assert not(cross(a,b,c)*cross(a,b,d)<-1e-8 and cross(c,d,a)*cross(c,d,b)<-1e-8),(p,ids)
  else:
   assert Path('mols/nomeclature-moc2',p.name).read_bytes()==p.read_bytes(),p
   assert conf.Is3D(),p
   for bond in m.GetBonds():
    d=rdMolTransforms.GetBondLength(conf,bond.GetBeginAtomIdx(),bond.GetEndAtomIdx());assert .85<d<1.7,(p,d)
  if key=='butadiene_1_2' and form in ['Skeletal','3D']:
   angle=rdMolTransforms.GetAngleDeg(conf,0,1,2);assert angle>175,(p,angle)
   if form=='3D':
    # H on C1 and C4 attached to terminal C3 define the two allene end planes.
    h1=next(n.GetIdx() for n in m.GetAtomWithIdx(0).GetNeighbors() if n.GetSymbol()=='H')
    import numpy as np
    xyz=conf.GetPositions();axis=xyz[2]-xyz[0];axis/=np.linalg.norm(axis)
    u=xyz[h1]-xyz[0];v=xyz[3]-xyz[2];u-=u.dot(axis)*axis;v-=v.dot(axis)*axis
    cosine=abs(float(u.dot(v)/(np.linalg.norm(u)*np.linalg.norm(v))));assert cosine<.15,(p,cosine)
 print('PASS',key,'four forms, graph/formula/valence/H/coordinates/crossings/3D',flush=True)
