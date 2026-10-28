"""Read-only preservation, catalog/lesson and generated-host contract checks."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

baseline = json.loads(Path('docs/checks/react-lesson-before-20261027.json').read_text())
allowed = {'react-preview/src/main.jsx', 'react-preview/src/preview.css',
           'react-preview/package.json', 'react-preview/README.md',
           'docs/SESSION-NOTES.md', 'docs/YANNIS-CONTRIBUTIONS.md'}
protected = {p: h for p, h in baseline['files'].items() if p not in allowed}
changed = [p for p, h in protected.items() if not Path(p).is_file()
           or hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]
assert not changed, changed
new_runtime = {'react-preview/src/LessonPreview.jsx', 'react-preview/public/lesson-host-bridge.js',
               'react-preview/tools/build-lesson-host.py', 'react-preview/public/lesson-host.html'}
paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).decode().split('\0')
assert all(not p or p in baseline['files'] or p in new_runtime or p.startswith('docs/') for p in paths), 'Unexpected new runtime file'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip() == baseline['head']
assert subprocess.check_output(['git', 'rev-parse', 'thesis-work']).decode().strip() == '3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab'
content = json.loads(Path('react-preview/src/content.json').read_text())
lessons = [s for c in content['library']['categories'] for s in c['lessons']]
assert len(lessons) == 12 and sum(s['steps'] for s in lessons) == 283
alkanes = next(s for s in lessons if s['id'] == 'alkanes')
assert alkanes['steps'] == 21
for lesson in lessons:
    data = json.loads(Path(lesson['scenario']).read_text())
    assert len(data['steps']) == lesson['steps']
assert len(json.loads(Path('react-preview/src/molecules.json').read_text())) == 126
# Build changes only the script; dependency versions/lockfile stay protected.
before = json.loads(subprocess.check_output(['git', 'show', baseline['head'] + ':react-preview/package.json']))
actual = json.loads(Path('react-preview/package.json').read_text())
assert before['dependencies'] == actual['dependencies'] and before['devDependencies'] == actual['devDependencies']
for script in ['react-preview/tools/build-lesson-host.py', 'docs/checks/test-react-lesson-browser-20261027.py',
               'docs/checks/test-react-lesson-lifecycle-20261027.py',
               'docs/checks/test-react-lesson-routes-20261027.py', __file__]:
    ast.parse(Path(script).read_text())
print(json.dumps({'passed': True, 'protectedFilesUnchanged': len(protected),
                  'outsideReactAndJournalsUnchanged': sum(not p.startswith('react-preview/') for p in protected),
                  'mainAndCoreChanged': False, 'lessonJSONChanged': False,
                  'molecules': 126, 'lessons': 12, 'steps': 283, 'pilotSteps': 21}, indent=2))
