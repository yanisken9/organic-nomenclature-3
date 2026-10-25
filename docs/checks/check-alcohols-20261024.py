"""Focused four-alcohol graph, geometry, explicit-H and provenance validation."""
from pathlib import Path
import argparse,json,math,itertools,hashlib,runpy,io
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,rdMolTransforms
ns=runpy.run_path('docs/checks/generate-alcohols-20261024.py');specs=ns['SPECS']

def check(folder,runtime=None):
 rows=[]
 for s in specs:
  query=ns['graph'](s);provenance=json.loads((folder/(s['key']+'_3D.provenance.json')).read_text())
  for form in ['Condensed','Expanded','Skeletal','3D']:
   p=folder/(s['key']+('_3D.sdf' if form=='3D' else '_2D_'+form+'.mol'));m=next(Chem.ForwardSDMolSupplier(io.BytesIO(p.read_bytes()),removeHs=False)) if form=='3D' else Chem.MolFromMolFile(str(p),removeHs=False);assert m is not None,p
   assert rdMolDescriptors.CalcMolFormula(m)==s['formula'],p
   assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(query,isomericSmiles=False),p
   assert all(a.GetFormalCharge()==0 and a.GetTotalValence()=={'C':4,'O':2,'H':1}[a.GetSymbol()] for a in m.GetAtoms()),p
   hs=sum(a.GetSymbol()=='H' for a in m.GetAtoms());assert hs==(2*s['carbons']+2 if form in ['Expanded','3D'] else 0),p
   oxygen=next(a for a in m.GetAtoms() if a.GetSymbol()=='O')
   if form in ['Expanded','3D']:assert sum(a.GetSymbol()=='H' for a in oxygen.GetNeighbors())==1,p
   c=m.GetConformer();assert all(math.isfinite(v) for xyz in c.GetPositions() for v in xyz),p
   clearance=min(c.GetAtomPosition(a).Distance(c.GetAtomPosition(b)) for a,b in itertools.combinations(range(m.GetNumAtoms()),2));assert clearance>.3,(p,clearance)
   mapping=provenance['atomMapping2Dto3D'] if form=='3D' else {str(i+1):i+1 for i in range(query.GetNumAtoms())}
   for a,b in s['edges']:assert m.GetBondBetweenAtoms(mapping[str(a)]-1,mapping[str(b)]-1).GetBondTypeAsDouble()==1,p
   for bond in m.GetBonds():
    distance=rdMolTransforms.GetBondLength(c,bond.GetBeginAtomIdx(),bond.GetEndAtomIdx())
    assert .7<distance<(2.35 if form=='Expanded' and s['key']=='isopropyl_4_dimethyl_3_5_heptanol_2' and {bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()}=={3,9} else 1.8),(p,distance)
    if form!='3D':
     attachment=(s['key']=='isopropyl_4_dimethyl_3_5_heptanol_2' and form=='Expanded' and {bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()}=={3,9})
     expected=2.34 if attachment else .78 if any(a.GetSymbol()=='H' for a in [bond.GetBeginAtom(),bond.GetEndAtom()]) else 1.17
     assert abs(distance-expected)<.0002,(p,distance)
     if form=='Expanded':
      a,b=c.GetAtomPosition(bond.GetBeginAtomIdx()),c.GetAtomPosition(bond.GetEndAtomIdx())
      assert min(abs(a.x-b.x),abs(a.y-b.y))<.0001,(p,'non-cardinal bond')
   if form!='3D':
    assert all(abs(xyz[2])<1e-6 for xyz in c.GetPositions()),p
    assert c.GetAtomPosition(0).x>c.GetAtomPosition(s['parent']-1).x,p
    if form!='Skeletal':assert max(c.GetAtomPosition(i).y for i in range(s['parent']))-min(c.GetAtomPosition(i).y for i in range(s['parent']))<.0001,p
    if form=='Skeletal':
     for i in range(1,s['parent']-1):assert abs(rdMolTransforms.GetAngleDeg(c,i-1,i,i+1)-120)<.02,(p,i)
    def cross(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
    for b1,b2 in itertools.combinations(m.GetBonds(),2):
     ids=[b1.GetBeginAtomIdx(),b1.GetEndAtomIdx(),b2.GetBeginAtomIdx(),b2.GetEndAtomIdx()]
     if len(set(ids))<4:continue
     a,b,c1,d=[c.GetAtomPosition(i) for i in ids]
     assert not(cross(a,b,c1)*cross(a,b,d)<-1e-8 and cross(c1,d,a)*cross(c1,d,b)<-1e-8),(p,ids)
   else:
    assert c.Is3D();assert hashlib.sha256(p.read_bytes()).hexdigest()==provenance['sha256']
    if runtime is not None:assert (runtime/p.name).read_bytes()==p.read_bytes()
    if provenance['source']=='PubChem':assert m.GetProp('PUBCHEM_COMPOUND_CID')==str(provenance['cid']);assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
   rows.append(dict(key=s['key'],form=form,formula=s['formula'],atoms=m.GetNumAtoms(),explicitH=hs,minimumClearance=clearance,source=provenance['source'] if form=='3D' else 'Authored 2D'))
 print(json.dumps({'forms':rows,'failures':[]},ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,default=Path('mols/new_molecules'));p.add_argument('--runtime',type=Path);a=p.parse_args();check(a.folder,a.runtime)
