"""Three approved enynes using existing diene/alkyne MOL and RDKit conventions.
Run from repo root with RDKit2024.09.6. PubChem lookup cache is supplied separately.
Refuses to overwrite existing assets; does not edit application data or old molecules.
"""
from pathlib import Path
import json,math,hashlib,runpy,sys,io
from rdkit import Chem,rdBase
from rdkit.Chem import AllChem,rdDepictor,rdMolDescriptors,rdMolTransforms
SPECS=json.loads(Path('docs/checks/enynes-specs-20261024.json').read_text())
shared=runpy.run_path('docs/checks/generate-dienes-20261024.py')

def graph(spec):
 rw=Chem.RWMol()
 for _ in range(max(max(a,b) for a,b,o in spec['edges'])):rw.AddAtom(Chem.Atom('C'))
 for a,b,o in spec['edges']:rw.AddBond(a-1,b-1,{1:Chem.BondType.SINGLE,2:Chem.BondType.DOUBLE,3:Chem.BondType.TRIPLE}[o])
 m=rw.GetMol();Chem.SanitizeMol(m)
 assert Chem.MolToSmiles(m)==Chem.MolToSmiles(Chem.MolFromSmiles(spec['smiles']))
 assert rdMolDescriptors.CalcMolFormula(m)==spec['formula']
 return m

def expanded_form(m):
 expanded=shared['orthogonal_expanded'](m)
 # Existing enyne/alkyne convention: terminal C#C-H is linear even in the
 # orthogonal connectivity diagram. Other H use the established cardinal layout.
 conf=expanded.GetConformer()
 for atom in expanded.GetAtoms():
  if atom.GetSymbol()!='C':continue
  triples=[b.GetOtherAtom(atom) for b in atom.GetBonds() if b.GetBondTypeAsDouble()==3]
  if not triples:continue
  pos=conf.GetAtomPosition(atom.GetIdx());other=conf.GetAtomPosition(triples[0].GetIdx())
  vector=pos-other;vector*=.78/vector.Length()
  for n in atom.GetNeighbors():
   if n.GetSymbol()=='H':conf.SetAtomPosition(n.GetIdx(),pos+vector)
 return expanded

def block(m,key):
 text=shared['block'](m,key)
 # RDKit can emit crossed-double stereo3 even for two identical substituents.
 # Keep unknown stereo for genuine E/Z candidates; clear only impossible E/Z.
 potential={int(x.centeredOn) for x in Chem.FindPotentialStereo(m) if x.type==Chem.StereoType.Bond_Double}
 lines=text.splitlines();count=m.GetNumAtoms()
 for i,bond in enumerate(m.GetBonds()):
  line=4+count+i
  if bond.GetBondTypeAsDouble()==2 and i not in potential and lines[line][9:12].strip()=='3':
   lines[line]=lines[line][:9]+'  0'+lines[line][12:]
 return '\n'.join(lines)+'\n'

def validate_three(m,spec):
 assert m is not None and m.GetConformer().Is3D()
 assert rdMolDescriptors.CalcMolFormula(m)==spec['formula']
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(graph(spec),isomericSmiles=False)
 assert all(a.GetFormalCharge()==0 and a.GetTotalValence()==(4 if a.GetSymbol()=='C' else 1) for a in m.GetAtoms())
 assert sum(a.GetSymbol()=='H' for a in m.GetAtoms())==int(spec['formula'].split('H')[1])
 conf=m.GetConformer();assert all(math.isfinite(v) for pt in conf.GetPositions() for v in pt)
 for bond in m.GetBonds():
  a,b=bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()
  assert .8<rdMolTransforms.GetBondLength(conf,a,b)<1.8
  if bond.GetBondTypeAsDouble()==3:
   for center,other in [(a,b),(b,a)]:
    for n in m.GetAtomWithIdx(center).GetNeighbors():
     if n.GetIdx()!=other:assert rdMolTransforms.GetAngleDeg(conf,n.GetIdx(),center,other)>175
 for atom in m.GetAtoms():
  if atom.GetSymbol()=='C' and atom.GetHybridization()==Chem.HybridizationType.SP2:
   neighbors=[n.GetIdx() for n in atom.GetNeighbors()];assert len(neighbors)==3
   angles=[rdMolTransforms.GetAngleDeg(conf,neighbors[i],atom.GetIdx(),neighbors[j]) for i in range(3) for j in range(i)]
   assert all(105<a<135 for a in angles) and sum(angles)>355
 return m

