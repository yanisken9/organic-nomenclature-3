"""Bounded Developer controller lifecycle checks; never edits production sources."""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
PATHS=['js/namelecule-quiz-checkpoints.js','js/namelecule-game-repair.js']
hashes={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in PATHS}
old_double=ROOT/'docs/checks/workshop-lesson-parity-20261110/unit/fake-dom.js'
source='const global=globalThis;global.window=global;\n'+(ROOT/'js/namelecule-game-repair.js').read_text()+'\n'+old_double.read_text()
source+='\nconst controllerSource='+json.dumps((ROOT/PATHS[0]).read_text())+';\n'+(HERE/'cases.js').read_text()
harness=HERE/'controller-harness.js'
harness.write_text(source)
run=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',str(harness.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
if run.returncode or 'FAIL ' in run.stdout:
    (HERE/'failure.txt').write_text(run.stdout+run.stderr)
    raise SystemExit(run.stdout+run.stderr)
report=json.loads(run.stdout.strip().splitlines()[-1])
report['sourceHashes']=hashes
report['fixtureHashes']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [old_double,HERE/'cases.js',HERE/'run.py',harness]}
report['role']='Developer supplied checks; not independent review'
report['runnerHistory']='Reused prior194 lifecycle checks in a new directory, adapting optional Return clicks to synthetic cancel/Escape because the button is now hidden; added targeted visible-action/reused-dialog cases. No prior evidence overwritten.'
report['frozenTargetMatches']=all(({**json.loads((HERE.parent/'target.json').read_text())['files'], **json.loads((HERE.parent/'target.json').read_text())['protected']})[path]==value for path,value in hashes.items())
assert hashes=={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in PATHS},'Production source changed while tests ran'
(HERE/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'completed':True,'checks':report['checks'],'sourceHashes':hashes}))
