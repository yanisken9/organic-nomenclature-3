"""Rerun directly affected broad naming/generator suites into new correction evidence.
Parser/map/geometry implementations are unchanged; original full evidence retained.
"""
from pathlib import Path
import argparse
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;D=H/'corrections-20261110';C=Path(argparse.ArgumentParser().parse_known_args()[1][0])
names=['test-causal-probes.py']if '--causal-only' in __import__('sys').argv else ['test-core55.py','test-naming55.py','test-en-variants.py','test-causal-probes.py']
for name in names:
 p=H/name;s=p.read_text()
 if name=='test-core55.py':s=s[:s.index("for name in ['mol-properties54','map-transitions54']:")]
 s=s.replace("H=Path(__file__).resolve().parent",'H=Path('+repr(str(D))+')')
 if name=='test-causal-probes.py':
  s=s.replace("assert all(x['status']=='named'for x in result['candidate55']['supported'])","assert all(x['status']=='named'for x in result['candidate55']['supported'][:2])\nassert result['candidate55']['supported'][2]['status']=='declined' # selected parent leaves a plain carbon branch (CV55-10)")
  s=s.replace("'off main chain' in result['candidate55']['fork']['error']", "'NOM-DECLINE' in result['candidate55']['fork']['error']")
 exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
