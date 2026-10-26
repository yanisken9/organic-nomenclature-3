"""Reuse the checked ketone MOL/3D generator, with the four other-ketone specs."""
from pathlib import Path
import argparse,json,runpy
if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--pubchem-cache',type=Path,required=True);parser.add_argument('--specs',type=Path,default=Path('docs/checks/other-ketones-specs-20261026.json'));args=parser.parse_args()
 base=runpy.run_path('docs/checks/generate-ketones-20261026.py')
 # Functions retain run_path's original globals, so update the generator's globals.
 base['generate'].__globals__['SPECS']=json.loads(args.specs.read_text())
 base['generate'](args.output,args.pubchem_cache)
