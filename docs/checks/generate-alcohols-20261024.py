"""Approved four-alcohol assets, existing V2000/MOL2D/SDF conventions.
Generate into --output only; refuses overwrite. PubChem cache supplied separately.
Condensed/Expanded parent horizontal, numbering right-to-left like butanol_1.
"""
from pathlib import Path
import argparse,json,math,hashlib
from rdkit import Chem,rdBase
from rdkit.Geometry import Point2D
from rdkit.Chem import AllChem,rdDepictor,rdMolDescriptors,rdMolTransforms
SPECS=json.loads(Path('docs/checks/alcohols-specs-20261024.json').read_text())

def graph(s):
 rw=Chem.RWMol()
 for _ in range(s['carbons']):rw.AddAtom(Chem.Atom('C'))
 rw.AddAtom(Chem.Atom('O'))
 for a,b in s['edges']:rw.AddBond(a-1,b-1,Chem.BondType.SINGLE)
 m=rw.GetMol();Chem.SanitizeMol(m)
 assert Chem.MolToSmiles(m)==Chem.MolToSmiles(Chem.MolFromSmiles(s['smiles']))
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
 return m

def block(m,key):
 text=Chem.MolToMolBlock(m,includeStereo=False)
 return key+'\n'+text.split('\n',1)[1]

def forms(s):
 m=graph(s);conf=Chem.Conformer(m.GetNumAtoms());conf.Set3D(False)
 for i,(x,y) in enumerate(s['xy']):conf.SetAtomPosition(i,(-1.17*x,1.17*y,0))
 m.AddConformer(conf);expanded=Chem.AddHs(m);conf=expanded.GetConformer();conf.Set3D(False)
 for atom in expanded.GetAtoms():
  if atom.GetSymbol()=='H':continue
  pos=conf.GetAtomPosition(atom.GetIdx());occupied=set()
  for nb in atom.GetNeighbors():
   if nb.GetSymbol()=='H':continue
   other=conf.GetAtomPosition(nb.GetIdx());dx=other.x-pos.x;dy=other.y-pos.y
   occupied.add((int(dx>0)-int(dx<0),int(dy>0)-int(dy<0)))
  directions=[(0,-1),(0,1),(-1,0),(1,0)]
  if atom.GetSymbol()=='O':directions=[(0,1),(0,-1),(-1,0),(1,0)]
  free=[d for d in directions if d not in occupied]
  hs=[n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol()=='H'];assert len(hs)<=len(free)
  for h,(dx,dy) in zip(hs,free):conf.SetAtomPosition(h,(pos.x+.78*dx,pos.y+.78*dy,0))
 # User-approved drawing exception: lift the whole isopropyl group by1.17
 # in Expanded only; its attachment C-C becomes2.34, all other bonds unchanged.
 if s['key']=='isopropyl_4_dimethyl_3_5_heptanol_2':
  branch={9,10,11}
  branch.update(atom.GetIdx() for atom in expanded.GetAtoms() if atom.GetSymbol()=='H' and any(n.GetIdx() in {9,10,11} for n in atom.GetNeighbors()))
  for i in branch:
   p=conf.GetAtomPosition(i);conf.SetAtomPosition(i,(p.x,p.y+1.17,0))
 sk=Chem.Mol(m)
 # Constrain the established parent to a regular horizontal zigzag; unconstrained
 # layout can snake even when its endpoint axis is level.
 parent_xy={i:Point2D(-1.17*math.sqrt(3)/2*i,.585*(i%2)) for i in range(s['parent'])}
 rdDepictor.Compute2DCoords(sk,bondLength=1.17,coordMap=parent_xy,canonOrient=False)
 c=sk.GetConformer();a=c.GetAtomPosition(0);b=c.GetAtomPosition(s['parent']-1)
 angle=math.pi-math.atan2(b.y-a.y,b.x-a.x);co,si=math.cos(angle),math.sin(angle)
 xy=[(p[0]*co-p[1]*si,p[0]*si+p[1]*co) for p in c.GetPositions()]
 cx=(min(x for x,y in xy)+max(x for x,y in xy))/2;cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
 for i,(x,y) in enumerate(xy):c.SetAtomPosition(i,(x-cx,y-cy,0))
 return {'Condensed':m,'Expanded':expanded,'Skeletal':sk}

def three(s,cache):
 record=json.loads((cache/(s['key']+'.json')).read_text());query=graph(s)
 if record.get('source')=='PubChem':
  raw=(cache/(s['key']+'.sdf')).read_bytes()
  import io
  m=next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False))
  assert m is not None and m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
  provenance=record
 else:
  m=Chem.AddHs(query);params=AllChem.ETKDGv3();params.randomSeed=20261024;params.numThreads=1
  ids=AllChem.EmbedMultipleConfs(m,numConfs=24,params=params);assert len(ids)
  scores=AllChem.MMFFOptimizeMoleculeConfs(m,numThreads=1,mmffVariant='MMFF94s',maxIters=1000)
  converged=[(energy,i) for i,(status,energy) in enumerate(scores) if status==0];assert converged
  energy,best=min(converged);chosen=Chem.Conformer(m.GetConformer(best));m.RemoveAllConformers();m.AddConformer(chosen,assignId=True)
  Chem.RemoveStereochemistry(m);raw=(Chem.MolToMolBlock(m)+'\n$$$$\n').encode()
  provenance={'source':'RDKit','rdkitVersion':rdBase.rdkitVersion,'method':'ETKDGv3 / MMFF94s, lowest converged among 24 sampled conformers','seed':20261024,'lookup':record,'energyKcalMol':energy}
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(query,isomericSmiles=False)
 match=Chem.RemoveHs(m).GetSubstructMatch(query);assert len(match)==query.GetNumAtoms()
 # Heavy atoms precede H in these source files; verify before using removed-H IDs.
 assert all(m.GetAtomWithIdx(i).GetSymbol()!='H' for i in match)
 mapping={str(i+1):v+1 for i,v in enumerate(match)}
 provenance.update(key=s['key'],name=s['name'],formula=s['formula'],retrievalDate='2026-10-24',sha256=hashlib.sha256(raw).hexdigest(),atomMapping2Dto3D=mapping,mainChain3D=[mapping[str(i)] for i in range(1,s['parent']+1)],stereochemistry='Unspecified; illustrative conformer does not assign R/S')
 return raw,provenance

def generate(output,cache):
 output.mkdir(parents=True,exist_ok=True)
 for s in SPECS:
  for form,m in forms(s).items():
   p=output/(s['key']+'_2D_'+form+'.mol');assert not p.exists(),p;p.write_text(block(m,p.stem))
  raw,provenance=three(s,cache)
  p=output/(s['key']+'_3D.sdf');assert not p.exists();p.write_bytes(raw)
  (output/(s['key']+'_3D.provenance.json')).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
  print('GENERATED',s['key'],s['formula'],provenance['source'],flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--pubchem-cache',type=Path,required=True);args=parser.parse_args();generate(args.output,args.pubchem_cache)
