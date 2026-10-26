"""Current horizontal-layout checks, reusing the established chemical validation."""
from pathlib import Path
exec(compile(Path('docs/checks/check-ethers-assets-20261026.py').read_text().split('base=json.loads')[0], 'ether-asset-validation', 'exec'))
base=json.loads(Path('/tmp/namelecule-before-2d-layout-20261026/manifest.json').read_text())
allowed={'js/mulermoc-nom-molview-51.js','js/jsme-nick-nomeclature-moc2-data_51.js','mulermoc-nom-51.html','docs/checks/ethers-specs-20261026.json','docs/checks/generate-ethers-20261026.py','docs/checks/check-ethers-assets-20261026.py','README.md','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md','docs/ETHERS-20261026.md'}
protected=0;changed=[]
for p,sha in base.items():
 current=Path(p);assert current.is_file(),p
 if hashlib.sha256(current.read_bytes()).hexdigest()==sha:protected+=1;continue
 if p in allowed:continue
 assert p.startswith('mols/new_molecules/') and '_2D_' in p and any(s['key']+'_2D_' in p for s in specs),('out of scope',p)
 old=Chem.MolFromMolFile(str(Path('/tmp/namelecule-before-2d-layout-20261026')/p),removeHs=False);new=Chem.MolFromMolFile(p,removeHs=False)
 assert [a.GetSymbol() for a in old.GetAtoms()]==[a.GetSymbol() for a in new.GetAtoms()]
 assert [(b.GetBeginAtomIdx(),b.GetEndAtomIdx(),b.GetBondTypeAsDouble()) for b in old.GetBonds()]==[(b.GetBeginAtomIdx(),b.GetEndAtomIdx(),b.GetBondTypeAsDouble()) for b in new.GetBonds()]
 changed.append(p)
out=dict(molecules=results,protectedFilesUnchanged=protected,changedMOL=changed,allChecksPassed=True)
Path('/tmp/horizontal-2d-assets-20261026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('PASS',len(changed),'MOL changed, all atoms/bonds preserved;',protected,'existing files unchanged incl core/3D/scenarios')
