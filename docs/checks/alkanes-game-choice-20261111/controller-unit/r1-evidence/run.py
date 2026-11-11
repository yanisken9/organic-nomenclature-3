"""Bounded Developer checks; writes only this owned evidence directory."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'

def execute(name,source):
    path=HERE/(name+'-harness.js')
    path.write_text(source)
    result=subprocess.run([JSC,str(path.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
    success=result.returncode==0 and 'FAIL ' not in result.stdout and 'FAIL ' not in result.stderr
    parsed=None
    if success:
        try:
            parsed=json.loads(result.stdout.strip().splitlines()[-1])
            success=parsed.get('completed',parsed.get('passed')) is True
        except (ValueError,IndexError):
            success=False
    report=dict(success=success,exitCode=result.returncode,result=parsed,stdout=result.stdout,stderr=result.stderr,
                role='Developer evidence; not independent review')
    (HERE/(name+'-results.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(name=name,success=success,checks=(parsed or {}).get('checks'),
                         failure=None if success else (result.stdout+result.stderr)[-2400:]),ensure_ascii=False))
    return success

controller=ROOT/'js/namelecule-quiz-checkpoints.js'
renderer=ROOT/'js/namelecule-game-repair.js'
prefix='const global=globalThis;global.window=global;\n'
controller_source=prefix+renderer.read_text()+'\n'+(HERE/'fake-dom.js').read_text()+'\n'
controller_source+='const controllerSource='+json.dumps(controller.read_text())+';\n'
controller_source+=(HERE/'choice-cases.js').read_text()+'\n'+(HERE/'cases.js').read_text()
passed=[execute('controller',controller_source)]

dompath=ROOT/'docs/checks/alkane-checkpoint-pilot-20261104/repair/test-mount.py'
tree=ast.parse(dompath.read_text())
dom=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='dom' for t in n.targets)))
dom=dom.replace(' get classList(){',' removeAttribute(key){delete this.attributes[key]}\n get classList(){')
dom=dom.replace('const window={scrollTo(){scrollCalls++}};','const window=globalThis;globalThis.scrollTo=()=>{scrollCalls++};')
renderer_source=prefix+dom+'\nglobal.document=document;\n'
renderer_source+='const GAME='+(ROOT/'games/data/name-repair-alkanes.json').read_text()+';\n'
renderer_source+='const beforeRendererSource='+json.dumps((ROOT/'docs/checks/alkanes-game-choice-20261111/before/js/namelecule-game-repair.js').read_text())+';\n'
renderer_source+='const rendererSource='+json.dumps(renderer.read_text())+';\n'
renderer_source+=(HERE/'renderer-cases.js').read_text()
passed.append(execute('renderer',renderer_source))
sources=[controller,renderer,HERE/'cases.js',HERE/'choice-cases.js',HERE/'fake-dom.js',HERE/'renderer-cases.js',dompath]
manifest=dict(success=all(passed),sourceSHA256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              role='Developer evidence; not independent review',conditions='System JavaScriptCore; explicit DOM/image/storage/adapter/canonical-trust doubles.',
              limits=['Native browser/integration/real generated molecular evidence is separate root-owned verification.','No source, core, notes, git or other evidence directories written by this runner.'])
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
sys.exit(0 if all(passed) else 1)
