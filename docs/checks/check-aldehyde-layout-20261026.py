"""Five aldehydes: chemical graphs, explicit H, 2D clearance, 3D, baseline protection."""
from pathlib import Path
import json,hashlib,math,io
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
specs=json.load(open('docs/checks/aldehydes-specs-20261026.json'));rows=[]
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def point_segment(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
for s in specs:
 key=s['key'];q=Chem.MolFromSmiles(s['smiles']);row=dict(key=key,formula=s['formula'],forms={})
 for form in ['Condensed','Expanded','Skeletal']:
  text=Path('mols/new_molecules',key+'_2D_'+form+'.mol').read_text();m=Chem.MolFromMolBlock(text,removeHs=False);assert m and len(Chem.GetMolFrags(m))==1
  assert rdMolDescriptors.CalcMolFormula(m)==s['formula']
  assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(q,isomericSmiles=False)
  assert sum(a.GetSymbol()=='H' for a in m.GetAtoms())==(2*s['carbons'] if form=='Expanded' else 0)
  assert sum(b.GetBondTypeAsDouble()==2 for b in m.GetBonds())==1
  assert all(b.GetStereo()==Chem.BondStereo.STEREONONE for b in m.GetBonds())
  pos=[tuple(p) for p in m.GetConformer().GetPositions()];xy=[p[:2] for p in pos];assert all(abs(p[2])<1e-6 for p in pos)
  pairs=[(b.GetBeginAtomIdx(),b.GetEndAtomIdx()) for b in m.GetBonds()];edges={frozenset(e) for e in pairs}
  nearest=min(math.dist(xy[i],xy[j]) for i in range(len(xy)) for j in range(i) if frozenset((i,j)) not in edges) if len(xy)>2 else None
  assert nearest is None or nearest>.55,(key,form,'nonbonded',nearest)
  for a,b in pairs:
   length=math.dist(xy[a],xy[b]);h='H' in [m.GetAtomWithIdx(i).GetSymbol() for i in [a,b]]
   assert abs(length-.78)<.00015 if h else .99<length<2.35,(key,form,a,b,length)
   for c,d in pairs:
    if {a,b}&{c,d}:continue
    assert not (cross(xy[a],xy[b],xy[c])*cross(xy[a],xy[b],xy[d]) < -1e-9 and cross(xy[c],xy[d],xy[a])*cross(xy[c],xy[d],xy[b]) < -1e-9),(key,form,'cross')
   for i in range(len(xy)):
    if i not in [a,b]:assert point_segment(xy[i],xy[a],xy[b])>.3,(key,form,'atom near bond',i)
  if form!='Skeletal':assert max(xy[i][1] for i in range(s['parent']))-min(xy[i][1] for i in range(s['parent']))<1e-5
  row['forms'][form]=dict(atoms=m.GetNumAtoms(),nearestNonbonded=nearest)
 raw=Path('mols/new_molecules',key+'_3D.sdf').read_bytes();assert raw==Path('mols/nomeclature-moc2',key+'_3D.sdf').read_bytes()
 prov=json.loads(Path('mols/new_molecules',key+'_3D.provenance.json').read_text());assert prov['sha256']==hashlib.sha256(raw).hexdigest()
 m=next(Chem.ForwardSDMolSupplier(io.BytesIO(raw),removeHs=False));assert m and m.GetConformer().Is3D()
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula'] and m.GetNumAtoms()==3*s['carbons']+1
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(q,isomericSmiles=False)
 if prov['source']=='PubChem':assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
 mapping=prov['atomMapping2Dto3D'];assert len(set(mapping.values()))==s['carbons']+1
 for a,b,order in s['edges']:assert m.GetBondBetweenAtoms(mapping[str(a)]-1,mapping[str(b)]-1).GetBondTypeAsDouble()==order
 pos=m.GetConformer().GetPositions()
 for b in m.GetBonds():
  a,c=b.GetBeginAtomIdx(),b.GetEndAtomIdx();length=math.dist(pos[a],pos[c]);h='H' in [m.GetAtomWithIdx(i).GetSymbol() for i in [a,c]]
  assert (.8<length<1.25 if h else 1.15<length<1.75),(key,'3D length',length)
 # Carbonyl carbon is trigonal planar in3D, including explicit aldehydic H.
 cidx=mapping['1']-1;center=pos[cidx];ns=[a.GetIdx() for a in m.GetAtomWithIdx(cidx).GetNeighbors()];assert len(ns)==3
 angles=[]
 for i,a in enumerate(ns):
  for b in ns[:i]:
   va=pos[a]-center;vb=pos[b]-center
   co=sum(x*y for x,y in zip(va,vb))/(math.sqrt(sum(x*x for x in va))*math.sqrt(sum(x*x for x in vb)))
   angle=math.degrees(math.acos(max(-1,min(1,co))));assert 108<angle<132,(key,'carbonyl angle',angle);angles.append(angle)
 assert abs(sum(angles)-360)<1,(key,'carbonyl planarity',angles)
 row.update(source=prov['source'],cid=prov.get('cid'),carbonylAngles=angles);rows.append(row)
base=json.loads(Path('/tmp/namelecule-before-aldehyde-layout-20261026/manifest.json').read_text())
allowed={'docs/checks/aldehydes-specs-20261026.json','docs/checks/generate-aldehydes-20261026.py','js/mulermoc-nom-molview-51.js','js/jsme-nick-nomeclature-moc2-data_51.js','mulermoc-nom-51.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
for spec in specs:
 allowed.add('mols/new_molecules/'+spec['key']+'_2D_Condensed.mol')
allowed.add('mols/new_molecules/methanal_2D_Expanded.mol')
protected=0
for path,h in base.items():
 if path in allowed:continue
 assert Path(path).is_file() and hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
 protected+=1
# Unchanged atom/bond records; only approved coordinate transformation.
for spec in specs:
 for form in ['Condensed','Expanded','Skeletal']:
  p=Path('mols/new_molecules',spec['key']+'_2D_'+form+'.mol');old=Path('/tmp/namelecule-before-aldehyde-layout-20261026')/p
  a=Chem.MolFromMolFile(str(p),removeHs=False);b=Chem.MolFromMolFile(str(old),removeHs=False)
  assert a and b and Chem.MolToSmiles(a)==Chem.MolToSmiles(b)
  if spec['key']!='methanal' and form=='Condensed':
   for i in range(a.GetNumAtoms()):
    x=a.GetConformer().GetAtomPosition(i);y=b.GetConformer().GetAtomPosition(i)
    expected=y.y*.75 if i<spec['carbons'] and i>=spec['parent'] else y.y
    assert abs(x.x-y.x)<1e-5 and abs(x.y-expected)<.00015,(spec['key'],i,x,y)
  if spec['key']=='methanal' and form=='Expanded':
   c=a.GetConformer();assert abs(c.GetAtomPosition(0).y-c.GetAtomPosition(1).y)<1e-5
   assert c.GetAtomPosition(1).x>c.GetAtomPosition(0).x
   hs=[c.GetAtomPosition(t.GetIdx()) for t in a.GetAtoms() if t.GetSymbol()=='H']
   assert any(h.x<0 and abs(h.y)<1e-5 for h in hs) and any(h.y>0 and abs(h.x)<1e-5 for h in hs)
out=dict(molecules=rows,protectedFilesUnchanged=protected,allChecksPassed=True)
Path('docs/checks/aldehyde-layout-assets-20261026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS graphs/H/valence/coordinates25percent/horizontalmethanal/3D/provenance;',protected,'protected files unchanged')
