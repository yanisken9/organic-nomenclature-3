"""Reuse the existing real-glyph acceptance probe on the candidate54 entry."""
from pathlib import Path
import sys
root=Path.cwd()
tool=root/'tools/check-2d-labels.py'
source=tool.read_text()
assert source.count("navigate('mulermoc-nom-52.html?audit=2d-acceptance')")==1
source=source.replace("navigate('mulermoc-nom-52.html?audit=2d-acceptance')", "navigate('mulermoc-nom-54.html?audit=2d-acceptance')")
sys.argv=[str(tool),'--base-url','http://127.0.0.1:8013/','--bidi-port','9244','--output',str(root/'docs/checks/v54-sync-20261104/all-2d.json.gz')]
exec(compile(source,str(tool),'exec'),{'__file__':str(tool),'__name__':'__main__'})
