"""Targeted policy, syntax and pre-existing-file protection checks."""
from pathlib import Path
import json,hashlib,subprocess,ast
root=Path(__file__).resolve().parents[2]
source=(root/'js/mulermoc-nom-molview-51.js').read_text()
start=source.index('function fSequentialKetoneNumberingTarget()')
end=source.index('function fExplainNameComp()',start)
helpers=source[start:end]
body='var currNumberEl=4,out={removed:0,cleared:0},document={querySelectorAll(){return [{remove(){out.removed++}}]}};function removeEcho3D(){out.cleared++}function fShowNumbering(time,a,b){out.timed=time===undefined;out.atoms=a;out.three=b};'+helpers+'fShowAnalysisNumbering(0,atoms,three);out.counter=currNumberEl;return out;'
keys=['pentanone_3','dimethyl_2_4_pentanone_3','trimethyl_3_4_4_pentanone_2','diethyl_4_5_dimethyl_2_6_heptanone_3']
js='var run=new Function("selectedMol","atoms","three",'+json.dumps(body)+');var rows=[];'
for key in keys+['methane','methyl_2_propanal','propanone']:
 js+='rows.push(['+json.dumps(key)+',run('+json.dumps(key)+',null,null)]);'
js+='rows.push(["override",run('+json.dumps(keys[0])+',[7,8],[2,3])]);print(JSON.stringify(rows));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True)
rows=json.loads(r.stdout)
for key,row in rows:
 scoped=key in keys
 assert row['timed']==scoped and row['removed']==int(scoped) and row['cleared']==int(scoped),(key,row)
 assert row['counter']==(0 if scoped else 4),(key,row)
 if key=='override':assert row['atoms']==[7,8] and row['three']==[2,3]
base=json.loads(Path('/tmp/namelecule-before-ketone-numbering-20261026/manifest.json').read_text())
allowed={'js/mulermoc-nom-molview-51.js','mulermoc-nom-51.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for path,h in base.items():
 if path in allowed:continue
 assert (root/path).is_file() and hashlib.sha256((root/path).read_bytes()).hexdigest()==h,path
 protected+=1
assert 'mulermoc-nom-molview-51.js?v=ketone-numbering-20261026' in (root/'mulermoc-nom-51.html').read_text()
ast.parse((root/'docs/checks/test-ketone-numbering-browser-20261026.py').read_text())
print('PASS8policy/override cases,AST/cache;',protected,'pre-existingfilesunchanged includingcore/data/MOL/SDF/scenarios')
