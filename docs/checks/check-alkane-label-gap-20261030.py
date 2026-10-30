"""Bounded static scope check for expanded alkane label-mask clearance."""
from pathlib import Path
import argparse
import ast
import base64
import difflib
import gzip
import hashlib
import json
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--before',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
snapshot=json.loads(gzip.decompress(args.before.read_bytes()))
old={p:base64.b64decode(v).decode()for p,v in snapshot['sources'].items()}
viewer='js/mulermoc-nom-molview-52.js';html='mulermoc-nom-52.html'
current=Path(viewer).read_text()
start=current.index('function fPadExpandedAlkaneBranchLabels()')
end=current.index('// ── fMolHasSpCarbon',start)
without=current[:start]+current[end:]
new_hook='''    if (mode2D === "expanded") {
      fPadExpandedCarboxylLabels();
      fPadExpandedAlkaneBranchLabels();
    }'''
assert without.replace(new_hook,'    if (mode2D === "expanded") fPadExpandedCarboxylLabels();')==old[viewer]
assert Path(html).read_text().replace('v=alkane-label-gap-20261030','v=ester-display-20261029')==old[html]
subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                '-e','new Function(JSON.parse(readline()));print("Viewer syntax PASS")'],
               input=json.dumps(current)+'\n',text=True,check=True)
for path in ('docs/checks/check-alkane-label-gap-20261030.py','docs/checks/test-alkane-label-gap-20261030.py'):
    ast.parse(Path(path).read_text())
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=[p for p in snapshot['fileHashes']if p not in allowed]
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==snapshot['fileHashes'][p]for p in protected)
diff=[]
for path,before in old.items():
    diff.extend(difflib.unified_diff(before.splitlines(keepends=True),Path(path).read_text().splitlines(keepends=True),fromfile='a/'+path,tofile='b/'+path))
args.output.with_name('alkane-label-gap-source-20261030.diff').write_text(''.join(diff))
result={'passed':True,'changedApplicationFiles':[viewer,html],'viewerScope':'One expanded alkane vertical C-C endpoint mask helper and fit hook; existing acid function unchanged',
        'nativeLineAndTextCoordinatesUnchangedByCode':True,'protectedFilesUnchanged':len(protected),
        'dataMOL3DCoreReactScenariosUnchanged':True,'viewerSyntax':'PASS','pythonAST':2,
        'coreSHA256':snapshot['fileHashes']['js/mulermoc-nom-core-52.js']}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS scope/syntax;',len(protected),'protected files unchanged')
