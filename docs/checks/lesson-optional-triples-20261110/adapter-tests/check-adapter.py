"""Developer headless adapter evidence; real pinned engine/generator, mocked UI/transport.

Run from the repository root. Requires the macOS JavaScriptCore command-line helper.
Browser rendering, controller integration, storage and network are separate checks.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
catalog_path = ROOT / 'games/data/alkane-structures.json'
catalog = json.loads(catalog_path.read_text())
assert hashlib.sha256(catalog_path.read_bytes()).hexdigest() == '9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'
core_path = ROOT / ('js/chemistry-engines/' + catalog['engineSHA256'] + '.js')
assert hashlib.sha256(core_path.read_bytes()).hexdigest() == catalog['engineSHA256']
# Reuse the existing pure analysis function, without executing its tests/writes.
definition = (ROOT / 'docs/checks/engine-workshop-20261105/generator/test-generator.py').read_text()
body = definition.split('analysis_body = ', 1)[1].split('\njs = ', 1)[0]
analysis_body = eval(body, {'core': core_path.read_text()})
adapter_path = ROOT / 'js/namelecule-generated-repair-checkpoint.js'
js = 'const catalog=' + json.dumps(catalog) + ';\n'
js += 'const analyze=new Function("molecule","engineHash",' + json.dumps(analysis_body) + ');\n'
js += (ROOT / 'js/namelecule-game-repair.js').read_text() + '\n'
js += (ROOT / 'js/namelecule-repair-generator.js').read_text() + '\n'
js += 'const adapterSource=' + json.dumps(adapter_path.read_text()) + ';\n'
js += (HERE / 'harness.js').read_text()
(HERE / 'generated.js').write_text(js)
run = subprocess.run([JSC, 'generated.js'], cwd=HERE, capture_output=True, text=True)
if run.returncode:
    raise SystemExit(run.stdout + run.stderr)
try:
    report = json.loads(run.stdout)
except ValueError:
    raise SystemExit(run.stdout + run.stderr)
report['sourceSHA256'] = hashlib.sha256(adapter_path.read_bytes()).hexdigest()
report['conditions'] = 'JSC, real pinned chemistry engine/generator; mocked browser UI, crypto digest and transport'
report['limitations'] = ['No browser renderer execution', 'No controller/storage integration', 'No live network/Worker execution']
(HERE / 'results.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(report, ensure_ascii=False))
