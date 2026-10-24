"""Reproduce six local diene assets. Run with RDKit 2024.09.6; writes assets only.
Integration into data50 is a separate, reviewed step. Existing validated PubChem
3D assets/provenance are preserved; missing/local 3D assets use RDKit (currently
the 1,2-butadiene fallback). PubChem retrieval and validation are separate steps.
"""
from pathlib import Path
import json, math, hashlib
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem, rdDepictor, rdMolDescriptors, rdMolTransforms

SPECS = [
 dict(key='butadiene_1_3',name='1,3-βουταδιένιο',smiles='C=CC=C',formula='C4H6',display='CH2=CHCH=CH2',parent=4,edges=[(1,2,2),(2,3,1),(3,4,2)],branches=[]),
 dict(key='butadiene_1_2',name='1,2-βουταδιένιο',smiles='C=C=CC',formula='C4H6',display='CH2=C=CHCH3',parent=4,edges=[(1,2,2),(2,3,2),(3,4,1)],branches=[]),
 dict(key='pentadiene_1_4',name='1,4-πενταδιένιο',smiles='C=CCC=C',formula='C5H8',display='CH2=CHCH2CH=CH2',parent=5,edges=[(1,2,2),(2,3,1),(3,4,1),(4,5,2)],branches=[]),
 dict(key='methyl_3_pentadiene_1_3',name='3-μεθυλο-1,3-πενταδιένιο',smiles='C=CC(C)=CC',formula='C6H10',display='CH2=CHC(CH3)=CHCH3',parent=5,edges=[(1,2,2),(2,3,1),(3,4,2),(4,5,1),(3,6,1)],branches=[(2,1)]),
 dict(key='dimethyl_2_3_pentadiene_1_3',name='2,3-διμεθυλο-1,3-πενταδιένιο',smiles='C=C(C)C(C)=CC',formula='C7H12',display='CH2=C(CH3)C(CH3)=CHCH3',parent=5,edges=[(1,2,2),(2,3,1),(3,4,2),(4,5,1),(2,6,1),(3,7,1)],branches=[(1,1),(2,-1)]),
 dict(key='ethyl_3_dimethyl_4_5_hexadiene_1_4',name='3-αιθυλο-4,5-διμεθυλο-1,4-εξαδιένιο',smiles='C=CC(CC)C(C)=C(C)C',formula='C10H18',display='CH2=CHCH(CH2CH3)C(CH3)=C(CH3)CH3',parent=6,edges=[(1,2,2),(2,3,1),(3,4,1),(4,5,2),(5,6,1),(3,7,1),(7,8,1),(4,9,1),(5,10,1)],branches=[(2,1),(3,-1),(4,1)]),
]

def graph(spec):
 n=max(max(a,b) for a,b,_ in spec['edges']);rw=Chem.RWMol()
 for _ in range(n):rw.AddAtom(Chem.Atom('C'))
 for a,b,o in spec['edges']:rw.AddBond(a-1,b-1,Chem.BondType.DOUBLE if o==2 else Chem.BondType.SINGLE)
 mol=rw.GetMol();Chem.SanitizeMol(mol)
 assert Chem.MolToSmiles(mol)==Chem.MolToSmiles(Chem.MolFromSmiles(spec['smiles']))
 assert rdMolDescriptors.CalcMolFormula(mol)==spec['formula']
 return mol

def block(mol,key):
 text=Chem.MolToMolBlock(mol,includeStereo=False)
 return key+'\n'+text.split('\n',1)[1]

def orthogonal_expanded(mol):
 """Connectivity diagram, not a projection of hybridization or 3D geometry.
 Preserve heavy-atom coordinates of the horizontal condensed form and all atom
 IDs. Put explicit H on unused cardinal directions at C-H0.78 vs C-C1.17.
 """
 expanded=Chem.AddHs(mol);conf=expanded.GetConformer();conf.Set3D(False)
 directions=[(0,-1),(0,1),(-1,0),(1,0)]
 for atom in expanded.GetAtoms():
  if atom.GetSymbol()!='C':continue
  i=atom.GetIdx();pos=conf.GetAtomPosition(i);occupied=set()
  for neighbor in atom.GetNeighbors():
   if neighbor.GetSymbol()=='H':continue
   other=conf.GetAtomPosition(neighbor.GetIdx());dx=other.x-pos.x;dy=other.y-pos.y
   occupied.add((int(dx>0)-int(dx<0),int(dy>0)-int(dy<0)))
  free=[d for d in directions if d not in occupied]
  hydrogens=[n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol()=='H']
  assert len(hydrogens)<=len(free)
  # Terminal CH2 uses one continuation and one vertical H, like the supplied
  # teacher diagram. Internal CH uses the available downward direction first.
  if len(hydrogens)==2 and len(occupied)==1:
   horizontal=[d for d in free if d[1]==0]
   free=horizontal+[d for d in free if d[1]!=0]
  for h,(dx,dy) in zip(hydrogens,free):conf.SetAtomPosition(h,(pos.x+.78*dx,pos.y+.78*dy,0))
 return expanded

