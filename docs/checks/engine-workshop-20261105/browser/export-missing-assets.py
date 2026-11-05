"""Export two missing diagrams through the existing Main54 SVG pipeline."""
from pathlib import Path
import ast
import hashlib
import json
import os
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
HERE = ROOT / "docs/checks/engine-workshop-20261105/browser"
os.environ["NAMELECULE_BIDI_PORT"] = "9245"
os.environ["NAMELECULE_TEST_BASE_URL"] = "http://127.0.0.1:8055/"
exec(compile((ROOT / "tools/namelecule_bidi.py").read_text(), "bidi", "exec"))
tree = ast.parse((ROOT / "tools/export-name-repair-assets.py").read_text())
EXPORT = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
              and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "EXPORT")
out = {"completed": False, "method": "Existing Main54 expanded SVG; established computed-style export and complete-label framing", "assets": []}
try:
    navigate("mulermoc-nom-54.html?libs=local")
    app_ready()
    ev("document.fonts.ready.then(()=>true)")
    for key, name, labels in [("methane", "μεθάνιο", 5), ("propane", "προπάνιο", 11)]:
        ev("selectedMol=" + json.dumps(key) + ";mode2D='expanded';mainChainMode='algorithmic';nameAnalysisMode='none';numberingFlag=false;fInitProps();fClearHighlights();fLoadMol2D();fShowNameAnalysis();true")
        until("document.querySelectorAll('#jsmeNomeclatureSVG text[data-namelecule-role=label]').length===" + str(labels))
        row = json.loads(ev(EXPORT))
        assert row["name"] == name and row["labels"] == labels, row
        svg = row.pop("svg").encode()
        ET.fromstring(svg)
        source = row.pop("sourceMol").encode()
        target = ROOT / "games/assets/name-repair" / (key + ".svg")
        assert not target.exists(), "Do not overwrite an existing diagram"
        target.write_bytes(svg)
        row.update(moleculeId=key, file=target.relative_to(ROOT).as_posix(),
                   SHA256=hashlib.sha256(svg).hexdigest(), expandedMOLSHA256=hashlib.sha256(source).hexdigest())
        out["assets"].append(row)
        screenshot(HERE / (key + "-main-expanded.png"))
    out["completed"] = True
finally:
    out["javascriptErrors"] = js_errors
    out["exportHelperSHA256"] = hashlib.sha256((ROOT / "tools/export-name-repair-assets.py").read_bytes()).hexdigest()
    (HERE / "missing-assets-provenance.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    call("browsingContext.close", {"context": ctx})
    call("session.end", {})
print(json.dumps({"completed": out["completed"], "assets": len(out["assets"]), "javascriptErrors": len(js_errors)}))
