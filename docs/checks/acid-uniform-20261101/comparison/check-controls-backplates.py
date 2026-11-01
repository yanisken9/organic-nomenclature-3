"""Offline native-primitive audit; never changes DOM, Main or exported figures."""
from pathlib import Path
import json,gzip,runpy,re,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent
d=json.load(gzip.open(HERE/'controls.json.gz','rt'))
assert d['completed']and not d['javascriptErrors']
audit=runpy.run_path(str(HERE/'audit-backplates.py'))['audit']
rows=[];raw_failures=0;removed=0
# Exact existing PNG-export orphan-attribute scrub (viewer52:4066). The browser
# accepts this native highlight DOM, but ElementTree requires valid XML.
pattern=r'\s+[A-Za-z_:-][A-Za-z0-9_:\-\.]*"=""(?=\s|>)'
for row in d['cases']:
    raw=row['rawFinalSVG']
    try:E.fromstring(raw)
    except E.ParseError:raw_failures+=1
    clean,count=re.subn(pattern,'',raw);removed+=count
    # The forensic normalization must leave every bond/backplate byte intact.
    assert re.findall(r'<(?:line|rect)\b[^>]*>',raw)==re.findall(r'<(?:line|rect)\b[^>]*>',clean)
    result=audit(dict(row,rawSVG=clean,variant=row['phase']))
    assert not result['occlusions']and not result['diagonalStrokes']
    rows.append(result)
out={'passed':True,'cases':rows,'source':'controls.json.gz','offlineXMLNormalizationOnly':True,
     'rawDOMXMLParseFailures':raw_failures,'orphanAttributesRemoved':removed,
     'existingExportNormalizationSource':'js/mulermoc-nom-molview-52.js:4066',
     'geometryPrimitiveBytesUnchangedByScrub':True,'appCodeChanged':False}
(HERE/'controls-backplate-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'cases':len(rows),'occlusions':0,'rawDOMXMLParseFailures':raw_failures}))
