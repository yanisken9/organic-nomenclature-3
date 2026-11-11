"""Reproduce R2 on exact preserved r1 source with virtual time and ignored fetch abort."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
# Current generated unit bundle supplies real chemistry dependencies; replace both
# adapter strings with the preserved, hash-checked r1 review target.
js=(HERE/'generated.js').read_text().split('const global=globalThis;\nconst analyses=',1)[0]
for name,filename,expected in [('generatedSource','r1-namelecule-generated-repair-checkpoint.js','0e3db17644ddaac83a41d34f6658b915a6d6047898fa51b84fab69a7d25eb9d9'),('choiceSource','r1-namelecule-game-choice-checkpoint.js','cc6e68fb9d6f1ed074c9ddf768bf9ede4250e32163d8b0e793f18139928c694c')]:
 old=(HERE/filename).read_text()
 assert hashlib.sha256(old.encode()).hexdigest()==expected
 prefix='const '+name+'='
 start=js.index(prefix)+len(prefix)
 _,length=json.JSONDecoder().raw_decode(js[start:])
 js=js[:start]+json.dumps(old)+js[start+length:]
js+=(HERE/'harness.js').read_text().split('(async()=>{',1)[0]
js+=(HERE/'counterfactual.js').read_text()
(HERE/'counterfactual-generated.js').write_text(js)
run=subprocess.run([JSC,'counterfactual-generated.js'],cwd=HERE,capture_output=True,text=True)
if run.returncode: raise SystemExit(run.stdout+run.stderr)
report=json.loads(run.stdout)
(HERE/'counterfactual-r1-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
