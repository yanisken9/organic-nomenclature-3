from pathlib import Path
import re,subprocess,json,hashlib,datetime
E=Path(__file__).parent;p=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js/mulermoc-nom-molview-56.js');s=p.read_text()
ms=list(re.finditer(r'^(?:async )?function (\w+)\(',s,re.M))
def fn(name):
 i=next(i for i,m in enumerate(ms) if m[1]==name);return s[ms[i].start():ms[i+1].start()]
code='\n'.join(fn(n) for n in ['fMulerSelectHeteroAnchors','fGetRenderedAtomTextMap','fBuildMoleculeSVG'])+'\n'+(E/'test-integration-cases.js').read_text()
(E/'actual-integration-functions.js').write_text(code)
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','actual-integration-functions.js'],cwd=E,capture_output=True,text=True)
(E/'integration-output.txt').write_text(r.stdout+r.stderr);print(r.stdout,r.stderr)
(E/'integration-results.json').write_text(json.dumps({'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual extracted selection map and renderer lifecycle functions with deterministic DOM/applet doubles; browser still required','runtimeSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'exitCode':r.returncode,'output':r.stdout},indent=2)+'\n')
raise SystemExit(r.returncode)
