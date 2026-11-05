#!/usr/bin/env python3
"""Actual full core/viewer functions with a deterministic mocked DOM/applets/timer."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[4]
checkdir=Path(__file__).resolve().parent
core=root/'js/mulermoc-nom-core-54.js'; viewer=root/'js/mulermoc-nom-molview-54.js'
source=(checkdir/'checks.js').read_text().replace('// INSERT ACTUAL SOURCE',core.read_text()+'\n'+viewer.read_text())
with tempfile.NamedTemporaryFile(mode='w',suffix='.js') as f:
 f.write(source);f.flush()
 result=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',f.name],text=True,capture_output=True)
 if result.returncode:
  print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
 report=json.loads(result.stdout)
report['environment']='JavaScriptCore; full current core/viewer; mocked DOM/JSME/scheduler, no browser or external PubChem'
report['hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [core,viewer]}
(checkdir/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if report['passed'] != report['total']: raise SystemExit(1)
