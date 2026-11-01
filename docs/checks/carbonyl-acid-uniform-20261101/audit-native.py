"""Audit actual expanded native strokes/backplates in saved Main browser states."""
from pathlib import Path
import gzip,json,runpy,re
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
audit=runpy.run_path(str(ROOT/'docs/checks/carbonyl-uniform-20261031/comparison/audit-backplates.py'))['audit']
rows=[];scrubbed=0
for file in ['forms-before.json.gz','forms-after.json.gz','lessons.json.gz',
             'controls.json.gz','expanded-lessons.json.gz']:
    source=json.load(gzip.open(HERE/file,'rt'));assert source['completed']and not source['javascriptErrors']
    for row in source['cases']:
        if row['mode']!='expanded':continue
        raw=row['rawFinalSVG']
        # Existing exporter scrub only for offline XML parsing. It must not
        # change a single native line or atom-backplate byte.
        clean,n=re.subn(r'\s+[A-Za-z_:-][A-Za-z0-9_:\-\.]*"=""(?=\s|>)','',raw)
        scrubbed+=bool(n)
        assert re.findall(r'<(?:line|rect)\b[^>]*>',raw)==re.findall(r'<(?:line|rect)\b[^>]*>',clean)
        result=audit(dict(row,rawSVG=clean,variant=row.get('phase','')))
        assert not result['occlusions']and not result['diagonalStrokes'],result
        result['source']=file;rows.append(result)
out={'passed':True,'cases':rows,'expandedStates':len(rows),'nonEndpointOcclusions':0,
     'diagonalStrokes':0,'offlineXMLScrubbedStates':scrubbed,
     'normalization':'Existing viewer orphan-attribute export scrub, native line/rect bytes unchanged.'}
(HERE/'native-backplate-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k!='cases'}))
