"""Developer JSC evidence: pinned chemistry/generator/engines; mocked DOM/bridge/transport."""
from pathlib import Path
import hashlib, json, subprocess
ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
catalog_path=ROOT/'games/data/alkane-structures.json'
catalog=json.loads(catalog_path.read_text())
assert hashlib.sha256(catalog_path.read_bytes()).hexdigest()=='9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'
core_path=ROOT/('js/chemistry-engines/'+catalog['engineSHA256']+'.js')
assert hashlib.sha256(core_path.read_bytes()).hexdigest()==catalog['engineSHA256']
definition=(ROOT/'docs/checks/engine-workshop-20261105/generator/test-generator.py').read_text()
body=definition.split('analysis_body = ',1)[1].split('\njs = ',1)[0]
analysis_body=eval(body,{'core':core_path.read_text()})
paths=['js/namelecule-game-repair.js','js/namelecule-repair-generator.js','js/namelecule-name-builder-engine.js']
js='const catalog='+json.dumps(catalog)+';\nconst analyze=new Function("molecule","engineHash",'+json.dumps(analysis_body)+');\n'
js+='\n'.join((ROOT/p).read_text() for p in paths)
for name,p in [('generatedSource','js/namelecule-generated-repair-checkpoint.js'),('choiceSource','js/namelecule-game-choice-checkpoint.js')]:
 js+='\nconst '+name+'='+json.dumps((ROOT/p).read_text())+';\n'
for name,p in [('oldScenario','docs/checks/alkanes-game-choice-20261111/before/scenarios/alkanes-user-3.scenario.json'),('newScenario','scenarios/alkanes-user-3.scenario.json')]:
 js+='\nconst '+name+'='+json.dumps(json.loads((ROOT/p).read_text()))+';\n'
js+=(HERE/'harness.js').read_text()
(HERE/'generated.js').write_text(js)
run=subprocess.run([JSC,'generated.js'],cwd=HERE,capture_output=True,text=True)
if run.returncode: raise SystemExit(run.stdout+run.stderr)
try: report=json.loads(run.stdout)
except ValueError: raise SystemExit(run.stdout+run.stderr)
report['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['js/namelecule-generated-repair-checkpoint.js','js/namelecule-game-choice-checkpoint.js']}
report['conditions']='JSC; real pinned chemistry engine/generator/name-builder engine; fake DOM, bridge, crypto digest and transport'
report['limitations']=['No actual browser renderer or native child viewer execution','No live Worker/network execution','Controller/storage/browser integration requires separate Root evidence']
(HERE/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
