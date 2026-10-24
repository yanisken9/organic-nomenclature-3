"""Read-only validation of the user-approved 2D expanded drawing convention."""
from pathlib import Path
import runpy, math, re, json
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
mod=runpy.run_path('docs/checks/generate-dienes-20261024.py')
data=Path('js/jsme-nick-nomeclature-moc2-data_50.js').read_text()
for spec in mod['SPECS']:
 key=spec['key'];p=Path('mols/new_molecules',key+'_2D_Expanded.mol');text=p.read_text()

 m=Chem.MolFromMolFile(str(p),removeHs=False);c=m.GetConformer();assert all(b.GetStereo() not in (Chem.BondStereo.STEREOE,Chem.BondStereo.STEREOZ,Chem.BondStereo.STEREOCIS,Chem.BondStereo.STEREOTRANS) for b in m.GetBonds()),key;assert rdMolDescriptors.CalcMolFormula(m)==spec['formula']
 for i in range(spec['parent']):
  pos=c.GetAtomPosition(i);assert abs(pos.y)<1e-6 and abs(pos.x-i*1.17)<1e-6,key
 for b in m.GetBonds():
  a=c.GetAtomPosition(b.GetBeginAtomIdx());z=c.GetAtomPosition(b.GetEndAtomIdx());dx=abs(a.x-z.x);dy=abs(a.y-z.y)
  assert min(dx,dy)<1e-6 and max(dx,dy)>0,(key,b.GetIdx())
  hydrogen=any(x.GetSymbol()=='H' for x in [b.GetBeginAtom(),b.GetEndAtom()])
  assert abs(math.hypot(dx,dy)-(.78 if hydrogen else 1.17))<1e-5,key
 assert all(abs(v[2])<1e-6 for v in c.GetPositions())
 condensed=Chem.MolFromMolFile(str(p.with_name(key+'_2D_Condensed.mol')),removeHs=False)
 generated=mod['orthogonal_expanded'](condensed)
 for i in range(m.GetNumAtoms()):assert c.GetAtomPosition(i).Distance(generated.GetConformer().GetAtomPosition(i))<1e-5,key
 embedded=json.loads(re.search(r'const '+re.escape(key)+r'_2D_Expanded = ("[^\n]*");',data).group(1));assert embedded==text,key
 print('PASS',key,'horizontal parent,cardinal bonds,C-C1.17/C-H0.78,explicitH,embed,generator')
