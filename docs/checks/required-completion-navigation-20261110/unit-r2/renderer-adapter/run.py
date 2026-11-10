"""Bounded Developer checks: actual renderer/adapter, explicit DOM/transport doubles.

Run from repo root. Writes only this new evidence folder. No old runner is run.
JSC receives an ASCII relative filename; FAIL output is a failure even on exit 0.
"""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
BEFORE = ROOT / 'docs/checks/required-completion-navigation-20261110/browser-r2/before'
TARGET = ROOT / 'docs/checks/required-completion-navigation-20261110/target-r2.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_assignment(path, name):
    tree = ast.parse(path.read_text())
    value = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
    return ast.literal_eval(value)


def execute(name, source):
    path = HERE / (name + '-generated.js')
    path.write_text(source)
    run = subprocess.run([JSC, str(path.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    success = run.returncode == 0 and 'FAIL ' not in run.stdout and 'FAIL ' not in run.stderr
    result = None
    if success:
        try:
            result = json.loads(run.stdout.strip().splitlines()[-1])
            success = result.get('passed') is True
        except (ValueError, IndexError):
            success = False
    report = dict(success=success, exitCode=run.returncode, stdout=run.stdout,
                  stderr=run.stderr, result=result,
                  role='Developer evidence; not independent review')
    (HERE / (name + '-results.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(name=name, success=success, checks=(result or {}).get('checks'),
                         failure=None if success else (run.stdout + run.stderr)[-2400:]), ensure_ascii=False))
    return success


dom_path = ROOT / 'docs/checks/alkane-checkpoint-pilot-20261104/repair/test-mount.py'
dom = literal_assignment(dom_path, 'dom')
dom = dom.replace(' constructor(tag){', ' get isConnected(){return this===document.body||!!(this.parentNode&&this.parentNode.isConnected)}\n constructor(tag){')
dom = dom.replace('const window={scrollTo(){scrollCalls++}};', 'const window=globalThis;globalThis.scrollTo=()=>{scrollCalls++};')
dom = dom.replace(' get classList(){', ' removeAttribute(key){delete this.attributes[key]}\n get classList(){')
prefix = 'const global=globalThis;\n' + dom + '\nglobal.document=document;global.window=global;\n'
game_path = ROOT / 'games/data/name-repair-alkanes.json'
renderer_path = ROOT / 'js/namelecule-game-repair.js'
adapter_path = ROOT / 'js/namelecule-generated-repair-checkpoint.js'
generator_path = ROOT / 'js/namelecule-repair-generator.js'
target = json.loads(TARGET.read_text())
for path in [renderer_path, adapter_path]:
    assert sha(path) == target['files'][str(path.relative_to(ROOT))], 'Frozen R2 source differs: ' + str(path)
source_paths = [renderer_path, adapter_path, generator_path, game_path, dom_path]
renderer_js = prefix + '\nconst GAME=' + game_path.read_text() + ';\n'
renderer_js += 'const beforeRendererSource=' + json.dumps((BEFORE / 'js/namelecule-game-repair.js').read_text()) + ';\n'
renderer_js += 'const rendererSource=' + json.dumps(renderer_path.read_text()) + ';\n'
renderer_js += (HERE / 'renderer-cases.js').read_text()

catalog_path = ROOT / 'games/data/alkane-structures.json'
catalog = json.loads(catalog_path.read_text())
assert sha(catalog_path) == '9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'
core_path = ROOT / ('js/chemistry-engines/' + catalog['engineSHA256'] + '.js')
assert sha(core_path) == catalog['engineSHA256']
# Read the established pure pinned-engine analysis expression without executing its writer/tests.
definition_path = ROOT / 'docs/checks/engine-workshop-20261105/generator/test-generator.py'
definition = definition_path.read_text()
body = definition.split('analysis_body = ', 1)[1].split('\njs = ', 1)[0]
analysis_body = eval(body, {'core': core_path.read_text(), '__builtins__': {}})
adapter_js = prefix + '\nconst catalog=' + json.dumps(catalog) + ';\n'
adapter_js += 'const analyze=new Function("molecule","engineHash",' + json.dumps(analysis_body) + ');\n'
adapter_js += renderer_path.read_text() + '\n' + generator_path.read_text() + '\n'
adapter_js += 'const adapterSource=' + json.dumps(adapter_path.read_text()) + ';\n'
adapter_js += 'const beforeAdapterSource=' + json.dumps((BEFORE / 'js/namelecule-generated-repair-checkpoint.js').read_text()) + ';\n'
adapter_js += (HERE / 'adapter-cases.js').read_text()
successes = [execute('renderer', renderer_js), execute('adapter', adapter_js)]
source_paths += [catalog_path, core_path, definition_path]
manifest = dict(sourceSHA256={str(p.relative_to(ROOT)): sha(p) for p in source_paths},
                beforeSHA256={str(p.relative_to(BEFORE)): sha(p) for p in [BEFORE / 'js/namelecule-game-repair.js', BEFORE / 'js/namelecule-generated-repair-checkpoint.js']},
                conditions='System JavaScriptCore, actual production renderer+adapter+generator and pinned chemistry engine; DOM, image events, fetch/crypto/Worker transport are explicit doubles.',
                limits=['No native DOM/layout/image network or browser input claim.',
                        'Actual renderer and adapter are exercised together and separately; focused stale-callback probes invoke captured adapter callbacks as a deliberately adversarial renderer double.',
                        'Controller integration and native browser checks are separate root/browser-worker evidence.'],
                artifactSHA256={p.name: sha(p) for p in HERE.iterdir() if p.is_file() and p.name != 'manifest.json'},
                success=all(successes))
(HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
sys.exit(0 if all(successes) else 1)
