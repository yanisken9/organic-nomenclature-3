"""Approved five aldehyde assets, existing V2000/MOL2D/SDF conventions.
Generate into --output only; refuses overwrite. PubChem cache supplied separately.
Condensed/Expanded parent horizontal, numbering right-to-left like butanol_1.
"""
from pathlib import Path
import argparse,json,math,hashlib
from rdkit import Chem,rdBase
from rdkit.Geometry import Point2D
from rdkit.Chem import AllChem,rdDepictor,rdMolDescriptors,rdMolTransforms
SPECS=json.loads(Path('docs/checks/aldehydes-specs-20261026.json').read_text())

def graph(s):
 rw=Chem.RWMol()
 for _ in range(s['carbons']):rw.AddAtom(Chem.Atom('C'))
 for _ in range(len(s['xy'])-s['carbons']):rw.AddAtom(Chem.Atom('O'))
 for a,b,order in s['edges']:rw.AddBond(a-1,b-1,{1:Chem.BondType.SINGLE,2:Chem.BondType.DOUBLE,3:Chem.BondType.TRIPLE}[order])
 m=rw.GetMol();Chem.SanitizeMol(m)
 assert Chem.MolToSmiles(m)==Chem.MolToSmiles(Chem.MolFromSmiles(s['smiles']))
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
 return m

def block(m,key):
 # Carbonyl bonds have no E/Z; export connectivity without stereo wedges.
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
  if atom.GetIdx()==0:directions=[(1,0),(0,-1),(0,1),(-1,0)]
  if atom.GetSymbol()=='O':directions=[(0,1),(0,-1),(-1,0),(1,0)]
  if any(b.GetBondTypeAsDouble()==3 for b in atom.GetBonds()):
   other=next(n for n in atom.GetNeighbors() if n.GetSymbol()!='H');point=conf.GetAtomPosition(other.GetIdx())
   directions=[(int(pos.x>point.x)-int(pos.x<point.x),int(pos.y>point.y)-int(pos.y<point.y))]
  free=[d for d in directions if d not in occupied]
  hs=[n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol()=='H'];assert len(hs)<=len(free)
  for h,(dx,dy) in zip(hs,free):conf.SetAtomPosition(h,(pos.x+.78*dx,pos.y+.78*dy,0))
 sk=Chem.Mol(m)
 # Preserve180deg at sp carbons; all other parent turns120deg.
 points=[(0.,0.)];angle=-math.pi/6
 for i in range(1,s['parent']):
  if i>1 and not any(b.GetBondTypeAsDouble()==3 for b in sk.GetAtomWithIdx(i-1).GetBonds()):angle=-angle
  x,y=points[-1];points.append((x-1.17*math.cos(angle),y+1.17*math.sin(angle)))
 parent_xy={i:Point2D(x,y) for i,(x,y) in enumerate(points)}
 rdDepictor.Compute2DCoords(sk,bondLength=1.17,coordMap=parent_xy,canonOrient=False)
 c=sk.GetConformer();a=c.GetAtomPosition(0);b=c.GetAtomPosition(s['parent']-1)
 turn=0 if s['parent']==1 else math.pi-math.atan2(b.y-a.y,b.x-a.x);co,si=math.cos(turn),math.sin(turn)
 xy=[(p[0]*co-p[1]*si,p[0]*si+p[1]*co) for p in c.GetPositions()]
 cx=(min(x for x,y in xy)+max(x for x,y in xy))/2;cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
 for i,(x,y) in enumerate(xy):c.SetAtomPosition(i,(x-cx,y-cy,0))
 # Condensed CH3/CH2 labels need slightly more horizontal clearance at the
 # approved uniform font size; preserve Expanded/Skeletal bond conventions.
 compact=Chem.Mol(m);cc=compact.GetConformer()
 for i in range(compact.GetNumAtoms()):
  p=cc.GetAtomPosition(i)
  # Branch stems were2.34; Condensed has no explicit H needing that clearance.
  y=p.y*.75 if i<s['carbons'] and i>=s['parent'] else p.y
  cc.SetAtomPosition(i,(p.x*1.2,y,0))
 if s['key']=='methanal':
  # Horizontal H-C=O backbone; the other C-bound H is drawn above C.
  cc.SetAtomPosition(0,(0,0,0));cc.SetAtomPosition(1,(1.17,0,0))
  ec=expanded.GetConformer();ec.SetAtomPosition(0,(0,0,0));ec.SetAtomPosition(1,(1.17,0,0))
  hs=[a.GetIdx() for a in expanded.GetAtoms() if a.GetSymbol()=='H']
  assert len(hs)==2
  ec.SetAtomPosition(hs[0],(-.78,0,0));ec.SetAtomPosition(hs[1],(0,.78,0))
 return {'Condensed':compact,'Expanded':expanded,'Skeletal':sk}

def three(s,cache):
 record=json.loads((cache/(s['key']+'.json')).read_text());query=graph(s)
 if record.get('source')=='PubChem':
  raw=(cache/(s['key']+'.sdf')).read_bytes()
  import io
  m=next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False))
  assert m is not None and m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
  provenance=record
  if m.HasProp('PUBCHEM_COMPOUND_CID'):provenance['cid']=int(m.GetProp('PUBCHEM_COMPOUND_CID'))
 else:
  m=Chem.AddHs(query);params=AllChem.ETKDGv3();params.randomSeed=20261026;params.numThreads=1
  ids=AllChem.EmbedMultipleConfs(m,numConfs=24,params=params);assert len(ids)
  scores=AllChem.MMFFOptimizeMoleculeConfs(m,numThreads=1,mmffVariant='MMFF94s',maxIters=1000)
  converged=[(energy,i) for i,(status,energy) in enumerate(scores) if status==0];assert converged
  energy,best=min(converged);chosen=Chem.Conformer(m.GetConformer(best));m.RemoveAllConformers();m.AddConformer(chosen,assignId=True)
  Chem.RemoveStereochemistry(m);raw=(Chem.MolToMolBlock(m,includeStereo=False)+'\n$$$$\n').encode()
  provenance={'source':'RDKit','rdkitVersion':rdBase.rdkitVersion,'method':'ETKDGv3 / MMFF94s, lowest converged among 24 sampled conformers','seed':20261026,'lookup':record,'energyKcalMol':energy}
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(query,isomericSmiles=False)
 match=Chem.RemoveHs(m).GetSubstructMatch(query);assert len(match)==query.GetNumAtoms()
 # Heavy atoms precede H in these source files; verify before using removed-H IDs.
 assert all(m.GetAtomWithIdx(i).GetSymbol()!='H' for i in match)
 mapping={str(i+1):v+1 for i,v in enumerate(match)}
 provenance.update(key=s['key'],name=s['name'],formula=s['formula'],retrievalDate='2026-10-26',sha256=hashlib.sha256(raw).hexdigest(),atomMapping2Dto3D=mapping,mainChain3D=[mapping[str(i)] for i in range(1,s['parent']+1)],stereochemistry='Unspecified; illustrative conformer does not specify R/S or E/Z')
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
