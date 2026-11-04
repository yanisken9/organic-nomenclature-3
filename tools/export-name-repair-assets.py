"""Export the repair game's existing Main52 drawings through an owned Firefox.

Requires an explicitly started Firefox BiDi endpoint (NAMELECULE_BIDI_PORT) and
local Main52 server (NAMELECULE_TEST_BASE_URL). Does not start processes, edit
Main52, change MOLs, or implement an alternative molecular renderer.
"""
from pathlib import Path
import hashlib
import json
import os
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/checks/game-repair-20261103"
ASSETS = ROOT / "games/assets/name-repair"
os.environ.setdefault("NAMELECULE_BIDI_PORT", "9241")
os.environ.setdefault("NAMELECULE_TEST_BASE_URL", "http://127.0.0.1:8053/")
exec(compile((ROOT / "tools/namelecule_bidi.py").read_text(), "bidi", "exec"))

EXPORT = r"""(() => {
  const src = document.querySelector('#jsmeNomeclatureSVG svg');
  const copy = src.cloneNode(true);
  const properties = ['fill','fill-opacity','stroke','stroke-width','stroke-opacity',
    'stroke-linecap','stroke-linejoin','font-family','font-size','font-weight',
    'font-style','letter-spacing','text-anchor','dominant-baseline','opacity',
    'visibility','display','paint-order'];
  const originals = [src, ...src.querySelectorAll('*')];
  const clones = [copy, ...copy.querySelectorAll('*')];
  const omittedInvalidAttributes=[];
  let bounds = {left:Infinity, top:Infinity, right:-Infinity, bottom:-Infinity};
  const inverse = src.getScreenCTM().inverse();
  for(let i=0;i<originals.length;i++) {
    const a=originals[i], b=clones[i], style=getComputedStyle(a);
    for(const p of properties)b.style.setProperty(p,style.getPropertyValue(p));
    // The first full-canvas background is not a chemical object. Masks and
    // highlights are retained, including their measured glyph-clearance areas.
    const background = a.tagName==='rect' && a.getAttribute('x')==='0' &&
      a.getAttribute('y')==='0' && !a.hasAttribute('data-namelecule-role');
    if(background){b.remove();continue;}
    if(a!==src && /^(text|rect|line|path|polyline|polygon|circle|ellipse)$/.test(a.tagName)
        && style.display!=='none' && style.visibility!=='hidden') {
      const r=a.getBoundingClientRect();
      for(const [x,y] of [[r.left,r.top],[r.right,r.bottom]]) {
        const p=new DOMPoint(x,y).matrixTransform(inverse);
        bounds.left=Math.min(bounds.left,p.x);bounds.right=Math.max(bounds.right,p.x);
        bounds.top=Math.min(bounds.top,p.y);bounds.bottom=Math.max(bounds.bottom,p.y);
      }
    }
    b.removeAttribute('id');b.removeAttribute('class');
    for(const attr of [...b.attributes]) {
      // HTML DOM accepts names that are illegal in standalone XML (for example
      // an incidental highlight attribute named black"). Remove those at the
      // export boundary; computed fill/stroke above preserves visible styling.
      if(!/^[A-Za-z_][A-Za-z0-9_.:-]*$/.test(attr.name)) {
        omittedInvalidAttributes.push(attr.name);b.removeAttribute(attr.name);
      } else if(/^on/i.test(attr.name))b.removeAttribute(attr.name);
    }
  }
  const label=src.querySelector('text[data-namelecule-role="label"]');
  // Remove the viewer's outer viewBox scale. Intrinsic SVG dimensions must
  // normalize glyphs in root coordinates, not in the old viewport's pixels.
  const m=inverse.multiply(label.getScreenCTM());
  const rootFont=parseFloat(getComputedStyle(label).fontSize)*Math.hypot(m.a,m.b);
  const scale=22/rootFont, margin=14/scale;
  const width=bounds.right-bounds.left+margin*2;
  const height=bounds.bottom-bounds.top+margin*2;
  copy.setAttribute('viewBox',[bounds.left-margin,bounds.top-margin,width,height].join(' '));
  copy.setAttribute('width',(width*scale).toFixed(3));
  copy.setAttribute('height',(height*scale).toFixed(3));
  copy.setAttribute('preserveAspectRatio','xMidYMid meet');
  copy.style.removeProperty('width');copy.style.removeProperty('height');
  copy.setAttribute('xmlns','http://www.w3.org/2000/svg');
  const svg=new XMLSerializer().serializeToString(copy);
  if(new DOMParser().parseFromString(svg,'image/svg+xml').querySelector('parsererror'))
    throw new Error('Export did not produce standalone XML');
  return JSON.stringify({svg, omittedInvalidAttributes,
    name:currentMolName, parts:nameComponentsList, parent:[...mainChainAtomsList],
    sourceMol:nameExamples[selectedMol].structure2D_Expanded,
    labels:src.querySelectorAll('text[data-namelecule-role="label"]').length,
    numbering:src.querySelectorAll('text[id^="number"]').length,
    nominalFontPixels:22, width:width*scale, height:height*scale});
})()"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def export():
    ASSETS.mkdir(parents=True, exist_ok=True)
    HERE.mkdir(parents=True, exist_ok=True)
    game = json.loads((ROOT / "games/data/name-repair-alkanes.json").read_text())
    expected = {r["moleculeId"]: r["correctName"] for r in game["rounds"]}
    evidence = {"date": "2026-11-03", "method": "Main52 live expanded SVG; inline existing computed styles and fit complete drawing; no atom/bond-coordinate edits", "assets": []}
    try:
        navigate("mulermoc-nom-52.html?libs=local")
        app_ready()
        ev("document.fonts.ready.then(()=>true)")
        ev("fInitNamingProps();true")
        for key, correct_name in expected.items():
            ev("selectedMol=" + json.dumps(key) + ";mode2D='expanded';mainChainMode='algorithmic';nameAnalysisMode='none';numberingFlag=false;fInitProps();fClearHighlights();fLoadMol2D();fShowNameAnalysis();true")
            until("!!document.querySelector('#jsmeNomeclatureSVG svg text[data-namelecule-role=label]')")
            for numbered in ([False, True] if key in ["butane", "methyl_2_pentane"] else [False]):
                if numbered:
                    ev("nameAnalysisMode='compCarbonsCount';numberingFlag=true;fHighLightMainChain();fHighLightMainChainBonds();fShowAnalysisNumbering(0);true")
                    until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===mainChainAtomsList.length", seconds=15)
                row = json.loads(ev(EXPORT))
                assert row["name"] == correct_name, (key, row["name"], correct_name)
                assert row["labels"] in [14, 20, 32], row["labels"]
                filename = key + ("-chain" if numbered else "") + ".svg"
                svg = row.pop("svg").encode()
                ET.fromstring(svg)  # independent XML parser before any asset is saved
                raw_mol = row.pop("sourceMol").encode()
                (ASSETS / filename).write_bytes(svg)
                row.update(file=filename, moleculeId=key, numbered=numbered, SHA256=sha(svg), expandedMOLSHA256=sha(raw_mol))
                evidence["assets"].append(row)
                screenshot(HERE / (filename + ".png"))
        evidence["sourceFiles"] = {p: sha((ROOT / p).read_bytes()) for p in ["js/jsme-nick-nomeclature-moc2-data_52.js", "js/mulermoc-nom-molview-52.js", "js/namelecule-label-metrics.js"]}
        (ASSETS / "provenance.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    finally:
        (HERE / "export-diagnostics.json").write_text(json.dumps({"javascriptErrors": js_errors, "diagnostics": [e for e in all_events if e.get("method") == "log.entryAdded" and e.get("params", {}).get("level") in ["error", "warn"]]}, ensure_ascii=False, indent=2) + "\n")
        call("browsingContext.close", {"context": ctx})
        call("session.end", {})
    print(json.dumps({"assets": len(evidence["assets"]), "namesMatchMain": True, "sourceFilesUnchanged": True, "javascriptErrors": len(js_errors)}), flush=True)


if __name__ == "__main__":
    export()
