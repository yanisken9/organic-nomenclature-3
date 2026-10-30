"""Prove the approved viewer-only scope against the pre-intervention snapshot."""
from pathlib import Path
import ast,base64,difflib,gzip,hashlib,json,subprocess
prefix=Path('docs/checks/alkane-clearance-v2-')
s=json.loads(gzip.decompress(Path(str(prefix)+'before-20261030.json.gz').read_bytes()))
old={p:base64.b64decode(v).decode()for p,v in s['sources'].items()}
v='js/mulermoc-nom-molview-52.js';h='mulermoc-nom-52.html';new=Path(v).read_text()
a=old[v].index('function fPadExpandedAlkaneBranchLabels()');b=old[v].index('// ── fMolHasSpCarbon',a)
x=new.index('function fPadExpandedAlkaneLabels()');y=new.index('// ── fMolHasSpCarbon',x)
assert new[:x]==old[v][:a]
assert new[y:].replace('fPadExpandedAlkaneLabels();','fPadExpandedAlkaneBranchLabels();')==old[v][b:]
assert Path(h).read_text().replace('v=alkane-clearance-v2-20261030','v=alkane-label-gap-20261030')==old[h]
allowed={v,h,'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=[p for p in s['fileHashes']if p not in allowed]
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==s['fileHashes'][p]for p in protected)
Path(str(prefix)+'source-20261030.diff').write_text(''.join(''.join(difflib.unified_diff(before.splitlines(True),Path(p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p))for p,before in old.items()))
subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','new Function(JSON.parse(readline()));print("JS syntax PASS")'],input=json.dumps(new)+'\n',text=True,check=True)
for p in ['docs/checks/check-alkane-clearance-v2-20261030.py','docs/checks/test-alkane-clearance-v2-20261030.py','docs/checks/test-alkane-clearance-v2-lesson-20261030.py','docs/checks/test-alkane-clearance-v2-fit-20261030.py','docs/checks/test-alkane-clearance-v2-targeted-zoom-20261030.py']:ast.parse(Path(p).read_text())
Path(str(prefix)+'static-20261030.json').write_text(json.dumps({'passed':True,'protectedFilesUnchanged':len(protected),'scope':'Alkane expanded C/H backplates only, fit hook rename and HTML cache URL','coreSHA256':s['fileHashes']['js/mulermoc-nom-core-52.js'],'syntax':'JavaScriptCore + 5 Python ASTs PASS'},indent=2)+'\n')
print(len(protected),'protected files unchanged')
