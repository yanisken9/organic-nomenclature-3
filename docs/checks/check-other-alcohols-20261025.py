"""Focused five other-alcohol graph, geometry, explicit-H and provenance validation."""
from pathlib import Path
import argparse,json,math,itertools,hashlib,runpy,io
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,rdMolTransforms
ns=runpy.run_path('docs/checks/generate-other-alcohols-20261025.py');specs=ns['SPECS']

def check(folder,runtime=None):
 rows=[]
 for s in specs:
  query=ns['graph'](s);provenance=json.loads((folder/(s['key']+'_3D.provenance.json')).read_text())
  for form in ['Condensed','Expanded','Skeletal','3D']:
   p=folder/(s['key']+('_3D.sdf' if form=='3D' else '_2D_'+form+'.mol'));m=next(Chem.ForwardSDMolSupplier(io.BytesIO(p.read_bytes()),removeHs=False)) if form=='3D' else Chem.MolFromMolFile(str(p),removeHs=False);assert m is not None,p
   assert rdMolDescriptors.CalcMolFormula(m)==s['formula'],p
   assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(query,isomericSmiles=False),p
   assert all(a.GetFormalCharge()==0 and a.GetTotalValence()=={'C':4,'O':2,'H':1}[a.GetSymbol()] for a in m.GetAtoms()),p
   hs=sum(a.GetSymbol()=='H' for a in m.GetAtoms());assert hs==(sum(a.GetTotalNumHs() for a in query.GetAtoms()) if form in ['Expanded','3D'] else 0),p
   if form in ['Expanded','3D']:
    for oxygen in [a for a in m.GetAtoms() if a.GetSymbol()=='O']:assert sum(a.GetSymbol()=='H' for a in oxygen.GetNeighbors())==1,p
   c=m.GetConformer();assert all(math.isfinite(v) for xyz in c.GetPositions() for v in xyz),p
   clearance=min(c.GetAtomPosition(a).Distance(c.GetAtomPosition(b)) for a,b in itertools.combinations(range(m.GetNumAtoms()),2));assert clearance>.3,(p,clearance)
   mapping=provenance['atomMapping2Dto3D'] if form=='3D' else {str(i+1):i+1 for i in range(query.GetNumAtoms())}
   for a,b,order in s['edges']:assert m.GetBondBetweenAtoms(mapping[str(a)]-1,mapping[str(b)]-1).GetBondTypeAsDouble()==order,p
   for bond in m.GetBonds():
    distance=rdMolTransforms.GetBondLength(c,bond.GetBeginAtomIdx(),bond.GetEndAtomIdx())
    assert .7<distance<1.8,(p,distance)
    if form!='3D':
     expected=.78 if any(a.GetSymbol()=='H' for a in [bond.GetBeginAtom(),bond.GetEndAtom()]) else 1.17
     assert abs(distance-expected)<.0002,(p,distance)
     if form=='Expanded':
      a,b=c.GetAtomPosition(bond.GetBeginAtomIdx()),c.GetAtomPosition(bond.GetEndAtomIdx())
      assert min(abs(a.x-b.x),abs(a.y-b.y))<.0001,(p,'non-cardinal bond')
   if form!='3D':
    assert all(abs(xyz[2])<1e-6 for xyz in c.GetPositions()),p
    assert c.GetAtomPosition(0).x>c.GetAtomPosition(s['parent']-1).x,p
    if form!='Skeletal':assert max(c.GetAtomPosition(i).y for i in range(s['parent']))-min(c.GetAtomPosition(i).y for i in range(s['parent']))<.0001,p
    if form=='Expanded':
     for atom in m.GetAtoms():
      if any(b.GetBondTypeAsDouble()==3 for b in atom.GetBonds()):
       neighbors=[a.GetIdx() for a in atom.GetNeighbors()];assert len(neighbors)==2,p
       assert abs(rdMolTransforms.GetAngleDeg(c,neighbors[0],atom.GetIdx(),neighbors[1])-180)<.02,(p,'bent terminal alkyne H')
    if form=='Skeletal':
     for i in range(1,s['parent']-1):
      angle=180 if any(b.GetBondTypeAsDouble()==3 for b in m.GetAtomWithIdx(i).GetBonds()) else 120
      assert abs(rdMolTransforms.GetAngleDeg(c,i-1,i,i+1)-angle)<.02,(p,i)
    def cross(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
    for b1,b2 in itertools.combinations(m.GetBonds(),2):
     ids=[b1.GetBeginAtomIdx(),b1.GetEndAtomIdx(),b2.GetBeginAtomIdx(),b2.GetEndAtomIdx()]
     if len(set(ids))<4:continue
     a,b,c1,d=[c.GetAtomPosition(i) for i in ids]
     assert not(cross(a,b,c1)*cross(a,b,d)<-1e-8 and cross(c1,d,a)*cross(c1,d,b)<-1e-8),(p,ids)
   else:
    assert c.Is3D();assert hashlib.sha256(p.read_bytes()).hexdigest()==provenance['sha256']
    for atom in m.GetAtoms():
     if any(b.GetBondTypeAsDouble()==3 for b in atom.GetBonds()):
      neighbors=[a.GetIdx() for a in atom.GetNeighbors()];assert len(neighbors)==2,p
      assert rdMolTransforms.GetAngleDeg(c,neighbors[0],atom.GetIdx(),neighbors[1])>175,(p,'nonlinear3D triple')
    if runtime is not None:assert (runtime/p.name).read_bytes()==p.read_bytes()
    if provenance['source']=='PubChem':assert m.GetProp('PUBCHEM_COMPOUND_CID')==str(provenance['cid']);assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
   if form=='Expanded':
    hydrogens=[a.GetIdx() for a in m.GetAtoms() if a.GetSymbol()=='H']
    hh=min(c.GetAtomPosition(i).Distance(c.GetAtomPosition(j)) for i,j in itertools.combinations(hydrogens,2))
    assert hh>.55,(p,'H labels too close',hh)
   rows.append(dict(key=s['key'],form=form,formula=s['formula'],atoms=m.GetNumAtoms(),explicitH=hs,minimumClearance=clearance,source=provenance['source'] if form=='3D' else 'Authored 2D'))
 print(json.dumps({'forms':rows,'failures':[]},ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,default=Path('mols/new_molecules'));p.add_argument('--runtime',type=Path);a=p.parse_args();check(a.folder,a.runtime)
