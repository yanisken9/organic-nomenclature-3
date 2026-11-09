"""Read-only task-start preservation and existing-catalog checks."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

baseline = json.loads(Path('docs/checks/react-rules-before-20261027.json').read_text())
allowed = {'react-preview/src/NameAnalysis.jsx', 'react-preview/src/MoleculePreview.jsx',
           'react-preview/src/preview.css', 'react-preview/public/viewer-host-bridge.js',
           'react-preview/tools/build-viewer-host.py', 'react-preview/README.md', 'docs/SESSION-NOTES.md', 'docs/YANNIS-CONTRIBUTIONS.md'}
protected = {p: h for p, h in baseline['files'].items() if p not in allowed}
changed = [p for p, h in protected.items() if not Path(p).is_file()
           or hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]
assert not changed, changed
paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).decode().split('\0')
new_runtime = {'react-preview/src/RulePanels.jsx', 'react-preview/src/rule-data.js', 'react-preview/src/rule-schema.json'}
assert all(not p or p in baseline['files'] or p in new_runtime or p.startswith('docs/') for p in paths), 'Unexpected new runtime file'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip() == baseline['head']
assert subprocess.check_output(['git', 'rev-parse', 'thesis-work']).decode().strip() == '3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab'
catalog = json.loads(Path('react-preview/src/molecules.json').read_text())
assert len(catalog) == 126 and len({m['id'] for m in catalog}) == 126
assert sum(m['series'] == 'ether' for m in catalog) == 11
for name in ['test-react-rules-browser-20261027.py', 'test-react-rules-static-20261027.py']:
    ast.parse(Path('docs/checks', name).read_text())
print(json.dumps({'passed': True, 'protectedFilesUnchanged': len(protected),
                  'outsideReactAndJournalsUnchanged': sum(not p.startswith('react-preview/') for p in protected),
                  'mainAndCoreChanged': False, 'catalogUnchanged': True,
                  'molecules': 126, 'ethers': 11}, indent=2))
