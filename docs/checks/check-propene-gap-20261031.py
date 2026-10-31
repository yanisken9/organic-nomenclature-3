"""Exact runtime scope and protected source identity for the propene trial."""
from pathlib import Path
import ast,base64,difflib,gzip,hashlib,json,subprocess
s=json.loads(gzip.decompress(Path('docs/checks/propene-gap-before-20261031.json.gz').read_bytes()));old={p:base64.b64decode(v).decode()for p,v in s['sources'].items()}
v='js/mulermoc-nom-molview-52.js';h='mulermoc-nom-52.html'
replacement='''  // The same padding is enabled for the approved propene trial only; other
  // alkenes and representation modes retain their existing native masks.
  if (mode2D !== "expanded" ||
      (nameExamples[selectedMol]?.classification?.seriesKey !== "alkanes" &&
       selectedMol !== "propene")) return;'''
needle='''  if (mode2D !== "expanded" ||
      nameExamples[selectedMol]?.classification?.seriesKey !== "alkanes") return;'''
assert old[v].count(needle)==1
assert Path(v).read_text()==old[v].replace(needle,replacement)
assert Path(h).read_text()==old[h].replace('js/mulermoc-nom-molview-52.js?v=alkane-all-uniform-20261030','js/mulermoc-nom-molview-52.js?v=propene-gap-20261031')
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in s['protected'].items())
assert hashlib.sha256(Path('.git/index').read_bytes()).hexdigest()==s['indexSHA256']
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
subprocess.run([JSC,'-e','new Function(JSON.parse(readline()));'],input=json.dumps(Path(v).read_text())+'\n',text=True,capture_output=True,check=True)
for p in ['docs/checks/check-propene-gap-20261031.py','docs/checks/test-propene-gap-20261031.py']:ast.parse(Path(p).read_text())
result={'passed':True,'viewerOnlyPropeneGateAndComment':True,'existingMaskAlgorithmUnchanged':True,'htmlOnlyViewerCache':True,'protectedRuntimeHashes':len(s['protected']),'coreMOL3DScenariosReactUnchanged':True,'originalIndexPreserved':True,'syntax':'JavaScriptCore viewer +2PythonAST PASS'}
Path('docs/checks/propene-gap-static-20261031.json').write_text(json.dumps(result,indent=2)+'\n')
Path('docs/checks/propene-gap-source-20261031.diff').write_text(''.join(''.join(difflib.unified_diff(t.splitlines(True),Path(p).read_text().splitlines(True),fromfile='before/'+p,tofile='after/'+p))for p,t in old.items()))
print(json.dumps(result))
