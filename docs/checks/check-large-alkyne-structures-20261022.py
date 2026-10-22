from pathlib import Path
import json,math,sys
from collections import Counter
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,rdMolTransforms
folder=Path(sys.argv[1]) if len(sys.argv)>1 else Path('mols/new_molecules');key='ethyl_4_dimethyl_3_5_heptyne_1';records=[];canonical=None
for p in list(sorted(folder.glob(key+'_2D_*.mol')))+[folder/(key+'_3D.sdf')]:
 m=Chem.MolFromMolFile(str(p),removeHs=False) if p.suffix=='.mol' else next(iter(Chem.SDMolSupplier(str(p),removeHs=False)))
 assert m is not None and rdMolDescriptors.CalcMolFormula(m)=='C11H20'
 heavy=Chem.RemoveHs(m);smiles=Chem.MolToSmiles(heavy,isomericSmiles=False)
 if canonical is None:canonical=smiles
 assert canonical==smiles
 counts=Counter(a.GetSymbol() for a in m.GetAtoms());explicit='Expanded' in p.name or p.suffix=='.sdf'
 assert counts==({'C':11,'H':20} if explicit else {'C':11})
 assert all(a.GetTotalValence()==(4 if a.GetSymbol()=='C' else 1) for a in m.GetAtoms())
 assert m.GetNumBonds()==m.GetNumAtoms()-1
 assert sum(b.GetBondTypeAsDouble()==3 for b in m.GetBonds())==1
 chain=[1,2,3,4,5,6,7];assert [m.GetBondBetweenAtoms(a-1,b-1).GetBondTypeAsDouble() for a,b in zip(chain,chain[1:])]==[3,1,1,1,1,1]
 for pair in [(3,8),(4,9),(9,10),(5,11)]:assert m.GetBondBetweenAtoms(pair[0]-1,pair[1]-1)
 if explicit:
  hs=lambda nums:sum(sum(n.GetSymbol()=='H' for n in m.GetAtomWithIdx(i-1).GetNeighbors()) for i in nums)
  assert hs([9,10])==5 and hs([8,11])==6
 if 'Skeletal' in p.name:
  xyz=m.GetConformer().GetPositions();u=xyz[0]-xyz[1];v=xyz[2]-xyz[1];cos=float(u.dot(v)/(sum(u*u)**.5*sum(v*v)**.5));assert cos<-.99999
 if p.suffix=='.sdf':
  conf=m.GetConformer();assert conf.Is3D();angle=rdMolTransforms.GetAngleDeg(conf,0,1,2);assert angle>175
  assert all(math.isfinite(x) for row in conf.GetPositions() for x in row)
 records.append({'path':p.name,'atoms':dict(counts),'bonds':m.GetNumBonds(),'formula':rdMolDescriptors.CalcMolFormula(m)})
assert smiles==Chem.MolToSmiles(Chem.MolFromSmiles('C#CC(C)C(CC)C(C)CC'),isomericSmiles=False)
Path('/tmp/large-alkyne-structure-results.json').write_text(json.dumps(records,indent=2));print('PASS all4forms C11H20/valences/graph/parent7/tripleat1/ethylat4/methyl3,5/H5+H6/sp linearity')