def horizontal_skeletal(mol, parent, whole_structure=False):
 """Rigid rotation/translation only: horizontal parent or parallel double bonds, centered bounds."""
 conf=mol.GetConformer();a=conf.GetAtomPosition(0);b=conf.GetAtomPosition(parent-1)
 angle=-math.atan2(b.y-a.y,b.x-a.x)
 if whole_structure:
  # Level the two parallel parent double bonds, rather than a statistical axis.
  a=conf.GetAtomPosition(0);b=conf.GetAtomPosition(1)
  angle=-math.atan2(b.y-a.y,b.x-a.x)
 c=math.cos(angle);s=math.sin(angle)
 xy=[(p[0]*c-p[1]*s,p[0]*s+p[1]*c) for p in conf.GetPositions()]
 cx=(min(x for x,y in xy)+max(x for x,y in xy))/2
 cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
 for i,(x,y) in enumerate(xy):conf.SetAtomPosition(i,(x-cx,y-cy,0))
 return mol

def generate(folder=Path('mols/new_molecules'),runtime=Path('mols/nomeclature-moc2')):
 folder.mkdir(parents=True,exist_ok=True);runtime.mkdir(parents=True,exist_ok=True)
 summary=[]
 for index,spec in enumerate(SPECS):
  key=spec['key'];mol=graph(spec);forms={}
  # Condensed: established horizontal parent, separated vertical branches.
  conf=Chem.Conformer(mol.GetNumAtoms());conf.Set3D(False)
  xy=[(i*1.17,0) for i in range(spec['parent'])]
  for a in range(spec['parent'],mol.GetNumAtoms()):
   neighbor=next(n.GetIdx() for n in mol.GetAtomWithIdx(a).GetNeighbors() if n.GetIdx()<a)
   sign=-1 if key=='dimethyl_2_3_pentadiene_1_3' and a==6 or key=='ethyl_3_dimethyl_4_5_hexadiene_1_4' and a==8 else 1
   x,y=xy[neighbor];xy.append((x,y+sign*1.17))
  for i,(x,y) in enumerate(xy):conf.SetAtomPosition(i,(x,y,0))
  mol.AddConformer(conf);forms['Condensed']=Chem.Mol(mol)
  expanded=orthogonal_expanded(mol);forms['Expanded']=expanded
  skeletal=Chem.Mol(mol);rdDepictor.Compute2DCoords(skeletal,bondLength=1.17)
  if key in ['dimethyl_2_3_pentadiene_1_3','ethyl_3_dimethyl_4_5_hexadiene_1_4']:horizontal_skeletal(skeletal,spec['parent'],whole_structure=key=='ethyl_3_dimethyl_4_5_hexadiene_1_4')
  forms['Skeletal']=skeletal
  for form,m in forms.items():(folder/(key+'_2D_'+form+'.mol')).write_text(block(m,key+'_2D_'+form))
  provenance_path=folder/(key+'_3D.provenance.json')
  if provenance_path.exists():
   saved=json.loads(provenance_path.read_text())
   if saved.get('source')=='PubChem':
    raw=(folder/(key+'_3D.sdf')).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==saved['sha256'],key
    assert (runtime/(key+'_3D.sdf')).read_bytes()==raw,key
    summary.append(saved)
    print('PRESERVED PubChem 3D',key,flush=True)
    continue
  three=Chem.AddHs(mol);three.RemoveAllConformers()
  params=AllChem.ETKDGv3();params.randomSeed=20261024+index;params.numThreads=1;params.pruneRmsThresh=.2
  ids=list(AllChem.EmbedMultipleConfs(three,numConfs=24,params=params));assert ids,key
  assert AllChem.MMFFHasAllMoleculeParams(three),key
  optimized=AllChem.MMFFOptimizeMoleculeConfs(three,numThreads=1,maxIters=2000,mmffVariant='MMFF94s')
  candidates=[(e,cid) for cid,(status,e) in zip(ids,optimized) if status==0 and math.isfinite(e)]
  assert candidates,key
  energy,cid=min(candidates);chosen=Chem.Conformer(three.GetConformer(cid));three.RemoveAllConformers();three.AddConformer(chosen,assignId=True)
  # The user specified connectivity, not stereochemistry. This is one illustrative
  # configuration; no R/S or E/Z identity is asserted in the name or exported bonds.
  Chem.RemoveStereochemistry(three)
  props={'NAMELECULE_SOURCE':'Locally generated RDKit, not PubChem','NAMELECULE_RDKIT_VERSION':rdBase.rdkitVersion,'NAMELECULE_METHOD':'ETKDGv3, explicit H, MMFF94s; lowest energy converged sampled conformer','NAMELECULE_SEED':str(params.randomSeed),'NAMELECULE_STEREOCHEMISTRY':'Unspecified in requested name; one illustrative configuration; no E/Z or R/S claim'}
  sdf=block(three,key)+'\n'+''.join('> <'+k+'>\n'+v+'\n\n' for k,v in props.items())+'$$$$\n'
  (folder/(key+'_3D.sdf')).write_text(sdf);(runtime/(key+'_3D.sdf')).write_text(sdf)
  provenance=dict(key=key,formula=spec['formula'],smiles=spec['smiles'],source='local RDKit; no PubChem CID',rdkitVersion=rdBase.rdkitVersion,method=props['NAMELECULE_METHOD'],stereochemistry=props['NAMELECULE_STEREOCHEMISTRY'],seed=params.randomSeed,conformers=len(ids),converged=len(candidates),energy=energy,mainChain3D=list(range(1,spec['parent']+1)),sha256=hashlib.sha256(sdf.encode()).hexdigest())
  (folder/(key+'_3D.provenance.json')).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n');summary.append(provenance)
  print('GENERATED',key,flush=True)
 return summary
if __name__=='__main__':generate()