def generate(lookup):
 folder=Path('mols/new_molecules');runtime=Path('mols/nomeclature-moc2')
 # Validate overwrite preconditions for the whole batch before writing.
 for spec in SPECS:
  for suffix in ['_2D_Condensed.mol','_2D_Expanded.mol','_2D_Skeletal.mol','_3D.sdf','_3D.provenance.json']:
   assert not (folder/(spec['key']+suffix)).exists(),spec['key']
  assert not (runtime/(spec['key']+'_3D.sdf')).exists()
 results=[]
 for index,spec in enumerate(SPECS):
  key=spec['key'];m=graph(spec);conf=Chem.Conformer(m.GetNumAtoms());conf.Set3D(False)
  xy=[(i*1.17,0) for i in range(spec['parent'])]
  directions={parent:direction for parent,direction in spec['branches']}
  for i in range(spec['parent'],m.GetNumAtoms()):
   neighbor=next(n.GetIdx() for n in m.GetAtomWithIdx(i).GetNeighbors() if n.GetIdx()<i)
   direction=directions.get(neighbor,1);x,y=xy[neighbor];xy.append((x,y+direction*1.17))
  for i,(x,y) in enumerate(xy):conf.SetAtomPosition(i,(x,y,0))
  m.AddConformer(conf)
  expanded=expanded_form(m)
  skeletal=Chem.Mol(m);rdDepictor.Compute2DCoords(skeletal,bondLength=1.17)
  shared['horizontal_skeletal'](skeletal,spec['parent'])
  candidate=next((r for r in lookup if r['key']==key),{})
  provenance={'key':key,'formula':spec['formula'],'smiles':spec['smiles'],'stereochemistry':'Unspecified by the requested name; one illustrative conformer; no R/S or E/Z assignment','pubchemLookup':candidate}
  sdf=None
  if candidate.get('path'):
   try:
    raw=Path(candidate['path']).read_bytes();three=validate_three(next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False)),spec)
    match=three.GetSubstructMatch(graph(spec));assert len(match)==m.GetNumAtoms()
    mapping={str(i+1):j+1 for i,j in enumerate(match)}
    provenance.update(source='PubChem',cid=candidate['cid'],downloadURL=candidate['sdfURL'],retrieved='2026-10-24',atomMapping2Dto3D=mapping,mainChain3D=[mapping[str(i)] for i in range(1,spec['parent']+1)])
    provenance['pubchemStereo']={p:three.GetProp(p) for p in three.GetPropNames() if 'STEREO_COUNT' in p}
    sdf=raw
   except (AssertionError,ValueError,RuntimeError) as e:provenance['pubchemRejected']='Candidate failed bounded graph/explicit-H/geometry validation: '+type(e).__name__
  if sdf is None:
   three=Chem.AddHs(m);three.RemoveAllConformers();params=AllChem.ETKDGv3();params.randomSeed=20261024+index;params.numThreads=1;params.pruneRmsThresh=.2
   ids=list(AllChem.EmbedMultipleConfs(three,numConfs=24,params=params));assert ids
   assert AllChem.MMFFHasAllMoleculeParams(three)
   optimized=AllChem.MMFFOptimizeMoleculeConfs(three,numThreads=1,maxIters=2000,mmffVariant='MMFF94s')
   candidates=[(e,cid) for cid,(status,e) in zip(ids,optimized) if status==0 and math.isfinite(e)];assert candidates
   energy,cid=min(candidates);chosen=Chem.Conformer(three.GetConformer(cid));three.RemoveAllConformers();three.AddConformer(chosen,assignId=True)
   Chem.RemoveStereochemistry(three);validate_three(three,spec)
   props={'NAMELECULE_SOURCE':'Locally generated RDKit, not PubChem','NAMELECULE_METHOD':'ETKDGv3, explicit H, MMFF94s; lowest energy converged sampled conformer','NAMELECULE_STEREOCHEMISTRY':provenance['stereochemistry']}
   sdf=(block(three,key)+'\n'+''.join('> <'+k+'>\n'+v+'\n\n' for k,v in props.items())+'$$$$\n').encode()
   provenance.update(source='local RDKit',rdkitVersion=rdBase.rdkitVersion,method=props['NAMELECULE_METHOD'],seed=params.randomSeed,conformers=len(ids),converged=len(candidates),energy=energy,atomMapping2Dto3D={str(i):i for i in range(1,m.GetNumAtoms()+1)},mainChain3D=list(range(1,spec['parent']+1)))
  provenance['sha256']=hashlib.sha256(sdf).hexdigest()
  for form,mol in [('Condensed',m),('Expanded',expanded),('Skeletal',skeletal)]:
   # Match existing enynes: triple at left, double at right; numbering from right.
   # Serialize 3D above first; this mirror belongs only to the 2D deliverables.
   conf2d=mol.GetConformer()
   for atom in range(mol.GetNumAtoms()):
    point=conf2d.GetAtomPosition(atom);conf2d.SetAtomPosition(atom,(-point.x,point.y,point.z))
   (folder/(key+'_2D_'+form+'.mol')).write_text(block(mol,key+'_2D_'+form))
  (folder/(key+'_3D.sdf')).write_bytes(sdf);(runtime/(key+'_3D.sdf')).write_bytes(sdf)
  (folder/(key+'_3D.provenance.json')).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
  results.append(provenance);print('GENERATED',key,provenance['source'],flush=True)
 return results
if __name__=='__main__':generate(json.loads(Path(sys.argv[1]).read_text()))
