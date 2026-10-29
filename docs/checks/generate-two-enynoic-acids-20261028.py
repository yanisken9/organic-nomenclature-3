"""Two approved unbranched enynoic acid assets using existing graph/3D conventions."""
from pathlib import Path
import argparse,json,runpy
helpers=runpy.run_path('docs/checks/generate-other-acids-20261028.py')
SPECS=json.loads(Path('docs/checks/two-enynoic-acids-specs-20261028.json').read_text())
def generate(output,cache):
 output.mkdir(parents=True,exist_ok=True)
 for s in SPECS:
  for form,m in helpers['forms'](s).items():
   p=output/(s['key']+'_2D_'+form+'.mol');assert not p.exists();p.write_text(helpers['block'](m,p.stem))
  raw,provenance=helpers['qualified_three'](s,cache)
  p=output/(s['key']+'_3D.sdf');assert not p.exists();p.write_bytes(raw)
  (output/(s['key']+'_3D.provenance.json')).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
  print('Generated',s['key'],s['formula'],provenance['source'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);a=p.parse_args();generate(a.output,a.cache)
