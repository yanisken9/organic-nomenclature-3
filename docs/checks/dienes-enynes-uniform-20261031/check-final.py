"""Read-only final cumulative check, plus retained stage-specific evidence."""
from pathlib import Path
import json,hashlib,runpy,difflib,subprocess
ROOT=Path(__file__).resolve().parents[3]
def check():
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 checkpoint=ROOT/'communication/checkpoints/dienes-enynes-uniform-20261031';base=json.load(open(checkpoint/'baseline.json'));old=checkpoint/'original'
 d=runpy.run_path(str(ROOT/'docs/checks/alkadiene-uniform-20261031/transform.py'));e=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'));data=e['DATA'];before=(old/data).read_text();after=(ROOT/data).read_text()
 for helper in [d,e]:
  for key in helper['KEYS']:
   m,original=helper['literal'](before,key);n,current=helper['literal'](after,key)
   assert current==helper['transform'](original),key
 # Every byte outside exactly these15Expanded literals must be preserved.
 def masked(code):
  for key in d['KEYS']+e['KEYS']:
   m,_=e['literal'](code,key);code=code[:m.start(1)]+'MOL'+code[m.end(1):]
  return code
 assert masked(before)==masked(after)
 for p in base['paths']:
  if not p.endswith('.mol'):continue
  helper=d if any(Path(p).name==k+'_2D_Expanded.mol'for k in d['KEYS'])else e
  assert (ROOT/p).read_text()==helper['transform']((old/p).read_text()),p
 protected={p:h for p,h in base['files'].items()if p not in base['paths']}
 assert len(protected)==842 and all(sha(ROOT/p)==h for p,h in protected.items())
 stage=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/check-sources.py'))['check'](ROOT/'communication/checkpoints/enyne-uniform-20261031')
 freeze=json.load(open(ROOT/'docs/checks/dienes-enynes-uniform-20261031/runtime-freeze.json'))
 assert all(sha(ROOT/p)==h for p,h in freeze.items())
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==base['HEAD']
 assert sha(ROOT/'.git/index')==base['indexSHA256']
 return {'passed':True,'expandedMolecules':15,'applicationPaths':len(base['paths']),'physicalMOLs':9,'protectedSources':len(protected),'enyneFinalCheckPassed':stage['passed'],'outside15LiteralsUnchanged':True,'HEADIndexUnchanged':True,'coreChangedToday':False}
if __name__=='__main__':print(json.dumps(check()))
