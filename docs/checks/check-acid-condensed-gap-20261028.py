"""Read-only with --read-only: exact source scope and all protected assets."""
from pathlib import Path
import base64,gzip,json,hashlib,difflib,subprocess,sys,ast
base=json.loads(Path('docs/checks/acid-condensed-gap-before-20261028.json').read_text())
old={p:base64.b64decode(v).decode()for p,v in json.loads(gzip.decompress(Path('docs/checks/acid-condensed-gap-before-source-20261028.json.gz').read_bytes())).items()}
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'};n=0
for p,h in base['files'].items():
 if p in allowed:continue
 assert Path(p).is_file()and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('protected changed',p);n+=1
p='js/mulermoc-nom-molview-52.js';before=old[p];after=Path(p).read_text();start=before.index('function fAddHydrogens2SVG()');end=before.index('function fGetCompactedAtomSkipSet',start)
a=after.index('function fAddHydrogens2SVG()');b=after.index('function fGetCompactedAtomSkipSet',a)
assert before[:start]==after[:a]and before[end:]==after[b:]
p='mulermoc-nom-52.html';assert old[p].replace('molview-52.js?v=acid-layout-20261028','molview-52.js?v=acid-condensed-gap-20261028')==Path(p).read_text()
node='/tmp/namelecule-react-tools/node-v24.22.1-darwin-x64/bin/node';subprocess.run([node,'--check','js/mulermoc-nom-molview-52.js'],check=True)
for p in ['docs/checks/check-acid-condensed-gap-20261028.py','docs/checks/test-acid-condensed-gap-browser-20261028.py']:ast.parse(Path(p).read_text(),filename=p)
subprocess.run(['git','diff','--check'],check=True)
result={'passed':True,'protectedFiles':n,'core52SHA256':hashlib.sha256(Path('js/mulermoc-nom-core-52.js').read_bytes()).hexdigest(),'unchangedAllMolsDataScenariosAndReact':True,'sourceScope':'Only existing fAddHydrogens2SVG and MainHTML viewer cache URL'}
if '--read-only'not in sys.argv:
 Path('docs/checks/acid-condensed-gap-static-20261028.json').write_text(json.dumps(result,indent=2)+'\n')
 diff=''.join(''.join(difflib.unified_diff(s.splitlines(True),Path(p).read_text().splitlines(True),fromfile='before/'+p,tofile='after/'+p))for p,s in old.items());Path('docs/checks/acid-condensed-gap-source-20261028.diff').write_text(diff)
print('PASS',result)
