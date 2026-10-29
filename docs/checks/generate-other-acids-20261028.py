"""Four approved unsaturated mono-/diacids, existing V2000/MOL2D/SDF conventions.
Uses established local RDKit ETKDGv3/MMFF94s provenance/mapping implementation.
No external structure lookup: automatic approval blocked transmitting SMILES.
"""
from pathlib import Path
import argparse,json,math,runpy,hashlib,io
from rdkit import Chem
from rdkit.Geometry import Point2D
from rdkit.Chem import rdDepictor,AllChem,rdMolTransforms
existing=runpy.run_path('docs/checks/generate-acids-20261028.py')
graph=existing['graph'];three=existing['three']
SPECS=json.loads(Path('docs/checks/other-acids-specs-20261028.json').read_text())
def block(m,key):
 text=Chem.MolToMolBlock(m,includeStereo=False);lines=text.splitlines();n=int(lines[3][:3]);nb=int(lines[3][3:6])
 # Existing MOL-only school convention. No stereochemical descriptor is claimed.
 for i in range(4+n,4+n+nb):lines[i]=lines[i][:9]+'  0'+lines[i][12:]
 return key+'\n'+'\n'.join(lines[1:])+'\n'
def forms(s):
 m=graph(s);conf=Chem.Conformer(m.GetNumAtoms());conf.Set3D(False)
 for i,(x,y) in enumerate(s['xy']):conf.SetAtomPosition(i,(-1.17*x,1.17*y,0))
 m.AddConformer(conf);expanded=Chem.AddHs(m);c=expanded.GetConformer();c.Set3D(False)
 for atom in expanded.GetAtoms():
  if atom.GetSymbol()=='H':continue
  i=atom.GetIdx();p=c.GetAtomPosition(i);occupied=set()
  for nb in atom.GetNeighbors():
   if nb.GetSymbol()=='H':continue
   q=c.GetAtomPosition(nb.GetIdx());occupied.add((int(q.x>p.x)-int(q.x<p.x),int(q.y>p.y)-int(q.y<p.y)))
  ds=[(0,-1),(0,1),(-1,0),(1,0)]
  if atom.GetSymbol()=='O':
   other=next(n for n in atom.GetNeighbors() if n.GetSymbol()!='H');q=c.GetAtomPosition(other.GetIdx());ds=[(1 if p.x>q.x else -1,0)]
  if any(b.GetBondTypeAsDouble()==3 for b in atom.GetBonds()):
   other=next(n for n in atom.GetNeighbors() if n.GetSymbol()!='H');q=c.GetAtomPosition(other.GetIdx());ds=[(int(p.x>q.x)-int(p.x<q.x),int(p.y>q.y)-int(p.y<q.y))]
  free=[d for d in ds if d not in occupied];hs=[n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol()=='H'];assert len(hs)<=len(free)
  for h,(dx,dy) in zip(hs,free):c.SetAtomPosition(h,(p.x+.78*dx,p.y+.78*dy,0))
 compact=Chem.Mol(m);c=compact.GetConformer()
 # Shift each alkyl subtree rigidly: single vertical level, two for isopropyl.
 xy=[list(p) for p in s['xy']];seen=set(range(s['parent']))
 for attach in range(s['parent']):
  for n in m.GetAtomWithIdx(attach).GetNeighbors():
   start=n.GetIdx()
   if start in seen or n.GetSymbol()!='C':continue
   todo=[start];sub=[];seen.add(start)
   while todo:
    a=todo.pop();sub.append(a)
    for nb in m.GetAtomWithIdx(a).GetNeighbors():
     b=nb.GetIdx()
     if b not in seen and nb.GetSymbol()=='C':seen.add(b);todo.append(b)
   iso=len(sub)==3 and len([n for n in m.GetAtomWithIdx(start).GetNeighbors() if n.GetSymbol()=='C'])==3
   target=(2 if iso else 1)*(1 if xy[start][1]>0 else -1)
   delta=target-xy[start][1]
   for a in sub:xy[a][1]+=delta
 for i,(x,y) in enumerate(xy):c.SetAtomPosition(i,(-1.404*x,1.17*y,0))
 for carbon,oxygen,hydroxy in s['acidGroups']:
  a=carbon-1;p=c.GetAtomPosition(a);sign=1 if carbon==1 else -1
  c.SetAtomPosition(oxygen-1,(p.x+sign*.702,p.y+1.2159,0));c.SetAtomPosition(hydroxy-1,(p.x+sign*1.404,p.y,0))
  group=Chem.CreateMolSubstanceGroup(compact,'SUP');group.SetAtoms([a,oxygen-1,hydroxy-1]);group.SetProp('LABEL','COOH')
  group.SetBonds([m.GetBondBetweenAtoms(a,1 if carbon==1 else a-1).GetIdx()])
 sk=Chem.Mol(m);points=[(0.,0.)];angle=-math.pi/6
 for i in range(1,s['parent']):
  if i>1 and not any(b.GetBondTypeAsDouble()==3 for b in sk.GetAtomWithIdx(i-1).GetBonds()):angle=-angle
  x,y=points[-1];points.append((x-1.17*math.cos(angle),y+1.17*math.sin(angle)))
 rdDepictor.Compute2DCoords(sk,bondLength=1.17,coordMap={i:Point2D(x,y) for i,(x,y) in enumerate(points)},canonOrient=False)
 c=sk.GetConformer();ps=[c.GetAtomPosition(i) for i in range(s['parent'])];cx=sum(p.x for p in ps)/len(ps);cy=sum(p.y for p in ps)/len(ps)
 xx=sum((p.x-cx)**2 for p in ps);yy=sum((p.y-cy)**2 for p in ps);xycov=sum((p.x-cx)*(p.y-cy)for p in ps)
 angle=-.5*math.atan2(2*xycov,xx-yy);co,si=math.cos(angle),math.sin(angle)
 coords=[(p[0]*co-p[1]*si,p[0]*si+p[1]*co) for p in c.GetPositions()]
 if coords[0][0]<coords[s['parent']-1][0]:coords=[(-x,-y)for x,y in coords]
 cx=(max(x for x,y in coords)+min(x for x,y in coords))/2;cy=(max(y for x,y in coords)+min(y for x,y in coords))/2
 for i,(x,y) in enumerate(coords):c.SetAtomPosition(i,(x-cx,y-cy,0))
 return dict(Condensed=compact,Expanded=expanded,Skeletal=sk)
