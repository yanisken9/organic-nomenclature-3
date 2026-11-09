"""Read-only source/data preservation checks for the approved 3D controls scope."""
import ast, hashlib, json, subprocess
from pathlib import Path
baseline=json.loads(Path('docs/checks/react-3d-controls-before-20261027.json').read_text())
allowed={'react-preview/src/MoleculePreview.jsx','react-preview/public/viewer-host-bridge.js',
 'react-preview/src/preview.css','react-preview/public/viewer-host.html','react-preview/README.md',
 'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected={p:h for p,h in baseline['files'].items() if p not in allowed and not p.startswith('react-preview/dist/')}
changed=[p for p,h in protected.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert not changed,changed
paths=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard']).decode().split('\0')
assert all(not p or p in baseline['files'] or p.startswith('docs/') for p in paths),'Unexpected new runtime path'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline['head']
assert subprocess.check_output(['git','rev-parse','thesis-work']).decode().strip()=='3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab'
assert len(json.loads(Path('react-preview/src/molecules.json').read_text()))==126
entries=[s for c in json.loads(Path('react-preview/src/content.json').read_text())['library']['categories'] for s in c['lessons']]
assert len(entries)==12 and sum(s['steps'] for s in entries)==283
for p in [__file__,'docs/checks/test-react-3d-controls-browser-20261027.py']:ast.parse(Path(p).read_text())
print(json.dumps({'passed':True,'protectedFilesUnchanged':len(protected),
 'outsideReactAndJournalsUnchanged':sum(not p.startswith('react-preview/') for p in protected),
 'coreChanged':False,'mainChanged':False,'moleculeFilesChanged':False,'scenarioJSONChanged':False,
 'lessonHostChanged':False,'dependenciesChanged':False,'molecules':126,'lessons':12,'steps':283},indent=2))
