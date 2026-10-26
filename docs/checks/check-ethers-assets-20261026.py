"""Chemistry, 2D geometry, 3D correspondence, byte preservation. RDKit required."""
from pathlib import Path
import json,hashlib,math,io
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
specs=json.loads(Path('docs/checks/ethers-specs-20261026.json').read_text());results=[]
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def point_segment(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
for s in specs:
 key=s['key'];q=Chem.MolFromSmiles(s['smiles']);row=dict(key=key,formula=s['formula'],forms={})
 for mode in ['Condensed','Expanded','Skeletal']:
  p=Path('mols/new_molecules',key+'_2D_'+mode+'.mol');text=p.read_text();m=Chem.MolFromMolBlock(text,removeHs=False);assert m and len(Chem.GetMolFrags(m))==1
  assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
  assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(q,isomericSmiles=False)
  assert sum(a.GetSymbol()=='H' for a in m.GetAtoms())==(2*s['carbons']+2 if mode=='Expanded' else 0)
  assert all(b.GetBondTypeAsDouble()==1 for b in m.GetBonds())
  coords=[tuple(p) for p in m.GetConformer().GetPositions()];assert all(abs(p[2])<1e-6 for p in coords)
  xy=[p[:2] for p in coords];pairs=[(b.GetBeginAtomIdx(),b.GetEndAtomIdx()) for b in m.GetBonds()];edge={frozenset(e) for e in pairs}
  nearest=min(math.dist(xy[i],xy[j]) for i in range(len(xy)) for j in range(i) if frozenset((i,j)) not in edge)
  assert nearest>.55,(key,mode,nearest)
  for a,b in pairs:
   length=math.dist(xy[a],xy[b]);h='H' in [m.GetAtomWithIdx(i).GetSymbol() for i in [a,b]]
   assert abs(length-(.78 if h else 1.17))<.00015,(key,mode,a,b,length)
   for c,d in pairs:
    if {a,b}&{c,d}:continue
    assert not (cross(xy[a],xy[b],xy[c])*cross(xy[a],xy[b],xy[d]) < -1e-9 and cross(xy[c],xy[d],xy[a])*cross(xy[c],xy[d],xy[b]) < -1e-9),(key,mode,'cross')
   for i in range(len(xy)):
    if i not in [a,b]:assert point_segment(xy[i],xy[a],xy[b])>.3,(key,mode,'atom on bond',i)
  o=s['carbons']; neighbors=[n.GetIdx() for n in m.GetAtomWithIdx(o).GetNeighbors()]
  a,b=neighbors;assert abs(xy[a][1]-xy[b][1])<.00015,(key,mode,'C-O-C axis')
  assert min(xy[a][0],xy[b][0])<xy[o][0]<max(xy[a][0],xy[b][0]),(key,mode,'opposite sides of O')
  if mode!='Skeletal':assert abs(xy[a][1]-xy[o][1])<.00015,(key,mode,'horizontal C-O-C')
  row['forms'][mode]=dict(atoms=m.GetNumAtoms(),nearestNonbonded=nearest)
 raw=Path('mols/new_molecules',key+'_3D.sdf').read_bytes();assert raw==Path('mols/nomeclature-moc2',key+'_3D.sdf').read_bytes()
 prov=json.loads(Path('mols/new_molecules',key+'_3D.provenance.json').read_text());assert prov['sha256']==hashlib.sha256(raw).hexdigest()
 m=next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False));assert m and m.GetConformer().Is3D()
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula'] and m.GetNumAtoms()==3*s['carbons']+3
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(q,isomericSmiles=False)
 assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0' and m.GetProp('PUBCHEM_BOND_DEF_STEREO_COUNT')=='0'
 mapping=prov['atomMapping2Dto3D'];assert len(set(mapping.values()))==s['carbons']+1
 for a,b in s['edges']:assert m.GetBondBetweenAtoms(mapping[str(a)]-1,mapping[str(b)]-1).GetBondTypeAsDouble()==1
 pos=m.GetConformer().GetPositions()
 for b in m.GetBonds():
  a,c=b.GetBeginAtomIdx(),b.GetEndAtomIdx();length=math.dist(pos[a],pos[c]);h='H' in [m.GetAtomWithIdx(i).GetSymbol() for i in [a,c]]
  assert (.8<length<1.25 if h else 1.2<length<1.7),(key,'3D length',length)
 row.update(source=prov['source'],cid=prov['cid']);results.append(row)
base=json.loads(Path('/tmp/namelecule-before-ethers-20261026/manifest.json').read_text());allowed={'js/mulermoc-nom-core-51.js','js/mulermoc-nom-molview-51.js','js/jsme-nick-nomeclature-moc2-data_51.js','mulermoc-nom-51.html','README.md','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for p,sha in base.items():
 if p in allowed:continue
 assert Path(p).is_file() and hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,('existing file changed',p)
 protected+=1
out=dict(molecules=results,protectedFilesUnchanged=protected,allChecksPassed=True)
Path('/tmp/ethers-assets-20261026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('PASS 7 molecules /21 MOL /7 PubChem SDF+runtime copies+mapping;',protected,'existing files unchanged')
