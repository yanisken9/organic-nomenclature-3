"""Audit actual final Expanded strokes, masks and native length/font ratios."""
from pathlib import Path
import gzip,json,runpy,re,math,xml.etree.ElementTree as E
ROOT=Path.cwd();HERE=ROOT/'docs/checks/ester-uniform-20261101/main'
audit=runpy.run_path(str(ROOT/'docs/checks/carbonyl-uniform-20261031/comparison/audit-backplates.py'))['audit']
rows=[]
for filename in ['forms-after.json.gz','controls.json.gz']:
    source=json.load(gzip.open(HERE/filename));assert source['completed']and not source['javascriptErrors']
    for row in source['cases']:
        if row['mode']!='expanded':continue
        raw=row['rawFinalSVG'];clean=re.sub(r'\s+[A-Za-z_:-][A-Za-z0-9_:\-\.]*"=""(?=\s|>)','',raw)
        assert re.findall(r'<(?:line|rect)\b[^>]*>',raw)==re.findall(r'<(?:line|rect)\b[^>]*>',clean)
        result=audit(dict(row,rawSVG=clean,variant=row.get('phase','')))
        assert not result['occlusions']and not result['diagonalStrokes'],result
        if row['key']in json.loads((HERE/'baseline.json').read_text())['keys']:
            root=E.fromstring(clean);labels={int(t.get('data-namelecule-atom')):t for t in root.iter('{http://www.w3.org/2000/svg}text')if t.get('data-namelecule-role')=='label'}
            assert len(labels)==len(row['atomSymbols'])
            fonts={float(t.get('font-size').removesuffix('px'))for t in labels.values()};assert len(fonts)==1
            font=next(iter(fonts))
            for a,b,o in row['bondGraph']:
                points=[tuple(float(labels[i].get(k))for k in ['data-fixed-c-c-atom-x','data-fixed-c-c-atom-y'])for i in [a,b]]
                target=1.30875 if 'H'in[row['atomSymbols'][a-1],row['atomSymbols'][b-1]]else 2.6175
                assert abs(math.dist(*points)/font-target)<.013
        result['source']=filename;rows.append(result)
out={'passed':True,'nativeExpandedAudits':len(rows),'nonEndpointMaskCuts':0,'diagonalStrokes':0,'esterNativeLengthFontRatiosPassed':True,'cases':rows}
(HERE/'native-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='cases'}))
