"""Read-only preservation checks for Main-only 2D scale; creates no artifacts."""
from pathlib import Path
import ast,hashlib,json,subprocess
base=json.loads(Path('docs/checks/main-2d-scale-before-20261027.json').read_text())
allowed={'mulermoc-nom-52.html','js/mulermoc-nom-molview-52.js','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
protected={p:h for p,h in base['files'].items() if p not in allowed}
changed=[p for p,h in protected.items() if not Path(p).is_file() or sha(p)!=h]
assert not changed,changed
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==base['head']
assert subprocess.check_output(['git','rev-parse','thesis-work'],text=True).strip()==base['stable']
for p in ['mulermoc-nom-52.html','js/mulermoc-nom-molview-52.js']:
 assert sha(Path(base['beforeSnapshots'])/p)==base['files'][p]
assert 'data-namelecule-2d-scale="1.15"' in Path('mulermoc-nom-52.html').read_text()
for p in ['react-preview/public/viewer-host.html','react-preview/public/lesson-host.html','react-preview/dist/viewer-host.html','react-preview/dist/lesson-host.html']:
 assert 'data-namelecule-2d-scale' not in Path(p).read_text()
for p in ['docs/checks/test-main-2d-scale-browser-20261027.py',__file__]:ast.parse(Path(p).read_text())
paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0')
newpaths={p for p in paths if p and not any(x in Path(p).parts for x in ['.git','.codex','.agents','.aws','node_modules','checkpoints','__pycache__'])}-set(base['files'])
assert all(p.startswith('docs/checks/main-2d-scale-') or p.startswith('docs/checks/test-main-2d-scale-') or p=='docs/MAIN-2D-SCALE-20261027.md' for p in newpaths),newpaths
print(json.dumps({'passed':True,'protectedFilesUnchanged':len(protected),'reactFilesUnchanged':sum(p.startswith('react-preview/') for p in protected),'coreFilesUnchanged':sum('/mulermoc-nom-core-' in p for p in protected),'core52SHA256':sha('js/mulermoc-nom-core-52.js'),'runtimeChanged':['mulermoc-nom-52.html','js/mulermoc-nom-molview-52.js'],'head':base['head'],'stable':base['stable'],'moleculeScenarioFilesUnchanged':True},indent=2))
