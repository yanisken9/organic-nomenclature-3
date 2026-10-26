"""Approved ether formula/branch-layout refinement; no application writes."""
from pathlib import Path
exec(compile(Path('docs/checks/check-ethers-assets-20261026.py').read_text().split('base=json.loads')[0], 'ether-assets', 'exec'))
import subprocess
base=Path('/tmp/namelecule-before-ether-refinement-20261026');hashes=json.loads((base/'manifest.json').read_text())
keys=['ethyl_isopropyl_ether','ethyl_sec_butyl_ether','tert_butyl_isopropyl_ether']
expected={'ethyl_isopropyl_ether':2,'ethyl_sec_butyl_ether':3,'tert_butyl_isopropyl_ether':2}
for s in specs:
 if s['key'] not in keys:continue
 for mode in ['Condensed','Expanded']:
  m=Chem.MolFromMolFile('mols/new_molecules/'+s['key']+'_2D_'+mode+'.mol',removeHs=False);p=m.GetConformer().GetPositions();o=s['carbons']
  # The attachment carbon and the longest outward arm lie on the O axis.
  seen=set();todo=[0 if s['key']!='tert_butyl_isopropyl_ether' else 4]
  while todo:
   a=todo.pop()
   if a in seen or m.GetAtomWithIdx(a).GetSymbol()!='C':continue
   seen.add(a);todo.extend(n.GetIdx() for n in m.GetAtomWithIdx(a).GetNeighbors() if n.GetSymbol()=='C')
  count=sum(abs(p[i][1]-p[o][1])<.0001 for i in seen)
  assert count==expected[s['key']],(s['key'],mode,count)
allowed={'js/jsme-nick-nomeclature-moc2-data_51.js','mulermoc-nom-51.html','docs/checks/ethers-specs-20261026.json','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md','docs/ETHERS-20261026.md'}
changed=[];protected=0
for file,h in hashes.items():
 p=Path(file);assert p.is_file(),file
 if hashlib.sha256(p.read_bytes()).hexdigest()==h:protected+=1;continue
 if file in allowed:continue
 assert any(file=='mols/new_molecules/'+k+'_2D_'+mode+'.mol' for k in keys for mode in ['Condensed','Expanded']),('out of scope',file)
 old=(base/file).read_text().splitlines();new=p.read_text().splitlines();na=int(old[3][:3]);assert len(old)==len(new)
 assert old[:4]==new[:4] and old[4+na:]==new[4+na:]
 assert all(a[30:]==b[30:] for a,b in zip(old[4:4+na],new[4:4+na]))
 changed.append(file)
assert len(changed)==6
src=Path('js/jsme-nick-nomeclature-moc2-data_51.js').read_text();before=(base/'js/jsme-nick-nomeclature-moc2-data_51.js').read_text()
viewer=Path('js/mulermoc-nom-molview-51.js').read_text()
frameCode=viewer[viewer.index('let uniform2DLibraryFrame = null;'):viewer.index('function fFit2DSVG()')]
fetch=';'+frameCode+';return {metadata:nameExamples,mols:window.MOL2D,frame:fGetUniform2DLibraryFrame()};'
code='print(JSON.stringify([(new Function('+json.dumps('var window={};'+before+fetch)+'))(),(new Function('+json.dumps('var window={};'+src+fetch)+'))()]));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
a,b=json.loads(r.stdout);assert a['frame']==b['frame'],('uniform font reference frame changed',a['frame'],b['frame']);formulaKeys=keys[:2]
for k,v in a['metadata'].items():
 new=dict(b['metadata'][k]);old=dict(v)
 if k in formulaKeys:
  assert new.pop('formula')==next(s['displayFormula'] for s in specs if s['key']==k);old.pop('formula')
 assert old==new,('metadata',k)
 for mode,mol in a['mols'].get(k,{}).items():
  if k in keys and mode in ['condensed','expanded']:
   assert b['mols'][k][mode]==Path('mols/new_molecules',k+'_2D_'+mode.title()+'.mol').read_text()
  else:assert mol==b['mols'][k][mode],('other embedded MOL',k,mode)
out=dict(changedMOL=changed,protectedFilesUnchanged=protected,molecules=results,metadataOnlyTwoFormulaChanges=True,uniformFontFrameUnchanged=a['frame'],allChecksPassed=True)
Path('/tmp/ether-refinement-assets-20261026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('PASS 6 MOL coords only /2 formulas /105 metadata and embeds; protected',protected)
