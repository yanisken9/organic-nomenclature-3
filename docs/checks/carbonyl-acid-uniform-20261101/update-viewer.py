"""Bounded shared expanded calibration/cache update; --apply is baseline guarded."""
from pathlib import Path
import argparse,gzip,json,runpy,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
base=json.loads((HERE/'baseline.json').read_text())
VIEWER='js/mulermoc-nom-molview-52.js';HTML='mulermoc-nom-52.html'
def outputs():
    original=json.load(gzip.open(HERE/'before-sources.json.gz','rt'))
    code=original[VIEWER]
    start=code.index('function fPrepareFixedCCAlkanePrototype()')
    end=code.index('function fGetUniform2DLibraryFrame()',start)
    function=code[start:end]
    declaration='  const carbonylScale = '+json.dumps(base['keys'])+'.includes(selectedMol);\n'
    function=function.replace('  const etherScale = [',declaration+'  const etherScale = [',1)
    function=function.replace('(!etherScale && ![','(!etherScale && !carbonylScale && ![',1)
    old='''    // Ethers use the same drawing unit for C-C and C-O. Include C-O so
    // dimethyl ether (which has no C-C bond) shares the same calibration.
    if (!(first === "C" && second === "C") &&
        !(etherScale && ((first === "C" && second === "O") ||
                         (first === "O" && second === "C")))) continue;'''
    new='''    // Normalized drawings share the same heavy-bond unit. C-O includes
    // C=O, so methanal and methanoic acid also calibrate without any C-C.
    if (!(first === "C" && second === "C") &&
        !((etherScale || carbonylScale) &&
          ((first === "C" && second === "O") || (first === "O" && second === "C"))) &&
        !(carbonylScale &&
          ((first === "C" && second === "N") || (first === "N" && second === "C")))) continue;'''
    assert function.count(old)==1;function=function.replace(old,new)
    old='    if (!label || label.node.textContent.trim() !== allAtomsTypeList[atom]) return;'
    new=r'''    const symbol = allAtomsTypeList[atom];
    const raw = label?.node.textContent.replace(/\s+/g, "");
    if (!label || !(raw === symbol || (carbonylScale &&
        ((symbol === "O" && ["OH", "HO"].includes(raw)) ||
         (symbol === "N" && raw === "NH2"))))) return;'''
    assert function.count(old)==1;function=function.replace(old,new)
    old='''    changes.push([label, {x: anchor.x - cx, y: anchor.y + cy,
      "font-size": font + "px"}, anchor]);'''
    new=r'''    const prefix = raw === "HO" ? context.measureText("H").width : 0;
    // Keep implicit-H labels intact. Queue all changes, including numeric
    // subscript offsets, so a later validation failure leaves the drawing intact.
    const offsets = [];
    for (const tspan of label.node.querySelectorAll("tspan[dy]")) {
      const dy = tspan.getAttribute("dy");
      if (/^-?\d+(?:\.\d+)?$/.test(dy))
        offsets.push([tspan, String(Number(dy) * font / originalFont)]);
    }
    changes.push([label, {x: anchor.x - cx - prefix, y: anchor.y + cy,
      "font-size": font + "px"}, anchor, offsets]);'''
    assert function.count(old)==1;function=function.replace(old,new)
    function=function.replace('changes.forEach(([label, attributes, anchor]) => {',
                              'changes.forEach(([label, attributes, anchor, offsets]) => {')
    function=function.replace('    label.attr(attributes);',
                              '    label.attr(attributes);\n    offsets.forEach(([node, dy]) => node.setAttribute("dy", dy));')
    code=code[:start]+function+code[end:]
    old='''    // Preserve the approved centered square policy for shortened expanded alkanes.
    if (svg.dataset.alkaneFixedCCScale && text.dataset.fixedCCAtomX) {'''
    new='''    // Single-element labels retain the approved centered square. Compound
    // OH/NH2 labels need their complete measured ink bounds, including H/tails.
    const singleElement = text.textContent.replace(/\\s+/g, "") === allAtomsTypeList[index];
    if (svg.dataset.alkaneFixedCCScale && text.dataset.fixedCCAtomX && singleElement) {'''
    assert code.count(old)==1;code=code.replace(old,new)
    html=original[HTML]
    data_output=runpy.run_path(str(HERE/'transform.py'))['outputs']()[1]
    for file in ['js/jsme-nick-nomeclature-moc2-data_52.js','js/mulermoc-nom-molview-52.js']:
        old=file+'?v=ether-uniform-20261031'
        assert html.count(old)==1
        content=code if file==VIEWER else data_output[file]
        version=hashlib.sha256(content.encode()).hexdigest()[:12]
        html=html.replace(old,file+'?v=carbonyl-acid-uniform-20261101-'+version)
    return original,{VIEWER:code,HTML:html}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args()
    original,result=outputs()
    if args.apply:
        for name in result:assert(ROOT/name).read_bytes()==original[name].encode(),('Baseline changed',name)
        for name,content in result.items():(ROOT/name).write_text(content)
    print(json.dumps({'files':list(result),'applied':args.apply}))
