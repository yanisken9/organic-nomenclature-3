"""Bounded preview geometry, native capture and protected-source checks."""
from pathlib import Path
import json,gzip,hashlib,runpy,subprocess,ast,re,math,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
p=runpy.run_path(str(HERE/'prepare.py'));parse=p['parse'];rows=[]
for key in p['CAPTURE_KEYS']:
    before=(HERE/(key+'-before.mol')).read_text();after=(HERE/(key+'-proposed.mol')).read_text()
    assert before==p['literal']((ROOT/p['helpers']['DATA']).read_text(),key)[1]
    assert after==p['proposal'](before,key)
    a,aa,ab=parse(before);b,ba,bb=parse(after);n=len(aa)
    assert a[:4]==b[:4]and a[4+n:]==b[4+n:]and ab==bb
    assert all(x[20:]==y[20:]for x,y in zip(a[4:4+n],b[4:4+n]))
    rows.append({'key':key,'atoms':n,'graphIDsNonXYUnchanged':True,'reproducible':True,'sha256':hashlib.sha256(after.encode()).hexdigest()})
original,preview=p['calibration']((ROOT/'js/mulermoc-nom-molview-52.js').read_text())
assert original==(HERE/'original-calibration.js').read_text()and preview==(HERE/'preview-calibration.js').read_text()
audit=runpy.run_path(str(ROOT/'docs/checks/carbonyl-uniform-20261031/comparison/audit-backplates.py'))['audit']
native=[]
for filename in ['browser.json.gz','controls.json.gz']:
    d=json.load(gzip.open(HERE/filename));assert d['completed']and not d['javascriptErrors']
    for row in d['cases']:
        if row.get('variant')=='before':continue
        raw=row.get('rawSVG',row.get('rawFinalSVG'))
        clean=re.sub(r'\s+[A-Za-z_:-][A-Za-z0-9_:\-\.]*"=""(?=\s|>)','',raw)
        assert re.findall(r'<(?:line|rect)\b[^>]*>',raw)==re.findall(r'<(?:line|rect)\b[^>]*>',clean)
        root=E.fromstring(clean)
        labels={int(t.get('data-namelecule-atom')):t for t in root.iter('{http://www.w3.org/2000/svg}text')if t.get('data-namelecule-role')=='label'}
        assert len(labels)==len(row['atomSymbols'])
        fonts={float(t.get('font-size').removesuffix('px'))for t in labels.values()};assert len(fonts)==1
        font=next(iter(fonts))
        for a,b,o in row['bondGraph']:
            points=[tuple(float(labels[i].get(k))for k in ['data-fixed-c-c-atom-x','data-fixed-c-c-atom-y'])for i in [a,b]]
            target=1.30875 if 'H'in[row['atomSymbols'][a-1],row['atomSymbols'][b-1]]else 2.6175
            assert abs(math.dist(*points)/font-target)<.013
        result=audit(dict(row,rawSVG=clean,variant=row.get('variant',row.get('phase'))))
        assert not result['occlusions']and not result['diagonalStrokes'];native.append(result)
base=json.loads((HERE/'application-baseline.json').read_text());protected=0
for name,digest in base['files'].items():
    if name in ['docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md']:continue
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('Protected file changed',name);protected+=1
assert hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest()==base['indexSHA256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==base['HEAD']
for path in HERE.glob('*.py'):ast.parse(path.read_text())
out={'passed':True,'molecules':rows,'nativeAudits':native,'protectedFilesUnchanged':protected,'MainChanged':False,'coreChanged':False}
(HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':True,'molecules':len(rows),'nativeAudits':len(native),'protectedFilesUnchanged':protected}))
