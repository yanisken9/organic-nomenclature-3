from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
sourcepath=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'js/namelecule-quiz-checkpoints.js'
source='const global=globalThis;global.window=global;\n'+(ROOT/'js/namelecule-game-repair.js').read_text()+'\n'+(ROOT/'docs/checks/workshop-lesson-parity-20261110/unit/fake-dom.js').read_text()+'\nconst controllerSource='+json.dumps(sourcepath.read_text())+';\n'+(HERE/'cases.js').read_text()
# A disposable harness in this new evidence directory; prior evidence stays unchanged.
p=HERE/('controller-harness-counterfactual.js' if len(sys.argv)>1 else 'controller-harness.js');p.write_text(source)
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',str(p.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
report={'controllerPath':str(sourcepath),'controllerSha256':hashlib.sha256(sourcepath.read_bytes()).hexdigest(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'role':'Developer evidence; not independent review'}
success=r.returncode==0 and 'FAIL ' not in r.stdout
report['success']=success
if success:report['result']=json.loads(r.stdout.strip().splitlines()[-1])
name='counterfactual.json' if len(sys.argv)>1 else 'results.json'
(HERE/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'completed':success,'checks':report.get('result',{}).get('checks'),'additionalChecks':report.get('result',{}).get('additionalFinalHeaderChecks'),'failure':(r.stdout+r.stderr)[-1800:] if not success else None}))
sys.exit(0 if success else 1)
