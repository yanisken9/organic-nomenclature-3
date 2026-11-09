"""Positive/negative controls for the independent pixel-overlap oracle."""
from pathlib import Path
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
out={'cases':[],'completed':False}
try:
    navigate('docs/checks/acid-uniform-20261101/comparison/index.html')
    ev('document.fonts.ready.then(()=>true)');ev((HERE/'glyph-overlap-probe.js').read_text())
    for font in [5.5,22]:
        for overlap in [False,True]:
            svg='<svg xmlns="http://www.w3.org/2000/svg" width="120" height="60" viewBox="0 0 120 60"><text data-namelecule-role="label" x="10" y="30" font-size="'+str(font)+'" font-family="Helvetica">C</text><text data-namelecule-role="label" x="'+('10'if overlap else'50')+'" y="30" font-size="'+str(font)+'" font-family="Helvetica">C</text></svg>'
            ev('(()=>{document.getElementById("probe")?.remove();const d=document.createElement("div");d.id="probe";d.innerHTML='+json.dumps(svg)+';document.body.append(d);return true})()')
            row=json.loads(ev('JSON.stringify(auditGlyphOverlap(document.querySelector("#probe svg")))'))
            assert bool(row['overlaps'])==overlap
            assert row['labels']==2 and row['inkPixels']>0
            row.update(fontCSS=font,expectedOverlap=overlap);out['cases'].append(row)
    out['completed']=True
finally:save_result(out,'glyph-probe-controls.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
