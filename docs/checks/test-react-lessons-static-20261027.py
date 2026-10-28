"""Read-only preservation and generated registry audit for the12-lesson expansion."""
import ast, hashlib, json, subprocess
from pathlib import Path
baseline=json.loads(Path('docs/checks/react-lessons-before-20261027.json').read_text())
allowed={'react-preview/src/main.jsx','react-preview/src/LessonPreview.jsx',
         'react-preview/public/lesson-host-bridge.js','react-preview/tools/build-lesson-host.py',
         'react-preview/public/lesson-host.html','react-preview/README.md',
         'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected={p:h for p,h in baseline['files'].items() if p not in allowed}
changed=[p for p,h in protected.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert not changed,changed
paths=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard']).decode().split('\0')
assert all(not p or p in baseline['files'] or p.startswith('docs/') for p in paths),'Unexpected new runtime path'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline['head']
assert subprocess.check_output(['git','rev-parse','thesis-work']).decode().strip()=='3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab'
catalog=json.loads(Path('react-preview/src/content.json').read_text())
entries=[s for c in catalog['library']['categories'] for s in c['lessons']]
assert len(entries)==12 and sum(s['steps'] for s in entries)==283
html=Path('react-preview/public/lesson-host.html').read_text()
registry=json.loads(html.split('const lessons = ',1)[1].split(';\n  const channel',1)[0])
assert set(registry)=={s['id'] for s in entries}
for entry in entries:
    obj=json.loads(Path(entry['scenario']).read_text())
    assert registry[entry['id']]=={'id':entry['id'],'scenario':entry['scenario'],'total':entry['steps'],'titles':[s['title'] for s in obj['steps']]}
assert len(json.loads(Path('react-preview/src/molecules.json').read_text()))==126
for script in ['react-preview/tools/build-lesson-host.py','docs/checks/test-react-lessons-browser-20261027.py',
               'docs/checks/test-react-lessons-lifecycle-20261027.py',__file__]:ast.parse(Path(script).read_text())
print(json.dumps({'passed':True,'protectedFilesUnchanged':len(protected),
 'outsideReactAndJournalsUnchanged':sum(not p.startswith('react-preview/') for p in protected),
 'mainAndCoreChanged':False,'scenarioJSONChanged':False,'catalogChanged':False,
 'molecules':126,'lessons':12,'steps':283,'registryMatchesSources':True},indent=2))
