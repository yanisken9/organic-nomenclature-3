"""Targeted R1 correction evidence; preserves the earlier frozen artifacts."""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
counterfactual=len(sys.argv)>1
controller=Path(sys.argv[1]) if counterfactual else ROOT/'js/namelecule-quiz-checkpoints.js'
renderer=ROOT/'js/namelecule-game-repair.js'
source='const global=globalThis;global.window=global;\n'+renderer.read_text()+'\n'+(HERE/'fake-dom.js').read_text()+'\n'
source+='const controllerSource='+json.dumps(controller.read_text())+';\n'
source+=(HERE/'choice-cases.js').read_text()+'\n'+(HERE/'cases.js').read_text()
name='controller-counterfactual-r1' if counterfactual else 'controller-r2'
target=HERE/(name+'-harness.js')
target.write_text(source)
run=subprocess.run([JSC,str(target.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
success=run.returncode==0 and 'FAIL ' not in run.stdout and 'FAIL ' not in run.stderr
result=None
if success:
    try:result=json.loads(run.stdout.strip().splitlines()[-1]);success=result.get('completed') is True
    except (ValueError,IndexError):success=False
report=dict(success=success,result=result,exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr,
            sourceSHA256={str(controller):hashlib.sha256(controller.read_bytes()).hexdigest(),str(renderer):hashlib.sha256(renderer.read_bytes()).hexdigest()},
            role='Developer evidence, not independent review',conditions='Actual production controller; explicit adapter/canonical-trust/DOM/storage/focus doubles.')
(HERE/(name+'-results.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(name=name,success=success,checks=(result or {}).get('checks'),failure=None if success else (run.stdout+run.stderr)[-2200:]),ensure_ascii=False))
sys.exit(0 if success else 1)
