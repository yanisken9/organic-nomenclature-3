"""Read-only preservation audit of the approved React PNG3D scope."""
from pathlib import Path
import ast,hashlib,json,subprocess
base=json.loads(Path('docs/checks/react-3d-png-before-20261027.json').read_text())
allowed={'react-preview/src/MoleculePreview.jsx','react-preview/public/viewer-host-bridge.js','react-preview/public/viewer-host.html','react-preview/README.md','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected={p:h for p,h in base['files'].items() if p not in allowed and not p.startswith('react-preview/dist/')}
bad=[p for p,h in protected.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert not bad,bad
paths=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard']).decode().split('\0')
assert all(not p or p in base['files'] or p.startswith('docs/') for p in paths),'Unexpected new runtime file'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==base['head']
assert subprocess.check_output(['git','rev-parse','thesis-work']).decode().strip()=='3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab'
for p in [__file__,'docs/checks/test-react-3d-png-browser-20261027.py','docs/checks/test-react-3d-png-lifecycle-20261027.py']:ast.parse(Path(p).read_text())
catalog=json.loads(Path('react-preview/src/content.json').read_text());lessons=[s for c in catalog['library']['categories'] for s in c['lessons']]
assert len(lessons)==12 and sum(s['steps'] for s in lessons)==283
assert len(json.loads(Path('react-preview/src/molecules.json').read_text()))==126
print(json.dumps({'passed':True,'protectedFilesUnchanged':len(protected),'outsideReactAndJournalsUnchanged':sum(not p.startswith('react-preview/') for p in protected),'mainChanged':False,'coreChanged':False,'MOLSDFChanged':False,'lessonRuntimeDataChanged':False,'CSSChanged':False,'dependenciesChanged':False,'molecules':126,'lessons':12,'steps':283},indent=2))
