"""Seven approved ether assets; reuse existing explicit-H/2D/3D conventions.
Requires an isolated RDKit environment and a supplied PubChem response cache.
Refuses to overwrite assets. Does not modify the registry or any old molecule.
"""
from pathlib import Path
import json,argparse,hashlib,math
from rdkit import Chem,rdBase
from rdkit.Chem import AllChem,rdDepictor,rdMolDescriptors
from rdkit.Geometry import Point2D
import io
SPECS=json.loads(Path('docs/checks/ethers-specs-20261026.json').read_text())

def graph(s):
 rw=Chem.RWMol()
 for _ in range(s['carbons']):rw.AddAtom(Chem.Atom('C'))
 rw.AddAtom(Chem.Atom('O'))
 for a,b in s['edges']:rw.AddBond(a-1,b-1,Chem.BondType.SINGLE)
 m=rw.GetMol();Chem.SanitizeMol(m)
 assert Chem.MolToSmiles(m)==Chem.MolToSmiles(Chem.MolFromSmiles(s['smiles']))
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
 return m

def forms(s):
 m=graph(s);c=Chem.Conformer(m.GetNumAtoms());c.Set3D(False)
 for i,(x,y) in enumerate(s['xy']):c.SetAtomPosition(i,(-1.17*x,1.17*y,0))
 m.AddConformer(c);expanded=Chem.AddHs(m);c=expanded.GetConformer();c.Set3D(False)
 for atom in expanded.GetAtoms():
  if atom.GetSymbol()=='H':continue
  p=c.GetAtomPosition(atom.GetIdx());occupied=set()
  for n in atom.GetNeighbors():
   if n.GetSymbol()=='H':continue
   q=c.GetAtomPosition(n.GetIdx());occupied.add((round((q.x-p.x)/1.17),round((q.y-p.y)/1.17)))
  free=[d for d in [(0,-1),(0,1),(-1,0),(1,0)] if d not in occupied]
  hs=[n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol()=='H'];assert len(hs)<=len(free)
  for h,(dx,dy) in zip(hs,free):c.SetAtomPosition(h,(p.x+.78*dx,p.y+.78*dy,0))
 sk=Chem.Mol(m)
 rdDepictor.Compute2DCoords(sk,bondLength=1.17,coordMap={i:Point2D(-1.17*math.sqrt(3)/2*i,.585*(i%2)) for i in range(s['parent'])},canonOrient=False)
 # Orient the C-O-C chord horizontally; retain the native skeletal angles.
 c=sk.GetConformer();o=s['carbons'];ns=[n.GetIdx() for n in sk.GetAtomWithIdx(o).GetNeighbors()]
 a=c.GetAtomPosition(ns[0]);b=c.GetAtomPosition(ns[1])
 angle=-math.atan2(b.y-a.y,b.x-a.x)
 if angle>math.pi/2:angle-=math.pi
 if angle<-math.pi/2:angle+=math.pi
 co,si=math.cos(angle),math.sin(angle)
 xy=[(p[0]*co-p[1]*si,p[0]*si+p[1]*co) for p in c.GetPositions()]
 cx=(min(x for x,y in xy)+max(x for x,y in xy))/2;cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
 for i,(x,y) in enumerate(xy):c.SetAtomPosition(i,(x-cx,y-cy,0))
 return dict(Condensed=m,Expanded=expanded,Skeletal=sk)

def three(s,cache):
 rec=json.loads((cache/(s['key']+'.json')).read_text());q=graph(s)
 if rec['source']=='PubChem':
  raw=(cache/(s['key']+'.sdf')).read_bytes();m=next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False))
  assert m is not None
  # A 3D conformer can induce RDKit chiral tags even for a PubChem
  # undefined center. Source identity, not that illustrative geometry, governs.
  assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
  assert m.GetProp('PUBCHEM_BOND_DEF_STEREO_COUNT')=='0'
  if m.HasProp('PUBCHEM_COMPOUND_CID'):rec['cid']=int(m.GetProp('PUBCHEM_COMPOUND_CID'))
 else:
  m=Chem.AddHs(q);params=AllChem.ETKDGv3();params.randomSeed=20261026;params.numThreads=1
  ids=AllChem.EmbedMultipleConfs(m,numConfs=24,params=params);assert len(ids)
  scores=AllChem.MMFFOptimizeMoleculeConfs(m,numThreads=1,mmffVariant='MMFF94s',maxIters=1000)
  energy,best=min((energy,i) for i,(status,energy) in enumerate(scores) if status==0)
  c=Chem.Conformer(m.GetConformer(best));m.RemoveAllConformers();m.AddConformer(c,assignId=True);Chem.RemoveStereochemistry(m)
  raw=(Chem.MolToMolBlock(m)+'\n$$$$\n').encode();rec=dict(source='RDKit',rdkitVersion=rdBase.rdkitVersion,method='ETKDGv3 / MMFF94s; lowest of 24 converged candidates',seed=20261026,lookup=rec,energyKcalMol=energy)
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(q,isomericSmiles=False)
 assert m.GetNumAtoms()==s['carbons']+1+2*s['carbons']+2
 match=Chem.RemoveHs(m).GetSubstructMatch(q);assert len(match)==q.GetNumAtoms()
 assert all(m.GetAtomWithIdx(i).GetSymbol()!='H' for i in match)
 mapping={str(i+1):v+1 for i,v in enumerate(match)}
 rec.update(key=s['key'],name=s['name'],commonName=s['common'],formula=s['formula'],retrievalDate='2026-10-26',sha256=hashlib.sha256(raw).hexdigest(),atomMapping2Dto3D=mapping,mainChain3D=[mapping[str(i)] for i in range(1,s['parent']+1)],stereochemistry='Unspecified; illustrative conformer does not assign R/S')
 return raw,rec

def generate(output,cache):
 output.mkdir(parents=True,exist_ok=True)
 for s in SPECS:
  for form,m in forms(s).items():
   p=output/(s['key']+'_2D_'+form+'.mol');assert not p.exists(),p
   block=Chem.MolToMolBlock(m,includeStereo=False);p.write_text(p.stem+'\n'+block.split('\n',1)[1])
  raw,rec=three(s,cache);p=output/(s['key']+'_3D.sdf');assert not p.exists(),p;p.write_bytes(raw)
  (output/(s['key']+'_3D.provenance.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
  print(s['key'],s['formula'],rec['source'],rec.get('cid'),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--pubchem-cache',type=Path,required=True);a=p.parse_args();generate(a.output,a.pubchem_cache)