def qualified_three(s,cache):
 raw,prov=three(s,cache)
 def sp_angles(m,cid=0):
  out=[]
  for a in m.GetAtoms():
   if any(b.GetBondTypeAsDouble()==3 for b in a.GetBonds()):
    ns=[n.GetIdx()for n in a.GetNeighbors()];out.append(rdMolTransforms.GetAngleDeg(m.GetConformer(cid),ns[0],a.GetIdx(),ns[1]))
  return out
 initial=next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False))
 if not sp_angles(initial) or min(sp_angles(initial))>175:return raw,prov
 # Keep the same sampled ensemble/method; reject strained sp geometries for display.
 m=Chem.AddHs(graph(s));params=AllChem.ETKDGv3();params.randomSeed=20261028;params.numThreads=1
 AllChem.EmbedMultipleConfs(m,numConfs=24,params=params)
 scores=AllChem.MMFFOptimizeMoleculeConfs(m,numThreads=1,mmffVariant='MMFF94s',maxIters=1000)
 eligible=[(energy,i)for i,(status,energy)in enumerate(scores)if status==0 and min(sp_angles(m,i))>175];assert eligible
 energy,i=min(eligible);angles=sp_angles(m,i);conf=Chem.Conformer(m.GetConformer(i));m.RemoveAllConformers();m.AddConformer(conf,assignId=True);Chem.RemoveStereochemistry(m)
 raw=(Chem.MolToMolBlock(m,includeStereo=False)+'\n$$$$\n').encode()
 prov.update(method='ETKDGv3 / MMFF94s, lowest converged among the 24 sampled conformers satisfying the sp-angle display criterion',energyKcalMol=energy,sha256=hashlib.sha256(raw).hexdigest(),selectedConformer=i,eligibleConformers=len(eligible),geometryCriterion='Both sp angles >175 degrees',spAngles=angles)
 return raw,prov
def generate(output,cache):
 output.mkdir(parents=True,exist_ok=True)
 for s in SPECS:
  for form,m in forms(s).items():
   p=output/(s['key']+'_2D_'+form+'.mol');assert not p.exists();p.write_text(block(m,p.stem))
  raw,prov=qualified_three(s,cache);p=output/(s['key']+'_3D.sdf');assert not p.exists();p.write_bytes(raw)
  (output/(s['key']+'_3D.provenance.json')).write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
  print('GENERATED',s['key'],s['formula'],prov['source'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);a=p.parse_args();generate(a.output,a.cache)
