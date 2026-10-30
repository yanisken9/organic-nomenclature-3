import sys
"""Two unbranched enynoic acids: chemical graphs, explicit H, 2D clearance, 3D, baseline protection."""
from pathlib import Path
import json,hashlib,math,io,gzip,base64
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,rdMolTransforms
old_sources={p:base64.b64decode(v).decode() for p,v in json.loads(gzip.decompress(Path('docs/checks/two-enynoic-acids-before-source-20261028.json.gz').read_bytes())).items()}
specs=json.load(open('docs/checks/two-enynoic-acids-specs-20261028.json'));rows=[]
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
  assert sum(a.GetSymbol()=='H' for a in m.GetAtoms())==(int(''.join(c for c in s['formula'].split('H')[1].split('O')[0] if c.isdigit())) if form=='Expanded' else 0)
  assert sum(b.GetBondTypeAsDouble()==2 for b in m.GetBonds())==sum(e[2]==2 for e in s['edges'])
  ls=text.splitlines();na=int(ls[3][:3]);nb=int(ls[3][3:6]);assert all(int(line[9:12] or '0')==0 for line in ls[4+na:4+na+nb]) # Existing MOL-only school display convention; no encoded stereo flags.
  pos=[tuple(p) for p in m.GetConformer().GetPositions()];xy=[p[:2] for p in pos];assert all(abs(p[2])<1e-6 for p in pos)
  pairs=[(b.GetBeginAtomIdx(),b.GetEndAtomIdx()) for b in m.GetBonds()];edges={frozenset(e) for e in pairs}
  nearest=min(math.dist(xy[i],xy[j]) for i in range(len(xy)) for j in range(i) if frozenset((i,j)) not in edges) if len(xy)>2 else None
  assert nearest is None or nearest>.55,(key,form,'nonbonded',nearest)
  for a,b in pairs:
   length=math.dist(xy[a],xy[b]);h='H' in [m.GetAtomWithIdx(i).GetSymbol() for i in [a,b]]
   assert abs(length-.78)<.00015 if h else .99<length<4.1,(key,form,a,b,length)
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
 assert rdMolDescriptors.CalcMolFormula(m)==s['formula'] and m.GetNumAtoms()==s['carbons']+len(s['xy'])-s['carbons']+int(s['formula'].split('H')[1].split('O')[0])
 assert Chem.MolToSmiles(Chem.RemoveHs(m),isomericSmiles=False)==Chem.MolToSmiles(q,isomericSmiles=False)
 if prov['source']=='PubChem':assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT')=='0'
 mapping=prov['atomMapping2Dto3D'];assert len(set(mapping.values()))==len(s['xy'])
 for a,b,order in s['edges']:assert m.GetBondBetweenAtoms(mapping[str(a)]-1,mapping[str(b)]-1).GetBondTypeAsDouble()==order
 pos=m.GetConformer().GetPositions()
 for b in m.GetBonds():
  a,c=b.GetBeginAtomIdx(),b.GetEndAtomIdx();length=math.dist(pos[a],pos[c]);h='H' in [m.GetAtomWithIdx(i).GetSymbol() for i in [a,c]]
  assert (.8<length<1.25 if h else 1.1<length<1.75),(key,'3D length',length)
 # Check sp linearity independently in the actual3D conformer.
 for atom in m.GetAtoms():
  if any(b.GetBondTypeAsDouble()==3 for b in atom.GetBonds()):
   ns3=[n.GetIdx() for n in atom.GetNeighbors()];assert len(ns3)==2
   assert rdMolTransforms.GetAngleDeg(m.GetConformer(),ns3[0],atom.GetIdx(),ns3[1])>175,(key,'3D sp angle')
 # Each COOH carbon is trigonal planar, independently of unspecified stereo.
 angles=[]
 for carbon,_,_ in s['acidGroups']:
  cidx=mapping[str(carbon)]-1;ns=[a.GetIdx() for a in m.GetAtomWithIdx(cidx).GetNeighbors()];assert len(ns)==3
  group=[rdMolTransforms.GetAngleDeg(m.GetConformer(),a,cidx,b) for i,a in enumerate(ns) for b in ns[:i]]
  assert all(108<x<132 for x in group),(key,'carbonyl angles',group)
  assert abs(sum(group)-360)<1,(key,'carbonyl planarity',group)
  angles.append(group)
 row.update(source=prov['source'],carbonylAngles=angles);rows.append(row)
base=json.loads(Path('docs/checks/two-enynoic-acids-before-20261028.json').read_text())['files']
allowed={'js/mulermoc-nom-molview-52.js','js/jsme-nick-nomeclature-moc2-data_52.js','mulermoc-nom-52.html','README.md','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for path,h in base.items():
 if path in allowed or path.startswith('docs/checks/two-enynoic-acids-') or path in ['docs/TWO-ENYNOIC-ACIDS-20261028.md','docs/checks/check-two-enynoic-acids-20261028.py']:continue
 assert Path(path).is_file() and hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
 protected+=1
# Semantic protection of every old data record/embedded MOL, plus new embeddings.
import subprocess
basepath=Path('/tmp/namelecule-acids-20261028/before')
datafile=Path('js/jsme-nick-nomeclature-moc2-data_52.js')
extract=lambda txt:'var window={};'+txt+';return {examples:nameExamples,mols:window.MOL2D};'
js='var old=(new Function('+json.dumps(extract(old_sources[str(datafile)]))+'))(),cur=(new Function('+json.dumps(extract(datafile.read_text()))+'))();var oldKeys=Object.keys(old.examples),curKeys=Object.keys(cur.examples);if(JSON.stringify(oldKeys)!==JSON.stringify(curKeys.slice(0,oldKeys.length)))throw Error("Old record order changed");var n=0;for(var key of oldKeys){if(JSON.stringify(old.examples[key])!==JSON.stringify(cur.examples[key])||JSON.stringify(old.mols[key])!==JSON.stringify(cur.mols[key]))throw Error(key);n++;}print(JSON.stringify({oldRecordsUnchanged:n,newCount:Object.keys(cur.examples).length,mols:cur.mols}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True)
obj=json.loads(r.stdout);assert obj['oldRecordsUnchanged']==134 and obj['newCount']==136
# Duplicate guard: compare approved new graphs with all old acid entries.
new_keys={s['key'] for s in specs}
old_acids={k:Chem.MolFromMolBlock(forms['condensed'],removeHs=True)
 for k,forms in obj['mols'].items() if k not in new_keys and 'acid' in k.lower()}
assert len(old_acids)==19 and all(m is not None for m in old_acids.values())
old_graphs={Chem.MolToSmiles(m,isomericSmiles=False) for m in old_acids.values()}
new_graphs=[Chem.MolToSmiles(Chem.MolFromSmiles(s['smiles']),isomericSmiles=False) for s in specs]
assert len(set(new_graphs))==2 and not old_graphs.intersection(new_graphs)
for spec in specs:
 for form in ['Condensed','Expanded','Skeletal']:
  assert obj['mols'][spec['key']][form.lower()]==Path('mols/new_molecules',spec['key']+'_2D_'+form+'.mol').read_text()
out=dict(oldRecordsUnchanged=134,newCount=136,molecules=rows,protectedFilesUnchanged=protected,allChecksPassed=True)
if '--read-only' not in sys.argv:Path('docs/checks/two-enynoic-acids-assets-20261028.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS 6 forms/graphs/H/geometry/3D/provenance;',protected,'protected files unchanged')
