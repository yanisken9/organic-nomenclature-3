#!/usr/bin/env python3
"""Export the six curated alkanes through the actual Main57 SVG renderer.

Requires an explicitly provided, owned Firefox BiDi endpoint and local server.
Starts no browser/server process. Writes only the twelve current pool-v2 SVGs
and their provenance after every live drawing passes its source/name checks.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CATALOG = "games/data/alkane-structures-v2.json"
MANIFEST = "data/namelecule-alkanes-v1/manifest.json"
BUNDLE = "js/MULERMOC_namelecule_alkanes_v1_data.js"
MAIN = "mulermoc-nom-57.html"
ASSETS = ROOT / "games/assets/name-repair"
PROVENANCE = ASSETS / "pool-v2-provenance.json"
EXPORT_SOURCE = "tools/export-name-repair-assets.py"
SOURCE_FILES = (
    MAIN, "js/mulermoc-nom-molview-57.js", "js/mulermoc-nom-core-57.js",
    "js/jsme-nick-nomeclature-moc2-data_57.js", BUNDLE,
    "js/namelecule-label-metrics.js", "css/jsme-nick-57.css",
    CATALOG, MANIFEST, EXPORT_SOURCE, "tools/export-alkane-pool-assets.py",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def extract_export():
    """Read the existing export expression without importing its live driver."""
    tree = ast.parse((ROOT / EXPORT_SOURCE).read_text(encoding="utf-8"))
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "EXPORT"
                           for t in node.targets)]
    if len(assignments) != 1:
        raise ValueError("Expected one existing EXPORT string")
    expression = ast.literal_eval(assignments[0].value)
    original = "sourceMol:nameExamples[selectedMol].structure2D_Expanded,"
    if not isinstance(expression, str) or expression.count(original) != 1:
        raise ValueError("Existing SVG export contract changed; inspect before reuse")
    return expression.replace(original,
        "sourceMol:nameExamples[selectedMol][mode2D==='expanded' ? "
        "'structure2D_Expanded' : 'structure2D_Condensed'],")


def read_inputs():
    catalog = json.loads((ROOT / CATALOG).read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    if catalog.get("catalogVersion") != 2 or manifest.get("id") != "namelecule-alkanes-v1":
        raise ValueError("Expected the approved version2 catalog and alkane pack")
    if catalog["source"]["pack"]["sha256"] != sha((ROOT / MANIFEST).read_bytes()):
        raise ValueError("Catalog does not match the current pack manifest; rebuild it first")
    molecules = manifest["molecules"]
    if len(molecules) != 6 or len({row["id"] for row in molecules}) != 6:
        raise ValueError("This export is bounded to the six approved new alkanes")
    by_id = {row["id"]: row for row in catalog["molecules"]}
    for row in molecules:
        key = row["id"]
        if not re.fullmatch(r"[a-z0-9_]+", key) or key not in by_id:
            raise ValueError("Missing or unsafe molecule ID: " + key)
        entry = by_id[key]
        for mode, field in (("expanded", "asset"), ("condensed", "condensedAsset")):
            if entry[field] != f"assets/name-repair/{mode}-v2/{key}.svg":
                raise ValueError("Unexpected output path for " + key)
            source = ROOT / row["files"][mode]
            source.resolve().relative_to((ROOT / "mols/namelecule-alkanes-v1").resolve())
            if sha(source.read_bytes()) != row["sha256"][mode]:
                raise ValueError("Manifest source hash mismatch: " + str(source))
        if sha(entry["mol"].encode()) != entry["sourceSHA256"] or entry["sourceSHA256"] != row["sha256"]["expanded"]:
            raise ValueError("Catalog expanded MOL does not match the source: " + key)
    return catalog, molecules, extract_export()


def valid_base(value):
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise argparse.ArgumentTypeError("Use an explicitly owned loopback HTTP server base URL")
    return value.rstrip("/") + "/"


def source_hashes(molecules):
    paths = list(SOURCE_FILES)
    paths.extend(row["files"][mode] for row in molecules for mode in ("expanded", "condensed"))
    return {path: sha((ROOT / path).read_bytes()) for path in paths}


def verify_server(base_url, hashes):
    result = {}
    for path in (MAIN, "js/mulermoc-nom-molview-57.js", BUNDLE):
        url = urllib.parse.urljoin(base_url, path)
        with urllib.request.urlopen(url, timeout=30) as response:
            digest = sha(response.read())
        if digest != hashes[path]:
            raise ValueError("Local server content differs from workspace: " + path)
        result[path] = {"url": url, "sha256": digest}
    return result


def validate_svg(row, molecule, mode):
    if row["name"] != molecule["nameGR"]:
        raise ValueError((molecule["id"], mode, "native name mismatch", row["name"]))
    if row["numbering"] != 0 or row["labels"] <= 0:
        raise ValueError((molecule["id"], mode, "numbering or missing labels"))
    raw_mol = row.pop("sourceMol").encode()
    if sha(raw_mol) != molecule["sha256"][mode]:
        raise ValueError((molecule["id"], mode, "native source MOL mismatch"))
    atom_count = int(raw_mol.decode().splitlines()[3][:3])
    if row["labels"] != atom_count:
        raise ValueError((molecule["id"], mode, "not every source atom has a label", row["labels"], atom_count))
    raw_svg = row.pop("svg").encode()
    svg = ET.fromstring(raw_svg)
    viewbox = [float(value) for value in svg.attrib["viewBox"].split()]
    if (svg.tag != "{http://www.w3.org/2000/svg}svg" or len(viewbox) != 4
            or not all(math.isfinite(v) for v in viewbox) or min(viewbox[2:]) <= 0
            or not all(math.isfinite(row[v]) and row[v] > 0 for v in ("width", "height"))):
        raise ValueError("Invalid standalone SVG dimensions")
    return raw_svg, sha(raw_mol)


def export(args):
    catalog, molecules, expression = read_inputs()
    before = source_hashes(molecules)
    served = verify_server(args.base_url, before)
    # The BiDi helper creates one tab/session only when this command is run.
    # Reading this module, --help and --check-inputs never load that helper.
    os.environ["NAMELECULE_BIDI_PORT"] = str(args.bidi_port)
    os.environ["NAMELECULE_TEST_BASE_URL"] = args.base_url
    bidi = {"__name__": "namelecule_alkane_export_bidi"}
    pending, records = {}, []
    evidence = {
        "schemaVersion": 1, "recordedUTC": datetime.now(timezone.utc).isoformat(),
        "method": "Actual native Main57 SVG; existing exporter AST-extracted, computed styles inlined and complete visible drawing fitted; no atom/bond-coordinate edits",
        "viewer": MAIN, "catalogVersion": 2, "catalogRevision": catalog["revision"],
        "catalogSHA256": before[CATALOG], "manifestSHA256": before[MANIFEST],
        "bundleSHA256": before[BUNDLE], "exportExpressionSHA256": sha(expression.encode()),
        "nominalFontPixels": 22, "numbering": False, "highlights": False,
        "sourceFiles": before, "servedSources": served, "assets": records,
    }
    try:
        exec(compile((ROOT / "tools/namelecule_bidi.py").read_text(), "namelecule_bidi", "exec"), bidi)
        bidi["call"]("browsingContext.setViewport", {"context": bidi["ctx"],
            "viewport": {"width": 1800, "height": 1400}, "devicePixelRatio": 1})
        bidi["navigate"](MAIN + "?libs=local&v=alkane-pool-export-v2")
        bidi["app_ready"]()
        bidi["ev"]("document.fonts.ready.then(()=>true)")
        bidi["ev"]("window.__mulerStepLang='gr';substNamingMode='school';etherNamingMode='iupac';fInitNamingProps();true")
        for molecule in molecules:
            key = molecule["id"]
            for mode in ("expanded", "condensed"):
                bidi["ev"]("selectedMol=" + json.dumps(key) + ";mode2D=" + json.dumps(mode) + ";"
                    "modeSuffix=" + json.dumps("_2D_" + mode.title()) + ";"
                    "mainChainMode='algorithmic';nameAnalysisMode='none';numberingFlag=false;"
                    "window.nameHiddenComps=[];window.nameExplainAll=false;window.nameCrossFlag=false;"
                    "window.MulerQuizTarget=null;window.MulerSelectPurpose='free';"
                    "if(typeof fMulerSelectClear==='function'){fMulerSelectClear();fMulerSelectState().active=false;}"
                    "document.getElementById('jsmeNomeclatureSVG').replaceChildren();"
                    "fInitProps();fClearHighlights();fLoadMol2D();fShowNameAnalysis();true")
                bidi["until"]("selectedMol===" + json.dumps(key) + "&&mode2D===" + json.dumps(mode) +
                    "&&!!document.querySelector('#jsmeNomeclatureSVG svg text[data-namelecule-role=label]')")
                row = json.loads(bidi["ev"](expression))
                raw_svg, mol_hash = validate_svg(row, molecule, mode)
                path = ASSETS / (mode + "-v2") / (key + ".svg")
                pending[path] = raw_svg
                row.update(file=str(path.relative_to(ROOT)), moleculeId=key, mode=mode,
                    nameGR=molecule["nameGR"], sourceFile=molecule["files"][mode],
                    sourceMOLSHA256=mol_hash, expandedMOLSHA256=molecule["sha256"]["expanded"],
                    SHA256=sha(raw_svg), numbered=False, highlighted=False)
                records.append(row)
        if source_hashes(molecules) != before:
            raise ValueError("Sources changed during export; no assets saved")
        evidence["javascriptErrors"] = bidi["js_errors"]
        evidence["diagnostics"] = [event for event in bidi["all_events"]
            if event.get("method") == "log.entryAdded" and event.get("params", {}).get("level") in ("error", "warn")]
    finally:
        cleanup_errors = []
        if "ctx" in bidi:
            for method, params in (("browsingContext.close", {"context": bidi["ctx"]}), ("session.end", {})):
                try:
                    bidi["call"](method, params)
                except Exception as failure:
                    cleanup_errors.append({"method": method, "error": str(failure)})
        if "s" in bidi:
            bidi["s"].close()
        evidence["ownedTabAndSessionCleanupErrors"] = cleanup_errors
        if cleanup_errors:
            print(json.dumps({"cleanupErrors": cleanup_errors}), file=sys.stderr)
    # All twelve drawings have passed before any current asset is replaced.
    for path, raw_svg in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw_svg)
    PROVENANCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"assets": len(records), "namesMatchMain": True,
        "sourceMOLsMatchManifest": True, "numbering": False, "highlights": False,
        "javascriptErrors": len(evidence["javascriptErrors"]),
        "provenance": str(PROVENANCE.relative_to(ROOT))}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bidi-port", type=int, default=os.environ.get("NAMELECULE_BIDI_PORT"),
        help="Explicitly owned Firefox BiDi port; or NAMELECULE_BIDI_PORT")
    parser.add_argument("--base-url", type=valid_base, default=os.environ.get("NAMELECULE_TEST_BASE_URL"),
        help="Explicitly owned local server root; or NAMELECULE_TEST_BASE_URL")
    parser.add_argument("--check-inputs", action="store_true",
        help="Validate sources, paths and export-expression extraction without connecting or writing")
    args = parser.parse_args()
    if args.check_inputs:
        catalog, molecules, expression = read_inputs()
        print(json.dumps({"valid": True, "molecules": len(molecules), "assets": len(molecules) * 2,
            "catalogRevision": catalog["revision"], "exportExpressionSHA256": sha(expression.encode())}))
        return
    if args.bidi_port is None or not 1 <= args.bidi_port <= 65535 or args.base_url is None:
        parser.error("Provide --bidi-port and --base-url for the explicitly owned browser/server")
    export(args)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, AssertionError, RuntimeError) as failure:
        print(str(failure), file=sys.stderr)
        raise SystemExit(1)
